# L-CAS Cost‑Efficient Implementation Plan (Bootstrapped)

> Goal: maximize quality while minimizing paid generations. Treat prompting as cheap, imagery as expensive, video as *very* expensive. Every paid call must be metered, gated, and budgeted.

---

## 1) Image Generation Cost Strategy

### A. Thumbnail‑First Workflow (default)
**Policy:** Never generate >768px unless explicitly approved.

**Workflow**
1. **Generate 100 prompts** → score → select top 10.
2. **Generate thumbnails** at **512px or 768px** (provider‑dependent pricing).
3. Human review/approval step on thumbnails only.
4. **Upscale or re‑render** at 2K/4K *only* after approval.

**Implementation details**
- **tier**: `thumb` (512/768), `mid` (1024), `hi` (2048/4096)
- **default tier** = `thumb`
- **approval required** to move to `mid` or `hi`

**Decision rule**
- If a prompt is rejected at thumbnail: no further spend.
- If accepted: allow *one* upscale or high‑res re‑render.

### B. Upscale‑on‑Approval
- Prefer **upscalers** (Topaz/Replicate/Fal) when cheaper than re‑rendering at high res.
- Cache original seed + prompt → allow deterministic upscale where possible.
- Add per‑brand configuration: `preferred_upscale_provider` and `max_upscale_cost`.

### C. Batch Optimization
- If provider pricing varies by time/region, queue large batches for **off‑peak windows**.
- Add **batch jobs** for daily/weekly thumbnail generation.

### D. Per‑Brand Quotas & Budgets
- **Monthly caps** by brand + campaign.
- **Spend categories:** `prompting`, `image_thumb`, `image_hi`, `upscale`, `video`.
- Hard limits with alerts at 70%/90% usage.

### E. Cost Tracking per Generation
- Log every generation with:
  - `provider`, `model`, `resolution`, `unit_cost`, `duration`, `total_cost`, `currency`, `tokens_used` (if any), `brand_id`, `campaign_id`, `asset_id`, `status`.
- Aggregate daily/weekly/monthly stats per brand.

---

## 2) Video Generation Cost Strategy

### A. Decide When Video Is Needed
**Rule of thumb:** use static unless video has clear ROI (ads, hero sections, social reels).
- Use static images for: blog posts, catalogs, product pages, internal previews.
- Use video for: paid social, homepage hero, launch campaign, product demos.

### B. Approval Gates Before Video
1. **Storyboard/animatic** stage (free or cheap): simple static sequence / motion mockups.
2. **Thumbnail + keyframe approval** before any real video render.
3. **Budget check** before final render.

### C. Duration Limits
Tiered options with fixed costs:
- **Tier S:** 5 seconds (default)
- **Tier M:** 15 seconds (requires explicit approval)
- **Tier L:** 30 seconds (exec approval + higher budget)

### D. Resolution Tiers
- **Preview**: 480p/720p, low FPS
- **Final**: 1080p (default), 2K only if required

### E. Preview/Draft vs Final Render
- Always generate **draft video** first (low res, short duration).
- Only render **final** after approval of draft.

---

## 3) Prompt Factory Economics

### A. Maximize Prompt Quality with Minimal Image Waste
- Generate 100 prompts (cheap), score with LLM + brand rules.
- **Top 10** → only these get thumbnails.
- Use **prompt mutation** (cheap) instead of more image generations.

### B. Pre‑Scoring Before Any Image Generation
- Scoring criteria (0–100):
  - Brand alignment (40)
  - Visual clarity (20)
  - Uniqueness (15)
  - Compliance risk (15)
  - Campaign fit (10)
- **Hard filters**: banned terms, disallowed claims, unsafe content.

### C. Human‑in‑the‑Loop Checkpoints
- **Prompt shortlist review** before thumbnails.
- **Thumbnail review** before any upscales.

### D. Kill Switches if Budget Exceeded
- If `brand.monthly_spend >= cap` → block new generations automatically.
- Manual override requires `admin` + reason logged.

---

## 4) Technical Implementation

### A. Database Schema Additions (example: Postgres)

**1) cost_events**
```sql
create table cost_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz default now(),
  brand_id uuid not null,
  campaign_id uuid,
  asset_id uuid,
  provider text not null,
  model text not null,
  operation text not null, -- prompt_gen|image_gen|upscale|video_gen
  tier text not null,      -- thumb|mid|hi|preview|final
  resolution text,         -- 512x512, 768x768, 2048x2048, 1080p
  duration_sec numeric,
  tokens_in integer,
  tokens_out integer,
  unit_cost numeric(10,4) not null,
  total_cost numeric(10,4) not null,
  currency text default 'USD',
  status text not null,    -- queued|success|failed|cancelled
  metadata jsonb
);
```

**2) brand_budgets**
```sql
create table brand_budgets (
  brand_id uuid primary key,
  month_start date not null,
  cap_prompt numeric(10,2) default 50,
  cap_image numeric(10,2) default 500,
  cap_video numeric(10,2) default 1000,
  cap_total numeric(10,2) default 1500,
  alert_70_sent boolean default false,
  alert_90_sent boolean default false
);
```

**3) asset_generation_requests**
```sql
create table asset_generation_requests (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid not null,
  campaign_id uuid,
  type text not null,     -- image|video
  prompt text not null,
  tier text not null,     -- thumb|hi|preview|final
  status text not null,   -- pending|approved|rejected|running|done|blocked
  approved_by uuid,
  approved_at timestamptz,
  cost_estimate numeric(10,4),
  created_at timestamptz default now()
);
```

### B. API Wrapper Pattern for Metering
**Goal:** every AI call goes through a wrapper that logs cost_event.

**Pseudo‑code**
```ts
async function meteredCall(opts: {
  brandId: string;
  campaignId?: string;
  assetId?: string;
  provider: string;
  model: string;
  operation: 'prompt_gen'|'image_gen'|'upscale'|'video_gen';
  tier: string;
  resolution?: string;
  durationSec?: number;
  costEstimate: number;
  call: () => Promise<any>;
}) {
  await enforceBudget(opts.brandId, opts.costEstimate);

  const eventId = await db.cost_events.insert({
    brand_id: opts.brandId,
    campaign_id: opts.campaignId,
    asset_id: opts.assetId,
    provider: opts.provider,
    model: opts.model,
    operation: opts.operation,
    tier: opts.tier,
    resolution: opts.resolution,
    duration_sec: opts.durationSec,
    unit_cost: opts.costEstimate,
    total_cost: opts.costEstimate,
    status: 'queued'
  });

  try {
    const result = await opts.call();
    await db.cost_events.update(eventId, { status: 'success' });
    return result;
  } catch (e) {
    await db.cost_events.update(eventId, { status: 'failed', metadata: { error: e.message } });
    throw e;
  }
}
```

### C. Budget Alerts & Hard Limits
- **enforceBudget(brandId, costEstimate)**:
  - If `monthly_spend + costEstimate > cap_total` → block.
  - Send alert at 70% and 90%.
- Store `alert_70_sent`, `alert_90_sent` flags to avoid spam.

### D. Resolution/Quality Tier System
- Central config table or JSON:
```json
{
  "image": {
    "thumb": {"resolution": "512x512", "max_cost": 0.05},
    "mid":   {"resolution": "1024x1024", "max_cost": 0.10},
    "hi":    {"resolution": "2048x2048", "max_cost": 0.30}
  },
  "video": {
    "preview": {"resolution": "720p", "max_duration": 5},
    "final":   {"resolution": "1080p", "max_duration": 15}
  }
}
```

### E. Approval Workflow Integration
- `asset_generation_requests` created at **each gate**.
- Only **approved** requests can move to higher tier.
- UI clearly shows **estimated cost** before approval.

---

## 5) Revised Phase Timeline

### Phase 0 (MVP – Week 1‑2)
- Prompt factory + scoring.
- Thumbnail generation (512/768).
- **Basic cost tracking + budgets**.
- Approval gate for upscales.

### Phase 1 (Week 3‑4)
- Upscaling pipeline.
- Brand budgets + alerts.
- Basic dashboard: spend by brand + campaign.

### Phase 2 (Week 5‑6)
- Draft video (preview tier only).
- Video approval gate + duration tiers.

### Phase 3 (Week 7‑8)
- Final video render after approval.
- Advanced reporting (cost per asset, ROI tags).

### Can Wait (Post‑MVP)
- Multi‑provider auto‑switching.
- Dynamic provider price optimization.
- Automated A/B testing with large batch costs.

---

## Summary: Key Guardrails
- **Thumb first** always.
- **No high‑res or video without approval + budget check.**
- **All AI calls metered.**
- **Per‑brand caps enforced.**
- **Human checkpoints at every expensive step.**

This plan ensures L‑CAS can scale content creation while protecting a bootstrapped budget.