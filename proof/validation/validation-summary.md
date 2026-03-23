# Validation Summary

This is the curated public-facing snapshot of the current lightweight validation pass.

It is intentionally small. The goal is to show that the toolkit has been exercised against real targets and that it reports directional findings without pretending lightweight fetches are perfect truth.

## Results

### https://stripe.com
- **Overall readiness:** 66/100 (decent baseline, meaningful improvements needed)
- Citability: 5/10
- Crawler: 10/10
- llms.txt: 5/10
- Schema: 4/10
- Fastest useful move: Tighten page-title quality so titles are specific, usable, and not just present.

### https://developer.mozilla.org
- **Overall readiness:** 58/100 (weak / inconsistent)
- Citability: 4/10
- Crawler: 10/10
- llms.txt: 4/10
- Schema: 3/10
- Fastest useful move: Publish a basic llms.txt file and refine it as the content model matures.

### https://www.shopify.com
- **Overall readiness:** 80/100 (strong foundation)
- Citability: 9/10
- Crawler: 10/10
- llms.txt: 5/10
- Schema: 4/10
- Fastest useful move: Tighten page-title quality so titles are specific, usable, and not just present.

### https://www.notion.so
- **Overall readiness:** 70/100 (decent baseline, meaningful improvements needed)
- Citability: 6/10
- Crawler: 10/10
- llms.txt: 5/10
- Schema: 4/10
- Fastest useful move: Tighten page-title quality so titles are specific, usable, and not just present.

## Notes for reviewers

- This toolkit uses a lightweight, non-browser fetch path on purpose.
- Some strong sites will be partially under-sampled in that mode.
- That is a known boundary, and the reporting should make it obvious.
- Curated proof stays intentionally small; disposable runs belong in `outputs/`.
