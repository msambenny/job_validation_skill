# Job Alert Validation Workflow

```mermaid
flowchart TD
    A[User provides job description + URL] --> B[Restructure to form fields JSON]
    B --> C[validate_url.py]
    C -->|valid: true, status 200| D[web_scraping.py]
    C -->|valid: false| E[Warn user: invalid link]
    D --> F[compare_job.py]
    F -->|matches: true| G[format_whatsapp.py]
    F -->|matches: false| H[Report mismatches to user]
    G --> I[Copy-ready WhatsApp group message]
```

## Script order

1. `validate_url.py` — always run first when a URL is present
2. `web_scraping.py` — only after validation succeeds
3. `compare_job.py` — compare restructured user JSON with scraped JSON
4. `format_whatsapp.py` — print a copy-ready WhatsApp group message (does not send)

## Example commands

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest

python scripts/validate_url.py "https://example.com/jobs/123" --pretty
python scripts/web_scraping.py "https://example.com/jobs/123" --pretty > scraped_job.json
python scripts/compare_job.py tests/fixtures/jobs/user_job.json tests/fixtures/jobs/scraped_job.json --pretty
python scripts/format_whatsapp.py tests/fixtures/jobs/user_job.json
python scripts/match_resume.py resume.pdf --pretty
```

Validated job JSON files are written locally to `job_postings/` for resume matching. They are gitignored and must not be committed. Canonical field list: [schemas/job_schema.json](../schemas/job_schema.json).
