# LLM Model Research for Cannabis Product Name Parsing (150K+ records)

_Last updated: 2026-02-14 (UTC)_

## 0) Executive summary

For this use case (deterministic extraction from noisy product strings into strict JSON), **the best cost/performance architecture is hybrid**:

1. **Rules + regex first-pass** for easy cases (likely 60–85%)
2. **Cheap model fallback** for hard/ambiguous cases
3. **Schema-constrained output** (JSON Schema / structured output libraries) for reliability

If you run pure LLM on all 150K daily, your cost can still be very low (single-digit dollars to tens of dollars/day depending model), but hybrid gets it even lower and increases consistency.

---

## 1) Workload assumptions and cost math

### Assumptions provided
- Products: **150,000**
- Input tokens/product: **~100**
- Output tokens/product: **~80**
- Total input: **15M tokens**
- Total output: **12M tokens**

### Cost formula
\[
\text{Total cost} = (15 \times \text{input\_price\_per\_1M}) + (12 \times \text{output\_price\_per\_1M})
\]

Batching 10–25 rows/request reduces overhead and HTTP latency. On providers with explicit batch discounts (Groq/Fireworks), cost can drop ~50% for async batch jobs.

---

## 2) Candidate model/provider matrix (focused on extraction)

## Legend
- **JSON reliability**: probability of valid parseable schema output in production with strict prompting + schema mode
- **Accuracy estimate**: expected field-level extraction accuracy for your schema after prompt tuning (not guaranteed benchmark)
- **Speed**: provider-published or observed ranges

### A) Dirt-cheap paid APIs (most practical)

| Option | Pricing (USD / 1M) | Est. cost @150K | Speed | JSON reliability | Accuracy est. | Structured output / batch |
|---|---:|---:|---|---|---|---|
| **DeepSeek V3.2 (direct API)** | In: **$0.28** (cache miss), Out: **$0.42** | **$9.24** | Fast, usually interactive latency | Medium-High | ~90–95% with schema prompting | JSON output supported; tool/function style supported |
| **DeepSeek V3.2 (if repeated prompts hit cache)** | In: **$0.028** cache-hit, Out: **$0.42** | **$5.46** | Same | Medium-High | ~90–95% | Same |
| **MiniMax M2.5 (OpenRouter / Fireworks)** | In: **$0.30**, Out: **$1.20** | **$18.90** | Good throughput | High with structured mode | ~92–96% | OpenRouter structured outputs; batch possible via provider APIs |
| **Groq Llama 3.1 8B** | In: **$0.05**, Out: **$0.08** | **$1.71** | **Very fast** (Groq lists ~840 tok/s) | Medium | ~85–92% | JSON mode possible; Groq Batch API has 50% discount |
| **Groq GPT-OSS 20B** | In: **$0.075**, Out: **$0.30** | **$4.73** | Very fast (~1000 tok/s listed) | Medium-High | ~88–94% | Batch API 50% lower pricing |
| **Together Llama 3 8B Lite** | In: **$0.10**, Out: **$0.10** | **$2.70** | Fast | Medium | ~85–92% | Batch API available |
| **Together Mistral Small 3** | In: **$0.10**, Out: **$0.30** | **$5.10** | Fast | Medium-High | ~88–94% | Batch/API support |
| **Fireworks <=16B tier (generic)** | In/Out around **$0.20** | **$5.40** | Fast; serverless + batch | Medium-High | ~88–94% (depends model) | Batch at ~50% of serverless price |

**Notes:**
- Groq/Fireworks async batch can cut costs in half for high-volume offline parse jobs.
- DeepSeek direct pricing is currently extremely strong for this exact extraction workload.

### B) Free/open-weight + free tiers

| Model family | Where to run | Cost potential | Practicality for 150K/day |
|---|---|---|---|
| **Llama 3.1/3.2/3.3** | Groq, Together, Fireworks, self-host | Can be free on small dev tiers | Full 150K/day at $0 unlikely unless self-hosted on owned hardware |
| **Mistral/Mixtral** | Mistral La Plateforme, Together, Fireworks | Mistral announced free tier for experimentation | Free tiers are generally prototyping-level, not guaranteed production throughput |
| **Qwen 2.5/3.x** | Alibaba/Qwen APIs, Together, Groq, OpenRouter | Some free quotas exist by platform/region | Usually not enough for sustained 27M tokens/day unless subsidized |
| **Phi-3/Phi-4** | Azure/third-party hosts/self-host | Cheap on small endpoints, self-host-friendly | Good candidate for fine-tune + self-host for deterministic extraction |
| **Gemma 2 / Gemma 3n** | Together/other hosts/self-host | Very cheap tiers exist on some hosts | Good low-cost fallback, but raw accuracy may trail bigger models |
| **DeepSeek V3/R1** | DeepSeek direct + many aggregators | Very cheap paid usage | Best “almost free” paid option right now |
| **Cerebras Inference** | Cerebras direct | Free tier exists + paid tiers | Great speed; free tier capacity/rate limits can block full daily prod runs |
| **NVIDIA NIM** | NVIDIA-hosted endpoints + self-host containers | Free prototyping access/credits for devs | Good for experimentation; production cost depends deployment path |

**Can this be literally $0?**
- **Possibly for prototyping**, not reliably for full daily 150K unless:
  - you self-host open model on already-owned hardware, or
  - free-tier limits are unusually high and stable (rare), or
  - you spread processing over many days.

---

## 3) Provider-specific findings you asked for

## DeepSeek (direct)
- Public pricing page lists (V3.2): **$0.28/M input (cache miss), $0.028/M input (cache hit), $0.42/M output**.
- Estimated cost for your batch: **$9.24** (or **$5.46** with strong cache-hit behavior).
- JSON mode + tooling supported.
- Very strong cost/quality for extraction.

## MiniMax M2.5 (OpenRouter / Fireworks)
- OpenRouter model feed indicates **$0.30/M input, $1.20/M output**.
- Estimated cost: **$18.90**.
- Good model quality and long context; strong candidate if quality beats DeepSeek for your data.

## Groq
- Pricing page lists many low-cost + high-speed models.
- Examples:
  - Llama 3.1 8B: **$0.05/$0.08** → **$1.71**
  - GPT-OSS 20B: **$0.075/$0.30** → **$4.73**
- Batch API advertises **~50% lower cost** for async jobs.
- Excellent for throughput-heavy nightly pipelines.

## Together
- Pricing page provides a broad catalog from tiny to frontier models.
- Examples:
  - Llama 3 8B Lite: **$0.10/$0.10** → **$2.70**
  - Mistral Small 3: **$0.10/$0.30** → **$5.10**
  - DeepSeek V3.1 on Together: materially higher than DeepSeek direct.
- Good multi-model flexibility and fallback routing.

## Fireworks
- Clear model-family pricing + dedicated endpoint options.
- MiniMax M2 family: **$0.30/$1.20** (similar to OpenRouter listing)
- Batch inference: **50% of serverless token pricing**.
- Useful when you want serverless now and dedicated infra later.

## Cerebras
- Pricing page emphasizes free tier and very high speed; paid starts low for developer tier.
- Good for ultra-fast throughput; exact per-model token prices may vary by route/plan.
- Evaluate carefully for stable production SLAs and rate-limit ceilings.

## NVIDIA NIM
- Strong for self-hostable microservices and enterprise deployment paths.
- Free developer prototyping access exists; production economics depend on where/how hosted.

---

## 4) Structured output reliability stack (important)

For this use case, JSON validity matters as much as base model quality.

### Recommended reliability tooling
1. **Provider-native schema mode** (when available): OpenAI Structured Outputs / OpenRouter structured outputs / tool calling with strict schema.
2. **Outlines / Guidance** (grammar-constrained decoding): force JSON grammar even on open models.
3. **BAML** (BoundaryML): type-safe generation, retries, validation, model-agnostic orchestration.
4. **Post-validators**: JSON Schema + business-rule validators (e.g., THC% bounds, mg consistency with pack size).

### Practical expectation
- Raw prompt-only JSON reliability: often 80–95%
- With structured outputs + validator/retry: effectively production-grade (>99% parseable JSON)

---

## 5) Fine-tuning small models for this niche task

## Could a fine-tuned small model beat larger general models here?
**Yes, often.** For deterministic entity extraction on narrow domain text, a fine-tuned 7B–14B model can outperform larger generic models on consistency and cost.

## Best fine-tune targets
- **Llama 8B class**, **Phi-3/4 class**, possibly **Qwen 7B/14B**
- Train on your verified parses + hard negatives

## Expected outcome
- Better normalization of domain-specific quirks (pack formats, THC string variants, brand noise)
- Lower latency + cheaper inference
- More predictable field behavior across edge patterns

## Fine-tune cost ballpark (SFT)
- Typical hosted SFT pricing (from Together/Fireworks style ranges): roughly **$0.5–$3 per 1M training tokens** for small-mid models.
- Example: 5M-token training corpus × 3 epochs = 15M training tokens
  - At $0.50/M: **$7.50**
  - At $3.00/M: **$45.00**
- Real cost rises with eval runs, larger models, and preference tuning.

This is usually cheap enough to justify if you parse at scale daily.

---

## 6) Non-LLM alternatives (and hybrid recommendation)

## Regex/rule parser only
- Likely handles **60–85%** depending catalog cleanliness.
- Near-zero marginal cost, very fast.
- Fails on ambiguous brand/strain and odd ordering/noise tokens.

## spaCy NER / classical NLP
- Can work for brand/strain tagging if labeled data is good.
- Harder for numeric normalization + compositional fields (pack_size, mg, THC%) without rules.

## Best practical architecture
**Hybrid pipeline**:
1. Rules/regex parse + confidence score
2. If confidence high: accept
3. If low: send to cheap LLM with strict schema
4. Validate and reconcile with deterministic rules

This usually gives best blend of:
- Accuracy
- Cost
- Throughput
- Explainability

---

## 7) API/rate-limit/batch notes

- **Groq**: very high speed, published token/sec, explicit async batch discount.
- **Fireworks**: explicit batch discount, strong serverless → dedicated migration path.
- **DeepSeek**: lowest direct cost among quality models; monitor reliability and uptime in your region.
- **OpenRouter**: great for routing/fallback and structured outputs across many models, but direct-provider pricing can sometimes be cheaper.
- **Free tiers**: good for eval/prototyping; rarely sufficient and predictable for 27M tokens/day production.

---

## 8) Recommended top 3 (cost-effectiveness for your exact use case)

## 1) **DeepSeek V3.2 direct + schema-constrained output**
- **Why #1:** Best price/quality balance for deterministic extraction.
- **Cost:** ~$9.24 per 150K (could be lower with caching).
- **Use when:** You need >90% field accuracy at minimal spend.

## 2) **Groq GPT-OSS 20B (or Llama 3.1 8B for ultra-cheap tier) + batch API**
- **Why #2:** Extremely fast + very low cost, especially with batch.
- **Cost:** $4.73 (20B) or $1.71 (8B), potentially ~50% less in batch mode.
- **Use when:** Throughput dominates and you can tolerate slightly lower edge-case quality vs DeepSeek/MiniMax.

## 3) **MiniMax M2.5 (OpenRouter/Fireworks) with structured outputs**
- **Why #3:** Strong quality and robust behavior; easy integration in existing OpenRouter stack.
- **Cost:** ~$18.90 per 150K.
- **Use when:** You want better extraction quality if it empirically beats cheaper options on your eval set.

---

## 9) Final picks requested

- **If money is no object:**
  - Use a top-tier reliable structured-output model (e.g., Claude Opus / top OpenAI class) as “gold parser,” optionally only on low-confidence rows.
  - Highest reliability and nuanced disambiguation.

- **Absolute cheapest that works:**
  - **Groq Llama 3.1 8B** or similar tiny-cost open model with strict schema + retries + validators.
  - Realistically better: hybrid rules-first + this fallback.

- **Could we run at literally $0?**
  - For full production 150K/day: **unlikely** via public free API tiers.
  - Possible only with **self-hosted open model on already-owned hardware** or limited-volume/non-SLA processing over longer windows.

---

## 10) Suggested next step (high ROI)

Run a **1,500-row benchmark** (stratified messy samples) across:
1. DeepSeek V3.2 direct
2. Groq GPT-OSS 20B (and/or Llama 3.1 8B)
3. MiniMax M2.5

Measure:
- Field-level F1 per key (brand, strain, pack_size, mg, THC%, etc.)
- JSON validity rate
- Retry rate
- Cost/1K products
- P95 latency

Then lock one primary + one fallback model.

---

## Sources checked (pricing/docs pages)
- DeepSeek API pricing docs
- Groq pricing page
- Together pricing page
- Fireworks pricing page
- OpenRouter model metadata API (for MiniMax pricing snapshot)
- Cerebras pricing page
- NVIDIA NIM developer page
- Outlines docs / repo
- BoundaryML (BAML) docs

(Provider prices and limits change frequently; re-verify before committing production budgets.)
