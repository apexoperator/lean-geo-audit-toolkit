# PROJECT-BRIEF.md

## Project
Lean GEO Audit Toolkit

Working-name options:
- `geo-audit-tool`
- `geo-visibility-kit`
- `answer-engine-audit`
- `llmstxt-and-citability-audit`

Recommended direction for now: keep the internal workspace folder as `geo-audit-tool` until naming is earned.

---

## Why This Project Exists

A reviewed external repo (`zubair-trabzada/geo-seo-claude`) surfaced a useful idea inside a bloated package:
- GEO / AI-search visibility auditing is real
- citability and crawler visibility are useful lenses
- llms.txt and structured-data checks are useful workflow components

But the source project is wrong-shaped for this repo’s publishing goals and operating constraints:
- Claude-specific installation paths (`~/.claude/...`)
- heavy installer behavior
- Python dependency sprawl
- optional Playwright/browser installs
- bundled CRM/webapp/proposal layers
- more “agency-in-a-box” than focused tool

This project should preserve the useful core and discard the clutter.

---

## Product Thesis

Build a **small, credible, GitHub-worthy GEO audit toolkit** that helps operators review a website’s AI-search readiness without pretending to be an entire agency operating system.

The first version should feel:
- clean
- auditable
- practical
- report-first
- easy to understand
- restrained in scope

---

## Intended User

Primary user:
- operator, consultant, founder, marketer, or technical generalist who wants a practical GEO/AI-search audit

Not the initial target:
- agencies wanting built-in CRM/proposals/dashboards
- people who want a giant one-command “business in a box” stack
- users expecting a hosted SaaS product

---

## What Makes Our Version Better

Our version should be better by being:
- **smaller** — fewer moving parts, clearer architecture
- **safer** — no sketchy install path, no unnecessary mutations
- **more portable** — workspace-friendly and easier to adapt beyond Claude-specific assumptions
- **less bloated** — no premature CRM, no local dashboard, no funnel fluff
- **more credible** — cleaner docs, clearer scoring, better boundaries
- **more maintainable** — easier to audit and update over time

---

## V1 Scope

### Must Have
1. **Page Fetch & Basic Discovery**
   - fetch homepage
   - inspect title, description, canonical, headings
   - discover a limited set of important internal pages
   - fetch `robots.txt`
   - attempt sitemap discovery

2. **GEO / Citability Audit**
   - assess answer-block quality
   - assess clarity / self-containment / specificity
   - assess passage usefulness for AI citation
   - highlight weak content patterns

3. **Crawler / Visibility Audit**
   - review robots.txt for major AI crawlers
   - surface allow/block posture clearly
   - note missing / ambiguous crawler guidance

4. **llms.txt Workflow**
   - detect whether `llms.txt` exists
   - validate basic structure if present
   - generate a draft if missing

5. **Schema / Technical Signals**
   - detect schema presence
   - note likely gaps
   - capture basic technical visibility signals such as SSR hints, internal linking quality, and key metadata basics

6. **Single Clean Report**
   - one markdown report
   - concise score summary
   - prioritized fixes
   - clear “quick wins / medium-term / strategic” separation

### Nice to Have Later
- page-by-page audit mode
- niche-specific recommendations (SaaS, local, ecommerce, publisher)
- competitor comparison
- historical diffing
- PDF export

---

## Explicit Non-Goals For V1

Do **not** include in the first version:
- CRM / prospect pipeline
- proposals / invoicing / sales workflow
- web dashboard
- local Flask app
- Playwright/browser automation unless clearly required
- giant subagent orchestration theater
- giant installer scripts
- global home-directory sprawl
- “community” upsell or monetization copy in the repo

---

## Product Shape

Suggested repo structure:

```text
geo-audit-tool/
├── README.md
├── PROJECT-BRIEF.md
├── SKILL.md                    # optional if shaped as an OpenClaw-compatible skill/workflow
├── scripts/
│   ├── fetch_site.py
│   ├── audit_citability.py
│   ├── audit_crawlers.py
│   ├── audit_llmstxt.py
│   ├── audit_schema.py
│   └── build_report.py
├── references/
│   ├── scoring.md
│   └── methodology.md
├── examples/
│   ├── sample-report.md
│   └── sample-llms.txt
└── outputs/                   # ignored or example-only, depending on final shape
```

Alternative path:
- If it becomes an OpenClaw-first project, put the workflow in a skill package and keep scripts minimal.
- If it becomes a GitHub-first Python tool, keep the skill optional and the CLI/report path primary.

---

## Installation Philosophy

Installation should be boring.

Preferred:
- clone repo
- install a small dependency set if truly needed
- run a clear script or command

Avoid:
- curl-pipe-bash install
- hidden writes outside the project or workspace without warning
- forcing global user-home directories by default
- optional browser installs in v1

---

## State Philosophy

V1 should create as little persistent state as possible.

Preferred:
- input URL
- generated report in current working directory or explicit output path
- optional generated `llms.txt` draft

Avoid by default:
- hidden databases
- background services
- CRM JSON stores
- long-lived webapp state

---

## Scoring Philosophy

Use a transparent, limited scoring model.

Proposed top-level buckets:
- Citability / Answer Quality
- Crawler Accessibility
- llms.txt Readiness
- Structured Data / Entity Signals
- Technical Visibility Basics

Important rule:
- The score must support the report, not replace it.
- Recommendations matter more than pretending the score is scientific.

---

## First Build Strategy

### Build Order
1. define scoring and report sections
2. implement fetch + discovery
3. implement robots / llms.txt checks
4. implement citability analysis
5. implement schema/basic technical checks
6. generate one good markdown report
7. polish docs and examples

### Build Style
- keep code modular
- keep outputs legible
- no hidden magic
- optimize for maintainability over cleverness

---

## Publish Positioning

The repo should be positioned as:

> A lean GEO audit toolkit for evaluating AI-search visibility, citability, crawler access, llms.txt readiness, and core discoverability signals.

Not as:
- a complete GEO agency operating system
- a growth funnel
- a dashboard empire
- an all-in-one SEO replacement

---

## Why It Fits Jon’s Broader Model

This project matches the broader strategy of:
- finding useful raw tools
- stripping away bloat
- rebuilding the strong parts cleanly
- publishing something credible on GitHub

It is also a good test case for the repo-improvement framework because:
- the source material has a real concept inside it
- the weaknesses are obvious enough to improve on
- the v1 can be meaningfully smaller and better

---

## Immediate Next Decisions

Before implementation starts, decide:
1. Is this **OpenClaw-first**, **Python-tool-first**, or **hybrid**?
2. What repo name should we ship under when it is ready?
3. Do we want just a markdown report in v1, or also a draft `llms.txt` output file?
4. Do we want SaaS/local/ecommerce profiles in v1, or keep it generic first?

---

## Apex Recommendation

Recommended path:
- **hybrid-lightweight**, but biased toward a simple script/report flow first
- one good markdown report in v1
- optional `llms.txt` draft output in v1
- no CRM, no dashboard, no PDF, no browser automation in v1

That would be the right first public version.
