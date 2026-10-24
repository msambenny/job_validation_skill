# job_validation_skill

Claude Code skills for validating WhatsApp-style job alerts: restructure input, check apply links, scrape postings, compare against user text, flag scam signals, format group messages, and match resumes to a local job library.

## Use it in Claude Code

**In this repository** — the skills are already in `.claude/skills/`, so Claude Code picks them up when you open the repo:

```text
/job-alert-validation <paste the job alert here>
/resume-match path/to/resume.pdf
```

You don't have to type the command: Claude also loads the skill on its own when you paste a job alert or ask whether a posting is real.

**In all your projects** — copy both skill folders to your personal skills directory (keep them side by side; `resume-match` uses `job-alert-validation`'s scripts):

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/job-alert-validation .claude/skills/resume-match ~/.claude/skills/
python3 -m pip install -r ~/.claude/skills/job-alert-validation/requirements.txt
```

On Windows, copy them to `%USERPROFILE%\.claude\skills\`.

The skill installs its Python dependencies on first use if they are missing. Validated jobs are saved to `job_postings/` inside the `job-alert-validation` folder (gitignored).

## Layout

| Path | Purpose |
|------|---------|
| [.claude/skills/job-alert-validation/SKILL.md](.claude/skills/job-alert-validation/SKILL.md) | `/job-alert-validation` — main workflow |
| [.claude/skills/resume-match/SKILL.md](.claude/skills/resume-match/SKILL.md) | `/resume-match` — match a resume to saved jobs |
| [.claude/skills/job-alert-validation/scripts/](.claude/skills/job-alert-validation/scripts/) | CLI tools the skills run |
| [.claude/skills/job-alert-validation/schemas/job_schema.json](.claude/skills/job-alert-validation/schemas/job_schema.json) | Canonical job JSON shape |
| [.claude/skills/job-alert-validation/job_postings/](.claude/skills/job-alert-validation/job_postings/) | Local validated jobs (JSON not committed) |
| [.claude/skills/job-alert-validation/demo/](.claude/skills/job-alert-validation/demo/) | Offline end-to-end demo (`run_demo.py`) |

## Development setup

```bash
cd .claude/skills/job-alert-validation
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Demo (offline, ~1 second)

From `.claude/skills/job-alert-validation/`:

```bash
python demo/run_demo.py          # add --json to see full output of each step
```

It walks through the whole skill without network access, using local HTML pages under `demo/pages/` and a temporary job library (your `job_postings/` is not touched):

1. **Genuine alert** (`demo/alerts/genuine_alert.json`) — matches its posting page, is saved, and a copy-ready WhatsApp message is printed.
2. **Suspicious alert** (`demo/alerts/suspicious_alert.json`) — a "Google" job pointing at a Google Form with a registration fee; critical fields don't match and trust warnings fire, so it is rejected.
3. **Resume matching** — `examples/backend_resume.txt` is matched against the saved library.

Posting dates are filled in relative to today, so the demo never goes stale against the 15-day freshness rule.

## Run tests

From `.claude/skills/job-alert-validation/`:

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

See [references/README.md](.claude/skills/job-alert-validation/references/README.md) for the full workflow diagram.
