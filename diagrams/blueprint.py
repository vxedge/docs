"""Shared drawing helpers for the diagrams in this folder (standard library only).

Style: a light panel that carries its own colours, so a diagram reads the same on GitHub, in the
rendered docs and on a slide. Solid outline = built today (real, emulated, building); dashed steel =
specified, not built yet (the states in FACTS.md's parity ledger).
"""

from html import escape

INK, MID, TEAL, STEEL, RULE, TINT, PANEL = "#1E2023", "#5A5E66", "#0E7C6B", "#5A5E66", "#C9C9C4", "#F3F3F0", "#FAFAF8"
out: list[str] = []


def add(s: str) -> None:
    out.append(s)


K = 1.15  # type scale: diagrams are shown at about two thirds of their width, so the text is drawn large


def text(x, y, s, size=13, weight=400, fill=INK, anchor="start", mono=False, spacing=None):
    fam = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" if mono else "ui-sans-serif,system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{round(size * K, 1)}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}>{escape(s)}</text>')


def box(x, y, w, h, title, sub="", state="", dashed=False, fill="#FFFFFF", rx=5):
    stroke = STEEL if dashed else INK
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
    ty = y + (24 if sub else (22 if h >= 50 else h / 2 + 5))
    text(x + 16, ty, title, 14.5, 700)
    if sub:
        text(x + 16, y + 45, sub, 12, 400, MID)
    if state:
        col = TEAL if state in ("REAL", "EMULATED") else MID
        text(x + w - 14, y + 20, state, 10, 600, col, "end", True, "1")


def group(x, y, w, h, label):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{TINT}" stroke="{RULE}" stroke-width="1.2"/>')
    text(x + 18, y + 24, label, 11.5, 600, MID, mono=True, spacing=".6")


def line(x1, y1, x2, y2, dashed=False):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    add(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{INK if not dashed else STEEL}" stroke-width="1.5" fill="none"{dash}/>')




def start(width, height, title, desc):
    """Begin a new diagram; returns nothing. Call finish() for the SVG text."""
    out.clear()
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t d">')
    add(f'<title id="t">{escape(title)}</title>')
    add(f'<desc id="d">{escape(desc)}</desc>')
    add(f'<rect width="{width}" height="{height}" rx="10" fill="{PANEL}" stroke="{RULE}"/>')


def finish():
    add("</svg>")
    return "\n".join(out) + "\n"


def legend(y, right_note="states follow the parity ledger in FACTS.md"):
    add(f'<rect x="40" y="{y - 10}" width="22" height="12" rx="2" fill="#FFFFFF" stroke="{INK}" stroke-width="1.5"/>')
    text(70, y, "built today (real, emulated or building)", 11.5, 400, MID)
    add(f'<rect x="360" y="{y - 10}" width="22" height="12" rx="2" fill="#FFFFFF" stroke="{STEEL}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    text(390, y, "specified, not built yet", 11.5, 400, MID)
    text(1160, y, right_note, 11.5, 400, MID, "end")
