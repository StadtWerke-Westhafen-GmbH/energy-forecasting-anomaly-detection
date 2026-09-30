"""Bausteine für die gemeinsame Präsentation von Gruppe 6 (Google-Slides-tauglich).

Lädt Kikos PPTX-Generator (``build_kiko_pptx.py``) per ``runpy`` und nutzt dessen Grundbausteine
(Textfelder, Scheiben, Karten, Zählwerk). Für Google Slides werden einzelne Funktionen in dessen
Globals ersetzt; Kikos Einzel-Deck bleibt davon unberührt, weil jedes ``runpy.run_path`` einen
eigenen Namensraum anlegt.

Google-Modus:
* Versalien werden als echte Großbuchstaben geschrieben (Google Slides kennt ``cap="all"`` nicht).
* Einzeilige Textfelder bekommen 10 % Breitenreserve, weil Google die Schrift minimal anders setzt.
* PowerPoint-Diagramme entstehen auf einer Hilfsfolie, die am Ende entfällt; auf der Folie steht
  stattdessen das PNG des Diagramms aus Kikos HTML-Deck (``export_team_charts.mjs``).
* Transparenzen werden am Ende in deckende Mischfarben mit dem darunterliegenden Grund umgerechnet.
"""

from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path

from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
# run_path liefert nur eine Kopie der Globals; ersetzt wird im echten Namensraum der Funktionen
K = runpy.run_path(str(ROOT / "scripts" / "build_kiko_pptx.py"))["build"].__globals__
BUILD = K["BUILD"]
TEAM_DIR = ROOT / "docs" / "presentation" / "team"
CHART_DIR = TEAM_DIR / "assets" / "charts"

E, rgb, mix, text, disc, line = K["E"], K["rgb"], K["mix"], K["text"], K["disc"], K["line"]
W, H, FOOT_Y = K["W"], K["H"], K["FOOT_Y"]
INK, MUTED, SOFT, LINE, LINE2 = K["INK"], K["MUTED"], K["SOFT"], K["LINE"], K["LINE2"]
NAVY, NAVY9, NAVY7 = K["NAVY"], K["NAVY9"], K["NAVY7"]
TEAL, TEAL6, TEAL7, TEAL3 = K["TEAL"], K["TEAL6"], K["TEAL7"], K["TEAL3"]
MIST, PALE, WHITE, SANS, MONO = K["MIST"], K["PALE"], K["WHITE"], K["SANS"], K["MONO"]

# Kapitel der Agenda: Nummer, Name, Icon, sprechende Person
CHAPTERS = [
    ("01", "Ausgangssituation", "building-2", "Iana"),
    ("02", "Daten", "database", "Iana"),
    ("03", "ML Canvas", "layout-grid", "Kiko"),
    ("04", "Methodik und Modell", "trees", "Kiko"),
    ("05", "Ergebnisse", "chart-column", "Patrick"),
    ("06", "Empfehlungen", "compass", "Patrick"),
]

STATE: dict = {"scratch": None, "native": []}


# --------------------------------------------------------------------------- Google-Modus


def _caps(paras, upper: bool):
    """Versalien als echte Großbuchstaben statt ``cap="all"``."""
    if isinstance(paras, str):
        return paras.upper() if upper else paras
    out = []
    for para in paras:
        if isinstance(para, str):
            out.append(para.upper() if upper else para)
        else:
            out.append([(t.upper() if o.get("upper", upper) else t, {k: v for k, v in o.items() if k != "upper"})
                        for t, o in para])
    return out


def _google_mode(k: dict) -> None:
    orig_text, orig_place, orig_header = k["text"], k["place_chart"], k["header"]

    def g_text(s, x, y, w, h, paras, size=16, color=INK, bold=False, font=SANS, align="l", anchor="t",
               lh=None, gap=0.0, name=None, tracking=0.0, wrap=True, upper=False, indent=18):
        paras = _caps(paras, upper)
        if not wrap:  # Reserve je nach Ausrichtung nach rechts, links oder beidseitig
            extra = max(4.0, 0.1 * w)
            x -= {"l": 0.0, "c": extra / 2, "r": extra}[align]
            w += extra
        return orig_text(s, x, y, w, h, paras, size, color, bold, font, align, anchor, lh, gap, name, tracking,
                         wrap, False, indent)

    def g_place_chart(s, chart_type, data, rect, pad=(0, 0, 0, 0), name=None):
        STATE["native"].append(rect)
        return orig_place(STATE["scratch"], chart_type, data, rect, pad, name)

    def g_header(s, root, dark=False):
        orig_header(s, root, dark)  # Kikos Schrittleiste entfällt, die Kapitelleiste kommt danach

    k["text"], k["place_chart"], k["header"] = g_text, g_place_chart, g_header
    k["tracker"] = lambda s, el, dark=False: None


_google_mode(K)
text = K["text"]


# --------------------------------------------------------------------------- Kapitelleiste


def chapter_bar(s, chapter: str, dark: bool = False) -> None:
    """Sechs Kapitel als Icon-Scheiben (je Person ein Paar), aktives gefüllt, Label mit Namen."""
    xs = [1000, 1030, 1076, 1106, 1152, 1182]
    active = next(i for i, c in enumerate(CHAPTERS) if c[0] == chapter)
    for i, ((nr, _, icon, _), x) in enumerate(zip(CHAPTERS, xs)):
        on = i == active
        if dark:
            tone = "light" if on else "glass"
        else:
            tone = "navy" if on else ("ring" if i < active else "off")
        disc(s, x, 42, icon, tone, 26, name=f"Kapitel {nr}{' aktiv' if on else ''}")
    for x in (1062, 1138):
        line(s, x, 55, x + 8, 55, "#3D6A8C" if dark else "#B4BFCB", 2, name="Kapitel-Lücke")
    nr, name, _, who = CHAPTERS[active]
    text(s, 688, 45, 300, 18, f"{nr} · {name} · {who}", 14, TEAL3 if dark else TEAL7, True, align="r", lh=18,
         wrap=False, name="Kapitel-Label")


# --------------------------------------------------------------------------- Diagramme als Bild


def load_charts() -> list[dict]:
    path = CHART_DIR / "charts.json"
    if not path.exists():
        subprocess.run(["node", str(ROOT / "scripts" / "export_team_charts.mjs")], check=True, cwd=ROOT)
    return json.loads(path.read_text(encoding="utf-8"))


def _box_px(el):
    off, ext = el.find(".//" + qn("a:off")), el.find(".//" + qn("a:ext"))
    if off is None or ext is None:
        return None
    x, y = int(off.get("x")) / 9525, int(off.get("y")) / 9525
    return x, y, x + int(ext.get("cx")) / 9525, y + int(ext.get("cy")) / 9525


def remove_inside(s, rect, tol: float = 6.0) -> int:
    """Alle Formen, die vollständig im Rechteck liegen, entfernen (Kartenrahmen außen bleiben)."""
    x, y, w, h = rect
    removed = 0
    for sh in list(s.shapes):
        b = _box_px(sh._element)
        if b and b[0] >= x - tol and b[1] >= y - tol and b[2] <= x + w + tol and b[3] <= y + h + tol:
            sh._element.getparent().remove(sh._element)
            removed += 1
    return removed


def replace_charts(s, slide_idx: int, spec, charts: list[dict]) -> None:
    """Diagrammbereiche mit nativem PowerPoint-Diagramm durch das PNG aus dem HTML-Deck ersetzen."""
    native, STATE["native"] = STATE["native"], []
    if not native:
        return
    svgs = list(K["parse"](spec).iter("svg"))
    for c in (c for c in charts if c["slide"] == slide_idx):
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        if not any(x <= rx + rw / 2 <= x + w and y <= ry + rh / 2 <= y + h for rx, ry, rw, rh in native):
            continue
        vb = [float(v) for v in svgs[c["svg"]].get("viewbox").split()]
        assert abs(vb[2] / vb[3] - w / h) < 0.02 * w / h, f"SVG-Zuordnung HTML/PPTX stimmt nicht: {c['file']}"
        remove_inside(s, (x, y, w, h))
        K["picture"](s, str(CHART_DIR / c["file"]), x, y, w, h, name=f"Diagramm {c['file']}")


def drop_slide(prs, slide) -> None:
    for sld_id in list(prs.slides._sldIdLst):
        if prs.part.related_part(sld_id.rId) is slide.part:
            prs.slides._sldIdLst.remove(sld_id)
            prs.part.drop_rel(sld_id.rId)
            return


# --------------------------------------------------------------------------- Transparenzen auflösen


def _hex(el) -> str:
    return "#" + el.get("val").upper()


def flatten_alpha(slide) -> None:
    """Transparente Füllungen und Linien in Mischfarben mit dem darunterliegenden Grund umrechnen.

    Der Grund ist die oberste deckende Fläche unter dem Formmittelpunkt, sonst der Folienhintergrund.
    Gruppenkinder liegen in Folienkoordinaten (python-pptx legt Gruppen ohne Transformation an).
    """
    bg_clr = slide._element.find(".//" + qn("p:bg") + "//" + qn("a:srgbClr"))
    bg = _hex(bg_clr) if bg_clr is not None else WHITE
    painted: list[tuple[tuple, str]] = []
    tree = slide.shapes._spTree
    for el in tree.iter(qn("p:sp"), qn("p:cxnSp")):
        sppr = el.find(qn("p:spPr"))
        b = _box_px(sppr) if sppr is not None else None
        if b is None:
            continue
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        under = next((c for r, c in reversed(painted) if r[0] <= cx <= r[2] and r[1] <= cy <= r[3]), bg)
        fill = sppr.find(qn("a:solidFill"))
        for clr in sppr.iter(qn("a:srgbClr")):
            alpha = clr.find(qn("a:alpha"))
            if alpha is not None:
                clr.set("val", mix(_hex(clr), under, int(alpha.get("val")) / 100000).lstrip("#"))
                clr.remove(alpha)
        if fill is not None and fill.find(qn("a:srgbClr")) is not None:
            painted.append((b, _hex(fill.find(qn("a:srgbClr")))))


def theme_fonts(prs) -> None:
    """Theme-Schriften auf IBM Plex Sans (Notizen, Tabellen ohne eigene Schrift)."""
    import re

    for part in prs.part.package.iter_parts():
        if not str(part.partname).startswith("/ppt/theme/"):
            continue
        if hasattr(part, "_element"):  # Notizen-Master-Theme wird als XML-Teil angelegt
            for latin in part._element.iter(qn("a:latin")):
                latin.set("typeface", "IBM Plex Sans")
        else:
            xml = part.blob.decode("utf-8")
            part._blob = re.sub(r'<a:latin typeface="[^"]*"', '<a:latin typeface="IBM Plex Sans"', xml).encode()
