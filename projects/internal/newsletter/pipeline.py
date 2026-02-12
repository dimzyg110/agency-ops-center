#!/usr/bin/env python3
"""Pipeline runner for newsletter generation."""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Optional

from data_contract import OPTIONAL_METADATA_KEYS, stage_output_filename


STAGES = [
    ("news", "scrapers/news_scraper.py", ["--days", "7"]),
    ("events", "scrapers/events_scraper.py", ["--days", "30"]),
    ("social", "scrapers/social_scraper.py", ["--limit", "20"]),
    ("tools", "scrapers/tools_scraper.py", []),
    ("ccc_ingest", "scrapers/ccc_ingest.py", []),
    ("glass", "scrapers/glass_data_processor.py", []),
    ("market", "scrapers/market_data_processor.py", []),
    ("validate", "content_validator.py", []),
    ("compose", "composer.py", []),
    ("quality", "quality_checker.py", []),
]

# Stages that gate composition/distribution.
# Validate is a gate: critical validation errors block the compose stage.
GATE_STAGES: set[str] = {"validate"}

OUTPUT_REQUIRED = {"news", "events", "social", "tools", "ccc_ingest", "glass", "market"}


@dataclass
class StageResult:
    name: str
    script: str
    args: List[str]
    start_time: str
    end_time: str
    duration_sec: float
    status: str
    returncode: Optional[int] = None
    output_path: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    records_written: Optional[int] = None
    source_breakdown: Optional[dict[str, Any]] = None
    retry_count: Optional[int] = None
    rate_limited_count: Optional[int] = None
    circuit_open_count: Optional[int] = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run newsletter generation pipeline")
    parser.add_argument(
        "--stage",
        action="append",
        default=[],
        help="Run only a specific stage (can be repeated)",
    )
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        help="Skip a specific stage (can be repeated)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would run")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument(
        "--publish-beehiiv",
        action="store_true",
        help="After composing, create a draft post on Beehiiv for review",
    )
    return parser.parse_args()


def stage_output_path(stage_name: str, data_dir: Path) -> Path:
    return data_dir / stage_output_filename(stage_name)


def send_block_reasons(results: List["StageResult"]) -> List[str]:
    """Build reasons that distribution must remain blocked."""
    reasons: List[str] = []
    status_by_stage = {r.name: r.status for r in results}

    for stage in ("validate", "quality"):
        if stage not in status_by_stage:
            reasons.append(f"required stage '{stage}' did not run")
            continue
        if status_by_stage[stage] != "success":
            reasons.append(f"required stage '{stage}' status is '{status_by_stage[stage]}'")

    for r in results:
        if r.status == "failed":
            reasons.append(f"stage '{r.name}' failed")

    # Keep stable, compact output.
    deduped = []
    seen = set()
    for reason in reasons:
        if reason in seen:
            continue
        seen.add(reason)
        deduped.append(reason)
    return deduped


def run_command(
    cmd: List[str],
    cwd: Path,
    verbose: bool,
) -> subprocess.CompletedProcess:
    if verbose:
        logging.info("Running: %s", " ".join(cmd))
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def run_stage(
    name: str,
    script: str,
    args: List[str],
    base_dir: Path,
    data_dir: Path,
    dry_run: bool,
    verbose: bool,
) -> StageResult:
    start_dt = utc_now()
    output_path: Optional[Path] = None
    stage_args = list(args)

    if name in OUTPUT_REQUIRED:
        output_path = stage_output_path(name, data_dir)
        stage_args = stage_args + ["--output", str(output_path)]

    # content_validator needs --data-dir and --output
    if name == "validate":
        output_path = stage_output_path("validate", data_dir)
        stage_args = stage_args + [
            "--data-dir", str(data_dir),
            "--output", str(output_path),
        ]

    # composer needs --data-dir and --output
    if name == "compose":
        today = utc_now().date().isoformat()
        drafts_dir = base_dir / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)
        compose_prefix = str(drafts_dir / f"newsletter_{today}")
        stage_args = stage_args + [
            "--data-dir", str(data_dir),
            "--output", compose_prefix,
        ]

    # quality_checker needs --draft, --output, and --data-dir
    if name == "quality":
        today = utc_now().date().isoformat()
        draft_path = base_dir / "drafts" / f"newsletter_{today}.md"
        output_path = stage_output_path("quality", data_dir)
        stage_args = stage_args + [
            "--draft", str(draft_path),
            "--output", str(output_path),
            "--data-dir", str(data_dir),
        ]

    script_path = base_dir / script
    if not script_path.exists():
        end_dt = utc_now()
        return StageResult(
            name=name,
            script=script,
            args=stage_args,
            start_time=isoformat(start_dt),
            end_time=isoformat(end_dt),
            duration_sec=(end_dt - start_dt).total_seconds(),
            status="failed",
            returncode=None,
            output_path=str(output_path) if output_path else None,
            error=f"Script not found: {script_path}",
        )

    cmd = [sys.executable, str(script_path)] + stage_args

    if dry_run:
        end_dt = utc_now()
        return StageResult(
            name=name,
            script=script,
            args=stage_args,
            start_time=isoformat(start_dt),
            end_time=isoformat(end_dt),
            duration_sec=(end_dt - start_dt).total_seconds(),
            status="dry_run",
            output_path=str(output_path) if output_path else None,
        )

    result = run_command(cmd, base_dir, verbose)
    end_dt = utc_now()

    status = "success" if result.returncode == 0 else "failed"
    stage_result = StageResult(
        name=name,
        script=script,
        args=stage_args,
        start_time=isoformat(start_dt),
        end_time=isoformat(end_dt),
        duration_sec=(end_dt - start_dt).total_seconds(),
        status=status,
        returncode=result.returncode,
        output_path=str(output_path) if output_path else None,
        stdout=result.stdout.strip() if result.stdout else None,
        stderr=result.stderr.strip() if result.stderr else None,
    )
    if output_path and output_path.exists():
        _apply_stage_metadata(stage_result, output_path)
    return stage_result


def _apply_stage_metadata(result: StageResult, output_path: Path) -> None:
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except Exception:
        return

    result.records_written = _infer_record_count(payload)
    coverage = payload.get("coverage", {}) if isinstance(payload, dict) else {}
    relevance = payload.get("relevance", {}) if isinstance(payload, dict) else {}
    if isinstance(coverage, dict):
        result.source_breakdown = {
            "geo_scope_counts": coverage.get("geo_scope_counts"),
            "domain_counts": coverage.get("domain_counts"),
            "dataset_count": coverage.get("dataset_count"),
        }

    source_health = payload.get("source_health", []) if isinstance(payload, dict) else []
    retries = 0
    rate_limited = 0
    circuit_open = 0
    if isinstance(source_health, list):
        for row in source_health:
            if not isinstance(row, dict):
                continue
            retries += int(row.get("retry_count", 0) or 0)
            rate_limited += int(row.get("rate_limited_count", 0) or 0)
            circuit_open += int(row.get("circuit_open_count", 0) or 0)
    result.retry_count = retries
    result.rate_limited_count = rate_limited
    result.circuit_open_count = circuit_open

    for key in OPTIONAL_METADATA_KEYS:
        if key in payload:
            continue
        # Metadata keys remain optional and additive; no-op when absent.
        _ = relevance


def _infer_record_count(payload: Any) -> Optional[int]:
    if not isinstance(payload, dict):
        return None
    for key in ("articles", "events", "posts", "tools", "market_pulse", "source_health"):
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)
    insights = payload.get("insights")
    if isinstance(insights, dict):
        total = insights.get("total_operators")
        if isinstance(total, int):
            return total
    coverage = payload.get("coverage")
    if isinstance(coverage, dict):
        count = coverage.get("dataset_count")
        if isinstance(count, int):
            return count
    return None


def summarize(results: Iterable[StageResult]) -> dict:
    results_list = list(results)
    total = len(results_list)
    success = sum(1 for r in results_list if r.status == "success")
    failed = sum(1 for r in results_list if r.status == "failed")
    skipped = sum(1 for r in results_list if r.status in {"skipped", "dry_run"})
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "skipped_or_dry_run": skipped,
    }


def main() -> int:
    args = parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s",
    )

    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    stage_map = {name: (script, stage_args) for name, script, stage_args in STAGES}

    requested = args.stage or [name for name, _, _ in STAGES]
    skipped = set(args.skip)

    unknown = [name for name in requested if name not in stage_map]
    if unknown:
        logging.error("Unknown stage(s): %s", ", ".join(unknown))
        return 1

    results: List[StageResult] = []
    for name in [n for n, _, _ in STAGES if n in requested]:
        if name in skipped:
            now = utc_now()
            results.append(
                StageResult(
                    name=name,
                    script=stage_map[name][0],
                    args=stage_map[name][1],
                    start_time=isoformat(now),
                    end_time=isoformat(now),
                    duration_sec=0.0,
                    status="skipped",
                )
            )
            continue

        script, stage_args = stage_map[name]
        result = run_stage(
            name=name,
            script=script,
            args=stage_args,
            base_dir=base_dir,
            data_dir=data_dir,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
        results.append(result)

        # Quality gate enforcement: if a gate stage fails, stop the pipeline.
        # This prevents producing a draft when critical validation errors exist.
        if name in GATE_STAGES and result.status == "failed":
            logging.error(
                "🚫 QUALITY GATE BLOCKED: Stage '%s' failed — stopping pipeline.",
                name,
            )
            logging.error(
                "The pipeline will NOT produce a draft until these issues are resolved."
            )
            if result.stdout:
                # Try to extract and display the most important issues
                try:
                    report = json.loads(result.stdout)
                    issues = report.get("issues", [])
                    errors = [i for i in issues if i.get("severity") == "error"]
                    warnings = [i for i in issues if i.get("severity") == "warning"]
                    logging.error(
                        "  Validation found %d error(s) and %d warning(s).",
                        len(errors), len(warnings),
                    )
                    for issue in errors[:10]:
                        logging.error("  ❌ %s", issue.get("message", str(issue)))
                    if len(errors) > 10:
                        logging.error("  ... and %d more errors.", len(errors) - 10)
                except (json.JSONDecodeError, TypeError):
                    logging.error("Validation output:\n%s", result.stdout[:2000])
            break

    run_report = {
        "run_at": isoformat(utc_now()),
        "stages": [r.__dict__ for r in results],
        "summary": summarize(results),
    }

    blocked_reasons = send_block_reasons(results)
    run_report["send_allowed"] = len(blocked_reasons) == 0 and not args.dry_run
    run_report["send_blocked_reasons"] = blocked_reasons

    quality_result = next((r for r in results if r.name == "quality"), None)
    if quality_result:
        run_report["quality_results"] = {
            "status": quality_result.status,
            "returncode": quality_result.returncode,
            "stdout": quality_result.stdout,
            "stderr": quality_result.stderr,
        }

    output_path = data_dir / f"pipeline_run_{utc_now().date().isoformat()}.json"
    output_path.write_text(json.dumps(run_report, ensure_ascii=False, indent=2))

    print(json.dumps(run_report["summary"], ensure_ascii=False, indent=2))
    print(f"Pipeline report written to {output_path}")

    # ------------------------------------------------------------------
    # Optional Beehiiv publishing
    # ------------------------------------------------------------------
    if args.publish_beehiiv and not args.dry_run:
        _publish_to_beehiiv(base_dir, results)

    if any(r.status == "failed" for r in results):
        return 1
    return 0


def _publish_to_beehiiv(base_dir: Path, results: List[StageResult]) -> None:
    """Create a draft post on Beehiiv from the latest composed newsletter."""
    import os

    api_key = os.environ.get("BEEHIIV_API_KEY", "")
    pub_id = os.environ.get("BEEHIIV_PUBLICATION_ID", "")

    if not api_key or not pub_id:
        logging.error(
            "🔴 BEEHIIV: Set BEEHIIV_API_KEY and BEEHIIV_PUBLICATION_ID env vars to publish."
        )
        return

    # Find the latest HTML draft
    today = utc_now().date().isoformat()
    html_path = base_dir / "drafts" / f"newsletter_{today}.html"
    if not html_path.exists():
        logging.error("🔴 BEEHIIV: No HTML draft found at %s", html_path)
        return

    try:
        from beehiiv_client import BeehiivClient, BeehiivError
    except ImportError:
        logging.error("🔴 BEEHIIV: Could not import beehiiv_client module.")
        return

    html_content = html_path.read_text(encoding="utf-8")
    title = f"The Operator's Margin Report — Week of {utc_now().strftime('%B %d, %Y')}"

    client = BeehiivClient(api_key, pub_id)
    try:
        post = client.create_post(
            title=title,
            content_html=html_content,
            subtitle="Survival intel for Massachusetts cannabis operators.",
            status="draft",
        )
        print(f"✅ BEEHIIV: Draft created — review at https://app.beehiiv.com/dashboard")
        logging.info("Beehiiv draft post ID: %s", post.get("id"))
    except BeehiivError as e:
        if e.code == "SEND_API_DISABLED":
            print(
                "⚠️  BEEHIIV: Post creation requires Scale plan. "
                "Copy the HTML from the drafts/ folder into Beehiiv manually.\n"
                f"   Draft: {html_path}"
            )
        else:
            logging.error("🔴 BEEHIIV publish failed: %s", e)


if __name__ == "__main__":
    raise SystemExit(main())
