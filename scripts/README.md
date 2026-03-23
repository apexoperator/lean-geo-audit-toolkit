# Scripts

This directory will hold the focused implementation pieces for the first version.

Current scripts:
- `fetch_site.py`
- `audit_crawlers.py`
- `audit_llmstxt.py`
- `audit_citability.py`
- `audit_schema.py`
- `build_report.py`
- `run_audit.py`
- `run_validation.py`

## Fast usage example

Run one audit:

```bash
python3 scripts/run_audit.py https://example.com --output-dir outputs/example-run
```

Run the validation set:

```bash
python3 scripts/run_validation.py
```

Typical outputs from a successful single-site run:
- `site-fetch.json`
- `crawler-audit.json`
- `llmstxt-audit.json`
- `citability-audit.json`
- `schema-audit.json`
- `draft-llms.txt`
- `report.md`

Planned next improvements:
- better schema extraction depth
- stronger technical-quality thresholds
- better signal extraction from noisy rendered pages while staying lightweight

Rules for scripts:
- keep them small and auditable
- avoid hidden state
- avoid surprise writes outside explicit output paths
- optimize for maintainability over cleverness
- fail honestly when lightweight fetch limits are hit; prefer explicit limitation reports over fake confidence
