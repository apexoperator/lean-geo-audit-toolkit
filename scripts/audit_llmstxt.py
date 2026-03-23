#!/usr/bin/env python3
"""Check llms.txt readiness and optionally draft a minimal file."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0 (compatible; geo-audit-tool/0.1; +https://example.com)"
TIMEOUT_SECONDS = 15


def normalize_base(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path
    if not netloc:
        raise ValueError(f"Invalid URL: {url}")
    return f"{scheme}://{netloc}"


def fetch_text(url: str) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read(200_000)
            charset = resp.headers.get_content_charset() or "utf-8"
            return {
                "ok": True,
                "status": getattr(resp, "status", 200),
                "text": body.decode(charset, errors="replace"),
            }
    except HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": f"HTTP {exc.code}"}
    except URLError as exc:
        return {"ok": False, "status": None, "error": str(exc.reason)}


def validate_llms_text(text: str) -> dict[str, Any]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    has_header = any(line.startswith("#") or line.startswith("[site]") for line in lines[:5])
    has_pages = any("[pages]" in line.lower() for line in lines)
    has_guidance = any("[guidance]" in line.lower() for line in lines)
    score = 0
    if lines:
        score += 3
    if has_header:
        score += 2
    if has_pages:
        score += 3
    if has_guidance:
        score += 2
    return {
        "lineCount": len(lines),
        "hasHeader": has_header,
        "hasPagesSection": has_pages,
        "hasGuidanceSection": has_guidance,
        "score": min(score, 10),
    }


def draft_llms_text(base: str, site_title: str = "") -> str:
    name = site_title or urlparse(base).netloc
    return "\n".join([
        "# Draft llms.txt",
        "",
        "[site]",
        f"name = {name}",
        f"url = {base}",
        "summary = Replace this with a concise description of the site and its public content.",
        "",
        "[pages]",
        f"- {base}/",
        f"- {base}/about",
        f"- {base}/docs",
        f"- {base}/contact",
        "",
        "[guidance]",
        "preferred_summary_style = concise",
        "citation_preference = link-to-source",
        "content_scope = public-pages-only",
        "sensitive_content = none",
        "",
    ])


def run(url: str, site_title: str = "") -> dict[str, Any]:
    base = normalize_base(url)
    llms = fetch_text(f"{base}/llms.txt")
    llms_full = fetch_text(f"{base}/llms-full.txt")
    validation = validate_llms_text(llms.get("text", "")) if llms.get("ok") else {
        "lineCount": 0,
        "hasHeader": False,
        "hasPagesSection": False,
        "hasGuidanceSection": False,
        "score": 0,
    }
    draft = draft_llms_text(base, site_title)
    score = validation["score"]
    if not llms.get("ok"):
        score = 4 if draft else 0
    result = {
        "target": base,
        "llmsTxt": {"url": f"{base}/llms.txt", **llms},
        "llmsFullTxt": {"url": f"{base}/llms-full.txt", **llms_full},
        "validation": validation,
        "draft": draft,
        "score": min(score, 10),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit llms.txt readiness")
    parser.add_argument("url")
    parser.add_argument("--site-title", default="")
    parser.add_argument("--output")
    parser.add_argument("--draft-output", help="Write draft llms.txt to file")
    args = parser.parse_args()
    result = run(args.url, args.site_title)
    if args.draft_output:
        with open(args.draft_output, "w", encoding="utf-8") as f:
            f.write(result["draft"])
    text = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
