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

## Setup

```bash
cd job-alert-validation
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

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
