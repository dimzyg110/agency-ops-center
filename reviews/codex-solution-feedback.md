# L-CAS Solution Review — Senior Architect Feedback

## 1) What’s good
- **Clear phased approach** with P0 fixes first; acknowledges immediate blockers.
- **Multi-brand foundation** is correctly prioritized early; current hardcoding is the core product failure.
- **Prompt factory + scoring** is the right direction to move from “generic” to “on-brand” content.
- **Brand verification phase** recognizes the real risk: outputs drifting from brand identity.
- **Quality pipeline** (A/B testing + learning loop) is aligned with marketing reality and long-term product value.

## 2) What’s missing or underestimated
- **Compliance/legal constraints** for cannabis marketing (jurisdiction-specific rules, platform policies, age-gating, claims). Needs to be first-class in data model and scoring, not an afterthought.
- **Content governance workflow** (approvals, audit trails, disclaimers, usage rights). Agencies need accountability and defensibility.
- **Data model depth**: brand needs more than tone/colors—include target audience, forbidden topics/visuals, platform-specific dos/don’ts, CTA templates, approved copy snippets, hashtags, and mandatory disclaimers.
- **Prompt scoring**: should include explicit compliance checks and brand lexicon matching, not just “creativity.”
- **Infrastructure & cost control**: generating 100 prompts × images is expensive; need quotas, caching, and batch scheduling.
- **Asset management**: versioning, storage, and metadata tagging for generated images; needs to integrate with brand verification & approvals.
- **AI provider abstraction**: central config is good, but also needs a routing layer + fallbacks + rate limit handling.

## 3) Alternative approaches to consider
- **Hybrid prompt strategy**: use curated “prompt templates + slots” rather than 100 freeform prompts, then diversify with controlled variations. Improves brand consistency and compliance.
- **Human-in-the-loop scoring**: allow quick thumbs-up/down to train prompt ranking. Start simple with manual scoring + telemetry.
- **Use embeddings for brand voice**: build brand “voice vectors” from reference copy and measure candidate prompt similarity.
- **Style “kits”** per brand: prebuilt style prompts + reference packs can reduce drift and speed generation.
- **Batch generation scheduling**: run large generations off-peak or in background jobs to reduce cost spikes.

## 4) Technical recommendations for brand verification
- **Two-layer verification**:
  1) **Embedding similarity** between generated images and brand reference images (CLIP / OpenCLIP).
  2) **Rule-based checks** (color palette match, presence/absence of logo, forbidden visual elements).
- **Reference image taxonomy**: store references by type (logo, product, lifestyle, palette, typography) and score per category.
- **Color palette compliance**: extract dominant colors from generated images and compare against brand palette with tolerance thresholds.
- **Logo detection**: use template matching or a lightweight object detector for brand logo presence.
- **Negative reference set**: include “avoid” examples to penalize drift (e.g., competitor styles, forbidden imagery).
- **Explainable scoring**: show *why* an image passed/failed (palette 80%, style 60%, logo missing). This is critical for agency trust.
- **Thresholds per brand**: allow stricter thresholds for high-compliance clients.

## 5) Priority adjustments
- **Move compliance + governance earlier** (Phase 2): introduce compliance rules in Brand model and scoring early. Cannabis marketing requires this before scaling.
- **Bring in asset management** earlier (Phase 3): metadata, storage, approval workflow should exist before large batch generation.
- **Brand verification MVP earlier**: basic palette + embedding checks should start in Phase 3 with prompt factory to prevent “scale of bad.”

## 6) Risk factors
- **Regulatory/platform compliance**: failures here can kill agency trust and violate ad platform rules.
- **Model instability/costs**: image generation costs + API changes can blow budgets; need rate limits and failover.
- **Data quality**: weak brand reference sets → poor verification accuracy; requires high-quality inputs.
- **Product UX**: if selection/review/approval flow is clunky, agencies will abandon.
- **Underestimating ops**: scaling prompt factory without proper monitoring, logging, and error recovery will stall.
- **Security**: mismanaged client assets or leaked brand IP could be reputationally fatal.

---
**Bottom line:** Strong direction, but needs compliance/governance and verification moved earlier, plus more rigorous brand data model and asset workflows. Without those, scaling prompt generation just scales bad outputs.
