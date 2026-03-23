# Curated Example Guidance

This project is designed to produce a **practical first-pass audit**, not a fake-perfect verdict.

For a tracked public-facing artifact, start with:
- `../proof/examples/example.com-report.md`
- `../proof/examples/example.com-draft-llms.txt`
- `../proof/validation/validation-summary.md`


The current report shape is centered on:
- executive summary first
- score summary with explicit sub-scores
- strengths and weaknesses
- page-level notes when useful
- prioritized actions split into quick wins, medium-term fixes, and strategic improvements
- confidence / caveats that state whether the pass was normal or fetch-limited

## Why this matters

A public example should show the repo's current output honestly.

That means examples should:
- match the actual report headings and section order
- preserve caveats when a result is low-confidence
- avoid polished marketing language that overstates certainty
- make the fastest useful move obvious

## Recommended public proof set

- one representative report in `proof/examples/`
- one representative generated `draft-llms.txt`
- one compact validation summary in `proof/validation/`

The value of the toolkit is not that it removes judgment.
The value is that it creates a cleaner first-pass diagnostic than bloated or hype-heavy alternatives.
