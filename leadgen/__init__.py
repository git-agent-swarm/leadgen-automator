"""leadgen-automator: find local businesses that need web help and draft outreach."""

from .models import CSV_FIELDS, Lead
from .outreach import draft_email
from .pipeline import build_lead, export_csv, run
from .score import evaluate

__all__ = ["Lead", "CSV_FIELDS", "run", "build_lead", "export_csv", "evaluate", "draft_email"]
__version__ = "0.1.0"
