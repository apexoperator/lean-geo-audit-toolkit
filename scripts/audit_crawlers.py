#!/usr/bin/env python3
"""Audit robots.txt and sitemap hints for crawler accessibility."""

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
AI_CRAWLERS = ["GPTBot", "CCBot", "ClaudeBot", "Claude-Web", "Google-Extended", "PerplexityBot"]


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
            body = resp.read(500_000)
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


def parse_robots(text: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    current_agents: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            agent = value or "*"
            current_agents = [agent]
            groups.setdefault(agent, [])
        elif key in {"allow", "disallow", "sitemap"}:
            if key == "sitemap":
                groups.setdefault("_sitemaps", []).append(value)
            elif current_agents:
                for agent in current_agents:
                    groups.setdefault(agent, []).append(f"{key}:{value}")
            else:
                groups.setdefault("*", []).append(f"{key}:{value}")
    return groups


def crawler_posture(groups: dict[str, list[str]], crawler: str) -> dict[str, Any]:
    rules = groups.get(crawler, []) + groups.get("*", [])
    disallows = [r.split(":", 1)[1] for r in rules if r.startswith("disallow:")]
    allows = [r.split(":", 1)[1] for r in rules if r.startswith("allow:")]
    blocked_all = any(rule == "/" for rule in disallows)
    posture = "blocked" if blocked_all else "allowed-or-unclear"
    return {
        "crawler": crawler,
        "posture": posture,
        "disallows": disallows,
        "allows": allows,
    }


def score(result: dict[str, Any]) -> int:
    robots_exists = result["robots"].get("ok", False)
    sitemaps = result.get("sitemaps", [])
    blocked = sum(1 for c in result["crawlerRules"] if c["posture"] == "blocked")
    score = 3 if robots_exists else 0
    if sitemaps:
        score += 2
    if blocked == 0 and robots_exists:
        score += 3
    elif blocked <= 2 and robots_exists:
        score += 2
    if robots_exists and any(c["allows"] or c["disallows"] for c in result["crawlerRules"]):
        score += 2
    return min(score, 10)


def run(url: str) -> dict[str, Any]:
    base = normalize_base(url)
    robots_url = f"{base}/robots.txt"
    robots = fetch_text(robots_url)
    groups = parse_robots(robots.get("text", "")) if robots.get("ok") else {}
    sitemaps = groups.get("_sitemaps", [])
    found_sitemap = []
    if not sitemaps:
        for candidate in [f"{base}/sitemap.xml", f"{base}/sitemap_index.xml"]:
            res = fetch_text(candidate)
            if res.get("ok") and re.search(r"<urlset|<sitemapindex", res.get("text", ""), re.I):
                found_sitemap.append(candidate)
    else:
        found_sitemap = sitemaps

    crawler_rules = [crawler_posture(groups, crawler) for crawler in AI_CRAWLERS]
    result = {
        "target": base,
        "robots": {"url": robots_url, **robots},
        "sitemaps": found_sitemap,
        "crawlerRules": crawler_rules,
    }
    result["score"] = score(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit robots.txt and crawler posture")
    parser.add_argument("url")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run(args.url)
    text = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
