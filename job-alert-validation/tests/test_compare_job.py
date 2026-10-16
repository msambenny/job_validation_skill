from __future__ import annotations

import json
from pathlib import Path

from compare_job import compare_jobs

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "jobs"


def test_compare_fixture_jobs_match() -> None:
    user = json.loads((FIXTURES / "user_job.json").read_text(encoding="utf-8"))
    scraped = json.loads((FIXTURES / "scraped_job.json").read_text(encoding="utf-8"))

    result = compare_jobs(user, scraped)

    assert result["matches"] is True
    assert result["summary"]["critical_mismatches"] == []


def test_critical_mismatch_blocks_match() -> None:
    user = {"company_name": "Wrong Co", "job_title": "Backend Engineer", "location": "Bengaluru"}
    scraped = {"company_name": "Acme Labs", "job_title": "Backend Engineer", "location": "Bengaluru"}

    result = compare_jobs(user, scraped)

    assert result["matches"] is False
    assert "company_name" in result["summary"]["critical_mismatches"]


def test_salary_mismatch_is_warning_only() -> None:
    user = {
        "company_name": "Acme",
        "job_title": "Engineer",
        "location": "Remote",
        "salary_min": "10 LPA",
        "salary_max": "12 LPA",
    }
    scraped = {
        "company_name": "Acme",
        "job_title": "Engineer",
        "location": "Remote",
        "salary_min": "999999 USD",
        "salary_max": "888888 USD",
    }

    result = compare_jobs(user, scraped)

    assert result["matches"] is True
    assert "salary_min" in result["summary"]["salary_warnings"]
    assert "salary_max" in result["summary"]["salary_warnings"]


def test_skipped_fields_when_user_omits_them() -> None:
    user = {"job_title": "Designer"}
    scraped = {"job_title": "Designer", "company_name": "Acme", "location": "NYC"}

    result = compare_jobs(user, scraped)
    skipped = [item for item in result["fields"] if item["status"] == "skipped"]

    assert any(item["field"] == "company_name" for item in skipped)
    assert result["matches"] is True
