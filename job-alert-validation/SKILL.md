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

Save the restructured data as JSON for later comparison.

3. If there is a link in the input, capture the URL.

4. Confirm the link is genuine by running `validate_url.py`:

```bash
python scripts/validate_url.py "<url>" --pretty
```

Expected valid response:

```json
{
  "url": "https://example.com/job-posting",
  "valid": true,
  "status_code": 200,
  "final_url": "https://example.com/job-posting",
  "error": null
}
```

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
| `scripts/validate_url.py` | Check URL returns HTTP 200 |
| `scripts/web_scraping.py` | Scrape job fields from a validated URL |
| `scripts/compare_job.py` | Compare user input JSON vs scraped JSON |
| `scripts/format_whatsapp.py` | Format a copy-ready WhatsApp group message |
| `scripts/match_resume.py` | Match a resume to jobs in `job_postings/` posted within 15 days |
