# Proof Artifacts

This directory holds the **curated, trackable proof layer** for the repo.

Use it for small, public-facing artifacts that help a reviewer understand:
- what the tool outputs look like
- how validation is being summarized
- where the current lightweight method is trustworthy vs limited

## What belongs here

- representative example reports
- representative draft `llms.txt` outputs
- compact validation summaries worth showing publicly
- short notes that explain fetch-limited or caveat-heavy cases honestly

## What does not belong here

- every local run
- bulky scratch outputs
- ad hoc experiments
- noisy intermediate files that are only useful during development

## Working rule

- `outputs/` stays ignored for disposable/generated work
- `proof/` stays intentionally small and curated

If an artifact is useful for a GitHub visitor or reviewer, consider `proof/`.
If it is just a local run, keep it in `outputs/`.
