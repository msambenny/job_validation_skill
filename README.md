# job_validation_skill

Cursor Agent Skill for validating WhatsApp-style job alerts: restructure input, check apply links, scrape postings, compare against user text, format group messages, and match resumes to a local job library.

## Layout

| Path | Purpose |
|------|---------|
| [job-alert-validation/SKILL.md](job-alert-validation/SKILL.md) | Main agent workflow |
| [job-alert-validation/resume-match/SKILL.md](job-alert-validation/resume-match/SKILL.md) | Resume matching sub-skill |
| [job-alert-validation/scripts/](job-alert-validation/scripts/) | CLI tools used by the agent |
| [job-alert-validation/schemas/job_schema.json](job-alert-validation/schemas/job_schema.json) | Canonical job JSON shape |
| [job-alert-validation/job_postings/](job-alert-validation/job_postings/) | Local validated jobs (JSON not committed) |
| [job-alert-validation/demo/](job-alert-validation/demo/) | Offline end-to-end demo (`run_demo.py`) |

## Setup

```bash
cd job-alert-validation
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Demo (offline, ~1 second)

From `job-alert-validation/`:

```bash
python demo/run_demo.py          # add --json to see full output of each step
```

It walks through the whole skill without network access, using local HTML pages under `demo/pages/` and a temporary job library (your `job_postings/` is not touched):

1. **Genuine alert** (`demo/alerts/genuine_alert.json`) — matches its posting page, is saved, and a copy-ready WhatsApp message is printed.
2. **Suspicious alert** (`demo/alerts/suspicious_alert.json`) — a "Google" job pointing at a Google Form with a registration fee; critical fields don't match and trust warnings fire, so it is rejected.
3. **Resume matching** — `examples/backend_resume.txt` is matched against the saved library.

Posting dates are filled in relative to today, so the demo never goes stale against the 15-day freshness rule.

## Run tests

From `job-alert-validation/`:

```bash
pytest
```

Tests use offline HTML/JSON fixtures only (no live URL fetches).

## Script quick reference

```bash
python scripts/validate_job.py tests/fixtures/jobs/user_job.json --scraped-json tests/fixtures/jobs/scraped_job.json --pretty
python scripts/validate_url.py "https://example.com/jobs/1" --pretty
python scripts/web_scraping.py "https://example.com/jobs/1" --pretty
python scripts/compare_job.py tests/fixtures/jobs/user_job.json tests/fixtures/jobs/scraped_job.json --pretty
python scripts/format_whatsapp.py tests/fixtures/jobs/user_job.json
python scripts/match_resume.py examples/sample_resume.txt --pretty
python scripts/list_jobs.py --pretty
python scripts/housekeep_jobs.py --pretty
```

See [job-alert-validation/references/README.md](job-alert-validation/references/README.md) for the full workflow diagram.
