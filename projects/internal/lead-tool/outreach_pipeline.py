#!/usr/bin/env python3
"""
Roviq Automated Outreach Pipeline
==================================
Full pipeline: Load leads → Generate HTML snapshots → Send emails → Track campaigns

Usage:
    # Preview what would be sent (dry run)
    python3 outreach_pipeline.py --dry-run

    # Send Day 0 emails to all leads (first batch)
    python3 outreach_pipeline.py --send --day 0

    # Send Day 3 follow-ups (only to leads who haven't replied)
    python3 outreach_pipeline.py --send --day 3

    # Send Day 7 final emails (only to leads who haven't replied)
    python3 outreach_pipeline.py --send --day 7

    # Send to specific leads only (by rank)
    python3 outreach_pipeline.py --send --day 0 --ranks 1,2,3,4,5

    # Check campaign status
    python3 outreach_pipeline.py --status

    # Generate HTML snapshots only (no sending)
    python3 outreach_pipeline.py --generate-snapshots

Config:
    Set these in .env or environment:
    - RESEND_API          : Resend API key
    - FROM_EMAIL          : Sender email (default: randy@spacemanwins.win)
    - FROM_NAME           : Sender name (default: Randy @ Roviq)
    - BATCH_SIZE          : Emails per batch (default: 10)
    - BATCH_DELAY_SEC     : Seconds between batches (default: 60)
"""

import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
SNAPSHOTS_DIR = OUTPUT_DIR / "snapshots"
CAMPAIGN_FILE = OUTPUT_DIR / "campaign_tracking.json"
OUTREACH_CSV = OUTPUT_DIR / "full_outreach_100.csv"
ENRICHED_CSV = OUTPUT_DIR / "signals_pack_enriched.csv"

# Load .env from workspace root
ENV_FILE = SCRIPT_DIR.parent.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

RESEND_API_KEY = os.environ.get("RESEND_API", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "randy@spacemanwins.win")
FROM_NAME = os.environ.get("FROM_NAME", "Randy @ Roviq")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "10"))
BATCH_DELAY_SEC = int(os.environ.get("BATCH_DELAY_SEC", "60"))
RESEND_URL = "https://api.resend.com/emails"


# ──────────────────────────────────────────────
# ENRICHMENT DATA LOADERS
# ──────────────────────────────────────────────

_enrichment_cache: dict | None = None


def _latest_output_file(pattern: str) -> Path | None:
    files = sorted(
        OUTPUT_DIR.glob(pattern),
        key=lambda path: path.stat().st_mtime if path.exists() else 0,
        reverse=True,
    )
    return files[0] if files else None


def _load_enrichment() -> dict:
    """Load and merge all per-operator enrichment data into a lookup by business name."""
    global _enrichment_cache
    if _enrichment_cache is not None:
        return _enrichment_cache

    data: dict[str, dict] = {}

    # Google Places data
    places_file = _latest_output_file("places_live_*.csv") or _latest_output_file(
        "places_enriched_*.csv"
    )
    if places_file and places_file.exists():
        with open(places_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("Business Name", "").strip()
                if name:
                    data.setdefault(name, {}).update({
                        "google_rating": row.get("google_rating", ""),
                        "google_review_count": row.get("google_review_count", "0"),
                        "review_velocity": row.get("review_velocity", ""),
                        "google_status": row.get("google_status", ""),
                        "distress_score": row.get("Distress Score", ""),
                        "signal_count": row.get("Signal Count", ""),
                        "pressure_signals_raw": row.get("Pressure Signals", ""),
                        "capacity_signals_raw": row.get("Capacity Signals", ""),
                        "why_now": row.get("Why Now", ""),
                        "talk_track": row.get("Talk Track", ""),
                        "city": row.get("City", ""),
                        "license_types": row.get("License Types", ""),
                    })

    # Hiring signals
    hiring_file = _latest_output_file("hiring_signals_*.csv")
    if hiring_file and hiring_file.exists():
        with open(hiring_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("Business Name", "").strip()
                if name:
                    data.setdefault(name, {}).update({
                        "hiring_signal": row.get("hiring_signal", ""),
                        "active_jobs": row.get("active_jobs", "0"),
                        "job_titles": row.get("job_titles", ""),
                    })

    # City competition density
    city_counts: dict[str, int] = {}
    enriched_file = _latest_output_file("signals_pack_enriched*.csv") or _latest_output_file(
        "ma_operator_signals_pack_*.csv"
    )
    if enriched_file and enriched_file.exists():
        with open(enriched_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                city = row.get("City", "").strip()
                if city:
                    city_counts[city] = city_counts.get(city, 0) + 1
    for name, d in data.items():
        city = d.get("city", "")
        d["city_operator_count"] = city_counts.get(city, 0)

    _enrichment_cache = data
    return data


def _get_enrichment(business_name: str) -> dict:
    """Get enrichment data for a specific operator."""
    data = _load_enrichment()
    return data.get(business_name.strip(), {})


# ──────────────────────────────────────────────
# SNAPSHOT → HTML CONVERTER (v2 — operator-specific)
# ──────────────────────────────────────────────

def _parse_stall_months(pressure_raw: str) -> int | None:
    """Extract stall duration from pressure signal string like 'stalled_ops_73mo'."""
    import re
    match = re.search(r"stalled_ops_(\d+)mo", pressure_raw)
    return int(match.group(1)) if match else None


def _is_actually_operating(enrichment: dict) -> bool:
    """
    Cross-validate CCC 'stalled' flag against live signals.
    Returns True if Google Places / hiring data proves the operator IS running,
    regardless of what CCC's COMMENCE_OPERATIONS_DATE says.
    """
    reviews = int(enrichment.get("google_review_count", "0") or "0")
    status = enrichment.get("google_status", "").lower()
    rating = enrichment.get("google_rating", "")
    hiring = enrichment.get("hiring_signal", "")
    active_jobs = int(enrichment.get("active_jobs", "0") or "0")
    job_titles = enrichment.get("job_titles", "").lower()

    # Strong operational signals — any one of these means they're running
    if reviews >= 10:
        return True
    if status == "operational" and rating and float(rating) > 0:
        return True
    if hiring == "hiring_warm" and active_jobs > 0:
        # Hiring for operational roles (not just construction/buildout)
        ops_roles = ["associate", "budtender", "manager", "cashier", "driver", "trimmer", "grower", "packager"]
        if any(role in job_titles for role in ops_roles):
            return True
    return False


def _adjusted_distress_score(raw_score: int, enrichment: dict) -> int:
    """
    Adjust the CCC-based distress score using live validation data.
    Reduces score for operators who are clearly running despite CCC gaps.
    """
    score = raw_score
    reviews = int(enrichment.get("google_review_count", "0") or "0")
    rating_str = enrichment.get("google_rating", "")
    rating = float(rating_str) if rating_str and rating_str != "0" else 0.0

    if _is_actually_operating(enrichment):
        # Remove the stalled_ops contribution (which can be up to 50 pts)
        # We can't know exact contribution, so cap the reduction
        if reviews >= 500:
            score = max(score - 60, 10)   # Major correction
        elif reviews >= 100:
            score = max(score - 45, 10)
        elif reviews >= 10:
            score = max(score - 30, 10)

        # Bonus for strong reputation
        if rating >= 4.5 and reviews >= 100:
            score = max(score - 10, 10)

    return score


def _distress_tier(score: int) -> tuple[str, str, str]:
    """Map distress score to human-readable tier. Returns (label, color, description)."""
    if score >= 180:
        return ("Critical", "#D94F3D", "Multiple compounding pressure signals detected")
    elif score >= 120:
        return ("Elevated", "#E8A838", "Significant operational friction identified")
    elif score >= 60:
        return ("Moderate", "#C4962C", "Some areas of concern worth monitoring")
    else:
        return ("Low", "#5B9F5B", "Relatively stable position")


def snapshot_to_html(snapshot: dict, enrichment: dict | None = None) -> str:
    """
    Convert a JSON snapshot + enrichment data into a genuinely operator-specific
    HTML one-pager. Every section references real data about THIS business.
    """
    if enrichment is None:
        enrichment = _get_enrichment(snapshot.get("business_name", ""))

    biz = snapshot.get("business_name", "Your Business")
    city = snapshot.get("city", "MA")
    date = snapshot.get("generated_date", datetime.now().strftime("%Y-%m-%d"))
    op_type = snapshot.get("operator_type", "operator").title()
    licenses = snapshot.get("license_types", [])

    # Pull enrichment
    rating = enrichment.get("google_rating", "")
    review_count = enrichment.get("google_review_count", "0")
    review_velocity = enrichment.get("review_velocity", "")
    distress_raw = enrichment.get("distress_score", "0")
    distress_score = int(distress_raw) if distress_raw and distress_raw.isdigit() else 0
    hiring = enrichment.get("hiring_signal", "")
    active_jobs = enrichment.get("active_jobs", "0")
    job_titles = enrichment.get("job_titles", "")
    city_count = enrichment.get("city_operator_count", 0)
    pressure_raw = enrichment.get("pressure_signals_raw", "")
    capacity_raw = enrichment.get("capacity_signals_raw", "")
    why_now = enrichment.get("why_now", "")
    license_str = enrichment.get("license_types", "")

    stall_months = _parse_stall_months(pressure_raw)
    actually_operating = _is_actually_operating(enrichment)

    # If Google/hiring data proves they're operating, override the stall signal
    if actually_operating and stall_months:
        stall_months = None  # Don't show stall data — it's wrong

    # Adjust distress score based on live data
    distress_score = _adjusted_distress_score(distress_score, enrichment)
    tier_label, tier_color, tier_desc = _distress_tier(distress_score)

    # ── YOUR NUMBERS section (operator-specific stats) ──
    stats = []
    if distress_score:
        stats.append(("Pressure Score", str(distress_score), tier_label, tier_color))
    if stall_months:
        color = "#D94F3D" if stall_months > 36 else "#E8A838"
        stats.append(("Months Since Licensed", str(stall_months), "without revenue" if stall_months > 24 else "ramping up", color))
    if rating and rating != "0":
        r = float(rating)
        color = "#5B9F5B" if r >= 4.5 else "#E8A838" if r >= 3.5 else "#D94F3D"
        stats.append(("Google Rating", f"{rating}\u2605", f"{review_count} reviews", color))
    if city_count and city_count > 1:
        stats.append(("Operators in {0}".format(city), str(city_count), "licensed in your area", "#888"))

    stat_cells = ""
    for label, value, sub, color in stats[:4]:
        stat_cells += f"""
        <div style="flex:1;min-width:120px;text-align:center;padding:12px 8px;">
            <div style="font-size:28px;font-weight:700;color:{color};">{value}</div>
            <div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px;margin-top:2px;">{label}</div>
            <div style="font-size:11px;color:#666;margin-top:2px;">{sub}</div>
        </div>"""

    # ── WHAT WE'RE SEEING section (operator-specific observations) ──
    observations = []
    reviews_int = int(review_count or 0)

    # Only show stall observation if we validated it's actually stalled
    if stall_months and stall_months > 24:
        burn_years = round(stall_months / 12, 1)
        observations.append(
            f"You've been licensed for <strong>{stall_months} months</strong> (~{burn_years} years) without commencing operations per CCC records. "
            f"That's rent, insurance, compliance costs, and holding fees accumulating with zero revenue offsetting them."
        )
    elif stall_months:
        observations.append(
            f"You've been licensed for <strong>{stall_months} months</strong>. The clock is ticking on your ramp-up. "
            f"Operators who don't reach profitability within 18-24 months of licensing face compounding pressure."
        )

    # Market pressure observation for operators who ARE running
    if actually_operating and not stall_months:
        if reviews_int >= 100:
            observations.append(
                f"You're established in {city} with <strong>{review_count} Google reviews</strong> — that's real traction. "
                f"But in a market where wholesale prices have dropped ~50% since 2021, even established operators are feeling the squeeze. "
                f"The question isn't whether you're running — it's whether your margins are keeping pace."
            )
        elif reviews_int >= 10:
            observations.append(
                f"You're up and running in {city}. In a market with over 1,600 licensed entities and wholesale prices "
                f"down ~50% since 2021, every operator is dealing with margin compression. "
                f"The operators who survive this cycle will be the ones who actively optimize rather than wait it out."
            )
        else:
            observations.append(
                f"The MA cannabis market has shed significant margin since 2021 — wholesale prices down ~50%, "
                f"and {city} is becoming increasingly competitive. Operators who aren't actively monitoring their "
                f"cost structure and market position are the ones getting squeezed out."
            )

    if "small_tier_cultivator" in capacity_raw:
        observations.append(
            f"As a small-tier cultivator, your per-unit costs are structurally higher than larger operations. "
            f"This isn't a flaw — it's a positioning decision. But it means you can't compete on volume. "
            f"Your margin strategy needs to focus on premium positioning, direct retail relationships, or value-added products."
        )

    if rating and float(rating) >= 4.5 and int(review_count or 0) > 100:
        observations.append(
            f"Your <strong>{rating}\u2605 rating across {review_count} reviews</strong> is a real asset. "
            f"Most operators in MA struggle to maintain above 4.3. This is leverage for wholesale negotiations, "
            f"retail partnerships, and customer acquisition costs."
        )
    elif rating and float(rating) < 3.5 and int(review_count or 0) > 10:
        observations.append(
            f"Your <strong>{rating}\u2605 rating</strong> is a red flag for customer acquisition. "
            f"In a market with 1,693 licensed operators, customers have options. "
            f"Addressing the top 3 complaints in your reviews is likely the fastest margin lever available."
        )

    if city_count and city_count >= 5:
        observations.append(
            f"<strong>{city}</strong> has <strong>{city_count} licensed operators</strong> — one of the most competitive "
            f"markets in the state. Differentiation isn't optional here. You need a clear reason someone picks you "
            f"over the {city_count - 1} other options."
        )

    if hiring == "hiring_warm" and int(active_jobs or 0) > 0:
        if actually_operating:
            observations.append(
                f"You're actively hiring ({job_titles or 'open roles'}). Growth is a good signal, "
                f"but in the current market, each new hire should be clearly tied to revenue generation "
                f"or measurable cost reduction within 90 days. Hiring without a margin plan is how operators bleed out."
            )
        else:
            # Hiring for ops roles but CCC says not commenced — likely about to launch
            observations.append(
                f"You're hiring for <strong>{job_titles or 'operational roles'}</strong> — it looks like you're "
                f"gearing up. The ramp from hiring to profitability is where most operators underestimate costs. "
                f"Having your margin strategy locked in before doors open is the difference between a strong launch "
                f"and playing catch-up from day one."
            )
    elif hiring == "hiring_cold" and stall_months and stall_months > 36:
        observations.append(
            f"No active hiring detected, combined with {stall_months} months without operations per CCC records. "
            f"If this is a strategic hold, the carrying costs are still compounding. "
            f"If it's a resource constraint, the market isn't going to wait."
        )

    if len(licenses) >= 3 or license_str.count(";") >= 2:
        lic_count = max(len(licenses), license_str.count(";") + 1)
        observations.append(
            f"You hold <strong>{lic_count} license types</strong>. Multi-license operations have more optionality "
            f"but also more compliance overhead, more capital requirements, and more operational complexity. "
            f"The question is whether all of them are contributing to margin or just burning it."
        )

    # Fallback if somehow no observations generated
    if not observations:
        observations.append(
            f"Based on CCC licensing data and market signals, we've identified pressure points "
            f"specific to your operation in {city}. The MA cannabis market has shed significant margin "
            f"since 2021 — operators who aren't actively optimizing are falling behind."
        )

    obs_html = ""
    for obs in observations:
        obs_html += f'<p style="margin:0 0 14px;font-size:14px;line-height:1.65;color:#333;">{obs}</p>'

    # ── WHERE YOU MIGHT BE LOSING MARGIN ──
    leaks = snapshot.get("likely_leaks", [])

    # Filter out stall-related leaks for operators who are actually running
    if actually_operating:
        stall_leak_names = {"burn without revenue", "burn without revenue.", "stalled operations"}
        leaks = [l for l in leaks if l.get("name", "").lower().strip() not in stall_leak_names]
        # Add a market-pressure leak if we removed stall leaks and have fewer than 3
        if len(leaks) < 3:
            leaks.append({
                "name": "Margin Compression",
                "description": "Wholesale prices down ~50% since 2021 — every operator is feeling the squeeze on per-unit margins",
                "quick_win": "Run a cost-per-unit analysis across your top 5 products to find the biggest leaks",
            })

    leak_html = ""
    for i, leak in enumerate(leaks[:3], 1):
        leak_name = leak.get("name", "")
        leak_desc = leak.get("description", "")
        quick_win = leak.get("quick_win", "")
        leak_html += f"""
        <div style="margin-bottom:14px;padding:14px 16px;background:#FAFAF8;border-left:3px solid #D94F3D;border-radius:0 6px 6px 0;">
            <div style="font-size:14px;font-weight:600;color:#1A1917;margin-bottom:4px;">{leak_name}</div>
            <div style="font-size:13px;color:#555;line-height:1.5;">{leak_desc}</div>
            <div style="font-size:12px;color:#2E7D32;margin-top:6px;font-style:italic;">\u2192 {quick_win}</div>
        </div>"""

    # ── BOTTOM LINE (specific to this operator) ──
    # Stall-based bottom lines (only if validated as actually stalled)
    if stall_months and stall_months > 48:
        bottom_line = (
            f"You've been carrying costs for {stall_months} months without revenue. Every month "
            f"that continues is money you don't get back. The single most important decision right now is whether to "
            f"accelerate to operations or cut your losses. If you're going to operate, the path to first revenue "
            f"needs to be measured in weeks, not quarters."
        )
    elif stall_months and stall_months > 24:
        bottom_line = (
            f"At {stall_months} months, you're past the point where delays are just inconvenient — they're "
            f"existentially expensive. The market has moved significantly since you got licensed. Your business plan "
            f"from {stall_months // 12} years ago may not match today's reality. A fresh 14-day operational audit "
            f"could save you from continuing to invest in assumptions that are no longer true."
        )
    # Operating businesses — bottom lines based on their actual situation
    elif actually_operating and rating and float(rating) >= 4.5 and reviews_int >= 100:
        bottom_line = (
            f"Your reputation ({rating}\u2605 across {review_count} reviews) is a real competitive moat. "
            f"But reputation alone doesn't fix margin compression. The operators thriving right now have paired "
            f"strong customer loyalty with relentless cost discipline. A focused margin audit could reveal whether "
            f"your cost structure still matches your brand promise — or if you're leaving money on the table."
        )
    elif actually_operating and reviews_int >= 10:
        bottom_line = (
            f"You're in the game and customers are finding you. But in a market where wholesale prices are down "
            f"~50% since 2021, 'operating' isn't the same as 'thriving.' The operators who pull ahead from here "
            f"are the ones who know their true cost per unit, optimize their product mix weekly, and treat margin "
            f"like a metric — not an afterthought. A 14-day margin audit can tell you exactly where you stand."
        )
    elif "small_tier_cultivator" in capacity_raw:
        bottom_line = (
            f"Small-tier cultivators who survive in this market all have one thing in common: they stopped trying "
            f"to compete on price and started competing on relationships, quality, or niche positioning. "
            f"Your next move should be identifying which of those three is your actual advantage."
        )
    elif "cultivator_no_mfg" in capacity_raw:
        bottom_line = (
            f"Selling raw flower at commodity prices in a market with 450+ cultivators is a race to the bottom. "
            f"The operators protecting their margins have found toll processing partners, built direct retail "
            f"relationships, or moved into value-added products. Even at 50/50 splits, processed goods capture "
            f"more margin than wholesale flower."
        )
    else:
        first_change = snapshot.get("first_change", "")
        # Don't use stall-related first_change for operators who are actually running
        stall_phrases = ["getting to revenue", "path to operations", "not yet operational"]
        if actually_operating and any(p in first_change.lower() for p in stall_phrases):
            first_change = ""
        bottom_line = first_change or (
            f"The MA cannabis market isn't forgiving right now. Wholesale prices are down ~50% since 2021, "
            f"and operators without a clear margin strategy are getting squeezed out. "
            f"The difference between operators who survive and those who don't usually comes down to "
            f"one thing: how quickly they adapt when the data tells them something needs to change."
        )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F5F2EA;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<div style="max-width:620px;margin:0 auto;padding:20px;">

    <!-- Header -->
    <div style="background:#1A1917;padding:28px 24px 20px;border-radius:8px 8px 0 0;">
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:2.5px;color:#666;margin-bottom:10px;">Margin Pressure Snapshot</div>
        <h1 style="margin:0;font-size:22px;font-weight:700;color:#F5F2EA;line-height:1.3;">{biz}</h1>
        <div style="margin-top:6px;color:#888;font-size:12px;">{city}, MA &middot; {op_type} &middot; {date}</div>
    </div>

    <!-- Your Numbers -->
    <div style="background:#fff;padding:16px 12px;border-bottom:1px solid #eee;display:flex;flex-wrap:wrap;justify-content:space-around;">
        {stat_cells}
    </div>

    <!-- What We're Seeing -->
    <div style="background:#fff;padding:24px;border-bottom:1px solid #eee;">
        <h2 style="margin:0 0 14px;font-size:15px;font-weight:600;color:#1A1917;text-transform:uppercase;letter-spacing:0.5px;">What We're Seeing</h2>
        {obs_html}
    </div>

    <!-- Where You Might Be Losing Margin -->
    <div style="background:#fff;padding:24px;border-bottom:1px solid #eee;">
        <h2 style="margin:0 0 14px;font-size:15px;font-weight:600;color:#1A1917;text-transform:uppercase;letter-spacing:0.5px;">Where You Might Be Losing Margin</h2>
        {leak_html}
    </div>

    <!-- Bottom Line -->
    <div style="background:#1A1917;padding:24px;border-radius:0 0 8px 8px;">
        <h2 style="margin:0 0 10px;font-size:14px;font-weight:600;color:#D94F3D;text-transform:uppercase;letter-spacing:0.5px;">Bottom Line</h2>
        <p style="margin:0;font-size:14px;line-height:1.7;color:#ccc;">{bottom_line}</p>
        <div style="margin-top:20px;padding-top:14px;border-top:1px solid #333;">
            <p style="margin:0;font-size:13px;color:#888;">Generated from CCC licensing records, Google Business data, hiring signals, and market analysis for {city}, MA.</p>
            <p style="margin:8px 0 0;font-size:13px;color:#aaa;">Want the full analysis? Just reply to this email. &mdash; <strong style="color:#F5F2EA;">Roviq</strong></p>
            <div style="margin-top:16px;padding:14px 18px;background:#222;border-radius:6px;border:1px solid #333;">
                <p style="margin:0 0 6px;font-size:12px;color:#D94F3D;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Free Weekly Intel</p>
                <p style="margin:0 0 10px;font-size:13px;color:#ccc;line-height:1.5;">Get margin data, market signals, and competitive intel for MA cannabis operators every Tuesday.</p>
                <a href="https://randytorres.github.io/roviq-sales/newsletter.html" style="display:inline-block;padding:8px 20px;background:#D94F3D;color:#fff;text-decoration:none;border-radius:4px;font-size:12px;font-weight:600;letter-spacing:0.5px;">Subscribe to The Operator&rsquo;s Margin Report &rarr;</a>
            </div>
        </div>
    </div>

</div>
</body>
</html>"""


# ──────────────────────────────────────────────
# EMAIL SENDING VIA RESEND
# ──────────────────────────────────────────────

def send_email(to_email: str, subject: str, html_body: str, text_body: str = "") -> dict:
    """Send a single email via Resend API. Returns response dict."""
    if not RESEND_API_KEY:
        return {"error": "No RESEND_API key configured"}

    payload = json.dumps({
        "from": f"{FROM_NAME} <{FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_body,
        "text": text_body or subject,
    }).encode("utf-8")

    req = urllib.request.Request(
        RESEND_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "RoviqOutreach/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}


# ──────────────────────────────────────────────
# CAMPAIGN TRACKING
# ──────────────────────────────────────────────

def load_campaign() -> dict:
    """Load campaign tracking data."""
    if CAMPAIGN_FILE.exists():
        return json.loads(CAMPAIGN_FILE.read_text())
    return {"leads": {}, "created": datetime.now(timezone.utc).isoformat(), "stats": {}}


def save_campaign(campaign: dict):
    """Save campaign tracking data."""
    campaign["last_updated"] = datetime.now(timezone.utc).isoformat()
    CAMPAIGN_FILE.write_text(json.dumps(campaign, indent=2))


def get_lead_status(campaign: dict, email: str) -> dict:
    """Get tracking status for a lead."""
    return campaign.get("leads", {}).get(email, {
        "day0_sent": False, "day0_at": None, "day0_id": None,
        "day3_sent": False, "day3_at": None, "day3_id": None,
        "day7_sent": False, "day7_at": None, "day7_id": None,
        "replied": False, "bounced": False, "status": "pending",
    })


def update_lead_status(campaign: dict, email: str, day: int, result: dict):
    """Update tracking after sending an email."""
    if email not in campaign["leads"]:
        campaign["leads"][email] = get_lead_status(campaign, email)

    lead = campaign["leads"][email]
    now = datetime.now(timezone.utc).isoformat()

    if "error" in result:
        lead[f"day{day}_error"] = result["error"]
        lead["status"] = "error"
    else:
        lead[f"day{day}_sent"] = True
        lead[f"day{day}_at"] = now
        lead[f"day{day}_id"] = result.get("id", "unknown")
        lead["status"] = f"day{day}_sent"


# ──────────────────────────────────────────────
# LEAD DATA LOADING
# ──────────────────────────────────────────────

def load_outreach_leads() -> list[dict]:
    """Load leads from the full outreach CSV."""
    leads = []
    if not OUTREACH_CSV.exists():
        print(f"ERROR: {OUTREACH_CSV} not found")
        return leads

    with open(OUTREACH_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads


def load_snapshot(business_name: str) -> dict | None:
    """Load a JSON snapshot for a business."""
    # Convert business name to filename format
    slug = business_name.lower().strip()
    slug = slug.replace(" ", "_").replace(".", "").replace(",", "")
    slug = slug.replace("'", "").replace('"', "").replace("&", "and")
    slug = "".join(c for c in slug if c.isalnum() or c == "_")

    # Try exact match first
    path = SNAPSHOTS_DIR / f"snapshot_{slug}.json"
    if path.exists():
        return json.loads(path.read_text())

    # Try fuzzy match — find closest filename
    if SNAPSHOTS_DIR.exists():
        for f in SNAPSHOTS_DIR.iterdir():
            if f.suffix == ".json" and slug[:15] in f.stem:
                return json.loads(f.read_text())

    return None


def parse_email_content(raw: str) -> tuple[str, str]:
    """Parse 'Subject: ...\n\nBody...' format into (subject, body)."""
    lines = raw.strip().split("\n")
    subject = ""
    body_start = 0

    for i, line in enumerate(lines):
        if line.startswith("Subject:"):
            subject = line.replace("Subject:", "").strip()
            body_start = i + 1
            # Skip blank line after subject
            if body_start < len(lines) and lines[body_start].strip() == "":
                body_start += 1
            break

    body = "\n".join(lines[body_start:]).strip()
    return subject, body


# ──────────────────────────────────────────────
# EMAIL COMPOSITION
# ──────────────────────────────────────────────

def compose_day0_email(lead: dict, snapshot: dict | None) -> tuple[str, str, str]:
    """
    Compose Day 0 email: the intro email with snapshot attached inline.
    Returns (subject, html_body, text_body).
    """
    raw = lead.get("Email 1 (Day 0)", "")
    subject, text_body = parse_email_content(raw)
    biz = lead.get("Business Name", "")

    if not subject:
        subject = f"{lead.get('City', 'MA')} dispensary margins - seeing something"

    # Build HTML version with snapshot embedded
    enrichment = _get_enrichment(biz)
    snapshot_html = ""
    if snapshot:
        snapshot_html = f"""
        <div style="margin-top:24px;padding-top:16px;border-top:2px solid #eee;">
            <p style="font-size:13px;color:#888;margin-bottom:8px;">Here's what we're seeing for {biz}:</p>
            {snapshot_to_html(snapshot, enrichment)}
        </div>"""

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#fff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:24px;">
    {text_body.replace(chr(10), '<br>')}
    {snapshot_html}
</div>
</body>
</html>"""

    return subject, html_body, text_body


def compose_followup_email(lead: dict, day: int) -> tuple[str, str, str]:
    """Compose Day 3 or Day 7 follow-up. Returns (subject, html, text)."""
    col = {3: "Email 2 (Day 3)", 7: "Email 3 (Day 7)"}.get(day, "")
    raw = lead.get(col, "")
    subject, text_body = parse_email_content(raw)

    if not subject:
        biz = lead.get("Business Name", "")
        subject = f"Re: {biz} margin data" if day == 3 else f"Last try - {biz}"

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#fff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:24px;">
    {text_body.replace(chr(10), '<br>')}
</div>
</body>
</html>"""

    return subject, html_body, text_body


# ──────────────────────────────────────────────
# PIPELINE COMMANDS
# ──────────────────────────────────────────────

def cmd_generate_snapshots():
    """Generate HTML snapshots for all leads."""
    html_dir = OUTPUT_DIR / "snapshot_html"
    html_dir.mkdir(exist_ok=True)

    count = 0
    for f in SNAPSHOTS_DIR.iterdir():
        if f.suffix != ".json":
            continue
        snapshot = json.loads(f.read_text())
        html = snapshot_to_html(snapshot)
        out = html_dir / f.name.replace(".json", ".html")
        out.write_text(html)
        count += 1

    print(f"Generated {count} HTML snapshots in {html_dir}")


def cmd_dry_run(day: int = 0, rank_filter: list[int] | None = None):
    """Preview what would be sent without actually sending."""
    leads = load_outreach_leads()
    campaign = load_campaign()

    print(f"\n{'='*60}")
    print(f"  DRY RUN — Day {day} Emails")
    print(f"  From: {FROM_NAME} <{FROM_EMAIL}>")
    print(f"{'='*60}\n")

    to_send = []
    skipped = 0

    for lead in leads:
        rank = int(lead.get("Rank", 0))
        email = lead.get("Email", "").strip()

        if rank_filter and rank not in rank_filter:
            continue
        if not email:
            continue

        status = get_lead_status(campaign, email)

        # Skip if already sent for this day
        if status.get(f"day{day}_sent"):
            skipped += 1
            continue
        # Skip follow-ups if Day 0 wasn't sent
        if day > 0 and not status.get("day0_sent"):
            skipped += 1
            continue
        # Skip if replied or bounced
        if status.get("replied") or status.get("bounced"):
            skipped += 1
            continue

        to_send.append(lead)

    for lead in to_send[:5]:  # Show first 5
        biz = lead.get("Business Name", "")
        email = lead.get("Email", "")
        rank = lead.get("Rank", "?")

        if day == 0:
            snapshot = load_snapshot(biz)
            subject, _, _ = compose_day0_email(lead, snapshot)
        else:
            subject, _, _ = compose_followup_email(lead, day)

        print(f"  #{rank} {biz}")
        print(f"     To: {email}")
        print(f"     Subject: {subject}")
        has_snap = "Yes" if day == 0 and load_snapshot(biz) else "No"
        if day == 0:
            print(f"     Snapshot: {has_snap}")
        print()

    if len(to_send) > 5:
        print(f"  ... and {len(to_send) - 5} more")

    print(f"\nSummary: {len(to_send)} to send, {skipped} skipped")
    print(f"Batching: {BATCH_SIZE} per batch, {BATCH_DELAY_SEC}s between batches")
    est_time = (len(to_send) // BATCH_SIZE) * BATCH_DELAY_SEC
    print(f"Estimated time: ~{est_time // 60}m {est_time % 60}s")


def cmd_send(day: int = 0, rank_filter: list[int] | None = None):
    """Execute email sending for a specific day."""
    if not RESEND_API_KEY:
        print("ERROR: No RESEND_API key found. Set it in .env or environment.")
        sys.exit(1)

    leads = load_outreach_leads()
    campaign = load_campaign()

    to_send = []
    for lead in leads:
        rank = int(lead.get("Rank", 0))
        email = lead.get("Email", "").strip()

        if rank_filter and rank not in rank_filter:
            continue
        if not email:
            continue

        status = get_lead_status(campaign, email)
        if status.get(f"day{day}_sent"):
            continue
        if day > 0 and not status.get("day0_sent"):
            continue
        if status.get("replied") or status.get("bounced"):
            continue

        to_send.append(lead)

    if not to_send:
        print("No leads to send to. All caught up!")
        return

    print(f"\nSending Day {day} emails to {len(to_send)} leads...")
    print(f"From: {FROM_NAME} <{FROM_EMAIL}>\n")

    sent = 0
    errors = 0

    for i, lead in enumerate(to_send):
        biz = lead.get("Business Name", "")
        email = lead.get("Email", "").strip()
        rank = lead.get("Rank", "?")

        # Compose email
        if day == 0:
            snapshot = load_snapshot(biz)
            subject, html_body, text_body = compose_day0_email(lead, snapshot)
        else:
            subject, html_body, text_body = compose_followup_email(lead, day)

        # Send
        result = send_email(email, subject, html_body, text_body)

        if "error" in result:
            print(f"  ✗ #{rank} {biz} ({email}) — {result['error']}")
            errors += 1
        else:
            print(f"  ✓ #{rank} {biz} ({email}) — ID: {result.get('id', '?')}")
            sent += 1

        # Update tracking
        update_lead_status(campaign, email, day, result)

        # Rate limit: 2 requests/sec max → 0.6s between sends
        if i + 1 < len(to_send):
            time.sleep(0.6)

        # Batch pause every BATCH_SIZE emails
        if (i + 1) % BATCH_SIZE == 0 and i + 1 < len(to_send):
            print(f"\n  [Batch {(i+1)//BATCH_SIZE} complete. Waiting {BATCH_DELAY_SEC}s...]\n")
            time.sleep(BATCH_DELAY_SEC)

    save_campaign(campaign)
    print(f"\nDone: {sent} sent, {errors} errors out of {len(to_send)} total")


def cmd_status():
    """Show campaign status summary."""
    campaign = load_campaign()
    leads = campaign.get("leads", {})

    if not leads:
        print("No campaign data yet. Run --send to start.")
        return

    total = len(leads)
    day0 = sum(1 for l in leads.values() if l.get("day0_sent"))
    day3 = sum(1 for l in leads.values() if l.get("day3_sent"))
    day7 = sum(1 for l in leads.values() if l.get("day7_sent"))
    replied = sum(1 for l in leads.values() if l.get("replied"))
    bounced = sum(1 for l in leads.values() if l.get("bounced"))
    errors = sum(1 for l in leads.values() if l.get("status") == "error")

    print(f"\n{'='*50}")
    print(f"  Campaign Status")
    print(f"{'='*50}")
    print(f"  Total leads:    {total}")
    print(f"  Day 0 sent:     {day0}")
    print(f"  Day 3 sent:     {day3}")
    print(f"  Day 7 sent:     {day7}")
    print(f"  Replied:        {replied}")
    print(f"  Bounced:        {bounced}")
    print(f"  Errors:         {errors}")
    print(f"  Last updated:   {campaign.get('last_updated', 'never')}")
    print()

    # Show leads needing follow-up
    needs_day3 = []
    needs_day7 = []
    for email, data in leads.items():
        if data.get("day0_sent") and not data.get("day3_sent") and not data.get("replied"):
            d0_at = data.get("day0_at", "")
            if d0_at:
                sent_time = datetime.fromisoformat(d0_at)
                days_since = (datetime.now(timezone.utc) - sent_time).days
                if days_since >= 3:
                    needs_day3.append(email)
        if data.get("day3_sent") and not data.get("day7_sent") and not data.get("replied"):
            d3_at = data.get("day3_at", "")
            if d3_at:
                sent_time = datetime.fromisoformat(d3_at)
                days_since = (datetime.now(timezone.utc) - sent_time).days
                if days_since >= 4:
                    needs_day7.append(email)

    if needs_day3:
        print(f"  Ready for Day 3 follow-up: {len(needs_day3)} leads")
    if needs_day7:
        print(f"  Ready for Day 7 follow-up: {len(needs_day7)} leads")


def cmd_test_email():
    """Send a single test email to yourself to verify Resend is working."""
    if not RESEND_API_KEY:
        print("ERROR: No RESEND_API key found. Set it in .env or environment.")
        sys.exit(1)

    test_to = FROM_EMAIL
    print(f"Sending test email to {test_to}...")

    result = send_email(
        test_to,
        "Roviq Outreach — Test Email",
        "<h2>Test email from Roviq Outreach Pipeline</h2><p>If you see this, Resend is working.</p>",
        "Test email from Roviq Outreach Pipeline. If you see this, Resend is working.",
    )

    if "error" in result:
        print(f"  ✗ FAILED: {result['error']}")
        print("\nTroubleshooting:")
        print("  1. Check your RESEND_API key in .env")
        print("  2. Verify spacemanwins.win domain in Resend dashboard (resend.com/domains)")
        print("  3. Make sure DNS records (SPF, DKIM, DMARC) are set up")
    else:
        print(f"  ✓ SUCCESS — Email ID: {result.get('id', '?')}")
        print(f"  Check {test_to} inbox (and spam folder)")


def cmd_mark_replied(email: str):
    """Mark a lead as replied (stop follow-ups)."""
    campaign = load_campaign()
    if email in campaign.get("leads", {}):
        campaign["leads"][email]["replied"] = True
        campaign["leads"][email]["status"] = "replied"
        save_campaign(campaign)
        print(f"Marked {email} as replied. No more follow-ups.")
    else:
        print(f"Lead {email} not found in campaign tracking.")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return

    day = 0
    rank_filter = None

    # Parse --day N
    if "--day" in args:
        idx = args.index("--day")
        if idx + 1 < len(args):
            day = int(args[idx + 1])

    # Parse --ranks 1,2,3
    if "--ranks" in args:
        idx = args.index("--ranks")
        if idx + 1 < len(args):
            rank_filter = [int(r) for r in args[idx + 1].split(",")]

    # Commands
    if "--dry-run" in args:
        cmd_dry_run(day, rank_filter)
    elif "--send" in args:
        cmd_send(day, rank_filter)
    elif "--status" in args:
        cmd_status()
    elif "--generate-snapshots" in args:
        cmd_generate_snapshots()
    elif "--test" in args:
        cmd_test_email()
    elif "--mark-replied" in args:
        idx = args.index("--mark-replied")
        if idx + 1 < len(args):
            cmd_mark_replied(args[idx + 1])
        else:
            print("Usage: --mark-replied email@example.com")
    else:
        print("Unknown command. Use --help for usage.")


if __name__ == "__main__":
    main()
