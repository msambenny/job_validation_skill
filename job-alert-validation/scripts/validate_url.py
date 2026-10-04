#!/usr/bin/env python3
"""Validate that a job posting URL is reachable and returns HTTP 200."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlparse

import requests

DEFAULT_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def validate_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {
            "url": url,
            "valid": False,
            "status_code": None,
            "final_url": None,
            "error": f"Invalid URL: {url}",
        }

    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}

    try:
        response = requests.head(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
        )

        # Some servers reject HEAD; fall back to GET only for that case.
        if response.status_code in {405, 501}:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                stream=True,
            )
            response.close()

        status_code = response.status_code
        return {
            "url": url,
            "valid": status_code == 200,
            "status_code": status_code,
            "final_url": response.url,
            "error": None if status_code == 200 else f"Expected status 200, got {status_code}",
        }
    except requests.RequestException as exc:
        return {
            "url": url,
            "valid": False,
            "status_code": None,
            "final_url": None,
            "error": f"Failed to reach URL: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether a URL is reachable and returns HTTP 200."
    )
    parser.add_argument("url", help="URL to validate")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    result = validate_url(args.url, timeout=args.timeout)
    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
