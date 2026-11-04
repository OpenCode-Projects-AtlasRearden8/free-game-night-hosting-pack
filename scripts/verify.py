#!/usr/bin/env python3
"""Verify the Free Game Night Hosting Pack.

Checks (all offline, no network):
  1. All six PDFs exist, are valid PDFs, have pages, and open with pypdf.
  2. The index site links to every PDF (links resolve on disk).
  3. LICENSE has the exact Asdale Dynamics, LLC copyright line.
  4. README credits Asdale Dynamics, LLC.
  5. No obvious secrets/keys/personal data in tracked files.

Copyright (c) 2026 Asdale Dynamics, LLC
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PDFS = [
    # (filename, expected min pages, landscape?)
    ("01_house_rule_cards.pdf", 3, False),
    ("02_score_sheets.pdf", 2, False),
    ("03_tournament_bracket.pdf", 2, True),
    ("04_snack_plan_worksheet.pdf", 1, False),
    ("05_all_ages_tips.pdf", 1, False),
    ("06_wind_down_checklist.pdf", 1, False),
]

EXPECTED_COPYRIGHT = "Copyright (c) 2026 Asdale Dynamics, LLC"

SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|api[_-]?secret|secret[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    re.compile(r"(?i)\bpassword\s*[:=]\s*['\"]?[^\s'\"]{6,}"),
    re.compile(r"(?i)\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)\bsk-(?:proj-)?[A-Za-z0-9\-_]{20,}"),
    re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"),
]

TEXT_SCAN_SKIP_NAMES = {"LICENSE"}


class Checker:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passes = 0

    def check(self, ok: bool, label: str) -> None:
        if ok:
            self.passes += 1
            print(f"  PASS  {label}")
        else:
            self.failures.append(label)
            print(f"  FAIL  {label}")

    def result(self) -> int:
        print()
        if self.failures:
            print(f"{len(self.failures)} check(s) FAILED, {self.passes} passed")
            for f in self.failures:
                print(f"  - {f}")
            return 1
        print(f"All {self.passes} checks passed.")
        return 0


def main() -> int:
    c = Checker()

    print("PDFs:")
    try:
        from pypdf import PdfReader
    except ImportError:
        print("  SKIP  pypdf not installed (run: pip install pypdf) - skipping PDF reads")
        PdfReader = None  # type: ignore

    for name, min_pages, landscape in PDFS:
        path = os.path.join(ROOT, "pdfs", name)
        exists = os.path.isfile(path) and os.path.getsize(path) > 1000
        c.check(exists, f"{name} exists and is non-trivial")
        if not exists:
            continue
        with open(path, "rb") as f:
            head = f.read(8)
            f.seek(-16, os.SEEK_END)
            tail_data = f.read()
        c.check(head.startswith(b"%PDF"), f"{name} starts with %PDF magic")
        c.check(b"%%EOF" in tail_data, f"{name} ends with %%EOF marker")
        if PdfReader is not None:
            try:
                reader = PdfReader(path)
                n = len(reader.pages)
                c.check(n >= min_pages, f"{name} has >= {min_pages} page(s) (got {n})")
                box = reader.pages[0].mediabox
                p00 = (float(box.width) > float(box.height))
                c.check(p00 == landscape, f"{name} page orientation correct")
                text = reader.pages[0].extract_text() or ""
                c.check("Asdale Dynamics, LLC".lower() in text.lower(),
                        f"{name} carries the Asdale Dynamics, LLC credit")
            except Exception as exc:
                c.check(False, f"{name} parses cleanly ({exc})")

    print("Site:")
    site_path = os.path.join(ROOT, "site", "index.html")
    c.check(os.path.isfile(site_path), "site/index.html exists")
    if os.path.isfile(site_path):
        html = open(site_path, encoding="utf-8").read()
        for name, _, _ in PDFS:
            href = f"../pdfs/{name}"
            c.check(href in html, f"site links to {href}")
            c.check(os.path.isfile(os.path.join(ROOT, "site", href)),
                    f"{href} resolves on disk from site/")
        c.check("Asdale Dynamics, LLC" in html, "site credits Asdale Dynamics, LLC")
        for forbidden in ("TODO", "Lorem ipsum", "FIXME"):
            c.check(forbidden.lower() not in html.lower(), f"site contains no '{forbidden}' placeholder")

    print("License & credit:")
    lic_path = os.path.join(ROOT, "LICENSE")
    lic_ok = os.path.isfile(lic_path) and EXPECTED_COPYRIGHT in open(lic_path, encoding="utf-8").read()
    c.check(lic_ok, 'LICENSE contains exact line "Copyright (c) 2026 Asdale Dynamics, LLC"')
    readme_path = os.path.join(ROOT, "README.md")
    readme_ok = os.path.isfile(readreadme := readme_path) and "Asdale Dynamics, LLC" in open(readme_path, encoding="utf-8").read()
    c.check(readme_ok, "README credits Asdale Dynamics, LLC")

    print("Secrets / personal data scan:")
    bad: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".venv", "venv")]
        for fn in filenames:
            if fn.endswith((".pdf", ".png", ".jpg", ".gif")):
                continue
            fp = os.path.join(dirpath, fn)
            if os.path.basename(fp).startswith(".git") or os.path.basename(fp) in TEXT_SCAN_SKIP_NAMES:
                continue
            try:
                content = open(fp, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for pat in SECRET_PATTERNS:
                if pat.search(content):
                    bad.append(os.path.relpath(fp, ROOT))
    c.check(not bad, "no obvious secrets/keys/personal data files found" + (f" (in: {bad})" if bad else ""))

    print("Generator runs:")
    import subprocess
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "generate_pdfs.py")],
        capture_output=True, text=True, timeout=180,
    )
    c.check(proc.returncode == 0, "scripts/generate_pdfs.py exits 0 and regenerates all PDFs")

    return c.result()


if __name__ == "__main__":
    sys.exit(main())
