# CODEX Review — Phase 2

Date: 2026-02-13 (UTC)
Reviewer: GPT-5.3 Codex (QA role)

---

## 1) Commit `7ab793a` — Demand Signal Aggregation
**File:** `scripts/etl/aggregate-demand-signals.ts`

### Verdict
**REQUEST CHANGES**

### Critical issues (must fix before deploy)
1. **Non-idempotent aggregation (double-counting risk):** Script reads all `budtender_queries` every run and increments `query_count` each time. Re-running the job will inflate counts indefinitely.
   - Fix: add watermarking (`last_processed_at`), or recompute-per-period into temp table + replace/upsert deterministically.
2. **Race condition in manual upsert:** `UPDATE ... RETURNING` then `INSERT` is not atomic. Concurrent runs can insert duplicate logical buckets.
   - Fix: add a unique constraint over bucket dimensions (`operator_id, category, goal, experience_level, budget_range, period_start, period_end`) and use `INSERT ... ON CONFLICT ... DO UPDATE`.

### Warnings (should fix)
1. **Connection cleanup missing:** script exits without explicitly closing DB pool/client; can hang in some runtime contexts.
2. **Keyword matching false positives:** naive `includes()` can misclassify (e.g., "painting" matches `pain`).
3. **No transaction around batch writes:** partial aggregation may be committed if failure occurs mid-loop.

### Suggestions (nice to have)
1. Add dry-run mode and processed time-window parameters.
2. Add metrics logging per bucket type and unmatched-intent rate.
3. Consider bounded vocabulary + regex word boundaries/tokenization for intent extraction.

---

## 2) Commit `9826369` — Weedmaps Scraper Hardening
**File:** `scripts/scrape-weedmaps.ts`

### Verdict
**REQUEST CHANGES**

### Critical issues (must fix before deploy)
1. **Tab/resource leak across retries:** inside `worker`, each retry attempt can create a new `tabId`, but failed-attempt tabs are not closed before the next attempt overwrites `tabId`. In long runs this can leak browser resources/memory.
   - Fix: close tab in per-attempt `finally`, or create one tab outside retry and reset/navigation safely.
2. **No per-store hard timeout budget:** while individual steps are wrapped, a pathological store can still consume excessive time via nested retries/backoffs.
   - Fix: add overall store timeout (AbortController / `withTimeout` around `executeAttempt`).

### Warnings (should fix)
1. **Duplicate error logging:** caught errors are pushed to `stats.errorLog` in catch, then again in post-processing loop from `res.errors`.
2. **`logged` failure classification is incomplete:** `categorizeError` has snapshot-aware paths, but many callsites pass no snapshot, reducing classification quality.
3. **Single-thread queue mutation is acceptable in Node, but result ordering is non-deterministic.** Fine for batch, but can complicate debugging/replay.

### Suggestions (nice to have)
1. Use atomic write pattern for snapshot/summary files (`write tmp` + `rename`).
2. Persist retry metadata per slug (attempt count, last error type) for resume analytics.
3. Add max failed-slug threshold/circuit breaker for broad rate-limit events.

---

## 3) Commit `f0ee8ba` — AC VB Tenant
**Files:**
- `projects/virtual-budtender-glass/tenantConfig.js`
- `projects/virtual-budtender-glass/server.js`

### Verdict
**REQUEST CHANGES**

### Critical issues (must fix before deploy)
1. **Unbounded in-memory `loggedSessions` set:** grows forever and never expires, causing memory leak in long-lived process.
   - Fix: TTL cache/LRU, or persist dedupe in datastore with expiration.
2. **Missing request validation for `/recommend` and `/chat`:** `answers`/`message` are used without schema validation; malformed payloads cause runtime errors and 500s.
   - Fix: enforce JSON schema validation (zod/joi/express-validator) and return 400 on bad input.

### Warnings (should fix)
1. **Error detail leakage:** 500 responses return `error.message` publicly (`details: error.message`) exposing internals.
2. **Tenant ID normalization not enforced:** path/query/body tenant inputs are accepted as-is; case/whitespace variants may create inconsistent behavior.
3. **Fallback behavior can mask client bugs:** defaulting to `'ch'` when tenant is omitted may route traffic to wrong tenant unintentionally.

### Suggestions (nice to have)
1. Prefer strict path-based tenant resolution for multitenancy endpoints; deprecate query/body tenant fields.
2. Add per-tenant rate limiting and abuse controls.
3. Externalize tenant prompts/greetings into DB-backed config with audit trail.

---

## 4) Commit `26bf4e5` — VB Admin API + Migration 008
**Files:**
- `services/api/src/routes/admin-vb.ts`
- `services/api/src/db/schema.ts`
- `services/api/src/index.ts`
- `scripts/migrations/008-vb-tenants.sql`

### Verdict
**REQUEST CHANGES**

### Critical issues (must fix before deploy)
1. **Secret material stored/returned in plaintext (`glass_api_key`):** API accepts and persists raw API keys and returns tenant objects directly.
   - Risk: accidental leakage through logs/responses/backups.
   - Fix: encrypt at rest (KMS/app-level crypto), redact in API responses, separate secret-write endpoint, never return full key after create.
2. **Migration seed may fail on fresh DB due to FK assumptions:** hardcoded `operator_id` values depend on existing `operators` rows; if absent, migration can fail.
   - Fix: seed with `NULL` operator_id or guarded inserts that verify operator existence.

### Warnings (should fix)
1. **Schema drift between migration and Drizzle schema:** migration does not enforce `NOT NULL` on fields that schema expects non-null (`enabled`, `created_at`, `updated_at`).
2. **Slug validation too permissive:** allows arbitrary strings; should enforce URL-safe tenant slug pattern (e.g., `^[a-z0-9-]+$`).
3. **No pagination on list endpoint:** `/admin/vb/tenants` returns all rows; can degrade over time.

### Suggestions (nice to have)
1. Add `updated_at` DB trigger for consistency.
2. Add audit logging for admin tenant CRUD (who changed what, when).
3. Add soft-delete or `archived_at` instead of hard delete.

---

## Overall assessment
All 4 commits improve functionality, but none are fully production-ready as-is. Primary blockers are **idempotency/race safety in demand aggregation**, **resource leak risk in scraper retries**, **validation/memory hygiene in VB server**, and **secret handling + migration robustness in VB admin API/migration**.
