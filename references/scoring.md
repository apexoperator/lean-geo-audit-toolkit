# Scoring Model

This project uses a transparent scoring model to support the report.

Important rule: the score is there to summarize the audit, not pretend to be scientific truth.
Recommendations matter more than the number.

---

## Top-Level Categories

Each category is scored from **0 to 10**.

### 1. Citability / Answer Quality
What it checks:
- clarity
- specificity
- self-contained passages
- factual density
- obvious answer blocks / summary sections
- low fluff-to-signal ratio

High score:
- pages contain quotable, useful, clear passages that an AI system could plausibly cite or summarize well

Low score:
- vague marketing copy, weak structure, no direct answers, thin or noisy content

### 2. Crawler Accessibility
What it checks:
- `robots.txt` exists
- sitemap discoverability
- crawler directives are present and readable
- major AI crawlers are not ambiguously blocked
- crawl posture is understandable

High score:
- crawler access is explicit and sane

Low score:
- missing, confusing, contradictory, or overly restrictive posture

### 3. llms.txt Readiness
What it checks:
- `llms.txt` exists
- `llms-full.txt` or equivalent exists if applicable
- structure is valid enough to be useful
- generated draft would be straightforward if missing

High score:
- strong existing machine-readable guidance or very easy path to produce it

Low score:
- missing with no clear structure to derive from, or malformed / thin implementation

### 4. Structured Data / Entity Signals
What it checks:
- schema presence
- likely organization/article/product/person/etc. markup where relevant
- machine-readable identity signals
- consistency of entity representation

High score:
- strong structured data and entity clarity

Low score:
- missing or weak signals that make machine interpretation harder

### 5. Technical Visibility Basics
What it checks:
- title/description/canonical basics
- heading structure
- internal linking sanity
- obvious rendering/discoverability clues
- basic page hygiene for machine interpretation

High score:
- clean technical baseline that supports discoverability

Low score:
- basic metadata and structural hygiene are weak or inconsistent

---

## Suggested Weighting

Default weighting for the overall score:

- **Citability / Answer Quality:** 30%
- **Crawler Accessibility:** 20%
- **llms.txt Readiness:** 15%
- **Structured Data / Entity Signals:** 15%
- **Technical Visibility Basics:** 20%

This keeps content usefulness in the lead while still reflecting crawler and technical realities.

---

## Score Calculation

Formula:

```text
overall =
  citability * 0.30 +
  crawler * 0.20 +
  llmstxt * 0.15 +
  structured_data * 0.15 +
  technical_visibility * 0.20
```

Then convert to a 100-point score by multiplying by 10.

Example:

```text
citability = 7
crawler = 8
llmstxt = 4
structured_data = 6
technical_visibility = 7

weighted = 7*0.30 + 8*0.20 + 4*0.15 + 6*0.15 + 7*0.20 = 6.6
final = 66/100
```

---

## Interpretation Bands

- **0–39** — poor readiness
- **40–59** — weak / inconsistent
- **60–74** — decent baseline, meaningful improvements needed
- **75–89** — strong foundation
- **90–100** — unusually strong and well-prepared

These bands should not be over-sold. A site with a lower score can still have a few high-value quick wins.

---

## Adjustment Rules

### Downward adjustments
Apply judgment downward when:
- a site has technically present signals that are obviously low quality
- content is structurally present but not truly useful
- crawler guidance is present but contradictory
- schema exists but appears shallow, broken, or misleading

### Upward restraint
Do not over-reward:
- token compliance theater
- thin `llms.txt` files that add little value
- generic schema pasted everywhere
- polished metadata sitting on top of weak content

---

## Reporting Rule

Every score must be paired with:
- what is working
- what is weak
- quick wins
- medium-term fixes
- strategic improvements

The report should help an operator decide what to do next, not just admire a number.
