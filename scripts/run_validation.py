#!/usr/bin/env python3
"""Run the GEO audit against a small validation set and summarize results."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_TARGETS = [
    "https://stripe.com",
    "https://developer.mozilla.org",
    "https://www.shopify.com",
    "https://www.notion.so",
]


def slugify(url: str) -> str:
    value = url.replace("https://", "").replace("http://", "").strip("/")
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_report_status(report_text: str) -> str:
    for line in report_text.splitlines():
        if line.startswith("- **Status:**"):
            return line.split(":", 1)[1].replace("**", "").strip()
    return "ok"


def run_one(base_dir: Path, url: str) -> dict[str, Any]:
    slug = slugify(url)
    outdir = base_dir / slug
    outdir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "python3",
            str(Path(__file__).with_name("run_audit.py")),
            url,
            "--output-dir",
            str(outdir),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    report_path = outdir / "report.md"
    if not report_path.exists():
        return {
            "url": url,
            "slug": slug,
            "status": "failed",
            "error": proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "unknown failure",
        }
    report = report_path.read_text(encoding="utf-8")
    status = parse_report_status(report)
    if status != "ok":
        failure_line = next((line for line in report.splitlines() if line.startswith("- ") and "Failure note" not in line and "could not complete" not in line), "")
        note_line = next((line for line in report.splitlines() if line.startswith("- RuntimeError") or line.startswith("- HTTP") or line.startswith("- Failed")), "")
        return {
            "url": url,
            "slug": slug,
            "status": status,
            "error": note_line.removeprefix("- ") if note_line else proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else failure_line,
        }
    lines = report.splitlines()
    overall_line = next((line for line in lines if "**Overall readiness:**" in line), "")
    summary = next((line[2:] for line in lines if line.startswith("- The fastest useful move is:")), "")
    return {
        "url": url,
        "slug": slug,
        "status": "ok",
        "overall": overall_line,
        "fastestMove": summary,
        "citability": load_json(outdir / "citability-audit.json").get("score", 0),
        "schema": load_json(outdir / "schema-audit.json").get("score", 0),
        "crawler": load_json(outdir / "crawler-audit.json").get("score", 0),
        "llmstxt": load_json(outdir / "llmstxt-audit.json").get("score", 0),
    }


def build_summary(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Validation Summary",
        "",
        "This file captures a lightweight multi-site validation pass for the GEO audit toolkit.",
        "",
        "## Results",
        "",
    ]
    for item in results:
        lines.append(f"### {item['url']}")
        if item.get("status") != "ok":
            lines.extend([
                f"- Status: {item.get('status', 'failed')}",
                f"- Failure note: {item.get('error', 'unknown failure')}",
                "",
            ])
            continue
        lines.extend(
            [
                item["overall"],
                f"- Citability: {item['citability']}/10",
                f"- Crawler: {item['crawler']}/10",
                f"- llms.txt: {item['llmstxt']}/10",
                f"- Schema: {item['schema']}/10",
                f"- Fastest useful move: {item['fastestMove'].replace('The fastest useful move is: ', '')}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GEO validation set")
    parser.add_argument("urls", nargs="*", help="Optional URLs to validate")
    parser.add_argument("--output-dir", default=str(Path(__file__).resolve().parents[1] / "outputs" / "validation"))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = args.urls or DEFAULT_TARGETS
    results = [run_one(output_dir, url) for url in targets]
    summary = build_summary(results)
    summary_path = output_dir / "SUMMARY.md"
    summary_path.write_text(summary + "\n", encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
