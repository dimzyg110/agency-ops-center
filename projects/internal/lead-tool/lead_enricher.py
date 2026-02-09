#!/usr/bin/env python3
"""
Lead Enricher - Lead Tool Phase 3

Master pipeline to enrich CCC/signals data:
- Google Places
- Menu Scraper
- Job Monitor
- Decision Maker Lookup
- MSO Mapper

Outputs a single enriched CSV with all columns.

Usage:
    python lead_enricher.py --input ccc_licenses.csv --output fully_enriched.csv --skip-existing
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


BASE_DIR = Path(os.environ.get("LEAD_TOOL_BASE_DIR", Path(__file__).resolve().parent))
OUTPUT_DIR = Path(os.environ.get("LEAD_TOOL_OUTPUT_DIR", BASE_DIR / "output"))

SCRIPTS = {
    "google_places": BASE_DIR / "google_places_agent.py",
    "menu_scraper": BASE_DIR / "menu_scraper.py",
    "job_monitor": BASE_DIR / "job_monitor.py",
    "decision_maker": BASE_DIR / "decision_maker_lookup.py",
    "mso_mapper": BASE_DIR / "mso_mapper.py",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS
# =============================================================================


def run_script(step_name: str, cmd: list, script_path: Path) -> None:
    """Run a pipeline step with subprocess, capturing output for logging."""
    if not script_path.exists():
        logger.error("Missing script for %s: %s", step_name, script_path)
        sys.exit(1)

    logger.info("[RUN] %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Step failed: %s", step_name)
        if result.stdout:
            logger.error("stdout:\n%s", result.stdout.strip())
        if result.stderr:
            logger.error("stderr:\n%s", result.stderr.strip())
        sys.exit(result.returncode)


def build_output_path(prefix: str) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return str(OUTPUT_DIR / f"{prefix}_{date_str}.csv")


# =============================================================================
# MAIN PIPELINE
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Run full lead enrichment pipeline")
    parser.add_argument("--input", "-i", required=True, help="Input CSV (raw CCC/signals data)")
    parser.add_argument("--output", "-o", required=True, help="Final enriched CSV output")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows processed")
    parser.add_argument("--dry-run", action="store_true", help="Use dry-run mode for all steps")
    parser.add_argument("--skip-existing", action="store_true", help="Skip steps if output already exists")

    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step outputs
    places_out = build_output_path("places_enriched")
    menu_out = build_output_path("menu_enriched")
    jobs_out = build_output_path("jobs_enriched")
    dm_out = build_output_path("decision_makers_enriched")
    mso_out = build_output_path("mso_enriched")

    # Step 1: Google Places
    if not (args.skip_existing and os.path.exists(places_out)):
        cmd = [sys.executable, str(SCRIPTS["google_places"]), "--input", args.input, "--output", places_out]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])  # pass --limit consistently
        if args.dry_run:
            cmd.append("--dry-run")
        run_script("google_places", cmd, SCRIPTS["google_places"])
    else:
        logger.info("[SKIP] Places output exists: %s", places_out)

    # Step 2: Menu Scraper
    if not (args.skip_existing and os.path.exists(menu_out)):
        cmd = [sys.executable, str(SCRIPTS["menu_scraper"]), "--input", places_out, "--output", menu_out]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        run_script("menu_scraper", cmd, SCRIPTS["menu_scraper"])
    else:
        logger.info("[SKIP] Menu output exists: %s", menu_out)

    # Step 3: Job Monitor
    if not (args.skip_existing and os.path.exists(jobs_out)):
        cmd = [sys.executable, str(SCRIPTS["job_monitor"]), "--input", menu_out, "--output", jobs_out]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        run_script("job_monitor", cmd, SCRIPTS["job_monitor"])
    else:
        logger.info("[SKIP] Job output exists: %s", jobs_out)

    # Step 4: Decision Maker Lookup
    if not (args.skip_existing and os.path.exists(dm_out)):
        cmd = [sys.executable, str(SCRIPTS["decision_maker"]), "--input", jobs_out, "--output", dm_out]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        if args.dry_run:
            cmd.append("--dry-run")
        run_script("decision_maker", cmd, SCRIPTS["decision_maker"])
    else:
        logger.info("[SKIP] Decision maker output exists: %s", dm_out)

    # Step 5: MSO Mapper
    if not (args.skip_existing and os.path.exists(mso_out)):
        cmd = [sys.executable, str(SCRIPTS["mso_mapper"]), "--input", dm_out, "--output", mso_out]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        if args.dry_run:
            cmd.append("--dry-run")
        run_script("mso_mapper", cmd, SCRIPTS["mso_mapper"])
    else:
        logger.info("[SKIP] MSO output exists: %s", mso_out)

    # Final output copy
    logger.info("[DONE] Final enriched CSV ready at %s", mso_out)
    if args.output != mso_out:
        # Copy final output
        with open(mso_out, "r", encoding="utf-8") as src, open(args.output, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        logger.info("[DONE] Copied to %s", args.output)


if __name__ == "__main__":
    main()
