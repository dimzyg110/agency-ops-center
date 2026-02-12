# AC Toll Processing Outreach Emails — Expert Review

**Reviewer:** Senior Email Marketing & Sales Copy Specialist
**Date:** 2026-02-12
**Files Reviewed:** `outreach-emails.md` (V1, 85 emails), `outreach-emails-v2.md` (V2, 85 emails), `prospects.md`

---

## Overall Verdict: 🟡 SEND WITH CHANGES (V2 preferred, with modifications below)

Both versions are *close* to sendable but have issues that will hurt open rates, deliverability, and reply rates. V2 is the stronger set and should be the base. With the fixes outlined below, you can send within 24-48 hours.

---

## V1 vs V2 Comparison

### V2 Wins. Here's Why:

| Criteria | V1 | V2 |
|---|---|---|
| **Sender persona** | "Advanced Cultivators Team" — corporate/anonymous | "Randy Torres" at roviqai.xyz — real human name |
| **Tone** | Tries to be casual but reads like a marketing team wrote it | Reads like a connector/intermediary making a warm intro |
| **Length** | 4-6 sentences — slightly too long for cold email | 3-4 sentences — tighter, faster to scan |
| **CTA** | Mixed ("test batch", "swing by", "tour the facility", "chat numbers") | Consistent, low-friction: "Want me to make an intro?" |
| **Personalization** | City name swapped in, generic otherwise | City + sqft tier + license context woven in |
| **Template count** | ~6 templates rotated across 85 emails | ~4 templates rotated, but more consistent framing |
| **Subject lines** | All "Toll processing / [Company Name]" — terrible | Varied ("Your [City] grow", "Quick question about your flower", "Connecting MA cultivators") — better |

**Bottom line:** V2 feels like a person reaching out. V1 feels like a mail merge. Use V2 as the base.

---

## Top 5 Strengths (V2)

1. **The "intro" framing is brilliant.** "Want me to make an intro?" positions Randy as a connector, not a salesman. It's the lowest-friction CTA possible and feels like a favor, not a pitch. This alone makes V2 significantly better than V1.

2. **Short and scannable.** Most V2 emails are 4-5 lines. For cold outreach to busy cultivators, this is perfect. Nobody in cannabis is reading 3-paragraph emails from strangers.

3. **Real human sender.** "Randy Torres" with a signature URL beats "Advanced Cultivators Team" every time. People reply to people, not companies.

4. **Value prop is clear and dual-sided.** "Roll your flower into prerolls under your brand, or supply you with ready-made prerolls to sell" — two options in one sentence. Smart.

5. **Tier-appropriate messaging.** Large operations hear "serious volume runs." Mid-tier hears "low MOQs." Micros hear "maximize what they grow." This shows you actually thought about the recipient's situation.

---

## Top 5 Issues (Both Versions)

### 1. 🚨 The .win Domain is a Deliverability Disaster

**Severity: CRITICAL**

The `.win` TLD is one of the most spam-abused TLDs on the internet. It's right up there with `.xyz`, `.top`, `.click`, and `.loan`. Here's what this means:

- **Gmail, Outlook, Yahoo** all have elevated spam scoring for `.win` domains
- Even with perfect SPF/DKIM/DMARC setup, you'll see 30-50% of emails landing in spam/promotions
- Many corporate/ISP email servers outright block `.win` domains
- You're sending to a mix of Gmail, Yahoo, AOL, Comcast, Verizon, iCloud, and business domains — the worst possible mix for a `.win` sender

**Recommendations:**
- Buy a `.com` domain immediately. Something like `advancedcultivators.com`, `acprerolls.com`, or even `lowellprerolls.com`. Cost: $12/year. This is the single highest-ROI fix.
- If `.win` must be used, warm it up for 2-3 weeks first (send 5-10 emails/day to known contacts who will open and reply)
- Set up SPF, DKIM, DMARC before sending a single email
- Do NOT send all 85 on day one. Stagger: 10-15/day over 6-7 days

### 2. ⚠️ V1 Subject Lines Are All Identical (and V2 Only Has 4 Variants)

**V1:** Every single email uses `Toll processing / [Company Name]`. This is:
- Boring — no curiosity, no reason to open
- Obviously mass-emailed — nobody writes subject lines like that
- Keyword-triggering — "processing" in a subject line can flag filters

**V2** is better with 4 variants but still too few for 85 emails:
- "Your [City] grow"
- "Quick question about your flower"
- "Connecting MA cultivators"
- "Connecting MA cultivators" (repeated too much)

**Problem:** If even 2 recipients forward/compare emails, the identical structure is obvious. In a tight MA cannabis market where everyone knows everyone, this is likely.

### 3. ⚠️ Template Repetition — Detectable in a Small Market

V1 uses **6 templates** rotated across 85 recipients. V2 uses **4 templates**. Massachusetts has ~400 active cannabis licensees. These people talk to each other. They're at the same industry events. They're in the same group chats.

If Cultivator A in Holyoke and Cultivator B in Holyoke compare notes and got the *exact same email* with only the city swapped — you're toast. Your credibility drops to zero and you may get reported as spam.

**V2 is less at risk** because the emails are shorter and more generic (making slight similarities less noticeable), but it's still a real concern.

### 4. ⚠️ CAN-SPAM Compliance Gaps

Both versions are **missing required elements** under CAN-SPAM:

- ❌ **No physical mailing address** — CAN-SPAM requires a valid physical postal address in every commercial email
- ❌ **No unsubscribe mechanism** — CAN-SPAM requires a clear way to opt out
- ❌ **No identification as an ad** — While the "connecting cultivators" angle helps, these are commercial solicitations

**Note:** CAN-SPAM applies even to B2B emails. Fines are up to $51,744 per email.

**V2 mitigation:** The "intermediary" framing ("I work with AC, want me to make an intro?") arguably positions these as relationship emails rather than direct commercial solicitations. But this is thin cover if someone complains.

**Fix:** Add a one-liner at the bottom: `Reply STOP to opt out | [Physical Address]` — it's small, unobtrusive, and keeps you legal.

### 5. ⚠️ V1 Sends From "Team" — Nobody to Reply To

V1 signs off as "Advanced Cultivators Team" or "Best, Advanced Cultivators Team." This creates two problems:
- Who do I reply to? A faceless team?
- There's no personal connection. In cannabis, relationships are everything.

V2 fixes this with "Randy Torres" but introduces a different issue: Randy is positioned as a third-party connector ("I work with Advanced Cultivators"), which may cause confusion. Is he an employee? A consultant? A broker? Recipients may hesitate if the relationship isn't clear.

---

## Specific Fixes Needed

### Fix 1: Rewrite V1 Subject Lines (or just use V2)

**Current V1 (all emails):**
> Subject: Toll processing / [Company Name]

**Replace with 8-10 rotating variants:**
- `Your [City] flower`
- `Quick preroll question`
- `Lowell → [City]`
- `Connecting growers in MA`
- `[First Name], preroll capacity in Lowell`
- `Thought of you guys`
- `Fellow grower in Lowell`
- `Your flower, our machine`

### Fix 2: Add V2 Subject Line Variety

**Current V2 uses only 4 variants for 85 emails.** Add 4-6 more:
- `[First Name] — quick one`
- `MA cultivator connection`
- `Your [City] operation`
- `Prerolls without the machine`
- `Thought this might help`
- `Short question for [Company]`

### Fix 3: Fix the Broken Sentences in V1 Tier 4-6

Multiple V1 emails have a **grammatically broken sentence**:

> "Instead of letting bulk sit in Attleboro, you need consistent output, let us turn it into shelf-ready packs."

This should be:
> "Instead of letting bulk sit in Attleboro, let us turn it into shelf-ready packs."

OR:
> "If you need consistent output from your Attleboro grow, we can turn bulk into shelf-ready packs."

**Affected emails:** Ashli's Farm, Nature Medicines, Canna-Farm, Stafford Green, UC Cultivation, 617 Therapeutic, Greenerside Holdings, Greenjeans Farms, plus several Tier 7-11 entries.

### Fix 4: Personalize V1 Greetings

**Current:** 40+ emails open with "Hi there" even when the prospect file has a first name.

**Examples of missed personalization:**
- ACMJ, Inc. → contact is font22@gmail.com — no name available, "Hi there" is fine
- Kapnos, Inc. → contact is ihedges@clozers.com — could use "Hi" but "Hi there" works
- Mass Cannabis Growers Cooperative → "Hi there" — should try harder (Brandon is in the contact info)

V2 handles this better, using first names when available.

### Fix 5: Fix "Jodiem" Personalization Error

V1 email to Green Patriot LLC opens with:
> "Hi Jodiem,"

The contact email is `jodiem1955@gmail.com`. "Jodiem" is clearly an email handle, not a name. It should be "Hi there" or research the actual contact name.

### Fix 6: Add CAN-SPAM Footer

Add to EVERY email (both versions):

```
---
Reply STOP to opt out | Advanced Cultivators, [Street Address], Lowell, MA [Zip]
```

### Fix 7: Fix "Palazzi, Inc.orporated" Display Name

Both versions reference this company as written in the license database: "Palazzi, Inc.orporated" — this is clearly a data formatting error. Use "Palazzi Inc." in the email.

### Fix 8: BeachGrass Topicals — Wrong Fit?

BeachGrass Topicals LLC is a **topicals** company. Their name literally says "topicals." They may not be growing smokable flower at all. Sending a preroll pitch to a topicals company shows you didn't look at who you're emailing. Either research this one or remove from the list.

### Fix 9: Bodelle's Edibles — Potentially Wrong Fit

Similar issue. "Bodelle's Edibles LLC" focuses on edibles. They may grow flower, but the pitch assumes they want prerolls. A topicals/edibles company may have zero interest in preroll processing. Research or flag for manual review.

### Fix 10: V2 Signature — Clarify Randy's Role

V2 signs as:
```
Randy Torres
roviqai.xyz
```

This raises questions: Who is Randy? Why is he emailing from roviqai.xyz about Advanced Cultivators? Is he an employee? A consultant?

**Better:**
```
Randy Torres
Partner, Advanced Cultivators
```
OR:
```
Randy Torres
Roviq | Working with Advanced Cultivators
```

And link to AC's toll processing page, not roviqai.xyz (recipients will Google the domain, see it's an AI company, and get confused).

---

## Subject Line Recommendations

### Best V2 Subject Lines (Keep These):
- ✅ "Your [City] grow" — simple, personalized, curiosity-driven
- ✅ "Quick question about your flower" — implies a real question, gets opens

### Drop or Limit:
- ⚠️ "Connecting MA cultivators" — too vague, overused (appears 20+ times)

### New Subject Lines to Add:
| Subject Line | Why It Works |
|---|---|
| `[First Name] — saw your grow in [City]` | Name + location = personal |
| `Preroll idea for [Company]` | Specific, relevant |
| `Fellow MA cultivator` | Peer framing, community |
| `Quick thought about your flower` | Soft, curious |
| `No machine needed` | Speaks to the pain point |
| `[City] → Lowell preroll run?` | Geographic, concrete |

### Subject Lines to AVOID:
- ❌ Anything with "toll processing" — too jargon-heavy for a subject line, and "processing" can trigger filters
- ❌ All caps (some company names like "HOLBROOK GROW LLC" carry over into subjects)
- ❌ Exclamation marks, dollar signs, "FREE", "limited time"

---

## Deliverability Warnings

### 🚨 RED FLAG: .win Domain

| Risk Factor | Impact |
|---|---|
| `.win` TLD reputation | HIGH — known spam TLD, elevated filtering across all major providers |
| New domain age | HIGH — if `spacemanwins.win` was recently registered, it has zero reputation |
| Volume (85 emails) | MEDIUM — sending 85 from a new/cold domain = instant red flag |
| Mixed recipient domains | MEDIUM — Gmail + Yahoo + AOL + Comcast + iCloud + business = inconsistent delivery |
| No warm-up history | HIGH — cold domain + cold IPs = worst possible starting point |

### Deliverability Action Plan:
1. **Buy a .com immediately** (24 hours to propagate DNS)
2. **Set up:** SPF, DKIM, DMARC, and a basic website on the domain
3. **Warm-up protocol:** Days 1-3: send 5 emails/day to known contacts. Days 4-7: 10/day. Days 8-14: 15/day. Day 15+: full volume.
4. **Stagger sends:** Never blast all 85 at once. 10-15/day max.
5. **Monitor bounces:** If bounce rate exceeds 5% after first batch, STOP and investigate
6. **Use a sending tool** (Instantly, Smartlead, or even Mailgun) that handles warm-up and throttling

### Spam Trigger Words Found in V1:
- "six figures" — money language, moderate risk
- "toll processing" in subject line — jargon but "processing" can flag
- "capacity open" — could read as commercial solicitation
- "without investing" — financial language
- "branded SKUs" — corporate jargon

V2 is cleaner on spam triggers. Another reason to prefer V2.

---

## Sample Rewrites (3 Emails)

### Rewrite 1: Small Operation (Tier 1) — Witch City Gardens LLC

**Original V2:**
```
Subject: Quick question about your flower

Hey Tim,

I work with Advanced Cultivators out of Lowell. They can either roll your 
flower into prerolls under your brand, or supply you with ready-made prerolls 
to sell. Either way, no manufacturing license needed.

Saw you're running a 5K sqft grow in Salem. Figured it might be worth 
connecting you two. No equipment needed on your end.

Want me to make an intro?

Randy Torres
roviqai.xyz
```

**Rewritten:**
```
Subject: Tim — preroll idea for Witch City Gardens

Hey Tim,

A cultivator I work with in Lowell (Advanced Cultivators) has a RollPros 
preroll machine with open capacity. They're looking for MA growers who want 
flower turned into branded prerolls — no equipment or manufacturing license 
needed on your end.

Figured your Salem operation might be a fit. Want me to connect you two?

— Randy Torres
Roviq | Working with Advanced Cultivators

Reply STOP to opt out | 123 Main St, Lowell, MA 01851
```

**What changed:**
- Subject line includes name + company = higher open rate
- Mentions RollPros by name = specificity builds trust
- "Open capacity" = urgency without being pushy
- Signature clarifies relationship
- CAN-SPAM footer added

---

### Rewrite 2: Mid Operation (Tier 2-3) — Cape Cod Grow Lab LLC

**Original V2:**
```
Subject: Your Brewster grow

Hey Art,

I work with Advanced Cultivators out of Lowell. They can either roll your 
flower into prerolls under your brand, or supply you with ready-made prerolls 
to sell. Either way, no manufacturing license needed.

Saw you're running a 10K sqft operation in Brewster. Figured it might be 
worth connecting you two. Low MOQs, no need to commit to huge runs.

Want me to make an intro?

Randy Torres
roviqai.xyz
```

**Rewritten:**
```
Subject: Art — your Brewster flower

Hey Art,

I work with a Lowell cultivator (Advanced Cultivators) that does preroll 
manufacturing for other MA growers. RollPros machine — about 900/hour, 
air compaction so they actually burn right.

Your 10K sqft Brewster operation seems like a good fit. They can run your 
flower under your brand with low minimums. No equipment purchase needed.

Worth a quick intro?

— Randy Torres
Roviq | Working with Advanced Cultivators

Reply STOP to opt out | 123 Main St, Lowell, MA 01851
```

**What changed:**
- Subject line uses first name + location
- Added technical detail (900/hour, air compaction) — gives Art something concrete to evaluate
- "Actually burn right" = casual, relatable, industry-appropriate
- Still short (5 sentences)
- CTA unchanged — still low-friction

---

### Rewrite 3: Microbusiness — Cannalive Genetics LLC

**Original V2:**
```
Subject: Your Holyoke grow

Hey Marko,

I work with Advanced Cultivators out of Lowell. They can either roll your 
flower into prerolls under your brand, or supply you with ready-made prerolls 
to sell. Either way, no manufacturing license needed.

Saw you're running a microbusiness in Holyoke. Figured it might be worth 
connecting you two. No equipment needed on your end—especially good fit for 
micros who want to maximize what they grow.

Want me to make an intro?

Randy Torres
roviqai.xyz
```

**Rewritten:**
```
Subject: Marko — fellow MA grower, quick question

Hey Marko,

A cultivator I work with in Lowell has a preroll machine with open time. 
They roll other people's flower into branded prerolls — your genetics, 
your brand, their machine.

For a microbusiness like yours in Holyoke, it means you can sell prerolls 
without buying equipment. Good way to get more margin out of what you 
already grow.

Want me to connect you with their team?

— Randy Torres
Roviq | Working with Advanced Cultivators

Reply STOP to opt out | 123 Main St, Lowell, MA 01851
```

**What changed:**
- Subject line says "fellow MA grower" = peer framing
- "Your genetics, your brand, their machine" = memorable value prop in 7 words
- "More margin out of what you already grow" = speaks to the micro pain point (limited canopy, need max value)
- Company name (Advanced Cultivators) deliberately held until intro stage = reduces the "pitch" feeling

---

## Final Recommendation

### Send V2 with these changes (in priority order):

1. **🔴 MUST DO: Get off the .win domain.** Buy a .com. This is the #1 thing that will kill this campaign. Budget: $12. Impact: 30-50% more emails reaching inboxes.

2. **🔴 MUST DO: Add CAN-SPAM footer** to every email (physical address + opt-out). Takes 5 minutes. Prevents legal liability.

3. **🟡 SHOULD DO: Add 4-6 more subject line variants.** The current 4 aren't enough for 85 emails in a small market. Use first names in subject lines where available.

4. **🟡 SHOULD DO: Clarify Randy's signature.** "Randy Torres / roviqai.xyz" will confuse people. Link to AC, not Roviq.

5. **🟡 SHOULD DO: Review BeachGrass Topicals and Bodelle's Edibles** — these may not be preroll prospects. Research or remove.

6. **🟢 NICE TO HAVE: Add RollPros technical detail** to mid-tier and large operation emails. These people know equipment. "900/hour, air compaction" gives them something concrete.

7. **🟢 NICE TO HAVE: Stagger sends across 7 days** with warm-up protocol. Even with a .com domain, sending 85 cold emails day one from a new domain is risky.

### If Forced to Send Today (No Domain Change):

- Send V2 as-is to the **10 most promising prospects** only
- Add the CAN-SPAM footer manually
- Monitor deliverability for 48 hours
- If >50% open rate → send next batch of 15
- If <20% open rate → STOP, you're in spam folders, switch domains

### Timeline to Full Send:
| Day | Action |
|---|---|
| Day 0 | Buy .com domain, set up DNS (SPF/DKIM/DMARC) |
| Day 1-3 | Send 5 warm-up emails/day to known contacts |
| Day 4-7 | Send first 15 prospect emails (highest priority) |
| Day 8-14 | Send remaining 70 in batches of 15/day |
| Day 15+ | Follow up on non-responders |

---

## Appendix: Quick-Reference Template Inventory

### V1 Templates (6 total):
1. **"Reaching out because we've got a RollPros setup"** — Used for Tier 1 + some micros
2. **"Saw you guys are operating out of [City]"** — Used for Tier 1 + some micros
3. **"Just wanted to flag that we've got toll processing capacity"** — Used for Tier 1 + some micros
4. **"You're likely at that scale where hand-rolling is a drag"** — Used for Tier 2-3
5. **"Writing from Advanced Cultivators in Lowell"** — Used for Tier 2-3
6. **"Quick note from Lowell"** — Used for Tier 4+ and some 7-11

### V2 Templates (4 total):
1. **Large ops (Tier 4+):** "They can handle serious volume runs."
2. **Mid ops (Tier 2-3):** "Low MOQs, no need to commit to huge runs."
3. **Small ops (Tier 1):** "No equipment needed on your end."
4. **Microbusinesses:** "Especially good fit for micros who want to maximize what they grow."

All 4 V2 templates share the same body structure — only the closing differentiator line changes.
