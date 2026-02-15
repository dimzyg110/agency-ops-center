# GLASS UX & Recommendation Engine Redesign

**Date:** 2026-02-12
**Triggered by:** Randy's feedback on Morning Brief pricing recommendations
**Status:** Design spec — ready for implementation

---

## Executive Summary

The current recommendation engine and Report Card use **naive price-matching logic**: "you're above market → lower price." This is actively harmful to operator trust. Randy's core insight:

> "At the end of the day people want to make more money, save money, or get more customers."

Every recommendation must answer: **"What do I GAIN by doing this?"**

This document covers:
1. **Recommendation Engine Redesign** — new logic, new language, new framing
2. **Report Card Rewrite** — category suggestions that think like an operator
3. **UX Cleanup** — navigation, empty states, information architecture
4. **Implementation Plan** — prioritized file-by-file changes

---

## Part 1: Recommendation Engine Redesign

### The Problem

Current logic in `generator.ts`:

```typescript
// Current: naive "move toward market average"
let recommendedPrice = currentPrice + (marketAvg - currentPrice) * 0.5;
// ...
const rationale =
  `Current price ($${currentPrice.toFixed(2)}) is ${absPctDiff}% ${direction} ` +
  `the market average ($${marketAvg.toFixed(2)}). ` +
  `Recommending $${recommendedPrice.toFixed(2)} to improve competitiveness.`;
```

This produces: *"Consider lowering by $10"* — which is insulting to an operator who may be charging premium prices intentionally and successfully.

### New Recommendation Framework

#### Core Principle: **Two Paths, One Goal**

Every recommendation presents **two strategic options** because we don't know the operator's sales velocity (yet). Both options should feel like opportunities.

#### When YOU > MARKET (Premium Position)

**Old:** "Consider lowering by $4"
**New:**

```
PREMIUM POSITION: Edibles at $22.90 (Market: $19.22)

🟢 OPTION A — Hold & Maximize Margin
You're capturing $3.68 more per unit than competitors. If your edibles
are moving well, you're earning premium margin others can't.
→ Estimated extra margin: ~$X/week at current volume

🟡 OPTION B — Capture Volume
Nearby customers shopping on price may be going to competitors.
A $2 promotional drop could pull traffic without giving up your
premium position.
→ Potential new customers: competitors' price-sensitive shoppers
```

**Key language changes:**
- "Premium position" not "overpriced"
- Lead with what they're GAINING (extra margin per unit)
- Second option is a "promotional drop" not a "price cut"
- Both options are valid strategies
- Never assume lowering price is the right move

#### When YOU < MARKET (Money Left on the Table)

**Old:** "You may have room to raise by $4"
**New:**

```
💰 OPPORTUNITY: Flower at $31.99 (Market: $35.88)

You're leaving $3.89 on the table per unit. The market supports
higher pricing — your customers are already paying you $4 less
than they'd pay next door.

Raising to $34.00 could add ~$X/week with minimal volume impact.
Even a $2 bump to $33.99 adds ~$Y/week.

→ This is free money. Your customers already chose you.
```

**Key language changes:**
- Lead with dollar amount of opportunity, not percentage
- "Free money" framing — customers already chose this store
- Give two price points (full adjustment, partial adjustment)
- Quantify weekly dollar impact, not percentages
- Frame as upside, not criticism of current pricing

#### When ON TARGET (Within 10%)

**Old:** "On target" (one line, no value)
**New:**

```
✅ COMPETITIVE: Concentrates at $45.00 (Market: $46.59)

Your pricing is dialed in. You're competitive without leaving money
on the table. Focus on inventory freshness and customer experience
to win on factors beyond price.

→ No action needed. You're in the sweet spot.
```

**Key language changes:**
- Affirm their strategy is working
- Redirect to non-price differentiation
- Still feels valuable (confirmation has value)

### New Data Model Additions

The recommendation needs richer context. Add to the `factors` JSONB column:

```typescript
interface RecommendationFactors {
  market_avg: number;
  pct_diff_from_market: number;
  elasticity_estimate: ElasticityEstimate;
  // NEW fields:
  position: 'premium' | 'value' | 'competitive';  // replaces above/below/on-target
  weekly_margin_at_current: number;      // estimated $/week at current price
  weekly_margin_at_recommended: number;  // estimated $/week at recommended price
  weekly_margin_delta: number;           // the GAIN in dollars
  hold_rationale: string;               // why holding current price could be smart
  adjust_rationale: string;             // why adjusting could be smart
  confidence_factors: string[];          // what data supports this recommendation
}
```

### New Rationale Builder

Replace the single-line rationale with structured messaging:

```typescript
function buildRationale(
  currentPrice: number,
  marketAvg: number,
  category: string,
  pctDiff: number,
  weeklyVolume: number,
): { headline: string; hold_option: string; adjust_option: string; bottom_line: string } {
  const absDiff = Math.abs(currentPrice - marketAvg);
  const absDiffRounded = Math.round(absDiff);

  if (pctDiff > 0.10) {
    // PREMIUM POSITION
    const weeklyExtra = Math.round(absDiff * weeklyVolume);
    return {
      headline: `Premium Position: ${category} at $${currentPrice.toFixed(2)} (Market: $${marketAvg.toFixed(2)})`,
      hold_option: `You're capturing $${absDiff.toFixed(2)} more per unit than competitors. ` +
        `If ${category.toLowerCase()} is moving well, that's ~$${weeklyExtra}/week in extra margin others aren't getting.`,
      adjust_option: `If movement is slow, a $${Math.round(absDiff * 0.5)} promotional adjustment could ` +
        `pull price-sensitive customers from nearby competitors without giving up your premium positioning.`,
      bottom_line: `Your call — premium margin or volume play. Both are valid strategies.`,
    };
  } else if (pctDiff < -0.10) {
    // MONEY ON THE TABLE
    const fullBump = Math.round(absDiff);
    const halfBump = Math.round(absDiff * 0.5);
    const weeklyGainFull = Math.round(absDiff * weeklyVolume);
    const weeklyGainHalf = Math.round(absDiff * 0.5 * weeklyVolume);
    return {
      headline: `Opportunity: ${category} at $${currentPrice.toFixed(2)} (Market: $${marketAvg.toFixed(2)})`,
      hold_option: `You're priced $${absDiff.toFixed(2)}/unit below market. If you're using low prices ` +
        `to drive traffic, that's a deliberate strategy. Just make sure the volume justifies it.`,
      adjust_option: `Raising by $${fullBump} could add ~$${weeklyGainFull}/week. ` +
        `Even a $${halfBump} bump adds ~$${weeklyGainHalf}/week. ` +
        `Your customers already chose you — the market supports higher pricing.`,
      bottom_line: `This is potential margin you're leaving on the table every week.`,
    };
  } else {
    // COMPETITIVE / ON TARGET
    return {
      headline: `Competitive: ${category} at $${currentPrice.toFixed(2)} (Market: $${marketAvg.toFixed(2)})`,
      hold_option: `Your pricing is dialed in. You're competitive without leaving money on the table.`,
      adjust_option: `Focus on inventory freshness, product mix, and customer experience to win on ` +
        `factors beyond price.`,
      bottom_line: `No price action needed. You're in the sweet spot.`,
    };
  }
}
```

---

## Part 2: Report Card Suggestion Rewrite

### Current Broken Logic

**File:** `src/services/api/src/routes/report-card.ts` (lines ~213-230)

```typescript
// CURRENT — the exact code that produces the bad suggestions
if (diffPct > 15) {
  status = 'red';
  suggestion = `Consider lowering by ${formatCurrency(Math.max(1, yourAvg - marketAvg))}`;
} else if (diffPct > 10) {
  status = 'yellow';
  suggestion = `Consider lowering by ${formatCurrency(Math.max(1, yourAvg - marketAvg))}`;
} else if (diffPct < -15) {
  status = 'red';
  suggestion = `You're likely underpriced. Consider raising by ${formatCurrency(Math.max(1, marketAvg - yourAvg))}`;
} else if (diffPct < -10) {
  status = 'yellow';
  suggestion = `You may have room to raise by ${formatCurrency(Math.max(1, marketAvg - yourAvg))}`;
}
```

### New Suggestion Logic

```typescript
function buildCategorySuggestion(
  category: string,
  yourAvg: number,
  marketAvg: number,
  diffPct: number,
  productCount: number,
): { status: Status; suggestion: string } {
  const absDiff = Math.abs(yourAvg - marketAvg);
  const absDiffStr = formatCurrency(Math.max(1, absDiff));
  const weeklyVolumeEstimate = Math.max(1, productCount * 2);
  const weeklyDollar = formatCurrency(Math.round(absDiff * weeklyVolumeEstimate));

  if (diffPct > 15) {
    return {
      status: 'yellow', // NOT red — premium pricing isn't inherently bad
      suggestion: `Premium position (+${absDiffStr}/unit over market). ` +
        `If sales are strong, you're earning margin others can't. ` +
        `If movement is slow, a targeted promo could pull competitor traffic.`,
    };
  } else if (diffPct > 10) {
    return {
      status: 'yellow',
      suggestion: `Slightly above market (+${absDiffStr}/unit). ` +
        `Strong sales? You're capturing premium margin. ` +
        `Slow movement? A small adjustment could boost volume.`,
    };
  } else if (diffPct < -15) {
    return {
      status: 'red', // Leaving significant money on the table IS urgent
      suggestion: `You're leaving ~${absDiffStr}/unit on the table. ` +
        `Raising toward market could add ~${weeklyDollar}/week. ` +
        `Your customers already chose you — the market supports more.`,
    };
  } else if (diffPct < -10) {
    return {
      status: 'yellow',
      suggestion: `Room to earn more (~${absDiffStr}/unit below market). ` +
        `Even a small bump could add ~${weeklyDollar}/week without losing customers.`,
    };
  } else {
    return {
      status: 'green',
      suggestion: 'Competitive pricing. Focus on experience and product mix to differentiate.',
    };
  }
}
```

### Key Changes in Suggestion Tone

| Scenario | Old | New |
|----------|-----|-----|
| YOU > MARKET by 19% | ❌ "Consider lowering by $4" | ✅ "Premium position (+$4/unit). If sales are strong, you're earning margin others can't." |
| YOU > MARKET by 28% | ❌ "Consider lowering by $10" | ✅ "Premium position (+$10/unit). If sales are strong, you're earning margin others can't. If movement is slow, a targeted promo could pull competitor traffic." |
| YOU < MARKET by 11% | ❌ "You may have room to raise by $4" | ✅ "Room to earn more (~$4/unit below market). Even a small bump could add ~$X/week without losing customers." |
| YOU < MARKET by 31% | ❌ "You're likely underpriced. Consider raising by $7" | ✅ "You're leaving ~$7/unit on the table. Raising toward market could add ~$X/week. Your customers already chose you." |
| On target | ❌ "On target" | ✅ "Competitive pricing. Focus on experience and product mix to differentiate." |

### Color Coding Redesign

Current logic marks `>15% above market` as **red** (danger). This is wrong. Being premium isn't dangerous. Being underpriced IS leaving money on the table.

**New color semantics:**

| Color | Meaning | When |
|-------|---------|------|
| 🟢 Green | You're in a good spot | Within ±10% of market |
| 🟡 Yellow | Worth monitoring | 10-20% above OR 10-15% below market |
| 🔴 Red | Action likely needed | >20% above (may be losing customers) OR >15% below (significant money left on table) |

Critical shift: **Red for overpriced only triggers at >20%**, not 15%. Premium positioning up to 20% is a valid strategy. But being 15%+ below market is always urgent — that's free money walking out the door.

### "Estimated Opportunity" Fix

Current code in `report-card.ts`:

```typescript
const moneyOpportunityRaw = over10.reduce((sum, category) => {
  const unitDelta = Math.max(0, category.your_avg - category.market_avg);
  const estimatedWeeklyVolume = Math.max(1, category.product_count * 2);
  return sum + unitDelta * estimatedWeeklyVolume;
}, 0);
```

**Problem:** This calculates "opportunity" as the money you'd lose by lowering prices. That's backwards. The opportunity should be money you could GAIN.

**Fix:** Opportunity = money left on table from underpriced categories + potential volume gain from overpriced categories with slow movement.

```typescript
// NEW: Opportunity = underpriced margin recovery + competitive positioning value
const underpriced = rawCategories.filter((c) => c.diff_pct < -10);
const moneyOnTable = underpriced.reduce((sum, cat) => {
  const perUnitGain = Math.abs(cat.your_avg - cat.market_avg);
  const weeklyVolume = Math.max(1, cat.product_count * 2);
  return sum + perUnitGain * weeklyVolume;
}, 0);

const moneyOpportunity = moneyOnTable > 0 ? Math.round(moneyOnTable) : null;
```

Now the number represents **money the operator could ADD to their revenue**, not money they should give up. The label should also change:

**Old:** "Estimated opportunity: ~$1,028/week"
**New:** "Potential additional margin: ~$1,028/week from underpriced categories"

### Action Items Rewrite

Current in `report-card.ts`:

```typescript
actions.push({
  priority: category.diff_pct > 15 ? 'high' : 'medium',
  text: `Lower your ${category.category} price by about ${formatCurrency(drop)} to match nearby stores.`,
  estimated_impact: `${formatCurrency(impact)}/week`,
});
```

**New:**

```typescript
// For overpriced categories
actions.push({
  priority: 'medium', // Never 'high' for overpriced — it's a choice, not a problem
  text: `Your ${category.category} pricing is ${formatCurrency(absDiff)}/unit above market. ` +
    `If sales are strong, you're earning premium margin. ` +
    `If movement is slow, a targeted promotion could attract nearby shoppers.`,
  estimated_impact: `Monitor sales velocity`,
});

// For underpriced categories
actions.push({
  priority: category.diff_pct < -15 ? 'high' : 'medium',
  text: `Your ${category.category} is priced ${formatCurrency(absDiff)}/unit below market. ` +
    `Raising to market level could add ~${formatCurrency(weeklyGain)}/week. ` +
    `Your customers already chose you — they'll likely stay.`,
  estimated_impact: `+${formatCurrency(weeklyGain)}/week`,
});
```

---

## Part 3: UX Cleanup

### 3.1 Navigation Simplification

**Current sidebar:** 7 nav items + 3 tools + Settings = **11 items**

An operator opening this at 7am wants 1-2 things: "How am I doing?" and "What should I do?"

**Proposed navigation (Phase 1):**

| Item | Keep/Remove | Reasoning |
|------|-------------|-----------|
| Morning Brief | ✅ Keep (rename to "Dashboard") | Primary view — everything starts here |
| Price Wire | ✅ Keep | Core value prop — real competitive data |
| Threat Radar | ✅ Keep | Unique value — license threats |
| Competitors | 🟡 Merge into Dashboard | Move key stats into Report Card |
| Geography | ❌ Hide (v2) | Requires more data to be useful |
| Recommendations | 🟡 Merge into Dashboard | Surface top 3 on Morning Brief, remove separate page |
| Alerts | ✅ Keep | Essential for notifications |
| Virtual Budtender | ✅ Keep | Revenue product |
| Cue | ✅ Keep | Revenue product |
| Delivery | ❌ Hide (v2) | Not built yet |

**Result: 7 items → 5 nav + 2 tools = 7 items**, but more focused.

### 3.2 Morning Brief Page Restructure

The current Morning Brief is **too long**. It has:
1. Header + Data Freshness
2. Welcome banner
3. Report Card (expandable, 4 sections)
4. FlywheelCTA (conditional)
5. Hero Stats (4 cards)
6. 6 D3 visualizations (BrandTreemap, CategorySunburst, EconomicIndicators, StrainStream, MarketSizeChart, CategoryGrowthCurves)
7. FlywheelCTA
8. Price Wire + Threat Radar (2 columns)
9. Recommendations + Alerts (3 columns)
10. Quick Actions (4 links)

**That's 10+ sections.** An operator scrolling through this at 7am will bounce.

**Proposed structure:**

```
┌─────────────────────────────────────────────┐
│  HEADER: "Good morning, [Name]"             │
│  Subtitle: Feb 12, 2026 • Data fresh ✓      │
├─────────────────────────────────────────────┤
│  REPORT CARD (always expanded pricing)       │
│  ├── Pricing: 5 category cards              │
│  ├── Top Actions: 1-3 actionable items      │
│  └── Competition summary (inline)           │
├─────────────────────────────────────────────┤
│  PRICE WIRE: Top 5 movers (compact)         │
│  THREAT RADAR: Recent threats (compact)     │
├─────────────────────────────────────────────┤
│  ALERTS: Unread count + top 3               │
└─────────────────────────────────────────────┘
```

**Remove from Morning Brief:**
- All 6 D3 visualizations → Move to a dedicated "Market" page (already exists at `/market`)
- Hero stat cards (redundant with Report Card)
- Quick Actions section (redundant with sidebar)
- Multiple FlywheelCTAs (keep one, tasteful)
- Welcome banner (show once, then gone)

### 3.3 Report Card — Pricing Section Default Expanded

Currently all 4 sections of the Report Card are **collapsed by default**. The most valuable section (Pricing) should be **expanded by default** since that's the #1 thing operators check.

### 3.4 Color Coding Overhaul

**Current:** Green = on track, Yellow = watch, Red = needs attention
**Problem:** "Needs attention" for being premium-priced sends the wrong signal

**New color semantics across the entire app:**

| Color | Semantic | Icon | Examples |
|-------|----------|------|----------|
| 🟢 Green | Opportunity to capture / Doing well | `$` or `✓` | "You could earn $X more/week", "On target" |
| 🟡 Yellow | Monitor / Your call | `👁` or `⚡` | "Premium positioning — watch sales velocity" |
| 🔴 Red | Urgent / Leaving significant money on table | `!` | ">15% below market", "3 new competitor applications" |

### 3.5 Empty State Audit

Pages that may show empty/broken states and how to handle them:

| Page | Empty State Risk | Fix |
|------|-----------------|-----|
| Price Wire | No movers if <2 days of data | ✅ Already handled with "check back soon" message |
| Threat Radar | No threats in area | Add: "No threats detected. We're watching for you." |
| Competitors | Needs operator comparison data | Add: "We're building your competitor profile. Check back in 24h." |
| Geography | Needs geo data | **Hide from nav entirely** until data exists |
| Recommendations | No pending recs | ✅ Already handled |
| Alerts | No alerts | Add: "All clear. We'll notify you when something needs attention." |
| Delivery | Not built | **Hide from nav entirely** |

---

## Part 4: Implementation Plan

### P0 — This Week (Critical Path)

These changes directly address Randy's feedback and should ship before any demos.

#### Change 1: Report Card Suggestion Text
**File:** `src/services/api/src/routes/report-card.ts`
**Lines:** ~213-230 (the `if (diffPct > 15)` block)
**What:** Replace the entire suggestion-generation block with the new `buildCategorySuggestion` function.

**Find:**
```typescript
    let status: Status = 'green';
    let suggestion = 'On target';

    if (diffPct > 15) {
      status = 'red';
      suggestion = `Consider lowering by ${formatCurrency(Math.max(1, yourAvg - marketAvg))}`;
    } else if (diffPct > 10) {
      status = 'yellow';
      suggestion = `Consider lowering by ${formatCurrency(Math.max(1, yourAvg - marketAvg))}`;
    } else if (diffPct < -15) {
      status = 'red';
      suggestion = `You're likely underpriced. Consider raising by ${formatCurrency(Math.max(1, marketAvg - yourAvg))}`;
    } else if (diffPct < -10) {
      status = 'yellow';
      suggestion = `You may have room to raise by ${formatCurrency(Math.max(1, marketAvg - yourAvg))}`;
    }
```

**Replace with:**
```typescript
    let status: Status = 'green';
    let suggestion = 'Competitive pricing. Focus on experience and product mix to differentiate.';

    const absDiffStr = formatCurrency(Math.max(1, Math.abs(yourAvg - marketAvg)));
    const weeklyVolumeEstimate = Math.max(1, toNumber(row.product_count) * 2);
    const weeklyDollarStr = formatCurrency(Math.round(Math.abs(yourAvg - marketAvg) * weeklyVolumeEstimate));

    if (diffPct > 20) {
      status = 'yellow';
      suggestion = `Premium position (+${absDiffStr}/unit over market). ` +
        `If sales are strong, you're earning margin others can't. ` +
        `If movement is slow, a targeted promo could pull competitor traffic.`;
    } else if (diffPct > 10) {
      status = 'yellow';
      suggestion = `Slightly above market (+${absDiffStr}/unit). ` +
        `Strong demand? You're capturing premium margin. ` +
        `Slow movement? A small adjustment could boost volume.`;
    } else if (diffPct < -15) {
      status = 'red';
      suggestion = `You're leaving ~${absDiffStr}/unit on the table. ` +
        `Raising toward market could add ~${weeklyDollarStr}/week. ` +
        `Your customers already chose you — the market supports more.`;
    } else if (diffPct < -10) {
      status = 'yellow';
      suggestion = `Room to earn more (~${absDiffStr}/unit below market). ` +
        `Even a small bump could add ~${weeklyDollarStr}/week without losing customers.`;
    }
```

**Priority:** P0
**Risk:** Low — text change only, no data model changes
**Test:** Load report card for an operator with both over- and under-priced categories, verify new language appears.

---

#### Change 2: Report Card Action Items
**File:** `src/services/api/src/routes/report-card.ts`
**Lines:** ~263-280 (the actions-building loop)
**What:** Replace the "Lower your X price" actions with opportunity-framed actions.

**Find:**
```typescript
  for (const category of rawCategories
    .filter((c) => c.diff_pct > 10)
    .sort((a, b) => b.diff_pct - a.diff_pct)
    .slice(0, 2)) {
    const drop = Math.max(1, Math.round(category.your_avg - category.market_avg));
    const impact = Math.max(25, Math.round((category.your_avg - category.market_avg) * Math.max(1, category.product_count * 2)));
    actions.push({
      priority: category.diff_pct > 15 ? 'high' : 'medium',
      text: `Lower your ${category.category} price by about ${formatCurrency(drop)} to match nearby stores.`,
      estimated_impact: `${formatCurrency(impact)}/week`,
    });
  }
```

**Replace with:**
```typescript
  // Underpriced categories — biggest opportunity (money on the table)
  for (const category of rawCategories
    .filter((c) => c.diff_pct < -10)
    .sort((a, b) => a.diff_pct - b.diff_pct)
    .slice(0, 2)) {
    const gap = Math.max(1, Math.round(Math.abs(category.your_avg - category.market_avg)));
    const weeklyGain = Math.max(25, Math.round(Math.abs(category.your_avg - category.market_avg) * Math.max(1, category.product_count * 2)));
    actions.push({
      priority: category.diff_pct < -15 ? 'high' : 'medium',
      text: `Your ${category.category} is priced ${formatCurrency(gap)}/unit below market. ` +
        `Raising toward market could add ~${formatCurrency(weeklyGain)}/week. ` +
        `Your customers already chose you — they'll likely stay.`,
      estimated_impact: `+${formatCurrency(weeklyGain)}/week`,
    });
  }

  // Overpriced categories — monitor, don't panic
  for (const category of rawCategories
    .filter((c) => c.diff_pct > 15)
    .sort((a, b) => b.diff_pct - a.diff_pct)
    .slice(0, 1)) {
    actions.push({
      priority: 'medium',
      text: `Your ${category.category} is ${formatCurrency(Math.round(category.your_avg - category.market_avg))}/unit above market. ` +
        `If sales are strong, you're earning premium margin. ` +
        `If movement is slow, consider a targeted promotion.`,
      estimated_impact: `Monitor velocity`,
    });
  }
```

**Priority:** P0
**Risk:** Low — text change only

---

#### Change 3: Estimated Opportunity Calculation
**File:** `src/services/api/src/routes/report-card.ts`
**Lines:** ~237-244 (moneyOpportunityRaw calculation)
**What:** Flip the calculation to show money GAINED from underpriced categories, not money lost from lowering prices.

**Find:**
```typescript
  const moneyOpportunityRaw = over10.reduce((sum, category) => {
    const unitDelta = Math.max(0, category.your_avg - category.market_avg);
    const estimatedWeeklyVolume = Math.max(1, category.product_count * 2);
    return sum + unitDelta * estimatedWeeklyVolume;
  }, 0);

  const moneyOpportunity = moneyOpportunityRaw > 0 ? Math.round(moneyOpportunityRaw) : null;
```

**Replace with:**
```typescript
  // Opportunity = margin recovery from underpriced categories
  const under10 = rawCategories.filter((c) => c.diff_pct < -10);
  const moneyOpportunityRaw = under10.reduce((sum, category) => {
    const perUnitGain = Math.abs(category.your_avg - category.market_avg);
    const estimatedWeeklyVolume = Math.max(1, category.product_count * 2);
    return sum + perUnitGain * estimatedWeeklyVolume;
  }, 0);

  const moneyOpportunity = moneyOpportunityRaw > 0 ? Math.round(moneyOpportunityRaw) : null;
```

**Priority:** P0
**Risk:** Low — changes what the dollar number represents. The label in the frontend also needs updating (see Change 4).

---

#### Change 4: Opportunity Label in Frontend
**File:** `src/apps/web/src/components/ReportCard.tsx`
**Lines:** Inside the pricing section expansion (search for `money_opportunity`)
**What:** Update the label to explain what the number means.

**Find:**
```tsx
              {pricing.money_opportunity != null && pricing.money_opportunity > 0 && (
                <div className="flex items-center gap-2 rounded-lg border border-glass-accent/25 bg-glass-accent/5 p-3">
                  <DollarSign className="h-4 w-4 text-glass-accent shrink-0" strokeWidth={1.5} />
                  <span className="text-xs text-glass-muted">
                    Estimated opportunity:{' '}
                    <span className="font-mono font-medium text-glass-accent">
                      ~{formatPrice(pricing.money_opportunity)}/week
                    </span>
                  </span>
                </div>
              )}
```

**Replace with:**
```tsx
              {pricing.money_opportunity != null && pricing.money_opportunity > 0 && (
                <div className="flex items-center gap-2 rounded-lg border border-emerald-500/25 bg-emerald-500/5 p-3">
                  <DollarSign className="h-4 w-4 text-emerald-400 shrink-0" strokeWidth={1.5} />
                  <span className="text-xs text-glass-muted">
                    Potential extra margin from underpriced categories:{' '}
                    <span className="font-mono font-medium text-emerald-400">
                      ~{formatPrice(pricing.money_opportunity)}/week
                    </span>
                  </span>
                </div>
              )}
```

**Priority:** P0
**Risk:** Minimal — UI text + color change

---

#### Change 5: Report Card Pricing Section Default Expanded
**File:** `src/apps/web/src/components/ReportCard.tsx`
**What:** Initialize the pricing section as expanded.

**Find:**
```tsx
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
```

**Replace with:**
```tsx
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({ pricing: true });
```

**Priority:** P0
**Risk:** Minimal

---

### P1 — Next Week

#### Change 6: Generator Engine Rationale Overhaul
**File:** `src/services/api/src/engine/generator.ts`
**What:** Replace the single-line rationale with structured two-option messaging.

Replace the rationale building section (~line 85-90):

**Find:**
```typescript
      const direction = pctDiff > 0 ? 'above' : 'below';
      const absPctDiff = Math.abs(Math.round(pctDiff * 100));
      const rationale =
        `Current price ($${currentPrice.toFixed(2)}) is ${absPctDiff}% ${direction} ` +
        `the market average ($${marketAvg.toFixed(2)}). ` +
        `Recommending $${recommendedPrice.toFixed(2)} to improve competitiveness.`;
```

**Replace with:**
```typescript
      const absDiff = Math.abs(currentPrice - marketAvg);
      const estimatedWeeklyVolume = 10; // Conservative baseline until we have real sales data
      let rationale: string;

      if (pctDiff > 0) {
        // Premium position
        const weeklyExtra = Math.round(absDiff * estimatedWeeklyVolume);
        rationale =
          `Premium position: $${currentPrice.toFixed(2)} is $${absDiff.toFixed(2)}/unit above ` +
          `market avg ($${marketAvg.toFixed(2)}). If sales are strong, you're capturing ` +
          `~$${weeklyExtra}/week in extra margin. If movement is slow, adjusting to ` +
          `$${recommendedPrice.toFixed(2)} could increase volume while keeping above-market positioning.`;
      } else {
        // Money on the table
        const weeklyGain = Math.round(absDiff * estimatedWeeklyVolume);
        rationale =
          `Opportunity: $${currentPrice.toFixed(2)} is $${absDiff.toFixed(2)}/unit below ` +
          `market avg ($${marketAvg.toFixed(2)}). Raising to $${recommendedPrice.toFixed(2)} ` +
          `could add ~$${weeklyGain}/week. Your customers already chose you — ` +
          `the market supports higher pricing.`;
      }
```

**Priority:** P1
**Risk:** Medium — changes recommendation text in the database for new recommendations. Existing pending recommendations keep old text.

---

#### Change 7: RecommendationCard UI — Show Two Options
**File:** `src/apps/web/src/components/RecommendationCard.tsx`
**What:** Instead of showing one recommended price, show the context of both options.

In the Rationale section, enhance the display:

**Find:**
```tsx
      {/* Rationale */}
      <div className="mt-5 rounded-lg bg-glass-elevated/50 p-4">
        <p className="text-sm text-glass-muted leading-relaxed">{recommendation.rationale}</p>
      </div>
```

**Replace with:**
```tsx
      {/* Rationale */}
      <div className="mt-5 space-y-2">
        <div className="rounded-lg bg-glass-elevated/50 p-4">
          <p className="text-sm text-glass-muted leading-relaxed">{recommendation.rationale}</p>
        </div>
        {recommendation.status === 'pending' && (
          <p className="px-1 font-mono text-[10px] uppercase tracking-wider text-glass-subtle">
            {isIncrease ? '💰 Potential margin recovery' : '⚡ Premium position — your call'}
          </p>
        )}
      </div>
```

**Priority:** P1
**Risk:** Low — additive UI change

---

#### Change 8: Morning Brief — Remove D3 Viz Section
**File:** `src/apps/web/src/pages/MorningBrief.tsx`
**What:** Remove the 6 D3 visualization components from the Morning Brief page. They're impressive but not what operators need at 7am. Move them to the Market page.

Remove the following blocks from MorningBrief.tsx:
- `<BrandTreemap>` and `<CategorySunburst>` grid
- `<EconomicIndicators>`
- Second `<FlywheelCTA>` (the one between EconomicIndicators and StrainStream)
- `<StrainStream>` and `<MarketSizeChart>` grid
- `<CategoryGrowthCurves>`

Also remove their state variables (`brandShare`, `categoryMix`, `economicData`, `strainTrends`, `marketSize`, `categoryGrowth`, `vizLoading`) and the `useEffect` that fetches them.

Also remove the Quick Actions section at the bottom (redundant with sidebar).

**Priority:** P1
**Risk:** Medium — significant page restructure, but purely removal of UI elements

---

#### Change 9: Hide Empty Nav Items
**File:** `src/apps/web/src/components/Sidebar.tsx`
**What:** Hide Geography and Delivery from nav until they have data.

**Find:**
```typescript
const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Morning Brief' },
  { path: '/prices', icon: TrendingDown, label: 'Price Wire' },
  { path: '/threats', icon: Radar, label: 'Threat Radar' },
  { path: '/competitors', icon: Users2, label: 'Competitors' },
  { path: '/geography', icon: Map, label: 'Geography' },
  { path: '/recommendations', icon: Lightbulb, label: 'Recommendations' },
  { path: '/alerts', icon: Bell, label: 'Alerts' },
];
```

**Replace with:**
```typescript
const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Morning Brief' },
  { path: '/prices', icon: TrendingDown, label: 'Price Wire' },
  { path: '/threats', icon: Radar, label: 'Threat Radar' },
  { path: '/competitors', icon: Users2, label: 'Competitors' },
  { path: '/recommendations', icon: Lightbulb, label: 'Recommendations' },
  { path: '/alerts', icon: Bell, label: 'Alerts' },
];
```

And for tools:
```typescript
const toolItems = [
  { path: '/budtender', icon: Bot, label: 'Virtual Budtender', product: 'budtender' },
  { path: '/cue', icon: Package, label: 'Cue', product: 'cue' },
];
```

**Priority:** P1
**Risk:** Low — hiding nav items, routes still work if someone has the URL

---

### P2 — Later (v2)

#### Change 10: Sales Velocity Integration
**Files:** New endpoint + schema changes
**What:** The recommendation engine currently can't distinguish between "premium and selling well" vs "premium and sitting on shelf." Adding even a basic sales velocity signal (could be inventory turn rate, restock frequency, or manual input) would make recommendations dramatically better.

Options:
1. **Manual input:** Operator marks categories as "fast", "normal", "slow"
2. **Inventory proxy:** Track product count changes over time as a velocity proxy
3. **POS integration:** Connect to their actual sales data (high effort, highest value)

**Priority:** P2 — requires product decision on data source

---

#### Change 11: A/B Recommendation Framing
**What:** Show recommendations in a clear A/B format in the UI — "Option A: Hold" vs "Option B: Adjust" — with estimated impact for each.

This requires:
- New `factors` fields in the recommendation model (hold_rationale, adjust_rationale)
- New frontend component for dual-option display
- Update generator to produce both options

**Priority:** P2

---

#### Change 12: Recommendation Dashboard → Inline on Morning Brief
**What:** Instead of a separate `/recommendations` page, surface the top 3 recommendations directly in the Morning Brief with inline Apply/Dismiss actions. The separate page becomes "history."

**Priority:** P2

---

## Appendix: Full File Impact Summary

| File | Changes | Priority |
|------|---------|----------|
| `services/api/src/routes/report-card.ts` | Suggestion text, action items, opportunity calc | P0 |
| `apps/web/src/components/ReportCard.tsx` | Opportunity label, default expanded, color tweaks | P0 |
| `services/api/src/engine/generator.ts` | Rationale text overhaul | P1 |
| `apps/web/src/components/RecommendationCard.tsx` | Context line under rationale | P1 |
| `apps/web/src/pages/MorningBrief.tsx` | Remove D3 viz, remove Quick Actions | P1 |
| `apps/web/src/components/Sidebar.tsx` | Hide Geography, Delivery from nav | P1 |
| Database schema (recommendations.factors) | Add position, hold/adjust rationale fields | P2 |
| New: Sales velocity endpoint | Manual or automated velocity input | P2 |
| `apps/web/src/components/RecommendationCard.tsx` | A/B option display | P2 |

---

## Design Principles (Reference)

These should guide every future feature in GLASS:

1. **Never criticize, always create opportunity.** An operator reading GLASS should feel empowered, not scolded.

2. **Dollars > Percentages.** "You could earn $200 more per week" hits harder than "+12.3%."

3. **Two paths, one goal.** Every recommendation should present both "hold" and "adjust" as valid strategies. We don't know their business; they do.

4. **Answer "What do I gain?"** Every recommendation, every card, every data point should make the operator think: "Oh, I should do something about that" — not "So what?"

5. **Respect premium positioning.** Charging more than the market is a STRATEGY, not a mistake. Only flag it when it's extreme (>20%) or when we have evidence of slow movement.

6. **Operator time is sacred.** They have 5 minutes at 7am. The Morning Brief should deliver all essential intelligence in that window. Everything else is a click away, not in their face.

7. **Randy's rule:** At the end of the day, people want to **make more money**, **save money**, or **get more customers**. Every pixel serves one of these three goals.
