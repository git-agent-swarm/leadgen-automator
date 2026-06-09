"""Fetch a business website and extract contact details from its HTML.

Pure regex/string work so it has no heavy dependencies and is easy to unit-test
against fixture HTML.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import requests

_HEADERS = {"User-Agent": "leadgen-automator/0.1 (+https://gitlab.com/broussardkobey67)"}
_TIMEOUT = 15

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Phone numbers must be *formatted* (a separator between groups) or come from a
# tel: link. This deliberately avoids matching bare digit runs like unix
# timestamps and tracking IDs, which a greedy pattern would wrongly grab.
_PHONE_RE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}")
_TEL_RE = re.compile(r'tel:\s*(\+?[\d\s().\-]{7,})', re.IGNORECASE)
_SOCIAL_RE = re.compile(
    r"https?://(?:www\.)?(?:facebook|instagram|twitter|x|linkedin|youtube|tiktok)\.com/[^\s\"'<>]+",
    re.IGNORECASE,
)
# Junk that the email regex sometimes grabs from asset filenames.
_EMAIL_JUNK = re.compile(r"\.(png|jpg|jpeg|gif|svg|webp|css|js)$", re.IGNORECASE)
# Tracking/analytics/sentry addresses that are never a real business contact.
_EMAIL_BLOCK = re.compile(
    r"(wixpress\.com|sentry|@sentry|@example\.|@schema\.org|\.w3\.org|"
    r"@2x\.|@3x\.|noreply@|no-reply@|^[0-9a-f]{16,}@)",
    re.IGNORECASE,
)


@dataclass
class Page:
    url: str
    status: int
    html: str
    final_url: str


def fetch(url: str) -> Page | None:
    """GET a URL, following redirects. Returns ``None`` on network failure."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
    except requests.RequestException:
        return None
    return Page(url=url, status=resp.status_code, html=resp.text, final_url=resp.url)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        key = it.lower()
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out


def extract_emails(html: str) -> list[str]:
    found = [
        e for e in _EMAIL_RE.findall(html)
        if not _EMAIL_JUNK.search(e) and not _EMAIL_BLOCK.search(e)
    ]
    return _dedupe(found)


def extract_phones(html: str) -> list[str]:
    # tel: links are the most reliable source; formatted numbers in text next.
    candidates = _TEL_RE.findall(html) + _PHONE_RE.findall(html)
    valid = [c.strip() for c in candidates if 10 <= len(re.sub(r"\D", "", c)) <= 11]
    return _dedupe(valid)


def extract_socials(html: str) -> list[str]:
    return _dedupe(_SOCIAL_RE.findall(html))
