# leadgen-automator

A command-line tool that **finds local businesses whose websites could use help,
scores the opportunity, and drafts personalized outreach** — the boring,
repetitive top of a freelance/agency sales funnel, automated.

Point it at a niche and a city. It searches for real businesses, visits each
site, pulls out contact details, and flags concrete weaknesses (no HTTPS, not
mobile-friendly, stale content, weak SEO). You get a ranked CSV of warm leads
and a ready-to-send email for each one.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-pytest-brightgreen)
![Dependencies](https://img.shields.io/badge/deps-requests-lightgrey)

## Example

```bash
$ leadgen "coffee shop" "Wichita Falls, TX" --limit 6

Found 5 leads (highest opportunity first):

  [ 35] Frank And Joes Coffee        https://frankandjoescoffee.example/
        contact: hello@frankandjoes.example  (940) 555-0142
        issues: Stale content (copyright 2+ years old), No contact form or mailto link
  [ 30] Corner Cafe                  https://cornercafe.example/
        issues: Built on a free site-builder tier, No meta description (poor SEO)
  ...
```

Add `-o leads.csv` to save the table ([example output](examples/sample_leads.csv))
and `--emails` to print a tailored draft per lead:

```
Subject: Quick note about Smith Family Plumbing's website

Hi Smith Family Plumbing team,

I came across your website and noticed your site is still served over an insecure
connection, which browsers now flag to visitors with a 'Not secure' warning. ...
```

## Why it's useful

Most freelance/agency time is lost finding and qualifying prospects. This
automates the qualification: instead of a generic list, you get businesses
ranked by **how clearly they need help**, with the specific reason attached — so
your outreach can open with something true and specific instead of spam.

## How the scoring works

Each site is checked against a set of weighted heuristics. Every hit adds points
and a human-readable reason you can quote in outreach:

| Signal | Points | Why it matters |
|---|---|---|
| No HTTPS | 30 | Browsers show a "Not secure" warning to visitors |
| Not mobile-friendly | 25 | Most local searches happen on phones |
| Under-construction / placeholder | 20 | Site isn't doing its job |
| Stale content (copyright 2+ yrs old) | 20 | Signals neglect |
| No meta description | 15 | Hurts Google ranking |
| Free site-builder tier | 15 | Ads + slow load for customers |
| No contact form / mailto | 10 | Lost conversions |

Score is capped at 100; leads are returned highest-first.

## Install

```bash
git clone https://gitlab.com/broussardkobey67/leadgen-automator.git
cd leadgen-automator
pip install -r requirements.txt     # just `requests`
```

## Usage

```bash
leadgen "<niche>" "<city, state>" [--limit N] [--min-score N] [-o leads.csv] [--emails]

# Examples
leadgen "plumber" "Dallas, TX" --limit 20 --min-score 30 -o plumbers.csv
leadgen "dentist" "Austin, TX" --emails
python -m leadgen "auto repair" "Wichita Falls, TX"
```

Use it as a library:

```python
from leadgen import run, export_csv, draft_email

leads = run("coffee shop", "Wichita Falls, TX", limit=10)
export_csv(leads, "leads.csv")
print(draft_email(leads[0]))
```

## Project structure

```
leadgen/
├── discover.py   # find business sites for a niche+city (keyless search)
├── scrape.py     # fetch a site; extract emails / phones / socials
├── score.py      # weighted "does this business need help?" heuristics
├── outreach.py   # turn a scored lead into a tailored email
├── pipeline.py   # discover → scrape → score → CSV
├── models.py     # the Lead data model
└── cli.py        # argparse entry point
tests/            # offline tests against fixture HTML (6 tests)
```

## Design notes

- **Polite by default.** One request per site with a real User-Agent and a
  configurable delay between fetches — it won't hammer small-business hosts.
- **Defensible signals only.** Every issue maps to something you can show the
  business owner, which keeps outreach honest and specific.
- **Tuned extraction.** Phone matching requires real formatting or `tel:` links
  (so timestamps/IDs aren't mistaken for numbers), and emails filter out
  analytics/tracking addresses.
- **No API keys.** Search and scraping are keyless; the outreach templates work
  offline. (An LLM can be dropped into `outreach.py` for more variety.)

## Public Proof Context

Built by Kobey Dev Services as a practical lead-generation and outreach proof.

- Portfolio: https://kobeydev.com
- GitHub org: https://github.com/git-agent-swarm
- Google Developer profile: https://me.developers.google.com/u/116492041557080639666

## License

MIT © Kobey Broussard
