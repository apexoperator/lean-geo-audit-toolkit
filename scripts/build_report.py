#!/usr/bin/env python3
"""Build a markdown GEO audit report from script outputs."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

WEIGHTS = {
    "citability": 0.30,
    "crawler": 0.20,
    "llmstxt": 0.15,
    "structuredData": 0.15,
    "technicalVisibility": 0.20,
}


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def valid_pages(site_fetch: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in site_fetch.get("pages", []) if not p.get("error")]


def title_quality(page: dict[str, Any]) -> bool:
    title = (page.get("title") or "").strip()
    return 20 <= len(title) <= 70 and len(title.split()) >= 3


def description_quality(page: dict[str, Any]) -> bool:
    description = (page.get("description") or "").strip()
    return 70 <= len(description) <= 170 and len(description.split()) >= 8


def canonical_consistency(page: dict[str, Any]) -> bool:
    from urllib.parse import urlparse

    canonical = (page.get("canonical") or "").strip().rstrip("/")
    url = (page.get("url") or "").strip().rstrip("/")
    if not canonical:
        return False
    if canonical == url or canonical.endswith(url.split("//", 1)[-1]):
        return True
    can_host = urlparse(canonical).netloc.lower().split(":")[0]
    url_host = urlparse(url).netloc.lower().split(":")[0]
    if not can_host or not url_host:
        return False
    can_parts = can_host.split('.')
    url_parts = url_host.split('.')
    can_family = '.'.join(can_parts[-2:]) if len(can_parts) >= 2 else can_host
    url_family = '.'.join(url_parts[-2:]) if len(url_parts) >= 2 else url_host
    can_path = urlparse(canonical).path.rstrip('/')
    url_path = urlparse(url).path.rstrip('/')
    return can_family == url_family and can_path == url_path


def internal_link_quality(page: dict[str, Any]) -> bool:
    links = page.get("internalLinks", [])
    return len(links) >= 2


def score_technical(site_fetch: dict[str, Any]) -> tuple[int, list[str], list[str], dict[str, Any]]:
    pages = valid_pages(site_fetch)
    if not pages:
        return 0, [], ["No pages were available for technical visibility checks."], {}

    title_good = sum(1 for p in pages if title_quality(p))
    title_present = sum(1 for p in pages if p.get("title"))
    description_good = sum(1 for p in pages if description_quality(p))
    description_present = sum(1 for p in pages if p.get("description"))
    canonical_good = sum(1 for p in pages if canonical_consistency(p))
    canonical_present = sum(1 for p in pages if p.get("canonical"))
    link_rich = sum(1 for p in pages if internal_link_quality(p))
    h1_count = sum(1 for p in pages if p.get("headings", {}).get("h1"))

    score = 0
    if title_good >= max(1, len(pages) // 2):
        score += 2
    elif title_present == len(pages):
        score += 1

    if description_good >= max(1, len(pages) // 2):
        score += 2
    elif description_present >= max(1, len(pages) - 1):
        score += 1

    if canonical_good >= max(1, len(pages) // 2):
        score += 2
    elif canonical_present >= max(1, len(pages) // 2):
        score += 1

    if link_rich >= max(1, len(pages) // 2):
        score += 2

    if h1_count >= max(1, len(pages) // 2):
        score += 2

    strengths = []
    weaknesses = []
    if title_good >= max(1, len(pages) // 2):
        strengths.append("A meaningful share of reviewed pages has titles that are present and plausibly usable.")
    elif title_present:
        weaknesses.append("Titles exist, but many may be weak, too short, or too thin to be useful.")
    else:
        weaknesses.append("Titles were not clearly detected on reviewed pages.")

    if description_good >= max(1, len(pages) // 2):
        strengths.append("Description coverage is not just present but reasonably usable on key pages.")
    elif description_present:
        weaknesses.append("Descriptions exist on some pages, but quality or consistency still looks weak.")
    else:
        weaknesses.append("Descriptions are missing on too many reviewed pages.")

    if canonical_good >= max(1, len(pages) // 2):
        strengths.append("Canonical usage looks directionally consistent on the reviewed sample.")
    elif canonical_present:
        weaknesses.append("Canonical signals exist, but consistency still needs review.")
    else:
        weaknesses.append("Canonical signals were not clearly detected on reviewed pages.")

    if link_rich:
        strengths.append("Internal linking is present, which helps discoverability.")
    else:
        weaknesses.append("Internal linking looks sparse in the reviewed sample.")

    if h1_count < max(1, len(pages) // 2):
        weaknesses.append("Primary heading coverage is inconsistent across reviewed pages.")

    diagnostics = {
        "titleGood": title_good,
        "titlePresent": title_present,
        "descriptionGood": description_good,
        "descriptionPresent": description_present,
        "canonicalGood": canonical_good,
        "canonicalPresent": canonical_present,
        "linkRich": link_rich,
        "h1Count": h1_count,
        "pageCount": len(pages),
    }
    return min(score, 10), strengths, weaknesses, diagnostics


def overall_score(scores: dict[str, int]) -> int:
    weighted = (
        scores["citability"] * WEIGHTS["citability"]
        + scores["crawler"] * WEIGHTS["crawler"]
        + scores["llmstxt"] * WEIGHTS["llmstxt"]
        + scores["structuredData"] * WEIGHTS["structuredData"]
        + scores["technicalVisibility"] * WEIGHTS["technicalVisibility"]
    )
    return round(weighted * 10)


def report_band(score: int) -> str:
    if score < 40:
        return "poor readiness"
    if score < 60:
        return "weak / inconsistent"
    if score < 75:
        return "decent baseline, meaningful improvements needed"
    if score < 90:
        return "strong foundation"
    return "unusually strong and well-prepared"


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def collect_actions(scores: dict[str, int], llms_data: dict[str, Any], crawler_data: dict[str, Any], schema_data: dict[str, Any], technical_diag: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    quick = []
    medium = []
    strategic = []
    if not llms_data.get("llmsTxt", {}).get("ok"):
        quick.append("Publish a basic llms.txt file and refine it as the content model matures.")
    if not crawler_data.get("robots", {}).get("ok"):
        quick.append("Add a robots.txt file so crawler posture is explicit instead of guesswork.")
    if technical_diag.get("titlePresent", 0) and technical_diag.get("titleGood", 0) < technical_diag.get("titlePresent", 0):
        quick.append("Tighten page-title quality so titles are specific, usable, and not just present.")
    if technical_diag.get("descriptionPresent", 0) and technical_diag.get("descriptionGood", 0) < technical_diag.get("descriptionPresent", 0):
        quick.append("Rewrite weak meta descriptions so they are more descriptive and machine-usable.")

    blocked = [c["crawler"] for c in crawler_data.get("crawlerRules", []) if c.get("posture") == "blocked"]
    if blocked:
        medium.append(f"Review whether these AI crawlers should remain blocked: {', '.join(blocked)}.")
    if scores["citability"] < 7:
        medium.append("Rewrite key page intros and answer blocks so they are more direct, self-contained, and citable.")
    if scores["technicalVisibility"] < 7:
        medium.append("Tighten metadata, canonical usage, and internal linking consistency across priority pages.")

    recommended_types = schema_data.get("recommendedTypes", [])
    if recommended_types:
        strategic.append(f"Design stronger structured-data coverage around likely page intents: {', '.join(recommended_types)}.")
    elif scores["structuredData"] < 7:
        strategic.append("Design a stronger structured-data and entity layer for high-value pages.")
    strategic.append("Treat AI-search readiness as a content operations discipline, not a one-time checkbox exercise.")
    return dedupe(quick), dedupe(medium), dedupe(strategic)


def pick_best_and_worst_pages(citability_data: dict[str, Any], schema_data: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    page_scores: dict[str, dict[str, Any]] = {}
    for page in citability_data.get("pageResults", []):
        page_scores.setdefault(page["url"], {"url": page["url"]})["citability"] = page.get("score", 0)
        page_scores[page["url"]]["citabilityObs"] = page.get("observations", [])
    for page in schema_data.get("pageResults", []):
        page_scores.setdefault(page["url"], {"url": page["url"]})["schema"] = page.get("score", 0)
        page_scores[page["url"]]["schemaObs"] = page.get("observations", [])
    if not page_scores:
        return None, None

    def total(item: dict[str, Any]) -> int:
        return int(item.get("citability", 0)) + int(item.get("schema", 0))

    ranked = sorted(page_scores.values(), key=total, reverse=True)
    return ranked[0], ranked[-1]


def confidence_note(site_fetch: dict[str, Any]) -> str:
    pages = valid_pages(site_fetch)
    if len(pages) <= 1:
        return "Low confidence: only a very small page sample was available, so findings may underrepresent the full site."
    if len(pages) <= 3:
        return "Moderate confidence: a limited page sample was reviewed, enough for directional findings but not broad certainty."
    return "Moderate confidence: enough pages were reviewed for directional conclusions, but this is still a lightweight non-browser pass."


def executive_summary(overall: int, scores: dict[str, int], quick: list[str]) -> list[str]:
    lines = []
    if overall < 40:
        lines.append("Current GEO readiness is weak, but the site likely has a manageable path to improvement through basic content, crawler, and metadata work.")
    elif overall < 60:
        lines.append("The site has some usable signals, but consistency is not yet strong enough for confident AI-search readiness.")
    else:
        lines.append("The site has a workable baseline, though there are still opportunities to improve AI-search clarity and machine readability.")

    weakest = min(scores, key=scores.get)
    labels = {
        "citability": "citability",
        "crawler": "crawler posture",
        "llmstxt": "llms.txt readiness",
        "structuredData": "structured data",
        "technicalVisibility": "technical visibility",
    }
    lines.append(f"The weakest area in this pass is {labels.get(weakest, weakest)}.")
    if quick:
        lines.append(f"The fastest useful move is: {quick[0]}")
    return lines


def build_markdown(
    target: str,
    scores: dict[str, int],
    strengths: list[str],
    weaknesses: list[str],
    quick: list[str],
    medium: list[str],
    strategic: list[str],
    best_page: dict[str, Any] | None,
    worst_page: dict[str, Any] | None,
    schema_data: dict[str, Any],
    confidence: str,
) -> str:
    overall = overall_score(scores)
    summary_lines = executive_summary(overall, scores, quick)
    lines = [
        "# GEO Audit Report",
        "",
        f"- **Target:** {target}",
        f"- **Audit date:** {datetime.now(UTC).date().isoformat()}",
        f"- **Overall readiness:** {overall}/100 ({report_band(overall)})",
        "",
        "## Executive Summary",
        "",
    ]
    lines.extend([f"- {line}" for line in summary_lines])
    lines.extend([
        "",
        "## Score Summary",
        "",
        f"- **Overall:** {overall}/100",
        f"- **Citability / Answer Quality:** {scores['citability']}/10",
        f"- **Crawler Accessibility:** {scores['crawler']}/10",
        f"- **llms.txt Readiness:** {scores['llmstxt']}/10",
        f"- **Structured Data / Entity Signals:** {scores['structuredData']}/10",
        f"- **Technical Visibility Basics:** {scores['technicalVisibility']}/10",
        "",
        "## Strengths",
        "",
    ])
    lines.extend([f"- {item}" for item in strengths] or ["- No major strengths detected in the current pass."])
    lines.extend(["", "## Weaknesses", ""])
    lines.extend([f"- {item}" for item in weaknesses] or ["- No major weaknesses detected in the current pass."])

    lines.extend(["", "## Page-Level Notes", ""])
    if best_page:
        lines.append(f"- **Best page candidate:** `{best_page['url']}`")
        best_obs = best_page.get("citabilityObs", [])[:2] + best_page.get("schemaObs", [])[:1]
        if best_obs:
            lines.append(f"  - Notes: {'; '.join(best_obs)}")
    if worst_page:
        lines.append(f"- **Weakest page candidate:** `{worst_page['url']}`")
        worst_obs = worst_page.get("citabilityObs", [])[:2] + worst_page.get("schemaObs", [])[:2]
        if worst_obs:
            lines.append(f"  - Notes: {'; '.join(worst_obs)}")
    if not best_page and not worst_page:
        lines.append("- Page-level notes unavailable in the current pass.")

    recommended_types = schema_data.get("recommendedTypes", [])
    lines.extend(["", "## Schema / Entity Direction", ""])
    if recommended_types:
        lines.append(f"- Likely schema families worth prioritizing: {', '.join(recommended_types)}")
    else:
        lines.append("- No strong schema-family recommendation emerged from the current lightweight pass.")

    lines.extend(["", "## Prioritized Actions", ""])
    if quick:
        lines.append("### Quick Wins")
        lines.extend([f"1. {item}" for item in quick])
        lines.append("")
    if medium:
        lines.append("### Medium-Term Fixes")
        lines.extend([f"1. {item}" for item in medium])
        lines.append("")
    if strategic:
        lines.append("### Strategic Improvements")
        lines.extend([f"1. {item}" for item in strategic])
        lines.append("")
    if not quick and not medium and not strategic:
        lines.append("- No action recommendations generated in the current pass.")
        lines.append("")

    lines.extend(["## Confidence / Caveats", "", f"- {confidence}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build markdown report from GEO audit JSON outputs")
    parser.add_argument("--site-fetch", required=True)
    parser.add_argument("--crawler-audit", required=True)
    parser.add_argument("--llmstxt-audit", required=True)
    parser.add_argument("--citability-audit", required=True)
    parser.add_argument("--schema-audit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    site_fetch = load_json(args.site_fetch)
    crawler_data = load_json(args.crawler_audit)
    llms_data = load_json(args.llmstxt_audit)
    citability_data = load_json(args.citability_audit)
    schema_data = load_json(args.schema_audit)

    technical_score, tech_strengths, tech_weaknesses, technical_diag = score_technical(site_fetch)
    scores = {
        "citability": int(citability_data.get("score", 0)),
        "crawler": int(crawler_data.get("score", 0)),
        "llmstxt": int(llms_data.get("score", 0)),
        "structuredData": int(schema_data.get("score", 0)),
        "technicalVisibility": technical_score,
    }
    strengths = dedupe(citability_data.get("strengths", []) + tech_strengths + schema_data.get("strengths", []))
    weaknesses = dedupe(citability_data.get("weaknesses", []) + tech_weaknesses + schema_data.get("weaknesses", []))
    if not crawler_data.get("robots", {}).get("ok"):
        weaknesses.append("robots.txt was not available, so crawler posture is unclear.")
    if not llms_data.get("llmsTxt", {}).get("ok"):
        weaknesses.append("No llms.txt file was detected.")
    weaknesses = dedupe(weaknesses)
    quick, medium, strategic = collect_actions(scores, llms_data, crawler_data, schema_data, technical_diag)
    best_page, worst_page = pick_best_and_worst_pages(citability_data, schema_data)
    confidence = confidence_note(site_fetch)
    report = build_markdown(
        site_fetch.get("target", "unknown target"),
        scores,
        strengths,
        weaknesses,
        quick,
        medium,
        strategic,
        best_page,
        worst_page,
        schema_data,
        confidence,
    )
    Path(args.output).write_text(report, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
