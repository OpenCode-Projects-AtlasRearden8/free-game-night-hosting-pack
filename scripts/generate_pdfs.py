#!/usr/bin/env python3
"""Generate the printable PDFs for the Free Game Night Hosting Pack.

Everything is drawn with ReportLab's built-in fonts, so the output is
fully self-contained: no downloads, no network, no secrets.

Copyright (c) 2026 Asdale Dynamics, LLC
"""

from __future__ import annotations

import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT, "pdfs")

PAGE_W, PAGE_H = letter  # 612 x 792 pt
MARGIN = 0.75 * inch

NAVY = colors.HexColor("#1F2A44")
AMBER = colors.HexColor("#E8A13D")
CORAL = colors.HexColor("#E0705C")
SAGE = colors.HexColor("#5F8A5B")
CREAM = colors.HexColor("#FDF6EC")
INK = colors.HexColor("#333333")
LIGHT_INK = colors.Color(0.45, 0.45, 0.45)

CREDIT = "Free Game Night Hosting Pack  |  Asdale Dynamics, LLC"


# --------------------------------------------------------------------------
# Shared drawing helpers
# --------------------------------------------------------------------------

def wrap_text(c: pdfcanvas.Canvas, text: str, font: str, size: float, width: float) -> list[str]:
    """Greedy word-wrap for canvas-drawn text."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if pdfmetrics.stringWidth(trial, font, size) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines_text(
    c: pdfcanvas.Canvas,
    text: str,
    x: float,
    y_top: float,
    width: float,
    font: str = "Helvetica",
    size: float = 10,
    leading: float = 14,
    align: str = "left",
) -> float:
    """Draw wrapped text starting at y_top; return the y of the last baseline."""
    y = y_top - size
    for line in wrap_text(c, text, font, size, width):
        if align == "center":
            c.drawCentredString(x + width / 2, y, line)
        else:
            c.drawString(x, y, line)
        y -= leading
    return y + leading


def draw_footer(c: pdfcanvas.Canvas, page_label: str = "") -> None:
    c.setFont("Helvetica", 7.5)
    c.setFillColor(LIGHT_INK)
    c.drawCentredString(
        PAGE_W / 2,
        0.42 * inch,
        f"{CREDIT}   |   {page_label}   |   Print at 100% on US Letter",
    )


def center_footer_landscape(c: pdfcanvas.Canvas, page_label: str = "") -> None:
    c.setFont("Helvetica", 7.5)
    c.setFillColor(LIGHT_INK)
    c.drawCentredString(
        landscape(letter)[0] / 2,
        0.4 * inch,
        f"{CREDIT}   |   {page_label}",
    )


def title_banner(c: pdfcanvas.Canvas, kicker: str, title: str, subtitle: str = "") -> None:
    """Cream banner with a thick navy bar at the very top of a portrait page."""
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 0.35 * inch, PAGE_W, 0.35 * inch, stroke=0, fill=1)
    c.setFillColor(AMBER)
    c.rect(0, PAGE_H - 0.42 * inch, PAGE_W, 0.07 * inch, stroke=0, fill=1)

    y = PAGE_H - 0.95 * inch
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(SAGE)
    c.drawString(MARGIN, y, kicker.upper())
    y -= 24
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(NAVY)
    c.drawString(MARGIN, y, title)
    if subtitle:
        y -= 20
        c.setFont("Helvetica-Oblique", 10.5)
        c.setFillColor(INK)
        c.drawString(MARGIN, y, subtitle)


def section_header(c: pdfcanvas.Canvas, x: float, y: float, text: str, width: float) -> float:
    c.setFillColor(CREAM)
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.2)
    c.roundRect(x, y - 22, width, 24, 6, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(NAVY)
    c.drawString(x + 10, y - 14, text)
    return y - 34


def checkbox(c: pdfcanvas.Canvas, x: float, y: float, size: float = 12) -> None:
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.roundRect(x, y - size, size, size, 2.5, stroke=1, fill=0)


def fill_line(c: pdfcanvas.Canvas, x: float, y: float, width: float) -> None:
    c.setStrokeColor(colors.HexColor("#9AA3B2"))
    c.setLineWidth(0.9)
    c.line(x, y, x + width, y)


def blank_field(c: pdfcanvas.Canvas, label: str, x: float, y: float, width: float) -> float:
    """A 'Label: ____________' field. Returns the next y."""
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString(x, y, label)
    label_w = pdfmetrics.stringWidth(label, "Helvetica-Bold", 10)
    fill_line(c, x + label_w + 8, y - 1.5, width - label_w - 8)
    return y - 20


# --------------------------------------------------------------------------
# Doc 01 - House rule cards (case, cut-out cards)
# --------------------------------------------------------------------------

FEATURED_GAMES = [
    {
        "name": "Go Fish",
        "goal": "Collect the most sets of 4 matching ranks (four 7s, four kings...).",
        "setup": "Deal 5 cards each (7 cards if 2 players). Rest is the 'pond'.",
        "rules": [
            "Ask anyone: 'Got any 5s?' - you must hold a 5 to ask for 5s.",
            "No match? 'Go fish!' Draw from the pond; your turn continues if you draw what you asked for.",
            "Completed sets go face-up for everyone to admire.",
        ],
        "tweak": "Easier: ask for matching colors, not ranks. Wilder: winner of each set takes another turn.",
    },
    {
        "name": "Crazy Eights",
        "goal": "Be first to empty your hand.",
        "setup": "Deal 5 cards each. Flip one card up as the discard pile.",
        "rules": [
            "Match the top card's suit or rank; eights are wild (pick the new suit).",
            "Stuck? Draw from the deck - our house rule: draw once, then play or pass.",
            "Play a 2 to make the next player draw 2 (stacks of fun, stacks optional by vote).",
        ],
        "tweak": "Easier: deal 3 cards and keep rules visible. Wilder: play a Queen to skip the next player.",
    },
    {
        "name": "War",
        "goal": "Win all the cards.",
        "setup": "Deal the whole deck evenly, face down. No peeking!",
        "rules": [
            "Everyone flips their top card at once; highest rank takes the pile. Aces high.",
            "Tie? 'War!' - flip one face-down, then one face-up; winner takes all.",
            "Play quick rounds: first to win 3 battles rests while others finish.",
        ],
        "tweak": "Shorter: play half the deck, count wins. Cooler: lowest card wins that round.",
    },
    {
        "name": "Old Maid",
        "goal": "Make pairs - and don't get stuck with the lone Queen.",
        "setup": "Remove one Queen from the deck. Deal all cards out.",
        "rules": [
            "Discard pairs as you get them, face-up.",
            "Hold your cards fanned out; each player draws one blind from the next hand.",
            "New pair? Lay it down happily. First to empty their hand wins the round.",
        ],
        "tweak": "Kindness rule: 'a fair warning' - before drawing you may ask 'any pairs left?' and peek at only one card.",
    },
    {
        "name": "Memory Match",
        "goal": "Find matching pairs. Sharpest memory wins.",
        "setup": "Use half a deck (24-28 cards). Lay out in a grid, face down.",
        "rules": [
            "Flip exactly 2 cards per turn, then flip them back if they don't match.",
            "A matched pair stays face-up and earns you another turn.",
            "No coaching from the peanut gallery - loving 'hmms' only.",
        ],
        "tweak": "Easier: fewer cards or a 10-second 'photo peek'. Harder: ban taking notes!",
    },
    {
        "name": "Snap",
        "goal": "Win the pile by spotting matching ranks first.",
        "setup": "Deal all cards face down (no peeking).",
        "rules": [
            "Players take turns flipping onto their own face-up pile.",
            "Top cards match on any pile? First to shout 'SNAP!' wins those piles.",
            "Agree a gentle volume: 'restaurant snap' voice, not stadium snap.",
        ],
        "tweak": "Slow mode: only your own two piles can snap. Kids mode: adults count to 3 before anyone snaps.",
    },
    {
        "name": "Slapjack",
        "goal": "Win all cards by slapping the Jack... politely.",
        "setup": "Deal the whole deck face down.",
        "rules": [
            "Flip cards onto one center pile in turn.",
            "A Jack appears? First hand on the pile wins it.",
            "House rule: flat-hand only, gentle slaps, no sliding tackles.",
        ],
        "tweak": "Add a second target card (like 7s) for extra suspense in a big group.",
    },
    {
        "name": "Quick Rummy",
        "goal": "Be first to lay down a 3-card set (rummy) and go out.",
        "setup": "Deal 7 cards each. Flip one for the discard pile; one draw, one discard per turn.",
        "rules": [
            "Draw from deck or top discard; end every turn by discarding one.",
            "Sets = same rank. Runs = 3 in a row, same suit.",
            "First to assemble one set lays it down and wins the round.",
        ],
        "tweak": "Two-set goal for longer nights; 'open hands' mode so a helper can coach a learner.",
    },
]

CARD_W, CARD_H = 256.0, 300.0
CARD_COLS, CARD_ROWS = 2, 2
CARD_GAP_X = 30.0
CARD_GAP_Y = 34.0
GRID_W = CARD_COLS * CARD_W + (CARD_COLS - 1) * CARD_GAP_X
START_X = (PAGE_W - GRID_W) / 2
START_Y = PAGE_H - MARGIN - 60


def draw_dice(c: pdfcanvas.Canvas, x: float, y: float, size: float) -> None:
    c.setStrokeColor(CORAL)
    c.setLineWidth(1.2)
    c.roundRect(x, y, size, size, 4, stroke=1, fill=0)
    p = size / 4
    for (dx, dy) in [(p, p), (size - p, size - p), (size - p, p), (p, size - p), (size / 2, size / 2)]:
        c.circle(x + dx, y + dy, 1.6, stroke=0, fill=1)


def draw_game_card(c: pdfcanvas.Canvas, x: float, y: float, game: dict) -> None:
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.4)
    c.setFillColor(colors.white)
    c.roundRect(x, y, CARD_W, CARD_H, 10, stroke=1, fill=1)

    c.setFillColor(NAVY)
    c.roundRect(x, y + CARD_H - 42, CARD_W, 42, 10, stroke=0, fill=1)
    c.rect(x, y + CARD_H - 42, CARD_W, 20, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H - 28, game["name"])
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H - 38, "house rule card")

    ty = y + CARD_H - 54
    inner_x = x + 12
    inner_w = CARD_W - 24

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(SAGE)
    c.drawString(inner_x, ty, "GOAL")
    ty = draw_lines_text(c, game["goal"], inner_x + 42, ty + 10, inner_w - 42, "Helvetica", 8.2, 10.4) - 12

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(SAGE)
    c.drawString(inner_x, ty, "SETUP")
    ty = draw_lines_text(c, game["setup"], inner_x + 42, ty + 10, inner_w - 42, "Helvetica", 8.2, 10.4) - 12

    c.setFillColor(NAVY)
    c.drawCentredString(x + CARD_W / 2, ty, "OUR HOUSE RULES")
    ty -= 12
    c.setFont("Helvetica", 8.2)
    c.setFillColor(INK)
    for rule in game["rules"]:
        lines = wrap_text(c, rule, "Helvetica", 8.2, inner_w - 12)
        first = True
        for line in lines:
            if first:
                c.setFillColor(CORAL)
                c.setFont("Helvetica-Bold", 8.2)
                c.drawString(inner_x + 2, ty - 8.2, "*")
                c.setFillColor(INK)
                c.setFont("Helvetica", 8.2)
            c.drawString(inner_x + 12, ty - 8.2, line)
            ty -= 10.4
            first = False
    ty -= 4

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(CORAL)
    ty = draw_lines_text(c, "Tweak it: " + game["tweak"], inner_x, ty, inner_w, "Helvetica-Oblique", 8, 10.4) - 6

    draw_dice(c, x + 10, y + 8, 14)
    c.setFont("Helvetica", 7)
    c.setFillColor(LIGHT_INK)
    c.drawString(x + 30, y + 12, "Circle the rules your table adopts")


def house_rule_cards() -> None:
    path = os.path.join(PDF_DIR, "01_house_rule_cards.pdf")
    c = pdfcanvas.Canvas(path, pagesize=letter)

    title_banner(
        c,
        "Eight classics, one friendly rulebook",
        "House Rule Cards",
        "Print on cardstock, cut along the dashed lines, and keep them in the card box.",
    )
    c.setFont("Helvetica", 10)
    c.setFillColor(INK)
    intro = wrap_text(
        c,
        "Picking house rules together is half the fun. These eight classics come with gentle, "
        "family-tested rules for keeping games quick, kind, and winnable by everyone. Mark which "
        "ones your table adopts, and write your own tweaks on the back before you laminate them.",
        "Helvetica",
        10,
        PAGE_W - 2 * MARGIN,
    )
    y = PAGE_H - 2.35 * inch
    for line in intro:
        c.drawString(MARGIN, y, line)
        y -= 14

    # TOC list of games
    y -= 6
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString(MARGIN, y, "Inside:")
    y -= 16
    c.setFont("Helvetica", 10)
    c.setFillColor(INK)
    for i, g in enumerate(FEATURED_GAMES, start=1):
        c.drawString(MARGIN + 12, y, f"{i}. {g['name']}  -  {g['goal'][:60]}...")
        y -= 15

    y -= 4
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(CORAL)
    c.drawString(MARGIN, y - 8, "Want the whole pack? It lives with your other favorites:")

    # compact pack inventory box fills the cover bottom
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.2)
    c.setFillColor(CREAM)
    box_top = y - 24
    items = [
        ("01", "House Rule Cards - this file"),
        ("02", "Score Sheets - four pads for every scoring style"),
        ("03", "Tournament Bracket - 8-player + 4-player mini"),
        ("04", "Snack-Plan Worksheet - balanced, low-effort snacks"),
        ("05", "All-Ages Tips - kids, grandparents, everyone"),
        ("06", "Wind-Down Checklist - the anti-meltdown plan"),
    ]
    box_h = 30 + len(items) * 17
    c.roundRect(MARGIN, box_top - box_h, PAGE_W - 2 * MARGIN, box_h, 8, stroke=1, fill=1)
    iy = box_top - 24
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString(MARGIN + 16, iy, "The Free Game Night Hosting Pack")
    iy -= 20
    for num, desc in items:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(CORAL)
        c.drawString(MARGIN + 16, iy, num)
        c.setFont("Helvetica", 9)
        c.setFillColor(INK)
        c.drawString(MARGIN + 40, iy, desc)
        iy -= 17

    draw_footer(c, "House Rule Cards - cover")
    c.showPage()

    labels = ["sheet 1 of 2", "sheet 2 of 2"]
    for sheet in range(2):
        c.setFillColor(NAVY)
        c.rect(0, PAGE_H - 0.3 * inch, PAGE_W, 0.3 * inch, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, PAGE_H - 0.55 * inch, "HOUSE RULE CARDS")
        c.setFont("Helvetica", 9)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.55 * inch, labels[sheet])

        # dashed cut guides
        c.setStrokeColor(LIGHT_INK)
        c.setDash(3, 3)
        c.setLineWidth(0.8)
        grid_h = CARD_ROWS * CARD_H + (CARD_ROWS - 1) * CARD_GAP_Y
        top_y = START_Y + 14
        for i in range(CARD_ROWS + 1):
            gy = top_y - (CARD_H + CARD_GAP_Y) * i
            c.line(MARGIN - 14, gy, PAGE_W - MARGIN + 14, gy)
        for i in range(CARD_COLS + 1):
            cx = START_X + (CARD_W + CARD_GAP_X) * i
            c.line(cx, top_y + 14, cx, top_y - grid_h - 14)
        c.setDash()

        idx = 0
        for row in range(CARD_ROWS):
            for col in range(CARD_COLS):
                game_idx = sheet * CARD_ROWS * CARD_COLS + row * CARD_COLS + col
                if game_idx < len(FEATURED_GAMES):
                    x = START_X + col * (CARD_W + CARD_GAP_X)
                    y = top_y - CARD_H - row * (CARD_H + CARD_GAP_Y)
                    draw_game_card(c, x, y, FEATURED_GAMES[game_idx])
        draw_footer(c, f"House Rule Cards - {labels[sheet]}")
        c.showPage()

    c.save()
    print("wrote", path)


# --------------------------------------------------------------------------
# Doc 02 - Score sheets (platypus tables)
# --------------------------------------------------------------------------

def score_sheets() -> None:
    path = os.path.join(PDF_DIR, "02_score_sheets.pdf")

    def header_footer(canv, doc):
        canv.saveState()
        canv.setFillColor(NAVY)
        canv.rect(0, PAGE_H - 0.3 * inch, PAGE_W, 0.3 * inch, stroke=0, fill=1)
        canv.setFillColor(AMBER)
        canv.rect(0, PAGE_H - 0.36 * inch, PAGE_W, 0.06 * inch, stroke=0, fill=1)
        canv.setFillColor(colors.white)
        canv.setFont("Helvetica-Bold", 9)
        canv.drawString(MARGIN, PAGE_H - 0.56 * inch, "SCORE SHEETS")
        canv.setFont("Helvetica", 9)
        canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.56 * inch, "one game per sheet, in pencil")
        draw_footer(canv, "Score Sheets")
        canv.restoreState()

    doc = BaseDocTemplate(
        path,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.8 * inch,
        bottomMargin=0.9 * inch,
        title="Score Sheets - Free Game Night Hosting Pack",
        author="Asdale Dynamics, LLC",
    )
    frame = Frame(MARGIN, 0.9 * inch, PAGE_W - 2 * MARGIN, PAGE_H - 1.7 * inch, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=header_footer)])

    heading = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=15, textColor=NAVY, spaceAfter=4)
    sub = ParagraphStyle("s", fontName="Helvetica-Oblique", fontSize=9.5, textColor=INK, spaceAfter=10)
    spacer = Spacer(1, 26)

    story = []
    grid = [("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#9AA3B2"))]
    header_style = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]

    # Sheet 1: round-by-round
    story.append(Paragraph("Round-by-Round Score Sheet", heading))
    story.append(Paragraph("Perfect for Crazy Eights, Quick Rummy, or any game played in rounds. Add up the TOTAL column using a calculator if the losers insist on accuracy.", sub))
    players = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5"]
    rows = [
        ["Player"] + [f"R{i}" for i in range(1, 9)] + ["TOTAL"]
    ] + [[p] + [""] * 9 for p in players]
    t = Table(rows, colWidths=[1.35 * inch] + [0.55 * inch] * 9, rowHeights=[0.28 * inch] + [0.42 * inch] * 5, repeatRows=1)
    t.setStyle(TableStyle(grid + header_style + [("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 1), (-1, -1), 10), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(t)
    story.append(spacer)

    # Sheet 2: quick pad
    story.append(Paragraph("Quick Score Pad", heading))
    story.append(Paragraph("One line per round for games like War, Snap, or Slapjack - just tally wins.", sub))
    rows2 = [["Round", "Winner", "Score / Tally"]] + [[str(i), "", ""] for i in range(1, 11)]
    t2 = Table(rows2, colWidths=[0.9 * inch, 3.4 * inch, 2.2 * inch], rowHeights=[0.26 * inch] + [0.32 * inch] * 10, repeatRows=1)
    t2.setStyle(TableStyle(grid + header_style + [("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 1), (-1, -1), 10), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(t2)
    story.append(spacer)

    # Sheet 3: team tournament sheet
    story.append(Paragraph("Team / Tournament Score Sheet", heading))
    story.append(Paragraph("For game-night leagues where every team plays every game. Highest grand total takes home the wooden spoon of honor.", sub))
    rows3 = [["Team", "Game 1", "Game 2", "Game 3", "Game 4", "TOTAL", "Place"]] + [
        [f"Team {i}", "", "", "", "", "", ""] for i in range(1, 5)
    ]
    t3 = Table(rows3, colWidths=[1.1 * inch, 0.95 * inch, 0.95 * inch, 0.95 * inch, 0.95 * inch, 0.95 * inch, 0.7 * inch], rowHeights=[0.28 * inch] + [0.42 * inch] * 4, repeatRows=1)
    t3.setStyle(TableStyle(grid + header_style + [("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 1), (-1, -1), 10), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(t3)
    story.append(spacer)

    # Sheet 4: go fish set tracker
    story.append(Paragraph("Go Fish Set Tracker", heading))
    story.append(Paragraph("Give completed sets a check for each of the 4 matching cards - 4 checks makes one full set.", sub))
    rows4 = [["Player", "Set 1", "Set 2", "Set 3", "Sets won"]] + [
        [p, "", "", "", ""] for p in ["Player 1", "Player 2", "Player 3", "Player 4"]
    ]
    t4 = Table(rows4, colWidths=[1.5 * inch] + [1.4 * inch] * 4, rowHeights=[0.28 * inch] + [0.5 * inch] * 4, repeatRows=1)
    t4.setStyle(TableStyle(grid + header_style + [("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 1), (-1, -1), 10), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(t4)

    doc.build(story)
    print("wrote", path)


# --------------------------------------------------------------------------
# Doc 03 - Tournament bracket (landscape, fold line)
# --------------------------------------------------------------------------

LAND_W, LAND_H = landscape(letter)  # 792 x 612


def draw_match_slot(c, x, y, w, h, label):
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.setFillColor(colors.white)
    c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(LIGHT_INK)
    c.drawString(x + 5, y + h - 9, label)
    c.setStrokeColor(colors.HexColor("#9AA3B2"))
    c.setLineWidth(0.8)
    c.line(x + 6, y + h / 2, x + w - 6, y + h / 2)


def elbow(c, x1, y1, x2, y2):
    """Horizontal elbow connector from (x1,y1) to (x2,y2)."""
    c.setStrokeColor(SAGE)
    c.setLineWidth(1.4)
    mid_x = x1 + (x2 - x1) / 2
    c.line(x1, y1, mid_x, y1)
    c.line(mid_x, y1, mid_x, y2)
    c.line(mid_x, y2, x2, y2)


def draw_bracket_page(
    c: pdfcanvas.Canvas,
    title: str,
    subtitle: str,
    cols: list[tuple[str, int]],
    slot_w: float,
    slot_h: float,
    page_label: str,
) -> None:
    """Draw one landscape bracket page: cols = [(label, n_slots), ...] with
    the first column holding all opening slots, halving each round."""
    c.setFillColor(NAVY)
    c.rect(0, LAND_H - 0.3 * inch, LAND_W, 0.3 * inch, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, LAND_H - 0.57 * inch, title)
    c.setFont("Helvetica", 9)
    c.setFillColor(INK)
    c.drawString(MARGIN, LAND_H - 0.78 * inch, subtitle)

    # column x positions
    col_x: list[float] = []
    x = MARGIN + 10
    for col_idx, (col_label, _) in enumerate(cols):
        col_x.append(x)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(SAGE)
        c.drawString(x, LAND_H - 1.08 * inch, col_label.upper())
        x += slot_w + 72

    # slot vertical centers: column 0 pairs are close, pairs separated more
    span_top = LAND_H - 1.55 * inch
    gap_within = slot_h + 12.0
    gap_between = slot_h + 40.0
    centers0: list[float] = []
    y = span_top
    for i in range(cols[0][1]):
        centers0.append(y)
        y -= gap_within if i % 2 == 0 else gap_between

    centers_by_col: dict[int, list[float]] = {0: centers0}
    for col_idx in range(1, len(cols)):
        prev = centers_by_col[col_idx - 1]
        centers_by_col[col_idx] = [
            (prev[2 * i] + prev[2 * i + 1]) / 2 for i in range(cols[col_idx][1])
        ]

    # draw slots and tree connectors
    for col_idx, (col_label, n_slots) in enumerate(cols):
        for i, cy in enumerate(centers_by_col[col_idx]):
            draw_match_slot(
                c,
                col_x[col_idx],
                cy - slot_h / 2,
                slot_w,
                slot_h,
                f"Match {i + 1}",
            )
        if col_idx + 1 < len(cols):
            nxt = centers_by_col[col_idx + 1]
            for i in range(n_slots):
                child = nxt[i // 2]
                elbow(c, col_x[col_idx] + slot_w, centers_by_col[col_idx][i], col_x[col_idx + 1], child)

    # champion box
    last_x = col_x[-1]
    champ_cy = (centers_by_col[len(cols) - 1][0] + centers_by_col[len(cols) - 1][1]) / 2
    box_w, box_h = 96.0, 56.0
    c.setFillColor(AMBER)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.6)
    c.roundRect(last_x + 42, champ_cy - box_h / 2, box_w, box_h, 6, stroke=1, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(last_x + 42 + box_w / 2, champ_cy + 10, "CHAMPION")
    c.setStrokeColor(colors.white)
    c.line(last_x + 56, champ_cy - 8, last_x + 42 + box_w - 14, champ_cy - 8)

    # fold line down the middle: fold to pocket size, then tri-fold for the box
    c.setStrokeColor(CORAL)
    c.setDash(4, 4)
    c.setLineWidth(1)
    c.line(LAND_W / 2, 0.62 * inch, LAND_W / 2, LAND_H - 0.92 * inch)
    c.setDash()


def draw_bracket_tip_box(c: pdfcanvas.Canvas, items: list[str]) -> None:
    """A small tip box for the spare half of the mini-bracket page."""
    LW = LAND_W - 2 * MARGIN
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.2)
    c.setFillColor(CREAM)
    box_h = 118.0
    c.roundRect(MARGIN, 0.95 * inch, LW, box_h, 8, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(NAVY)
    c.drawString(MARGIN + 16, 0.95 * inch + box_h - 22, "Small-table rules (they keep every bracket friendly)")
    ly = 0.95 * inch + box_h - 40
    c.setFont("Helvetica", 9)
    c.setFillColor(INK)
    for item in items:
        c.setFillColor(SAGE)
        c.drawString(MARGIN + 16, ly, "*")
        c.setFillColor(INK)
        c.drawString(MARGIN + 28, ly, item)
        ly -= 16


def tournament_bracket() -> None:
    path = os.path.join(PDF_DIR, "03_tournament_bracket.pdf")
    c = pdfcanvas.Canvas(path, pagesize=landscape(letter))

    draw_bracket_page(
        c,
        "Tournament Bracket - 8 Players",
        "Write names as players join. Fold along the dotted line, then in thirds, to slip it into the card box.",
        [("Round of 8", 8), ("Semifinals", 4), ("Final", 2)],
        118.0,
        34.0,
        "8-player bracket",
    )
    center_footer_landscape(c, "8-player bracket")
    c.showPage()

    draw_bracket_page(
        c,
        "Mini Bracket - 4 Players",
        "A quick bracket for short attention spans and after-dinner playoffs.",
        [("Semifinals", 4), ("Final", 2)],
        150.0,
        38.0,
        "4-player bracket",
    )
    draw_bracket_tip_box(
        c,
        [
            "Two-game guarantee: play a sorry-I-won rematch so everyone plays twice.",
            "Winner picks the next game; runner-up picks the snack order.",
            "No stalemates: sudden-death 'next hand wins' settles every tie.",
            "Losers are an official committee. Their verdict: dramatically narrate the final.",
        ],
    )
    center_footer_landscape(c, "4-player bracket")
    c.showPage()
    c.save()
    print("wrote", path)


# --------------------------------------------------------------------------
# Doc 04 - Snack plan worksheet
# --------------------------------------------------------------------------

def snack_plan() -> None:
    path = os.path.join(PDF_DIR, "04_snack_plan_worksheet.pdf")
    c = pdfcanvas.Canvas(path, pagesize=letter)
    W = MARGIN + 30
    LW = PAGE_W - W - MARGIN

    title_banner(c, "Plan it before the first hand is dealt", "Snack-Plan Worksheet", "Fill this in the day before - future-you will be grateful.")

    y = PAGE_H - 2.15 * inch
    y = section_header(c, MARGIN, y, "The balance rule", LW)
    for line in wrap_text(
        c,
        "Every good game-night spread has three things: something fresh (fruit, veggies), something filling (pretzels, popcorn, sandwiches), and something fun (cookies, the good stuff). Aim for one of each and a big jug of water.",
        "Helvetica",
        9.5,
        LW,
    ):
        c.setFont("Helvetica", 9.5)
        c.setFillColor(INK)
        c.drawString(MARGIN + 14, y, line)
        y -= 13

    y -= 12
    y = section_header(c, MARGIN, y, "Tonight's lineup", LW)
    rows = ["FRESH (fruit / veggies)", "FILLING (crunchy / hearty)", "FUN (the good stuff)"]
    for label in rows:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(SAGE)
        c.drawString(W, y, label)
        y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(NAVY)
        c.drawString(W, y, "Snack:")
        fill_line(c, W + 42, y - 1.5, LW * 0.42)
        c.drawString(W + LW * 0.52, y, "Who makes it:")
        fill_line(c, W + LW * 0.52 + 68, y - 1.5, LW - LW * 0.52 - 68)
        y -= 14
        c.drawString(W, y, "Allergy check (nuts? dairy?):")
        fill_line(c, W + 118, y - 1.5, LW - 118)
        y -= 20

    y -= 6
    y = section_header(c, MARGIN, y, "Shopping list", LW)
    list_headers = ["Item", "Amount", "Got it?"]
    col_x = [W + 24, W + LW * 0.62, W + LW * 0.84]
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NAVY)
    for hx, htxt in zip(col_x, list_headers):
        c.drawString(hx, y, htxt)
    y -= 4
    for i in range(6):
        c.setStrokeColor(colors.HexColor("#C9CFDA"))
        c.setLineWidth(0.8)
        c.line(W + 2, y - 8, W + LW - 2, y - 8)
        c.setFont("Helvetica", 9)
        c.setFillColor(INK)
        c.drawString(W + 6, y - 6, f"{i + 1}.")
        checkbox(c, col_x[2] + 2, y + 2)
        y -= 22
    y -= 20
    y = section_header(c, MARGIN, y, "Prep timeline", LW)
    for when, what in [
        ("The day before", "Shop + fill the water jug. Set the table? Almost."),
        ("One hour before", "Chop, pour, and put bowls where everyone can reach. Cards on the table!"),
        ("Ten minutes before", "Napkins down. Music on. Phone on the shelf - tonight belongs to the table."),
    ]:
        checkbox(c, W, y - 2)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(NAVY)
        c.drawString(W + 20, y, when)
        y -= 13
        y = draw_lines_text(c, f"Plan: {what}", W + 20, y, LW - 20, "Helvetica", 9, 12) - 8

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(SAGE)
    c.drawString(MARGIN, y, "Pro tip: hands that shuffle cards shouldn't touch dip. Little tongs and forks save the deck.")

    draw_footer(c, "Snack Plan Worksheet")
    c.showPage()
    c.save()
    print("wrote", path)


# --------------------------------------------------------------------------
# Doc 05 - All-ages tips (platypus)
# --------------------------------------------------------------------------

def all_ages_tips() -> None:
    path = os.path.join(PDF_DIR, "05_all_ages_tips.pdf")

    body = ParagraphStyle("b", fontName="Helvetica", fontSize=10, leading=14, textColor=INK, spaceAfter=6)
    bullet = ParagraphStyle("bl", parent=body, leftIndent=14, bulletIndent=4)
    h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=16, textColor=NAVY, spaceBefore=6, spaceAfter=4)
    h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12.5, textColor=colors.HexColor("#B36A00") if False else CORAL, spaceBefore=14, spaceAfter=6)
    note = ParagraphStyle("n", parent=body, fontName="Helvetica-Oblique", textColor=SAGE, spaceBefore=8)

    def header_footer(canv, doc):
        canv.saveState()
        canv.setFillColor(NAVY)
        canv.rect(0, PAGE_H - 0.3 * inch, PAGE_W, 0.3 * inch, stroke=0, fill=1)
        canv.setFillColor(AMBER)
        canv.rect(0, PAGE_H - 0.36 * inch, PAGE_W, 0.06 * inch, stroke=0, fill=1)
        canv.setFillColor(colors.white)
        canv.setFont("Helvetica-Bold", 9)
        canv.drawString(MARGIN, PAGE_H - 0.56 * inch, "ALL-AGES GAME NIGHT")
        canv.setFont("Helvetica", 9)
        canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.56 * inch, "everyone belongs at the table")
        draw_footer(canv, "All-Ages Tips")
        canv.restoreState()

    doc = BaseDocTemplate(
        path,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.8 * inch,
        bottomMargin=0.9 * inch,
        title="All-Ages Tips - Free Game Night Hosting Pack",
        author="Asdale Dynamics, LLC",
    )
    frame = Frame(MARGIN, 0.9 * inch, PAGE_W - 2 * MARGIN, PAGE_H - 1.7 * inch, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=header_footer)])

    story = [
        Paragraph("Young kids, grandparents, and everyone in between", h1),
        Paragraph("The goal of game night is not a winner. It's a table where everybody wants to come back next week.", sub := ParagraphStyle("sub", parent=body, fontName="Helvetica-Oblique", textColor=SAGE)),

        Paragraph("For the youngest players", h2),
        Paragraph("- Deal them in - never 'help them watch'. Kids who hold cards are players.", bullet),
        Paragraph("- Narrate the tricky bits: 'This card means the suit changes. Which suit do you like?'", bullet),
        Paragraph("- Let them win sometimes on purpose, and lose sometimes on purpose. Both teach something.", bullet),
        Paragraph("- Give them a job when attention runs out: scorekeeper, chip mover, official card-shuffler.", bullet),
        Paragraph("- Round lengths matter more than rules. Two short hands beat one long epic.", bullet),

        Paragraph("For grandparents", h2),
        Paragraph("- Ask them to teach a game from their own childhood. Elders become the experts, not guests.", bullet),
        Paragraph("- Big-print score sheets and a brighter lamp. Eyes tire before enthusiasm does.", bullet),
        Paragraph("- Trade vigorous games (Snap!) for memory games (Go Fish, Old Maid) if hands or reflexes prefer it.", bullet),
        Paragraph("- Invite stories between hands. The story of the 1974 family tournament is part of the game.", bullet),

        Paragraph("For the whole table", h2),
        Paragraph("- Read the house-rule cards together before round one. Rules everyone helped pick are rules everyone can live with.", bullet),
        Paragraph("- Celebrate the best loss of the night. 'You drew the exact card you needed and everyone saw it!' is a trophy too.", bullet),
        Paragraph("- Never rank the players out loud. Scores stay on the sheet, love stays on the table.", bullet),
        Paragraph("- Rotate a 'table captain' each week who picks the first game. Power is a snack too.", bullet),
        Paragraph("- End while it's still fun. A night people don't want to finish is the highest compliment.", bullet),

        Paragraph("A friendly note from Asdale Dynamics, LLC: these pages are written the way we'd explain them to a friend - plainly, warmly, and with zero judgment. If a rule doesn't fit your table, change it. It's your table.", note),
    ]
    doc.build(story)
    print("wrote", path)


# --------------------------------------------------------------------------
# Doc 06 - Wind-down checklist
# --------------------------------------------------------------------------

def checklist_section(
    c: pdfcanvas.Canvas,
    x: float,
    y: float,
    width: float,
    heading: str,
    items: list[str],
) -> float:
    y = section_header(c, x, y, heading, width)
    for item in items:
        lines = wrap_text(c, item, "Helvetica", 9.5, width - 24)
        # checkbox aligned with the first text line
        checkbox(c, x + 2, y - 4)
        ty = y
        for line in lines:
            c.setFont("Helvetica", 9.5)
            c.setFillColor(INK)
            c.drawString(x + 24, ty - 9.5, line)
            ty -= 12.5
        y = ty - 8
    return y


def wind_down_checklist() -> None:
    path = os.path.join(PDF_DIR, "06_wind_down_checklist.pdf")
    c = pdfcanvas.Canvas(path, pagesize=letter)
    LW = PAGE_W - 2 * MARGIN

    title_banner(c, "Keep the good vibes past bedtime", "Wind-Down Checklist", "The anti-meltdown plan. Tape it inside a cabinet door and glance, don't memorize.")

    y = PAGE_H - 2.2 * inch
    y = checklist_section(
        c,
        MARGIN,
        y,
        LW,
        "Before the last hand (in the final 20 minutes)",
        [
            "Close the current game at a natural stopping point - 'last round' means the last round.",
            "Start tidying as you play: cards get sorted, cups get ferried to the sink.",
            "Announce the timeline: 'Winner gets crowned in 15 minutes, then snacks and goodnight.'",
            "Dim the lights one notch. Bodies read dim light as 'winding down.'",
            "Crown the champion with the whole table cheering - losers clap too, that's the rule.",
        ],
    )

    y -= 10
    y = checklist_section(
        c,
        MARGIN,
        y,
        LW,
        "If a meltdown is brewing (any age, any size human)",
        [
            "Lower the volume before raising it. Whisper - it's surprisingly contagious.",
            "Name the feeling, fix nothing yet: 'Losing is disappointing. It's okay to be disappointed.'",
            "Offer a small job with both hands: shuffling, snack patrol, holding the score sheet.",
            "Take a 'snack break' - food and water fix more arguments than fairness ever will.",
            "If someone needs air, walk with them. The game can pause; the people can't.",
        ],
    )

    y -= 10
    y = section_header(c, MARGIN, y, "The calm-down corner (park one before you need it)", LW)
    box_lines = wrap_text(
        c,
        "A quiet chair with: a glass of water, one soft thing to hold, and the rule that it is not a punishment - it is a pit stop. Grown-ups may use it too, and sometimes should.",
        "Helvetica",
        9.5,
        LW - 20,
    )
    c.setStrokeColor(SAGE)
    c.setLineWidth(1.2)
    box_h = 12 + len(box_lines) * 13 + 10
    c.roundRect(MARGIN + 4, y - box_h, LW - 8, box_h, 8, stroke=1, fill=0)
    ty = y - 4
    for line in box_lines:
        c.setFont("Helvetica", 9.5)
        c.setFillColor(INK)
        c.drawString(MARGIN + 16, ty - 12, line)
        ty -= 13
    y -= box_h + 20

    y = checklist_section(
        c,
        MARGIN,
        y,
        LW,
        "After the table empties (tomorrow-you says thanks)",
        [
            "Shuffle the decks and return each to its box. Losers make great shufflers.",
            "Write down one moment worth keeping - the story, not the score.",
            "Put the score sheets and the crowned bracket somewhere visible until next time.",
        ],
    )

    y -= 26
    c.setFont("Helvetica-Oblique", 9.5)
    c.setFillColor(SAGE)
    for line in wrap_text(c, "Remember: the pack is about connection, not perfection. If tonight had one laugh, it worked.", "Helvetica-Oblique", 9.5, LW):
        c.drawString(MARGIN, y, line)
        y -= 13

    draw_footer(c, "Wind-Down Checklist")
    c.showPage()
    c.save()
    print("wrote", path)


# --------------------------------------------------------------------------

PDF_BUILDERS = [
    ("01_house_rule_cards.pdf", house_rule_cards),
    ("02_score_sheets.pdf", score_sheets),
    ("03_tournament_bracket.pdf", tournament_bracket),
    ("04_snack_plan_worksheet.pdf", snack_plan),
    ("05_all_ages_tips.pdf", all_ages_tips),
    ("06_wind_down_checklist.pdf", wind_down_checklist),
]


def main() -> int:
    os.makedirs(PDF_DIR, exist_ok=True)
    failures = []
    for name, build in PDF_BUILDERS:
        try:
            build()
        except Exception as exc:  # pragma: no cover
            failures.append((name, exc))
            print(f"FAILED: {name}: {exc}", file=sys.stderr)
    if failures:
        return 1
    print("All 6 PDFs generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
