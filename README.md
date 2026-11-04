# Free Game Night Hosting Pack

A free, printable pack for an easy family card-game night: simple house-rule
cards for classic card games, printable score sheets, a fold-away tournament
bracket, a snack-plan worksheet, tips for including younger kids and
grandparents, and an anti-meltdown wind-down checklist.

Plain English, warm tone, tested, local-first. No accounts, no tracking, no
secrets — it's just paper.

By **Asdale Dynamics, LLC** — from Dylan Asdale, author of *The Massive AI
Manual* and [dylanasdale.github.io](https://dylanasdale.github.io/).

## What's inside

| File | What it is | Pages |
|---|---|---|
| `pdfs/01_house_rule_cards.pdf` | House-rule cards for 8 classic card games (Go Fish, Crazy Eights, War, Old Maid, Memory Match, Snap, Slapjack, Quick Rummy) + a pack cover sheet | 3 |
| `pdfs/02_score_sheets.pdf` | Four score pads: round-by-round, quick tally, team/tournament, Go Fish set tracker | 2 |
| `pdfs/03_tournament_bracket.pdf` | 8-player tournament bracket + 4-player mini bracket, with dotted fold lines | 2 (landscape) |
| `pdfs/04_snack_plan_worksheet.pdf` | Snack "balance rule," shopping list, and prep timeline | 1 |
| `pdfs/05_all_ages_tips.pdf` | Tips for including younger kids and grandparents at the same table | 1 |
| `pdfs/06_wind_down_checklist.pdf` | The anti-meltdown plan: wind-down steps, early-warning responses, calm-down corner | 1 |
| `site/index.html` | Small index site linking to every PDF, with printing tips | — |

This pack is **card-games only**. It is distinct from the
*free-chess-club-kit* (chess) and the *free-party-planner-pack* (parties).

## How to print

- US Letter (8.5 × 11 in), portrait (brackets are landscape), **print at 100% scale**.
- Cardstock is nice for the rule cards; plain paper works everywhere else.
- The bracket page has a dotted fold line so the finished sheet can fold flat.

## How to view the site locally

Serve the repo root with any static server, then open the `site/` folder:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/site/
```

## How to regenerate the PDFs

The PDFs are generated (not scanned) with Python + ReportLab, using only
built-in fonts — no network access needed.

```sh
pip install reportlab
python3 scripts/generate_pdfs.py   # writes all 6 PDFs into pdfs/
python3 scripts/verify.py          # checks PDFs, site links, license, secrets
```

## Verify everything

```sh
python3 scripts/verify.py
```

Checks that all six PDFs are valid and readable, that the site links to every
PDF, that the LICENSE carries the exact Asdale Dynamics, LLC copyright line,
and that no secrets/keys are committed.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
