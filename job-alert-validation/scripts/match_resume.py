#!/usr/bin/env python3
"""Match an uploaded resume against jobs in job_postings/, skipping posts older than 15 days."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

MAX_AGE_DAYS = 15
MATCH_THRESHOLD = 0.35
STOPWORDS = {
    "the", "and", "for", "with", "from", "this", "that", "your", "you", "are",
    "was", "were", "have", "has", "had", "job", "role", "team", "work",
}


def load_jobs(jobs_dir: Path) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for path in sorted(jobs_dir.glob("*.json")):
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            continue
        payload["_source_file"] = str(path)
        jobs.append(payload)
    return jobs


def read_resume(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install pypdf to parse PDF resumes: pip install pypdf") from exc
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]{1,}", text.lower())
    return {word for word in words if word not in STOPWORDS and len(word) > 2}


def parse_posted_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    match = re.search(r"(\d{4}-\d{2}-\d{2})", str(value))
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    return None


def posting_freshness(job: dict[str, Any], today: date, max_age_days: int) -> dict[str, Any]:
    posted = parse_posted_date(job.get("posted_date") or job.get("posting_date"))
    if posted is None:
        return {
            "fresh": False,
            "posted_date": job.get("posted_date") or "",
            "age_days": None,
            "reason": "Missing posted_date; cannot confirm the posting is within 15 days",
        }
    age_days = (today - posted).days
    if age_days < 0:
        return {
            "fresh": True,
            "posted_date": posted.isoformat(),
            "age_days": age_days,
            "reason": "Posting date is in the future",
        }
    if age_days > max_age_days:
        return {
            "fresh": False,
            "posted_date": posted.isoformat(),
            "age_days": age_days,
            "reason": f"Posted {age_days} days ago (limit is {max_age_days} days)",
        }
    return {
        "fresh": True,
        "posted_date": posted.isoformat(),
        "age_days": age_days,
        "reason": f"Posted {age_days} days ago",
    }


def job_blob(job: dict[str, Any]) -> str:
    skills = job.get("skills") or []
    if isinstance(skills, list):
        skill_text = " ".join(str(item) for item in skills)
    else:
        skill_text = str(skills)
    parts = [
        job.get("job_title"),
        job.get("department"),
        job.get("education"),
        job.get("experience"),
        job.get("description"),
        skill_text,
    ]
    return " ".join(str(part) for part in parts if part)


def score_resume_against_job(resume_text: str, job: dict[str, Any]) -> dict[str, Any]:
    resume_tokens = tokenize(resume_text)
    job_tokens = tokenize(job_blob(job))
    overlap = sorted(resume_tokens & job_tokens)

    title = str(job.get("job_title") or "").strip()
    title_tokens = tokenize(title)
    title_score = (
        len(title_tokens & resume_tokens) / max(len(title_tokens), 1) if title_tokens else 0.0
    )

    skill_score = (len(overlap) / max(len(job_tokens), 1)) if job_tokens else 0.0
    score = round(min(1.0, (0.55 * skill_score) + (0.45 * title_score)), 2)
    applies = score >= MATCH_THRESHOLD or len(title_tokens & resume_tokens) >= 2

    return {
        "applies": applies,
        "score": score,
        "matched_terms": overlap[:20],
        "job_title": title,
        "company_name": job.get("company_name") or "",
    }


def match_resume(
    resume_path: Path,
    jobs_dir: Path,
    *,
    today: date | None = None,
    max_age_days: int = MAX_AGE_DAYS,
) -> dict[str, Any]:
    today = today or date.today()
    resume_text = read_resume(resume_path)
    if not resume_text.strip():
        raise ValueError(f"No text extracted from resume: {resume_path}")

    matches: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for job in load_jobs(jobs_dir):
        freshness = posting_freshness(job, today, max_age_days)
        result = {
            "source_file": job.get("_source_file"),
            "company_name": job.get("company_name") or "",
            "job_title": job.get("job_title") or "",
            "apply_link": job.get("apply_link") or "",
            "freshness": freshness,
        }
        if not freshness["fresh"]:
            skipped.append(result)
            continue
        scored = score_resume_against_job(resume_text, job)
        result.update(scored)
        if scored["applies"]:
            matches.append(result)
        else:
            result["reason"] = "Resume does not match this job well enough"
            skipped.append(result)

    matches.sort(key=lambda item: item.get("score", 0), reverse=True)
    return {
        "resume": str(resume_path),
        "jobs_dir": str(jobs_dir),
        "today": today.isoformat(),
        "max_age_days": max_age_days,
        "match_count": len(matches),
        "matches": matches,
        "skipped": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find jobs in job_postings/ that fit a resume and were posted within 15 days."
    )
    parser.add_argument("resume", help="Path to resume (.pdf, .txt, .md)")
    parser.add_argument(
        "--jobs-dir",
        default=str(Path(__file__).resolve().parents[1] / "job_postings"),
        help="Folder of job JSON files (default: job_postings/)",
    )
    parser.add_argument("--max-age-days", type=int, default=MAX_AGE_DAYS)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    try:
        result = match_resume(
            Path(args.resume),
            Path(args.jobs_dir),
            max_age_days=args.max_age_days,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent, ensure_ascii=False))
    return 0 if result["match_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
