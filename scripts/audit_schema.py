#!/usr/bin/env python3
"""Dedicated schema / entity-signal audit based on fetched page data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

IMPORTANT_TYPES = {
    "Organization",
    "WebSite",
    "Product",
    "Service",
    "FAQPage",
    "Article",
    "BlogPosting",
    "LocalBusiness",
    "BreadcrumbList",
    "Person",
}


def load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def valid_pages(site_fetch: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in site_fetch.get("pages", []) if not p.get("error")]


def same_registered_family(url_a: str, url_b: str) -> bool:
    host_a = urlparse(url_a).netloc.lower().split(":")[0]
    host_b = urlparse(url_b).netloc.lower().split(":")[0]
    if not host_a or not host_b:
        return False
    parts_a = host_a.split(".")
    parts_b = host_b.split(".")
    family_a = ".".join(parts_a[-2:]) if len(parts_a) >= 2 else host_a
    family_b = ".".join(parts_b[-2:]) if len(parts_b) >= 2 else host_b
    return family_a == family_b


def infer_schema_types(page: dict[str, Any], target: str) -> list[str]:
    title = (page.get("title") or "").lower()
    description = (page.get("description") or "").lower()
    headings = " ".join(page.get("headings", {}).get("h1", []) + page.get("headings", {}).get("h2", [])).lower()
    text = (page.get("textSample") or "").lower()
    path = urlparse(page.get("url") or "").path.lower()
    combined = " ".join([title, description, headings, text, path])

    inferred: list[str] = []
    is_homepage = (page.get("url") or "").rstrip("/") == target.rstrip("/")
    if is_homepage or any(term in path for term in ["/about", "/company", "/team", "/mission"]):
        inferred.append("Organization")
    if any(term in combined for term in ["faq", "frequently asked", "questions"]):
        inferred.append("FAQPage")
    if any(term in path for term in ["/blog", "/article", "/news", "/guides"]) or any(term in headings for term in ["guide", "article", "blog"]):
        inferred.append("Article")
    if any(term in path for term in ["/pricing", "/product", "/products"]) or any(term in combined for term in ["pricing", "plans", "buy", "purchase", "product"]):
        inferred.append("Product")
    if any(term in path for term in ["/service", "/services", "/solutions"]) or any(term in headings for term in ["service", "services", "solutions"]):
        inferred.append("Service")
    local_terms = ["address", "hours", "visit us", "locations", "find us"]
    if any(term in combined for term in local_terms):
        inferred.append("LocalBusiness")
    if len(page.get("internalLinks", [])) >= 3 and is_homepage:
        inferred.append("WebSite")
    return list(dict.fromkeys(inferred))


def assess_page(page: dict[str, Any], target: str) -> dict[str, Any]:
    schema_count = int(page.get("schemaCount", 0))
    meta_robots = bool(page.get("metaRobots"))
    title = bool(page.get("title"))
    description = bool(page.get("description"))
    canonical = bool(page.get("canonical"))
    inferred_types = infer_schema_types(page, target)

    score = 0
    if schema_count > 0:
        score += 4
    if inferred_types and schema_count > 0:
        score += 2
    if meta_robots:
        score += 1
    if title:
        score += 1
    if description:
        score += 1
    if canonical:
        score += 1

    observations = []
    if schema_count == 0:
        observations.append("no schema detected")
    if inferred_types and schema_count == 0:
        observations.append(f"page likely wants schema such as: {', '.join(inferred_types)}")
    if not canonical:
        observations.append("no canonical detected")
    if not description:
        observations.append("no description detected")
    if schema_count > 0 and not inferred_types:
        observations.append("schema exists, but page intent/type is not yet clearly classified by lightweight heuristics")

    return {
        "url": page.get("url"),
        "score": min(score, 10),
        "schemaCount": schema_count,
        "inferredTypes": inferred_types,
        "importantTypeHits": [t for t in inferred_types if t in IMPORTANT_TYPES],
        "hasMetaRobots": meta_robots,
        "hasTitle": title,
        "hasDescription": description,
        "hasCanonical": canonical,
        "observations": observations,
    }


def summarize(page_results: list[dict[str, Any]]) -> tuple[list[str], list[str], int, list[str]]:
    if not page_results:
        return [], ["No valid pages were available for schema scoring."], 0, []
    average = round(sum(p["score"] for p in page_results) / len(page_results))
    strengths = []
    weaknesses = []
    recommended_types: list[str] = []
    if any(p["schemaCount"] > 0 for p in page_results):
        strengths.append("Some reviewed pages publish detectable schema markup.")
    if sum(1 for p in page_results if p["hasCanonical"]) >= max(1, len(page_results) // 2):
        strengths.append("Canonical coverage appears on a meaningful share of reviewed pages.")
    if sum(1 for p in page_results if p["schemaCount"] == 0) >= max(1, len(page_results) // 2):
        weaknesses.append("Schema coverage is thin across the reviewed sample.")
    if sum(1 for p in page_results if not p["hasDescription"]) >= max(1, len(page_results) // 2):
        weaknesses.append("Descriptions are missing on too many reviewed pages.")

    for page in page_results:
        for schema_type in page.get("importantTypeHits", []):
            if schema_type not in recommended_types:
                recommended_types.append(schema_type)

    if not recommended_types:
        likely_needed = []
        for page in page_results:
            for schema_type in page.get("inferredTypes", []):
                if schema_type not in likely_needed:
                    likely_needed.append(schema_type)
        if likely_needed:
            weaknesses.append(f"Relevant schema may be missing for page intents such as: {', '.join(likely_needed)}.")
            recommended_types = likely_needed

    return strengths, weaknesses, average, recommended_types


def run(site_fetch_path: str) -> dict[str, Any]:
    site_fetch = load_json(site_fetch_path)
    pages = valid_pages(site_fetch)
    target = site_fetch.get("target", "")
    page_results = [assess_page(page, target) for page in pages]
    strengths, weaknesses, score, recommended_types = summarize(page_results)
    return {
        "target": target,
        "score": score,
        "recommendedTypes": recommended_types,
        "pageResults": page_results,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit schema/entity signals using fetched page data")
    parser.add_argument("--site-fetch", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run(args.site_fetch)
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
