# WEEDMAPS Fix Plan (Discovery = 0 Slugs)

## Scope
This plan addresses why `scrape-weedmaps.ts` returns 0 discovered slugs while manual local CamoFox calls work.

Files reviewed:
- `/data/workspace/projects/glass/src/scripts/scrape-weedmaps.ts`
- `/data/workspace/projects/glass/src/scripts/lib/weedmaps-parser.ts`
- `/data/workspace/projects/glass/src/scripts/lib/browser-pool.ts`
- `/data/workspace/projects/glass/src/scripts/lib/config.ts`
- `/tmp/wm-boston-full.txt` (validation fixture referenced in task)

---

## 1) Force local CamoFox for Weedmaps (never Railway)

### Problem
`BrowserPool` currently binds base URL at module load:
- `lib/browser-pool.ts:9` → `const CAMOFOX_BASE = process.env.CAMOFOX_URL || 'http://localhost:9377';`

If global env uses Railway (`https://roviq-browser-production.up.railway.app`), Weedmaps gets datacenter-blocked.

### Implementation plan

#### A. Add a Weedmaps-specific endpoint constant in config
**File:** `/data/workspace/projects/glass/src/scripts/lib/config.ts`

- Add near other environment constants (around lines 31-37):

```ts
export const WEEDMAPS_CAMOFOX_URL = 'http://localhost:9377';
```

Rationale: hard-coded local endpoint for Weedmaps path, independent of generic `CAMOFOX_URL`.

#### B. Refactor BrowserPool to accept runtime options (baseUrl/userId/sessionKey)
**File:** `/data/workspace/projects/glass/src/scripts/lib/browser-pool.ts`

- Replace global constants at lines 9-11 with per-instance config.
- Keep defaults for backward compatibility (Dutchie can still use env/default).

Suggested shape:

```ts
type BrowserPoolOptions = {
  baseUrl?: string;
  userId?: string;
  sessionKey?: string;
};

export class BrowserPool {
  private readonly baseUrl: string;
  private readonly userId: string;
  private readonly sessionKey: string;

  constructor(private readonly maxTabs: number = 3, opts: BrowserPoolOptions = {}) {
    this.baseUrl = opts.baseUrl ?? process.env.CAMOFOX_URL ?? 'http://localhost:9377';
    this.userId = opts.userId ?? 'glass-scraper';
    this.sessionKey = opts.sessionKey ?? 'scrape-session';
  }

  // instance fetch wrapper uses this.baseUrl
}
```

#### C. Instantiate Weedmaps pool with forced local URL
**File:** `/data/workspace/projects/glass/src/scripts/scrape-weedmaps.ts`

- Update `main()` pool creation (line ~311):

```ts
const pool = new BrowserPool(CONCURRENCY, {
  baseUrl: WEEDMAPS_CAMOFOX_URL,
  userId: 'glass-weedmaps',
  sessionKey: `weedmaps-${todayUTC()}`,
});
```

- Add `WEEDMAPS_CAMOFOX_URL` to config import block (lines 5-12).

#### D. Add startup assertion log
In `scrape-weedmaps.ts` right after pool init (line ~314):

```ts
console.log(`[wm] CamoFox endpoint: ${WEEDMAPS_CAMOFOX_URL} (forced local)`);
```

---

## 2) Sequential execution runner (Dutchie first, then Weedmaps)

### Problem
Local CamoFox is effectively single-browser constrained. Parallel use causes tab-create hangs.

### Implementation plan
Create an orchestrator script that runs scrapers serially in one process chain.

### New file
**Create:** `/data/workspace/projects/glass/src/scripts/run-scrapers-sequential.ts`

```ts
#!/usr/bin/env node
import { spawn } from 'child_process';

function run(cmd: string, args: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: 'inherit', env: process.env });
    child.on('exit', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${cmd} ${args.join(' ')} exited with ${code}`));
    });
    child.on('error', reject);
  });
}

async function main() {
  const passArgs = process.argv.slice(2); // optional passthrough
  console.log('[runner] Step 1/2: Dutchie');
  await run('node', ['./dist/scripts/scrape-dutchie.js', ...passArgs]);

  console.log('[runner] Step 2/2: Weedmaps');
  await run('node', ['./dist/scripts/scrape-weedmaps.js', ...passArgs]);

  console.log('[runner] Complete');
}

main().catch((err) => {
  console.error('[runner] failed:', err);
  process.exit(1);
});
```

If executed via `tsx` in dev:

```bash
npx tsx src/scripts/run-scrapers-sequential.ts --db
```

### Optional package script
Add in `/data/workspace/projects/glass/src/package.json`:

```json
{
  "scripts": {
    "scrape:sequential": "tsx src/scripts/run-scrapers-sequential.ts"
  }
}
```

---

## 3) Add progress logging in city + slug discovery

### Current gap
- `discoverWeedmapsCities()` (lines 156-178) has no logs.
- `discoverWeedmapsSlugs()` logs only failures (line 217), no per-city progress/success counts.

### Implementation plan

#### A. City discovery logs
**File:** `scrape-weedmaps.ts`

Add logs in `discoverWeedmapsCities()`:

```ts
console.log(`[wm-discovery] state page: ${WM_STATE_URL}`);
console.log('[wm-discovery] opening tab...');
...
console.log('[wm-discovery] handling age/cookie gate...');
...
console.log(`[wm-discovery] scrolling pass ${i + 1}/6`);
...
console.log(`[wm-discovery] extracted ${matches.length} city-link matches, ${fromFooter.size} unique after seed list merge`);
```

#### B. Slug discovery logs
In `discoverWeedmapsSlugs()` around loop lines 184-222:

```ts
console.log(`[wm-discovery] city ${i + 1}/${citySlugs.length}: ${city}`);
...
console.log(`[wm-discovery] ${city}: ${cityMatches} regex matches, unique slugs total=${map.size}`);
```

Track per-city counts via local `cityMatches` and `newSlugs` counters.

#### C. Final discovery summary log
Before return (line ~224):

```ts
console.log(`[wm-discovery] complete: cities=${citySlugs.length}, uniqueSlugs=${map.size}`);
```

---

## 4) Cookie/age gate reliability hardening

### Current state
`handleWeedmapsAgeGate()` (lines 124-144) is single-pass and silent-fail. If cookie banner appears late, extraction can be blocked.

### Implementation plan
Replace with bounded retry helper that:
1. snapshots
2. clicks age gate if present
3. clicks cookie accept if present
4. repeats until neither appears, max attempts reached

Suggested replacement:

```ts
async function dismissWeedmapsInterstitials(pool: BrowserPool, tabId: string, maxAttempts = 4): Promise<void> {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const snap = await pool.snapshot(tabId);

    const ageRef =
      snap.match(/button "Yes,?\s*let me in!?" \[(e\d+)\]/i)?.[1] ||
      snap.match(/button "[^"]*yes[^"]*let me in[^"]*" \[(e\d+)\]/i)?.[1];

    if (ageRef) {
      console.log(`[wm-gate] attempt ${attempt}: click age gate ${ageRef}`);
      await pool.click(tabId, ageRef);
      await pool.sleep(1200);
      continue;
    }

    const cookieRef =
      snap.match(/button "[^"]*(Accept|Accept All|I Agree|Got it|Close|Dismiss)[^"]*" \[(e\d+)\]/i)?.[2];

    if (cookieRef) {
      console.log(`[wm-gate] attempt ${attempt}: click cookie ${cookieRef}`);
      await pool.click(tabId, cookieRef);
      await pool.sleep(800);
      continue;
    }

    console.log(`[wm-gate] cleared after ${attempt} attempt(s)`);
    return;
  }

  console.warn('[wm-gate] max attempts reached; proceeding');
}
```

Then replace all `handleWeedmapsAgeGate(...)` calls with `dismissWeedmapsInterstitials(...)` at:
- city discovery (line ~161)
- per-city slug discovery (line ~192)
- store scrape worker (line ~399)

---

## 5) Retry logic for CamoFox tab creation (30s timeout + exponential backoff)

### Current gap
`createTab()` in `browser-pool.ts` (lines 70-76) is a single call with global 45s timeout. If CamoFox is contended, tab creation can stall.

### Implementation plan

#### A. Add per-call timeout support in fetch wrapper
In `browser-pool.ts` update fetch helper signature:

```ts
async function camofoxFetch<T>(path: string, options?: RequestInit, timeoutMs = FETCH_TIMEOUT_MS): Promise<T>
```

Use `timeoutMs` for AbortController timer.

#### B. Implement retry in `createTab()`

```ts
async createTab(url: string): Promise<string> {
  const attempts = 4;
  let delayMs = 1000;

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const result = await this.camofoxFetch<TabResult>(
        '/tabs',
        {
          method: 'POST',
          body: JSON.stringify({ userId: this.userId, sessionKey: this.sessionKey, url }),
        },
        30_000,
      );
      return result.tabId;
    } catch (err) {
      const isLast = attempt === attempts;
      console.warn(`[camofox] createTab failed attempt ${attempt}/${attempts}: ${String(err)}`);
      if (isLast) throw err;
      await this.sleep(delayMs);
      delayMs *= 2; // 1s, 2s, 4s
    }
  }

  throw new Error('unreachable');
}
```

(If keeping helper as free function, pass base URL and timeout similarly.)

---

## 6) Weedmaps product parser validation (`extractWeedmapsProductsFromSnapshot`)

### What was validated now
Fixture file provided in task: `/tmp/wm-boston-full.txt`

Observed:
- It is a **city dispensary listing** snapshot (contains `/dispensaries/<slug>` links).
- It contains **0** `/dispensaries/<slug>/menu/...` links.
- Current extractor in `weedmaps-parser.ts:151-193` only captures rows with `/menu/` hrefs, so expected output is 0 on this fixture.

This means parser is not necessarily broken; fixture type does not match parser input contract.

### Implementation plan for robust validation

#### A. Keep parser contract explicit
At top of `extractWeedmapsProductsFromSnapshot()` add doc comment:
- expects **menu page** snapshot (product cards)
- city/store listing snapshots are out-of-scope and should return 0

#### B. Add two fixture tests
**File:** `/data/workspace/projects/glass/src/scripts/test-weedmaps-parser.ts`

1. Positive fixture (existing menu snapshot) should return `raw.length > 0`.
2. Negative fixture (`/tmp/wm-boston-full.txt` copied into repo fixtures) should return `raw.length === 0`.

Snippet:

```ts
const cityListing = readFileSync(path.join(fixtureDir, 'weedmaps-boston-city-listing.snapshot.txt'), 'utf8');
const cityRaw = extractWeedmapsProductsFromSnapshot(cityListing);
console.log(`city listing raw=${cityRaw.length} (expected 0)`);
```

#### C. Add one live smoke parser check in Weedmaps script
After first page snapshot in `scrapePaginatedMenu()` (line ~235):

```ts
if (page1Count === 0) {
  console.warn(`[wm:${slug}] page 1 parsed 0 products; possible gate/block/layout shift`);
}
```

---

## 7) Verification test plan before full 235-store run

## Phase A — connectivity & contention
1. **Force-local proof:** run Weedmaps discovery and confirm startup log prints local endpoint only.
   - Expect: `[wm] CamoFox endpoint: http://localhost:9377 (forced local)`
2. **No parallel contention:** run new sequential runner.
   - Expect Dutchie fully exits before Weedmaps starts.
   - No hanging `createTab` calls.

## Phase B — discovery quality
3. Run Weedmaps discovery only:

```bash
npx tsx src/scripts/scrape-weedmaps.ts --dry-run
```

Expectations:
- `discoverWeedmapsCities()` logs scroll and extraction counts.
- Per-city logs show regex match counts.
- Final unique slug count > 0 (Boston alone should yield many).

4. Spot-check saved slugs file:
- `/data/workspace/projects/glass/src/scripts/weedmaps-slugs.json`
- confirm includes known Boston slugs (`new-dia-fenway-llc`, etc.)

## Phase C — gate handling
5. Run discovery 3 times in a row.
- Expect no 0-slug runs caused by cookie wall.
- Logs should show gate dismissal actions when banner appears.

## Phase D — createTab retry behavior
6. Simulate temporary CamoFox unavailability (stop/restart service briefly) and run discovery.
- Expect retry warnings with exponential backoff.
- Recovery succeeds without immediate fatal exit when service returns.

## Phase E — parser validation
7. Run parser test script:

```bash
npx tsx src/scripts/test-weedmaps-parser.ts
```

Expectations:
- Menu fixtures: non-zero parsed products.
- City listing fixture: zero parsed products (by design).

## Phase F — controlled mini scrape
8. Run 5-store Weedmaps scrape with DB off:

```bash
npx tsx src/scripts/scrape-weedmaps.ts --skip-discovery --slugs-file src/scripts/test-slugs.json --limit 5
```

Expect:
- Per-store logs show page progression.
- No systemic 0-product failures.
- Raw snapshots saved under `raw-snapshots/<date>/`.

## Phase G — production run gate
9. Run sequential production scrape (Dutchie then Weedmaps) after Phases A–F pass.
10. Monitor summary JSON outputs and error logs; only proceed to full 235-store run if:
- discovery slugs stable,
- createTab retries are rare/transient,
- 0-product store failure rate is within acceptable baseline.

---

## Exact change map (by file)

1. `/data/workspace/projects/glass/src/scripts/lib/config.ts`
- Add `WEEDMAPS_CAMOFOX_URL` near env constants (around lines 31-37).

2. `/data/workspace/projects/glass/src/scripts/lib/browser-pool.ts`
- Refactor global constants (lines 9-11) into constructor options.
- Add per-call timeout support in fetch helper (lines 37-55).
- Add retry/backoff around `createTab` (lines 70-76).

3. `/data/workspace/projects/glass/src/scripts/scrape-weedmaps.ts`
- Import and use `WEEDMAPS_CAMOFOX_URL` (import block lines 5-12).
- Update `new BrowserPool(...)` instantiation (line ~311).
- Replace `handleWeedmapsAgeGate` with robust interstitial dismissor (lines 124-144 and call sites at ~161, ~192, ~399).
- Add detailed logs in `discoverWeedmapsCities` (156-178) and `discoverWeedmapsSlugs` (180-225).
- Add parser smoke warning in `scrapePaginatedMenu` around line ~252.

4. `/data/workspace/projects/glass/src/scripts/run-scrapers-sequential.ts` (new)
- Serially run Dutchie then Weedmaps to avoid CamoFox contention.

5. `/data/workspace/projects/glass/src/scripts/test-weedmaps-parser.ts`
- Add city-listing negative fixture assertion/log and keep menu positive checks.

---

## Rollout order
1. BrowserPool refactor + createTab retries
2. Weedmaps forced-local endpoint + dedicated userId/session
3. Gate dismissal hardening
4. Discovery logging
5. Sequential runner
6. Parser fixture validation updates
7. Mini-run verification, then full run
