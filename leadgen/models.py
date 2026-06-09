"""Core data types shared across the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Lead:
    """A prospective business lead and everything we learn about it."""

    name: str
    url: str
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    socials: list[str] = field(default_factory=list)
    # Findings that signal the business could use web/automation help.
    issues: list[str] = field(default_factory=list)
    opportunity_score: int = 0

    @property
    def primary_email(self) -> str:
        return self.emails[0] if self.emails else ""

    @property
    def primary_phone(self) -> str:
        return self.phones[0] if self.phones else ""

    def as_row(self) -> dict[str, str]:
        """Flatten to a CSV-friendly record."""
        return {
            "name": self.name,
            "url": self.url,
            "opportunity_score": str(self.opportunity_score),
            "email": self.primary_email,
            "phone": self.primary_phone,
            "issues": "; ".join(self.issues),
            "socials": " ".join(self.socials),
        }


CSV_FIELDS = ["name", "url", "opportunity_score", "email", "phone", "issues", "socials"]
