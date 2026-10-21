---
name: job-alert-validation
description: Restructures job descriptions, validates apply links, scrapes posting pages, and compares content against user input. Use when the user enters a job or career opportunity.
---

# job-alert-validation

## Setup

Install dependencies once:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest
```

Job JSON shape is defined in [schemas/job_schema.json](schemas/job_schema.json).

## Instructions

1. Ask the user for the job description.

2. Restructure the job description to fit this pattern:

Form Fields:
- Company name, job title, department
- Job type (Full-Time, Part-Time, Remote, etc.) and work mode (On-site/Hybrid/Remote)
- Location
- Salary range (min and max) and benefits
- Experience, education, and skills
- Job description / responsibilities
- Application deadline
- Contact details (name, WhatsApp, email)
- Apply link and custom note

Save the restructured data as JSON for later comparison (for example `user_job.json`).

3. If there is a link in the input, capture the URL.

**Optional — run the full pipeline in one step** after saving user JSON:

```bash
python scripts/validate_job.py user_job.json --pretty --whatsapp --save
```

- Exit code `0` — comparison passed; with `--save`, the job is stored under `job_postings/` for resume matching.
- Exit code `1` — mismatches; report `comparison.summary.critical_mismatches` and do not save.
- Exit code `2` — no URL in the JSON (and no `--url`).
- Exit code `3` — URL validation failed; warn the user not to apply.

For offline checks (fixtures / HTML on disk), pass `--scraped-json scraped_job.json` instead of hitting the network.

4. Confirm the link is genuine by running `validate_url.py` (or rely on step 3 / `validate_job.py`):

```bash
python scripts/validate_url.py "<url>" --pretty
```

Expected valid response (Phase 2 adds redirect and host-awareness fields):

```json
{
  "url": "https://example.com/job-posting",
  "valid": true,
  "status_code": 200,
  "final_url": "https://example.com/job-posting",
  "fetch_method": "HEAD",
  "redirect_chain": ["https://example.com/job-posting"],
  "warnings": [],
  "flags": [],
  "error": null
}
```

Prefer employer apply links (e.g. `on.tcs.com`, company careers pages) over LinkedIn URLs when both appear in an alert. LinkedIn often returns a login wall to automated checks even when the page looks fine in a browser. Host rules live in [references/url_hosts.json](references/url_hosts.json).

5. Only if `valid` is `true`, scrape the page with `web_scraping.py`:

```bash
python scripts/web_scraping.py "<url>" --pretty
```

`web_scraping.py` validates the URL automatically before scraping. Do not scrape if validation fails.

If validation returns any other result, tell the user the job link is invalid and warn them not to apply for this posting. Example message:

> This job link appears invalid (HTTP status: 404). Do not apply through this posting until a working link is confirmed.

6. Compare the scraped content with the user input using `compare_job.py`:

```bash
python scripts/compare_job.py user_job.json scraped_job.json --pretty
```

- Exit code `0` means the content matches well enough to proceed.
- Exit code `1` means mismatches were found — review `summary.critical_mismatches` and report differences to the user.
- Fields the user did not provide are skipped.
- `company_name`, `job_title`, and `location` are treated as critical when the user supplied them.

For detailed comparison rules, see [references/comparison-rules.md](references/comparison-rules.md).

7. If the posting is valid, format a WhatsApp group message and present it as copy-ready text. Do not send it automatically.

```bash
python scripts/format_whatsapp.py user_job.json
```

Show the output in chat so the user can paste it into the WhatsApp group. Layout: [references/whatsapp-template.md](references/whatsapp-template.md).

When comparison succeeds, persist the validated record for resume matching:

```bash
python scripts/save_job.py user_job.json --pretty
```

Saved `*.json` files stay in `job_postings/` locally (gitignored).

`validate_job.py` and `save_job.py` include a `trust` object with **domain mismatch** and **duplicate posting** warnings. These do not block saving by default — surface them to the user before sharing a WhatsApp alert.

## Job library (local index)

List saved jobs and freshness:

```bash
python scripts/list_jobs.py --pretty
python scripts/housekeep_jobs.py --pretty
python scripts/housekeep_jobs.py --remove-stale --pretty
```

## Resume matching (sub-skill)

When the user uploads a resume, follow [resume-match/SKILL.md](resume-match/SKILL.md). Match it against jobs in `job_postings/` and skip any posting older than 15 days or missing `posted_date`.

```bash
python scripts/match_resume.py "<resume-path>" --pretty
```

## Workflow

See [references/README.md](references/README.md) for the end-to-end flow.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate_job.py` | End-to-end validate → scrape → compare → optional save / WhatsApp |
| `scripts/validate_url.py` | Check URL returns HTTP 200 |
| `scripts/web_scraping.py` | Scrape job fields from a validated URL |
| `scripts/compare_job.py` | Compare user input JSON vs scraped JSON |
| `scripts/save_job.py` | Write validated job JSON to `job_postings/` |
| `scripts/format_whatsapp.py` | Format a copy-ready WhatsApp group message |
| `scripts/match_resume.py` | Match a resume to jobs in `job_postings/` posted within 15 days |
| `scripts/list_jobs.py` | Index `job_postings/` with freshness metadata |
| `scripts/housekeep_jobs.py` | Report or remove stale / duplicate saved jobs |
