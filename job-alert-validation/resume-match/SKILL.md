---
name: resume-job-match
description: Matches an uploaded resume against jobs in job_postings/ and keeps only postings from the last 15 days. Use when the user uploads a resume or asks which listed jobs they can apply to.
---

# resume-job-match

Sub-skill of job-alert-validation. Use when the user uploads a resume (PDF or text).

## Instructions

1. Take the uploaded resume path.

2. Run the matcher against jobs in `job_postings/`:

```bash
python scripts/match_resume.py "<resume-path>" --pretty
python scripts/match_resume.py "<resume-path>" --company "Acme" --location "Bengaluru" --min-score 0.4 --limit 5 --pretty
```

3. Keep a job only when **both** are true:
- The resume fits the job (skills, title, education, experience, description overlap).
- `posted_date` is present and the posting is **not older than 15 days**.

4. Skip a job when:
- `posted_date` is missing (cannot prove it is recent).
- The posting is older than 15 days.
- The resume does not match the job well enough.

5. Show matching jobs first (company, title, apply link, score, posting age). Then list skipped jobs with the skip reason.

6. If at least one job matches, share the job details in whatsapp format.

Do not invent a posting date. If the JSON has no `posted_date`, skip that job.
