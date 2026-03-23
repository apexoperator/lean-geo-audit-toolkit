#!/usr/bin/env python3
"""Dedicated citability / answer-quality audit based on fetched page data."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

QUESTION_WORDS = {"what", "why", "how", "when", "where", "who", "which"}
ANSWER_CUE_WORDS = {
    "because", "means", "includes", "typically", "often", "best", "steps", "process",
    "benefits", "cost", "pricing", "works", "example", "examples", "guide",
}


def load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def valid_pages(site_fetch: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in site_fetch.get("pages", []) if not p.get("error")]


def count_questions(text: str) -> int:
    return text.count("?")


def count_lists(text: str) -> int:
    return len(re.findall(r"\b(first|second|third|steps?|tips?|ways?|how to|best|guide|faq|checklist)\b", text, re.I))


def count_numbers(text: str) -> int:
    return len(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[a-zA-Z]{3,}", text)]


def specificity_score(text: str) -> int:
    score = 0
    if count_numbers(text) > 0:
        score += 2
    if re.search(r"\b(percent|hours|days|months|years|users|customers|pricing|cost|revenue|kpi)\b", text, re.I):
        score += 2
    if re.search(r"\bfor example\b|\be\.g\.\b|\bsuch as\b", text, re.I):
        score += 2
    if re.search(r"\bversus\b|\bcompare\b|\btradeoff\b|\bdifference\b", text, re.I):
        score += 1
    return min(score, 5)


def answer_block_score(preview: list[str], headings: dict[str, list[str]]) -> int:
    blocks = 0
    for paragraph in preview:
        tokens = set(tokenize(paragraph))
        if len(paragraph.split()) >= 18:
            blocks += 1
        if QUESTION_WORDS & tokens:
            blocks += 1
        if ANSWER_CUE_WORDS & tokens:
            blocks += 1
    if headings.get("h2"):
        blocks += min(len(headings["h2"]), 2)
    return min(blocks, 5)


def assess_page(page: dict[str, Any]) -> dict[str, Any]:
    text = page.get("textSample", "")
    preview = page.get("contentPreview", [])
    word_count = int(page.get("wordCount", 0))
    sentence_count = int(page.get("sentenceCount", 0))
    h1s = page.get("headings", {}).get("h1", [])
    h2s = page.get("headings", {}).get("h2", [])
    question_count = count_questions(text)
    list_signal_count = count_lists(text)
    numeric_signal_count = count_numbers(text)
    specificity = specificity_score(text)
    answer_blocks = answer_block_score(preview, page.get("headings", {}))

    score = 0
    if page.get("title"):
        score += 1
    if page.get("description"):
        score += 1
    if h1s:
        score += 1
    if h2s:
        score += 1
    if word_count >= 250:
        score += 1
    if sentence_count >= 5:
        score += 1
    if question_count > 0 or list_signal_count > 0:
        score += 1
    if numeric_signal_count > 0:
        score += 1
    if specificity >= 2:
        score += 1
    if answer_blocks >= 3:
        score += 1

    observations = []
    if not h1s:
        observations.append("missing clear H1")
    if word_count < 250:
        observations.append("thin content sample")
    if answer_blocks < 3:
        observations.append("weak answer-block structure")
    if question_count == 0 and list_signal_count == 0:
        observations.append("few explicit answer-pattern signals")
    if numeric_signal_count == 0 and specificity < 2:
        observations.append("low specificity / factual density")

    return {
        "url": page.get("url"),
        "score": min(score, 10),
        "wordCount": word_count,
        "sentenceCount": sentence_count,
        "questionCount": question_count,
        "listSignalCount": list_signal_count,
        "numericSignalCount": numeric_signal_count,
        "specificityScore": specificity,
        "answerBlockScore": answer_blocks,
        "topTerms": page.get("topTerms", []),
        "observations": observations,
    }


def summarize(page_results: list[dict[str, Any]]) -> tuple[list[str], list[str], int]:
    if not page_results:
        return [], ["No valid pages were available for citability scoring."], 0
    average = round(sum(p["score"] for p in page_results) / len(page_results))
    strengths = []
    weaknesses = []
    if any(p["score"] >= 7 for p in page_results):
        strengths.append("At least one reviewed page shows decent answer-structure potential.")
    if sum(1 for p in page_results if p["wordCount"] >= 250) >= max(1, len(page_results) // 2):
        strengths.append("A meaningful share of reviewed pages has enough copy to support answer extraction.")
    if sum(1 for p in page_results if p["answerBlockScore"] >= 3) >= max(1, len(page_results) // 2):
        strengths.append("Several pages show usable answer-block structure rather than pure marketing fluff.")
    if sum(1 for p in page_results if p["specificityScore"] >= 2) >= max(1, len(page_results) // 2):
        strengths.append("Reviewed pages include some specific, concrete signals rather than only vague claims.")
    if sum(1 for p in page_results if p["wordCount"] < 250) >= max(1, len(page_results) // 2):
        weaknesses.append("Too many reviewed pages are thin, which weakens citability.")
    if sum(1 for p in page_results if p["answerBlockScore"] < 3) >= max(1, len(page_results) // 2):
        weaknesses.append("Many pages do not yet provide strong, self-contained answer blocks.")
    if sum(1 for p in page_results if p["specificityScore"] < 2) >= max(1, len(page_results) // 2):
        weaknesses.append("The sampled content often lacks specificity, evidence, or concrete factual density.")
    return strengths, weaknesses, average


def run(site_fetch_path: str) -> dict[str, Any]:
    site_fetch = load_json(site_fetch_path)
    pages = valid_pages(site_fetch)
    page_results = [assess_page(page) for page in pages]
    strengths, weaknesses, score = summarize(page_results)
    return {
        "target": site_fetch.get("target"),
        "score": score,
        "pageResults": page_results,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit citability using fetched page data")
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
