# STATUS — Free Game Night Hosting Pack

Last updated: 2026-11-04
Maintained by: Asdale Dynamics, LLC

## What was built

A free, printable pack for an easy family card-game night. Six print-ready PDFs
(US Letter), a small static index site that links them together, plus the
scripts that generate and verify everything:

| Deliverable | File | Contents |
|---|---|---|
| House-rule cards | `pdfs/01_house_rule_cards.pdf` | Rules + playful tweaks for 8 classic card games (Go Fish, Crazy Eights, War, Old Maid, Memory Match, Snap, Slapjack, Quick Rummy) as cut-out cards, plus a pack cover sheet. 3 pages. |
| Score sheets | `pdfs/02_score_sheets.pdf` | Round-by-round sheet, quick score pad, team/tournament sheet, Go Fish set tracker. 2 pages. |
| Tournament bracket | `pdfs/03_tournament_bracket.pdf` | 8-player bracket + 4-player "mini bracket" with small-table rules and a dotted fold line. 2 pages, landscape. |
| Snack-plan worksheet | `pdfs/04_snack_plan_worksheet.pdf` | Snack "balance rule," lineup + allergy-check fields, shopping list, prep timeline. 1 page. |
| All-ages tips | `pdfs/05_all_ages_tips.pdf` | Practical tips for including younger kids and grandparents at the same table. 1 page. |
| Wind-down checklist | `pdfs/06_wind_down_checklist.pdf` | Anti-meltdown plan: end-of-night steps, early-warning responses, calm-down corner, after-the-table cleanup. 1 page. |
| Index site | `site/index.html` | Self-contained page (inline CSS, no external assets) describing the pack and linking each PDF. |
| Generator | `scripts/generate_pdfs.py` | Rebuilds all six PDFs with Python + ReportLab (built-in fonts only; offline). |
| Verifier | `scripts/verify.py` | 57 checks over PDFs, site links, license, credit lines, secrets scan, and a clean re-generate run. |
| License | `LICENSE` | MIT, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC`. |

Scope note: this pack is card-games only — distinct from the free-chess-club-kit
(chess) and the free-party-planner-pack (parties).

## How to run it

Everything is local-first; nothing phones home and no data is collected.

```sh
# Regenerate the PDFs (requires reportlab + pypdf)
pip install reportlab pypdf
python3 scripts/generate_pdfs.py

# Verify the whole pack
python3 scripts/verify.py

# Browse the index site (serve the repo root, then open site/)
python3 -m http.server 8000
# open http://localhost:8000/site/
```

## Verification results

- `scripts/verify.py` — **all 57 checks pass**:
  - Each PDF exists, starts with `%PDF`, ends with `%%EOF`, parses with pypdf,
    has the expected page count and orientation, and carries the
    "Asdale Dynamics, LLC" credit on page 1.
  - The site links to all six PDFs and the links resolve on disk.
  - `LICENSE` contains the exact line `Copyright (c) 2026 Asdale Dynamics, LLC`.
  - README, site, and footer credit Asdale Dynamics, LLC.
  - Automated scan finds no secrets, API keys, or personal-data files.
  - `generate_pdfs.py` reruns cleanly from scratch (exit 0).
- Every PDF page was also rendered to PNG and visually reviewed for layout
  issues (overlaps, misaligned checkboxes, split-table headers); all found
  issues were fixed and re-verified.
- Site + PDFs were served over a local HTTP server (all requests returned 200).

## Known gaps

- Score sheets are fill-by-pencil by design; there is no interactive
  (fillable-form) PDF variant yet.
- One page per worksheet: big families may want duplicate copies of the snack
  plan and checklist.
- The bracket covers 8 and 4 players; a 16-player bracket could be added later.
- The site is a single page; no search or per-game deep-link pages.
- Fonts are ReportLab's built-in Helvetica family; a friendlier embeddable
  typeface could improve the look further.

## Notes

- No secrets, API keys, or personal data are stored in the repo (verified).
- Git repo initialized locally; nothing is pushed, published, or hosted.
- MIT License applies; contributions and house-rule remixes are welcome.
