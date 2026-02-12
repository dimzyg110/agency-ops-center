#!/usr/bin/env python3
from __future__ import annotations
"""
Newsletter Composer - The Operator's Margin Report

Takes scraped data from various sources and composes a ready-to-review
newsletter draft in both Markdown and HTML formats.

Usage:
    python composer.py --data-dir ./data --output ./drafts/newsletter_2026-02-04
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
import html

from data_contract import DATASET_FILES, GLASS_SCHEMA


# ============================================================================
# Data Loading
# ============================================================================

def load_json_file(filepath: Path) -> list[dict] | dict | None:
    """Load a JSON file, returning None if it doesn't exist or is invalid."""
    if not filepath.exists():
        print(f"  ⚠️  Missing: {filepath.name}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  ✓  Loaded: {filepath.name}")
        return data
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in {filepath.name}: {e}")
        return None


def load_all_data(data_dir: Path) -> dict[str, Any]:
    """Load all data files from the data directory."""
    print("\n📂 Loading data files...")
    
    news_raw = load_json_file(data_dir / DATASET_FILES["news"])
    events_raw = load_json_file(data_dir / DATASET_FILES["events"])
    reddit_raw = load_json_file(data_dir / DATASET_FILES["reddit"])
    tools_raw = load_json_file(data_dir / DATASET_FILES["tools"])
    market_raw = load_json_file(data_dir / DATASET_FILES["market"])
    glass_raw = load_json_file(data_dir / DATASET_FILES["glass"])
    
    # Extract lists from nested structures
    data = {
        'news': news_raw.get('articles', []) if isinstance(news_raw, dict) else (news_raw or []),
        'events': events_raw.get('events', []) if isinstance(events_raw, dict) else (events_raw or []),
        'reddit': reddit_raw.get('posts', []) if isinstance(reddit_raw, dict) else (reddit_raw or []),
        'tools': tools_raw.get('tools', []) if isinstance(tools_raw, dict) else (tools_raw or []),
        'market': market_raw if isinstance(market_raw, dict) else {},
        'glass': glass_raw if isinstance(glass_raw, dict) else {},
    }
    
    return data


# ============================================================================
# Content Selection & Ranking
# ============================================================================

def score_news_item(item: dict) -> float:
    """Score a news item for importance. Higher = more important.
    
    Heavily prioritizes MA-local content over generic national articles.
    """
    score = float(item.get("composite_relevance_score", 0) or 0)
    
    # ── MA-local boost (critical — requires cannabis context too) ──
    text = f"{item.get('title', '')} {item.get('headline', '')} {item.get('excerpt', '')} {item.get('description', '')}".lower()
    
    # Must be cannabis-related first
    cannabis_terms = ['cannabis', 'marijuana', 'dispensary', 'dispensaries', 'thc', 'weed',
                      'cultivation', 'cultivator', 'operator', 'license', 'ccc',
                      'cannabis control', 'adult-use', 'medical marijuana', 'edible',
                      'pre-roll', 'concentrate', 'flower', 'metrc', 'budtender']
    is_cannabis = any(term in text for term in cannabis_terms)
    
    ma_keywords = ['massachusetts', 'boston', 'cambridge', 'worcester', 'springfield',
                   'ccc', 'cannabis control commission', 'mass.', 'commonw',
                   'berkshire', 'cape cod', 'metrc', 'dispensary mass']
    ma_match_count = sum(1 for kw in ma_keywords if kw in text)
    
    if is_cannabis and ma_match_count > 0:
        score += 40 + (ma_match_count * 5)  # Massive MA-local boost
    elif ma_match_count > 0 and not is_cannabis:
        score -= 10  # Penalize MA articles with no cannabis relevance
    
    geo = (item.get('geo_scope') or '').lower()
    if geo == 'ma':
        score += 30
    
    # ── Content quality signals ──
    title = (item.get('title') or item.get('headline') or '').lower()
    
    # Penalize junk/non-article results
    junk_signals = ['home page', 'about us', 'subscribe', 'newsletter', 'login',
                    'skip to', 'all your cannabis news', 'in one place']
    if any(j in title for j in junk_signals):
        score -= 50
    
    # Short titles are likely nav elements, not articles
    if len(title.strip()) < 20:
        score -= 20
    
    # ── Priority keywords ──
    high_value = ['license', 'regulation', 'approved', 'announces', 'launches',
                  'revenue', 'sales record', 'opens', 'closes', 'social consumption',
                  'delivery', 'equity', 'enforcement', 'inspection']
    for keyword in high_value:
        if keyword in title:
            score += 8
    
    # ── Source quality ──
    source = (item.get('source') or '').lower()
    url = (item.get('url') or '').lower()
    ma_sources = ['masslive', 'boston globe', 'boston.com', 'wbur', 'wcvb', 'nbc boston']
    national_sources = ['marijuana moment', 'mjbizdaily', 'cannabis business times']
    if any(s in source for s in ma_sources):
        score += 20
    elif any(s in source for s in national_sources):
        score += 8

    # ── Penalize non-MA regional publications that might slip through ──
    non_ma_domains = ['rcbizjournal.com', 'hudsonvalley', 'njbiz.com', 'silive.com']
    if any(d in url for d in non_ma_domains):
        score -= 60  # Heavy penalty — these are not MA content

    # ── Penalize dubious sources ──
    blocked_sources = ['dontlegalizedrugs', 'infowars', 'dailystormer']
    if any(d in url for d in blocked_sources):
        score -= 100

    # ── Engagement signals ──
    score += item.get('engagement', 0) * 0.1
    score += item.get('shares', 0) * 0.5
    score += item.get('comments', 0) * 0.2
    
    return score


def score_reddit_post(post: dict) -> float:
    """Score a Reddit post for relevance."""
    score = 0.0
    
    # Upvotes/score
    score += post.get('score', 0) * 0.1
    score += post.get('upvotes', 0) * 0.1
    score += post.get('num_comments', 0) * 0.3
    
    # Content type bonus
    if post.get('is_self', False):
        score += 5  # Discussion posts often have good insights
    
    return score


def score_tool(tool: dict) -> float:
    """Score a tool for relevance to operators."""
    score = float(tool.get("composite_relevance_score", 0) or 0)
    
    # Operator-focused keywords
    description = (tool.get('description') or tool.get('summary') or '').lower()
    name = (tool.get('name') or tool.get('title') or '').lower()
    text = f"{name} {description}"
    
    operator_keywords = ['pos', 'inventory', 'compliance', 'tracking', 'seed-to-sale',
                        'dispensary', 'cultivation', 'retail', 'erp', 'crm', 'analytics']
    for keyword in operator_keywords:
        if keyword in text:
            score += 10
    
    # Free/open source bonus
    if 'free' in text or 'open source' in text:
        score += 5
    
    return score


def select_top_story(news: list[dict] | None) -> dict | None:
    """Select the most important news item as the top story."""
    if not news:
        return None
    
    scored = [(item, score_news_item(item)) for item in news]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return scored[0][0] if scored else None


def select_quick_hits(news: list[dict] | None, exclude: dict | None = None, count: int = 3) -> list[dict]:
    """Select secondary news items for quick hits."""
    if not news:
        return []
    
    # Filter out the top story
    filtered = [item for item in news if item != exclude]
    scored = [(item, score_news_item(item)) for item in filtered]
    scored.sort(key=lambda x: x[1], reverse=True)

    chosen: list[dict] = []
    domains: set[str] = set()
    for item, _ in scored:
        if len(chosen) >= count:
            break
        domain = (item.get("url") or "").split("/")[2] if "://" in str(item.get("url")) else ""
        if domain and domain in domains and len(scored) > count:
            continue
        chosen.append(item)
        if domain:
            domains.add(domain)

    if len(chosen) < count:
        for item, _ in scored:
            if item in chosen:
                continue
            chosen.append(item)
            if len(chosen) >= count:
                break

    return chosen


def select_tool_of_week(tools: list[dict] | None) -> dict | None:
    """Select the best tool to feature."""
    if not tools:
        return None
    
    scored = [(tool, score_tool(tool)) for tool in tools]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return scored[0][0] if scored else None


def select_events(events: list[dict] | None, count: int = 5) -> list[dict]:
    """Select upcoming events, sorted by date."""
    if not events:
        return []
    
    # Try to sort by date
    def parse_event_date(event: dict) -> datetime:
        date_str = event.get('date') or event.get('start_date') or event.get('datetime') or ''
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(date_str[:19], fmt)
                except (ValueError, TypeError):
                    continue
        except Exception:
            pass
        return datetime.max  # Push unparseable dates to end
    
    sorted_events = sorted(events, key=parse_event_date)
    return sorted_events[:count]


def extract_market_insights(market: dict | list | None) -> list[str]:
    """Extract key market insights."""
    if not market:
        return []
    
    insights = []
    
    if isinstance(market, dict):
        # Handle market_pulse list format (preferred)
        if 'market_pulse' in market and isinstance(market['market_pulse'], list):
            insights = market['market_pulse'][:3]
        # Handle dict insights format
        elif 'insights' in market and isinstance(market['insights'], list):
            insights = market['insights'][:3]
        elif 'highlights' in market:
            insights = market['highlights'][:3]
        elif 'summary' in market:
            insights = [market['summary']]
        else:
            # Try to extract from nested data
            for key in ['price_trends', 'market_trends', 'analysis']:
                if key in market and market[key]:
                    if isinstance(market[key], list):
                        insights.extend([str(x) for x in market[key][:3]])
                    else:
                        insights.append(str(market[key]))
    elif isinstance(market, list):
        # Handle list format
        for item in market[:3]:
            if isinstance(item, str):
                insights.append(item)
            elif isinstance(item, dict):
                text = item.get('insight') or item.get('summary') or item.get('text') or str(item)
                insights.append(text)
    
    return insights[:3]


def extract_demographic_card(market: dict | list | None) -> dict | None:
    if not isinstance(market, dict):
        return None
    card = market.get("demographic_trend_card")
    if isinstance(card, dict):
        return card
    return None


def extract_license_news(news: list[dict] | None, reddit: list[dict] | None) -> list[dict]:
    """Extract license-related news from available sources."""
    license_items = []
    license_keywords = ['license', 'licensed', 'licensing', 'permit', 'approval', 
                       'ccc', 'closure', 'revoked', 'suspended', 'application']
    
    # Check news
    if news:
        for item in news:
            title = (item.get('title') or item.get('headline') or '').lower()
            if any(kw in title for kw in license_keywords):
                license_items.append({
                    "title": item.get('title') or item.get('headline'),
                    "url": item.get("url"),
                    "source": item.get("source"),
                    "published": item.get("published"),
                })
    
    # Check reddit
    if reddit:
        for post in reddit:
            title = (post.get('title') or '').lower()
            if any(kw in title for kw in license_keywords):
                subreddit = post.get("subreddit")
                license_items.append({
                    "title": post.get('title'),
                    "url": post.get("url"),
                    "source": f"Reddit/r/{subreddit}" if subreddit else "Reddit",
                    "published": post.get("published"),
                })

    deduped = []
    seen = set()
    for item in license_items:
        key = (item.get("title"), item.get("url"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:3]


def extract_big_number(market: dict | list | None, news: list[dict] | None) -> tuple[str, str]:
    """Extract a compelling statistic for THE NUMBER section."""
    # Default
    number = "N/A"
    context = "No market data available this week."
    
    if market:
        if isinstance(market, dict):
            # Canonical market payload
            the_number = market.get("the_number")
            if isinstance(the_number, dict):
                value = str(the_number.get("value", "")).strip()
                label = str(the_number.get("context", "")).strip()
                if value and label:
                    return value, label

            # Look for specific number fields
            for key in ['total_sales', 'weekly_sales', 'market_cap', 'growth_rate', 
                       'average_price', 'transaction_volume']:
                if key in market and market[key]:
                    val = market[key]
                    if isinstance(val, (int, float)):
                        if val >= 1_000_000_000:
                            number = f"${val/1_000_000_000:.1f}B"
                        elif val >= 1_000_000:
                            number = f"${val/1_000_000:.1f}M"
                        elif val >= 1000:
                            number = f"${val/1000:.1f}K"
                        else:
                            number = f"${val:,.0f}"
                        context = f"{key.replace('_', ' ').title()} for the week."
                        break
                    elif isinstance(val, str):
                        number = val
                        context = f"{key.replace('_', ' ').title()} for the week."
                        break
            
            # Check for percentage changes
            if number == "N/A":
                for key in ['change_percent', 'growth', 'yoy_change', 'mom_change']:
                    if key in market:
                        val = market[key]
                        if isinstance(val, (int, float)):
                            sign = "+" if val >= 0 else ""
                            number = f"{sign}{val:.1f}%"
                            context = f"Week-over-week market change."
                            break
    
    return number, context


def generate_margin_tip(reddit: list[dict] | None, tools: list[dict] | None) -> dict:
    """Generate an actionable, MA-specific margin improvement tip.
    
    Returns a dict with 'title', 'body', and 'action' for richer formatting.
    """
    tips = [
        {
            "title": "Rethink Your Ounce Pricing",
            "body": (
                "Most MA operators price ounces at a flat discount — 8x the eighth price minus 15%. "
                "That's leaving money on the table. Pull a POS report on your ounce buyers from the last 90 days. "
                "If they also purchase edibles, carts, or pre-rolls at normal prices, they're convenience shoppers "
                "who happen to buy in bulk — not pure price-shoppers. They'll tolerate a smaller ounce discount "
                "if you bundle: 'Buy an ounce, get 15% off any cartridge.' Average lift: $8-12 per transaction."
            ),
            "action": "Ask your POS vendor how to segment ounce purchasers with cross-category buys.",
        },
        {
            "title": "Audit Your Metrc Reconciliation",
            "body": (
                "The CCC is cracking down on 'ghost inventory' — products in Metrc that aren't on your shelf. "
                "Spend 15 minutes checking that your physical inventory matches the system. "
                "This is the #1 cause of compliance violations in MA right now, and a failed audit "
                "costs far more than the 15 minutes it takes to verify."
            ),
            "action": "Walk the floor with your Metrc manifest open. Flag any discrepancies before the CCC does.",
        },
        {
            "title": "Capture Closed Competitor Traffic",
            "body": (
                "27 MA cannabis licenses were surrendered in 2025. Those customers need a new store. "
                "Google your closed competitors and make sure your Google Business profile shows up for their keywords. "
                "Add their name in your description: 'Convenient to former XYZ customers.' "
                "Run geo-targeted ads in their zip codes for 2 weeks — it's the cheapest customer acquisition you'll find."
            ),
            "action": "Check if any competitors near you have closed. Update your Google Business profile today.",
        },
        {
            "title": "The Add-On Ask That Actually Works",
            "body": (
                "Most budtenders skip the upsell because they feel salesy. Try this phrase instead: "
                "'One more thing — a lot of people who buy [their product] also grab [complementary product] "
                "because [specific reason]. Want me to add one?' You're not selling — you're sharing "
                "what other people do. Social proof removes the friction. Expected lift: $5-12 per transaction."
            ),
            "action": "At 50+ transactions/day, that's $250-600/week — $13K-31K/year from one phrase.",
        },
        {
            "title": "Use Delivery Exclusivity Before It Expires",
            "body": (
                "MA's social equity delivery exclusivity runs through 2029. If you're not partnering with a "
                "social equity delivery courier, you're missing the only protected growth channel left. "
                "The big MSOs can't touch this segment. Find your delivery partner this month."
            ),
            "action": "Search the CCC's delivery license list and reach out to 3 couriers in your area.",
        },
        {
            "title": "Check Your ID Scanner Firmware",
            "body": (
                "New CT, NY, and RI IDs are failing on outdated Veriscan versions. If you're rejecting "
                "valid customers because your scanner can't read their ID, that's money walking out. "
                "Border-town operators in the Berkshires and SouthCoast are especially exposed."
            ),
            "action": "Takes 5 minutes to check for firmware updates. Do it before your next shift.",
        },
        {
            "title": "Position Your Best Margin Product at Eye Level",
            "body": (
                "Walk your floor right now. Is your highest-margin product at eye level, or buried on a bottom shelf? "
                "Infused pre-rolls are the fastest-growing category in MA — if they're not visible, "
                "you're losing sales. Move your craft flower and premium concentrates front-and-center."
            ),
            "action": "Rearrange one shelf today to put your best-margin product where customers see it first.",
        },
        {
            "title": "Know Your Market Share Number",
            "body": (
                "MA did $1.65B in adult-use sales in 2025, roughly $137M/month. "
                "Your monthly revenue ÷ $137M = your market share. "
                "If you don't know this number, you can't set realistic growth targets. "
                "Track it monthly and benchmark against your region (Boston, Valley, Cape, Berkshires)."
            ),
            "action": "Pull your last 3 months of revenue and calculate your slice of the $137M/month pie.",
        },
    ]
    
    # Rotate weekly
    week_num = datetime.now().isocalendar()[1]
    return tips[week_num % len(tips)]


# ============================================================================
# Content Formatting
# ============================================================================

def get_item_title(item: dict) -> str:
    """Extract title from various item formats."""
    return item.get('title') or item.get('headline') or item.get('name') or 'Untitled'


def get_item_summary(item: dict, max_length: int = 200) -> str:
    """Extract or generate a summary."""
    summary = (item.get('summary') or item.get('description') or 
               item.get('excerpt') or item.get('content') or item.get('body') or item.get('selftext') or '')
    
    # Truncate if needed
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
    
    return summary or "Summary could not be extracted from source snippet."


def _load_env():
    """Load .env file for API keys."""
    # Walk upward from this file to find .env
    env_candidates = []
    current = Path(__file__).resolve().parent
    for _ in range(5):
        env_candidates.append(current / ".env")
        current = current.parent
    # Also check cwd
    env_candidates.append(Path.cwd() / ".env")

    for env_path in env_candidates:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())
            break


_load_env()


def _llm_generate(prompt: str, max_tokens: int = 500) -> str | None:
    """Generate text using OpenAI API. Returns None on failure."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        return None

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("NEWSLETTER_REWRITE_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": (
                    "You write the 'Operator's Margin Report,' a weekly newsletter for Massachusetts "
                    "cannabis dispensary operators. Your voice is direct, data-driven, and blunt — "
                    "like a smart friend who happens to track the CCC. No fluff, no hype. "
                    "Always tell operators what a story means for THEIR margins, THEIR store, THEIR week. "
                    "Use specific numbers when available. Write in second person ('you'). "
                    "Keep it punchy — short paragraphs, bold key numbers."
                )},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"  ⚠️  LLM generation failed: {e}")
        return None


def maybe_grounded_rewrite(text: str, citations: list[str]) -> str:
    """Rewrite a snippet with editorial voice if LLM is available."""
    if os.getenv("NEWSLETTER_ENABLE_LLM_REWRITE", "1") != "1":
        return text
    if not citations or not text:
        return text

    prompt = (
        "Rewrite this newsletter snippet in 2-3 concise sentences. "
        "Keep all facts unchanged. Add operator-focused context — "
        "what does this mean for a dispensary operator in Massachusetts?\n\n"
        f"Source text:\n{text}\n\nSource URL: {citations[0]}"
    )
    result = _llm_generate(prompt, max_tokens=200)
    return result or text


def generate_editorial_top_story(
    item: dict,
    market_data: dict | None = None,
) -> str | None:
    """Generate a rich editorial analysis for the top story.

    This is what made newsletter_v2_real.md compelling — an LLM turns
    a raw news snippet into a multi-paragraph editorial with analysis,
    context, and operator implications.
    """
    title = item.get("title") or item.get("headline") or ""
    excerpt = item.get("excerpt") or item.get("description") or item.get("summary") or ""
    url = item.get("url") or ""
    source = item.get("source") or ""

    # Build context from market data
    market_context = ""
    if market_data and isinstance(market_data, dict):
        insights = market_data.get("insights", {})
        total_ops = insights.get("total_operators", 0)
        new_licenses = insights.get("new_licenses", 0)
        hiring = insights.get("hiring_hot", [])
        market_context = (
            f"\nContext: {total_ops} MA operators tracked, {new_licenses} new licenses this week. "
            f"Hiring leaders: {', '.join(hiring[:3]) if hiring else 'none notable'}."
        )

    prompt = (
        f"Write a 3-4 paragraph editorial analysis of this top story for MA cannabis dispensary operators.\n\n"
        f"Headline: {title}\n"
        f"Source: {source}\n"
        f"Excerpt: {excerpt}\n"
        f"URL: {url}\n"
        f"{market_context}\n\n"
        f"Guidelines:\n"
        f"- Open with what happened, then immediately pivot to what it MEANS for operator margins\n"
        f"- Include specific numbers and data points where possible\n"
        f"- End with a clear 'what to do' recommendation\n"
        f"- Be direct and blunt — no generic industry cheerleading\n"
        f"- Reference Massachusetts and the CCC specifically where relevant\n"
        f"- 200-300 words total"
    )
    return _llm_generate(prompt, max_tokens=500)


def get_item_url(item: dict) -> str:
    """Extract URL from item."""
    return item.get('url') or item.get('link') or item.get('href') or '#'


def get_item_source(item: dict) -> str:
    return (item.get("source") or item.get("subreddit") or "").strip()


def get_item_date(item: dict) -> str:
    return (item.get("published") or item.get("date") or "").strip()


def format_event(event: dict) -> str:
    """Format an event for display."""
    name = event.get('name') or event.get('title') or 'Unnamed Event'
    date = event.get('date') or event.get('start_date') or 'TBD'
    location = event.get('location') or event.get('venue') or event.get('city') or 'TBD'
    
    return f"{name} - {date} - {location}"


# ============================================================================
# Newsletter Generation
# ============================================================================

def format_price_wire(glass_data: dict) -> list[str]:
    """Format GLASS Price Wire section for the newsletter.

    Shows MA average prices by category, biggest drops, biggest increases.
    """
    lines: list[str] = []
    price_wire = glass_data.get("price_wire", {})
    if not price_wire or not price_wire.get("category_averages"):
        return []

    lines.append("### 📊 PRICE WIRE")
    lines.append("")
    lines.append("*Live pricing from 490+ MA dispensary menus, updated daily via GLASS.*")
    lines.append("")

    # Category averages table
    lines.append("| Category | Avg Price | Median | Observations |")
    lines.append("|----------|----------|--------|-------------|")

    category_labels = {
        "flower": "🌿 Flower",
        "edible": "🍫 Edibles",
        "vape": "💨 Vapes",
        "concentrate": "💎 Concentrates",
        "preroll": "🚬 Pre-Rolls",
    }

    for cat in price_wire["category_averages"]:
        label = category_labels.get(cat["category"], cat["category"].title())
        lines.append(
            f"| {label} | **${cat['avg_price']:.2f}** | "
            f"${cat['median_price']:.2f} | {cat['observation_count']:,} |"
        )

    total_obs = price_wire.get("total_observations", 0)
    lines.append("")
    lines.append(f"*Based on {total_obs:,} price observations this week.*")
    lines.append("")

    # Biggest drops (deals)
    drops = price_wire.get("biggest_drops", [])
    if drops:
        lines.append("**💥 BIGGEST VALUE FINDS:**")
        for item in drops[:5]:
            pct = abs(item.get("pct_vs_avg", 0))
            lines.append(
                f"- {item['brand']} {item['product']} at {item['operator']} "
                f"({item['city'].title()}): **${item['price']:.2f}** "
                f"({pct:.0f}% below {item['category']} avg)"
            )
        lines.append("")

    # Biggest increases (premium)
    increases = price_wire.get("biggest_increases", [])
    if increases:
        lines.append("**📈 PREMIUM SHELF:**")
        for item in increases[:3]:
            pct = item.get("pct_vs_avg", 0)
            lines.append(
                f"- {item['brand']} {item['product']} at {item['operator']} "
                f"({item['city'].title()}): **${item['price']:.2f}** "
                f"(+{pct:.0f}% above {item['category']} avg)"
            )
        lines.append("")

    return lines


def format_threat_radar(glass_data: dict) -> list[str]:
    """Format GLASS Threat Radar section for the newsletter.

    Shows new competitors detected, active threats, enforcement activity.
    """
    lines: list[str] = []
    threat_data = glass_data.get("threat_radar", {})
    if not threat_data:
        return []

    new_ops = threat_data.get("new_operators", [])
    threats = threat_data.get("active_threats", [])

    if not new_ops and not threats:
        return []

    lines.append("### 🔴 THREAT RADAR")
    lines.append("")

    # New operators detected
    new_count = threat_data.get("new_operator_count", 0)
    if new_count > 0:
        lines.append(f"**{new_count} new dispensaries detected this week on MA menus.**")
        lines.append("")
        for op in new_ops[:8]:
            lines.append(f"- **{op['name']}** — {op['city']}, {op['state']}")
        if new_count > 8:
            lines.append(f"- *...and {new_count - 8} more*")
        lines.append("")

    # Active threats
    if threats:
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }
        lines.append("**ACTIVE ALERTS:**")
        for threat in threats[:5]:
            emoji = severity_emoji.get(threat.get("severity", ""), "⚪")
            desc = threat.get("description", "")
            if len(desc) > 120:
                desc = desc[:120].rsplit(" ", 1)[0] + "..."
            lines.append(
                f"- {emoji} **{threat.get('entity', 'Unknown')}** [{threat['type']}]: {desc}"
            )
        lines.append("")

    return lines


def format_brand_movers(glass_data: dict) -> list[str]:
    """Format GLASS Brand Movers section for the newsletter."""
    lines: list[str] = []
    brand_data = glass_data.get("brand_movers", {})
    if not brand_data or not brand_data.get("top_brands"):
        return []

    lines.append("### 🏷️ BRAND MOVERS")
    lines.append("")
    lines.append("*Top brands by shelf presence across MA dispensary menus this week.*")
    lines.append("")

    for brand in brand_data["top_brands"][:10]:
        lines.append(
            f"- **{brand['brand']}** — in {brand['store_count']} stores, "
            f"avg ${brand['avg_price']:.2f}"
        )

    total = brand_data.get("total_brands_tracked", 0)
    if total:
        lines.append(f"\n*{total:,} total brands tracked across MA.*")
    lines.append("")
    return lines


def generate_markdown(data: dict[str, Any], week_date: str) -> str:
    """Generate the newsletter in Markdown format."""
    
    # Select content
    top_story = select_top_story(data['news'])
    quick_hits = select_quick_hits(data['news'], exclude=top_story)
    tool = select_tool_of_week(data['tools'])
    events = select_events(data['events'])
    market_insights = extract_market_insights(data['market'])
    demographic_card = extract_demographic_card(data['market'])
    license_news = extract_license_news(data['news'], data['reddit'])
    big_number, number_context = extract_big_number(data['market'], data['news'])
    margin_tip = generate_margin_tip(data['reddit'], data['tools'])
    glass_data = data.get('glass', {})

    # Enhance THE NUMBER with GLASS market stats if available
    market_stats = glass_data.get("market_stats", {})
    if market_stats and big_number == "N/A":
        total_ops = market_stats.get("total_operators", 0)
        if total_ops:
            big_number = f"{total_ops:,}"
            number_context = "dispensaries tracked across Massachusetts menus via GLASS"
    
    # Build newsletter
    lines = []
    
    lines.append(f"# The Operator's Margin Report")
    lines.append(f"## Week of {week_date}")
    lines.append("")
    lines.append("*Survival intel for Massachusetts cannabis operators. Less headlines, more margin.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Price Wire (NEW — GLASS powered, leads the newsletter)
    price_wire_lines = format_price_wire(glass_data)
    if price_wire_lines:
        lines.extend(price_wire_lines)
        lines.append("---")
        lines.append("")
    
    # Top Story
    lines.append("### 🔥 TOP STORY")
    if top_story:
        lines.append(f"**{get_item_title(top_story)}**")
        lines.append("")
        
        # Try editorial generation first — this is what made v2_real great
        editorial = generate_editorial_top_story(top_story, market_data=data['market'])
        if editorial:
            lines.append(editorial)
        else:
            # Fallback to rewritten summary
            summary = get_item_summary(top_story, 300)
            summary = maybe_grounded_rewrite(summary, [get_item_url(top_story)])
            lines.append(summary)
        
        source = get_item_source(top_story)
        published = get_item_date(top_story)
        if source or published:
            source_line = " · ".join([p for p in [source, published] if p])
            lines.append(f"\n_Source: {source_line}_")
        url = get_item_url(top_story)
        if url != '#':
            lines.append(f"\n[Read more]({url})")
    else:
        lines.append("*No major stories this week.*")
    lines.append("")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # The Number
    lines.append("### 📊 THE NUMBER")
    lines.append("")
    lines.append(f"# {big_number}")
    lines.append("")
    lines.append(number_context)
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Market Pulse
    lines.append("### 📈 MARKET PULSE")
    lines.append("")
    if market_insights:
        for insight in market_insights:
            # Add operator-focused context to raw bullet points
            lines.append(f"**🔹 {insight}**")
            lines.append("")
    else:
        lines.append("*Market data not available this week.*")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Threat Radar (NEW — GLASS powered)
    threat_lines = format_threat_radar(glass_data)
    if threat_lines:
        lines.extend(threat_lines)
        lines.append("---")
        lines.append("")

    # Brand Movers (NEW — GLASS powered)
    brand_lines = format_brand_movers(glass_data)
    if brand_lines:
        lines.extend(brand_lines)
        lines.append("---")
        lines.append("")

    # Demographic & Equity Signal
    lines.append("### 🌍 DEMOGRAPHIC & EQUITY SIGNAL")
    if demographic_card:
        insight = demographic_card.get("insight") or "No demographic insight found."
        implication = demographic_card.get("ma_operator_implication") or ""
        source_url = demographic_card.get("source_url")
        lines.append(f"- {insight}")
        if implication:
            lines.append(f"- {implication}")
        if source_url:
            lines.append(f"- [Demographic source]({source_url})")
    else:
        lines.append("- Demographic trend data missing; run CCC ingest before send.")
    lines.append("")
    
    # License Watch
    lines.append("### 📋 LICENSE WATCH")
    if license_news:
        for item in license_news:
            title = item.get("title") or "License update"
            url = item.get("url") or "#"
            source = item.get("source")
            published = item.get("published")
            meta = " · ".join([p for p in [source, published] if p])
            if url != "#":
                bullet = f"- [{title}]({url})"
            else:
                bullet = f"- {title}"
            if meta:
                bullet += f" — {meta}"
            lines.append(bullet)
    else:
        lines.append("*No major license updates this week.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Tool of the Week
    lines.append("### 🛠️ TOOL OF THE WEEK")
    lines.append("")
    if tool:
        tool_name = get_item_title(tool)
        lines.append(f"**{tool_name}**")
        lines.append("")
        tool_summary = get_item_summary(tool, 400)
        tool_summary = maybe_grounded_rewrite(tool_summary, [get_item_url(tool)])
        lines.append(tool_summary)
        lines.append("")
        if tool.get("why_ma_impact"):
            lines.append(f"_{tool.get('why_ma_impact')}_")
            lines.append("")
        url = get_item_url(tool)
        if url != '#':
            lines.append(f"[Check it out →]({url})")
        lines.append("")
    else:
        lines.append("*No tool featured this week.*")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # Upcoming Events
    lines.append("### 📅 UPCOMING EVENTS")
    if events:
        for event in events:
            event_text = format_event(event)
            event_url = event.get("url")
            if event_url:
                lines.append(f"- [{event_text}]({event_url})")
            else:
                lines.append(f"- {event_text}")
    else:
        lines.append("*No upcoming events listed.*")
    lines.append("")
    
    # Quick Hits
    lines.append("### ⚡ QUICK HITS")
    if quick_hits:
        for item in quick_hits:
            title = get_item_title(item)
            url = get_item_url(item)
            source = get_item_source(item)
            published = get_item_date(item)
            meta = " · ".join([p for p in [source, published] if p])
            if url != "#":
                bullet = f"- [{title}]({url})"
            else:
                bullet = f"- {title}"
            if meta:
                bullet += f" — {meta}"
            lines.append(bullet)
            if item.get("why_ma_impact"):
                lines.append(f"  - {item.get('why_ma_impact')}")
    else:
        lines.append("*No additional news this week.*")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Margin Tip (now a rich dict)
    lines.append("### 💡 MARGIN TIP")
    lines.append("")
    if isinstance(margin_tip, dict):
        lines.append(f"**{margin_tip.get('title', 'Margin Tip')}**")
        lines.append("")
        lines.append(margin_tip.get('body', ''))
        lines.append("")
        action = margin_tip.get('action', '')
        if action:
            lines.append(f"**Action:** {action}")
        lines.append("")
    else:
        # Fallback for string tips
        lines.append(str(margin_tip))
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Compliance Reminder
    lines.append("### 📋 COMPLIANCE REMINDER")
    lines.append("")
    compliance_reminders = [
        {
            "title": "Video Surveillance Retention",
            "body": (
                "Massachusetts requires **90 days minimum** of video surveillance footage. "
                "When's the last time you verified your DVR is actually retaining that much? "
                "Check: all cameras recording, 90+ days accessible, timestamps accurate. "
                "This is a common violation during inspections."
            ),
        },
        {
            "title": "Exit Bag Labeling",
            "body": (
                "Inspectors recently cited multiple stores for faded or illegible 'Keep out of reach of children' "
                "text on exit bags. Check your bag inventory — if the print is wearing off, replace them "
                "before your next order. Costs $50 to reprint. Costs a lot more when they cite you."
            ),
        },
        {
            "title": "Purchase Limit Math",
            "body": (
                "Train your team on equivalence: 1 oz flower = 5g concentrate = 500mg edibles. "
                "Customers trying to mix categories get confused and frustrated. "
                "This question comes up 5+ times/day — your team should answer it cold."
            ),
        },
        {
            "title": "Metrc Batch Tracking",
            "body": (
                "Make sure incoming transfers match physical product counts exactly. "
                "'Ghost inventory' — products in Metrc that aren't on your shelf — is the #1 "
                "audit finding right now. A 15-minute daily reconciliation prevents major headaches."
            ),
        },
    ]
    week_num = datetime.now().isocalendar()[1]
    reminder = compliance_reminders[week_num % len(compliance_reminders)]
    lines.append(f"**{reminder['title']}**")
    lines.append("")
    lines.append(reminder['body'])
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Footer
    lines.append("## 📬 THAT'S THE REPORT")
    lines.append("")
    lines.append("*The Operator's Margin Report is written for dispensary operators who are tired of generic industry news. Every number is sourced. Every tip is actionable.*")
    lines.append("")
    lines.append("*Powered by [GLASS](https://glass.roviq.com) — real-time price intelligence from 490+ MA dispensary menus.*")
    lines.append("")
    lines.append("Got a question? A tip? Reply to this email.")
    lines.append("")
    lines.append("*The Operator's Margin Report is published by Roviq — AI-powered intelligence for cannabis operators.*")
    lines.append("*Boston, MA · [roviq.com](https://roviq.com)*")
    
    return "\n".join(lines)


def markdown_to_html(md_content: str) -> str:
    """Convert markdown newsletter to HTML with styling."""
    
    # Escape HTML in content (but we'll unescape our own tags)
    content = html.escape(md_content)
    
    # Convert markdown to HTML
    # Headers
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # Bold
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    
    # Italic
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
    
    # Links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
    
    # Lists
    lines = content.split('\n')
    in_list = False
    result = []
    for line in lines:
        if line.startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    if in_list:
        result.append('</ul>')
    content = '\n'.join(result)
    
    # Horizontal rule
    content = content.replace('---', '<hr>')
    
    # Paragraphs (double newlines)
    content = re.sub(r'\n\n+', '</p><p>', content)
    content = f'<p>{content}</p>'
    content = content.replace('<p></p>', '')
    content = content.replace('<p><h', '<h')
    content = content.replace('</h1></p>', '</h1>')
    content = content.replace('</h2></p>', '</h2>')
    content = content.replace('</h3></p>', '</h3>')
    content = content.replace('<p><ul>', '<ul>')
    content = content.replace('</ul></p>', '</ul>')
    content = content.replace('<p><hr></p>', '<hr>')
    
    # Build full HTML document
    html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Operator's Margin Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 680px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a5f2a;
            border-bottom: 3px solid #2d8a3e;
            padding-bottom: 10px;
            margin-bottom: 5px;
        }}
        h2 {{
            color: #666;
            font-weight: normal;
            margin-top: 0;
            font-size: 1.1em;
        }}
        h3 {{
            color: #1a5f2a;
            margin-top: 30px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        strong {{
            color: #1a5f2a;
        }}
        a {{
            color: #2d8a3e;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }}
        .footer {{
            text-align: center;
            color: #888;
            font-size: 0.9em;
        }}
        .big-number {{
            font-size: 2.5em;
            color: #1a5f2a;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>'''
    
    return html_doc


def generate_checklist(data: dict[str, Any], week_date: str) -> str:
    """Generate a review checklist for the newsletter."""
    
    lines = []
    lines.append(f"# Newsletter Review Checklist - Week of {week_date}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    lines.append("## Data Sources")
    lines.append(f"[ ] News data loaded: {'✓' if data['news'] else '✗'}")
    lines.append(f"[ ] Events data loaded: {'✓' if data['events'] else '✗'}")
    lines.append(f"[ ] Reddit data loaded: {'✓' if data['reddit'] else '✗'}")
    lines.append(f"[ ] Tools data loaded: {'✓' if data['tools'] else '✗'}")
    lines.append(f"[ ] Market data loaded: {'✓' if data['market'] else '✗'}")
    lines.append("")
    
    lines.append("## Content Review")
    lines.append("[ ] Top story is current and relevant")
    lines.append("[ ] Top story summary is accurate")
    lines.append("[ ] The Number is verified and sourced")
    lines.append("[ ] Market insights are accurate")
    lines.append("[ ] License watch items are verified")
    lines.append("[ ] Tool of the week link works")
    lines.append("[ ] All events have correct dates/locations")
    lines.append("[ ] Quick hits are relevant and current")
    lines.append("[ ] Margin tip is actionable")
    lines.append("")
    
    lines.append("## Quality Checks")
    lines.append("[ ] No broken links")
    lines.append("[ ] No typos or grammar issues")
    lines.append("[ ] Tone is professional and helpful")
    lines.append("[ ] HTML renders correctly in email preview")
    lines.append("[ ] Mobile responsive layout verified")
    lines.append("")
    
    lines.append("## Items to Verify")
    
    # Add specific items that need verification
    top_story = select_top_story(data['news'])
    if top_story:
        lines.append(f"[ ] TOP STORY: {get_item_title(top_story)}")
        url = get_item_url(top_story)
        if url != '#':
            lines.append(f"    Link: {url}")
    
    tool = select_tool_of_week(data['tools'])
    if tool:
        lines.append(f"[ ] TOOL: {get_item_title(tool)}")
        url = get_item_url(tool)
        if url != '#':
            lines.append(f"    Link: {url}")
    
    events = select_events(data['events'])
    for event in events:
        lines.append(f"[ ] EVENT: {format_event(event)}")
    
    lines.append("")
    lines.append("## Sign-off")
    lines.append("[ ] Content approved by: _________________")
    lines.append("[ ] Ready to send: _________________")
    lines.append(f"[ ] Scheduled send date: _________________")
    
    return "\n".join(lines)


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Compose The Operator's Margin Report newsletter from scraped data."
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='./data',
        help='Directory containing scraped data files (default: ./data)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output path prefix (without extension). Default: ./drafts/newsletter_YYYY-MM-DD'
    )
    parser.add_argument(
        '--week-date',
        type=str,
        default=None,
        help='Week date for the newsletter header (default: current date)'
    )
    
    args = parser.parse_args()
    
    # Set defaults
    today = datetime.now().strftime('%Y-%m-%d')
    week_date = args.week_date or datetime.now().strftime('%B %d, %Y')
    output_prefix = args.output or f'./drafts/newsletter_{today}'
    data_dir = Path(args.data_dir)
    
    print("=" * 60)
    print("📰 The Operator's Margin Report - Newsletter Composer")
    print("=" * 60)
    
    # Create output directory if needed
    output_path = Path(output_prefix)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    data = load_all_data(data_dir)
    
    # Check if we have any data
    has_data = any(v is not None for v in data.values())
    if not has_data:
        print("\n⚠️  Warning: No data files found. Generating template newsletter.")
    
    # Generate content
    print("\n📝 Generating newsletter...")
    
    md_content = generate_markdown(data, week_date)
    html_content = markdown_to_html(md_content)
    checklist = generate_checklist(data, week_date)
    
    # Write output files
    md_path = f"{output_prefix}.md"
    html_path = f"{output_prefix}.html"
    checklist_path = f"{output_prefix}_checklist.txt"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"  ✓  Created: {md_path}")
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  ✓  Created: {html_path}")
    
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist)
    print(f"  ✓  Created: {checklist_path}")
    
    print("\n" + "=" * 60)
    print("✅ Newsletter draft complete!")
    print(f"   Review the checklist: {checklist_path}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())
