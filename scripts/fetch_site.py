#!/usr/bin/env python3
"""Fetch a site homepage plus a limited set of internal pages and basic metadata."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0 (compatible; geo-audit-tool/0.1; +https://example.com)"
MAX_PAGE_BYTES = 1_000_000
DEFAULT_PAGE_LIMIT = 8
TIMEOUT_SECONDS = 15
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in", "is", "it", "its",
    "of", "on", "or", "that", "the", "to", "was", "were", "will", "with", "your", "you", "our", "we",
}
BOILERPLATE_PHRASES = {
    "skip to main content",
    "skip to content",
    "cookie settings",
    "sign in",
    "log in",
    "download app",
    "back to top",
}


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.meta_robots = ""
        self.headings: dict[str, list[str]] = {"h1": [], "h2": [], "h3": []}
        self.links: list[dict[str, str]] = []
        self.schema_count = 0
        self.in_title = False
        self._current_title: list[str] = []
        self._active_heading_tag: str | None = None
        self._current_heading: list[str] = []
        self._active_anchor_index: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attr_map.get("name", "").lower()
            prop = attr_map.get("property", "").lower()
            content = attr_map.get("content", "").strip()
            if name == "description" and content and not self.description:
                self.description = content
            elif prop == "og:description" and content and not self.description:
                self.description = content
            elif name == "robots" and content and not self.meta_robots:
                self.meta_robots = content
        elif tag == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href", "").strip()
            if "canonical" in rel and href and not self.canonical:
                self.canonical = href
        elif tag in self.headings:
            self._active_heading_tag = tag
            self._current_heading = []
        elif tag == "a":
            href = attr_map.get("href", "").strip()
            text = attr_map.get("title", "").strip()
            rel = attr_map.get("rel", "").strip()
            link = {"href": href, "text": text, "rel": rel}
            self.links.append(link)
            self._active_anchor_index = len(self.links) - 1
        elif tag == "script":
            script_type = attr_map.get("type", "").lower()
            if "ld+json" in script_type:
                self.schema_count += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
            title = " ".join(self._current_title).strip()
            if title:
                self.title = re.sub(r"\s+", " ", title)
            self._current_title = []
        elif self._active_heading_tag == tag:
            cleaned = re.sub(r"\s+", " ", " ".join(self._current_heading)).strip()
            if cleaned:
                self.headings[tag].append(cleaned)
            self._active_heading_tag = None
            self._current_heading = []
        elif tag == "a":
            self._active_anchor_index = None

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self._current_title.append(data)
        if self._active_heading_tag is not None:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self._current_heading.append(cleaned)
        if self._active_anchor_index is not None:
            marker = self.links[self._active_anchor_index]
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                existing = marker.get("text", "")
                marker["text"] = f"{existing} {cleaned}".strip()


class ContentParser(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "form", "button", "nav", "footer", "header", "aside"}
    BLOCK_TAGS = {"p", "div", "section", "article", "main", "li", "blockquote", "pre", "td", "th", "br", "hr"}

    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        attr_blob = " ".join([attr_map.get("class", ""), attr_map.get("id", ""), attr_map.get("role", "")]).lower()
        if tag in self.SKIP_TAGS or any(term in attr_blob for term in ["nav", "menu", "footer", "header", "breadcrumb", "sidebar", "cookie", "modal", "drawer"]):
            self.skip_depth += 1
            return
        if self.skip_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skip_depth > 0 and tag in self.SKIP_TAGS.union({"div", "section", "aside", "header", "footer", "nav"}):
            self.skip_depth -= 1
            if self.skip_depth < 0:
                self.skip_depth = 0
            return
        if self.skip_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth > 0:
            return
        cleaned = re.sub(r"\s+", " ", data).strip()
        if cleaned:
            self.parts.append(cleaned)


def normalize_url(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path
    path = parsed.path if parsed.netloc else ""
    if not netloc:
        raise ValueError(f"Invalid URL: {url}")
    normalized = f"{scheme}://{netloc}{path or '/'}"
    return normalized.rstrip("/") if path not in ("", "/") else normalized


def fetch_url(url: str) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read(MAX_PAGE_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            text = body.decode(charset, errors="replace")
            return {
                "url": url,
                "ok": True,
                "status": getattr(resp, "status", 200),
                "contentType": content_type,
                "text": text,
            }
    except HTTPError as exc:
        return {"url": url, "ok": False, "status": exc.code, "error": f"HTTP {exc.code}"}
    except URLError as exc:
        return {"url": url, "ok": False, "status": None, "error": str(exc.reason)}


def tokenize(text: str) -> set[str]:
    tokens = {t.lower() for t in re.findall(r"[a-zA-Z]{3,}", text)}
    return {t for t in tokens if t not in STOPWORDS}


def score_link_candidate(base_url: str, link: dict[str, str]) -> tuple[int, int, str]:
    href = link.get("href", "")
    text = link.get("text", "")
    rel = link.get("rel", "").lower()
    parsed = urlparse(urljoin(base_url, href))
    path = parsed.path or "/"
    path_lower = path.lower()
    text_tokens = tokenize(text)
    path_tokens = tokenize(path_lower.replace("/", " ").replace("-", " "))

    score = 0
    if any(term in path_lower for term in [
        "/about", "/pricing", "/product", "/products", "/service", "/services", "/features",
        "/solutions", "/docs", "/blog", "/resources", "/faq", "/help", "/guide", "/contact",
    ]):
        score += 5
    if any(term in text.lower() for term in [
        "about", "pricing", "product", "service", "features", "docs", "blog", "resources", "faq", "guide", "contact",
    ]):
        score += 4
    if len(text_tokens) >= 2:
        score += 2
    if len(path_tokens) >= 1:
        score += 1
    if len(path) <= 40:
        score += 1
    if path.count("/") <= 2:
        score += 1
    if rel and "nofollow" in rel:
        score -= 2
    if any(bad in path_lower for bad in ["login", "signin", "signup", "cart", "checkout", "account", "privacy", "terms", "legal", "cdn-cgi"]):
        score -= 6
    if any(bad in href.lower() for bad in ["#", "javascript:", "mailto:", "tel:"]):
        score -= 10

    return (-score, path.count("/"), path)


def extract_internal_links(base_url: str, html: str, limit: int) -> list[str]:
    parser = MetadataParser()
    parser.feed(html)
    base = urlparse(base_url)
    unique: dict[str, dict[str, str]] = {}

    for link in parser.links:
        href = link.get("href", "")
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.netloc != base.netloc:
            continue
        if parsed.scheme not in {"http", "https"}:
            continue
        cleaned = f"{parsed.scheme}://{parsed.netloc}{parsed.path or '/'}"
        if cleaned == base_url:
            continue
        if cleaned not in unique:
            unique[cleaned] = {"href": cleaned, "text": link.get("text", ""), "rel": link.get("rel", "")}
        elif len(link.get("text", "")) > len(unique[cleaned].get("text", "")):
            unique[cleaned]["text"] = link.get("text", "")

    ranked = sorted(unique.values(), key=lambda item: score_link_candidate(base_url, item))
    return [item["href"] for item in ranked[:limit]]


def top_terms(text: str, limit: int = 8) -> list[str]:
    tokens = [t.lower() for t in re.findall(r"[a-zA-Z]{4,}", text) if t.lower() not in STOPWORDS]
    counts = Counter(tokens)
    return [term for term, _count in counts.most_common(limit)]


def clean_text_from_html(html: str) -> str:
    stripped = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    stripped = re.sub(r"<style[\s\S]*?</style>", " ", stripped, flags=re.I)
    stripped = re.sub(r"<noscript[\s\S]*?</noscript>", " ", stripped, flags=re.I)
    parser = ContentParser()
    parser.feed(stripped)
    raw_parts = [re.sub(r"\s+", " ", part).strip() for part in parser.parts]

    cleaned_parts: list[str] = []
    seen_normalized: set[str] = set()
    for part in raw_parts:
        if not part or len(part) < 20:
            continue
        normalized = part.lower().strip(" .:-|")
        if normalized in BOILERPLATE_PHRASES:
            continue
        if normalized in seen_normalized:
            continue
        if len(set(normalized.split())) <= 2 and len(normalized.split()) >= 4:
            continue
        if normalized.count(" ") < 2 and len(normalized) < 30:
            continue
        seen_normalized.add(normalized)
        cleaned_parts.append(part)

    return "\n".join(cleaned_parts)


def analyze_page(url: str, html: str, page_limit: int) -> dict[str, Any]:
    parser = MetadataParser()
    parser.feed(html)
    cleaned_text = clean_text_from_html(html)
    word_count = len(cleaned_text.split()) if cleaned_text else 0
    sentence_count = len(re.findall(r"[.!?]+", cleaned_text))
    paragraphs = [p.strip() for p in cleaned_text.splitlines() if p.strip()]
    return {
        "url": url,
        "title": parser.title,
        "description": parser.description,
        "canonical": parser.canonical,
        "metaRobots": parser.meta_robots,
        "headings": parser.headings,
        "wordCount": word_count,
        "sentenceCount": sentence_count,
        "schemaCount": parser.schema_count,
        "textSample": cleaned_text[:1200],
        "contentPreview": paragraphs[:5],
        "topTerms": top_terms(cleaned_text),
        "internalLinks": extract_internal_links(url, html, page_limit),
    }


def run(target_url: str, page_limit: int) -> dict[str, Any]:
    target_url = normalize_url(target_url)
    homepage = fetch_url(target_url)
    if not homepage.get("ok"):
        raise RuntimeError(f"Failed to fetch homepage: {homepage.get('error', 'unknown error')}")

    home_analysis = analyze_page(target_url, homepage["text"], page_limit)
    internal_links = home_analysis["internalLinks"][:page_limit]
    pages = [home_analysis]
    for link in internal_links:
        fetched = fetch_url(link)
        if fetched.get("ok") and str(fetched.get("contentType", "")).startswith("text/html"):
            pages.append(analyze_page(link, fetched["text"], page_limit))
        else:
            pages.append({
                "url": link,
                "error": fetched.get("error", "non-html or fetch failure"),
                "status": fetched.get("status"),
            })

    return {
        "target": target_url,
        "homepage": home_analysis,
        "pages": pages,
        "discoveredInternalLinks": internal_links,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch a site and basic metadata for GEO audit.")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--page-limit", type=int, default=DEFAULT_PAGE_LIMIT)
    parser.add_argument("--output", help="Write JSON output to file")
    args = parser.parse_args()

    result = run(args.url, max(1, args.page_limit))
    text = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
