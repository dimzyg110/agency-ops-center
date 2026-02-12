# GLASS Platform Security Audit (Pen-Test Style)

**Date:** 2026-02-12 (UTC)  
**Auditor:** Senior Security Engineer (Code + Production Active Testing)  
**Scope:**
- Backend/API code, frontend code, scripts/config listed in brief
- Live API/Web testing against production
- Read-only DB validation against provided PostgreSQL endpoint

---

## 1) Executive Summary

**Overall Risk Rating: HIGH**

GLASS has several strong controls (TypeBox schema validation, generally parameterized Drizzle SQL, auth on most core CRUD endpoints), but production currently exposes multiple high-impact weaknesses:

### Top 5 Findings
1. **Public admin endpoint exposure (`/api/v1/admin/data-quality`)**: returns internal operational metrics without authentication when `ADMIN_API_KEY` is unset.  
2. **Hardcoded secret/API key in source history and code (`re_...` Resend key)**: credential hygiene issue with potential third-party service abuse.  
3. **Overly permissive account provisioning model**: new Clerk users are auto-provisioned with role `owner` in plugin flow, which is risky for privilege model integrity.  
4. **Information leakage via infrastructure endpoints (`/metrics`, verbose `/health`)**: request counts, memory usage, uptime, DB connectivity exposed publicly.  
5. **Public high-value data APIs (`viz`, `ccc`, `report-card`) allow broad scraping/enumeration**: no auth/rate-limit on many expensive and data-rich endpoints.

---

## 2) Vulnerability Table

| ID | Severity | Category | Description | Remediation | CVSS-like |
|---|---|---|---|---|---|
| GLASS-SEC-001 | **High** | Broken Access Control | `/api/v1/admin/data-quality` is accessible unauthenticated in prod | Require `fastify.authenticate` + `requireRole('admin')`; fail-closed when admin key missing | 8.2 |
| GLASS-SEC-002 | **High** | Secrets Management | Hardcoded Resend key in `scripts/auto-invite/send-invites.ts` and git history | Revoke/rotate immediately; remove fallback key; use env-only secrets | 8.0 |
| GLASS-SEC-003 | **High** | Privilege Escalation / IAM Logic | Clerk auto-provision sets `role: 'owner'` for newly created users | Default to least privilege (`viewer` or `admin_pending`) and require explicit approval workflow | 7.9 |
| GLASS-SEC-004 | **Medium** | Info Disclosure | `/metrics` publicly leaks memory, uptime, request counters; `/health` reveals DB state/versioning signal | Restrict to internal network or auth; reduce response detail | 6.5 |
| GLASS-SEC-005 | **Medium** | Data Exposure / Abuse | Many `ccc`, `viz`, `report-card` endpoints are unauthenticated and scrapeable | Add auth + per-IP and token-based rate limits; pagination + caching + quotas | 6.8 |
| GLASS-SEC-006 | **Medium** | Input Handling / Error Path | Oversized waitlist payload triggers Fastify serialization failure (`FST_ERR_FAILED_ERROR_SERIALIZATION`) | Standardize validation error handling to clean 400 responses; add body size guardrail | 5.9 |
| GLASS-SEC-007 | **Medium** | Rate Limiting | Waitlist limit is in-memory (resets on deploy/scale), bypassable | Use Redis/global rate limiter with sliding window and bot controls | 6.1 |
| GLASS-SEC-008 | **Medium** | Network Exposure | Production DB endpoint publicly reachable on Internet (`turntable.proxy...:18582`) | Restrict network ACL/IP allowlist/private networking; enforce non-superuser app roles | 6.7 |
| GLASS-SEC-009 | **Low** | Security Headers | Missing/weak hardening headers (no clear CSP/HSTS/XFO in tested responses) | Add helmet-like header policy at API/web edge | 4.8 |
| GLASS-SEC-010 | **Low** | Dependency Risk | `npm audit` flags high vulns via `bcrypt` transitive `tar` chain | Upgrade bcrypt to patched major and re-run audit | 4.9 |

---

## 3) Detailed Findings

### GLASS-SEC-001 — Public Admin Endpoint Exposure
**Severity:** High  
**Description:** `/api/v1/admin/data-quality` route in `routes/ccc.ts` has no auth middleware. It only checks an optional `ADMIN_API_KEY`; if unset, endpoint is effectively public.

**PoC**
```bash
curl -i https://glass-api-production.up.railway.app/api/v1/admin/data-quality
# HTTP/2 200 + full internal score payload observed
```

**Impact:**
- Reveals internal quality metrics and operational weak spots
- Enables reconnaissance for targeted abuse/DoS timing

**Exact Remediation (code):**
```ts
fastify.get('/admin/data-quality', {
  onRequest: [fastify.authenticate],
  preHandler: [fastify.requireRole('admin')],
}, async (request, reply) => { ... })
```
Also fail startup if `ADMIN_API_KEY` is required but missing.

**Priority:** P0

---

### GLASS-SEC-002 — Hardcoded Secret in Source
**Severity:** High  
**Description:** Hardcoded Resend API key fallback found:
- `src/scripts/auto-invite/send-invites.ts` contains `re_SX85...`

Git history indicates prior secret hygiene fixes, but this key remains present in repo context.

**PoC**
```bash
grep -rn "re_" /data/workspace/projects/glass/src/scripts/auto-invite/send-invites.ts
```

**Impact:**
- Unauthorized email sends/cost abuse
- Reputation damage/domain deliverability risk

**Remediation:**
- Immediately revoke/rotate key in provider
- Remove all hardcoded fallback keys
- Enforce env-only secret loading + startup fail if missing
- Add pre-commit secret scanning (gitleaks/trufflehog)

**Priority:** P0

---

### GLASS-SEC-003 — Risky Auto-Provision Privilege Assignment
**Severity:** High  
**Description:** In `plugins/auth.ts`, auto-provision flow can create new users with elevated role context (`owner`) for newly provisioned accounts.

**PoC (code path):**
- `autoProvisionClerkUser()` inserts into `users` with `role: 'owner'` when no existing mapping exists.

**Impact:**
- New signups may receive excessive permissions by default
- Increases blast radius if signup abuse occurs

**Remediation (code):**
```ts
role: 'viewer' // or 'pending'
```
Then require admin approval + explicit role elevation workflow.

**Priority:** P0

---

### GLASS-SEC-004 — Public Metrics/Health Info Disclosure
**Severity:** Medium  
**Description:** `/metrics` is publicly accessible and reveals request totals, memory usage, uptime, timestamps. `/health` reveals DB connectivity and service metadata.

**PoC**
```bash
curl -s https://glass-api-production.up.railway.app/metrics
curl -sI https://glass-api-production.up.railway.app/health
```

**Impact:**
- Improves attacker recon for resource exhaustion attacks
- Provides internals for fingerprinting and timing

**Remediation:**
- Restrict to private network / auth token
- Return minimal health signal for public probes

**Priority:** P1

---

### GLASS-SEC-005 — Public Scrapeable Data APIs
**Severity:** Medium  
**Description:** Endpoints in `ccc.ts`, `viz.ts`, `report-card.ts` are mostly public.
Verified unauthenticated success on:
- `/api/v1/viz/price-ticker`
- `/api/v1/ccc/cross-reference`
- `/api/v1/report-card/<valid-uuid>` returns 404/200 logic without auth gate

**PoC**
```bash
curl -i https://glass-api-production.up.railway.app/api/v1/viz/price-ticker
curl -i https://glass-api-production.up.railway.app/api/v1/ccc/cross-reference
```

**Impact:**
- Bulk competitor intelligence scraping
- Costly query abuse and potential DB pressure

**Remediation:**
- Introduce auth tiering (public-lite vs authenticated-full)
- Add strict per-route rate limiting and pagination limits
- Add caching and anti-enumeration controls

**Priority:** P1

---

### GLASS-SEC-006 — Oversized Payload Error-Path Weakness
**Severity:** Medium  
**Description:** Waitlist oversized email payload triggers serialization failure path:
`FST_ERR_FAILED_ERROR_SERIALIZATION` instead of controlled validation response.

**PoC**
```bash
curl -s -X POST https://glass-api-production.up.railway.app/api/v1/waitlist \
  -H 'Content-Type: application/json' \
  --data-binary @big_payload.json
# observed 500 serialization error mentioning missing "success" field
```

**Impact:**
- Inconsistent error handling and noisy internals
- Potential abuse of expensive validation/error paths

**Remediation:**
- Ensure route schema includes 500 shape or use centralized generic errors
- Add explicit `bodyLimit` in Fastify config and route-level payload caps

**Priority:** P1

---

### GLASS-SEC-007 — Non-Distributed Rate Limit for Waitlist
**Severity:** Medium  
**Description:** Waitlist limiter uses in-memory `Map`; resets across deploys/instances.

**Impact:**
- Easy bypass under autoscaling/restart
- Insufficient anti-spam protection

**Remediation:**
- Redis-backed limiter keyed by IP + fingerprint + email domain heuristics
- Add captcha/challenge for anonymous submissions

**Priority:** P1

---

### GLASS-SEC-008 — Public Database Reachability
**Severity:** Medium  
**Description:** DB endpoint reachable from internet and accepted direct login with provided creds (read test successful). TLS in place (TLSv1.3), but exposure remains risky.

**PoC**
```bash
# TCP open
# psql connection successful, SELECT count(*) from operators returned data
```

**Impact:**
- If credentials leak (already happened in task context), direct DB compromise risk is high

**Remediation:**
- Move DB to private network / allowlist app egress only
- Use least-privilege DB roles (no superuser app creds)
- Rotate credentials immediately

**Priority:** P0

---

### GLASS-SEC-009 — Security Header Hardening Gaps
**Severity:** Low  
**Description:** Tested responses did not clearly include strict CSP/HSTS/X-Frame-Options at origin layer.

**Remediation:**
- Add strict CSP, HSTS (preload if ready), X-Frame-Options or `frame-ancestors`, Referrer-Policy, X-Content-Type-Options.

**Priority:** P2

---

### GLASS-SEC-010 — Dependency Vulnerabilities
**Severity:** Low  
**Description:** `npm audit` in API reports **3 high** vulnerabilities tied to `bcrypt` dependency chain (`@mapbox/node-pre-gyp` -> `tar`).

**PoC**
```bash
cd src/services/api && npm audit --omit=dev --json
```

**Remediation:**
- Upgrade `bcrypt` to major patched line (`6.x`), test auth flows
- Re-run audit in CI and gate merges on high/critical vulns

**Priority:** P2

---

## AuthZ/AuthN Endpoint Mapping Summary

### Authenticated (with `fastify.authenticate`)
- `operators` (except `/operators/search`)
- `prices`, `products`, `sources`, `watchlists`, `alerts`, `threats`, `recommendations`, `profile`, `dashboard`, `exports`, `margin-rules`, `admin/waitlist/stats`

### Public
- `/health`, `/metrics`
- `/api/v1/operators/search`
- `/api/v1/waitlist`
- `/api/v1/newsletter/subscribe`
- Most `/api/v1/ccc/*`
- Most `/api/v1/viz/*`
- `/api/v1/report-card/*`
- `/api/v1/admin/data-quality` (**critical exposure**)

---

## Active Testing Notes (requested tests)

- SQL injection payload on `/operators/search`: no DB break observed; endpoint returned empty data (parameterized behavior appears safe).  
- XSS payload in waitlist email: accepted as invalid-email path dependence; no reflected XSS observed from API response.  
- Enumeration with `%`: returned empty due current escape/validation behavior.  
- Oversized payload: triggered 500 serialization-path defect (see GLASS-SEC-006).  
- Unauthorized admin access:
  - `/api/v1/admin/data-quality` => **200 exposed**
  - `/api/v1/admin/waitlist/stats` => **401 protected**
- Exposed files on web (`/.env`, `/.git/config`, `/package.json`) returned SPA index, not raw file disclosure.
- CORS preflight from `evil.com`: 204 but no permissive `Access-Control-Allow-Origin` observed in response sample.

---

## 4) Positive Findings

- Good use of TypeBox validation schemas on many routes.
- Most DB queries use Drizzle parameterization (`sql` template usage appears non-concatenated).
- Global error handler avoids full stack trace leakage in production mode.
- `/admin/waitlist/stats` correctly requires auth + admin role.
- Waitlist includes basic validation + anti-dup behavior.
- DB connection observed using TLS 1.3.
- Frontend static file probing (`.env`, `.git`) did not expose internals directly.

---

## 5) Recommendations (Prioritized)

### Immediate (0–24h)
1. **Lock down `/admin/data-quality`** behind auth+role.
2. **Revoke/rotate exposed secrets** (Resend + DB creds if reused/exposed).
3. **Restrict DB network exposure** (private networking/IP allowlist) and remove broad credentials.

### Short Term (1–7 days)
4. Change auto-provision role from `owner` to least privilege + approval workflow.
5. Move rate-limiting to Redis/global strategy; add anti-bot challenge on anonymous endpoints.
6. Restrict `/metrics` and reduce `/health` verbosity.
7. Add response/body size limits and normalize oversize validation errors.

### Medium Term (1–4 weeks)
8. Split public vs private data APIs with clear product policy and quotas.
9. Add WAF/rate rules for scraping-heavy endpoints (`viz`, `ccc`, `report-card`).
10. Patch dependency chain (`bcrypt` major upgrade) and enforce CI security gates.
11. Implement security headers baseline across API/web edges.

---

## Appendix: Selected Proof Commands

```bash
# Unauth admin data exposure
curl -i https://glass-api-production.up.railway.app/api/v1/admin/data-quality

# Protected admin endpoint comparison
curl -i https://glass-api-production.up.railway.app/api/v1/admin/waitlist/stats

# Public metrics exposure
curl -s https://glass-api-production.up.railway.app/metrics

# Unauth data-rich endpoint
curl -i https://glass-api-production.up.railway.app/api/v1/viz/price-ticker

# Oversized payload error path
curl -s -X POST https://glass-api-production.up.railway.app/api/v1/waitlist \
  -H 'Content-Type: application/json' --data-binary @big_payload.json
```
