# GLASS Database / Migrations / Schema Audit

Date: 2026-02-13 (UTC)
Auditor: Senior Backend Engineer (subagent)
Scope: Railway Postgres + SQL migrations + Drizzle schema/config + DB layer code + infra schema/seed + strategy alignment

---

## Executive Summary

The database layer is in a **dangerous drift state**:

- The expected `glass` schema does **not exist** in Railway; all GLASS tables live in `public`.
- Runtime `search_path` and schema strategy are inconsistent across DB, migrations, Drizzle, and app code.
- There is **no migration tracking system** (critical for repeatable deploys).
- Several migrations are non-idempotent and include destructive/data-mutation behavior.
- Drizzle schema and live DB are out of sync (e.g., `pos_connections` defined in code but absent in DB).
- `src/infra/schema.sql` is materially outdated relative to production schema.
- DB code has at least one **runtime-breaking upsert conflict target bug** (`sources.url` has no unique constraint).

---

## Method & Evidence

### Live DB checks run
Connected to Railway Postgres and verified:
- `SHOW search_path` => `"$user", public`
- Schemas => only `information_schema`, `pg_catalog`, temp/toast, `public` (no `glass`)
- GLASS domain tables all present in `public` (e.g., `products`, `prices`, `scrape_runs`, `canonical_products`, `product_matches`, `vb_tenants`, etc.)
- Extensions: `pgcrypto`, `unaccent`, `pg_trgm`, `plpgsql`
- Views: `daily_price_averages`, `stage1_brand_normalization`, `stage2_exact_match_candidates`, `stage3_fuzzy_match_candidates`
- Materialized views: `mv_thc_integrity`, `mv_operator_health`
- No migration tracking table found (`schema_migrations`, `__drizzle_migrations`, etc. absent)

### Files reviewed
- `/data/workspace/projects/glass/src/scripts/migrations/001-009`
- `/data/workspace/projects/glass/src/migrations/004_matching_engine.sql`
- `/data/workspace/projects/glass/src/services/api/src/db/schema.ts`
- `/data/workspace/projects/glass/src/services/api/drizzle.config.ts`
- `/data/workspace/projects/glass/src/scripts/lib/db.ts`
- `/data/workspace/projects/glass/src/infra/schema.sql`
- `/data/workspace/projects/glass/src/seed.sql`
- `/data/workspace/projects/glass/GLASS-MASTER-STRATEGY.md` (DB/infra-relevant sections)

---

## Findings

### 1) `glass` schema is missing in production; all GLASS objects are in `public`
**Severity:** Critical  
**Description:** The platform architecture expects `glass` vs `public` separation, but Railway has no `glass` schema. All GLASS objects are in `public`.  
**Impact:** Namespace collisions, weak tenancy boundaries, brittle object resolution, high risk of cross-app contamination (Cue/GLASS). Makes `search_path` assumptions unreliable.  
**Fix:**
1. Create `glass` schema.
2. Move GLASS tables/views/functions/indexes into `glass`.
3. Lock DB role defaults: `ALTER ROLE ... SET search_path = glass, public`.
4. Fully qualify SQL in migrations (`glass.table`).
5. Keep only shared/common objects in `public` intentionally.  
**Effort:** 10-16h

---

### 2) `search_path` is inconsistent and currently wrong by default
**Severity:** High  
**Description:** DB default is `"$user", public`; app code (`db.ts`) sets `SET search_path TO glass, public` on connect; Drizzle config/schema still effectively target `public`.  
**Impact:** Behavior differs by connection path/tool. Queries can hit different objects depending on client. Hard-to-debug prod incidents.  
**Fix:**
- Enforce search path centrally at role/database level.
- Make app bootstrap verify `current_setting('search_path')` and fail-fast if unexpected.
- Ensure Drizzle migration generation/runtime use `glass` explicitly.
- Use explicit schema qualification for critical DDL/DML.  
**Effort:** 4-8h

---

### 3) No migration tracking/versioning table
**Severity:** Critical  
**Description:** No `schema_migrations`/`__drizzle_migrations` equivalent exists in live DB. Raw SQL files exist, but there is no authoritative applied-state registry.  
**Impact:** Cannot safely guarantee ordering, replay safety, or environment parity. High risk of double-apply, drift, and failed deploys.  
**Fix:**
- Introduce migration ledger table (or adopt Drizzle migrations table consistently).
- Backfill applied migrations with checksums and executed_at.
- Gate deploy pipeline on migration ledger validation.  
**Effort:** 6-10h

---

### 4) Non-idempotent / destructive migration patterns in `004_matching_engine.sql`
**Severity:** High  
**Description:** Contains `DROP INDEX IF EXISTS uq_canonical_products_exact_signature;` followed by unconditional `CREATE UNIQUE INDEX ...` (without IF NOT EXISTS), and many unqualified object names.  
**Impact:** Re-run risk, lock/contention risk, and schema-target ambiguity with multi-schema plans.  
**Fix:**
- Convert to strongly idempotent DDL (`CREATE ... IF NOT EXISTS`, guarded ALTERs).
- Fully qualify all objects (`glass.canonical_products`, etc.).
- Use transactional DDL strategy with explicit lock minimization and rollback playbook.  
**Effort:** 4-6h

---

### 5) `004-merge-duplicate-operators.sql` is a data migration with side effects and poor re-run safety
**Severity:** High  
**Description:** It mutates many FK tables, deletes operators, and relies on runtime data shape. Even if transactional, repeated runs can produce different outcomes.  
**Impact:** Potential accidental merges/deletes, referential surprises, and irrecoverable business data changes without audit checkpointing.  
**Fix:**
- Move to controlled one-off runbook with dry-run output tables + approval step.
- Add pre/post validation checks and backup snapshot requirement.
- Record execution artifacts and operator merge mapping persistently (not temp only).  
**Effort:** 6-12h

---

### 6) Runtime-breaking conflict target in `db.ts` (`upsertSource`)
**Severity:** Critical  
**Description:** `upsertSource` does `ON CONFLICT (url)` but `sources.url` has no unique constraint in live DB.  
**Impact:** Upsert can fail at runtime (`there is no unique or exclusion constraint matching the ON CONFLICT specification`), breaking ingestion.  
**Fix:**
- Add unique constraint/index on `sources(url)` (or change conflict target to existing unique key).
- If same URL can exist per operator, use composite unique `(operator_id, url)` and update SQL accordingly.  
**Effort:** 1-3h

---

### 7) Schema contamination: `public` is not Cue-clean; GLASS tables are mixed in
**Severity:** High  
**Description:** Requirement says verify `public` is clean Cue app, but `public` contains broad GLASS domain (scraper, matching, CCC, VB, etc.).  
**Impact:** Operational ambiguity, accidental cross-app coupling, permission scoping complexity, migration blast radius expansion.  
**Fix:**
- Execute schema split (`glass` for GLASS objects).
- Restrict Cue to its own namespace (`public` or `cue`), with explicit grants.
- Add CI check to block new unqualified GLASS DDL.  
**Effort:** 8-14h

---

### 8) Drizzle schema does not match live DB (missing table in DB)
**Severity:** High  
**Description:** Drizzle defines `pos_connections`; live DB has no `pos_connections` table.  
**Impact:** Runtime failures in any code path querying/inserting this table; false confidence from type-safe code.  
**Fix:**
- Add missing migration for `pos_connections` (in target schema).
- Add schema parity check in CI (Drizzle model vs information_schema diff).  
**Effort:** 2-4h

---

### 9) Drizzle config not schema-scoped to `glass`
**Severity:** High  
**Description:** `drizzle.config.ts` does not set/force a `glass` schema strategy; tables in `schema.ts` are unscoped (`pgTable('...')`).  
**Impact:** Drizzle defaults to `public`, conflicting with intended architecture and `db.ts` search_path behavior.  
**Fix:**
- Use schema-aware table builders (e.g., `pgSchema('glass')`) or explicit schema options.
- Align generated migrations to `glass` namespace.
- Add guard test to fail if generated SQL references `public` for GLASS domain tables.  
**Effort:** 3-6h

---

### 10) Duplicate/redundant indexes exist
**Severity:** Medium  
**Description:** Live DB has overlapping duplicates (examples):
- `prices`: both `idx_prices_operator` and `idx_prices_operator_id`; both `idx_prices_product` and `idx_prices_product_id`
- `ccc_licenses`: `idx_ccc_licenses_type` and `idx_licenses_type`
Also multiple overlapping time/composite indexes on `prices`.  
**Impact:** Extra write amplification, larger index maintenance cost, planner confusion, slower inserts/updates.  
**Fix:**
- Run index usage analysis (`pg_stat_user_indexes`) over representative load.
- Drop true duplicates and low-value overlaps.
- Keep canonical naming convention and ownership comments per index.  
**Effort:** 3-5h

---

### 11) Missing FK on lineage field `price_changes.run_id`
**Severity:** Medium  
**Description:** `price_changes.run_id` exists but has no FK to `scrape_runs(id)`.  
**Impact:** Orphan lineage references possible; weak traceability for run-to-change analytics.  
**Fix:**
- Add FK with `ON DELETE SET NULL` (or cascade policy per retention).
- Backfill/validate existing values before constraint enablement.  
**Effort:** 1-2h

---

### 12) Additional likely-unconstrained IDs in analytics/event tables
**Severity:** Low  
**Description:** Columns like `tenant_id`, `participant_id`, `reviewer_id`, `scrape_job_id` are intentionally flexible but currently unconstrained.  
**Impact:** Data quality entropy over time; harder joins and attribution consistency.  
**Fix:**
- Decide canonical reference model (strict FK vs soft reference).
- Add CHECK/domain validation where FK is not desirable.  
**Effort:** 3-6h

---

### 13) `src/infra/schema.sql` is outdated vs production
**Severity:** High  
**Description:** Infra schema file omits many current objects/columns (matching engine tables, newer run fields, ecosystem tables, billing fields, etc.).  
**Impact:** New environments built from infra SQL diverge from prod immediately; onboarding/recovery unreliable.  
**Fix:**
- Regenerate baseline schema from current canonical migration chain.
- Mark old schema as deprecated or derive from migration output only.
- Add CI to detect infra schema drift.  
**Effort:** 4-8h

---

### 14) `seed.sql` assumes `public` and hardcoded operator UUIDs
**Severity:** Medium  
**Description:** Seed script writes to `public.*` explicitly and includes hardcoded target operator IDs.  
**Impact:** Breaks schema split plans; fragile across environments; can silently seed wrong tenant/operator.  
**Fix:**
- Parameterize schema + operator identity lookup.
- Make seed idempotent with deterministic keys and explicit environment guards.
- Split demo seed from prod-safe seed.  
**Effort:** 3-5h

---

### 15) Strategy gap: tax normalization DB requirements are not implemented
**Severity:** High  
**Description:** Master strategy explicitly requires `store_tax_profile` and full MA municipal tax rate dataset + post-tax price logic; these tables/structures are absent in live DB.  
**Impact:** Core consumer promise (“tax-included comparable prices”) is not enforceable at data layer; trust and product positioning risk.  
**Fix:**
- Add `store_tax_profile` and municipal tax reference tables.
- Backfill 351 municipalities + tax rates.
- Link operator/store geography to tax profile resolution and pricing API outputs.  
**Effort:** 8-14h

---

## Migration-by-Migration Notes (001–009 + matching engine)

- **001-scraper-v2.sql:** Mostly idempotent (`IF NOT EXISTS`) but unqualified schema names; assumes current `search_path`.
- **002-price-idempotency.sql:** Good idempotent pattern; depends on expression index consistency.
- **003-data-quality-infra.sql:** Creates heavy matviews and function in migration; operationally risky for deploy windows.
- **004-merge-duplicate-operators.sql:** Data-destructive migration; should be controlled runbook, not standard replay migration.
- **005-performance-indexes.sql:** Adds indexes that duplicate existing ones (drift from prior migrations/Drizzle).
- **006-ecosystem-integration.sql:** Structurally fine, but unqualified schema and no tenant FK model.
- **007-billing.sql:** Simple additive migration; okay.
- **008-vb-tenants.sql:** Includes environment-specific seed inserts with hardcoded operator IDs; not portable.
- **009-demand-signals-upsert-safety.sql:** Good guard, but checks only by constraint name globally (not schema-scoped).
- **004_matching_engine.sql:** Rich functionality but includes non-idempotent/rebuild patterns and assumes schema path.

---

## Scraper Pipeline Column Health (`glass` expected domain, currently `public`)

Core tables required by scraper pipeline are present with expected key fields:
- `operators`: includes `platform`, `platform_slug`, `metadata`
- `products`: includes `weight_grams`, `strain_type`, `subcategory`
- `prices`: includes `price_per_gram`, `weight_grams`, `menu_type`, `run_id`
- `scrape_jobs`: includes `run_id`, `quality_metrics`
- `scrape_runs`: includes both legacy/new columns (`platform`, `source`, `products_found`, `products_upserted`, `error_log`, `errors`, etc.)

Main issue is **namespace and governance**, not absence of these columns.

---

## Prioritized Action List

1. **(Critical)** Stand up migration ledger and freeze deploys until migration state is authoritative.  
2. **(Critical)** Fix `upsertSource` conflict target mismatch (`sources.url` uniqueness vs SQL conflict clause).  
3. **(Critical/High)** Execute schema split: create `glass`, migrate GLASS objects out of `public`, set role-level `search_path`.  
4. **(High)** Align Drizzle with target schema (`glass`) and restore schema parity checks (including `pos_connections`).  
5. **(High)** Refactor risky migrations (`004_matching_engine`, `004-merge-duplicate-operators`) into safe idempotent + controlled runbook patterns.  
6. **(Medium)** Remove duplicate/overlapping indexes after usage analysis.  
7. **(Medium)** Add missing FK(s), starting with `price_changes.run_id`.  
8. **(High strategic)** Implement strategy-required tax data layer (`store_tax_profile` + municipal tax tables) to support tax-included pricing promise.  
9. **(High)** Rebuild `infra/schema.sql` from canonical migration chain and deprecate stale schema snapshot.  
10. **(Medium)** Refactor `seed.sql` to schema-parameterized, environment-safe, idempotent seeds.

---

## Estimated Total Remediation Effort

~44 to 84 engineering hours (depending on migration complexity, data volume for schema move, and rollout safety requirements).