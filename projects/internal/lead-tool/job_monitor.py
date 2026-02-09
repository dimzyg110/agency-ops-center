#!/usr/bin/env python3
"""
Job Posting Monitor for Lead Tool Phase 2

Monitors job postings using Google search to detect hiring signals:
- hiring_hot: 3+ jobs in last 30 days (rapid growth or high turnover)
- hiring_warm: 1-2 jobs in last 30 days (moderate activity)
- hiring_cold: No recent postings (stable or stagnant)
- buyer_incoming: Has inventory/purchasing manager posting (SALES OPPORTUNITY!)

Uses Google/Brave search API instead of direct Indeed scraping (which blocks bots).

Usage:
    python job_monitor.py [--input signals_pack.csv] [--limit 10] [--output hiring.csv]

Output:
    - output/hiring_signals_YYYY-MM-DD.csv (enriched with job data)
"""

import argparse
import csv
import os
import re
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

# Try requests for better HTTP handling
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(os.environ.get("LEAD_TOOL_BASE_DIR", Path(__file__).resolve().parent))
# Allow env override while keeping relative defaults
DEFAULT_OUTPUT_DIR = Path(os.environ.get("LEAD_TOOL_OUTPUT_DIR", BASE_DIR / "output"))
DEFAULT_INPUT = Path(os.environ.get("LEAD_TOOL_INPUT_FILE", DEFAULT_OUTPUT_DIR / "ma_operator_signals_pack_2026-02-04.csv"))

# Rate limiting
SEARCH_DELAY_SECONDS = 1.5  # Delay between searches
REQUEST_TIMEOUT = 15

# Job titles that indicate a buyer/decision-maker is being hired
BUYER_TITLES = [
    "inventory manager",
    "purchasing manager",
    "procurement",
    "buyer",
    "inventory control",
    "inventory specialist",
    "supply chain",
    "operations manager",
    "general manager",
    "director of operations",
    "vp operations",
    "head of operations",
    "store manager",
]

# Job titles for scoring (cannabis-related jobs)
CANNABIS_JOB_TITLES = [
    "budtender",
    "dispensary",
    "cannabis",
    "marijuana",
    "cultivator",
    "grower",
    "trimmer",
    "extraction",
    "edibles",
    "packaging",
    "compliance",
    "inventory",
    "retail associate",
    "sales associate",
    "patient consultant",
    "wellness advisor",
    "manager",
    "assistant manager",
]


# =============================================================================
# SEARCH VIA SHELL (uses system's brave search tool)
# =============================================================================

def search_jobs_via_shell(company_name: str, location: str = "Massachusetts") -> Dict[str, Any]:
    """
    Use shell command to search for jobs (leverages system's web_search).
    Falls back to basic detection if unavailable.
    """
    # Clean company name
    search_name = company_name
    for suffix in [' Llc', ' LLC', ' Inc', ' Inc.', ' Corp', ' Corporation']:
        search_name = search_name.replace(suffix, '')
    search_name = search_name.strip()
    
    # Search query targeting job boards
    query = f'"{search_name}" jobs {location} site:indeed.com OR site:linkedin.com OR site:glassdoor.com'
    
    print(f"  🔍 Searching for: {search_name} jobs")
    
    try:
        # Try curl with Brave Search API if we have an API key
        # Otherwise, we'll use a simpler approach
        result = search_with_brave_api(query)
        if result:
            return result
    except Exception as e:
        print(f"    ⚠️  Search error: {e}")
    
    # Return empty result if search failed
    return {
        'jobs': [],
        'job_count': 0,
        'error': 'Search unavailable'
    }


def search_with_brave_api(query: str) -> Optional[Dict[str, Any]]:
    """Try to search using Brave Search API via environment key."""
    api_key = os.environ.get('BRAVE_API_KEY')
    
    if not api_key or not HAS_REQUESTS:
        return None
    
    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
        params = {
            "q": query,
            "count": 10
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return parse_brave_results(data)
    except Exception:
        pass
    
    return None


def parse_brave_results(data: dict) -> Dict[str, Any]:
    """Parse Brave Search API results for job listings."""
    jobs = []
    
    web_results = data.get('web', {}).get('results', [])
    
    for result in web_results:
        title = result.get('title', '')
        url = result.get('url', '')
        description = result.get('description', '')
        
        # Check if this is a job listing
        if is_job_listing(title, url, description):
            job = extract_job_info(title, url, description)
            if job:
                jobs.append(job)
    
    return {
        'jobs': jobs,
        'job_count': len(jobs),
        'error': None
    }


def is_job_listing(title: str, url: str, description: str) -> bool:
    """Check if a search result is a job listing."""
    combined = (title + ' ' + url + ' ' + description).lower()
    
    job_indicators = ['job', 'hiring', 'career', 'position', 'apply', 'employment']
    job_sites = ['indeed.com', 'linkedin.com/jobs', 'glassdoor.com', 'ziprecruiter', 'careers']
    
    has_indicator = any(ind in combined for ind in job_indicators)
    is_job_site = any(site in url.lower() for site in job_sites)
    
    return has_indicator or is_job_site


def extract_job_info(title: str, url: str, description: str) -> Optional[Dict[str, Any]]:
    """Extract job information from search result."""
    # Try to extract job title from the result
    combined = title + ' ' + description
    
    # Common job title patterns
    job_title = None
    for keyword in CANNABIS_JOB_TITLES:
        if keyword.lower() in combined.lower():
            # Try to extract the full title
            job_title = extract_title_around_keyword(combined, keyword)
            break
    
    if not job_title:
        job_title = title[:100]  # Use search result title as fallback
    
    return {
        'title': job_title,
        'url': url,
        'source': 'web_search',
        'posted': None  # Can't determine from search results
    }


def extract_title_around_keyword(text: str, keyword: str) -> str:
    """Extract a reasonable job title around a keyword."""
    text_lower = text.lower()
    pos = text_lower.find(keyword.lower())
    
    if pos == -1:
        return keyword.title()
    
    # Get surrounding context
    start = max(0, pos - 30)
    end = min(len(text), pos + len(keyword) + 30)
    
    snippet = text[start:end].strip()
    
    # Clean up
    snippet = re.sub(r'[|•\-–].*$', '', snippet)
    snippet = re.sub(r'^.*[|•\-–]', '', snippet)
    
    return snippet.strip()[:80]


# =============================================================================
# ALTERNATIVE: MOCK DATA FOR TESTING
# =============================================================================

def generate_mock_job_data(company_name: str) -> Dict[str, Any]:
    """
    Generate mock job data for testing when API access is unavailable.
    In production, this would be replaced with actual job board integration.
    """
    # Use company name hash for deterministic "random" results
    name_hash = sum(ord(c) for c in company_name.lower())
    
    # Deterministic "random" based on name
    has_jobs = (name_hash % 3) != 0  # ~67% have some jobs
    job_count = (name_hash % 5) if has_jobs else 0
    has_buyer_role = (name_hash % 7) == 0  # ~14% have buyer role
    
    jobs = []
    
    job_templates = [
        "Budtender",
        "Dispensary Associate",
        "Cannabis Retail Associate",
        "Shift Supervisor",
        "Assistant Manager",
    ]
    
    buyer_templates = [
        "Inventory Manager",
        "Purchasing Manager",
        "Operations Manager",
    ]
    
    for i in range(job_count):
        title = job_templates[(name_hash + i) % len(job_templates)]
        days_ago = (name_hash + i) % 45
        posted = datetime.now() - timedelta(days=days_ago)
        jobs.append({
            'title': title,
            'posted': posted,
            'source': 'mock'
        })
    
    if has_buyer_role:
        jobs.append({
            'title': buyer_templates[name_hash % len(buyer_templates)],
            'posted': datetime.now() - timedelta(days=(name_hash % 20)),
            'source': 'mock'
        })
    
    return {
        'jobs': jobs,
        'job_count': len(jobs),
        'error': None,
        'mock': True
    }


# =============================================================================
# SIGNAL HELPERS
# =============================================================================

def is_buyer_role(title: str) -> bool:
    """Check if a job title indicates a buyer/decision-maker role."""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in BUYER_TITLES)


def is_cannabis_job(title: str) -> bool:
    """Check if a job title is cannabis-related."""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in CANNABIS_JOB_TITLES)


# =============================================================================
# SIGNAL SCORING
# =============================================================================

def analyze_hiring_signals(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze job listings to generate hiring signals."""
    
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    recent_jobs = []
    buyer_jobs = []
    all_titles = []
    last_job_date = None
    
    for job in jobs:
        title = job.get('title', '')
        posted = job.get('posted')
        
        if title:
            all_titles.append(title)
        
        # Track most recent job date
        if posted and (last_job_date is None or posted > last_job_date):
            last_job_date = posted
        
        # Only count dated postings as recent; unknown dates stay separate
        if posted is not None and posted >= thirty_days_ago:
            recent_jobs.append(job)
        
        # Check for buyer/decision-maker roles
        if is_buyer_role(title):
            buyer_jobs.append(job)
    
    # Determine hiring signal
    recent_count = len(recent_jobs)
    if recent_count >= 3:
        hiring_signal = 'hiring_hot'
    elif recent_count >= 1:
        hiring_signal = 'hiring_warm'
    else:
        hiring_signal = 'hiring_cold'
    
    # Check for buyer incoming
    buyer_incoming = len(buyer_jobs) > 0
    
    return {
        'active_jobs': len(jobs),
        'recent_jobs': recent_count,
        'job_titles': '; '.join(all_titles[:5]),
        'hiring_signal': hiring_signal,
        'buyer_incoming': buyer_incoming,
        'buyer_titles': '; '.join([j.get('title', '') for j in buyer_jobs]),
        'last_job_date': last_job_date.strftime('%Y-%m-%d') if last_job_date else '',
    }


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_companies(input_path: Path, limit: Optional[int] = None, 
                      delay: float = SEARCH_DELAY_SECONDS,
                      use_mock: bool = False) -> List[Dict[str, Any]]:
    """Process companies from input CSV and enrich with job data."""
    
    results = []
    
    # Read input CSV
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)
    
    if limit:
        companies = companies[:limit]
    
    total = len(companies)
    print(f"\n📋 Processing {total} companies...")
    print("=" * 60)
    
    for i, company in enumerate(companies, 1):
        business_name = company.get('Business Name', company.get('business_name', ''))
        city = company.get('City', company.get('city', ''))
        
        if not business_name:
            continue
        
        print(f"\n[{i}/{total}] {business_name} ({city})")
        
        # Get job data (mock or real search)
        if use_mock:
            job_results = generate_mock_job_data(business_name)
            print("  📊 Using mock data (API unavailable)")
        else:
            job_results = search_jobs_via_shell(business_name, f"{city}, Massachusetts")
        
        # Analyze signals
        signals = analyze_hiring_signals(job_results.get('jobs', []))
        
        # Build result row (preserve original data + add new columns)
        result = dict(company)
        result.update({
            'active_jobs': signals['active_jobs'],
            'job_titles': signals['job_titles'],
            'hiring_signal': signals['hiring_signal'],
            'buyer_incoming': signals['buyer_incoming'],
            'buyer_job_titles': signals['buyer_titles'],
            'last_job_date': signals['last_job_date'],
            'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'data_source': 'mock' if job_results.get('mock') else 'search',
        })
        
        results.append(result)
        
        # Print summary
        signal_emoji = {
            'hiring_hot': '🔥',
            'hiring_warm': '🌡️',
            'hiring_cold': '❄️'
        }
        emoji = signal_emoji.get(signals['hiring_signal'], '❓')
        
        print(f"    {emoji} {signals['hiring_signal']} | Jobs: {signals['active_jobs']}")
        
        if signals['buyer_incoming']:
            print(f"    💰 BUYER INCOMING: {signals['buyer_titles']}")
        
        if signals['job_titles']:
            titles_preview = signals['job_titles'][:60] + ('...' if len(signals['job_titles']) > 60 else '')
            print(f"    📝 Titles: {titles_preview}")
        
        # Rate limiting
        if i < total:
            actual_delay = delay + random.uniform(0.2, 0.5)
            time.sleep(actual_delay)
    
    return results


def save_results(results: List[Dict[str, Any]], output_path: Path):
    """Save results to CSV."""
    
    if not results:
        print("⚠️  No results to save")
        return
    
    # Get all fieldnames from first result
    fieldnames = list(results[0].keys())
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Saved {len(results)} rows to: {output_path}")


def print_summary(results: List[Dict[str, Any]]):
    """Print summary statistics."""
    
    if not results:
        return
    
    hot = sum(1 for r in results if r.get('hiring_signal') == 'hiring_hot')
    warm = sum(1 for r in results if r.get('hiring_signal') == 'hiring_warm')
    cold = sum(1 for r in results if r.get('hiring_signal') == 'hiring_cold')
    buyers = sum(1 for r in results if r.get('buyer_incoming'))
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  🔥 Hiring Hot:     {hot}")
    print(f"  🌡️  Hiring Warm:    {warm}")
    print(f"  ❄️  Hiring Cold:    {cold}")
    print(f"  💰 Buyer Incoming: {buyers}")
    
    if buyers > 0:
        print("\n💰 BUYER INCOMING - HIGH VALUE LEADS:")
        for r in results:
            if r.get('buyer_incoming'):
                name = r.get('Business Name', r.get('business_name', 'Unknown'))
                titles = r.get('buyer_job_titles', '')
                print(f"    • {name}: {titles}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Monitor job postings for cannabis dispensaries to detect hiring signals'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=DEFAULT_INPUT,
        help='Input CSV with company data (default: signals pack)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=None,
        help='Output CSV path (default: output/hiring_signals_YYYY-MM-DD.csv)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit number of companies to process (for testing)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=SEARCH_DELAY_SECONDS,
        help='Delay between requests in seconds (default: 1.5)'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock data instead of real search (for testing)'
    )
    
    args = parser.parse_args()

    # Require explicit mock mode when Brave API key is unavailable
    if not args.mock and not os.environ.get('BRAVE_API_KEY'):
        print("❌ BRAVE_API_KEY not set. Use --mock for testing or set the environment variable.")
        return 1
    
    # Validate input file
    if not args.input.exists():
        print(f"❌ Input file not found: {args.input}")
        alt_inputs = list(DEFAULT_OUTPUT_DIR.glob("*signals*.csv"))
        if alt_inputs:
            print(f"   Available files: {[f.name for f in alt_inputs]}")
        return 1
    
    # Set output path
    if args.output:
        output_path = args.output
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_path = DEFAULT_OUTPUT_DIR / f"hiring_signals_{date_str}.csv"
    
    print("🔎 Job Posting Monitor - Lead Tool Phase 2")
    print("=" * 60)
    print(f"📂 Input:  {args.input}")
    print(f"📂 Output: {output_path}")
    if args.limit:
        print(f"⚡ Limit:  {args.limit} companies")
    print(f"⏱️  Delay:  {args.delay}s between requests")
    if args.mock:
        print("📊 Mode:   MOCK DATA (for testing)")
    
    # Process companies
    results = process_companies(args.input, args.limit, delay=args.delay, use_mock=args.mock)
    
    # Save results
    save_results(results, output_path)
    
    # Print summary
    print_summary(results)
    
    return 0


if __name__ == '__main__':
    exit(main())
