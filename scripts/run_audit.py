#!/usr/bin/env python3
"""Run the first end-to-end GEO audit flow."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def write_failure_report(report_path: Path, url: str, failure_note: str) -> None:
    report = f"""# GEO Audit Report

- **Target:** {url}
- **Audit date:** {datetime.now(UTC).date().isoformat()}
- **Status:** fetch-limited / incomplete

## Executive Summary

- The audit could not complete a normal lightweight fetch for this target.
- This does **not** automatically mean the site is poor.
- It means the current lightweight, non-browser fetch path was blocked or could not retrieve usable source HTML.

## Failure Note

- {failure_note}

## What This Usually Means

- The site may block generic fetch clients.
- The site may rely heavily on rendering or client-side hydration.
- The site may require a richer acquisition layer than this lightweight v1 tool intentionally uses.

## Recommended Next Step

- Treat this as a **fetch limitation**, not a content verdict.
- If this target matters, review it manually or use a future optional enhanced-fetch mode rather than forcing fake certainty from the lightweight path.
"""
    report_path.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the first end-to-end GEO audit flow")
    parser.add_argument("url")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_dir = (root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    site_fetch = output_dir / "site-fetch.json"
    crawler = output_dir / "crawler-audit.json"
    llmstxt = output_dir / "llmstxt-audit.json"
    citability = output_dir / "citability-audit.json"
    schema = output_dir / "schema-audit.json"
    report = output_dir / "report.md"
    llms_draft = output_dir / "draft-llms.txt"

    commands = [
        [sys.executable, str(root / "scripts" / "fetch_site.py"), args.url, "--output", str(site_fetch)],
        [sys.executable, str(root / "scripts" / "audit_crawlers.py"), args.url, "--output", str(crawler)],
        [sys.executable, str(root / "scripts" / "audit_llmstxt.py"), args.url, "--output", str(llmstxt), "--draft-output", str(llms_draft)],
        [sys.executable, str(root / "scripts" / "audit_citability.py"), "--site-fetch", str(site_fetch), "--output", str(citability)],
        [sys.executable, str(root / "scripts" / "audit_schema.py"), "--site-fetch", str(site_fetch), "--output", str(schema)],
        [sys.executable, str(root / "scripts" / "build_report.py"), "--site-fetch", str(site_fetch), "--crawler-audit", str(crawler), "--llmstxt-audit", str(llmstxt), "--citability-audit", str(citability), "--schema-audit", str(schema), "--output", str(report)],
    ]

    try:
        for cmd in commands:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        failure_lines = [line.strip() for line in (exc.stdout or "").splitlines() + (exc.stderr or "").splitlines() if line.strip()]
        failure_note = failure_lines[-1] if failure_lines else f"Command failed: {' '.join(exc.cmd)}"
        write_failure_report(report, args.url, failure_note)
        print("Audit incomplete:")
        print(f"- Report: {report}")
        print(f"- Failure note: {failure_note}")
        return

    print("Audit complete:")
    print(f"- JSON outputs: {output_dir}")
    print(f"- Report: {report}")
    print(f"- Draft llms.txt: {llms_draft}")


if __name__ == "__main__":
    main()
