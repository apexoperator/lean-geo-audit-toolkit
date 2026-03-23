# Methodology

This project evaluates GEO / AI-search readiness by combining content usefulness, crawler posture, machine-readable guidance, structured data, and technical discoverability basics.

## Principles

### 1. Report-first
The main output is a concise markdown audit report.
The toolkit is not trying to be a dashboard empire in v1.

### 2. Practical over theatrical
Prefer checks that produce useful recommendations.
Avoid shallow vanity checks that create score noise without operational value.

### 3. Transparent heuristics
Use understandable heuristics and clearly state their limits.
Do not imply precision that the system does not actually have.

### 4. Minimal state
Default behavior should create as little persistent state as possible.
The primary outputs should be the report and optional draft files.

### 5. Narrow first version
The first version should solve one problem cleanly:
produce a useful AI-search/GEO audit for a target site.

## Core audit flow

1. Fetch homepage and a limited set of important pages.
2. Inspect metadata and structural signals.
3. Fetch and analyze `robots.txt`.
4. Attempt sitemap discovery.
5. Check for `llms.txt` and validate or draft it.
6. Inspect schema and likely entity signals.
7. Assess citability and answer quality.
8. Build one markdown report with scored sections and prioritized recommendations.

## Limits

This project should be explicit about what it does not do in v1:
- it does not guarantee how AI systems will rank or cite content
- it does not replace a full technical SEO audit
- it does not model every crawler or inference engine
- it does not promise perfect rendering or indexing insight
- it does not need a browser-based crawler unless evidence later proves that requirement

## Recommendation hierarchy

Recommendations should be grouped as:
- **Quick wins** — easy, high-leverage improvements
- **Medium-term fixes** — meaningful structural/content improvements
- **Strategic improvements** — larger system/content architecture opportunities

## Output standard

Each report should clearly state:
- target URL
- audit date
- top-level scores
- notable strengths
- notable weaknesses
- prioritized next actions
- confidence / caveat notes if needed
