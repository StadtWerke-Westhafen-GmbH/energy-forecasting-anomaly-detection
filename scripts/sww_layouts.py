"""Folienlayouts des SWW-Designsystems als Google-Slides-taugliche PPTX-Bausteine.

Vorbild sind die HTML-Layouts unter brand/design-system/slides/ (slide.css): Label in Versalien
über dem Titel, Titel als Aussage, weiße Karten mit feinem Rand, Kennzahlen in Geist Mono,
Kapitelfolie mit halber Navy-Fläche, Vergleichskarten mit Etikett, dunkle Abschlussfolie.
Maße in CSS-Pixeln der 1280 × 720-Folie; die Google-Anpassungen kommen aus ``team_kit``.
"""

from __future__ import annotations

import team_kit as kit
from team_kit import E, K, MONO, SANS, WHITE, box, line, rgb, text

# Tokens (brand/design-system/dist/css/tokens.css)
NAVY900, NAVY800, NAVY700 = "#04263F", "#063659", "#084878"
NAVY100, NAVY200, NAVY300 = "#E4EFF7", "#BBD7EA", "#7FB4D8"
TEAL100, TEAL200, TEAL300, TEAL500, TEAL600, TEAL700 = "#E3F3F7", "#B2DEE7", "#6CC0D2", "#0080A0", "#00718E", "#005E77"
GREY25, GREY50, GREY100, GREY200 = "#F7F9FB", "#F1F4F7", "#E4E9EF", "#D2DAE2"
GREY400, GREY500, GREY600, GREY900 = "#8C99A7", "#657383", "#4E5A68", "#141A21"
CYAN500, AMBER600, RED500 = "#0090C8", "#A86505", "#B3261E"
BADGE = {  # Hintergrund, Rand, Text (.b-warn, .b-crit, .b-info, .b-ok, dunkel)
    "warn": ("#FDF3E0", "#F7DFAF", "#7F4C03"), "crit": ("#FBE9E7", "#F3C6C1", "#951C15"),
    "info": (TEAL100, TEAL200, TEAL700), "ok": ("#EDF6E9", "#CFE7C8", "#2F7A33"),
    "dark": ("rgba(255,255,255,.10)", "rgba(255,255,255,.24)", WHITE),
}
GLASS, GLASS_LINE = "rgba(255,255,255,.07)", "rgba(255,255,255,.16)"
PROJECT = "Verbrauchsprognose & Frühwarnung"
X0, CW, FOOT = 72, 1136, 646      # linker Rand, Inhaltsbreite, Oberkante der Fußzeile


def slide(prs, bg: str = WHITE):
    return kit.blank(prs, bg)


def header(s, eyebrow: str, title: str, dark: bool = False) -> None:
    """.eyebrow (16 px, Versalien, teal) und .h2 (40 px, 600)."""
    text(s, X0, 48, 820, 20, eyebrow, 16, TEAL300 if dark else TEAL600, True, lh=20, tracking=.1, upper=True,
         wrap=False, name="Label")
    text(s, X0, 80, CW, 46, title, 40, WHITE if dark else GREY900, True, lh=45, name="Titel")


def footer(s, num: str, dark: bool = False, logo: bool = True) -> None:
    """.slide__ft: Linie, kleines Logo, Projekttitel, Seitenzahl rechts."""
    if logo:
        line(s, 0, FOOT, 1280, FOOT, GLASS_LINE if dark else GREY100, 1, name="Fußlinie")
        if dark:
            box(s, X0, 666, 70, 30, fill=WHITE, radius=4, name="Logo-Grund")
            kit.picture(s, kit.LOGO, X0 + 6, 670, h=22, name="Logo")
            x = X0 + 86
        else:
            kit.picture(s, kit.LOGO, X0, 668, h=26, name="Logo")
            x = X0 + 92
        text(s, x, 671, kit.measure(PROJECT, 16) + 12, 20, PROJECT, 16, NAVY300 if dark else GREY600, lh=20,
             wrap=False)
    w = max(64.0, kit.measure(num, 16))
    text(s, 1208 - w, 671, w, 20, num, 16, NAVY300 if dark else GREY600, align="r", lh=20, wrap=False,
         name="Seitenzahl")


def card(s, x, y, w, h, fill: str = WHITE, border: str = GREY200, name: str | None = None):
    """.panel / .kpi: weiß, 1 px Rand, 10 px Radius (Schatten entfällt für Google Slides)."""
    return box(s, x, y, w, h, fill=fill, line=border, radius=10, name=name)


def panel(s, x, y, w, h, head: str, body, variant: str = "white", head_size: float = 20, body_size: float = 19,
          name: str | None = None) -> None:
    """.panel mit h4 und p; Varianten white, teal, navy, glass (auf dunklem Grund)."""
    fill, border, hc, bc = {
        "white": (WHITE, GREY200, GREY900, GREY600), "teal": (TEAL100, TEAL200, TEAL700, GREY900),
        "navy": (NAVY700, NAVY900, WHITE, NAVY100), "glass": (GLASS, GLASS_LINE, WHITE, NAVY200),
        "muted": (GREY50, GREY200, GREY600, GREY600),
    }[variant]
    card(s, x, y, w, h, fill=fill, border=border)
    top = y + 22
    if head:
        text(s, x + 24, top, w - 48, head_size * 1.3, head, head_size, hc, True, lh=head_size * 1.3)
        top += head_size * 1.3 + 8
    text(s, x + 24, top, w - 48, y + h - 20 - top, body, body_size, bc, lh=body_size * 1.45, name=name)


def eyebrow(s, x, y, w, t: str, color: str = TEAL600, size: float = 16) -> None:
    text(s, x, y, w, size * 1.3, t, size, color, True, lh=size * 1.3, tracking=.06, upper=True, wrap=False)


def badge(s, x, y, t: str, kind: str = "info", size: float = 16) -> float:
    """.badge: Pille mit Rand; gibt die Breite zurück."""
    bg, border, ink = BADGE[kind]
    w = kit.measure(t, size, True) + 30
    h = size * 1.3 + 12
    box(s, x, y, w, h, fill=bg, line=border, radius=h / 2, name=f"Etikett {t}")
    text(s, x, y, w, h, t, size, ink, True, align="c", anchor="m", lh=size * 1.3, wrap=False)
    return w


def kpi(s, x, y, w, h, label: str, value: str, unit: str = "", note: str = "", value_color: str = GREY900) -> None:
    """.kpi: Label 18 px, Wert Geist Mono 40 px, Einheit 18 px, Hinweis 16 px."""
    card(s, x, y, w, h)
    text(s, x + 26, y + 24, w - 52, 24, label, 18, GREY600, lh=24)
    vw = kit.measure(value, 40, True, MONO)
    text(s, x + 26, y + 54, vw + 8, 52, value, 40, value_color, True, MONO, lh=52, wrap=False)
    if unit:
        text(s, x + 26 + vw + 12, y + 72, kit.measure(unit, 18, True) + 8, 24, unit, 18, GREY500, True, lh=24,
             wrap=False)
    if note:
        text(s, x + 26, y + 112, w - 52, h - 128, note, 16, GREY600, lh=22)


def image_card(s, path, x, y, w, h=None, name: str | None = None):
    """Diagramm oder Screenshot in weißer Karte mit 1 px Rand; Höhe folgt dem Seitenverhältnis."""
    from PIL import Image

    iw, ih = Image.open(path).size
    h = h or w * ih / iw
    card(s, x - 12, y - 12, w + 24, h + 24)
    kit.picture(s, str(path), x, y, w, h, name=name or f"Bild {getattr(path, 'name', path)}")
    return h


def section(prs, number: str, title: str, eyebrow_text: str, question: str, items, speaker: str, num: str):
    """Abschnittsfolie: linke 46 % Navy mit Kapitelnummer, rechts die Fragen des Kapitels.

    ``items``: Texte (Aufzählung) oder Tupel (Frage, Icon, Ton, Hinweis, Name) für Zeilen mit
    farbiger Icon-Scheibe; die Töne folgen den Rollenfarben (navy Prognose, teal Messen, amber Schwelle).
    """
    s = slide(prs)
    box(s, 0, 0, 589, 720, fill=NAVY800, name="Kapitelfläche")
    kit.ring_arc(s, 589, 30, 250, (0, 0, 589, 720), "rgba(108,192,210,.2)", 2)
    kit.ring_arc(s, 579, 40, 160, (0, 0, 589, 720), "rgba(108,192,210,.12)", 2)
    text(s, 56, 40, 480, 20, eyebrow_text, 16, TEAL300, True, lh=20, tracking=.1, upper=True, wrap=False,
         name="Label")
    text(s, 56, 408, 480, 116, number, 120, kit.mix(TEAL300, NAVY800, .5), True, MONO, lh=108, wrap=False)
    text(s, 56, 540, 480, 100, title, 40, WHITE, True, lh=45, name="Titel")
    rows = isinstance(items[0], tuple)
    step = 96 if rows else 38.5
    top = 360 - (62 + step * len(items)) / 2  # Block senkrecht mittig wie im Layout (justify-content:center)
    box(s, 661, top, 64, 4, fill=TEAL500, radius=2, name="Regel")
    text(s, 661, top + 30, 547, 32, question, 24, GREY900, lh=32)
    if rows:
        for i, (q, icon_name, tone, hint, name) in enumerate(items):
            y = top + 84 + i * step
            kit.disc(s, 661, y, icon_name, tone, 44, name=f"Scheibe {name}")
            text(s, 723, y - 2, 485, 30, q, 22, GREY900, True, lh=29)
            text(s, 723, y + 30, 485, 22, hint, 16, GREY500, lh=22)
    else:
        text(s, 661, top + 82, 547, step * len(items) * 1.06 + 4, ["• " + b for b in items], 22, GREY600, lh=step,
             indent=26)
    text(s, 661, 600, 547, 24, speaker, 18, GREY500, lh=24)
    footer(s, num, logo=False)
    return s
