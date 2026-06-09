"""Score how much a business could benefit from web/automation help.

The heuristics look for concrete, defensible signals in a site's HTML — the kind
of thing you can point to in an outreach message ("I noticed your site isn't
mobile-friendly..."). A higher score means a warmer lead *for us*.
"""

from __future__ import annotations

import re
from datetime import datetime

from .scrape import Page

# Each rule: (points, human-readable issue, predicate(page) -> bool).
# Points roughly track how strong a selling point the issue is.


def _no_https(page: Page) -> bool:
    return page.final_url.startswith("http://")


def _not_mobile_friendly(page: Page) -> bool:
    return 'name="viewport"' not in page.html.lower()


def _no_meta_description(page: Page) -> bool:
    return 'name="description"' not in page.html.lower()


def _stale_copyright(page: Page, *, now_year: int | None = None) -> bool:
    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\D{0,10}(20\d{2})", page.html, re.I)]
    if not years:
        return False
    current = now_year or datetime.now().year
    return max(years) <= current - 2


def _free_site_builder(page: Page) -> bool:
    h = page.html.lower()
    return any(s in h for s in ("wix.com", "weebly.com", ".godaddysites.com", "squarespace badge"))


def _under_construction(page: Page) -> bool:
    return bool(re.search(r"under construction|coming soon|page not found", page.html, re.I))


def _no_contact_form(page: Page) -> bool:
    return "<form" not in page.html.lower() and "mailto:" not in page.html.lower()


_RULES = [
    (30, "No HTTPS / insecure site", _no_https),
    (25, "Not mobile-friendly (no viewport tag)", _not_mobile_friendly),
    (20, "Stale content (copyright 2+ years old)", _stale_copyright),
    (15, "No meta description (poor SEO)", _no_meta_description),
    (15, "Built on a free site-builder tier", _free_site_builder),
    (20, "Placeholder / under-construction content", _under_construction),
    (10, "No contact form or mailto link", _no_contact_form),
]


def evaluate(page: Page) -> tuple[int, list[str]]:
    """Return (opportunity_score capped at 100, list of issue descriptions)."""
    score = 0
    issues: list[str] = []
    for points, label, rule in _RULES:
        try:
            hit = rule(page)
        except Exception:  # a single bad rule should never sink the whole scan
            hit = False
        if hit:
            score += points
            issues.append(label)
    return min(score, 100), issues
