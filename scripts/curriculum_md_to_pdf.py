#!/usr/bin/env python3
"""
Convert curriculum markdown to PDF. Uses fpdf2 (install next to vendor: see below).

  python3 -m pip install fpdf2 -t lessons/.vendor_pdf
  PYTHONPATH=lessons/.vendor_pdf python3 lessons/scripts/curriculum_md_to_pdf.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("Missing fpdf2. Run: python3 -m pip install fpdf2 -t lessons/.vendor_pdf", file=sys.stderr)
    sys.exit(1)


def _dejavu_regular() -> Path | None:
    for p in (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
    ):
        if p.is_file():
            return p
    return None


def _strip_inline_md(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    s = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", s)
    return s


def _flush_paragraph(pdf: FPDF, family: str, buf: list[str], lh: float, pt: float) -> None:
    if not buf:
        return
    text = "\n".join(buf).strip()
    if not text:
        buf.clear()
        return
    pdf.set_font(family, size=pt)
    bold = "**" in text
    pdf.set_font(family, style="B" if bold else "", size=pt)
    for raw_line in text.split("\n"):
        line = _strip_inline_md(raw_line)
        pdf.multi_cell(0, lh, line)
        pdf.ln(1)
    pdf.set_font(family, style="", size=pt)
    buf.clear()


def markdownish_to_pdf(src: Path, dst: Path) -> None:
    raw = src.read_text(encoding="utf-8").splitlines()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    dj = _dejavu_regular()
    if dj:
        fam = "DocSans"
        pdf.add_font(fam, "", str(dj))
    else:
        fam = "Helvetica"

    pt_body = 10
    lh = 5.5
    pdf.set_font(fam, size=pt_body)

    buf: list[str] = []
    in_table = False
    table_rows: list[list[str]] = []

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        ncols = max(len(r) for r in table_rows)
        col_w = pdf.epw / max(ncols, 1)
        small = pt_body - 1
        for ri, row in enumerate(table_rows):
            if ri == 1 and all(set(c.strip()) <= {"-", " "} for c in row):
                continue
            pdf.set_font(fam, style="B" if ri == 0 else "", size=small)
            padded = row + [""] * (ncols - len(row))
            for cell in padded[:ncols]:
                txt = _strip_inline_md(cell.strip()).replace("|", "")[:140]
                pdf.cell(col_w, 7, txt, border=1, align="L")
            pdf.ln(7)
        pdf.set_font(fam, style="", size=pt_body)
        pdf.ln(4)
        in_table = False
        table_rows = []

    for line in raw:
        s = line.rstrip("\n")

        if s.startswith("|") and s.count("|") >= 2:
            _flush_paragraph(pdf, fam, buf, lh, pt_body)
            flush_table()
            in_table = True
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            table_rows.append(cells)
            continue

        if in_table and not s.startswith("|"):
            flush_table()

        if s.startswith("# "):
            _flush_paragraph(pdf, fam, buf, lh, pt_body)
            pdf.set_font(fam, style="B", size=17)
            pdf.multi_cell(0, 10, _strip_inline_md(s[2:].strip()))
            pdf.ln(3)
            pdf.set_font(fam, style="", size=pt_body)
            continue

        if s.startswith("## "):
            _flush_paragraph(pdf, fam, buf, lh, pt_body)
            pdf.set_font(fam, style="B", size=13)
            pdf.multi_cell(0, 8, _strip_inline_md(s[3:].strip()))
            pdf.ln(2)
            pdf.set_font(fam, style="", size=pt_body)
            continue

        if s.startswith("### "):
            _flush_paragraph(pdf, fam, buf, lh, pt_body)
            pdf.set_font(fam, style="B", size=11)
            pdf.multi_cell(0, 7, _strip_inline_md(s[4:].strip()))
            pdf.ln(2)
            pdf.set_font(fam, style="", size=pt_body)
            continue

        if s.strip() == "---":
            _flush_paragraph(pdf, fam, buf, lh, pt_body)
            pdf.ln(2)
            y = pdf.get_y()
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(5)
            continue

        if not s.strip():
            _flush_paragraph(pdf, fam, buf, lh, pt_body)
            continue

        buf.append(s)

    _flush_paragraph(pdf, fam, buf, lh, pt_body)
    flush_table()

    dst.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(dst))


def main() -> None:
    lessons = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=lessons / "CURRICULUM_MODULES_1_TO_10.txt")
    ap.add_argument("--output", type=Path, default=lessons / "CURRICULUM_MODULES_1_TO_10.pdf")
    args = ap.parse_args()
    markdownish_to_pdf(args.input, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
