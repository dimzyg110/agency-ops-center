# Seedance 2.0 Automation Scoping Decision Memo

**Date:** 2026-02-15  
**Status:** Research Complete — Pending Decision  
**Authors:** Roviq Development Team  

---

## Executive Summary

Seedance 2.0 automation for GLASS/Roviq is **technically feasible but requires trade-offs**. There is **no official ByteDance API for Seedance 2.0 available yet** (expected late February 2026 via BytePlus). Current options rely on third-party API aggregators (Fal.ai, Replicate, WaveSpeedAI) or third-party wrapper services (seedanceapi.org, Kie AI). Browser automation via Playwright/Camoufox is possible but high-risk due to TOS restrictions and anti-bot measures.

**Recommendation:** Wait for official BytePlus API if timeline allows (est. Feb 24+), or implement via **Fal.ai** or **Replicate** for immediate production use with fallback to official API when available.

---

## 1. Official API Status

### ByteDance/BytePlus Official API
| Attribute | Status |
|-----------|--------|
| **Availability** | **Not yet launched** — scheduled for "late February 2026" per multiple sources |
| **Platform** | BytePlus (ByteDance enterprise platform) |
| **Pricing (Seedance 1.5 Pro)** | $1.20 USD/M tokens (video only) / $2.40 USD/M tokens (with audio) |
| **Est. Cost** | ~$0.50-0.99 per 5-10s 720p clip |
| **Auth** | BytePlus account + enterprise verification |
| **SLA** | 99.99% uptime, SOC 2 Type II, HIPAA-aligned |
| **Rate Limits** | Custom concurrency for enterprise plans |

**Key Finding:** The official ByteDance Seedance 2.0 API does not exist as of February 15, 2026. Multiple sources indicate a February 24, 2026 launch target.

### Model Versions Available
1. **Seedance 1.0 Pro** — Available via Together AI, Replicate (legacy)
2. **Seedance 1.5 Pro** — Available via Fal.ai, BytePlus (official), Together AI
3. **Seedance 2.0** — Third-party wrappers only; official API pending

---

## 2. Third-Party API Aggregator Options

### Option A: Fal.ai (Recommended)
| Attribute | Details |
|-----------|---------|
| **Status** | ✅ Available now |
| **Models** | Seedance 1.5 Pro (text-to-video, image-to-video) |
| **Pricing** | ~$2.40/M tokens with audio (~$0.62 per 1080p 5s video) |
| **Features** | 600+ models, unified API, serverless, fast inference |
| **Auth** | API key (Bearer token) |
| **Integration** | REST API + SDKs (Python, Node, cURL) |
| **Rate Limits** | Scale to thousands of requests |
| **Compliance** | SOC 2 compliant |
| **Pros** | Enterprise-grade, fast, reliable, good docs |
| **Cons** | Seedance 2.0 not yet available (only 1.5 Pro), cost premium |

### Option B: Replicate
| Attribute | Details |
|-----------|---------|
| **Status** | ✅ Available now |
| **Models** | Seedance 1.0 Lite, Seedance 1.0 Pro |
| **Pricing** | ~$0.74 per Pro video (estimated markup) |
| **Features** | Standard Replicate workflow, cold start possible |
| **Auth** | API token |
| **Rate Limits** | Standard Replicate limits |
| **Pros** | Familiar API pattern, pay-per-use |
| **Cons** | Cold starts, Seedance 2.0 not available, higher latency |

### Option C: Third-Party Wrappers (seedanceapi.org, Kie AI, etc.)
| Attribute | Details |
|-----------|---------|
| **Status** | ⚠️ Unofficial, use at own risk |
| **Pricing** | $0.04-0.42 per generation (480p-720p, varies by audio) |
| **Features** | REST API, credit-based billing |
| **Auth** | OAuth (Google sign-in) + API key |
| **Pros** | Cheapest option, immediate Seedance 2.0 access (claimed) |
| **Cons** | **No SLA**, unknown reliability, potential TOS violations, could disappear |

### Option D: Together AI
| Attribute | Details |
|-----------|---------|
| **Status** | ✅ Available now |
| **Models** | ByteDance/Seedance-1.0-pro |
| **Note** | Model card shows "Coming Soon" for serverless; requires dedicated endpoint |
| **Pros** | Established platform |
| **Cons** | Complex pricing, Seedance 2.0 not available |

---

## 3. Browser Automation Evaluation

### Feasibility: ⚠️ High Risk, Not Recommended

| Approach | Assessment |
|----------|------------|
| **Direct UI automation** (Playwright/Camoufox on seed.bytedance.com or Jimeng) | **NOT VIABLE** — Chinese platform requires WeChat/Alipay auth, Chinese ID verification, bot detection active |
| **Dreamina international** (if launched) | Possible but unverified; TOS likely prohibits automation |
| **Anti-detection browsers** | Camoufox could work technically, but violates TOS |

### Risks of Browser Automation
| Risk | Severity | Mitigation |
|------|----------|------------|
| **Account termination** | High | None (TOS violation) |
| **CAPTCHA/anti-bot** | High | May require paid solving services |
| **Rate limiting** | Medium | Exponential backoff, proxy rotation |
| **Chinese payment requirements** | High | WeChat Pay/Alipay required for Jimeng |
| **Output reliability** | Medium | No webhook, must poll DOM |
| **Maintenance burden** | High | UI changes break automation |

**Verdict:** Browser automation is technically possible but **legally and practically inadvisable** for production use. Third-party APIs are cheaper than maintaining automation infrastructure.

---

## 4. Architecture Comparison

### Approach A: Wait for Official BytePlus API
```
Use Case: Enterprise, compliance-sensitive deployments
Cost: $$ (medium-high)
Reliability: ⭐⭐⭐⭐⭐ (highest)
Time to Market: 2-4 weeks (post-launch)
Best For: Production apps requiring SLA guarantees
```

### Approach B: Fal.ai Aggregator (Recommended for Immediate Use)
```
Use Case: Production apps needing Seedance now
Cost: $$$ (higher than official)
Reliability: ⭐⭐⭐⭐ (enterprise-grade)
Time to Market: 1-2 days
Best For: Rapid deployment, can migrate to official later
```

### Approach C: Third-Party Wrappers (Budget Option)
```
Use Case: Prototyping, low-budget experiments
Cost: $ (cheapest)
Reliability: ⭐⭐ (no guarantees)
Time to Market: 1 day
Best For: Testing only, NOT for production
```

### Approach D: Browser Automation
```
Use Case: NOT RECOMMENDED
Cost: $$ (hidden engineering cost)
Reliability: ⭐⭐ (fragile)
Time to Market: 1-2 weeks
Best For: None — avoid
```

---

## 5. Proposed Implementation Architecture (OpenClaw/Railway)

### Recommended: Hybrid Queue Worker with Fal.ai + Future Migration Path

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   GLASS API     │────▶│   Job Queue      │────▶│  Worker Pool    │
│   (Railway)     │     │   (BullMQ/       │     │   (Railway      │
└─────────────────┘     │    Bull/Qstash)  │     │    Workers)     │
                        └──────────────────┘     └────────┬────────┘
                                                          │
                                ┌───────────────────────┼────────────┐
                                ▼                       ▼            ▼
                         ┌────────────┐         ┌──────────┐  ┌──────────┐
                         │   Fal.ai   │         │  Fallback │  │  BytePlus│
                         │  (Active)  │         │ (S3/Queue)│  │  (Future)│
                         └────────────┘         └──────────┘  └──────────┘
                                │
                                ▼
                         ┌────────────┐
                         │  S3/audio  │
                         │  Storage   │
                         └────────────┘
```

### Components

| Component | Technology | Notes |
|-----------|------------|-------|
| **Job Queue** | BullMQ (Redis) or Qstash (serverless) | Retry logic, dead letter queue |
| **Workers** | Railway containers or AWS Lambda | Scale 0-N based on queue depth |
| **Video Provider** | Fal.ai REST API | Primary target |
| **Storage** | S3 / R2 / Railway volumes | Webhook output or poll+download |
| **Monitoring** | Railway logs + webhook status | Alert on failures |

### Workflow
```