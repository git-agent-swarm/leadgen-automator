"""Offline tests for extraction, scoring, and outreach.

All fixtures are inline HTML strings, so the suite needs no network access.
Run with: ``pytest``
"""

from __future__ import annotations

from leadgen.models import Lead
from leadgen.outreach import draft_email
from leadgen.scrape import Page, extract_emails, extract_phones, extract_socials
from leadgen.score import evaluate

GOOD_SITE = """
<html><head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Best coffee in town">
</head><body>
  <p>Email us at hello@bluebottle.example or call (940) 555-0192.</p>
  <a href="https://facebook.com/bluebottle">Facebook</a>
  <form action="/contact"><input name="email"></form>
  <footer>&copy; 2026 Blue Bottle</footer>
</body></html>
"""

BAD_SITE = """
<html><head><title>Joe Plumbing</title></head><body>
  <p>Coming soon! Contact joe@joeplumbing.example</p>
  <footer>Copyright 2019 Joe Plumbing. Built with Wix.com</footer>
</body></html>
"""


def _page(html: str, url: str = "https://example.com") -> Page:
    return Page(url=url, status=200, html=html, final_url=url)


def test_extract_emails_filters_assets():
    html = "contact: a@b.example and logo@2x.png and x@y.co.uk"
    emails = extract_emails(html)
    assert "a@b.example" in emails
    assert "x@y.co.uk" in emails
    assert all(not e.endswith(".png") for e in emails)


def test_extract_phones_accepts_common_formats():
    html = "(940) 555-0192 or 214.555.7788 or +1 555 123 4567"
    phones = extract_phones(html)
    assert len(phones) == 3


def test_extract_socials():
    html = '<a href="https://instagram.com/shop">ig</a> <a href="https://x.com/shop">x</a>'
    socials = extract_socials(html)
    assert any("instagram.com" in s for s in socials)
    assert any("x.com" in s for s in socials)


def test_good_site_scores_low():
    score, issues = evaluate(_page(GOOD_SITE, "https://bluebottle.example"))
    assert score == 0
    assert issues == []


def test_bad_site_scores_high_and_flags_issues(monkeypatch):
    # Pin "now" so the stale-copyright rule is deterministic.
    import leadgen.score as score_mod

    class _FixedDate:
        @staticmethod
        def now():
            class _N:
                year = 2026
            return _N()

    monkeypatch.setattr(score_mod, "datetime", _FixedDate)
    score, issues = evaluate(_page(BAD_SITE, "http://joeplumbing.example"))
    assert score >= 60
    assert any("HTTPS" in i for i in issues)
    assert any("mobile" in i.lower() for i in issues)


def test_draft_email_is_personalized():
    # evaluate() emits issues in rule-weight order, so HTTPS leads.
    lead = Lead(
        name="Joe Plumbing",
        url="http://joeplumbing.example",
        issues=["No HTTPS / insecure site", "Not mobile-friendly (no viewport tag)"],
    )
    email = draft_email(lead)
    assert "Joe Plumbing" in email
    assert "insecure connection" in email  # pitches the top (highest-weight) issue
