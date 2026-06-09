"""Discover candidate business websites for a niche + location.

Uses DuckDuckGo's HTML endpoint (no API key) and filters out the usual
directory/aggregator domains so you're left with actual business sites.
"""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse

import requests

_HEADERS = {"User-Agent": "leadgen-automator/0.1 (+https://gitlab.com/broussardkobey67)"}
_TIMEOUT = 15

# Aggregators/directories that aren't themselves leads.
_SKIP_DOMAINS = {
    "yelp.com", "facebook.com", "instagram.com", "tripadvisor.com", "yellowpages.com",
    "mapquest.com", "google.com", "bing.com", "duckduckgo.com", "wikipedia.org",
    "linkedin.com", "indeed.com", "angi.com", "thumbtack.com", "bbb.org",
}


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        a = dict(attrs)
        if "result__a" in (a.get("class") or ""):
            href = a.get("href") or ""
            target = _unwrap(href)
            if target:
                self.links.append(target)


def _unwrap(href: str) -> str:
    parsed = urlparse(href)
    if parsed.path.startswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg")
        if uddg:
            return uddg[0]
    return href if href.startswith("http") else ""


def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def discover(niche: str, location: str, *, limit: int = 10) -> list[str]:
    """Return up to ``limit`` distinct business homepage URLs."""
    query = f"{niche} in {location}"
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers=_HEADERS,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    parser = _LinkParser()
    parser.feed(resp.text)

    out: list[str] = []
    seen: set[str] = set()
    for link in parser.links:
        dom = _domain(link)
        if not dom or dom in _SKIP_DOMAINS or dom in seen:
            continue
        seen.add(dom)
        out.append(f"{urlparse(link).scheme}://{urlparse(link).netloc}")
        if len(out) >= limit:
            break
    return out
