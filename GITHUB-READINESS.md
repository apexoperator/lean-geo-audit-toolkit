# GitHub Readiness

This repo is close to public-worthy.
Not because it is "finished," but because the current shape is already coherent and honest.

## What is already in good shape

- Clear repo framing in `README.md`, `PROJECT-BRIEF.md`, and `POSITIONING.md`
- Standard-library-only Python scripts with no install sprawl
- End-to-end run path via `scripts/run_audit.py`
- Multi-site validation path via `scripts/run_validation.py`
- Tracked proof artifacts in `proof/`
- License present
- `outputs/` ignored so generated noise stays out of the repo
- Methodology / scoring docs present

## Minimum remaining gaps before pushing

These are the smallest worthwhile remaining fixes.

### 1. Do one final proof sanity pass before push
Check:
- `proof/examples/example.com-report.md`
- `proof/examples/example.com-draft-llms.txt`
- `proof/validation/validation-summary.md`

Goal:
- make sure they still match current output shape and wording.

### 2. Pick and standardize the public default branch name
Why:
- Not a code blocker, just public-polish consistency across the hosting setup.

### 3. Add a very small release note / first-tag note when publishing
Why:
- Helps frame the project as an intentionally narrow v0/v1 instead of an underbuilt platform.

## What does *not* need to happen before pushing

Avoid slipping into fake completeness work.

Do not block publication on:
- browser automation
- web UI
- PDF export
- a hosted service
- competitor comparison
- niche profiles
- elaborate packaging
- perfect scoring science

## Push standard

Good enough to push means:
- a stranger can understand what it does in under two minutes
- a reviewer can run it locally without dependency drama
- the repo shows proof, not just promises
- limitations are obvious instead of buried

That standard is already mostly met.

## Smallest next step

Update `scripts/README.md` with one short copy-paste usage example, then do the final proof sanity pass and push.
