# Lean GEO Audit Toolkit

A small, report-first toolkit for evaluating AI-search visibility, citability, crawler access, `llms.txt` readiness, and core technical discoverability signals.

---

## Overview

This repo is intentionally narrow. It covers:

- Lightweight fetch and page discovery
- `robots.txt` and sitemap review
- `llms.txt` detection and draft generation
- Citability scoring
- Schema and entity-direction checks
- Markdown report generation
- Repeatable validation runs
- Honest fetch-limited reporting when lightweight acquisition fails

---

## Who this is for

Operators, consultants, founders, and technical generalists who want a practical first-pass GEO / AI-search audit — without adopting a bloated SEO platform or an agency-in-a-box repo.

---

## What it does

Given a target site, the toolkit:

1. Fetches the homepage and selected internal pages
2. Inspects metadata, headings, canonicals, and internal-linking basics
3. Reviews `robots.txt` and sitemap discovery
4. Assesses citability and answer quality
5. Detects `llms.txt` and drafts one when missing
6. Checks schema and technical visibility signals
7. Produces one clean markdown report with prioritized next actions

---

## Why this exists

The GEO / AI-search audit idea is useful, but many implementations are too installer-heavy, too environment-specific, too broad, or too sloppy to trust. This project keeps the useful core and removes the surrounding sprawl.

---

## Runtime posture

| Property | Value |
|---|---|
| Language | Python 3 |
| Recommended version | Python 3.11+ |
| Dependencies | Standard library only |
| Execution model | Local scripts, explicit output paths, no hidden service state |

That posture is intentional. The goal is to stay small, auditable, and easy to reason about.

---

## Quickstart

**Run a single audit:**
```bash
python3 scripts/run_audit.py https://example.com --output-dir outputs/test-run
```

**Run the validation set:**
```bash
python3 scripts/run_validation.py
```

**Primary outputs from a normal run:**
```
site-fetch.json
crawler-audit.json
llmstxt-audit.json
citability-audit.json
schema-audit.json
draft-llms.txt
report.md
```

If lightweight fetch fails or is blocked, the tool writes a fetch-limited report rather than misattributing the limitation as a site weakness.

---

## Proof that it is real

This is not a concept stub. The repo includes:

- An end-to-end audit flow producing JSON artifacts, a markdown report, and a draft `llms.txt`
- Tracked proof artifacts in `proof/`
- Standard-library-only runtime posture
- A real-site validation pass showing both usable results and honest fetch limits
- Explicit methodology, scoring, and caveat documentation

**Public-facing proof artifacts live in `proof/`:**
```
proof/examples/example.com-report.md
proof/examples/example.com-draft-llms.txt
proof/validation/validation-summary.md
```

Disposable local runs stay in `outputs/` and are excluded by `.gitignore`.

---

## Validation snapshot

| Site | Score / Status |
|---|---|
| https://stripe.com | 66 / 100 |
| https://developer.mozilla.org | 58 / 100 |
| https://www.shopify.com | 80 / 100 |
| https://www.notion.so | 70 / 100 |
| https://openai.com | Fetch-limited / incomplete (HTTP 403 in lightweight mode) |

That mix is intentional. The goal is not flattering scores — it is believable first-pass diagnostics.

---

## What v1 is not

Explicit non-goals for this version:

- CRM
- Proposal generation
- Dashboard app or Flask web UI
- Browser automation (by default)
- PDF export
- Giant installer scripts
- Hidden persistent state
- Treating lightweight signals as perfect truth

---

## Repo structure
```
README.md               — Overview, runtime posture, quickstart, and limitations
LICENSE                 — Repo license
PROJECT-BRIEF.md        — Product brief
POSITIONING.md          — Product framing
references/
  scoring.md            — Scoring model
  methodology.md        — Audit method and assumptions
  validation-notes.md   — What validation exposed
proof/                  — Curated public-facing proof artifacts
examples/               — Lightweight example material and format references
scripts/                — Focused utilities
GITHUB-READINESS.md     — Minimum publish checklist
MONETIZATION.md         — First productized-service path
outputs/                — Local generated runs (git-ignored)
```

---

## Product direction

Current direction is hybrid-lightweight:

- Script/report flow first
- Optional richer crawler wrapper later, if it earns it
- Markdown report is the primary artifact

The strongest immediate use is not SaaS. It is a practical GEO baseline audit workflow and a credible proof asset.

---

## Limitations

This is intentionally a narrow first version.

Current fetch mode is lightweight and non-browser. That keeps the tool simple and auditable, but it means JS-heavy or bot-protected sites may return incomplete, noisy, or blocked HTML.

When that happens, the tool fails honestly: it writes a fetch-limited report, does not treat blocked acquisition as evidence the site is weak, and surfaces the limitation as a real caveat.

**This toolkit does not:**

- Predict rankings
- Replace a browser-based technical audit
- Fully model all AI systems
- Replace strategic content work
- Replace a full SEO or GEO platform

---

## Standard for publishability

This repo is only worth keeping public if it stays:

- Genuinely useful
- Easy to explain
- Easy to audit
- Modest in scope
- Honest about its limits
- Good enough to point clients or peers at without apology
