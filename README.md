Lean GEO Audit Toolkit
A small, report-first toolkit for evaluating AI-search visibility, citability, crawler access, llms.txt readiness, and basic technical discoverability signals.

This repo is intentionally narrow:

lightweight fetch + page discovery
robots.txt / sitemap review
llms.txt detection and draft generation
citability scoring
schema / entity-direction checks
markdown report generation
repeatable validation runs
honest fetch-limited reporting when lightweight acquisition fails
Who this is for
This is for operators, consultants, founders, and technical generalists who want a practical first-pass GEO / AI-search audit without adopting a bloated SEO platform or an agency-in-a-box repo.

What it does
Given a target site, the toolkit:

fetches a homepage and selected internal pages
inspects metadata, headings, canonicals, and internal-linking basics
reviews robots.txt and sitemap discovery
assesses citability / answer quality
detects llms.txt and drafts one when missing
checks schema / technical visibility signals
produces one clean markdown report with prioritized next actions
Why this exists
The GEO / AI-search audit idea is useful, but many implementations are too installer-heavy, too environment-specific, too broad, or too sloppy to trust.

This project keeps the useful core and removes the surrounding sprawl.

Runtime posture
Language: Python 3
Recommended version: Python 3.11+
Dependencies: standard library only
Execution model: local scripts with explicit output paths and no hidden service state
That posture is intentional. The goal is to stay small, auditable, and easy to reason about.

Quickstart
Run a single audit:

python3 scripts/run_audit.py https://example.com --output-dir outputs/test-run

Run the validation set:

python3 scripts/run_validation.py

Primary outputs from a normal run:

site-fetch.json
crawler-audit.json
llmstxt-audit.json
citability-audit.json
schema-audit.json
draft-llms.txt
report.md
If lightweight fetch fails or is blocked, the tool writes a fetch-limited report instead of pretending the site itself is poor.

Proof that it is real
This is not just a concept stub. The repo already includes:

an end-to-end audit flow that produces JSON artifacts, a markdown report, and a draft llms.txt
tracked proof artifacts in proof/
a standard-library-only runtime posture
a small real-site validation pass showing both usable results and honest fetch limits
explicit methodology, scoring, and caveat documentation
Public-facing proof artifacts live in proof/:

proof/examples/example.com-report.md
proof/examples/example.com-draft-llms.txt
proof/validation/validation-summary.md
Disposable local runs stay in outputs/ and are ignored by git.

Validation snapshot
Current lightweight validation examples include:

https://stripe.com → 66/100
https://developer.mozilla.org → 58/100
https://www.shopify.com → 80/100
https://www.notion.so → 70/100
https://openai.com → fetch-limited / incomplete (HTTP 403 in lightweight mode)
That mix is useful on purpose. The goal is not flattering scores; it is believable first-pass diagnostics.

What v1 is not
Explicit non-goals for this version:

CRM
proposal generation
dashboard app
Flask web UI
browser automation by default
PDF export
giant installer scripts
hidden persistent state
pretending lightweight signals are perfect truth
Repo structure
README.md — overview, runtime posture, quickstart, and limitations
LICENSE — repo license
PROJECT-BRIEF.md — product brief
POSITIONING.md — product framing
references/scoring.md — scoring model
references/methodology.md — audit method and assumptions
references/validation-notes.md — what validation exposed
proof/ — curated public-facing proof artifacts
examples/ — lightweight example material and format references
scripts/ — focused utilities
GITHUB-READINESS.md — minimum publish checklist
MONETIZATION.md — first productized-service path
outputs/ — local generated runs
Product direction
Current direction is hybrid-lightweight:

script/report flow first
optional OpenClaw wrapper later if it earns it
markdown report is the primary artifact
The strongest immediate use is not SaaS. It is a practical GEO baseline audit workflow and a credible proof asset.

Limitations
This is intentionally a narrow first version.

Current fetch mode is lightweight and non-browser. That keeps the tool simple and auditable, but it also means some JS-heavy or bot-protected sites may return incomplete, noisy, or blocked HTML.

When that happens, the tool should fail honestly:

it writes a fetch-limited report
it does not treat blocked acquisition as proof the site is weak
it surfaces the limitation as a real caveat
This toolkit does not:

predict rankings
replace a browser-based technical audit
fully model all AI systems
replace strategic content work
replace a full SEO or GEO platform
Standard for publishability
This repo is only worth keeping public if it stays:

genuinely useful
easy to explain
easy to audit
modest in scope
honest about limits
good enough to point clients or peers at without apology
