# Lab Test Import Script — Bug Fix Summary

**Date:** 2026-02-12
**Files Fixed:**
- `src/scripts/import/import-lab-tests.ts`
- `src/scripts/import/lib/etl-base.ts`

---

## Bugs Found & Fixed

### 1. ❌ Broken Drizzle ORM Import Chain (CRITICAL)

**File:** `lib/etl-base.ts`

The ETL base library imported from `../../../services/api/src/db/index`, which uses `import postgres from 'postgres'` (the postgres.js driver for Drizzle ORM). However, the `postgres` npm package is **not installed** — only `pg` is available. This caused a fatal module-not-found error at runtime.

**Fix:** Rewrote all `etl-base.ts` database operations to use raw `pg.Pool` queries instead of Drizzle ORM. This eliminates the broken dependency chain while maintaining identical functionality:
- `isAlreadyImported()` → raw SQL `SELECT` query
- `startEtlRun()` → raw SQL `INSERT ... RETURNING`
- `updateEtlProgress()` → raw SQL `UPDATE` with dynamic SET clauses
- `completeEtlRun()` → raw SQL `UPDATE`

Removed imports: `db` from Drizzle, `eq` from `drizzle-orm`, `etlRuns` from schema.

### 2. ❌ CSV Column Name Mismatches (CRITICAL)

**File:** `import-lab-tests.ts`

The `RawRow` interface declared field names that don't match the actual CSV headers:

| Interface Field (old) | Actual CSV Header | Used In Code |
|---|---|---|
| `ExternalIdentifier` | `ID` | ✅ Code used `row["ID"]` — but interface was wrong |
| `ProductCategory` | `ProductCategoryType` | ✅ Code used `row.ProductCategoryType` — but interface was wrong |
| `StrainCode` | `Strain` | ✅ Code used `row.Strain` — but interface was wrong |
| `TestAnalyte` | `Test Type Name` | ✅ Code used `row["Test Type Name"]` — but interface was wrong |
| `Result` | `TestResult` | ⚠️ `parseDecimal(row.TestResult)` worked but interface said `Result` |
| `TestingLab` | `TestingLab(ITL)` | ✅ Code used `row["TestingLab(ITL)"]` — but interface was wrong |
| `TestDate` | `TestPerformedDate` | ✅ Code used `row.TestPerformedDate` — but interface was wrong |
| `TestComment` | `TestComment` | ✅ Matched |

**Fix:** Updated `RawRow` interface to match actual CSV headers exactly:
```typescript
interface RawRow {
  ProductCategoryType: string;
  ID: string;
  Strain: string;
  'Test Type Name': string;
  TestResult: string;
  'TestingLab(ITL)': string;
  TestPerformedDate: string;
  TestComment: string;
}
```

While the runtime code happened to use bracket notation with the correct names, the TypeScript interface was completely wrong, providing no type safety.

### 3. ❌ Wrong Default CSV Path

**File:** `import-lab-tests.ts`

```
Old: /data/workspace/projects/internal/newsletter/data/ccc/testing-thc-thca.csv
New: /data/workspace/projects/glass/src/data/ccc-raw/testing-thc-thca.csv
```

### 4. ❌ Status Ternary Always Returns 'completed'

**File:** `import-lab-tests.ts`, line ~217

```typescript
// Old (bug): always 'completed' regardless of errors
errors.length > 0 ? 'completed' : 'completed'

// Fixed: properly reports 'failed' when there are errors
errors.length > 0 ? 'failed' : 'completed'
```

### 5. ⚠️ Redundant `|| ""` Expressions

**File:** `import-lab-tests.ts`

```typescript
// Old
const tag = (row["ID"] || "" || '').trim();
const analyte = (row["Test Type Name"] || "" || '').trim().toUpperCase();

// Fixed
const tag = (row.ID || '').trim();
const analyte = (row['Test Type Name'] || '').trim().toUpperCase();
```

### 6. ⚠️ Added Defensive Truncation for Schema Constraints

**File:** `import-lab-tests.ts`

Added `.substring()` guards to prevent varchar overflow:

| Field | Schema Limit | Max Data Length | Guard Added |
|---|---|---|---|
| `testing_lab` | `varchar(10)` | 4 chars (e.g., "LabX") | Yes — truncate to 10 |
| `strain_code` | `varchar(30)` | 11 chars (e.g., "Strain_5733") | Yes — truncate to 30 |
| `metrc_tag` | `varchar(30)` | 24 chars | Yes — truncate to 30 |
| `product_category` | `varchar(30)` | 16 chars (e.g., "InfusedNonEdible") | Yes — truncate to 30 |

Current data fits within constraints, but truncation guards prevent future breakage.

### 7. ⚠️ THCA Check Order in Analyte Matching

**File:** `import-lab-tests.ts`

The original code checked `analyte.includes('THCA') || analyte === 'THCA'` — the `=== 'THCA'` is redundant when `includes('THCA')` is already checked. Simplified to just `analyte.includes('THCA')`, and importantly kept it **before** the THC check since "THCA" also contains "THC".

### 8. ✅ Comment/Documentation Updated

Updated the file header comment to reflect the actual CSV column names instead of the old/wrong ones.

---

## Verification

### Dry Run Results (2026-02-12)

```
Raw rows read:   298,342
Pivoted tags:    147,649
Rows skipped:    0
Rows errored:    0
```

Sample output:
```
Tag: 1A40A030000DBZV7777779DL, Category: Buds, THC: 0.44, THCA: 14.21, Total: 12.902
Tag: 1A40A030000DBZV7777779D9, Category: Buds, THC: 0.43, THCA: 14.16, Total: 12.848
Tag: 1A40A030000DBZV7777779DI, Category: Buds, THC: 0.5, THCA: 14.98, Total: 13.637
```

Total THC formula: `THC + (THCA × 0.877)` ✅

### How to Run

```bash
# Dry run (no DB needed)
cd /data/workspace/projects/glass/src
npx tsx scripts/import/import-lab-tests.ts --dry-run

# Real import
DATABASE_URL=postgres://user:pass@host:5432/glass npx tsx scripts/import/import-lab-tests.ts
```

---

## Architecture Decision: pg.Pool over Drizzle ORM

The etl-base library was rewritten to use `pg.Pool` directly instead of Drizzle ORM because:

1. The `postgres` npm package (postgres.js) required by `db/index.ts` is not installed
2. The import script already uses `pg.Pool` for batch upserts
3. ETL scripts benefit from raw SQL control (batch operations, parameterized upserts)
4. This eliminates a fragile transitive dependency chain through `services/api/src/db/`

The Drizzle ORM setup in `services/api/src/db/index.ts` is untouched — it's used by the API service which presumably has `postgres` installed in its own `node_modules`.
