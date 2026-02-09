#!/usr/bin/env python3
"""
Menu Scraper - Lead Tool Phase 2

Scrapes dispensary menus to identify SKU counts and menu gaps.
This is the killer feature of the Intel Pack: Menu Gap Analysis.

Features:
- Detect menu platform (Dutchie, Jane, Weedmaps, etc.)
- Count SKUs per category
- Identify menu gaps (low beverage, low edible, no topicals, etc.)
- Output enriched CSV with menu intelligence

Usage:
    python3 menu_scraper.py [--input signals_pack.csv] [--limit 10] [--output menu.csv]
    python3 menu_scraper.py --detect-only --input stores.csv --limit 5

Output:
    - output/menu_analysis_YYYY-MM-DD.csv
"""

import argparse
import csv
import json
import os
import re
import time
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser


# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(os.environ.get("LEAD_TOOL_BASE_DIR", Path(__file__).resolve().parent))
# Allow env override while keeping relative defaults
DEFAULT_OUTPUT_DIR = Path(os.environ.get("LEAD_TOOL_OUTPUT_DIR", BASE_DIR / "output"))
DEFAULT_INPUT = Path(os.environ.get("LEAD_TOOL_INPUT_DIR", DEFAULT_OUTPUT_DIR))

# Rate limiting: requests per second
RATE_LIMIT = 2.0  # 2 requests/second = 500ms between requests
REQUEST_TIMEOUT = 15  # seconds

# SSL verification is enabled by default; can be disabled via CLI flag
SSL_VERIFY = True

# User agent to avoid blocks
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Menu platform detection patterns
PLATFORM_PATTERNS = {
    'dutchie': [
        r'dutchie\.com',
        r'dutchie-plus',
        r'iframe.*dutchie',
        r'embed\.dutchie\.com',
        r'"dutchie"',
        r'dutchie\.iframe',
        r'dutchiePlus',
        r'api\.dutchie\.com',
    ],
    'jane': [
        r'iheartjane\.com',
        r'iheartjane',
        r'jane-embed',
        r'jane\.menu',
        r'janetechnologies',
        r'api\.iheartjane\.com',
    ],
    'weedmaps': [
        r'weedmaps\.com',
        r'weedmaps-embed',
        r'wm\.com',
        r'api\.weedmaps\.com',
    ],
    'leafly': [
        r'leafly\.com',
        r'leafly-embed',
    ],
}

# Category normalization - map various names to standard categories
CATEGORY_ALIASES = {
    'flower': ['flower', 'flowers', 'bud', 'buds', 'cannabis flower', 'dried flower'],
    'vape': ['vape', 'vapes', 'vaporizer', 'vaporizers', 'cartridge', 'cartridges', 'cart', 'carts', 'pod', 'pods'],
    'edible': ['edible', 'edibles', 'food', 'gummy', 'gummies', 'chocolate', 'candy', 'baked goods'],
    'beverage': ['beverage', 'beverages', 'drink', 'drinks', 'liquid', 'soda', 'tea', 'coffee', 'seltzer'],
    'concentrate': ['concentrate', 'concentrates', 'extract', 'extracts', 'wax', 'shatter', 'rosin', 'resin', 'dab', 'dabs', 'badder', 'sauce'],
    'topical': ['topical', 'topicals', 'cream', 'creams', 'lotion', 'lotions', 'balm', 'balms', 'salve', 'patch', 'patches'],
    'preroll': ['preroll', 'prerolls', 'pre-roll', 'pre-rolls', 'joint', 'joints', 'blunt', 'blunts', 'infused preroll'],
    'tincture': ['tincture', 'tinctures', 'sublingual', 'oil', 'oils', 'drops', 'spray', 'sprays'],
    'accessory': ['accessory', 'accessories', 'gear', 'merch', 'merchandise', 'apparel', 'pipe', 'pipes', 'grinder'],
}

# Gap thresholds - flag stores with fewer than these counts
GAP_THRESHOLDS = {
    'low_beverage': ('beverage', 3),
    'low_edible': ('edible', 5),
    'no_topicals': ('topical', 1),
    'no_tinctures': ('tincture', 1),
    'low_vape': ('vape', 5),
    'low_concentrate': ('concentrate', 3),
    'low_preroll': ('preroll', 5),
    'limited_flower': ('flower', 10),
}


# =============================================================================
# SIMPLE HTML PARSER (no external dependencies)
# =============================================================================

class LinkExtractor(HTMLParser):
    """Extract links, iframes, and scripts from HTML."""
    
    def __init__(self):
        super().__init__()
        self.links = []
        self.iframes = []
        self.scripts = []
        self.script_content = []
        self._in_script = False
        self._current_script = ""
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])
        elif tag == 'iframe':
            self.iframes.append(attrs_dict.get('src', ''))
        elif tag == 'script':
            self._in_script = True
            self._current_script = ""
            if 'src' in attrs_dict:
                self.scripts.append(attrs_dict['src'])
    
    def handle_data(self, data):
        if self._in_script:
            self._current_script += data
    
    def handle_endtag(self, tag):
        if tag == 'script' and self._in_script:
            self._in_script = False
            if self._current_script.strip():
                self.script_content.append(self._current_script)


# =============================================================================
# HTTP UTILITIES
# =============================================================================

def get_ssl_context(verify_ssl: bool) -> ssl.SSLContext:
    """Build an SSL context; opt-out only when explicitly requested."""
    if verify_ssl:
        return ssl.create_default_context()
    # Explicit opt-out for sites with invalid certs
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def make_request(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    """Make an HTTP request and return the response body."""
    try:
        ctx = get_ssl_context(SSL_VERIFY)
        
        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            # Handle different encodings
            content_type = response.headers.get('Content-Type', '')
            encoding = 'utf-8'
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1].split(';')[0].strip()
            
            data = response.read()
            try:
                return data.decode(encoding)
            except:
                return data.decode('utf-8', errors='ignore')
                
    except urllib.error.HTTPError as e:
        print(f"      HTTP {e.code}: {url}")
        return None
    except urllib.error.URLError as e:
        print(f"      URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"      Request failed: {type(e).__name__}: {e}")
        return None


def make_api_request(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[Dict]:
    """Make an API request and return JSON."""
    try:
        ctx = get_ssl_context(SSL_VERIFY)
        
        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
        })
        
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
            
    except Exception as e:
        return None


# =============================================================================
# PLATFORM DETECTION
# =============================================================================

def detect_platform(html: str, url: str) -> Tuple[str, Optional[str]]:
    """
    Detect the menu platform from page HTML.
    Returns (platform, embed_url) tuple.
    """
    html_lower = html.lower()
    
    # Parse the HTML
    parser = LinkExtractor()
    try:
        parser.feed(html)
    except:
        pass  # HTML parsing errors are common, continue anyway
    
    # Combine all sources to search
    all_content = html_lower
    for script in parser.script_content:
        all_content += " " + script.lower()
    
    # Check each platform's patterns
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                # Try to extract embed URL
                embed_url = extract_embed_url(html, platform, parser)
                return platform, embed_url
    
    return 'unknown', None


def extract_embed_url(html: str, platform: str, parser: LinkExtractor) -> Optional[str]:
    """Extract the embedded menu URL for the detected platform."""
    
    if platform == 'dutchie':
        # Look for Dutchie iframe or embed URL
        for iframe in parser.iframes:
            if 'dutchie.com' in iframe:
                return iframe
        # Look for Dutchie store ID in scripts
        match = re.search(r'dutchie.*?["\']([a-zA-Z0-9-]+)["\']', html)
        if match:
            store_id = match.group(1)
            if len(store_id) > 5:  # Reasonable ID length
                return f"https://dutchie.com/embedded-menu/{store_id}"
    
    elif platform == 'jane':
        # Look for Jane iframe
        for iframe in parser.iframes:
            if 'iheartjane.com' in iframe:
                return iframe
        # Look for Jane store ID
        match = re.search(r'iheartjane\.com/stores/(\d+)', html)
        if match:
            return f"https://www.iheartjane.com/stores/{match.group(1)}"
    
    elif platform == 'weedmaps':
        # Look for Weedmaps dispensary link
        match = re.search(r'weedmaps\.com/dispensaries/([a-zA-Z0-9-]+)', html)
        if match:
            return f"https://weedmaps.com/dispensaries/{match.group(1)}"
    
    return None


def extract_dutchie_store_id(html: str) -> Optional[str]:
    """Extract Dutchie store ID from page."""
    patterns = [
        r'dutchie\.com/embedded-menu/([a-zA-Z0-9-]+)',
        r'dutchie\.com/stores/([a-zA-Z0-9-]+)',
        r'"storeId"\s*:\s*"([a-zA-Z0-9-]+)"',
        r'"retailerId"\s*:\s*"([a-zA-Z0-9-]+)"',
        r'data-store-id=["\']([a-zA-Z0-9-]+)["\']',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def extract_jane_store_id(html: str) -> Optional[str]:
    """Extract Jane store ID from page."""
    patterns = [
        r'iheartjane\.com/stores/(\d+)',
        r'iheartjane\.com/embed/stores/(\d+)',
        r'"storeId"\s*:\s*(\d+)',
        r'data-store-id=["\'](\d+)["\']',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


# =============================================================================
# MENU SCRAPING
# =============================================================================

def normalize_category(category: str) -> str:
    """Normalize a category name to our standard categories."""
    category_lower = category.lower().strip()
    
    for standard, aliases in CATEGORY_ALIASES.items():
        if category_lower in aliases:
            return standard
        # Partial match for compound categories
        for alias in aliases:
            if alias in category_lower or category_lower in alias:
                return standard
    
    return 'other'


def scrape_dutchie_menu(store_id: str) -> Optional[Dict[str, int]]:
    """
    Scrape menu from Dutchie API.
    Returns dict of category -> count.
    """
    # Dutchie uses GraphQL but has a public products endpoint
    # Try the embedded menu API first
    api_url = f"https://dutchie.com/graphql"
    
    # GraphQL query for products
    query = {
        "operationName": "FilteredProducts",
        "variables": {
            "retailerId": store_id,
            "limit": 1000,
        },
        "query": """
            query FilteredProducts($retailerId: ID!, $limit: Int) {
                menu(retailerId: $retailerId) {
                    products(limit: $limit) {
                        id
                        category
                    }
                }
            }
        """
    }
    
    try:
        ctx = get_ssl_context(SSL_VERIFY)
        
        req = urllib.request.Request(
            api_url,
            data=json.dumps(query).encode('utf-8'),
            headers={
                'User-Agent': USER_AGENT,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        )
        
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'data' in data and 'menu' in data['data']:
                products = data['data']['menu'].get('products', [])
                return count_by_category(products)
    except Exception as e:
        print(f"      Dutchie API failed: {e}")
    
    # Fallback: try scraping the embed page
    embed_url = f"https://dutchie.com/embedded-menu/{store_id}"
    html = make_request(embed_url)
    if html:
        return estimate_counts_from_html(html)
    
    return None


def scrape_jane_menu(store_id: str) -> Optional[Dict[str, int]]:
    """
    Scrape menu from Jane API.
    Returns dict of category -> count.
    """
    # Jane has a public products API
    api_url = f"https://api.iheartjane.com/v1/stores/{store_id}/products"
    
    try:
        data = make_api_request(api_url)
        if data and 'products' in data:
            return count_by_category(data['products'])
    except Exception as e:
        print(f"      Jane API failed: {e}")
    
    # Fallback: try the store page
    store_url = f"https://www.iheartjane.com/stores/{store_id}"
    html = make_request(store_url)
    if html:
        return estimate_counts_from_html(html)
    
    return None


def scrape_weedmaps_menu(slug: str) -> Optional[Dict[str, int]]:
    """
    Scrape menu from Weedmaps.
    Returns dict of category -> count.
    """
    # Weedmaps has a products API
    api_url = f"https://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{slug}/menu_items"
    
    try:
        data = make_api_request(api_url)
        if data and 'data' in data:
            items = data.get('data', {}).get('menu_items', [])
            return count_by_category(items)
    except Exception as e:
        print(f"      Weedmaps API failed: {e}")
    
    return None


def count_by_category(products: List[Dict]) -> Dict[str, int]:
    """Count products by normalized category."""
    counts = {
        'flower': 0,
        'vape': 0,
        'edible': 0,
        'beverage': 0,
        'concentrate': 0,
        'topical': 0,
        'preroll': 0,
        'tincture': 0,
        'accessory': 0,
        'other': 0,
    }
    
    for product in products:
        # Try various category field names
        category = product.get('category') or product.get('kind') or product.get('type') or product.get('category_name') or 'other'
        
        if isinstance(category, dict):
            category = category.get('name', 'other')
        
        normalized = normalize_category(str(category))
        counts[normalized] = counts.get(normalized, 0) + 1
    
    return counts


def estimate_counts_from_html(html: str) -> Optional[Dict[str, int]]:
    """
    Estimate category counts from HTML (fallback when API fails).
    Looks for category sections and product counts.
    """
    counts = {
        'flower': 0,
        'vape': 0,
        'edible': 0,
        'beverage': 0,
        'concentrate': 0,
        'topical': 0,
        'preroll': 0,
        'tincture': 0,
        'accessory': 0,
        'other': 0,
    }
    
    # Look for patterns like "Flower (45)" or "45 products"
    for category, aliases in CATEGORY_ALIASES.items():
        for alias in aliases:
            # Pattern: "Category (N)" or "Category: N products"
            patterns = [
                rf'{alias}\s*\((\d+)\)',
                rf'{alias}\s*:\s*(\d+)',
                rf'(\d+)\s*{alias}',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    try:
                        count = int(match)
                        if count < 10000:  # Sanity check
                            counts[category] = max(counts[category], count)
                    except:
                        pass
    
    # If we found any counts, return them
    if sum(counts.values()) > 0:
        return counts
    
    return None


def scrape_menu(platform: str, embed_url: Optional[str], html: str) -> Optional[Dict[str, int]]:
    """
    Scrape menu data based on detected platform.
    Returns dict of category -> count.
    """
    if platform == 'dutchie':
        store_id = extract_dutchie_store_id(html) or (embed_url and extract_dutchie_store_id(embed_url))
        if store_id:
            return scrape_dutchie_menu(store_id)
    
    elif platform == 'jane':
        store_id = extract_jane_store_id(html) or (embed_url and extract_jane_store_id(embed_url))
        if store_id:
            return scrape_jane_menu(store_id)
    
    elif platform == 'weedmaps':
        # Extract slug from URL
        if embed_url:
            match = re.search(r'/dispensaries/([a-zA-Z0-9-]+)', embed_url)
            if match:
                return scrape_weedmaps_menu(match.group(1))
    
    # Fallback: try to estimate from HTML
    return estimate_counts_from_html(html)


# =============================================================================
# GAP ANALYSIS
# =============================================================================

def identify_gaps(counts: Dict[str, int]) -> List[str]:
    """Identify menu gaps based on category counts."""
    gaps = []
    
    for gap_name, (category, threshold) in GAP_THRESHOLDS.items():
        count = counts.get(category, 0)
        if count < threshold:
            gaps.append(gap_name)
    
    # Additional gap detection
    total = sum(counts.values())
    
    if total == 0:
        gaps.append('empty_menu')
    elif total < 20:
        gaps.append('limited_menu')
    
    # Check for category imbalance
    flower_pct = counts.get('flower', 0) / max(total, 1) * 100
    if flower_pct > 70:
        gaps.append('flower_heavy')
    
    return gaps


# =============================================================================
# CSV PROCESSING
# =============================================================================

def find_latest_signals_pack() -> Optional[Path]:
    """Find the most recent signals pack CSV."""
    output_dir = DEFAULT_OUTPUT_DIR
    
    # Look for signals pack files
    pattern = "ma_operator_signals_pack_*.csv"
    files = list(output_dir.glob(pattern))
    
    if not files:
        # Try alternate names
        for alt_pattern in ["signals_pack*.csv", "*signals*.csv"]:
            files = list(output_dir.glob(alt_pattern))
            if files:
                break
    
    if files:
        # Return most recent by modification time
        return max(files, key=lambda p: p.stat().st_mtime)
    
    return None


def load_input_csv(input_path: Path) -> List[Dict[str, str]]:
    """Load input CSV and return list of rows."""
    rows = []
    
    with open(input_path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    
    return rows


def get_website_from_row(row: Dict[str, str]) -> Optional[str]:
    """Extract website URL from a row."""
    # Try various column names
    url_columns = ['website', 'url', 'Website', 'URL', 'web', 'site', 'dispensary_url', 'store_url']
    
    for col in url_columns:
        if col in row and row[col]:
            url = row[col].strip()
            if url:
                # Ensure it has a scheme
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
    
    return None


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_dispensary(row: Dict[str, str], detect_only: bool = False) -> Dict[str, Any]:
    """
    Process a single dispensary row.
    Returns enriched data with menu analysis.
    """
    result = dict(row)  # Copy original data
    
    # Initialize menu columns
    result['menu_platform'] = 'unknown'
    result['menu_embed_url'] = ''
    result['total_skus'] = 0
    result['flower_count'] = 0
    result['vape_count'] = 0
    result['edible_count'] = 0
    result['beverage_count'] = 0
    result['concentrate_count'] = 0
    result['topical_count'] = 0
    result['preroll_count'] = 0
    result['tincture_count'] = 0
    result['menu_gaps'] = ''
    result['last_scraped'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    result['scrape_status'] = 'pending'
    
    # Get website
    website = get_website_from_row(row)
    if not website:
        result['scrape_status'] = 'no_website'
        return result
    
    # Fetch homepage
    print(f"   📡 Fetching {website}...")
    html = make_request(website)
    
    if not html:
        result['scrape_status'] = 'fetch_failed'
        return result
    
    # Detect platform
    platform, embed_url = detect_platform(html, website)
    result['menu_platform'] = platform
    result['menu_embed_url'] = embed_url or ''
    
    print(f"      Platform: {platform}" + (f" → {embed_url}" if embed_url else ""))
    
    if detect_only:
        result['scrape_status'] = 'detected'
        return result
    
    # Scrape menu if platform is known
    if platform != 'unknown':
        print(f"   🔍 Scraping menu...")
        time.sleep(1.0 / RATE_LIMIT)  # Rate limit
        
        counts = scrape_menu(platform, embed_url, html)
        
        if counts:
            result['total_skus'] = sum(counts.values())
            result['flower_count'] = counts.get('flower', 0)
            result['vape_count'] = counts.get('vape', 0)
            result['edible_count'] = counts.get('edible', 0)
            result['beverage_count'] = counts.get('beverage', 0)
            result['concentrate_count'] = counts.get('concentrate', 0)
            result['topical_count'] = counts.get('topical', 0)
            result['preroll_count'] = counts.get('preroll', 0)
            result['tincture_count'] = counts.get('tincture', 0)
            
            gaps = identify_gaps(counts)
            result['menu_gaps'] = ','.join(gaps)
            result['scrape_status'] = 'success'
            
            print(f"      Total SKUs: {result['total_skus']}")
            if gaps:
                print(f"      Gaps: {', '.join(gaps)}")
        else:
            result['scrape_status'] = 'scrape_failed'
            print(f"      Could not extract menu data")
    else:
        result['scrape_status'] = 'unknown_platform'
    
    return result


def run_scraper(
    input_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    limit: Optional[int] = None,
    detect_only: bool = False,
) -> Path:
    """
    Main scraper function.
    Returns path to output file.
    """
    # Find input file
    if input_path is None:
        input_path = find_latest_signals_pack()
        if input_path is None:
            raise FileNotFoundError("No input file specified and no signals pack found")
    
    print(f"📂 Loading: {input_path}")
    rows = load_input_csv(input_path)
    print(f"   Loaded {len(rows)} records")
    
    # Apply limit
    if limit:
        rows = rows[:limit]
        print(f"   Limited to {limit} records")
    
    # Process each row
    results = []
    for i, row in enumerate(rows, 1):
        name = row.get('dba_name') or row.get('name') or row.get('business_name') or f'Row {i}'
        print(f"\n[{i}/{len(rows)}] {name}")
        
        result = process_dispensary(row, detect_only=detect_only)
        results.append(result)
        
        # Rate limit between requests
        if i < len(rows):
            time.sleep(1.0 / RATE_LIMIT)
    
    # Determine output path
    if output_path is None:
        today = datetime.now().strftime('%Y-%m-%d')
        output_path = DEFAULT_OUTPUT_DIR / f"menu_analysis_{today}.csv"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output CSV
    if results:
        # Gather all fieldnames (preserving order, adding new columns at end)
        original_fields = list(rows[0].keys()) if rows else []
        new_fields = [
            'menu_platform', 'menu_embed_url', 'total_skus',
            'flower_count', 'vape_count', 'edible_count', 'beverage_count',
            'concentrate_count', 'topical_count', 'preroll_count', 'tincture_count',
            'menu_gaps', 'last_scraped', 'scrape_status'
        ]
        fieldnames = original_fields + [f for f in new_fields if f not in original_fields]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n✅ Output: {output_path}")
    
    # Summary stats
    platforms = {}
    gaps_found = 0
    for r in results:
        p = r.get('menu_platform', 'unknown')
        platforms[p] = platforms.get(p, 0) + 1
        if r.get('menu_gaps'):
            gaps_found += 1
    
    print("\n📊 Summary:")
    for p, count in sorted(platforms.items(), key=lambda x: -x[1]):
        print(f"   {p}: {count}")
    print(f"   Stores with gaps: {gaps_found}")
    
    return output_path


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Menu Scraper - Analyze dispensary menus for SKU counts and gaps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Detect platforms only (fast)
    python menu_scraper.py --detect-only --limit 5
    
    # Full scrape with limit
    python menu_scraper.py --input stores.csv --limit 10
    
    # Full scrape, custom output
    python menu_scraper.py --input stores.csv --output my_analysis.csv
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=Path,
        help='Input CSV file with dispensary data (default: latest signals pack)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output CSV file (default: output/menu_analysis_YYYY-MM-DD.csv)'
    )
    
    parser.add_argument(
        '--limit', '-n',
        type=int,
        help='Limit number of records to process (for testing)'
    )
    
    parser.add_argument(
        '--detect-only', '-d',
        action='store_true',
        help='Only detect platforms, skip full menu scrape'
    )

    parser.add_argument(
        '--no-ssl-verify',
        action='store_true',
        help='Disable SSL certificate verification (use only if needed)'
    )
    
    args = parser.parse_args()

    # Apply explicit SSL verification override
    global SSL_VERIFY
    SSL_VERIFY = not args.no_ssl_verify
    
    print("=" * 60)
    print("🍃 Menu Scraper - Lead Tool Phase 2")
    print("=" * 60)
    
    try:
        output_path = run_scraper(
            input_path=args.input,
            output_path=args.output,
            limit=args.limit,
            detect_only=args.detect_only,
        )
        print(f"\n✨ Done! Results saved to {output_path}")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("   Specify an input file with --input <file.csv>")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
