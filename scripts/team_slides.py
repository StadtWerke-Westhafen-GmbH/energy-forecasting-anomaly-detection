"""Team-Folien: Titel, Agenda, Ianas und Patricks Entwürfe, Schluss, Backup-Ergänzungen.

Quellen: Ianas Folien in der Team-Vorlage (Ausgangssituation, Datenstruktur, Datenqualität,
Datenqualität im Detail) und der Bericht (1.1–1.4, 3.1, 3.6, 3.7, 4.3–4.5). Entwürfe für Iana
und Patrick tragen das in den Notizen; Zahlen stehen wörtlich wie in den Quellen.
Jede Funktion hat die Form ``make(prs, num) -> Folie``.
"""

from __future__ import annotations

import team_kit as kit
from team_kit import (AMBER, GREEN, INK, LINE, LINE2, MIST, MONO, MUTED, NAVY, NAVY7, NAVY9, PALE, RED, SOFT,
                      TEAL3, TEAL6, TEAL7, TINT, WHITE, box, card, code, disc, footer, header, icard, icon, line,
                      marker, merk, text)

PERSONS = [  # Sprechreihenfolge
    ("Iana Kraievska", "Datenmanagement und Datenqualität", "database", ["01", "02"]),
    ("Kiko Ramon Lukas", "Machine Learning und Evaluation", "trees", ["03", "04"]),
    ("Patrick Olmo Hederer", "EDA und Visualisierung", "chart-column", ["05", "06"]),
]
AGENDA = [  # Nummer, Kapitel, Minuten, Leitfrage der ersten Folie
    ("01", "Ausgangssituation", "3 min", "Warum braucht SWW eine Prognose je Zähler?"),
    ("02", "Daten und Datenqualität", "4 min", "Welche Daten stehen zur Verfügung?"),
    ("03", "ML Canvas", "2,5 min", "Passt vom Nutzen bis zur Wartung alles zusammen?"),
    ("04", "Methodik und Modell", "7 min", "Wie wird aus Daten ein Prüfhinweis?"),
    ("05", "Ergebnisse", "5 min", "Was hat das Projekt für SWW ergeben?"),
    ("06", "Empfehlungen und Ausblick", "4 min", "Was empfehlen wir SWW?"),
]
PROJECT_QUESTION = ("Wie können historische Verbrauchsdaten und weitere Einflussfaktoren genutzt werden, um den "
                    "monatlichen Energieverbrauch zuverlässig zu prognostizieren und auffällige Abweichungen "
                    "frühzeitig zu erkennen?")
DATE = "01.10.2026"
COCKPIT = kit.TEAM_DIR / "assets" / "verbrauchs-cockpit-prueffall.png"
COCKPIT_BOX = (72, 146, 690, 479)                                  # Lage des Screenshots (1440 × 1000 px)
COCKPIT_SPOTS = [(130, 250), (700, 165), (1310, 390), (1330, 760)]  # erklärte Stellen, Screenshot-px
COCKPIT_MARKERS = [(50, 266), (407, 196), (665, 329), (680, 539)]   # Marker daneben, Folien-px


def _rings(s, cx, cy, clip):
    kit.ring_arc(s, cx, cy, 230, clip, "rgba(108,192,210,.2)", 2)
    kit.ring_arc(s, cx - 10, cy + 10, 150, clip, "rgba(108,192,210,.12)", 2)


# --------------------------------------------------------------------------- Titel und Agenda


def titel(prs, num):
    s = kit.blank(prs)
    box(s, 0, 0, 560, 720, fill=NAVY, name="Split links")
    _rings(s, 560, 20, (0, 0, 560, 720))
    box(s, 56, 52, 188, 70, fill=WHITE, radius=10, name="Logo-Grund")
    kit.picture(s, kit.BUILD["_small_logo"](160), 72, 63, h=48, name="Logo")
    text(s, 56, 214, 460, 18, "IHK-Zertifizierung Data Analyst · Gruppe 6", 14, TEAL3, True, lh=18,
         tracking=.08, upper=True, wrap=False)
    text(s, 56, 244, 470, 200, "Prognose des monatlichen Energieverbrauchs und Erkennung von Anomalien", 38,
         WHITE, True, lh=46, tracking=-0.02, name="Titel")
    text(s, 56, 600, 460, 24, f"{DATE} · Gruppe 6 · StadtWerke Westhafen", 18, PALE, lh=24, wrap=False)

    disc(s, 616, 60, "lightbulb", "amber", 32, name="Leitfrage-Scheibe")
    text(s, 660, 66, 400, 20, "Projektfrage", 14, TEAL6, True, lh=20, tracking=.08, upper=True, wrap=False)
    text(s, 616, 110, 592, 160, PROJECT_QUESTION, 22, INK, lh=31, name="Projektfrage")
    text(s, 616, 312, 400, 20, "Wer spricht", 14, TEAL6, True, lh=20, tracking=.08, upper=True, wrap=False)
    for i, (name, role, icon_name, chapters) in enumerate(PERSONS):
        y = 344 + i * 92
        if i:
            line(s, 616, y - 12, 1208, y - 12, LINE2, 1)
        disc(s, 616, y + 6, icon_name, "navy", 44)
        text(s, 676, y, 520, 26, name, 21, INK, True, lh=26)
        text(s, 676, y + 28, 520, 20, role, 15, MUTED, lh=20)
        chap = " · ".join(f"{nr} {next(a[1] for a in AGENDA if a[0] == nr)}" for nr in chapters)
        text(s, 676, y + 51, 520, 20, chap, 14, TEAL7, font=MONO, lh=20)
    kit.set_notes(s, [
        ("STICHWORTE", ["• Begrüßung, Gruppe 6, drei Rollen", "• Projektfrage einmal laut vorlesen"]),
        ("SPRECHTEXT", ["Guten Tag, wir sind Gruppe 6. Unser Projekt für die StadtWerke Westhafen beantwortet eine "
                        "Frage: wie wir aus historischen Verbrauchsdaten den Verbrauch im nächsten Monat je Zähler "
                        "vorhersagen und Auffälliges früher erkennen.",
                        "Wer eröffnet, legt das Team fest; Vorschlag: Iana, weil sie mit der Ausgangssituation "
                        "beginnt."]),
    ])
    return s


def agenda(prs, num):
    s = kit.blank(prs)
    header(s, "Wer erzählt welchen Teil?", "list-checks", "Sechs Kapitel, drei Stimmen, rund 27 Minuten")
    for p, (name, role, icon_name, chapters) in enumerate(PERSONS):
        x = 72 + p * 385
        disc(s, x, 146, icon_name, "navy", 40)
        text(s, x + 52, 145, 314, 24, name.split()[0], 20, INK, True, lh=24)
        text(s, x + 52, 169, 314, 20, role, 14, MUTED, lh=19)
        for c, nr in enumerate(chapters):
            _, chapter, minutes, question = next(a for a in AGENDA if a[0] == nr)
            y = 206 + c * 164
            card(s, x, y, 366, 150)
            text(s, x + 18, y + 16, 60, 34, nr, 28, TEAL6, True, MONO, lh=34, wrap=False)
            box(s, x + 366 - 18 - 74, y + 18, 74, 26, fill=TINT, radius=13)
            text(s, x + 366 - 18 - 74, y + 18, 74, 26, minutes, 14, TEAL7, True, MONO, "c", "m", lh=18, wrap=False)
            text(s, x + 18, y + 58, 330, 26, chapter, 20, NAVY7, True, lh=25)
            text(s, x + 18, y + 90, 330, 48, question, 15, MUTED, lh=21)
    # Zeitleiste: Anteil der Kapitel an rund 26 Minuten Vortrag
    mins = [3, 4, 2.5, 7, 5, 4]
    total, x = sum(mins), 72.0
    for i, (m, (nr, *_)) in enumerate(zip(mins, AGENDA)):
        w = 1136 * m / total
        box(s, x + (2 if i else 0), 548, w - (2 if i else 0), 30, fill=[NAVY7, "#2A6A9A"][i % 2],
            name=f"Zeit {nr}")
        text(s, x + 8, 548, w - 12, 30, nr, 14, WHITE, True, MONO, anchor="m", lh=18, wrap=False)
        x += w
    text(s, 72, 588, 1136, 22, "Rund 26 Minuten Vortrag plus Übergaben; Titel und Agenda eine Minute. "
         "Fragen im Anschluss.", 15, SOFT, lh=21)
    footer(s, (), "Iana", num)
    kit.set_notes(s, [
        ("STICHWORTE", ["• Drei Personen, je zwei Kapitel", "• Übergaben: Iana → Kiko → Patrick"]),
        ("SPRECHTEXT", ["Wir sind zu dritt und haben das Projekt nach Rollen aufgeteilt. Ich beginne mit der "
                        "Ausgangssituation und den Daten, Kiko zeigt Canvas, Methodik und Modell, Patrick die "
                        "Ergebnisse und unsere Empfehlungen."]),
        ("HINWEIS", ["Minuten sind ein Vorschlag: Kikos Teil ist mit 9:30 min gestoppt, Iana und Patrick bitte "
                     "einmal mit Stoppuhr prüfen."]),
    ])
    return s


# --------------------------------------------------------------------------- Iana


def iana_ausgangssituation(prs, num):
    s = kit.blank(prs)
    header(s, "Warum braucht SWW eine Prognose je Zähler?", "building-2",
           "Planung per Hand, Auffälliges erst im Quartal", chapter="01")
    # Organisation
    card(s, 72, 146, 330, 250)
    disc(s, 90, 164, "building-2", "navy", 40)
    kit.label(s, 142, 176, 240, "Organisation")
    text(s, 90, 218, 300, 24, "StadtWerke Westhafen GmbH", 18, INK, True, lh=24)
    text(s, 90, 246, 300, 70, "700 gewerbliche, industrielle und kommunale Großkunden im Hamburger Hafengebiet",
         15, MUTED, lh=21)
    for i, (val, lbl) in enumerate([("700", "Großkunden"), ("180 Mio. EUR", "Jahresumsatz, rund")]):
        x = 90 + i * 120
        text(s, x, 324, 200, 32, val, 22 if i == 0 else 18, NAVY7, True, MONO, lh=32, wrap=False)
        text(s, x, 358, 200, 20, lbl, 14, SOFT, lh=20)
    # Bisher
    card(s, 72, 410, 330, 130, fill=MIST, border=LINE2)
    kit.label(s, 90, 426, 240, "Bisher", SOFT)
    text(s, 90, 450, 300, 84, ["• Mengen per Hand fortgeschrieben", "• Monatsauswertungen rückblickend",
                               "• Kein automatisiertes Prognosesystem"], 15, INK, lh=21, gap=4)
    # Problem -> Folge
    kit.label(s, 424, 146, 300, "Problem", SOFT)
    kit.label(s, 812, 146, 300, "Folge", SOFT)
    rows = [
        ("chart-spline", "navy", "Ungenaue Verbrauchsprognosen",
         "Die Monatsmengen werden bisher manuell fortgeschrieben.",
         "coins", "amber", "Steigende Beschaffungskosten",
         "Abweichungen erzwingen Käufe und Verkäufe am Spotmarkt.", "Energiebeschaffung · Stefan Lechtenberg"),
        ("hourglass", "navy", "Anomalien werden spät erkannt",
         "Auffällige Monatswerte fallen oft erst im Quartal auf.",
         "triangle-alert", "red", "Technische Probleme spät erkannt",
         "Messfehler, Abrechnungsprobleme und Störungen werden spät geprüft.", "Netzmanagement · Anke Bürger"),
    ]
    for r, (i1, t1, h1, b1, i2, t2, h2, b2, who) in enumerate(rows):
        y = 170 + r * 120
        icard(s, 424, y, 356, 108, i1, t1, h1, b1, psize=14.5)
        icon(s, "arrow-right", TEAL6, 784, y + 42, 24)
        icard(s, 812, y, 396, 108, i2, t2, h2, b2, psize=14.5)
        text(s, 877, y + 84, 314, 18, who, 13, TEAL7, True, lh=18, wrap=False)
    # Ziel und Abgrenzung
    icard(s, 424, 414, 480, 126, "target", "teal", "Projektziel",
          "Reproduzierbarer Python-Workflow: Folgemonatsprognose je Zähler, Vergleich mit einfachen Regeln "
          "und Prüfhinweise.", fill=TINT, border=TINT)
    icard(s, 918, 414, 290, 126, "ban", "ring", "Nicht im Projekt",
          "Produktivanbindung, automatische Maßnahmen, Euro-Einsparungen (Pilot).", psize=14)
    merk(s, 72, 556, 1136, 64, "Projektnutzen: genauer beschaffen und Auffälliges monatlich statt quartalsweise "
         "prüfen. Die Entscheidung bleibt beim Fachbereich.")
    footer(s, ("01", "07"), "Iana", num)
    kit.draft_notes(s, "Abschnitt 1.1–1.4 und Ianas Vorlage-Folie „Ausgangssituation“", [
        "Die StadtWerke Westhafen versorgen im Hamburger Hafengebiet 700 Großkunden aus Gewerbe, Industrie und "
        "Kommunen, bei rund 180 Millionen Euro Jahresumsatz.",
        "Zwei Probleme: Die Beschaffung schreibt Monatsmengen per Hand fort. Liegt sie daneben, muss am Spotmarkt "
        "nachgekauft oder verkauft werden, das kostet. Und auffällige Verbräuche fallen oft erst in der "
        "Quartalsauswertung auf, Messfehler oder Störungen werden also spät geprüft.",
        "Unser Ziel ist deshalb ein reproduzierbarer Workflow: eine Prognose je Zähler für den nächsten Monat und "
        "ein Prüfhinweis, wenn der Istwert ungewöhnlich stark abweicht. Nicht Teil des Projekts sind eine "
        "Produktivanbindung, automatische Maßnahmen und Euro-Einsparungen; die misst erst ein Pilot.",
        "Wie wir die Daten dafür aufbereitet haben, zeige ich jetzt."],
        keywords=["700 Großkunden, 180 Mio. EUR", "Problem → Folge, zweimal", "Ziel und Abgrenzung"],
        todo=["Ansprechpartner (Lechtenberg, Bürger) stammen aus Bericht und Canvas; bei Bedarf streichen."])
    return s


def iana_datenstruktur(prs, num):
    s = kit.blank(prs, MIST)
    header(s, "Welche Daten stehen zur Verfügung?", "database", "700 Zähler, 24 Monate, sechs Merkmalsgruppen",
           chapter="02")
    groups = [
        ("id-card", "Identifikation", "Zähler-ID, Kunden-ID (700 eindeutige)"),
        ("zap", "Verbrauch", "Verbrauch, Vormonats-, 3-Monats-Durchschnitts- und Vorjahresverbrauch"),
        ("thermometer", "Wetter", "Temperatur, Heizgradtage"),
        ("calendar", "Kalender", "Monat/Jahr (24 eindeutige), Arbeitstage, Feiertage im Monat"),
        ("factory", "Produktion & Betrieb", "Produktionsplan-Index, Wartung"),
        ("handshake", "Kunden & Vertrag", "Kundentyp, Vertragsleistung"),
    ]
    for i, (icon_name, head, body) in enumerate(groups):
        x, y = 72 + (i % 3) * 385, 146 + (i // 3) * 134
        icard(s, x, y, 366, 120, icon_name, "navy", head, body, psize=15)
    box(s, 72, 424, 1136, 116, fill=NAVY, radius=12, name="Kennzahlen")
    stats = [("16.830 → 16.800", "Zeilen vor und nach der Bereinigung"), ("16", "Spalten"), ("700", "Zähler"),
             ("24", "Monate · 01/2024–12/2025")]
    xs = [100, 520, 700, 880]
    for (val, lbl), x in zip(stats, xs):
        text(s, x, 446, 400, 44, val, 34, WHITE, True, MONO, lh=44, wrap=False)
        text(s, x, 494, 320, 22, lbl, 15, PALE, lh=21)
    merk(s, 72, 556, 1136, 64, "Jede Zeile ist ein Zähler-Monat: 700 Zähler × 24 Monate = 16.800 Zeilen.")
    footer(s, ("02", "04"), "Iana", num)
    kit.draft_notes(s, "Anhang B.1 und Ianas Vorlage-Folie „Datenstruktur“", [
        "Grundlage sind Monatswerte von 700 Zählern über 24 Monate, Januar 2024 bis Dezember 2025.",
        "Die Spalten lassen sich in sechs Gruppen ordnen: Identifikation, Verbrauch mit seiner Historie, Wetter, "
        "Kalender, Produktion und Betrieb sowie Kunde und Vertrag.",
        "Vor der Bereinigung waren es 16.830 Zeilen, danach 16.800. Das passt genau: 700 Zähler mal 24 Monate. "
        "Was wir dabei gefunden haben, zeigt die nächste Folie."],
        keywords=["700 × 24 = 16.800", "sechs Gruppen", "16.830 → 16.800"],
        todo=["„Heiztage“ aus der Vorlage als „Heizgradtage“ geschrieben (so heißt die Größe im Bericht)."])
    return s


def iana_datenqualitaet(prs, num):
    s = kit.blank(prs)
    header(s, "Was war an den Rohdaten nicht in Ordnung?", "shield-check",
           "Vier Problemarten, jede mit begründeter Maßnahme", chapter="02")
    rows = [
        ["Problem", "Betroffene Spalte", "Umfang", "Maßnahme"],
        [[("Duplikate", {"bold": True})], "ganze Zeile", "30 (0,18 %)", "Entfernt"],
        [[("Fehlende Werte", {"bold": True})], [[code("vorjahr_monat_verbrauch_kwh")], [code("vormonat_verbrauch_kwh")]],
         [["8.400 (50 %)"], ["700 (4 %)"]], "Strukturell bedingt → nicht imputiert"],
        [[("Inkonsistente Werte", {"bold": True})], [[code("monat")], [code("kundentyp")]],
         [["11.316 (67 %)"], ["505 (3 %)"]], "Datumsformat und Kategorien vereinheitlicht"],
        [[("Ausreißer / fehlerhafte Werte", {"bold": True})], [[code("verbrauch_kwh")]], "20 (0,12 %)",
         "Gegen die technisch mögliche Monatsenergie geprüft: alle unmöglich; 10 aus 2024 nicht trainiert, "
         "10 aus 2025 im Test belassen und alle markiert"],
    ]
    kit.table(s, 72, 146, [250, 300, 170, 416], rows, [44, 46, 64, 64, 76], name="Tabelle Datenqualität")
    card(s, 72, 456, 560, 92)
    kit.label(s, 90, 470, 300, "Vom Rohdatensatz zur Basis", SOFT)
    x = 90
    for i, chip in enumerate(["16.830 Zeilen", "− 30 Duplikate", "16.800 Zeilen"]):
        w = kit.measure(chip, 15, True, MONO) + 22
        box(s, x, 500, w, 32, fill=NAVY7 if i == 2 else TINT, radius=16, name="Chip")
        text(s, x, 500, w, 32, chip, 15, WHITE if i == 2 else TEAL7, True, MONO, "c", "m", lh=20, wrap=False)
        x += w
        if i < 2:
            icon(s, "arrow-right", TEAL6, x + 6, 506, 20)
            x += 32
    icard(s, 648, 456, 560, 92, "table-2", "ring", "Weitere Befunde im Backup B7",
          "u. a. 672 MWh-Werte → kWh, fehlende Temperaturen, 3 fehlende Verbrauchswerte", psize=14)
    merk(s, 72, 556, 1136, 64, "Lastspitzen sind nicht automatisch Messfehler: Geprüft wird gegen die technisch "
         "mögliche Monatsenergie (Vertragsleistung × Monatsstunden).")
    footer(s, ("02",), "Iana", num)
    kit.draft_notes(s, "Anhang C, Abschnitt 3.6 (Ianas Fazit) und Ianas Vorlage-Folie „Datenqualität“", [
        "Bei der Prüfung der Rohdaten haben wir vier Arten von Problemen gefunden.",
        "30 Zeilen waren doppelt, die haben wir entfernt. Fehlende Vorjahres- und Vormonatswerte sind strukturell "
        "bedingt: Für Januar 2024 gibt es schlicht keinen Vormonat im Datensatz. Die haben wir bewusst nicht "
        "aufgefüllt.",
        "Die Monatsangaben lagen in verschiedenen Formaten vor, die Kundentypen in verschiedenen Schreibweisen; "
        "beides haben wir vereinheitlicht.",
        "Und 20 Verbrauchswerte waren auffällig hoch. Die haben wir nicht einfach gelöscht, sondern gegen die "
        "technisch mögliche Monatsenergie geprüft, also Vertragsleistung mal Stunden im Monat. Alle 20 lagen "
        "darüber, waren also physikalisch unmöglich: Die zehn aus 2024 haben wir vom Training ausgeschlossen, "
        "die zehn aus 2025 im Test gelassen, und das Verfahren hat alle zehn markiert. Hohe, aber mögliche Werte "
        "blieben erhalten.",
        "Damit übergebe ich an Kiko, der zeigt, wie daraus ein Modell wird."],
        keywords=["vier Problemarten", "nicht imputiert: strukturell", "Lastspitze ≠ Messfehler", "→ Kiko"],
        todo=["Spaltennamen wie im Datensatz (kundentyp, vorjahr_monat_verbrauch_kwh) statt der Kurzformen der "
              "Vorlage.", "Übergabesatz an Kiko am Ende."])
    return s


# --------------------------------------------------------------------------- Patrick


def patrick_ergebnisse(prs, num):
    s = kit.blank(prs)
    header(s, "Was hat das Projekt für SWW ergeben?", "chart-column", "Genauer planen, früher prüfen, sauber messen",
           chapter="05")
    cols = [
        ("chart-spline", "navy", "Energiebeschaffung", "Stefan Lechtenberg", "−15,9 %",
         "weniger Prognosefehler (RMSE) als die beste einfache Regel; Test 2025: 10.922 → 9.188 kWh"),
        ("flag", "amber", "Netzmanagement", "Anke Bürger", "9,5 / Monat",
         "Prüfhinweise statt Quartalsauswertung: 114 Hinweise bei 107 Zählern im Jahr 2025"),
        ("shield-check", "green", "Datenanalyse", "Henrik Maaß", "10 von 10",
         "physikalisch unmöglichen Werten 2025 markiert; Workflow reproduzierbar, Schwelle dokumentiert"),
    ]
    for i, (icon_name, tone, dept, who, big, body) in enumerate(cols):
        x = 72 + i * 385
        card(s, x, 146, 366, 236)
        disc(s, x + 18, 164, icon_name, tone, 40)
        kit.label(s, x + 70, 166, 280, dept)
        text(s, x + 70, 186, 280, 20, who, 14, MUTED, lh=20)
        text(s, x + 18, 222, 330, 52, big, 40, NAVY7, True, MONO, lh=52, wrap=False)
        text(s, x + 18, 282, 330, 90, body, 15, INK, lh=21)
    box(s, 72, 398, 1136, 142, fill=MIST, radius=12, name="EDA")
    kit.label(s, 92, 414, 400, "Aus der EDA", TEAL6)
    eda = [("users", "92 % der Streuung liegen zwischen den Zählern",
            "Darum normieren wir auf Vollaststunden: Anschlüsse werden vergleichbar."),
           ("filter-x", "Korrelation ist noch kein Treiber",
            "Wetter- und Feiertagseffekte sind teils von der saisonalen Produktion überlagert.")]
    for i, (icon_name, head, body) in enumerate(eda):
        x = 92 + i * 560
        disc(s, x, 444, icon_name, "ring", 34)
        text(s, x + 48, 444, 490, 22, head, 16, NAVY7, True, lh=21)
        text(s, x + 48, 468, 490, 60, body, 15, MUTED, lh=21)
    merk(s, 72, 556, 1136, 64, "Ein Prüfhinweis ist noch keine bestätigte Anomalie. Euro-Wirkung und "
         "Trefferquote misst erst der Pilot.")
    footer(s, ("08",), "Patrick", num)
    kit.draft_notes(s, "Abschnitte 3.6, 4.3 und 4.4; Zahlen wie in Kikos Folien", [
        "Was hat das Projekt den drei Bereichen gebracht?",
        "Für die Energiebeschaffung: Die Prognose je Zähler liegt im Testjahr 2025 um 15,9 Prozent genauer als die "
        "beste einfache Regel.",
        "Für das Netzmanagement: Statt einer Quartalsauswertung gibt es im Schnitt 9,5 Prüfhinweise pro Monat, "
        "eine Menge, die man tatsächlich bearbeiten kann.",
        "Für die Datenanalyse: Alle zehn physikalisch unmöglichen Werte aus 2025 wurden markiert, und der Weg dahin "
        "ist reproduzierbar dokumentiert.",
        "Aus meiner explorativen Analyse kamen zwei Entscheidungen: 92 Prozent der Streuung liegen zwischen den "
        "Zählern, deshalb die Normierung auf Vollaststunden. Und eine Korrelation ist noch kein Treiber: Wetter- "
        "und Feiertagseffekte waren teils von der Produktion überlagert."],
        keywords=["drei Bereiche, drei Zahlen", "EDA: 92 % → VLS", "Hinweis ≠ Anomalie"],
        todo=["Kiko zeigt RMSE, Baseline und Treiber bereits; hier nur die Wirkung je Bereich nennen, nicht "
              "wiederholen.", "EDA-Aussagen bei Bedarf durch eigene Grafik ersetzen (Muster „Text + Bild“)."])
    return s


def patrick_cockpit(prs, num):
    s = kit.blank(prs)
    header(s, "Wie arbeitet die Fachabteilung damit?", "layout-dashboard",
           "Das Verbrauchs-Cockpit führt vom Hinweis zum Prüffall", chapter="05")
    x0, y0, w, h = COCKPIT_BOX
    box(s, x0 - 1, y0 - 1, w + 2, h + 2, fill=WHITE, line=LINE, name="Screenshot-Rahmen")
    kit.picture(s, str(COCKPIT), x0, y0, w, h, name="Screenshot Verbrauchs-Cockpit")
    for n, (mx, my) in enumerate(COCKPIT_MARKERS, 1):  # neben der Stelle, damit sie sichtbar bleibt
        marker(s, mx, my, n, fill=RED if n == 3 else NAVY7, d=26)
    items = [
        ("Rollen statt Rohdaten", "Beschaffung sieht die Verbrauchsprognose, Netzmanagement die 114 Prüfhinweise "
                                  "und den einzelnen Prüffall."),
        ("Ein Fall auf einen Blick", "Erwartet, gemessen, Abweichung und Toleranz des Anschlusses stehen oben."),
        ("Verlauf mit Korridor", "Ist gegen Prognose über das Jahr; der Prüfhinweis ist rot markiert."),
        ("Einordnung unter allen Zählern", "Die Verteilung zeigt, wie ungewöhnlich die Abweichung im Monat ist."),
    ]
    for n, (head, body) in enumerate(items, 1):
        y = 150 + (n - 1) * 110
        marker(s, 802, y + 15, n, fill=RED if n == 3 else NAVY7)
        text(s, 830, y + 3, 378, 24, head, 17, NAVY7, True, lh=23)
        text(s, 830, y + 29, 378, 66, body, 15, MUTED, lh=21)
    text(s, 786, 600, 422, 22, "Prototyp mit retrospektiven Daten 2025, keine Live-Anbindung.", 14, SOFT, lh=20)
    footer(s, ("07", "08"), "Patrick", num)
    kit.draft_notes(s, "Abschnitt 4.5 und Anhang E; Screenshot aus dem Verbrauchs-Cockpit", [
        "So sieht das im Alltag aus. Links wählt man nach Rolle: Die Beschaffung sieht die Verbrauchsprognose, das "
        "Netzmanagement die Prüfhinweise, 2025 waren es 114.",
        "Öffnet man einen Fall, stehen oben erwarteter und gemessener Verbrauch, die Abweichung und die Toleranz "
        "dieses Anschlusses.",
        "Darunter der Verlauf über das Jahr mit dem erwarteten Korridor; der rote Kreis ist der Prüfhinweis.",
        "Und rechts unten die Einordnung: Wie ungewöhnlich ist diese Abweichung im Vergleich zu allen Zählern im "
        "selben Monat?"],
        keywords=["nach Rolle", "Fall auf einen Blick", "Korridor", "Einordnung"],
        todo=["Screenshot zeigt Stand des Prototyps (Fall ZL-00561, 12/2025); bei neuerem Stand deine zwei "
              "Cockpit-Seiten einsetzen (Muster „Screenshot mit Hinweisen“).",
              "Kikos Folie 16 zeigt schon Fallakte und Bewertung; hier den Blick der Fachabteilung betonen."])
    return s


def patrick_empfehlungen(prs, num):
    s = kit.blank(prs, MIST)
    header(s, "Was empfehlen wir SWW?", "compass", "Erst im Schattenbetrieb messen, dann schrittweise einführen",
           chapter="06")
    recs = [
        ("eye", "Empfehlung 1 · Schattenpilot",
         "Prognose und Prüfliste parallel für eine Zählergruppe, ohne Eingriff in Beschaffung oder Netzmanagement.",
         "Effekt: belegte Werte für Prognosefehler, Prüfaufwand und Bestätigungsquote, die Grundlage einer "
         "Euro-Bewertung."),
        ("messages-square", "Empfehlung 2 · Feedback im Cockpit",
         "Die Bewertungsmaske aus Kikos Prototyp im Pilot verbindlich nutzen: bestätigt oder verworfen, mit "
         "Ursache.",
         "Effekt: Die Trefferquote wird messbar; mit genug Ja/Nein-Labels wird eine Klassifikation möglich."),
    ]
    for i, (icon_name, head, body, effect) in enumerate(recs):
        x = 72 + i * 578
        card(s, x, 146, 558, 176)
        disc(s, x + 18, 164, icon_name, "navy", 40)
        text(s, x + 72, 170, 468, 24, head, 18, NAVY7, True, lh=24)
        text(s, x + 72, 198, 468, 44, body, 15, INK, lh=21)
        box(s, x + 18, 252, 522, 56, fill=TINT, radius=8)
        text(s, x + 32, 252, 500, 56, effect, 14.5, TEAL7, anchor="m", lh=20)
    kit.label(s, 72, 340, 400, "Nächste Schritte", SOFT)
    steps = ["Pilotgruppe und Verantwortliche festlegen", "Monatlich Prognose und Prüfliste parallel erstellen",
             "RMSE, MAE, Hinweise, Bearbeitungszeit und Bestätigungsquote beobachten",
             "Nach stabilen Monaten integrieren und ausweiten"]
    for i, step in enumerate(steps):
        x = 72 + i * 290
        card(s, x, 364, 266, 112)
        marker(s, x + 30, 392, i + 1)
        text(s, x + 54, 378, 204, 92, step, 15, INK, lh=21)
        if i < 3:
            kit.chevron(s, x + 278, 420)
    box(s, 72, 490, 1136, 100, fill=NAVY, radius=12, name="Ausblick")
    disc(s, 92, 522, "telescope", "light", 36)
    text(s, 144, 506, 1040, 24, "Ausblick", 18, WHITE, True, lh=24)
    text(s, 144, 532, 1040, 50, "Mit genug bestätigten Labels könnte ein Klassifikationsmodell die Prognose "
         "ergänzen und schätzen, wie wahrscheinlich sich ein Hinweis bestätigt; belastbar erst nach eigener "
         "Prüfung und Kalibrierung.", 16, PALE, lh=22)
    text(s, 72, 604, 1136, 22, "Neu trainiert oder die Schwelle geändert wird erst bei belegter Verschlechterung "
         "über mehrere Monate (Bericht 4.4.3).", 14, SOFT, lh=20)
    footer(s, ("08", "10"), "Patrick", num)
    kit.draft_notes(s, "Abschnitte 3.7, 4.4.3 und 4.5", [
        "Wir empfehlen zwei Dinge.",
        "Erstens einen Schattenpilot: Für eine ausgewählte Zählergruppe laufen Prognose und Prüfliste parallel "
        "zum bisherigen Prozess, ohne einzugreifen. So bekommen wir belegte Werte für Fehler, Prüfaufwand und "
        "Bestätigungsquote, und erst damit lässt sich ein Euro-Nutzen seriös bewerten.",
        "Zweitens Feedback: Die Bewertungsmaske, die Kiko im Prototyp gezeigt hat, wird im Pilot verbindlich "
        "genutzt. Nach jeder Prüfung wird gespeichert, ob sich der Hinweis bestätigt hat und warum.",
        "Die nächsten Schritte: Pilotgruppe festlegen, monatlich parallel rechnen, beobachten, und erst nach "
        "stabilen Monaten integrieren.",
        "Der Ausblick: Mit genug bestätigten Fällen könnte ein Klassifikationsmodell ergänzen, wie wahrscheinlich "
        "ein Hinweis sich bestätigt. Belastbar wäre das erst nach eigener Prüfung."],
        keywords=["Schattenpilot", "Feedback → Labels", "4 Schritte", "Ausblick Klassifikation"])
    return s


def patrick_fazit(prs, num):
    s = kit.blank(prs)
    header(s, "Was nehmen wir mit?", "quote", "Drei Rollen, drei Erkenntnisse", chapter="06")
    quotes = [
        "Datenbereinigung ist keine rein technische Routine: Erst der Vergleich mit der technisch möglichen "
        "Monatsenergie trennt Messfehler von plausiblen Verbrauchswerten.",
        "Bei Zeitreihendaten ist die Validierung wichtiger als die Wahl des komplexesten Modells.",
        "Eine auffällige Korrelation beweist noch keinen Treiber: Wetter- und Feiertagseffekte waren teils von der "
        "saisonalen Produktion überlagert.",
    ]
    for i, ((name, role, icon_name, _), quote) in enumerate(zip(PERSONS, quotes)):
        x = 72 + i * 385
        card(s, x, 146, 366, 318)
        disc(s, x + 18, 166, icon_name, "navy", 44)
        text(s, x + 74, 166, 280, 24, name, 18, INK, True, lh=24)
        text(s, x + 74, 192, 280, 20, role, 14, MUTED, lh=19)
        icon(s, "quote", TEAL3, x + 18, 234, 28)
        text(s, x + 18, 272, 330, 180, quote, 18, NAVY7, lh=26)
    box(s, 72, 480, 1136, 104, fill=NAVY, radius=12, name="Gemeinsames Fazit")
    disc(s, 92, 512, "circle-check", "light", 36)
    text(s, 144, 496, 1040, 24, "Gemeinsames Fazit", 18, WHITE, True, lh=24)
    text(s, 144, 522, 1040, 50, "Die Grundlage steht: Prognose je Zähler, eingefrorene Schwelle und ein "
         "Prüfprozess mit Feedback. Den wirtschaftlichen Nachweis liefert der Pilot.", 16, PALE, lh=22)
    footer(s, (), "Patrick", num)
    kit.draft_notes(s, "Abschnitt 3.6 (persönliche Fazits, je ein Satz)", [
        "Zum Schluss sagt jede und jeder von uns in einem Satz, was wir mitnehmen. Iana beginnt, dann Kiko, dann "
        "ich.",
        "Iana: Datenbereinigung ist keine rein technische Routine …",
        "Kiko: Bei Zeitreihendaten ist die Validierung wichtiger als die Wahl des komplexesten Modells.",
        "Patrick: Eine auffällige Korrelation beweist noch keinen Treiber …",
        "Gemeinsam: Die Grundlage steht, den wirtschaftlichen Nachweis liefert der Pilot."],
        keywords=["jede Person ein Satz", "Grundlage steht, Pilot liefert Nachweis"],
        todo=["Jede Person spricht ihren eigenen Satz (individuelle Sichtbarkeit).",
              "Kikos Folie 16 nennt sein Fazit schon; dort kann er es weglassen oder hier nur kurz wiederholen."])
    return s


def schluss(prs, num):
    s = kit.blank(prs, NAVY)
    _rings(s, 1180, 110, (0, 0, 1280, 653))
    text(s, 72, 72, 800, 18, "Unsere Antwort auf die Projektfrage", 14, TEAL3, True, lh=18, tracking=.08,
         upper=True, wrap=False)
    text(s, 72, 104, 900, 180, "Aus Verbrauchshistorie, Kalender, Heizgradtagen, Produktionsplan, Wartung und "
         "Kundentyp entsteht vor jedem Monat eine Prognose je Zähler. Weicht der Istwert stärker als die "
         "eingefrorene q99-Schwelle von der Prognose ab, landet der Fall zur Prüfung im Cockpit: monatlich statt "
         "erst im Quartal.", 24, WHITE, lh=34, name="Antwort")
    text(s, 72, 370, 1100, 70, "Vielen Dank. Ihre Fragen?", 60, WHITE, True, lh=70, tracking=-0.02, name="Titel")
    for i, (name, role, icon_name, _) in enumerate(PERSONS):
        x = 72 + i * 385
        disc(s, x, 500, icon_name, "light", 40)
        text(s, x + 52, 498, 320, 24, name, 18, WHITE, True, lh=24)
        text(s, x + 52, 522, 320, 20, role, 14, PALE, lh=19)
    footer(s, (), "Team", num, dark=True)
    kit.draft_notes(s, "Projektfrage aus der Vorlage, Antwort aus Abschnitt 1.2 und 4.3", [
        "Unsere Antwort auf die Projektfrage: Aus Historie, Kalender, Wetter, Planungsdaten und Kundentyp entsteht "
        "vor jedem Monat eine Prognose je Zähler. Weicht der Istwert stärker als die Schwelle von der Prognose ab, "
        "wird der Fall monatlich geprüft statt erst im Quartal.",
        "Vielen Dank, wir freuen uns auf Ihre Fragen."],
        keywords=["Antwort in einem Satz", "Fragen"])
    return s


# --------------------------------------------------------------------------- Backup


BACKUP_INDEX = [
    ("B1", "ML Canvas im Wortlaut (Tab. A1)", "Kiko"), ("B2", "Hyperparameter des Random Forest", "Kiko"),
    ("B3", "Treiber: Permutation Importance", "Kiko"), ("B4", "Lag-Merkmale", "Kiko"),
    ("B5", "Grenzen und Verantwortung", "Kiko"), ("B6", "Prüfaufwand statt ROI · Kosten-Annahmen", "Kiko"),
    ("B7", "Datenqualität im Detail", "Iana"), ("B8", "Ethik", "Team"),
]


def backup_trenner(prs, num):
    s = kit.blank(prs, NAVY)
    _rings(s, 1180, 110, (0, 0, 1280, 720))
    text(s, 72, 96, 600, 70, "Backup", 60, WHITE, True, lh=70, name="Titel")
    text(s, 72, 172, 800, 26, "Detailfolien für Rückfragen", 20, PALE, lh=26)
    for i, (nr, title, who) in enumerate(BACKUP_INDEX):
        x, y = 72 + (i // 4) * 568, 250 + (i % 4) * 78
        kit.dcard(s, x, y, 548, 64)
        text(s, x + 18, y, 50, 64, nr, 20, TEAL3, True, MONO, anchor="m", lh=24, wrap=False)
        text(s, x + 70, y, 380, 64, title, 16, WHITE, True, anchor="m", lh=21)
        text(s, x + 440, y, 90, 64, who, 14, PALE, align="r", anchor="m", lh=18, wrap=False)
    kit.set_notes(s, [("HINWEIS", ["Backup-Folien nur bei Rückfragen zeigen. Die Vorlage nennt Detail-Metriken, "
                                   "Ethik und Kosten-Annahmen: Detail-Metriken → Folie 11 (Modellvergleich), "
                                   "Folie 12 (Schwelle) und B3 (Treiber); Kosten-Annahmen → B6; Ethik → B8."])])
    return s


def backup_datenqualitaet(prs, num):
    s = kit.blank(prs)
    header(s, "Welche Befunde gab es im Einzelnen?", "table-2", "Datenqualität im Detail: elf Befunde, jeder begründet")
    data = [
        ("kundentyp", "Inkonsistenzen", "505", "3,0 %", "Vereinheitlicht"),
        ("monat", "Inkonsistenzen", "11.316", "67,3 %", "Datumsformat vereinheitlicht"),
        ("verbrauch_kwh", "MWh-Werte", "672", "4,0 %", "MWh → kWh"),
        (None, "Duplikate", "30", "0,2 %", "Entfernt"),
        ("mittlere_temperatur_c", "fehlend", "504", "3,0 %", "Für EDA beibehalten"),
        ("produktionsplan_index", "fehlend", "672", "4,0 %", "Für EDA beibehalten"),
        ("vormonat_verbrauch_kwh", "fehlend", "700", "4,2 %", "Strukturell bedingt"),
        ("letzte_3_monate_durchschnitt_kwh", "fehlend", "1", "<0,1 %", "Geprüft"),
        ("vorjahr_monat_verbrauch_kwh", "fehlend", "8.400", "50 %", "Strukturell bedingt"),
        ("verbrauch_kwh", "fehlend", "3", "<0,1 %", "Post-hoc imputiert"),
        ("verbrauch_kwh", "Ausreißer", "20", "0,1 %", "Geprüft"),
    ]
    rows = [["Problem", "Anzahl", "Anteil", "Maßnahme"]]
    for col, what, n, share, action in data:
        cell = [code(col), (f" – {what}", {})] if col else [(what, {})]
        rows.append([cell, n, share, action])
    kit.table(s, 72, 146, [520, 140, 140, 336], rows, [40] + [38.4] * 11, size=15, right_cols=(1, 2),
              name="Tabelle Datenqualität Detail")
    footer(s, ("02",), "Iana", num)
    kit.draft_notes(s, "Ianas Vorlage-Folie „Datenqualität (Backup)“", [
        "Hier die vollständige Liste. Anteile beziehen sich auf die deduplizierte Basis.",
        "Fehlende Temperatur- und Produktionsplanwerte haben wir für die EDA beibehalten; im Modell nutzt Kiko die "
        "Heizgradtage statt der Temperatur."],
        keywords=["vollständige Liste", "Anteile auf deduplizierter Basis"])
    return s


def backup_ethik(prs, num):
    s = kit.blank(prs)
    header(s, "Welche ethischen Fragen stellt das Modell?", "scale",
           "Ethik: begründete Merkmale, menschliche Entscheidung")
    cards = [
        ("filter-x", "navy", "Bewusst ausgeschlossene Merkmale",
         "Vorjahreswert (keine Historie aus 2023), Temperatur (nahezu gleich den Heizgradtagen), Spalte „anomalie“ "
         "(kein bestätigtes Label), Vertragsleistung als Merkmal (dient nur der Umrechnung)."),
        ("users", "navy", "Fairness je Kundentyp",
         "Gewerbe, Industrie und Kommunal werden über Vollaststunden vergleichbar (Mediane 160–173 VLS-h). "
         "Hinweisquote je Kundentyp im Pilot beobachten, damit keine Gruppe übermäßig geprüft wird."),
        ("user-check", "teal", "Menschliche Letztentscheidung",
         "Das Modell ersetzt keine Abrechnungsentscheidung. Ein Prüfhinweis ist keine bestätigte Anomalie; "
         "entschieden wird im Fachbereich."),
        ("lock", "teal", "Datenschutz und Speicherdauer",
         "Gewerbliche Großkunden, Zähler- und Kunden-IDs ohne Namen oder Adressen. Speicherdauer für Hinweise und "
         "Bewertungen im Pilot festlegen, gemeinsam mit dem Datenschutz."),
    ]
    for i, (icon_name, tone, head, body) in enumerate(cards):
        x, y = 72 + (i % 2) * 578, 146 + (i // 2) * 204
        icard(s, x, y, 558, 190, icon_name, tone, head, body, psize=16)
    merk(s, 72, 564, 1136, 60, "Nachvollziehbar statt Blackbox: Jede Markierung lässt sich über Faktor, Schwelle "
         "und Rechenweg erklären.")
    footer(s, ("04", "07"), "Team", num)
    kit.draft_notes(s, "Abschnitte 2.2, 4.4.2 und Kikos Folie „Zeitliche Validierung“", [
        "Ethisch sind vier Punkte wichtig: Welche Merkmale wir bewusst weggelassen haben und warum, ob einzelne "
        "Kundengruppen benachteiligt werden könnten, dass am Ende ein Mensch entscheidet, und wie mit den Daten "
        "umgegangen wird.",
        "Zur Speicherdauer haben wir im Projekt keine Festlegung getroffen; das gehört in den Pilot."],
        keywords=["vier Punkte", "Mensch entscheidet", "Speicherdauer: Pilot"],
        todo=["Folie ist ein Team-Entwurf; wer bei Rückfragen antwortet, bitte festlegen."])
    return s
