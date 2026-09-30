"""Kikos ML-Teil, reduziert und in den Folienlayouts des SWW-Designsystems (für Google Drive).

Neun Hauptfolien und vier Backups: Kapitel, ML Canvas, zeitliche Validierung, Zielgröße VLS,
Hauptmetrik RMSE, Modellwahl 2024, Schwelle, Prüffall, Ausblick Klassifikation. Ergebnisse des
Testjahrs 2025 (RMSE 9.188, −15,9 %, Treiber, Hinweiszahlen) zeigt Patrick; sie fehlen hier bewusst.

Diagramme sind Bilder aus Kikos HTML-Deck (``export_team_charts.mjs``), das RMSE-Beispiel aus
Notebook 13 ist nativ gezeichnet. Stichworte, Sprechtext und Rückfragen stehen in den Notizen.

    .venv/Scripts/python.exe scripts/build_kiko_ml_folien.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sww_layouts as L  # noqa: E402
import team_kit as kit  # noqa: E402
from kiko_ml_notizen import NOTES  # noqa: E402
from sww_layouts import (AMBER600, CYAN500, GREY200, GREY400, GREY500, GREY600, GREY900, NAVY200, NAVY800,  # noqa: E402
                         RED500, TEAL300, TEAL600, TEAL700, WHITE, X0, badge, card, footer, header, image_card,
                         panel, text)

K, BUILD, ROOT = kit.K, kit.BUILD, kit.ROOT
OUT = ROOT / "docs" / "presentation" / "kiko" / "Kiko_ML_Folien_SWW.pptx"
ASSETS = ROOT / "docs" / "presentation" / "kiko" / "assets"
MONO = kit.MONO
CHART = {"timeline": "s04_svg07.png", "vls": "s05_svg11.png", "cv": "s06_svg07.png", "calib": "s07_svg12.png",
         "case": "s10_svg08.png",
         "lags": "s15_svg01.png"}


def chart(name: str) -> Path:
    kit.load_charts()  # erzeugt die PNGs, falls sie fehlen
    path = kit.CHART_DIR / CHART[name]
    assert path.exists(), f"Diagramm fehlt: {path}"
    return path


def notes(s, keywords, speech, understand=(), questions=()):
    """Notizen: Stichworte, Sprechtext zum Ablesen, Hintergrund zum Verstehen, Rückfragen mit Antworten."""
    sections = [("STICHWORTE", [f"• {k}" for k in keywords]), ("SPRECHTEXT", list(speech))]
    if understand:
        sections.append(("SO VERSTEHST DU ES", [f"• {u}" for u in understand]))
    if questions:
        sections.append(("FALLS GEFRAGT WIRD", list(questions)))
    kit.set_notes(s, sections)


def notes_main(s, key: str) -> None:
    n = NOTES[key]
    notes(s, n["stichworte"], n["sprechtext"], n["verstehen"], n.get("fragen", ()))


# --------------------------------------------------------------------------- Hauptfolien


def f1_kapitel(prs, num):
    s = L.section(prs, "03/04", "Machine Learning: vom Canvas zum Prüfhinweis", "Kapitel 3 und 4 · Kiko",
                  "Was in diesem Teil beantwortet wird",
                  [("Was sagt das Modell vorher, und womit?", "chart-spline", "navy", "Folie 2–4", "Vorhersage"),
                   ("Woran messen wir, ob es gut ist?", "ruler", "teal", "Folie 5–6", "Messen"),
                   ("Ab wann wird eine Abweichung geprüft?", "flag", "amber", "Folie 7–8", "Prüfhinweis")],
                  "Kiko Ramon Lukas · Machine Learning und Evaluation", num)
    notes_main(s, "f1")
    return s


CANVAS_ML = [  # Nr, Feld, Frage des Feldes, Antwort in Alltagssprache
    ("03", "Vorhersage", "Was sagt das Modell vorher?",
     "Den Stromverbrauch jedes Zählers im nächsten Monat, am Ende in kWh."),
    ("04", "Merkmale", "Womit rechnet es?",
     "Nur mit Wissen vor Monatsbeginn: Verbrauchshistorie, Kalender, Wetter, Produktion, Wartung, Kundentyp."),
    ("05", "Lernansatz", "Wie lernt es?",
     "Aus Beispielen mit bekanntem Ergebnis: Random Forest gegen einfachere Verfahren."),
    ("06", "Evaluation", "Woran messen wir es?",
     "Am RMSE in kWh, nur auf Monaten, die das Modell beim Lernen nicht kannte."),
    ("07", "Entscheidung", "Was passiert mit dem Ergebnis?",
     "Die Prognose geht in die Beschaffung; ungewöhnliche Abweichungen gehen zur Prüfung."),
    ("09", "Zeitpunkt", "Wann läuft es?",
     "Zweimal im Monat: Prognose vor Monatsbeginn, Prüfung nach Monatsende."),
]


def f2_canvas(prs, num):
    s = L.slide(prs)
    header(s, "Kapitel 3 · ML Canvas · Kiko", "ML Canvas: sechs Felder gehören zum Modell")
    for i, (nr, name, question, body) in enumerate(CANVAS_ML):
        x, y = X0 + (i % 3) * 385, 160 + (i // 3) * 206
        card(s, x, y, 366, 192)
        L.eyebrow(s, x + 22, y + 18, 322, f"{nr} · {name}", TEAL600, 16)
        text(s, x + 22, y + 46, 322, 26, question, 19, GREY900, True, lh=26, name=f"Frage {nr}")
        text(s, x + 22, y + 78, 322, 104, body, 18, GREY600, lh=25, name=f"Feld {nr}")
    for i, (fields, who) in enumerate([("01 Mehrwert · 02 Datenquellen", "besprochen · Iana"),
                                       ("08 Impact · 10 Monitoring", "folgt · Patrick")]):
        x = X0 + i * 578
        card(s, x, 578, 558, 52, fill=L.GREY50, border=GREY200)
        text(s, x + 22, 578, 330, 52, fields, 17, GREY600, True, anchor="m", lh=22)
        text(s, x + 340, 578, 196, 52, who, 17, GREY500, align="r", anchor="m", lh=22)
    footer(s, num)
    notes_main(s, "f2")
    return s


def f3_validierung(prs, num):
    s = L.slide(prs)
    header(s, "Kapitel 4 · Methodik · Kiko", "Vergangenheit erklärt Zukunft, niemals umgekehrt")
    image_card(s, chart("timeline"), 84, 176, 1112, name="Diagramm Zeitliche Validierung")
    text(s, X0, 470, 700, 64, "Jede Bewertung nutzt nur Monate, die davor liegen. Modell und Schwelle stehen fest, "
         "bevor 2025 bewertet wird.", 20, GREY600, lh=29)
    panel(s, 800, 460, 408, 150, "Leakage vermieden", "Das 3-Monats-Mittel wurde nur aus abgeschlossenen "
          "Monaten neu berechnet.", variant="teal", head_size=18, body_size=17)
    footer(s, num)
    notes_main(s, "f3")
    return s


def f4_vls(prs, num):
    s = L.slide(prs)
    header(s, "Kapitel 4 · Zielgröße · Kiko", "Das Modell lernt Vollaststunden, geplant wird in kWh")
    for i, (head, formula) in enumerate([("Normieren", "VLS = Verbrauch [kWh] ÷ Leistung [kW]"),
                                         ("Zurückrechnen", "Prognose [kWh] = VLS × Leistung [kW]")]):
        y = 166 + i * 124
        card(s, X0, y, 560, 108)
        L.eyebrow(s, X0 + 24, y + 18, 400, head)
        text(s, X0 + 24, y + 52, 512, 32, formula, 21, GREY900, True, MONO, lh=30, wrap=False)
    panel(s, X0, 414, 560, 176, "Warum?", "92 % der Streuung im Rohverbrauch liegen zwischen den Zählern. In "
          "VLS werden große und kleine Anschlüsse vergleichbar.", variant="teal", head_size=20, body_size=19)
    image_card(s, chart("vls"), 676, 178, 520, name="Diagramm Vollaststunden")
    footer(s, num)
    notes_main(s, "f4")
    return s


def _rmse_chart(s, x, y, w, h):
    """Natives Balkendiagramm aus Notebook 13: MAE und RMSE für zwei Fehlerverteilungen."""
    card(s, x, y, w, h)
    lx = x + 24
    for color, label in [(GREY400, "MAE · mittlerer Fehler"), (CYAN500, "RMSE · große Fehler stärker gewichtet")]:
        lw = kit.measure(label, 16) + 8
        L.box(s, lx, y + 26, 16, 16, fill=color, radius=3)
        text(s, lx + 24, y + 22, lw, 24, label, 16, GREY600, lh=24, wrap=False)
        lx += 24 + lw * 1.1 + 18
    top, bottom = y + 86, y + h - 110
    scale = (bottom - top) / 24
    for tick in (0, 10, 20):
        ty = bottom - tick * scale
        L.line(s, x + 70, ty, x + w - 24, ty, GREY200, 1)
        text(s, x + 20, ty - 11, 40, 22, str(tick), 16, GREY500, align="r", lh=22, wrap=False)
    text(s, x + 20, top - 34, 120, 22, "kWh", 16, GREY500, lh=22, wrap=False)
    groups = [("A · gleichmäßig", "10 · 10 · 10 · 10 kWh", 10, 10), ("B · ein großer Fehler", "0 · 0 · 0 · 40 kWh",
                                                                      10, 20)]
    span = (w - 94) / 2
    for g, (name, errors, mae, rmse) in enumerate(groups):
        cx = x + 70 + span * g + span / 2
        for k, (value, color, metric) in enumerate([(mae, GREY400, "MAE"), (rmse, CYAN500, "RMSE")]):
            bx = cx - 78 + k * 82
            L.box(s, bx, bottom - value * scale, 74, value * scale, fill=color, name=f"Balken {name[0]} {metric}")
            text(s, bx - 10, bottom - value * scale - 30, 94, 24, f"{value} kWh", 18, GREY900, True, align="c", lh=24,
                 wrap=False)
        text(s, cx - 130, bottom + 14, 260, 24, name, 18, GREY900, True, align="c", lh=24, wrap=False)
        text(s, cx - 130, bottom + 40, 260, 22, errors, 16, GREY600, align="c", lh=22, wrap=False)
    text(s, x + 24, y + h - 40, w - 48, 22, "Beispiel aus Notebook 13, keine Projektwerte", 16, GREY500, lh=22)


def f5_rmse(prs, num):
    s = L.slide(prs)
    header(s, "Kapitel 4 · Hauptmetrik · Kiko", "Warum RMSE? Er gewichtet große Fehler stärker")
    _rmse_chart(s, X0, 160, 620, 470)
    card(s, 716, 160, 492, 180, fill=L.NAVY100, border=L.NAVY200)
    L.eyebrow(s, 740, 180, 440, "Formel")
    text(s, 740, 212, 448, 30, "RMSE = √( Σ (Ist − Prognose)² ÷ n )", 20, GREY900, True, MONO, lh=30, wrap=False)
    text(s, 740, 258, 448, 64, ["A: √(4 · 10² ÷ 4) = 10 kWh", "B: √(40² ÷ 4) = 20 kWh"], 17, GREY600, font=MONO,
         lh=26)
    text(s, 716, 362, 492, 260, [
        "• Misst in kWh: der Einheit, in der die Beschaffung plant.",
        "• Große Abweichungen gleicht die Beschaffung teuer am Spotmarkt aus.",
        "• MAE und R² ergänzen, entscheiden aber nicht."], 19, GREY900, lh=27, gap=12, indent=22)
    footer(s, num)
    notes_main(s, "f5")
    return s


def f6_modellwahl(prs, num):
    s = L.slide(prs)
    header(s, "Kapitel 4 · Modellwahl · Kiko", "Random Forest gewinnt die Auswahl in 2024")
    card(s, X0, 160, 700, 470)
    text(s, X0 + 24, 180, 650, 26, "Ø RMSE über drei zeitliche Folds 2024", 19, GREY900, True, lh=26)
    text(s, X0 + 24, 206, 650, 22, "in kWh · Raute je Fold, Strich ±1 Standardabweichung", 16, GREY600, lh=22)
    img = chart("cv")
    kit.picture(s, str(img), X0 + 24, 250, 652, 652 * 239.08 / 524, name="Diagramm Modellwahl 2024")
    for i, (head, body) in enumerate([
        ("Knapp vor der linearen Regression", "13.272 gegen 13.643 kWh: der Wald erfasst nichtlineare Effekte."),
        ("Klar vor einfachen Regeln", "3-Monats-Mittel 15.483, Vormonat 18.460 kWh."),
        ("Fold 1 ist für alle am schwersten", "Mai–Jun zieht jeden Mittelwert hoch.")]):
        panel(s, 796, 160 + i * 158, 412, 144, head, body, head_size=18, body_size=17)
    footer(s, num)
    notes_main(s, "f6")
    return s


def f7_schwelle(prs, num):
    s = L.slide(prs)
    header(s, "Kapitel 4 · Schwelle · Kiko", "Ungewöhnlich ist, was 99 von 100 Fehler übertrifft")
    steps = [("Abweichung messen", "Nach Monatsende: Ist minus Prognose, in Vollaststunden."),
             ("Normale Fehler sammeln", "1.397 echte Vorhersagefehler aus Nov–Dez 2024, der Größe nach sortiert."),
             ("Grenze ziehen", "99 von 100 Fehlern liegen darunter: 144,4 VLS-h, vor 2025 eingefroren.")]
    for i, (head, body) in enumerate(steps):
        y = 160 + i * 96
        kit.marker(s, X0 + 18, y + 18, i + 1, fill=L.NAVY700, d=32, size=17)
        text(s, X0 + 50, y + 4, 420, 28, head, 20, GREY900, True, lh=27)
        text(s, X0 + 50, y + 34, 420, 52, body, 17, GREY600, lh=24)
    L.panel(s, X0, 450, 470, 100, "", "99 % ist der Startwert für den Pilot. Wie viele Hinweise das Team schafft, "
            "zeigt Patrick im Dashboard.", variant="teal", body_size=17)
    image_card(s, chart("calib"), 584, 172, 612, name="Diagramm Kalibrierung")
    L.box(s, X0, 566, 1136, 60, fill=L.NAVY700, radius=10, name="Faktor")
    bw = badge(s, X0 + 20, 580, "Faktor", "dark")
    text(s, X0 + 40 + bw, 566, 900, 60, "F = Abweichung ÷ 144,4 VLS-h  ·  ab F ≥ 1 Prüfhinweis  ·  ZL-00147: F = 2,3",
         19, WHITE, font=MONO, anchor="m", lh=26, wrap=False)
    footer(s, num)
    notes_main(s, "f7")
    return s


def f8_prueffall(prs, num):
    s = L.slide(prs)
    header(s, "Kapitel 4 · Prüffall · Kiko", "ZL-00147: im August 2,3-mal so groß wie erlaubt")
    image_card(s, chart("case"), 84, 172, 560, name="Diagramm Prüffall ZL-00147")
    L.kpi(s, 688, 160, 520, 150, "Faktor im August 2025", "+2,30", "", "Residuum 331,8 VLS-h ÷ Schwelle 144,4 "
          "VLS-h", value_color=RED500)
    card(s, 688, 330, 520, 300)
    L.eyebrow(s, 712, 352, 470, "Bewertung im Cockpit")
    for i, question in enumerate(["Messwert gültig?", "Abweichung erklärt?"]):
        y = 392 + i * 60
        text(s, 712, y, 250, 40, question, 19, GREY900, anchor="m", lh=26)
        x = 990
        for answer in ("Ja", "Nein"):
            x += badge(s, x, y + 2, answer, "info" if answer == "Ja" else "crit") + 10
    text(s, 712, 512, 250, 40, "Ursache", 19, GREY900, anchor="m", lh=26)
    card(s, 990, 514, 194, 36, fill=L.GREY50, border=GREY200)
    text(s, 1002, 514, 176, 36, "Freitext", 16, GREY500, anchor="m", lh=22, wrap=False)
    text(s, 712, 570, 470, 44, "Jede Bewertung ist ein Label für später.", 19, TEAL700, True, anchor="m", lh=26)
    footer(s, num)
    notes_main(s, "f8")
    return s


def f9_ausblick(prs, num):
    s = L.slide(prs, NAVY800)
    header(s, "Ausblick · Kiko", "Aus Bewertungen wird ein Klassifikationsmodell", dark=True)
    steps = [("01", "Prüfhinweise bewerten", "Jede Prüfung speichert: Messwert gültig? Abweichung erklärt? "
                                             "Ursache."),
             ("02", "Klassifikation trainieren", "Mit genug bestätigten Fällen schätzt ein zweites Modell je Hinweis "
                                                 "die Wahrscheinlichkeit in %."),
             ("03", "Workflow automatisieren", "Hinweise nach Wahrscheinlichkeit automatisiert vorsortieren; der "
                                               "Mensch entscheidet.")]
    for i, (nr, head, body) in enumerate(steps):
        x = X0 + i * 385
        L.box(s, x, 160, 366, 262, fill=L.GLASS, line=L.GLASS_LINE, radius=10)
        text(s, x + 26, 184, 120, 40, nr, 32, TEAL300, True, MONO, lh=40, wrap=False)
        text(s, x + 26, 236, 314, 30, head, 22, WHITE, True, lh=29)
        text(s, x + 26, 276, 314, 132, body, 19, NAVY200, lh=27)
    L.box(s, X0, 440, 1136, 70, fill=L.GLASS, line=L.GLASS_LINE, radius=10)
    bw = badge(s, X0 + 20, 458, "Vorbehalt", "dark")
    text(s, X0 + 36 + bw, 440, 1136 - 56 - bw, 70, "Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur "
         "Untersuchungswürdiges.", 18, WHITE, anchor="m", lh=25)
    text(s, X0, 532, 1136, 64, "Weiter mit Patrick: Ergebnisse 2025 und wie hinterlegte echte Zählerwerte das "
         "Retraining der Prognose verbessern.", 20, TEAL300, True, lh=29)
    footer(s, num, dark=True)
    notes_main(s, "f9")
    return s


# --------------------------------------------------------------------------- Backups


def _spec(label):
    specs = BUILD["build_slides"](BUILD["extract_facts"](BUILD["Notebook"].load()))
    return next(s for s in specs if s.label == label)


def b1_hyper(prs, num):
    s = L.slide(prs)
    header(s, "Backup · Modellwahl · Kiko", "Acht kontrollierte Kombinationen, entschieden nur in 2024")
    root = K["parse"](_spec("Backup Hyperparameter"))
    rows = [[K["plain"](td) for td in tr] for tr in K["qa"](root, "tr")]
    kit.table(s, X0, 160, [200, 200, 220, 250, 266], rows, [48] + [44] * (len(rows) - 1), size=17, head_size=16,
              right_cols=(3, 4), tint_rows=(1,), name="Tabelle Hyperparameter")
    text(s, X0, 578, 1136, 26, "300 Bäume, random_state = 42. Die Unterschiede sind klein; entscheidend ist die "
         "zeitliche Prüfung.", 18, GREY600, lh=26)
    footer(s, num)
    notes(s, ["acht Kombinationen", "nur 2024 entscheidet"], [
        "Baumtiefe, Merkmalsanteil und Mindestfälle je Blatt haben wir in acht Kombinationen verglichen, nur in "
        "den Folds 2024. Die Unterschiede sind klein."])
    return s


def b2_lags(prs, num):
    s = L.slide(prs)
    header(s, "Backup · Merkmale · Kiko", "Lag-Merkmale verschieben bekannte Historie nach vorn")
    image_card(s, chart("lags"), 84, 172, 600, name="Diagramm Lag-Merkmale")
    for i, (head, body) in enumerate([("Januar 2024", "Echter Kaltstart ohne Historie; bleibt leer."),
                                      ("Februar und März", "Nutzen die verfügbare Historie (1 bzw. 2 Monate)."),
                                      ("Ab April", "Mittel aus bis zu drei abgeschlossenen Vormonaten.")]):
        panel(s, 728, 160 + i * 142, 480, 128, head, body, head_size=18, body_size=17)
    text(s, 728, 590, 480, 26, "1.453 Drei-Monats-Werte bleiben erhalten.", 17, GREY600, lh=24)
    footer(s, num)
    notes(s, ["shift(1): nur Vergangenheit", "Kaltstart Januar"], [
        "Die Historien-Merkmale werden je Zähler um einen Monat verschoben, damit nur abgeschlossene Monate "
        "einfließen."])
    return s


def b3_kalibrierung(prs, num):
    s = L.slide(prs)
    header(s, "Backup · Schwelle · Kiko", "Warum die Schwelle aus Nov–Dez 2024 stammt")
    for i, (head, body) in enumerate([
        ("Jüngste Monate vor dem Test", "November mit einem Modell aus Jan–Okt, Dezember aus Jan–Nov."),
        ("Nicht für die Modellwahl genutzt", "Die Folds enden im Oktober; die Fehler sind echte Vorwärtsfehler."),
        ("Später geht nicht", "Jede spätere Wahl würde 2025 selbst verwenden, also Leakage.")]):
        panel(s, X0 + i * 385, 160, 366, 200, head, body, head_size=19, body_size=18)
    L.kpi(s, X0, 384, 366, 200, "Kalibriert Nov–Dez 2024", "144,4", "VLS-h", "q99 aus 1.397 Fehlern, eingefroren")
    L.kpi(s, X0 + 385, 384, 366, 200, "Nachträglich aus 2025", "175,1", "VLS-h", "wäre Leakage, nur zur Einordnung")
    L.kpi(s, X0 + 770, 384, 366, 200, "Typischer Fehler (Median)", "17,3 → 17,1", "", "Kalibrierung gegen 2025: "
          "gleich groß")
    footer(s, num)
    notes(s, ["jüngste Monate vor dem Test", "keine Überschneidung mit der Modellwahl", "2025-Wert nur Einordnung"], [
        "Die Schwelle muss vor 2025 feststehen. November und Dezember 2024 sind die letzten Monate davor und "
        "wurden nicht für die Modellwahl gebraucht.",
        "Im Nachhinein läge das 99. Perzentil 2025 bei 175 Vollaststunden. Der typische Fehler ist aber gleich "
        "groß; 2025 sind nur die Extreme größer."])
    return s


def b4_canvas(prs, num):
    s = L.slide(prs)
    header(s, "Backup · ML Canvas · Kiko", "ML Canvas im Wortlaut von Tabelle A1 des Berichts")
    rows = [["Nr.", "Feld", "Wortlaut (Bericht, Tab. A1)"]]
    for nr in [f"{n:02d}" for n in range(1, 11)]:
        rows.append([nr, BUILD["CANVAS"][nr][0], BUILD["CANVAS_A1"][nr]])
    kit.table(s, X0, 150, [60, 190, 886], rows, [36] + [46] * 10, size=14, head_size=14,
              tint_rows=tuple(i for i, nr in enumerate(range(1, 11), 1) if f"{nr:02d}" in BUILD["ML_FIELDS"]),
              name="Tabelle Canvas")
    footer(s, num)
    notes(s, ["Wortlaut wie im Bericht", "ML-Felder hellteal"], [
        "Falls gefragt: Das ist der Canvas im Wortlaut des Berichts; die hervorgehobenen Zeilen sind meine Felder."])
    return s


MAIN = [f1_kapitel, f2_canvas, f3_validierung, f4_vls, f5_rmse, f6_modellwahl, f7_schwelle, f8_prueffall,
        f9_ausblick]
BACKUP = [b1_hyper, b2_lags, b3_kalibrierung, b4_canvas]


def build(path: Path = OUT) -> Path:
    missing = K["_MISSING"]
    missing.clear()
    prs = _assemble()
    if missing:  # fehlende Icon-PNGs gesammelt rendern, dann neu zusammenbauen
        K["render_icons"](missing)
        missing.clear()
        prs = _assemble()
        assert not missing, f"Icons fehlen weiterhin: {sorted(missing)}"
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)
    return path


def _assemble():
    prs = Presentation()
    prs.slide_width, prs.slide_height = kit.E(1280), kit.E(720)
    prs.core_properties.title = "Machine Learning: vom Canvas zum Prüfhinweis"
    prs.core_properties.author = "Kiko Ramon Lukas · Gruppe 6"
    prs.core_properties.language = "de-DE"
    for i, make in enumerate(MAIN, 1):
        make(prs, f"{i} / {len(MAIN)}")
    for i, make in enumerate(BACKUP, 1):
        make(prs, f"B{i}")
    for slide in prs.slides:
        kit.flatten_alpha(slide)
    kit.theme_fonts(prs)
    return prs



if __name__ == "__main__":
    out = build()
    print(f"{out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
