# GEO Audit Report

- **Target:** https://example.com/
- **Audit date:** 2026-03-22
- **Overall readiness:** 20/100 (poor readiness)

## Executive Summary

- Current GEO readiness is weak, but the site likely has a manageable path to improvement through basic content, crawler, and metadata work.
- The weakest area in this pass is crawler posture.
- The fastest useful move is: Publish a basic llms.txt file and refine it as the content model matures.

## Score Summary

- **Overall:** 20/100
- **Citability / Answer Quality:** 2/10
- **Crawler Accessibility:** 0/10
- **llms.txt Readiness:** 4/10
- **Structured Data / Entity Signals:** 1/10
- **Technical Visibility Basics:** 3/10

## Strengths

- No major strengths detected in the current pass.

## Weaknesses

- Too many reviewed pages are thin, which weakens citability.
- Many pages do not yet provide strong, self-contained answer blocks.
- The sampled content often lacks specificity, evidence, or concrete factual density.
- Titles exist, but many may be weak, too short, or too thin to be useful.
- Descriptions are missing on too many reviewed pages.
- Canonical signals were not clearly detected on reviewed pages.
- Internal linking looks sparse in the reviewed sample.
- Schema coverage is thin across the reviewed sample.
- robots.txt was not available, so crawler posture is unclear.
- No llms.txt file was detected.

## Page-Level Notes

- **Best page candidate:** `https://example.com/`
  - Notes: thin content sample; weak answer-block structure; no schema detected
- **Weakest page candidate:** `https://example.com/`
  - Notes: thin content sample; weak answer-block structure; no schema detected; page likely wants schema such as: Organization

## Schema / Entity Direction

- Likely schema families worth prioritizing: Organization

## Prioritized Actions

### Quick Wins
1. Publish a basic llms.txt file and refine it as the content model matures.
1. Add a robots.txt file so crawler posture is explicit instead of guesswork.
1. Tighten page-title quality so titles are specific, usable, and not just present.

### Medium-Term Fixes
1. Rewrite key page intros and answer blocks so they are more direct, self-contained, and citable.
1. Tighten metadata, canonical usage, and internal linking consistency across priority pages.

### Strategic Improvements
1. Design stronger structured-data coverage around likely page intents: Organization.
1. Treat AI-search readiness as a content operations discipline, not a one-time checkbox exercise.

## Confidence / Caveats

- Low confidence: only a very small page sample was available, so findings may underrepresent the full site.
