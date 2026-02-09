# CH Alpine IQ Campaign Schedule

**Current state:** Points system live, no campaigns running
**Goal:** Regular SMS/email touchpoints to drive repeat visits

---

## Campaign Types

### 1. AUTOMATED (Set Once, Runs Forever)
Triggered by customer behavior - set up and forget.

### 2. WEEKLY CAMPAIGNS (Manual)
Scheduled sends to drive traffic on specific days.

### 3. MONTHLY CAMPAIGNS (Manual)
Bigger pushes around events, holidays, promotions.

---

## Automated Campaigns (Set Up First)

| Trigger | Message | Timing | Goal |
|---------|---------|--------|------|
| **Welcome** | "Welcome to Flight Club! You just earned [X] points. Here's 15% off your next visit: [CODE]" | 1 hour after first purchase | Convert to repeat |
| **Second Visit Push** | "Ready for round 2? Use code FLYBACK for 10% off" | 5 days after first purchase (if no 2nd visit) | Get 2nd visit |
| **Win-Back** | "We miss you at Cannabis Healing! Here's 20% off to come back: [CODE]" | 30 days no purchase | Reactivate lapsed |
| **Birthday** | "Happy Birthday! 🎂 Stop by for a FREE pre-roll on us today" | On birthday | Loyalty / goodwill |
| **Points Reminder** | "You have [X] points at Cannabis Healing - that's $[Y] in rewards waiting!" | 14 days no purchase + 100+ points | Drive redemption visit |
| **High Spender** | "Thanks for being a Flight Club VIP! Here's early access to [new product/deal]" | After $500 lifetime spend | Reward top customers |

---

## Weekly Campaign Schedule

**Send 2-3 campaigns per week. Rotate these:**

| Day | Campaign Name | Message | Segment |
|-----|--------------|---------|---------|
| **Monday** | Start Fresh | "New week, fresh start. 15% off all flower today. Land. Walk. Relax." | All |
| **Wednesday** | Midweek Deal | "Midweek pick-me-up: Buy any vape, get a pre-roll free" | Purchased in last 60 days |
| **Friday** | Weekend Ready | "Weekend plans? Stock up today - 20% off orders $100+" | All |

**Alternative campaigns to rotate in:**

| Campaign | Message | Best For |
|----------|---------|----------|
| Product Drop | "NEW: [Strain name] just landed. Limited quantity." | All |
| Flash Sale | "4 HOURS ONLY: 25% off edibles. Ends at 8pm" | All |
| Double Points | "Earn 2X points on all purchases today" | All |
| Staff Pick | "[Budtender name]'s pick this week: [product]. Here's why..." | Engaged customers |
| Traveler Special | "Flying out? Grab a Flight Kit - everything you need, ready to go" | All (new positioning) |

---

## Monthly Campaign Calendar

### January 2026
| Date | Campaign | Message |
|------|----------|---------|
| Jan 22 (Wed) | Midweek Deal | Vape + pre-roll bundle |
| Jan 24 (Fri) | Weekend Ready | 20% off $100+ |
| Jan 27 (Mon) | Start Fresh | 15% off flower |
| Jan 29 (Wed) | Flash Sale | 4-hour edible sale |
| Jan 31 (Fri) | Weekend Ready | Double points |

### February 2026
| Date | Campaign | Message |
|------|----------|---------|
| Feb 3 (Mon) | Start Fresh | 15% off flower |
| Feb 5 (Wed) | Product Drop | New strain announcement |
| Feb 7 (Fri) | **Superbowl Pre-Game** | "Game day ready? Stock up - 25% off everything" |
| Feb 9 (Sun) | **Superbowl Sunday** | "Game day! Free pre-roll with any purchase today" |
| Feb 12 (Wed) | Midweek Deal | Valentine's prep |
| Feb 14 (Fri) | **Valentine's Day** | "Treat yourself (or someone else). 20% off" |
| Feb 17 (Mon) | President's Day | "Day off? Come see us. 15% off" |

---

## Message Guidelines

**Tone:**
- Casual, friendly, not corporate
- Short - people skim texts
- Clear value (discount, freebie, points)
- Always include CTA

**Format:**
```
[Hook/Offer]
[1-2 sentence detail]
[CODE if applicable]
[CTA: "Stop by today" or "Order ahead: cannabishealingllc.com"]
```

**Example:**
```
Weekend ready? 🛫
Stock up before you fly out - 20% off orders over $100 today.
Code: WEEKEND20
See you soon.
```

**What NOT to do:**
- Long paragraphs
- Multiple offers in one message
- Sending more than 3x/week (causes unsubscribes)
- Generic "come visit us" with no offer

---

## Segments to Create

| Segment | Definition | Use For |
|---------|------------|---------|
| All Customers | Everyone in database | Big announcements, major sales |
| Recent (60 days) | Purchased in last 60 days | Regular promos, new products |
| Lapsed (60+ days) | No purchase in 60+ days | Win-back offers |
| First-Timers | Only 1 purchase ever | Second visit push |
| VIPs | $500+ lifetime | Early access, exclusive deals |
| High Points | 200+ points unredeemed | Points reminder |
| Flower Buyers | Bought flower | Flower-specific drops |
| Edible Buyers | Bought edibles | Edible sales |
| Travelers | (if trackable) | Flight Kit promos |

---

## Setup Checklist

### Automations (Do First)
- [ ] Create Welcome automation
- [ ] Create Second Visit Push automation
- [ ] Create Win-Back (30 day) automation
- [ ] Create Birthday automation
- [ ] Create Points Reminder automation
- [ ] Test all automations with test customer

### Segments
- [ ] Create "Recent 60 days" segment
- [ ] Create "Lapsed 60+ days" segment
- [ ] Create "First-Timers" segment
- [ ] Create "VIPs $500+" segment

### Weekly Rhythm
- [ ] Schedule first Monday campaign
- [ ] Schedule first Wednesday campaign
- [ ] Schedule first Friday campaign
- [ ] Set calendar reminder to schedule next week every Friday

---

## Tracking

**Weekly metrics to watch:**
- Open rate (goal: 25%+)
- Click rate (goal: 5%+)
- Redemption rate (goal: 10%+ for discount codes)
- Unsubscribe rate (concern if >1%)

**Monthly review:**
- Which campaigns drove most redemptions?
- Which day/time performs best?
- Are automations converting first-timers to repeat?

---

## Quick Reference: Discount Codes

| Code | Discount | Use |
|------|----------|-----|
| WELCOME15 | 15% off | New customer welcome |
| FLYBACK | 10% off | Second visit push |
| MISSYOU20 | 20% off | Win-back |
| WEEKEND20 | 20% off $100+ | Weekend campaigns |
| FLASH25 | 25% off | Flash sales |
| DOUBLE | 2X points | Double points days |

**Set these up in POS so they work automatically.**
