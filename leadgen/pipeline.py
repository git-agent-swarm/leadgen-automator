"""Glue: discover -> scrape -> score -> build Leads, and export helpers."""

from __future__ import annotations

import csv
import time
from urllib.parse import urlparse

from .discover import discover
from .models import CSV_FIELDS, Lead
from .scrape import extract_emails, extract_phones, extract_socials, fetch
from .score import evaluate


def _name_from_url(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host.split(".")[0].replace("-", " ").title() if host else url


def build_lead(url: str) -> Lead | None:
    """Fetch one site and turn it into a scored Lead. ``None`` if unreachable."""
    page = fetch(url)
    if page is None or page.status >= 400:
        return None
    score, issues = evaluate(page)
    return Lead(
        name=_name_from_url(page.final_url),
        url=page.final_url,
        emails=extract_emails(page.html),
        phones=extract_phones(page.html),
        socials=extract_socials(page.html),
        issues=issues,
        opportunity_score=score,
    )


def run(niche: str, location: str, *, limit: int = 10, delay: float = 1.0) -> list[Lead]:
    """Full pipeline: find businesses, profile each, return leads worst-site-first."""
    urls = discover(niche, location, limit=limit)
    leads: list[Lead] = []
    for url in urls:
        lead = build_lead(url)
        if lead is not None:
            leads.append(lead)
        time.sleep(delay)  # be polite; don't hammer small business hosts
    leads.sort(key=lambda ld: ld.opportunity_score, reverse=True)
    return leads


def export_csv(leads: list[Lead], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead.as_row())
