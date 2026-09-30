"""Folienmuster M1–M10 zum Duplizieren (Google Slides: Folie markieren, Strg+D, nach vorn ziehen).

Platzhalter stehen in [eckigen Klammern]; jede Musterfolie erklärt in den Notizen, wofür sie
gedacht ist und worauf man achten muss. Alle Elemente sind Formen und Textfelder aus denselben
Bausteinen wie die fertigen Folien, damit kopierte Teile exakt gleich aussehen.
"""

from __future__ import annotations

import team_kit as kit
from team_kit import (INK, LINE, LINE2, MIST, MONO, MUTED, NAVY, NAVY7, PALE, RED, SOFT, TEAL3, TEAL6, TEAL7, TINT,
                      WHITE, box, card, disc, footer, header, icard, icon, line, marker, merk, text)

Q, T = "[Leitfrage des Publikums]?", "[Titel = Antwort in einem Satz]"
PATTERNS = ["Regeln", "Drei Karten", "Text und Bild", "Tabelle", "Kennzahlen", "Prozesskette",
            "Split blau/weiß", "Dunkler Merksatz", "Screenshot mit Hinweisen", "Baukasten"]


def _how(s, *lines):
    kit.set_notes(s, [("SO NUTZT DU DIESES MUSTER", list(lines)),
                      ("IMMER", ["• Leitfrage mit Fragezeichen, höchstens 58 Zeichen; Titel ist die Antwort.",
                                 "• Kapitelleiste oben rechts: von einer Folie deines Kapitels kopieren "
                                 "(aktive Scheibe und Label passen dann).",
                                 "• Fußzeile: Canvas-Felder der Folie, eigener Name, Seitenzahl anpassen.",
                                 "• Musterfolie duplizieren (Strg+D), nicht direkt bearbeiten."])])


def _placeholder(s, x, y, w, h, hint: str, dark: bool = False):
    """Rahmen für Bild oder Diagramm: gestrichelt, mit Icon und Hinweis."""
    from pptx.enum.dml import MSO_LINE_DASH_STYLE

    box(s, x, y, w, h, fill="rgba(255,255,255,.06)" if dark else MIST, line=TEAL3 if dark else "#B4BFCB",
        radius=10, lw=1.5, dash=MSO_LINE_DASH_STYLE.DASH, name="Bild-Platzhalter")
    icon(s, "image-plus", TEAL3 if dark else SOFT, x + w / 2 - 20, y + h / 2 - 44, 40)
    text(s, x + 24, y + h / 2 + 6, w - 48, 44, hint, 15, PALE if dark else MUTED, align="c", lh=21)


def trenner(prs, num):
    s = kit.blank(prs, NAVY)
    kit.ring_arc(s, 1180, 110, 230, (0, 0, 1280, 720), "rgba(108,192,210,.2)", 2)
    text(s, 72, 96, 900, 70, "Folienmuster", 60, WHITE, True, lh=70, name="Titel")
    text(s, 72, 172, 900, 26, "Zum Duplizieren: so bauen Iana und Patrick ihre Folien im gleichen Design", 20,
         PALE, lh=26)
    for i, name in enumerate(PATTERNS):
        x, y = 72 + (i // 5) * 568, 240 + (i % 5) * 70
        kit.dcard(s, x, y, 548, 58)
        text(s, x + 18, y, 60, 58, f"M{i + 1}", 20, TEAL3, True, MONO, anchor="m", lh=24, wrap=False)
        text(s, x + 80, y, 440, 58, name, 17, WHITE, True, anchor="m", lh=22)
    kit.set_notes(s, [("HINWEIS", ["Die Muster sind keine Vortragsfolien. Vor der Präsentation den ganzen Abschnitt "
                                   "„Folienmuster“ löschen oder ausblenden."])])
    return s


def m_regeln(prs, num):
    s = kit.blank(prs)
    header(s, "Wie baue ich eine Folie in diesem Design?", "circle-help", "Sechs Regeln für einheitliche Folien")
    rules = [
        ("circle-help", "Leitfrage und Titel", "Oben die Frage des Publikums (mit „?“, höchstens 58 Zeichen), "
                                               "darunter der Titel als Antwort in einem Satz."),
        ("target", "Eine Aussage pro Folie", "Höchstens 5 Punkte mit je höchstens 12 Wörtern; in 6 Sekunden lesbar."),
        ("palette", "Farben mit Bedeutung", "Navy Prognose, Teal ML-Feld, Amber Schwelle, Rot Prüfhinweis, Grün in "
                                            "Ordnung. Höchstens 4 Farben je Folie."),
        ("gauge", "Zahlen in Geist Mono", "Zahlen und Spaltennamen in Geist Mono; das Zählwerk nur für die eine "
                                          "Kernzahl eines Kapitels."),
        ("contrast", "Hell, grau, dunkel", "Weiß als Standard, Hellgrau zur Abwechslung, Dunkelblau für Merksatz oder "
                                           "Entscheidung, Split für Kapitelstarts."),
        ("panel-bottom", "Kopf- und Fußzeile", "Kapitelleiste nennt Kapitel und Person; Fußzeile nennt Canvas-Felder, "
                                               "Namen und Seitenzahl."),
    ]
    for i, (icon_name, head, body) in enumerate(rules):
        x, y = 72 + (i % 3) * 385, 146 + (i // 3) * 190
        icard(s, x, y, 366, 176, icon_name, "navy", head, body, psize=15)
    merk(s, 72, 540, 1136, 64, "Keine Kursivschrift, keine Farbverläufe, keine farbigen Seitenstreifen. Schrift IBM Plex "
         "Sans, Zahlen Geist Mono (beide in Google Fonts).")
    footer(s, (), "Team", num)
    _how(s, "Diese Folie fasst die Designsprache zusammen; sie selbst wird nicht präsentiert.",
         "Rollenfarben: Navy #084878, Teal #00718E, Amber #A86505, Rot #B3261E, Grün #2F7A33, Dunkelblau #063659, "
         "Hellgrau #F1F4F7.")
    return s


def m_karten(prs, num):
    s = kit.blank(prs)
    header(s, Q, "layout-grid", T, chapter="05")
    for i in range(3):
        icard(s, 72 + i * 385, 146, 366, 250, ["target", "flag", "shield-check"][i], ["navy", "amber", "green"][i],
              f"[Überschrift {i + 1}]", "[Zwei bis drei Zeilen Text. Eine Aussage je Karte, höchstens 12 Wörter "
                                       "je Satz.]")
    card(s, 72, 412, 1136, 120, fill=MIST, border=LINE2)
    kit.label(s, 92, 428, 400, "[Optional: Einordnung]", SOFT)
    text(s, 92, 452, 1096, 64, "[Ein Satz, der die drei Karten verbindet, z. B. Quelle, Zeitraum oder Grenze der "
         "Aussage.]", 16, INK, lh=22)
    merk(s, 72, 548, 1136, 64, "[Merksatz: die eine Aussage, die hängen bleiben soll]")
    footer(s, ("08",), "[Name]", num)
    _how(s, "Für drei gleichrangige Punkte (Befunde, Bereiche, Argumente).",
         "Icon tauschen: Bild in der Scheibe ersetzen (PNG aus docs/presentation/kiko/assets/icons oder aus dem "
         "Baukasten M10 kopieren). Scheibenfarbe = Rollenfarbe.")
    return s


def m_text_bild(prs, num):
    s = kit.blank(prs)
    header(s, Q, "image", T, chapter="05")
    kit.label(s, 72, 150, 400, "[Kurzes Label]", TEAL6)
    text(s, 72, 178, 420, 250, ["• [Punkt 1: höchstens 12 Wörter]", "• [Punkt 2: höchstens 12 Wörter]",
                                "• [Punkt 3: höchstens 12 Wörter]"], 18, INK, lh=26, gap=10)
    icard(s, 72, 440, 420, 120, "lightbulb", "amber", "[Was die Grafik zeigt]",
          "[Die Aussage der Grafik in einem Satz, damit niemand selbst suchen muss.]")
    _placeholder(s, 520, 146, 688, 420, "[Grafik oder Screenshot einfügen, 16:10; Achsen beschriften]")
    text(s, 520, 576, 688, 22, "[Quelle · Zeitraum · Einheit]", 14, SOFT, lh=20)
    footer(s, ("06",), "[Name]", num)
    _how(s, "Für eine Grafik mit Erklärung (z. B. EDA-Diagramm, Cockpit-Ansicht).",
         "Bild einfügen: Platzhalter anklicken → Bild ersetzen, oder Bild darüberlegen und Platzhalter löschen.",
         "Diagramme aus Notebooks als PNG in doppelter Auflösung exportieren; höchstens 4 Farben.")
    return s


def m_tabelle(prs, num):
    s = kit.blank(prs)
    header(s, Q, "table-2", T, chapter="02")
    rows = [["[Spalte 1]", "[Spalte 2]", "[Zahl]", "[Maßnahme]"]]
    for i in range(1, 5):
        rows.append([[(f"[Befund {i}]", {"bold": True})], [kit.code("[spaltenname]")], "[0.000 (0 %)]", "[Maßnahme]"])
    kit.table(s, 72, 146, [300, 300, 200, 336], rows, [44, 56, 56, 56, 56], right_cols=(2,), tint_rows=(2,),
              name="Tabelle Muster")
    text(s, 72, 432, 1136, 22, "[Hervorgehobene Zeile: hellteal hinterlegt, wenn sie die Aussage der Folie trägt]", 14,
         SOFT, lh=20)
    merk(s, 72, 548, 1136, 64, "[Merksatz: was aus der Tabelle folgt]")
    footer(s, ("02",), "[Name]", num)
    _how(s, "Für Übersichten mit höchstens 5 Zeilen; lange Listen gehören ins Backup.",
         "Zeile hinzufügen: Rechtsklick in die Tabelle → Zeile einfügen. Spaltennamen in Geist Mono, Zahlen "
         "rechtsbündig.")
    return s


def m_kennzahlen(prs, num):
    s = kit.blank(prs, MIST)
    header(s, Q, "gauge", T, chapter="05")
    box(s, 72, 146, 420, 250, fill=NAVY, radius=12, name="Kernzahl")
    kit.label(s, 96, 168, 360, "[Kernzahl des Kapitels]", TEAL3)
    kit.zw(s, 96, 206, "12,3", "glass", 64)
    text(s, 96, 300, 372, 80, "[Was die Zahl bedeutet, mit Einheit und Vergleich]", 16, PALE, lh=22)
    for i in range(2):
        x = 512 + i * 358
        card(s, x, 146, 338, 250)
        kit.label(s, x + 20, 168, 300, f"[Kennzahl {i + 2}]")
        text(s, x + 20, 198, 300, 56, "[0,0 %]", 44, NAVY7, True, MONO, lh=56, wrap=False)
        text(s, x + 20, 264, 300, 110, "[Vergleich oder Einordnung: gegenüber was, in welchem Zeitraum]", 15, MUTED,
             lh=21)
    icard(s, 72, 412, 1136, 110, "ruler", "teal", "[Woher die Zahlen kommen]",
          "[Quelle, Zeitraum, Definition. Eine Zahl ohne Vergleich ist keine Aussage.]")
    merk(s, 72, 540, 1136, 64, "[Merksatz: die Zahl in Worten]")
    footer(s, ("06", "08"), "[Name]", num)
    _how(s, "Für eine Kernzahl plus zwei Nebenwerte.",
         "Zählwerk: Jede Ziffer ist ein eigenes Kästchen. Ziffern einzeln überschreiben; für mehr Stellen ein "
         "Kästchen duplizieren. Pro Kapitel höchstens ein Zählwerk.",
         "Nebenwerte in Geist Mono, Einheit immer nennen.")
    return s


def m_prozess(prs, num):
    s = kit.blank(prs)
    header(s, Q, "workflow", T, chapter="06")
    for i in range(4):
        x = 72 + i * 290
        card(s, x, 146, 266, 220)
        marker(s, x + 34, 180, i + 1)
        text(s, x + 20, 212, 226, 26, f"[Schritt {i + 1}]", 18, NAVY7, True, lh=24)
        text(s, x + 20, 244, 226, 110, "[Was passiert, wer ist zuständig, was kommt heraus?]", 15, MUTED, lh=21)
        if i < 3:
            kit.chevron(s, x + 278, 256)
    box(s, 72, 384, 1136, 140, fill=NAVY, radius=12, name="Ergebnis")
    disc(s, 92, 420, "flag", "light", 36)
    text(s, 144, 404, 1040, 24, "[Ergebnis oder Entscheidung am Ende]", 18, WHITE, True, lh=24)
    text(s, 144, 432, 1040, 76, "[Ein bis zwei Sätze: was nach dem letzten Schritt feststeht und wer es nutzt.]", 16,
         PALE, lh=22)
    text(s, 72, 540, 1136, 22, "[Optional: Bedingung oder Grenze des Ablaufs]", 14, SOFT, lh=20)
    footer(s, ("07",), "[Name]", num)
    _how(s, "Für Abläufe mit drei bis fünf Schritten (Workflow, nächste Schritte, Prüfprozess).",
         "Schritt hinzufügen: Karte, Nummer und Chevron gemeinsam markieren, duplizieren, Abstände angleichen.")
    return s


def m_split(prs, num):
    s = kit.blank(prs)
    box(s, 0, 0, 512, kit.FOOT_Y, fill=NAVY, name="Split links")
    kit.ring_arc(s, 502, 20, 209, (0, 0, 512, kit.FOOT_Y), "rgba(108,192,210,.2)", 2)
    text(s, 56, 40, 408, 86, "0X", 96, kit.mix(TEAL3, NAVY, .5), True, MONO, lh=86.4, wrap=False)
    text(s, 56, 136, 420, 90, "[Kapitelname]", 38, WHITE, True, lh=42, tracking=-0.02, name="Titel")
    kit.dcard(s, 56, 400, 408, 200)
    kit.label(s, 76, 420, 360, "[Einstieg: Beispiel oder Frage]", TEAL3)
    text(s, 76, 448, 368, 140, "[Ein konkreter Fall, der neugierig macht und später aufgelöst wird.]", 18, WHITE,
         lh=25)
    disc(s, 560, 38, "circle-help", "teal", 32, name="Leitfrage-Scheibe")
    text(s, 604, 40.5, 560, 27, Q, 20, TEAL6, lh=27, wrap=False, name="Leitfrage")
    for i in range(3):
        y = 150 + i * 130
        marker(s, 590, y + 16, i + 1)
        text(s, 620, y + 3, 560, 26, f"[Punkt {i + 1}]", 18, NAVY7, True, lh=24)
        text(s, 620, y + 31, 560, 70, "[Ein bis zwei Sätze Erklärung]", 15, MUTED, lh=21)
        if i < 2:
            line(s, 620, y + 112, 1208, y + 112, LINE2, 1)
    footer(s, (), "[Name]", num)
    _how(s, "Für den Start eines Kapitels (wie Kikos Folie „Methodik und Modell“): links Nummer und Name des "
            "Kapitels, rechts der Ablauf.",
         "Keine Kapitelleiste auf dieser Folie; die große Nummer ersetzt sie.")
    return s


def m_dunkel(prs, num):
    s = kit.blank(prs, NAVY)
    header(s, Q, "lightbulb", T, dark=True, chapter="06")
    text(s, 72, 170, 1000, 110, "[Die eine Aussage dieser Folie, groß und in höchstens zwei Zeilen]", 34, WHITE, True,
         lh=44)
    for i in range(2):
        icard(s, 72 + i * 578, 318, 558, 150, ["check", "triangle-alert"][i], "light", f"[Punkt {i + 1}]",
              "[Begründung oder Beleg in ein bis zwei Sätzen]", dark=True)
    merk(s, 72, 494, 1136, 70, "[Merksatz oder Entscheidung, die das Publikum mitnehmen soll]", dark=True)
    footer(s, ("07",), "[Name]", num, dark=True)
    _how(s, "Für Entscheidungen, Merksätze oder Wendepunkte; höchstens eine dunkle Folie pro Kapitel.",
         "Auf Dunkelblau: Text Weiß, Nebentext Hellblau (#BBD7EA), Akzente Hellteal (#6CC0D2).")
    return s


def m_screenshot(prs, num):
    s = kit.blank(prs)
    header(s, Q, "layout-dashboard", T, chapter="05")
    _placeholder(s, 72, 146, 690, 470, "[Screenshot einfügen und auf 690 × 470 px zuschneiden]")
    for n, (x, y) in enumerate([(200, 230), (520, 330), (640, 520)], 1):
        marker(s, x, y, n, fill=RED if n == 2 else NAVY7)
    for n in range(1, 4):
        y = 150 + (n - 1) * 130
        marker(s, 802, y + 15, n, fill=RED if n == 2 else NAVY7)
        text(s, 830, y + 3, 378, 24, f"[Hinweis {n}: Was sieht man?]", 17, NAVY7, True, lh=23)
        text(s, 830, y + 29, 378, 80, "[Wofür die Fachabteilung das braucht]", 15, MUTED, lh=21)
    text(s, 786, 590, 422, 22, "[Datenstand · Prototyp oder Live]", 14, SOFT, lh=20)
    footer(s, ("07", "08"), "[Name]", num)
    _how(s, "Für Dashboard- oder Tool-Ansichten (wie Patricks Verbrauchs-Cockpit).",
         "Nummernkreise auf die Stelle im Screenshot ziehen; Rot nur für den Prüfhinweis selbst.",
         "Nur echte Screenshots mit Projektdaten verwenden, keine Designvorlagen mit Beispielzahlen.")
    return s


def m_baukasten(prs, num):
    s = kit.blank(prs)
    header(s, "Welche Elemente kann ich kopieren?", "layers", "Baukasten: Scheiben, Chips, Bänder, Zählwerk")
    kit.label(s, 72, 146, 400, "Scheiben (Icon-Farbe = Ton)", SOFT)
    tones = list(kit.K["TONES"])
    light_tones = [t for t in tones if t not in ("light", "lamber", "glass")]
    for i, tone in enumerate(light_tones):
        x = 72 + i * 84
        disc(s, x + 13, 172, "flag", tone, 40, name=f"Scheibe {tone}")
        text(s, x, 218, 70, 18, tone, 13, SOFT, font=MONO, align="c", lh=18, wrap=False)
    box(s, 72 + len(light_tones) * 84, 164, 1136 - len(light_tones) * 84, 84, fill=NAVY, radius=10,
        name="Dunkler Grund")
    for i, tone in enumerate(("light", "lamber", "glass")):
        x = 72 + len(light_tones) * 84 + 16 + i * 84
        disc(s, x + 13, 172, "flag", tone, 40, name=f"Scheibe {tone}")
        text(s, x, 218, 70, 18, tone, 13, PALE, font=MONO, align="c", lh=18, wrap=False)
    kit.label(s, 72, 268, 400, "Chips und Nummern", SOFT)
    x = 72
    for fill, ink, t in ((TINT, TEAL7, "16.830 Zeilen"), (NAVY7, WHITE, "16.800 Zeilen"), (WHITE, INK, "Chip weiß")):
        w = kit.measure(t, 16, True, MONO) + 28
        box(s, x, 294, w, 32, fill=fill, line=LINE if fill == WHITE else None, radius=16, name="Chip")
        text(s, x, 294, w, 32, t, 16, ink, True, MONO, "c", "m", lh=20, wrap=False)
        x += w + 16
    marker(s, x + 20, 310, 1)
    marker(s, x + 64, 310, 2, fill=RED)
    kit.label(s, 680, 268, 400, "Zählwerk", SOFT)
    kit.zw(s, 680, 290, "9,5", "navy", 36)
    kit.zw(s, 800, 290, "+2,30", "red", 36)
    kit.label(s, 72, 356, 400, "Merksatz hell und dunkel", SOFT)
    merk(s, 72, 380, 558, 64, "Merksatz auf hellem Grund")
    box(s, 650, 372, 558, 80, fill=NAVY, radius=10, name="Dunkler Grund")
    merk(s, 658, 380, 542, 64, "Merksatz auf dunklem Grund", dark=True)
    kit.label(s, 72, 468, 400, "Karte mit Icon", SOFT)
    icard(s, 72, 492, 558, 110, "target", "teal", "Kopfzeile der Karte", "Text der Karte in Plex Sans 15 px, "
          "Farbe Grau (#4E5A68).")
    kit.label(s, 650, 468, 400, "Pfeile", SOFT)
    icon(s, "arrow-right", TEAL6, 650, 500, 28)
    kit.chevron(s, 710, 514)
    footer(s, ("01", "03"), "Team", num)
    _how(s, "Elemente markieren, kopieren (Strg+C) und auf der eigenen Folie einfügen (Strg+V).",
         "Scheibe mit anderem Icon: Bild in der Scheibe ersetzen. Icons sind Lucide-Icons (ISC-Lizenz), als PNG "
         "unter docs/presentation/kiko/assets/icons/<name>__<FARBE>.png.",
         "Neue Icons erzeugen: node scripts/render_icons.mjs <Ordner> '[{\"name\":\"flag\",\"color\":\"#FFFFFF\"}]'.")
    return s


BUILDERS = [m_regeln, m_karten, m_text_bild, m_tabelle, m_kennzahlen, m_prozess, m_split, m_dunkel, m_screenshot,
            m_baukasten]
