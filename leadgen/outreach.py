"""Turn a scored lead into a short, personalized outreach email.

Template-based so it runs with zero API keys. The message references the single
most compelling issue found on the site, which makes the outreach specific
instead of generic spam. (You can swap in an LLM here for more variety.)"""

from __future__ import annotations

from .models import Lead

# Map an issue to a benefit-led sentence we can lead with.
_ISSUE_PITCH = {
    "No HTTPS / insecure site": (
        "your site is still served over an insecure connection, which browsers "
        "now flag to visitors with a 'Not secure' warning"
    ),
    "Not mobile-friendly (no viewport tag)": (
        "your site doesn't appear to be optimized for phones — and most local "
        "customers are searching on mobile"
    ),
    "Stale content (copyright 2+ years old)": (
        "a few things on the site look like they haven't been updated in a "
        "couple of years"
    ),
    "No meta description (poor SEO)": (
        "the site is missing some basic SEO tags, which makes it harder to find "
        "on Google"
    ),
    "Built on a free site-builder tier": (
        "the site looks like it's on a free builder plan, which usually means "
        "ads and a slower experience for your customers"
    ),
    "Placeholder / under-construction content": (
        "part of the site still shows placeholder content"
    ),
    "No contact form or mailto link": (
        "there's no easy way for a visitor to contact you directly from the site"
    ),
}

_TEMPLATE = """Subject: Quick note about {name}'s website

Hi {name} team,

I came across your website and noticed {pitch}. That's a quick fix, and it's
usually the difference between a visitor reaching out and bouncing.

I help local businesses with fast, mobile-friendly sites and simple automation
(online booking, contact forms, follow-up emails). If it's useful, I'd be happy
to send over a couple of specific suggestions — no obligation.

Would a 10-minute call this week work?

Best,
Kobey
"""


def draft_email(lead: Lead) -> str:
    pitch = "a couple of things that could be bringing in more customers"
    for issue in lead.issues:  # issues are already ordered by rule weight
        if issue in _ISSUE_PITCH:
            pitch = _ISSUE_PITCH[issue]
            break
    return _TEMPLATE.format(name=lead.name, pitch=pitch)
