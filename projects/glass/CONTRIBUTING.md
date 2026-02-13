# CONTRIBUTING.md — GLASS Development Standards

**Read this before touching any code. No exceptions.**

---

## The Law

1. **Never commit to `main` directly.** Feature branches only.
2. **Every change goes through a PR.** No merging your own work.
3. **Every PR gets 2 independent reviews** from different models.
4. **Every agent reads this file** before starting work.
5. **Dead code gets deleted**, not commented out.

---

## Git Workflow

### Branch Naming

```
feat/[description]      — new feature or page
fix/[description]       — bug fix
refactor/[description]  — restructuring without behavior change
chore/[description]     — deps, config, cleanup
docs/[description]      — documentation only
migration/[description] — database schema changes
```

Examples: `feat/consumer-price-api`, `fix/weedmaps-parser-timing`, `migration/add-tax-profiles`

### Working Directory Isolation

Agents MUST work in isolated directories to prevent conflicts:

```
/data/workspace/projects/glass/src/     ← main branch (COO read-only)
/tmp/glass-[agent-label]/               ← agent worktree (isolated)
```

**Setup for each agent:**
```bash
cd /data/workspace/projects/glass/src
git worktree add /tmp/glass-[label] -b [branch-name] main
```

**Agent works in `/tmp/glass-[label]/` only.** Never in the main checkout.

### Commit Messages

Follow Conventional Commits:
```
type(scope): description

[body — what and why, not how]
```

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`, `migration`

Scopes: `scraper`, `api`, `db`, `parser`, `gpid`, `consumer`, `auth`, `infra`

Examples:
```
feat(scraper): add post-interstitial wait for Weedmaps menu hydration
fix(db): add unique constraint on sources.url for upsert safety
migration(db): add store_tax_profiles table for post-tax normalization
refactor(gpid): remove platform prefix from makeSKU for cross-platform matching
```

### PR Process

1. Agent completes work on feature branch
2. Agent pushes branch: `git push origin [branch-name]`
3. Agent writes PR notes (see format below)
4. COO spawns 2 reviewer agents (different models)
5. Reviewers read the diff + PR notes, write review
6. COO synthesizes reviews → approve / request changes / reject
7. **Only COO merges to main** after approval

### PR Notes Format

Every PR must include a file at the repo root: `PR-NOTES-[branch-name].md`

```markdown
# PR: [branch-name]

## What Changed
[2-3 sentences]

## Why
[Link to audit finding, strategy requirement, or bug report]

## Files Changed
| File | Action | What |
|------|--------|------|
| `path/to/file.ts` | Modified | Added X |
| `path/to/new.ts` | Created | New Y component |

## DB Changes
- [ ] Migration file included? (required for any schema change)
- [ ] Migration is idempotent? (uses IF NOT EXISTS, etc.)
- [ ] Rollback possible?

## How to Verify
1. Step-by-step instructions
2. Expected behavior
3. Edge cases to check

## Breaking Changes
- None / [describe what breaks]

## Dependencies
- [ ] No new packages added
- [ ] New package: [name] — [why needed]
```

---

## Database Rules

### Migration Standards

All schema changes go through numbered migration files:

```
scripts/migrations/NNN-description.sql
```

Rules:
- **Always idempotent** — use `IF NOT EXISTS`, `IF EXISTS`, etc.
- **Always include rollback comments** at the bottom
- **Never modify existing migration files** — create a new one
- **Test on a branch DB or local before applying to Railway**
- **Set search_path** at the top: `SET search_path TO glass, public;`

### Migration Tracking

Before applying a migration, check:
```sql
SELECT * FROM glass.migration_log ORDER BY applied_at;
```

After applying:
```sql
INSERT INTO glass.migration_log (filename, applied_by, notes)
VALUES ('NNN-description.sql', 'agent-label', 'what this does');
```

### Schema Boundaries

| Schema | Purpose | Who Writes |
|--------|---------|------------|
| `glass` | GLASS price intelligence (scrapers, products, prices, GPID) | GLASS agents |
| `public` | Cue budtender app (missions, brands, wallets) | Cue agents |
| `drizzle` | Drizzle ORM migration tracking | Drizzle only |

**Never write cross-schema.** If GLASS needs Cue data, create a read-only view.

---

## Code Standards

### TypeScript

- Strict mode always (`"strict": true`)
- No `any` types — use `unknown` + type guards if needed
- All async functions must have error handling
- All external API calls wrapped in try/catch with meaningful errors
- No dead imports, no unused variables

### File Organization

```
scripts/
  lib/           — shared libraries (db, parsers, normalizers, config)
  migrations/    — SQL migration files
  scrape-*.ts    — individual scraper entry points
services/
  api/           — Fastify API service
  intelligence/  — CCC data ingestion (dormant)
migrations/      — matching engine migrations
apps/
  web/           — React frontend
```

### Naming

- Files: `kebab-case.ts`
- Functions: `camelCase` — verb-first (`fetchOperatorData`, `parseWeedmapsMenu`)
- Types/Interfaces: `PascalCase` (`OperatorRecord`, `ScrapedProduct`)
- Constants: `SCREAMING_SNAKE` (`MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT_MS`)
- DB tables: `snake_case` (`canonical_products`, `brand_dictionary`)

### Error Handling

```typescript
// BAD — silent failure
const data = await fetch(url).then(r => r.json()).catch(() => null);

// GOOD — explicit handling
try {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
  const data = await response.json();
} catch (err) {
  console.error(`[scraper] Failed to fetch ${url}:`, err.message);
  throw err; // or handle gracefully with fallback
}
```

---

## Review Standards

Reviewers follow `team/QA.md` severity taxonomy:
- 🔴 **Critical** — blocks merge
- 🟠 **Major** — should fix before merge
- 🟡 **Minor** — nice to fix
- ⚪ **Nit** — style preference

**Merge requirements:**
- Zero 🔴 Critical issues
- All 🟠 Major issues addressed (fixed or justified)
- 2 independent reviews from different models

---

## Dead Code Policy

- If code hasn't been used in 30 days and has no clear future plan → delete it
- `services/scrape/` is DEAD CODE (replaced by `scripts/`). Scheduled for deletion.
- Commented-out code blocks are not allowed in PRs
- "TODO" comments must have a linked issue or task, not just "TODO: fix later"

---

## Testing

Every PR should include verification steps. For code changes:

| Change Type | Minimum Verification |
|-------------|---------------------|
| Parser change | Run parser against 3+ raw snapshots, show output |
| DB migration | Show before/after table structure |
| API route | curl example with expected response |
| Scraper change | Run against 1-2 stores, show results |
| Config change | Show the config diff |

---

## Agent Spawn Template

When the COO spawns an agent for GLASS work:

```javascript
sessions_spawn({
  task: `Read /data/workspace/projects/glass/CONTRIBUTING.md first.
Read /data/workspace/team/DEVELOPER.md for your role.

CONTEXT: [what and why]
TASK: [specific deliverable with success criteria]
BRANCH: Work on branch [name] in worktree /tmp/glass-[label]
OUTPUT: [file paths for deliverables]
PR NOTES: Write PR-NOTES-[branch].md at repo root

Setup:
cd /data/workspace/projects/glass/src
git worktree add /tmp/glass-[label] -b [branch] main
cd /tmp/glass-[label]
[work here]
git add -A && git commit -m "[conventional commit]"
git push origin [branch]`,
  label: "[role]-[task]",
  model: "[model]"
})
```

---

**This file is the standard. If an agent's work doesn't follow it, that's a review failure.**
