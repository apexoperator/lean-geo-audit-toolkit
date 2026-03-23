# Lean GEO Audit Toolkit

A lightweight, report-first toolkit for evaluating AI-search visibility, citability, crawler access, `llms.txt` readiness, and basic technical discoverability signals.

## Status

Active build with a working end-to-end core.

The toolkit currently supports:
- lightweight fetch + page discovery
- crawler / `robots.txt` review
- `llms.txt` detection and draft generation
- citability scoring
- schema / entity-direction checks
- markdown report generation
- repeatable multi-site validation
- graceful fetch-limited reporting for blocked or unusable targets

Current focus is no longer "make it work at all." Current focus is **trustworthiness, report quality, and public-proof polish**.

## Why this exists

The GEO / AI-search audit idea is useful, but many implementations are too bloated, too installer-heavy, too environment-specific, or too sloppy to adopt directly.

This project keeps the useful core and removes the agency-in-a-box sprawl.

## Runtime and dependency posture

- **Language:** Python 3
- **Recommended version:** Python 3.11+
- **Dependency posture:** standard-library only right now; no third-party packages are required
- **Execution model:** local scripts with explicit output paths and no hidden service state

That is intentional. The current value proposition is small, auditable, and easy to inspect.

## Quickstart

Run a single audit:

```bash
python3 scripts/run_audit.py https://example.com --output-dir outputs/test-run
```

Run the validation set:

```bash
python3 scripts/run_validation.py
```

Primary outputs from a normal run:
- `site-fetch.json`
- `crawler-audit.json`
- `llmstxt-audit.json`
- `citability-audit.json`
- `schema-audit.json`
- `draft-llms.txt`
- `report.md`

If the lightweight fetch path is blocked, the tool still writes a **fetch-limited report** instead of pretending the site is poor.

## Product direction

This version is being built to be:
- smaller
- safer
- easier to audit
- easier to maintain
- more GitHub-worthy
- more honest about limitations
- less cluttered by CRM / dashboard / agency fluff

## Why this repo is credible already

This is not just a concept stub.

Today the repo already has:
- an end-to-end audit flow that produces JSON artifacts, a markdown report, and a draft `llms.txt`
- tracked proof artifacts in `proof/` instead of only disposable local outputs
- a standard-library-only runtime posture
- a small real-site validation pass showing both usable results and honest fetch limits
- explicit methodology, scoring, and caveat documentation

That combination matters more than feature count.

## GitHub-readiness and commercialization notes

Two small planning docs now live alongside the code:
- `GITHUB-READINESS.md` — the minimum remaining cleanup before public push
- `MONETIZATION.md` — the first simple service offer this repo can support without pretending to be SaaS

## What v1 is for

Use it to produce a practical first-pass GEO / AI-search audit that:
- fetches a homepage and selected internal pages
- inspects metadata, headings, canonical, and internal linking basics
- reviews `robots.txt` and sitemap discovery
- assesses citability / answer quality
- detects `llms.txt` and drafts one when missing
- inspects schema / technical visibility signals
- outputs one clean markdown report with prioritized next actions

## Explicit non-goals for v1

- CRM
- proposal generation
- dashboard app
- Flask web UI
- browser automation by default
- PDF export
- giant installer scripts
- hidden persistent state
- pretending lightweight signals are perfect truth

## Validation evidence

A lightweight validation pass currently includes examples like:
- `https://stripe.com` → 66/100
- `https://developer.mozilla.org` → 58/100
- `https://www.shopify.com` → 80/100
- `https://www.notion.so` → 70/100
- `https://openai.com` → fetch-limited / incomplete (HTTP 403 in lightweight mode)

That mix is useful on purpose: the goal is not flattering scores, but believable first-pass diagnostics.

Public-facing proof artifacts live in `proof/`:
- `proof/examples/example.com-report.md`
- `proof/examples/example.com-draft-llms.txt`
- `proof/validation/validation-summary.md`

Disposable run outputs stay in `outputs/` and are ignored by git.

## Repo structure

- `README.md` — overview, runtime posture, quickstart, and limitations
- `LICENSE` — repo license
- `PROJECT-BRIEF.md` — product brief
- `POSITIONING.md` — product framing
- `references/scoring.md` — scoring model
- `references/methodology.md` — audit method and assumptions
- `references/validation-notes.md` — what validation exposed
- `proof/` — curated public-facing proof artifacts
- `examples/` — lightweight example material and format references
- `scripts/` — focused utilities
- `GITHUB-READINESS.md` — remaining minimum publish checklist
- `MONETIZATION.md` — first productized-service path
- `outputs/` — local generated runs

## Architecture choice

Current direction: **hybrid-lightweight**
- script/report flow first
- optional OpenClaw wrapper later if it earns it
- markdown report is the primary artifact

## Limitations

This is intentionally a narrow first version.

Current fetch mode is intentionally lightweight and non-browser. That keeps the tool simple and auditable, but it also means some JS-heavy or bot-protected sites may return incomplete, noisy, or blocked HTML.

When that happens, the tool should fail honestly:
- it writes a fetch-limited report
- it does **not** pretend the site is bad just because lightweight acquisition failed
- it surfaces the limitation as a real caveat

This toolkit does **not**:
- predict rankings
- replace a browser-based technical audit
- fully model all AI systems
- replace strategic content work
- replace a full SEO or GEO platform

## Standard for publishability

This repo is only worth publishing if it becomes:
- genuinely useful
- easy to explain
- easy to audit
- modest in scope
- honest about limits
- something worth pointing clients or peers at without apology
