"""Command-line interface.

Examples:
    leadgen "coffee shop" "Wichita Falls, TX" --limit 15 -o leads.csv
    leadgen "plumber" "Dallas, TX" --emails        # print outreach drafts too
"""

from __future__ import annotations

import argparse
import sys

from .outreach import draft_email
from .pipeline import export_csv, run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="leadgen",
        description="Find local businesses whose websites could use help, and draft outreach.",
    )
    parser.add_argument("niche", help='Business type, e.g. "coffee shop".')
    parser.add_argument("location", help='City/area, e.g. "Wichita Falls, TX".')
    parser.add_argument("--limit", type=int, default=10, help="Max businesses to profile.")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests.")
    parser.add_argument("-o", "--output", help="Write results to this CSV file.")
    parser.add_argument("--emails", action="store_true", help="Print an outreach draft per lead.")
    parser.add_argument("--min-score", type=int, default=0, help="Only show leads at/above this score.")
    args = parser.parse_args(argv)

    print(f"Searching for '{args.niche}' in {args.location}...", file=sys.stderr)
    leads = [ld for ld in run(args.niche, args.location, limit=args.limit, delay=args.delay)
             if ld.opportunity_score >= args.min_score]

    if not leads:
        print("No leads found.", file=sys.stderr)
        return 1

    print(f"\nFound {len(leads)} leads (highest opportunity first):\n")
    for ld in leads:
        print(f"  [{ld.opportunity_score:3d}] {ld.name:<28} {ld.url}")
        if ld.primary_email or ld.primary_phone:
            print(f"        contact: {ld.primary_email}  {ld.primary_phone}".rstrip())
        if ld.issues:
            print(f"        issues: {', '.join(ld.issues)}")

    if args.output:
        export_csv(leads, args.output)
        print(f"\nWrote {len(leads)} leads to {args.output}", file=sys.stderr)

    if args.emails:
        print("\n" + "=" * 60 + "\nOUTREACH DRAFTS\n" + "=" * 60)
        for ld in leads:
            print("\n" + draft_email(ld))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
