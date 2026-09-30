"""Kikos Präsentationsteil (ML Canvas, Methodik und Modell, Prüffall) als HTML-Foliensatz.

Alle Kennzahlen und Diagrammdaten stammen aus den gespeicherten Ausgaben von
``notebooks/13_modellierung_von_grund_auf_verstehen.ipynb``. Das Skript trainiert
nichts neu, sondern liest die Plotly-Figuren und HTML-Ausgaben des Notebooks und
zeichnet sie im Design der SWW-Projektpräsentation
(``brand/reference/export/templates/projekt-praesentation``) als Inline-SVG.

Ausgaben unter ``docs/presentation/kiko/``:
- ``Kiko_ML_Canvas_Methodik_Prueffall.html``: Foliensatz (1280 × 720, Präsentiermodus)
- ``Kiko_Sprechzettel.html``: Sprechtexte, Lesehilfen und Rückfragen je Folie
"""

from __future__ import annotations

import base64
import html
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "13_modellierung_von_grund_auf_verstehen.ipynb"
OUT_DIR = ROOT / "docs" / "presentation" / "kiko"
ASSET_DIR = OUT_DIR / "assets"
DECK = OUT_DIR / "Kiko_ML_Canvas_Methodik_Prueffall.html"
NOTES = OUT_DIR / "Kiko_Sprechzettel.html"
FONT_DIR = ROOT / "brand" / "design-system" / "dist" / "fonts"
LOGO = ROOT / "brand" / "design-system" / "assets" / "logo-sww-wordmark.png"

SPEAKER = "Kiko"
FOOTER_TITLE = "Verbrauchsprognose &amp; Frühwarnung"

# Farbrollen aus src/energy_analytics/visualization/_tokens.json
C = {
    "ist": "#084878", "prognose": "#0090C8", "band": "rgba(0,144,200,.16)",
    "residuum": "#0080A0", "schwelle": "#A86505", "anomalie": "#B3261E",
    "navy900": "#04263F", "navy800": "#063659", "navy700": "#084878", "navy300": "#7FB4D8",
    "navy200": "#BBD7EA", "navy100": "#E4EFF7", "navy50": "#EDF3F9",
    "teal700": "#005E77", "teal600": "#00718E", "teal300": "#6CC0D2", "teal100": "#E3F3F7",
    "grey900": "#141A21", "grey600": "#4E5A68", "grey500": "#657383", "grey400": "#8C99A7",
    "grey300": "#B4BFCB", "grey200": "#D2DAE2", "grey100": "#E4E9EF", "grey50": "#F1F4F7",
    "amber100": "#FDF3E0", "amber200": "#F7DFAF", "amber700": "#7F4C03",
    "red100": "#FBE9E7", "red200": "#F3C6C1", "red600": "#951C15",
    "green700": "#2F7A33", "green100": "#EDF6E9", "green200": "#CFE7C8",
}

# Werte, die nur im Bericht stehen (docs/IHK_Bericht_Gruppe_6_final.docx); die Tests sichern sie ab.
BERICHT = {
    "r2": "0,901",                              # Kap. 4.4.1, Benchmark 2025
    "streuung_zwischen_zaehlern": 92,           # Kap. 3.3.2 (EDA): Anteil der Streuung zwischen Zählern, %
    "median_kundentyp": (160, 173),             # Kap. 3.3.2: Kundentyp-Mediane nach Normierung, VLS-h
    "importance": [                             # Tab. D1: RMSE-Anstieg beim Mischen, kWh (5 Wiederholungen)
        ("Verbrauchshistorie", 7256), ("Produktionsplan", 798), ("Wartung", 591), ("Kalender", 276),
        ("Heizgradtage (Wetter)", 154), ("Saison (Monat)", 121), ("Kundentyp", 3),
    ],
}

# Kopie aus notebooks/13 (learn-analysis); der Test prüft die Übereinstimmung.
FOLD_DEFINITIONS = [
    ("2024-04-01", "2024-05-01", "2024-06-30"),
    ("2024-06-01", "2024-07-01", "2024-08-31"),
    ("2024-08-01", "2024-09-01", "2024-10-31"),
]


# --------------------------------------------------------------------------- Zahlen


def de(value: float, digits: int = 0) -> str:
    """Deutsche Zahlendarstellung: 13272.4 -> '13.272', 144.35 -> '144,35'."""
    text = f"{float(value):,.{digits}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def signed_de(value: float, digits: int = 2) -> str:
    return ("+" if value > 0 else "−" if value < 0 else "±") + de(abs(value), digits)


def parse_de(text: str) -> float:
    return float(text.replace(".", "").replace(",", "."))


def _decode(value):
    if isinstance(value, dict) and "bdata" in value:
        import numpy as np

        array = np.frombuffer(base64.b64decode(value["bdata"]), dtype=np.dtype(value["dtype"]))
        if "shape" in value:
            array = array.reshape([int(s) for s in str(value["shape"]).split(",")])
        return array.tolist()
    return value


def _plain(fragment: str) -> str:
    fragment = re.sub(r"<style.*?</style>", " ", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


@dataclass
class Notebook:
    cells: dict

    @classmethod
    def load(cls, path: Path = NOTEBOOK) -> "Notebook":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls({cell.get("id"): cell for cell in raw["cells"]})

    def figure(self, cell_id: str) -> list[dict]:
        for output in self.cells[cell_id].get("outputs", []):
            fig = output.get("data", {}).get("application/vnd.plotly.v1+json")
            if fig:
                traces = []
                for trace in fig["data"]:
                    item = {k: _decode(trace.get(k)) for k in ("name", "x", "y", "customdata")}
                    if trace.get("error_x"):
                        item["err"] = _decode(trace["error_x"].get("array"))
                    traces.append(item)
                return traces
        raise KeyError(f"Keine Plotly-Figur in Zelle {cell_id}")

    def text(self, cell_id: str) -> str:
        parts = []
        for output in self.cells[cell_id].get("outputs", []):
            data = output.get("data", {})
            if "text/html" in data:
                parts.append(_plain("".join(data["text/html"])))
        return " || ".join(parts)

    def source(self, cell_id: str) -> str:
        return "".join(self.cells[cell_id]["source"])


def _trace(traces: list[dict], name) -> dict:
    return next(t for t in traces if t["name"] == name)


def _search(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Muster nicht gefunden: {pattern}")
    return match.group(1)


def extract_facts(nb: Notebook) -> dict:
    """Liest alle für die Folien benötigten Zahlen aus den Notebook-Ausgaben."""
    facts: dict = {}

    cv = nb.figure("learn-cv-comparison")
    mean = _trace(cv, "Mittelwert")
    facts["cv"] = [
        {
            "name": name,
            "mean": m,
            "std": s,
            "folds": [_trace(cv, f"Fold {k}")["x"][i] for k in (1, 2, 3)],
        }
        for i, (name, m, s) in enumerate(zip(mean["y"], mean["x"], mean["err"]))
    ]

    bench = nb.figure("learn-benchmark")[0]
    facts["bench"] = [{"name": n, "rmse": v} for n, v in zip(bench["y"], bench["x"])]
    bench_text = nb.text("learn-benchmark")
    facts["test_mae"] = parse_de(_search(r"MAE ([\d.]+) kWh", bench_text))
    facts["test_n"] = int(parse_de(_search(r"Bewertete Fälle ([\d.]+)", bench_text)))
    rmse = {row["name"]: row["rmse"] for row in facts["bench"]}
    facts["test_rmse"] = rmse["Random Forest"]
    facts["baseline_gain_pct"] = (1 - rmse["Random Forest"] / rmse["Bis-zu-3-Monats-Mittel"]) * 100

    direct = nb.figure("learn-vls-vs-kwh")[0]
    direct_rmse = dict(zip(direct["x"], direct["y"]))
    facts["direct_kwh_rmse"] = direct_rmse["Direkt kWh"]
    facts["vls_rmse"] = direct_rmse["VLS → kWh"]
    facts["vls_gain_pct"] = (1 - facts["vls_rmse"] / facts["direct_kwh_rmse"]) * 100

    imp = nb.figure("learn-feature-importance")[0]
    facts["importance"] = sorted(
        ({"name": n, "value": v} for n, v in zip(imp["y"], imp["x"])),
        key=lambda row: -row["value"],
    )

    ranked = nb.figure("learn-ranked-errors")
    below, above = _trace(ranked, "bis zur Schwelle"), _trace(ranked, "oberhalb der Schwelle")
    points = sorted(set(zip(below["x"] + above["x"], below["y"] + above["y"])))
    facts["ranked"] = points
    facts["threshold"] = _trace(ranked, "99-%-Schwelle")["y"][0]
    facts["n_calibration"] = len(points)
    facts["n_above"] = sum(1 for _, y in points if y > facts["threshold"])

    workload = nb.text("learn-threshold-workload")
    facts["workload"] = [
        {"q": parse_de(q), "schwelle": parse_de(s), "hinweise": int(n), "je_monat": parse_de(m)}
        for q, s, n, m in re.findall(r"(\d+,\d) % ([\d.]+,\d) (\d+) ([\d]+,\d)", workload)
    ]

    tuning = nb.text("learn-tuning-table")
    facts["tuning"] = [
        {"depth": d, "features": f, "leaf": int(leaf), "cv": parse_de(cvv), "std": parse_de(sd)}
        for d, f, leaf, cvv, sd in re.findall(
            r"(8|unbegrenzt) (0,7|1,0) (5|20) ([\d.]+) ([\d.]+)", tuning
        )
    ]

    case = nb.figure("learn-case-timeseries")
    facts["case_months"] = [x[:7] for x in _trace(case, "Ist")["x"]]
    facts["case_ist"] = _trace(case, "Ist")["y"]
    facts["case_prognose"] = _trace(case, "Prognose")["y"]
    facts["case_factor"] = nb.figure("learn-factor-plot")[0]["y"]
    factor_text = nb.text("learn-factor-explanation")
    facts["case_kw"] = int(_search(r"Zählergröße (\d+) kW", factor_text))
    facts["case_id"] = "ZL-00147"

    scatter = nb.figure("learn-vls-boundary-plot")
    facts["scatter_normal"] = list(zip(*(_trace(scatter, "kein Prüfhinweis")[k] for k in "xy")))
    alerts = _trace(scatter, "Prüfhinweis")
    facts["scatter_alerts"] = list(zip(alerts["x"], alerts["y"]))
    facts["n_alerts"] = len(facts["scatter_alerts"])
    # customdata je Hinweis: [Zähler-ID, Monat, VLS-Residuum]
    facts["alert_meters"] = len({row[0] for row in alerts["customdata"]})
    facts["alerts_high"] = sum(1 for row in alerts["customdata"] if row[2] > 0)
    facts["alerts_low"] = sum(1 for row in alerts["customdata"] if row[2] < 0)
    months = [row[1] for row in alerts["customdata"]]  # Format "MM/2025"
    facts["alerts_by_month"] = [months.count(f"{m:02d}/2025") for m in range(1, 13)]

    # Kalibrierung im Vergleich zu 2025 (nur zur Erklärung, nicht zur Entscheidung verwendet)
    import numpy as np

    res_2025 = np.abs([y - x for x, y in facts["scatter_normal"] + facts["scatter_alerts"]
                       if x is not None and y is not None])
    cal = np.array([y for _, y in facts["ranked"]])
    facts["q99_2025_hindsight"] = float(np.quantile(res_2025, 0.99))
    facts["median_cal"] = float(np.median(cal))
    facts["median_2025"] = float(np.median(res_2025))

    lag = nb.figure("learn-lag-plot")
    facts["lag"] = {t["name"]: t["y"] for t in lag}
    facts["lag_months"] = [x[:7] for x in lag[0]["x"]]

    facts["folds_in_notebook"] = [
        tuple(m) for m in re.findall(
            r'\("(\d{4}-\d\d-\d\d)", "(\d{4}-\d\d-\d\d)", "(\d{4}-\d\d-\d\d)"\)',
            nb.source("learn-analysis"),
        )
    ]
    return facts


# --------------------------------------------------------------------------- SVG-Helfer

# Schriftgrößen in Diagrammen (Vorlage: 15 px Ticks, 17 px Legende/Achsentitel)
TICK = 15
LABEL = 16


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def lin(d0: float, d1: float, r0: float, r1: float):
    span = (d1 - d0) or 1.0
    return lambda v: r0 + (v - d0) / span * (r1 - r0)


def txt(x, y, s, size=LABEL, fill=None, anchor="start", weight=400, mono=False, extra=""):
    family = "'Geist Mono',monospace" if mono else "'IBM Plex Sans',sans-serif"
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill or C["grey600"]}" text-anchor="{anchor}" {extra}>'
        f"{esc(s)}</text>"
    )


def rbar(x, y, w, h, fill, r=4, horizontal=True, title=None):
    """Balken mit abgerundetem Datenende, am Nullpunkt gerade."""
    if w <= 0 or h <= 0:
        return ""
    r = min(r, w / 2, h / 2)
    if horizontal:
        path = (
            f"M{x:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} "
            f"a{r},{r} 0 0 1 -{r},{r} h-{w - r:.1f} z"
        )
    else:
        path = (
            f"M{x:.1f},{y + h:.1f} v-{h - r:.1f} a{r},{r} 0 0 1 {r},-{r} h{w - 2 * r:.1f} "
            f"a{r},{r} 0 0 1 {r},{r} v{h - r:.1f} z"
        )
    tip = f"<title>{esc(title)}</title>" if title else ""
    return f'<path d="{path}" fill="{fill}">{tip}</path>'


def svg(w, h, body, label):
    return (
        f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" '
        f'style="display:block;width:100%;height:auto;overflow:visible">{body}</svg>'
    )


def diamond(cx, cy, r, fill, title=None):
    tip = f"<title>{esc(title)}</title>" if title else ""
    return (
        f'<path d="M{cx:.1f},{cy - r:.1f} L{cx + r:.1f},{cy:.1f} L{cx:.1f},{cy + r:.1f} '
        f'L{cx - r:.1f},{cy:.1f} z" fill="{fill}" stroke="#fff" stroke-width="2">{tip}</path>'
    )


MONTHS = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

# Fold-Farben aus der Markenpalette (amber-500, navy-600, green-600); Farbvalidator: alle Prüfungen bestanden
FOLD_COLORS = ["#C77E11", "#0A5A93", "#3F9440"]
FOLD_LABELS = ["Fold 1 · Mai–Jun", "Fold 2 · Jul–Aug", "Fold 3 · Sep–Okt"]


# --------------------------------------------------------------------------- Diagramme


def chart_vls_example() -> str:
    w, h = 454, 310
    body = []
    panels = [
        ("Energiemenge", "kWh", [10_000, 40_000], 40_000, ["10.000", "40.000"]),
        ("Vollaststunden", "VLS-h", [200, 200], 250, ["200", "200"]),
    ]
    colors = [C["navy300"], C["ist"]]
    for p, (title, unit, values, vmax, labels) in enumerate(panels):
        x0 = p * 240
        body.append(txt(x0, 18, title, 17, C["grey900"], weight=600))
        body.append(txt(x0, 40, f"in {unit}", TICK, C["grey500"]))
        y = lin(0, vmax, 250, 70)
        body.append(f'<line x1="{x0}" x2="{x0 + 212}" y1="250" y2="250" stroke="{C["grey300"]}"/>')
        for i, v in enumerate(values):
            bx = x0 + 14 + i * 100
            body.append(rbar(bx, y(v), 78, 250 - y(v), colors[i], horizontal=False,
                             title=f"Zähler {'AB'[i]}: {labels[i]} {unit}"))
            body.append(txt(bx + 39, y(v) - 9, labels[i], 17, C["grey900"], "middle", 600, True))
            body.append(txt(bx + 39, 274, f"Zähler {'AB'[i]}", LABEL, C["grey900"], "middle", 500))
            body.append(txt(bx + 39, 298, ["50 kW", "200 kW"][i], TICK, C["grey500"], "middle", mono=True))
    body.append(txt(227, 168, "÷ kW", LABEL, C["teal600"], "middle", 600, True))
    return svg(w, h, "".join(body), "Zwei Zähler mit 10.000 und 40.000 kWh haben jeweils 200 Vollaststunden")


def chart_folds(facts) -> str:
    w, h = 1096, 256
    left, right, top = 150, 1090, 44
    cell = (right - left) / 24
    rows = [
        ("Fold 1", [(0, 4, "Lernen"), (4, 6, "Bewerten")]),
        ("Fold 2", [(0, 6, "Lernen"), (6, 8, "Bewerten")]),
        ("Fold 3", [(0, 8, "Lernen"), (8, 10, "Bewerten")]),
        ("Schwelle", [(10, 12, "Kalibrieren")]),
        ("Finales Modell", [(0, 12, "Lernen · ganz 2024"), (12, 24, "Benchmark")]),
    ]
    style = {
        "Lernen": (C["navy200"], C["navy900"]),
        "Lernen · ganz 2024": (C["navy200"], C["navy900"]),
        "Bewerten": (C["ist"], "#fff"),
        "Kalibrieren": (C["schwelle"], "#fff"),
        "Benchmark": (C["residuum"], "#fff"),
    }
    body = [
        txt(left + 6 * cell, 16, "2024 · Entwicklung", LABEL, C["grey900"], "middle", 600),
        txt(left + 18 * cell, 16, "2025 · Test im Nachhinein", LABEL, C["grey900"], "middle", 600),
    ]
    for m in range(24):
        body.append(txt(left + (m + .5) * cell, 37, MONTHS[m % 12][0], 14, C["grey500"], "middle"))
    row_h, gap = 30, 10
    for r, (label, spans) in enumerate(rows):
        y0 = top + 8 + r * (row_h + gap)
        body.append(txt(left - 14, y0 + 21, label, LABEL, C["grey900"], "end", 500))
        body.append(
            f'<rect x="{left}" y="{y0}" width="{right - left}" height="{row_h}" rx="4" '
            f'fill="{C["grey50"]}"/>'
        )
        for start, end, kind in spans:
            fill, ink = style[kind]
            x = left + start * cell + 1
            wid = (end - start) * cell - 2
            body.append(f'<rect x="{x:.1f}" y="{y0}" width="{wid:.1f}" height="{row_h}" rx="4" fill="{fill}">'
                        f"<title>{esc(label)}: {kind}</title></rect>")
            name = kind
            if kind == "Benchmark":
                name = f"Anwenden auf 2025 · {de(facts['test_n'])} Zähler-Monate"
            if kind == "Kalibrieren":
                body.append(txt(x - 10, y0 + 21, f"Kalibrieren · {de(facts['n_calibration'])} Fehler",
                                15, C["amber700"], "end", 600))
                continue
            body.append(txt(x + wid / 2, y0 + 21, name, 15, ink, "middle", 600))
    split_x = left + 12 * cell
    body.append(
        f'<line x1="{split_x:.1f}" x2="{split_x:.1f}" y1="24" y2="{top + 5 * (row_h + gap) + 4}" '
        f'stroke="{C["grey900"]}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    )
    lock_y = top + 3 * (row_h + gap) + 8 + row_h / 2  # Zeile "Schwelle"
    body.append(f'<circle cx="{split_x:.1f}" cy="{lock_y:.1f}" r="14" fill="{C["ist"]}" stroke="#fff" stroke-width="2"/>')
    lock = icon("lock", "#FFFFFF", 16).replace("<svg", f'<svg x="{split_x - 8:.1f}" y="{lock_y - 8:.1f}"', 1)
    body.append(lock)
    body.append(txt(split_x + 22, lock_y + 5, "eingefroren", 14, C["ist"], weight=600))
    return svg(w, h, "".join(body), "Zeitliche Validierung: drei Folds 2024, Kalibrierung Nov–Dez 2024, "
                                    "finales Modell auf ganz 2024, Test 2025")


def _hbar_axis(body, x, left, right, top, h):
    for tick in range(0, 28_001, 7_000):
        tx = x(tick)
        body.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="{top - 6}" y2="{h - 32}" stroke="{C["grey100"]}"/>')
        body.append(txt(tx, h - 10, de(tick / 1000), TICK, C["grey500"], "middle", mono=True))
    body.append(txt(left - 14, h - 10, "Tsd. kWh", TICK, C["grey500"], "end"))


def chart_cv(facts, w=526, h=240) -> str:
    rows = sorted(facts["cv"], key=lambda r: r["mean"])
    left, right, top = 200, w - 92, 60
    x = lin(0, 28_000, left, right)
    row_h = (h - top - 36) / len(rows)
    body = []
    _hbar_axis(body, x, left, right, top, h)
    for k, (color, label) in enumerate(zip(FOLD_COLORS, FOLD_LABELS)):
        lx = k * 168
        body.append(diamond(lx + 8, 13, 7, color))
        body.append(txt(lx + 22, 18, label, TICK, C["grey600"]))
    body.append(txt(w, 46, "Ø RMSE", TICK, C["grey500"], "end", 600))
    for i, row in enumerate(rows):
        yc = top + i * row_h + row_h / 2
        best = i == 0
        fill = C["prognose"] if best else C["grey300"]
        body.append(txt(left - 14, yc + 5, row["name"], LABEL, C["grey900"], "end", 600 if best else 400))
        body.append(rbar(left, yc - 12, x(row["mean"]) - left, 24, fill,
                         title=f"{row['name']}: Ø {de(row['mean'])} kWh (±{de(row['std'])})"))
        lo, hi = x(row["mean"] - row["std"]), x(row["mean"] + row["std"])  # ±1 Standardabweichung
        body.append(f'<path d="M{lo:.1f},{yc:.1f}H{hi:.1f}M{lo:.1f},{yc - 6:.1f}V{yc + 6:.1f}'
                    f'M{hi:.1f},{yc - 6:.1f}V{yc + 6:.1f}" stroke="{C["grey600"]}" stroke-width="1.5" fill="none"/>')
        for k, v in enumerate(row["folds"]):
            body.append(diamond(x(v), yc, 7.5, FOLD_COLORS[k], f"{row['name']} · {FOLD_LABELS[k]}: {de(v)} kWh"))
        body.append(txt(w, yc + 6, de(row["mean"]), 17, C["grey900"], "end", 600, True))
    return svg(w, h, "".join(body), "Mittlerer Validierungs-RMSE je Kandidat mit farbigen Fold-Werten und Streuung")


def chart_bench(facts, w=526, h=240) -> str:
    rows = sorted(facts["bench"], key=lambda r: r["rmse"])
    left, right, top = 200, w - 92, 60
    x = lin(0, 28_000, left, right)
    row_h = (h - top - 36) / len(rows)
    body = []
    _hbar_axis(body, x, left, right, top, h)
    body.append(txt(w, 46, "RMSE 2025", TICK, C["grey500"], "end", 600))
    body.append(txt(0, 18, "gleiche Skala wie links", TICK, C["grey500"]))
    for i, row in enumerate(rows):
        yc = top + i * row_h + row_h / 2
        best = i == 0
        body.append(txt(left - 14, yc + 5, row["name"], LABEL, C["grey900"], "end", 600 if best else 400))
        body.append(rbar(left, yc - 13, x(row["rmse"]) - left, 26, C["prognose"] if best else C["grey300"],
                         title=f"{row['name']}: {de(row['rmse'])} kWh"))
        body.append(txt(w, yc + 6, de(row["rmse"]), 17, C["grey900"], "end", 600, True))
    return svg(w, h, "".join(body), "Test-RMSE 2025 je Kandidat auf derselben Skala wie die Validierung")


def chart_ranked(facts, w=588, h=330) -> str:
    left, right, top, bottom = 58, w - 12, 28, h - 50
    pts = facts["ranked"]
    thr = facts["threshold"]
    x = lin(0, 100, left, right)
    y = lin(0, 500, bottom, top)
    body = []
    for tick in range(0, 501, 100):
        ty = y(tick)
        body.append(f'<line x1="{left}" x2="{right}" y1="{ty:.1f}" y2="{ty:.1f}" stroke="{C["grey100"]}"/>')
        body.append(txt(left - 10, ty + 5, str(tick), TICK, C["grey500"], "end", mono=True))
    for tick in (0, 25, 50, 75):
        body.append(txt(x(tick), bottom + 22, f"{tick} %", TICK, C["grey500"], "middle", mono=True))
    body.append(txt(left, bottom + 44, "Rang in der sortierten Liste (Perzentil)", TICK, C["grey600"]))
    body.append(txt(0, 12, "Fehlerbetrag in VLS-h", TICK, C["grey600"]))
    tail = [(px, py) for px, py in pts if py > thr]
    base = [(px, py) for px, py in pts if py <= thr]
    line = " ".join(f"{x(px):.1f},{y(py):.1f}" for px, py in base)
    body.append(f'<polyline points="{line}" fill="none" stroke="{C["residuum"]}" stroke-width="2.5"/>')
    tail_line = " ".join(f"{x(px):.1f},{y(py):.1f}" for px, py in [base[-1], *tail])
    body.append(f'<polyline points="{tail_line}" fill="none" stroke="{C["anomalie"]}" stroke-width="2.5"/>')
    for px, py in tail:
        body.append(f'<circle cx="{x(px):.1f}" cy="{y(py):.1f}" r="4.5" fill="{C["anomalie"]}" stroke="#fff" '
                    f'stroke-width="1.5"><title>{de(py, 1)} VLS-h</title></circle>')
    ty = y(thr)
    body.append(f'<line x1="{left}" x2="{right}" y1="{ty:.1f}" y2="{ty:.1f}" stroke="{C["schwelle"]}" '
                f'stroke-width="2" stroke-dasharray="6 4"/>')
    body.append(f'<line x1="{x(99):.1f}" x2="{x(99):.1f}" y1="{top}" y2="{bottom}" stroke="{C["grey400"]}" '
                f'stroke-width="1" stroke-dasharray="3 3"/>')
    body.append(txt(x(99), bottom + 22, "99 %", TICK, C["grey900"], "middle", 600, True))
    body.append(txt(left + 8, ty - 10, f"Schwelle q99 = {de(thr, 1)} VLS-h", LABEL, C["amber700"], weight=600))
    n_below = facts["n_calibration"] - facts["n_above"]
    body.append(txt(x(50), y(40) - 16, f"{de(n_below)} Fehler unter der Schwelle", LABEL, C["teal700"],
                    "middle", 600))
    body.append(txt(x(99) - 12, y(430), f"{facts['n_above']} Fehler darüber (1 %)", LABEL, C["red600"],
                    "end", 600))
    return svg(w, h, "".join(body), "Sortierte Fehlerbeträge der Kalibrierung mit 99-Prozent-Schwelle")


def chart_cal_compare(facts, w=520, h=106) -> str:
    """Kalibrierte Schwelle gegen nachträglich aus 2025 berechnete Schwelle (auf dunklem Grund)."""
    left, right = 0, w - 70
    x = lin(0, 200, left, right)
    rows = [
        ("Kalibriert Nov–Dez 2024 · gilt für 2025", facts["threshold"], "#0090C8", ""),
        ("Nachträglich aus 2025 · wäre Leakage", facts["q99_2025_hindsight"], "none", ' stroke-dasharray="5 4"'),
    ]
    body = []
    for i, (label, value, fill, dash) in enumerate(rows):
        y0 = 2 + i * 50
        body.append(txt(0, y0 + 14, label, TICK, "#BBD7EA"))
        if fill == "none":
            body.append(f'<rect x="{left}" y="{y0 + 22}" width="{x(value) - left:.1f}" height="22" rx="4" '
                        f'fill="rgba(255,255,255,.08)" stroke="#9CC3E0" stroke-width="1.5"{dash}/>')
        else:
            body.append(rbar(left, y0 + 22, x(value) - left, 22, fill))
        body.append(txt(x(value) + 10, y0 + 39, f"{de(value, 1)} VLS-h", 17, "#FFFFFF", weight=600, mono=True))
    return svg(w, h, "".join(body), "Kalibrierte Schwelle 144,4 VLS-h gegen nachträglich berechnete 175,1 VLS-h")


def chart_case(facts, w=578, h=436) -> str:
    left, right, top, bottom = 70, w - 12, 66, h - 36
    ist, prog = facts["case_ist"], facts["case_prognose"]
    band = facts["threshold"] * facts["case_kw"]
    x = lin(0, 11, left + 14, right - 14)
    y = lin(0, 26_000, bottom, top)
    body = []
    for tick in range(0, 26_001, 5_000):
        ty = y(tick)
        body.append(f'<line x1="{left}" x2="{right}" y1="{ty:.1f}" y2="{ty:.1f}" stroke="{C["grey100"]}"/>')
        body.append(txt(left - 10, ty + 5, de(tick), TICK, C["grey500"], "end", mono=True))
    body.append(txt(left - 10, top - 18, "kWh", TICK, C["grey600"], "end"))
    for i in range(12):
        body.append(txt(x(i), bottom + 24, MONTHS[i], TICK, C["grey500"], "middle"))
    upper = [f"{x(i):.1f},{y(p + band):.1f}" for i, p in enumerate(prog)]
    lower = [f"{x(i):.1f},{y(max(0, p - band)):.1f}" for i, p in reversed(list(enumerate(prog)))]
    body.append(f'<polygon points="{" ".join(upper + lower)}" fill="{C["band"]}"/>')
    body.append(f'<polyline points="{" ".join(f"{x(i):.1f},{y(p):.1f}" for i, p in enumerate(prog))}" '
                f'fill="none" stroke="{C["prognose"]}" stroke-width="2.5" stroke-dasharray="7 4"/>')
    body.append(f'<polyline points="{" ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(ist))}" '
                f'fill="none" stroke="{C["ist"]}" stroke-width="2.5"/>')
    for i, v in enumerate(ist):
        alert = abs(facts["case_factor"][i]) >= 1
        body.append(
            f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="{7 if alert else 4.5}" '
            f'fill="{C["anomalie"] if alert else C["ist"]}" stroke="#fff" stroke-width="2">'
            f"<title>{MONTHS[i]} 2025 · Ist {de(v)} kWh · Prognose {de(prog[i])} kWh · "
            f"Faktor {signed_de(facts['case_factor'][i])}</title></circle>"
        )
    aug = 7
    body.append(txt(x(aug) + 14, y(ist[aug]) + 6, f"Aug: Faktor {signed_de(facts['case_factor'][aug])}",
                    LABEL, C["red600"], weight=600))
    sep = 8
    body.append(txt(x(sep) + 10, y(ist[sep]) + 28, f"Sep: {signed_de(facts['case_factor'][sep])}",
                    TICK, C["grey600"]))
    # Legende
    body.append(f'<line x1="0" x2="26" y1="12" y2="12" stroke="{C["ist"]}" stroke-width="2.5"/>')
    body.append(txt(32, 17, "Ist", TICK, C["grey600"]))
    body.append(f'<line x1="66" x2="92" y1="12" y2="12" stroke="{C["prognose"]}" stroke-width="2.5" '
                f'stroke-dasharray="7 4"/>')
    body.append(txt(98, 17, "Prognose", TICK, C["grey600"]))
    body.append(f'<rect x="184" y="5" width="26" height="14" rx="3" fill="{C["band"]}"/>')
    body.append(txt(216, 17, f"Toleranz ± {de(band)} kWh", TICK, C["grey600"]))
    body.append(f'<circle cx="412" cy="12" r="6" fill="{C["anomalie"]}"/>')
    body.append(txt(424, 17, "Prüfhinweis", TICK, C["grey600"]))
    return svg(w, h, "".join(body), "ZL-00147 im Jahr 2025: Ist, Prognose und Toleranzband")


def chart_importance(rows, w=578, h=330) -> str:
    """rows: [(Name, RMSE-Anstieg in kWh)], absteigend."""
    left, right, top = 200, w - 120, 10
    x = lin(0, 7_500, left, right)
    row_h = (h - top - 20) / len(rows)
    body = []
    for i, (name, value) in enumerate(rows):
        yc = top + i * row_h + row_h / 2
        body.append(txt(left - 14, yc + 5, name, LABEL, C["grey900"], "end", 600 if i == 0 else 400))
        width = max(x(max(value, 0)) - left, 2)
        body.append(rbar(left, yc - 12, width, 24, C["ist"] if i == 0 else C["navy300"],
                         title=f"{name}: +{de(value)} kWh RMSE"))
        body.append(txt(left + width + 10, yc + 5, f"+{de(value)} kWh", TICK, C["grey900"], mono=True))
    return svg(w, h, "".join(body), "Permutation Importance nach Merkmalsgruppe")


def chart_monthly(facts, w=578, h=330) -> str:
    left, right, top, bottom = 46, w - 10, 30, h - 36
    values = facts["alerts_by_month"]
    mean = facts["n_alerts"] / 12
    y = lin(0, 18, bottom, top)
    bw = (right - left) / 12
    body = []
    for tick in range(0, 19, 6):
        body.append(f'<line x1="{left}" x2="{right}" y1="{y(tick):.1f}" y2="{y(tick):.1f}" stroke="{C["grey100"]}"/>')
        body.append(txt(left - 8, y(tick) + 5, str(tick), TICK, C["grey500"], "end", mono=True))
    for i, v in enumerate(values):
        x0 = left + i * bw + 6
        body.append(rbar(x0, y(v), bw - 12, bottom - y(v), C["residuum"], horizontal=False,
                         title=f"{MONTHS[i]} 2025: {v} Hinweise"))
        body.append(txt(x0 + (bw - 12) / 2, y(v) - 6, str(v), TICK, C["grey900"], "middle", 600, True))
        body.append(txt(left + i * bw + bw / 2, bottom + 22, MONTHS[i], TICK, C["grey500"], "middle"))
    body.append(f'<line x1="{left}" x2="{right}" y1="{y(mean):.1f}" y2="{y(mean):.1f}" stroke="{C["schwelle"]}" '
                f'stroke-width="2" stroke-dasharray="6 4"/>')
    body.append(txt(right, y(mean) - 8, f"Ø {de(mean, 1)} je Monat", LABEL, C["amber700"], "end", 600))
    return svg(w, h, "".join(body), "Prüfhinweise je Monat 2025")


def chart_scatter(facts, w=500, h=480) -> str:
    left, right, top, bottom = 62, w - 14, 84, h - 50
    vmax = 800
    x = lin(0, vmax, left, right)
    y = lin(0, vmax, bottom, top)
    thr = facts["threshold"]
    body = []
    for tick in range(0, vmax + 1, 200):
        body.append(f'<line x1="{left}" x2="{right}" y1="{y(tick):.1f}" y2="{y(tick):.1f}" stroke="{C["grey100"]}"/>')
        body.append(txt(left - 8, y(tick) + 5, str(tick), TICK, C["grey500"], "end", mono=True))
        body.append(txt(x(tick), bottom + 22, str(tick), TICK, C["grey500"], "middle", mono=True))
    body.append(txt(left, bottom + 44, "Prognose in VLS-h →", TICK, C["grey600"]))
    body.append(txt(0, top - 16, "↑ Ist in VLS-h", TICK, C["grey600"]))
    band = (f"{x(0):.1f},{y(thr):.1f} {x(vmax - thr):.1f},{y(vmax):.1f} {x(vmax):.1f},{y(vmax):.1f} "
            f"{x(vmax):.1f},{y(vmax - thr):.1f} {x(thr):.1f},{y(0):.1f} {x(0):.1f},{y(0):.1f}")
    body.append(f'<polygon points="{band}" fill="{C["band"]}"/>')
    dots = [f"M{x(px):.1f},{y(py):.1f}h0" for px, py in facts["scatter_normal"]
            if px is not None and py is not None and 0 <= px <= vmax and 0 <= py <= vmax]
    body.append(f'<path d="{" ".join(dots)}" stroke="{C["navy300"]}" stroke-width="3.2" '
                f'stroke-linecap="round" opacity=".55"/>')
    body.append(f'<line x1="{x(0)}" y1="{y(0)}" x2="{x(vmax)}" y2="{y(vmax)}" stroke="{C["ist"]}" stroke-width="1.5"/>')
    outside = []
    for px, py in facts["scatter_alerts"]:
        if 0 <= px <= vmax and 0 <= py <= vmax:
            body.append(f'<circle cx="{x(px):.1f}" cy="{y(py):.1f}" r="4.5" fill="{C["anomalie"]}" '
                        f'stroke="#fff" stroke-width="1"/>')
        else:
            outside.append((px, py))
    for px, py in outside:  # Hinweise jenseits des Ausschnitts als Dreieck am Rand
        cx = x(min(max(px, 0), vmax))
        body.append(f'<path d="M{cx:.1f},{top - 1:.1f} l-6,10 h12 z" fill="{C["anomalie"]}">'
                    f"<title>Ist {de(py)} VLS-h</title></path>")
    if outside:
        body.append(txt(w, 42, f"▲ {len(outside)} Hinweise über {vmax} VLS-h",
                        TICK, C["red600"], "end", 600))
    # Legende
    body.append(f'<circle cx="6" cy="12" r="4.5" fill="{C["navy300"]}"/>')
    body.append(txt(16, 17, "kein Hinweis", TICK, C["grey600"]))
    body.append(f'<circle cx="122" cy="12" r="5" fill="{C["anomalie"]}"/>')
    body.append(txt(133, 17, "Prüfhinweis", TICK, C["grey600"]))
    body.append(f'<line x1="232" x2="258" y1="12" y2="12" stroke="{C["ist"]}" stroke-width="1.5"/>')
    body.append(txt(264, 17, "Ist = Prognose", TICK, C["grey600"]))
    body.append(f'<rect x="6" y="30" width="24" height="14" rx="3" fill="{C["band"]}"/>')
    body.append(txt(36, 42, f"Band ± {de(thr, 1)} VLS-h (q99)", TICK, C["grey600"]))
    return svg(w, h, "".join(body), "Ist gegen Prognose 2025 in VLS mit Toleranzband und Prüfhinweisen")


def chart_lag(facts, w=578, h=340) -> str:
    left, right, top, bottom = 50, w - 16, 44, h - 36
    x = lin(0, 11, left + 10, right - 10)
    y = lin(50, 130, bottom, top)
    series = [
        ("Ist-VLS des Monats", C["ist"], "", "Ist des Monats"),
        ("Vormonat als Merkmal", C["grey500"], ' stroke-dasharray="7 4"', "Vormonat"),
        ("bis zu 3 Vormonate", C["navy300"], ' stroke-dasharray="2 4"', "Ø bis zu 3 Vormonate"),
    ]
    body = []
    for tick in range(50, 131, 20):
        body.append(f'<line x1="{left}" x2="{right}" y1="{y(tick):.1f}" y2="{y(tick):.1f}" stroke="{C["grey100"]}"/>')
        body.append(txt(left - 8, y(tick) + 5, str(tick), TICK, C["grey500"], "end", mono=True))
    for i in range(12):
        body.append(txt(x(i), bottom + 22, MONTHS[i], TICK, C["grey500"], "middle"))
    lx = 0
    for name, color, dash, legend in series:
        vals = facts["lag"][name]
        segs = [f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals) if v is not None and not math.isnan(v)]
        body.append(f'<polyline points="{" ".join(segs)}" fill="none" stroke="{color}" stroke-width="2.5"{dash}/>')
        body.append(f'<line x1="{lx}" x2="{lx + 24}" y1="10" y2="10" stroke="{color}" stroke-width="2.5"{dash}/>')
        body.append(txt(lx + 30, 15, legend, TICK, C["grey600"]))
        lx += 170
    return svg(w, h, "".join(body), "Lag-Features für ZL-00000 im Jahr 2024")


# --------------------------------------------------------------------------- Designsprache
#
# Drei Bausteine ziehen sich durch alle Folien (siehe Designkonzept):
#   1. Leitfrage mit Icon-Scheibe statt Eyebrow; der Titel ist die Antwort.
#   2. Icon-Scheiben (Lucide) als einzige Form für Konzepte; gleiche Scheibe = gleiches Konzept.
#   3. Zählwerk-Ziffern für höchstens eine Kernzahl je Folie (Bild aus der Welt der Stadtwerke).
# Dazu zeigt jede Fußzeile, welches Canvas-Feld die Folie belegt.

ICON_DIR = ROOT / "node_modules" / "lucide-static" / "icons"


@dataclass
class Slide:
    label: str
    html: str
    minutes: float = 0.0
    title: str = ""
    speech: list[str] = field(default_factory=list)
    reading: list[str] = field(default_factory=list)
    questions: list[tuple[str, str]] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    backup: bool = False


def icon(name: str, color: str = "#FFFFFF", size: int = 18, stroke: float = 2) -> str:
    """Lucide-SVG inline einbetten (ISC-Lizenz, node_modules/lucide-static)."""
    s = (ICON_DIR / f"{name}.svg").read_text(encoding="utf-8")
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r'\s*class="[^"]*"', "", s)
    s = s.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    s = s.replace('stroke="currentColor"', f'stroke="{color}"').replace('stroke-width="2"', f'stroke-width="{stroke}"')
    s = s.replace("<svg", '<svg aria-hidden="true" focusable="false"', 1)
    return re.sub(r"\s+", " ", s).strip()


# Scheiben-Töne: Hintergrund, Iconfarbe, Ring
TONES = {
    "navy": ("#084878", "#FFFFFF", None),        # Stufe 1 · Prognose
    "teal": ("#00718E", "#FFFFFF", None),        # Stufe 2 · Prüfung, ML-Canvas-Felder
    "amber": ("#A86505", "#FFFFFF", None),       # Schwelle
    "red": ("#B3261E", "#FFFFFF", None),         # Prüfhinweis-Faktor
    "green": ("#2F7A33", "#FFFFFF", None),       # innerhalb der Grenze
    "ring": ("#FFFFFF", "#084878", "#B4BFCB"),   # Team-Felder
    "off": ("#FFFFFF", "#8A96A3", "#D2DAE2"),    # inaktiver Tracker-Schritt
    "light": ("#6CC0D2", "#04263F", None),       # auf dunklem Grund
    "lamber": ("#C77E11", "#04263F", None),      # Schwelle auf dunklem Grund
    "glass": ("rgba(255,255,255,.10)", "#9CC3E0", "rgba(255,255,255,.24)"),
}


def disc(name: str, tone: str = "navy", d: int = 32) -> str:
    bg, fg, ring = TONES[tone]
    ring_css = f"box-shadow:inset 0 0 0 1.5px {ring};" if ring else ""
    return (f'<span class="disc" style="width:{d}px;height:{d}px;background:{bg};{ring_css}">'
            f"{icon(name, fg, round(d * 0.52))}</span>")


def zw(text: str, tone: str = "navy", size: int = 56) -> str:
    """Zählwerk: jede Ziffer in einer eigenen Zelle, Trennzeichen ohne Zelle."""
    cells = "".join(f"<b>{c}</b>" if c.isdigit() else f"<i>{c}</i>" for c in text)
    return f'<span class="zw zw-{tone}" style="font-size:{size}px">{cells}</span>'


def frac(num: str, den: str) -> str:
    return f'<span class="frac"><span>{num}</span><span>{den}</span></span>'


def merksatz(text: str, dark: bool = False) -> str:
    return (f'<div class="merk{" dark" if dark else ""}">{disc("lightbulb", "lamber" if dark else "amber", 30)}'
            f"<p>{text}</p></div>")


def icard(name: str, tone: str, title: str, body: str, cls: str = "") -> str:
    return (f'<div class="icard {cls}">{disc(name, tone, 34)}<div><strong>{title}</strong>'
            f"<p>{body}</p></div></div>")


# Canvas-Felder: Name, Icon; ML-Felder (Kikos Verantwortung) sind teal
CANVAS = {
    "01": ("Mehrwert", "gem"), "02": ("Datenquellen", "database"), "03": ("Vorhersage", "chart-spline"),
    "04": ("Merkmale", "sliders-horizontal"), "05": ("Lernansatz", "trees"), "06": ("Evaluation", "ruler"),
    "07": ("Entscheidung", "split"), "08": ("Impact", "target"), "09": ("Zeitpunkt", "calendar-clock"),
    "10": ("Monitoring", "activity"),
}
ML_FIELDS = {"03", "04", "05", "06", "07", "09"}

STEPS = ["Vergangenheit", "Modell", "Rückrechnung", "Istwert", "Residuum", "Prüfhinweis"]
STEP_ICONS = ["history", "trees", "calculator", "gauge", "diff", "flag"]


def tracker(active: set[int], dark: bool = False) -> str:
    items = []
    for i, name in enumerate(STEP_ICONS, start=1):
        on = i in active
        tone = ("light" if dark else ("navy" if i <= 3 else "teal")) if on else ("glass" if dark else "off")
        items.append(f'<span class="tstep" title="{i} {STEPS[i - 1]}">{disc(name, tone, 26)}</span>')
        if i == 3:
            items.append('<span class="trk-gap"></span>')
    first, last = min(active), max(active)
    nums = f"{first}" if first == last else f"{first}–{last}"
    label = f'<span class="tlabel">{nums} · {" · ".join(STEPS[i - 1] for i in sorted(active))}</span>'
    return f'<div class="tracker">{label}{"".join(items)}</div>'


def canvas_dots() -> str:
    dots = "".join(f'<span class="cdot{" ml" if nr in ML_FIELDS else ""}">{nr}</span>' for nr in CANVAS)
    return f'<div class="cdots"><span>10 von 10 Feldern</span>{dots}</div>'


def header(question: str, qicon: str, title: str, right: str = "", tone: str = "teal", dark: bool = False) -> str:
    qtone = {"teal": "light", "amber": "lamber", "navy": "light"}[tone] if dark else tone
    return (f'<header class="hd"><div class="hd-top"><div class="lq">{disc(qicon, qtone, 32)}<p>{question}</p></div>'
            f"{right}</div><h2>{title}</h2></header>")


def footer(refs: tuple[str, ...] = (), dark: bool = False, extra: str = "") -> str:
    """Seitenangabe wird in render_deck eingesetzt ({NUM})."""
    chips = "".join(
        f'<span class="cref">{disc(CANVAS[r][1], ("light" if dark else "teal") if r in ML_FIELDS else ("glass" if dark else "ring"), 22)}'
        f"<b>{r}</b>{CANVAS[r][0]}</span>" for r in refs)
    mid = f'<span class="crefs">{chips}</span>' if refs else ""
    return (
        f'<footer class="ft{" dark" if dark else ""}"><img src="{{LOGO}}" alt="StadtWerke Westhafen GmbH">'
        f"<span>{FOOTER_TITLE}</span>{mid}{extra}<span class=\"who\">{SPEAKER}</span>"
        '<span class="num">{NUM}</span></footer>'
    )


def screenshot(name: str, alt: str, cls: str = "shot") -> str:
    path = ASSET_DIR / name
    if not path.exists():
        return f'<div class="{cls} missing">Screenshot fehlt: {esc(name)}</div>'
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<img class="{cls}" src="data:image/png;base64,{data}" alt="{esc(alt)}">'


def highlight(left: float, top: float, width: float, height: float, tag: str, side: str = "right") -> str:
    """Markierung über einem Screenshot, Angaben in Prozent des Bildes."""
    return (
        f'<span class="hl {side}" style="left:{left}%;top:{top}%;width:{width}%;height:{height}%">'
        f"<em>{tag}</em></span>"
    )


# --------------------------------------------------------------------------- Inhalte des Canvas

# Folienfassung (Pfad-Layout, höchstens 2 Zeilen je Feld)
CANVAS_SHORT = {
    "01": ("Planen & früher prüfen", "Spotmarkt-Ausgleich senken, Auffälliges monatlich prüfen.", "← Iana"),
    "07": ("Beschaffen oder prüfen", "Prognose → Beschaffung; |F| ≥ 1 → Netzmanagement.", ""),
    "09": ("Monatlich, zwei Takte", "Prognose vor Monatsbeginn, Prüfung nach Monatsende.", ""),
    "03": ("Regression je Zähler", "Folgemonat in VLS, zurück in kWh; Residuum → Hinweis.", ""),
    "04": ("9 Merkmale, alle vorab", "Bewusst weg: Vorjahr, Temperatur, Anomalie-Spalte.", ""),
    "02": ("700 Zähler · 24 Monate", "CSV-Monatswerte: Verbrauch, Vertrag, Wetter, Pläne.", "← Iana"),
    "05": ("Überwachte Regression", "Random Forest gegen lineare Referenz; noch keine Labels.", ""),
    "06": ("RMSE in kWh", "2 Baselines, 3 Zeit-Folds, Test 2025; Precision@K im Pilot.", ""),
    "08": ("Test 2025: −15,9 % RMSE · 9,5 Hinweise/Monat",
           "Euro nicht belegt: Spotmarkt-Kosten, Prüfzeit und Bestätigungsquote misst der Pilot.", "→ Patrick"),
    "10": ("Monatlich kontrollieren",
           "Fehler, Drift, Hinweisvolumen je Monat; Schwelle oder Modell erst bei belegter Verschlechterung erneuern.",
           "→ Patrick"),
}
CANVAS_ORDER = ["01", "07", "09", "03", "04", "02", "05", "06", "08", "10"]

# Wortlaut Bericht, Tabelle A1 (Backup, damit Bericht und Präsentation übereinstimmen)
CANVAS_A1 = {
    "01": "Genauere Folgemonatsplanung und monatliche Prüfung ungewöhnlicher Zählerwerte.",
    "02": "Zählerverbräuche, Verträge, Kundentyp, Kalender, Wetter, Produktionsplan und Wartung.",
    "03": "VLS je Zähler-Monat; Rückrechnung in kWh; große Residuen werden Prüfhinweise.",
    "04": "Historie, Saison, Kalender, Wetterprognose, Produktionsplan, Wartung und Kundentyp.",
    "05": "Überwachte Regression; lineare Regression als Referenz, Random Forest als nichtlinearer Vergleich.",
    "06": "RMSE in kWh als Hauptmetrik; MAE und R² ergänzend; Vergleich mit zwei Baselines.",
    "07": "Prognose unterstützt Beschaffung; Hinweis führt zur menschlichen Prüfung.",
    "08": "Pilot-KPIs: Fehler, Hinweisvolumen, Prüfzeit und Bestätigungsquote.",
    "09": "Prognose vor Monatsbeginn; Residuenprüfung nach Eintreffen des Monatswerts.",
    "10": "Monatliche Fehler-, Drift- und Hinweiskontrolle; Retraining nur bei belegter Verschlechterung.",
}


def canvas_card(nr: str, x: int, y: int, w: int, h: int) -> str:
    name, ic = CANVAS[nr]
    head, body, owner = CANVAS_SHORT[nr]
    ml = nr in ML_FIELDS
    own = f'<span class="cv-own">{owner}</span>' if owner else ""
    return (f'<article class="cv {"ml" if ml else "team"}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="cv-top">{disc(ic, "teal" if ml else "ring", 36)}<span class="cv-nr">{nr}</span>'
            f'<span class="cv-name">{name}</span>{own}</div><h4>{head}</h4><p>{body}</p></article>')


# --------------------------------------------------------------------------- Folien


def build_slides(facts: dict) -> list[Slide]:
    thr = facts["threshold"]
    thr1 = de(thr, 1)
    wl = {row["q"]: row for row in facts["workload"]}
    q99, q95 = wl[99.0], wl[95.0]
    cv = {row["name"]: row for row in facts["cv"]}
    bench = {row["name"]: row["rmse"] for row in facts["bench"]}
    rf_cv, lr_cv = cv["Random Forest"]["mean"], cv["Lineare Regression"]["mean"]
    rf_gap = (1 - rf_cv / lr_cv) * 100
    kw = facts["case_kw"]
    aug = 7
    ist_aug, prog_aug = facts["case_ist"][aug], facts["case_prognose"][aug]
    res_aug = ist_aug - prog_aug
    f_aug = facts["case_factor"][aug]
    f_sep = facts["case_factor"][aug + 1]
    band = thr * kw
    monthly = facts["alerts_by_month"]
    share = facts["n_alerts"] / facts["test_n"] * 100
    per_week = facts["n_alerts"] / 52
    q95_ratio = q95["je_monat"] / q99["je_monat"]
    top3 = BERICHT["importance"][:3]

    slides: list[Slide] = []

    # ------------------------------------------------------------------ 1 ML Canvas komplett
    xs, w = [72, 363, 654, 945], 263
    cards = "".join(canvas_card(nr, xs[i], 148, w, 150) for i, nr in enumerate(CANVAS_ORDER[:4]))
    cards += "".join(canvas_card(nr, xs[i], 314, w, 150) for i, nr in enumerate(CANVAS_ORDER[4:8]))
    cards += canvas_card("08", 72, 480, 532, 144) + canvas_card("10", 632, 480, 532, 144)
    chev = "".join(f'<span class="chev" style="left:{x - 8}px;top:{y}px"></span>'
                   for x in (349, 640, 931) for y in (217, 383))
    chev += '<span class="chev" style="left:610px;top:546px"></span>'
    path = ('<svg class="cv-path" width="1280" height="720" aria-hidden="true">'
            '<path d="M1076 298 V306 H203 V314" fill="none" stroke="#6CC0D2" stroke-width="2.5"/>'
            '<path d="M1076 464 V472 H338 V480" fill="none" stroke="#6CC0D2" stroke-width="2.5"/></svg>')
    back = (f'<span class="cv-back">{disc("rotate-ccw", "ring", 32)}<b>01</b></span>')
    slides.append(Slide(
        "ML Canvas", minutes=115 / 60, title="ML Canvas: alle zehn Felder als Kette",
        html=f"""
<section class="slide light" data-screen-label="Kiko 01 ML Canvas">
{header("Passt vom Nutzen bis zur Wartung alles zusammen?", "puzzle", "ML Canvas: vom Nutzen zum Modell und zurück", canvas_dots())}
{path}{cards}{chev}{back}
{footer(extra='<span class="sponsor">Sponsor: Stefan Lechtenberg, Energiebeschaffung · Wortlaut: Bericht Tab. A1</span>')}
</section>""",
        speech=[
            "Danke, Iana. Ich zeige jetzt, wie daraus ein Modell wird. Zuerst als Canvas, alle zehn Felder, in der Reihenfolge, in der sie sich bedingen.",
            "Oben der Nutzen: weniger Ausgleich am Spotmarkt, und Auffälliges monatlich statt erst im Quartal prüfen. Daraus folgen zwei Entscheidungen: Die Prognose geht an die Beschaffung, ein Prüfhinweis an das Netzmanagement. Also zwei Takte, vor Monatsbeginn und nach Monatsende. Damit ist die Vorhersage klar: eine Regression, der Folgemonat je Zähler.",
            "Zweite Zeile, das Modell: nur Wissen, das vor Monatsbeginn vorliegt. Den Vorjahreswert, die Temperatur und die gelieferte Anomalie-Spalte lassen wir bewusst weg. Die Daten sind Monatswerte von 700 Zählern. Ein Random Forest tritt gegen eine lineare Referenz an; eine Klassifikation geht noch nicht, weil bestätigte Labels fehlen. Gemessen wird der RMSE in Kilowattstunden, der Einheit, in der die Beschaffung plant.",
            "Unten, was ankommt: im Test 2025 15,9 Prozent weniger Fehler als die beste einfache Regel [Pause] und rund zehn Prüfhinweise im Monat. [Pause] Euro haben wir nicht beziffert, das misst der Pilot. Und neu trainiert wird nur bei belegter Verschlechterung.",
        ],
        keywords=["Kette: Nutzen → Entscheidung → Takt → Vorhersage", "nur Vorab-Wissen, bewusst weggelassen",
                  "RMSE in kWh = Planungseinheit", "−15,9 % · 9,5/Monat · Euro misst der Pilot"],
        reading=[
            "Lesefolge wie ein Z: oben der Nutzen und was mit der Vorhersage passiert, Mitte womit gelernt und gemessen wird, unten Wirkung und Wartung; der Pfeil unten rechts führt zurück zum Mehrwert.",
            "Türkis umrandet sind die ML-Felder (meine Verantwortung laut Bericht Tab. 1). „← Iana“ heißt: schon gezeigt, „→ Patrick“: kommt gleich in den Ergebnissen und Empfehlungen.",
            "Die Kurzfassungen stimmen inhaltlich mit Tabelle A1 im Bericht überein; der Wortlaut steht auf Backup B1.",
        ],
        questions=[
            ("Warum zeigen Sie alle zehn Felder, obwohl die Vorlage fünf empfiehlt?",
             "Der Canvas ist die Klammer unseres Vorgehens. Die sechs ML-Felder sind hervorgehoben, die übrigen vier stehen je in zwei Zeilen. Der Wortlaut entspricht Tabelle A1 im Bericht (Backup B1)."),
            ("Warum Regression und keine Klassifikation?",
             "Es gibt keine bestätigten Anomalie-Labels. Deshalb lernen wir den erwarteten Verbrauch und leiten Auffälligkeiten aus dem Fehler ab. Mit gesammelten Bewertungen wird später eine Klassifikation möglich."),
            ("Welche Merkmale wurden bewusst weggelassen?",
             "Der Vorjahreswert (keine Historie aus 2023), die Temperatur (nahezu redundant zu den Heizgradtagen), die Spalte „anomalie“ (geliefertes Kennzeichen, kein bestätigtes Label) und die Vertragsleistung als Merkmal (sie dient nur zur Umrechnung)."),
            ("Welches Feld war am schwersten?",
             "Impact. Es gibt keine Preis- oder Prüfkostendaten und keine Labels. Deshalb nennen wir nur Belegtes (−15,9 %, 9,5 pro Monat) und lassen die Euro-Werte im Pilot messen."),
            ("Was ist Precision@K?",
             f"Der Anteil fachlich bestätigter Fälle unter den K obersten Hinweisen. Bei uns ist K die Prüfliste mit rund {de(q99['je_monat'], 1)} Fällen pro Monat; die Kennzahl entspricht der Bestätigungsquote."),
        ],
    ))

    # ------------------------------------------------------------------ 2 Fehlerkosten
    def cost_cell(ic, tone, head, body, lever):
        return (f'<div class="cost">{disc(ic, tone, 36)}<div><strong>{head}</strong><p>{body}</p>'
                f'<p class="lever">{icon("arrow-right", "#00718E", 15)}{lever}</p></div></div>')

    slides.append(Slide(
        "Fehlerkosten", minutes=40 / 60, title="Was kostet eine falsche Vorhersage?",
        html=f"""
<section class="slide mist" data-screen-label="Kiko 02 Fehlerkosten">
{header("Was kostet es, wenn das Modell falsch liegt?", "scale", "Fehler kosten Spotmarkt-Ausgleich oder Prüfzeit")}
<div class="body">
  <div class="units">
    <div class="ucard">{disc("gem", "ring", 34)}<div><span class="uk">01 Mehrwert</span><strong>genauer beschaffen · früher prüfen</strong></div></div>
    <span class="uarrow">{icon("arrow-right", "#6CC0D2", 26)}</span>
    <div class="ucard wide">{disc("scale", "teal", 34)}<div><span class="uk">Gleiche Einheiten</span><strong><span class="mono">kWh</span> Prognosefehler · <span class="mono">Fälle/Monat</span> Prüfvolumen · <span class="mono">Stunden</span> Prüfzeit</strong></div></div>
    <span class="uarrow">{icon("arrow-right", "#6CC0D2", 26)}</span>
    <div class="ucard">{disc("target", "ring", 34)}<div><span class="uk">08 Impact</span><strong>−{de(facts['baseline_gain_pct'], 1)} % RMSE · {de(q99['je_monat'], 1)} Hinweise/Monat</strong></div></div>
  </div>
  <div class="matrix">
    <span></span>
    <div class="mhead">{disc("chart-spline", "navy", 28)}<div><b>Stufe 1 · Prognose</b><span>→ Beschaffung (Stefan Lechtenberg)</span></div></div>
    <div class="mhead">{disc("flag", "amber", 28)}<div><b>Stufe 2 · Prüfhinweis</b><span>→ Netzmanagement (Anke Bürger)</span></div></div>
    <div class="mrow"><b>Zu viel</b><span>Prognose zu hoch · Fehlalarm</span></div>
    {cost_cell("trending-up", "navy", "Prognose zu hoch", "Überschuss am Spotmarkt verkaufen.", f"Hebel: RMSE 2025 {de(bench['Random Forest'])} statt {de(bench['Bis-zu-3-Monats-Mittel'])} kWh")}
    {cost_cell("bell-ring", "amber", "Fehlalarm", "Prüfzeit ohne Befund.", f"Hebel: q99 = {de(q99['je_monat'], 1)} statt {de(q95['je_monat'], 1)} Fälle/Monat (q95)")}
    <div class="mrow"><b>Zu wenig</b><span>Prognose zu niedrig · übersehen</span></div>
    {cost_cell("trending-down", "navy", "Prognose zu niedrig", "Fehlmenge am Spotmarkt zukaufen.", "Hebel: RMSE bestraft große Fehler stärker")}
    {cost_cell("eye-off", "amber", "Übersehen", "Fällt wie heute erst in der Quartalsauswertung auf.", "Hebel: Stichprobe unauffälliger Fälle misst den Recall")}
  </div>
  <p class="fnote">Euro-Beträge sind nicht belegt: Spotmarkt-Kosten, Prüfzeit und Bestätigungsquote misst der Pilot (Bericht, Canvas-Feld 08).</p>
</div>
{footer(("01", "08"))}
</section>""",
        speech=[
            "Was kostet es, wenn wir falsch liegen? Liegt die Prognose daneben, gleicht die Beschaffung am Spotmarkt aus: Überschuss verkaufen oder Fehlmenge zukaufen. Deshalb bestraft unsere Hauptmetrik große Fehler stärker.",
            f"Bei den Hinweisen kostet ein Fehlalarm Prüfzeit; ein übersehener Fall fällt wie heute erst im Quartal auf. Den Zielkonflikt steuert die Schwelle: {de(q99['je_monat'], 1)} statt {de(q95['je_monat'])} Fälle im Monat. [Pause] Euro misst erst der Pilot.",
        ],
        keywords=["Spotmarkt: verkaufen oder zukaufen", "Fehlalarm = Prüfzeit, übersehen = Quartal", "Schwelle steuert den Zielkonflikt"],
        reading=[
            "Oben: Mehrwert und Impact werden in denselben Einheiten gemessen (kWh, Fälle pro Monat, Prüfstunden), so verlangt es die Canvas-Vorlage.",
            "Die Matrix zeigt je Stufe beide Fehlerrichtungen und den Hebel, den wir im Projekt dagegen haben.",
        ],
        questions=[
            ("Wenn das Modell falsch liegt, wer ist betroffen?",
             "Bei einer Fehlprognose die Beschaffung (Stefan Lechtenberg) über den Spotmarkt-Ausgleich. Bei einem Fehlalarm oder einem übersehenen Fall das Netzmanagement (Anke Bürger): Prüfzeit oder späte Erkennung."),
            ("Was brächte es, wenn es morgen produktiv ginge?",
             f"Belegt sind {de(facts['baseline_gain_pct'], 1)} % weniger RMSE, im Mittel {de(bench['Bis-zu-3-Monats-Mittel'] - bench['Random Forest'])} kWh je Zähler-Monat, und etwa {de(q99['je_monat'], 1)} priorisierte Fälle pro Monat statt einer Quartalsauswertung. In Euro ist das nicht beziffert, deshalb zuerst ein Schattenbetrieb."),
        ],
    ))

    # ------------------------------------------------------------------ 3 Roter Faden (Split) mit Hook
    flow = [
        (1, "Vergangenheit", "Nur Informationen, die vor dem Prognosemonat bekannt sind."),
        (2, "Modell", "Random Forest schätzt die Vollaststunden (VLS) des Folgemonats."),
        (3, "Rückrechnung", "Prognose-VLS × Vertragsleistung = Prognose in kWh."),
        (4, "Istwert", "Nach Monatsende kommt der gemessene Verbrauch."),
        (5, "Residuum", "Ist minus Prognose, bezogen auf die Anschlussgröße."),
        (6, "Prüfhinweis", "Nur über der Schwelle prüft ein Mensch · Export ins Dashboard (JSON)."),
    ]
    flow_html = ""
    for nr, name, text in flow:
        if nr == 1:
            flow_html += '<div class="grp">Vor Monatsbeginn · Prognose <span>→ Beschaffung (S. Lechtenberg)</span></div>'
        flow_html += (f'<div class="fstep">{disc(STEP_ICONS[nr - 1], "navy" if nr <= 3 else "teal", 40)}'
                      f'<div><strong><span class="mono">{nr}</span> {name}</strong><p>{text}</p></div></div>')
        if nr == 3:
            flow_html += (f'<div class="fcut">{icon("calendar-days", "#657383", 16)}<span>Monat läuft</span></div>'
                          '<div class="grp late">Nach Monatsende · Prüfung <span>→ Netzmanagement (A. Bürger)</span></div>')
    slides.append(Slide(
        "Roter Faden", minutes=35 / 60, title="Methodik: vom Zählerwert zum Prüfhinweis",
        html=f"""
<section class="slide split" data-screen-label="Kiko 03 Roter Faden">
<div class="split-l">
  <span class="ring r1"></span><span class="ring r2"></span>
  <span class="big-nr">04</span><h2>Methodik und Modell</h2>
  <div class="hook">
    <div class="hook-top">{disc("gauge", "light", 34)}<span>ZL-00147 · August 2025</span></div>
    <span class="hook-lbl">gemessen</span>
    <div class="hook-val">{zw(de(ist_aug), "glass", 50)}<span>kWh</span></div>
    <p class="hook-exp">erwartet <b class="mono">{de(prog_aug)} kWh</b> · gut das Dreifache</p>
    <div class="hook-then"><span class="old">{icon("calendar-range", "#BBD7EA", 18)}Bisher: fällt erst in der Quartalsauswertung auf</span>
    <span class="new">{icon("flag", "#FFFFFF", 18)}Neu: Prüfhinweis direkt nach Monatsende</span></div>
  </div>
</div>
<div class="split-r">
  <div class="lq">{disc("route", "teal", 32)}<p>Wie wird aus Daten ein Prüfhinweis?</p></div>
  <div class="flow"><span class="wire"></span>{flow_html}</div>
  <p class="story">{icon("quote", "#00718E", 16)}User Story Henrik Maaß: reproduzierbarer Workflow mit dokumentierter Schwelle</p>
</div>
{footer(("03", "09"))}
</section>""",
        speech=[
            f"Ein echter Fall: Zähler ZL-00147, August 2025. Gemessen {de(ist_aug)} Kilowattstunden, erwartet gut {de(round(prog_aug, -2))}, mehr als das Dreifache. [Pause] Bisher fiele das erst in der Quartalsauswertung auf.",
            "Unser Weg zum Hinweis hat sechs Schritte: Vor Monatsbeginn schätzt das Modell aus der Vergangenheit den Verbrauch, zurückgerechnet in Kilowattstunden, für die Beschaffung. Nach Monatsende vergleichen wir mit dem Istwert, und nur über der Schwelle prüft ein Mensch.",
        ],
        keywords=["Hook: 23.563 statt 7.304 kWh", "bisher Quartal, neu nach Monatsende", "6 Schritte, zwei Takte"],
        reading=[
            "Links der Einstieg mit einem echten Fall, den wir am Ende auflösen. Rechts der rote Faden; er steht ab jetzt als Scheiben oben rechts auf jeder Methodenfolie.",
            "Zwischen Schritt 3 und 4 läuft der Monat: Prognose und Prüfung sind zwei getrennte Zeitpunkte.",
        ],
    ))

    # ------------------------------------------------------------------ 4 Validierung
    left_out = [("Vorjahr:", "keine Historie 2023"), ("Temperatur", "≈ Heizgradtage"),
                ("„anomalie“:", "kein Label"), ("Vertragsleistung:", "nur Umrechnung")]
    left_out_html = "".join(f'<span class="lo"><b>{a}</b> {b}</span>' for a, b in left_out)
    slides.append(Slide(
        "Zeitliche Validierung", minutes=50 / 60, title="Zeitliche Validierung ohne Leakage",
        html=f"""
<section class="slide light" data-screen-label="Kiko 04 Validierung">
{header("Warum diese Train/Test-Aufteilung?", "history", "Vergangenheit erklärt Zukunft, niemals umgekehrt", tracker({1}), "navy")}
<div class="body">
  <div class="card chart-card wide">{chart_folds(facts)}</div>
  <div class="row-3">
    {icard("history", "navy", "3-Monats-Mittel neu berechnet", "Die gelieferte Spalte enthielt spätere Werte (Leakage). Jetzt je Zähler nur abgeschlossene Monate.")}
    {icard("workflow", "navy", "Pipeline je Fold", "Auch das Auffüllen fehlender Werte lernt nur aus dem jeweiligen Lernblock.")}
    {icard("lock", "navy", "2025 entscheidet nichts", "Modell, Einstellungen und Schwelle stehen fest, bevor 2025 bewertet wird.")}
  </div>
  <div class="leftout">{disc("ban", "off", 30)}<span class="lo-k">Nicht im Modell</span>{left_out_html}</div>
</div>
{footer(("04", "06", "09"))}
</section>""",
        speech=[
            "Die wichtigste Regel: Das Modell darf nie aus der Zukunft lernen. Das nennt man Leakage. Deshalb prüfen wir in drei Durchläufen, sogenannten Folds: Jede Zeile ist ein Durchlauf, hellblau lernt das Modell, dunkelblau wird es bewertet, immer danach.",
            "November und Dezember legen die Schwelle fest, dann ist alles eingefroren. Das gewählte Modell lernt auf ganz 2024 und wird unverändert auf 2025 angewendet. Übrigens: Das gelieferte 3-Monats-Mittel enthielt spätere Werte; wir haben es je Zähler neu berechnet.",
        ],
        keywords=["nie aus der Zukunft lernen = kein Leakage", "3 Folds, Bewertung immer danach", "Nov–Dez Schwelle, dann eingefroren",
                  "3-Monats-Mittel neu berechnet"],
        reading=[
            "Jede Zeile ist ein Durchlauf. Hellblau = Training, dunkelblau = Bewertung, amber = Kalibrierung der Schwelle, türkis = Anwendung auf 2025. Das Schloss markiert den Stichtag: danach wird nichts mehr verändert.",
            f"Kalibrierung: {de(facts['n_calibration'])} rollierend erzeugte Fehler, November mit einem Modell aus Januar bis Oktober, Dezember mit einem Modell aus Januar bis November.",
            "Unten die bewusst weggelassenen Merkmale, wie es die Canvas-Vorlage (Feld 4) verlangt.",
        ],
        questions=[
            ("Was ist Leakage?",
             "Wenn das Modell beim Lernen Informationen erhält, die bei der echten Prognose noch nicht verfügbar wären, zum Beispiel spätere Monate oder einen Median über alle Daten. Bei uns steckte das im gelieferten 3-Monats-Mittel."),
            ("Nutzt ihr echtes Wetter des Prognosemonats?",
             f"Ja, vereinfachend: Die Heizgradtage des Monats stehen stellvertretend für eine Wetterprognose. Das ist leicht optimistisch, der Effekt ist aber klein (Permutation +{de(BERICHT['importance'][4][1])} kWh RMSE laut Bericht). Im Betrieb muss hier die Prognose stehen."),
        ],
    ))

    # ------------------------------------------------------------------ 5 Zielgröße VLS
    slides.append(Slide(
        "Zielgröße VLS", minutes=35 / 60, title="Zielgröße: Vollaststunden statt Kilowattstunden",
        html=f"""
<section class="slide mist" data-screen-label="Kiko 05 Zielgröße">
{header("Warum nicht direkt Kilowattstunden vorhersagen?", "divide", "Das Modell lernt Vollaststunden, geplant wird in kWh", tracker({2, 3}), "navy")}
<div class="body grid-3-2">
  <div class="stack tight">
    <div class="fcard">{disc("divide", "navy", 34)}<div><span class="fk">Normieren</span><div class="fexpr">VLS <span class="op">=</span> {frac("Verbrauch [kWh]", "Vertragsleistung [kW]")}</div></div></div>
    <div class="fcard">{disc("calculator", "navy", 34)}<div><span class="fk">Zurückrechnen</span><div class="fexpr">Prognose [kWh] <span class="op">=</span> Prognose-VLS <span class="op">×</span> kW</div></div></div>
    {icard("chart-column", "teal", "Aus unseren Daten", f"{BERICHT['streuung_zwischen_zaehlern']} % der Streuung im Rohverbrauch liegen zwischen den Zählern. In VLS liegen die Kundentyp-Mediane nur noch bei {BERICHT['median_kundentyp'][0]}–{BERICHT['median_kundentyp'][1]} h.")}
    <div class="chip-note">{disc("hotel", "ring", 30)}<p>Wie bei Hotels: Man vergleicht die Auslastung, nicht die Gästezahl.</p></div>
  </div>
  <div class="stack tight">
    <div class="card chart-card">{chart_vls_example()}</div>
    <div class="evidence"><span class="ev-v">−{de(facts['vls_gain_pct'], 1)} %</span><p>Test-RMSE gegenüber einem gleich abgestimmten, direkt auf kWh trainierten Random Forest<br><span class="mono">{de(facts['direct_kwh_rmse'])} → {de(facts['vls_rmse'])} kWh</span></p></div>
  </div>
</div>
{footer(("03", "05"))}
</section>""",
        speech=[
            f"Was soll das Modell lernen? Unsere Zähler sind sehr unterschiedlich groß: {BERICHT['streuung_zwischen_zaehlern']} Prozent der Streuung liegen zwischen den Zählern. Deshalb teilen wir durch die Vertragsleistung, wie ein Hotel die Auslastung vergleicht und nicht die Gästezahl.",
            f"Für die Beschaffung rechnen wir zurück in Kilowattstunden. Im Testjahr ist der Fehler so {de(facts['vls_gain_pct'], 1)} Prozent kleiner als bei einem direkt auf Kilowattstunden trainierten Modell.",
        ],
        keywords=["92 % Streuung zwischen Zählern", "Hotel: Auslastung statt Gästezahl", "zurück in kWh · −6,2 %"],
        reading=[
            "Rechts oben: 10.000 kWh bei 50 kW und 40.000 kWh bei 200 kW ergeben beide 200 Vollaststunden.",
            "VLS sind eine Normierung, keine gemessene Laufzeit. Das Ergebnis −6,2 % gilt für unsere Daten, nicht allgemein.",
        ],
        questions=[
            ("Heißt 200 VLS, dass die Anlage 200 Stunden unter Volllast lief?",
             "Nein. Es ist eine rechnerische Normierung (kWh ÷ kW) und keine gemessene Laufzeit."),
            ("Welcher Kundentyp ist am schwersten zu prognostizieren?",
             f"Nicht segmentiert ausgewertet. Nach der Normierung liegen die Mediane bei {BERICHT['median_kundentyp'][0]}–{BERICHT['median_kundentyp'][1]} VLS-h, und der Kundentyp bringt nur rund 3 kWh (Permutation, Bericht). Eine Auswertung je Kundentyp gehört in den Pilot."),
        ],
    ))

    # ------------------------------------------------------------------ 6 Modellwahl & Test
    top3_html = "".join(f'<li><span>{name}</span><b class="mono">+{de(value)}</b></li>' for name, value in top3)
    slides.append(Slide(
        "Modellwahl und Test", minutes=65 / 60, title="Modellvergleich: Validierung 2024 und Test 2025",
        html=f"""
<section class="slide light" data-screen-label="Kiko 06 Modellwahl">
{header("Schlägt das Modell eine einfache Regel?", "ruler", "Random Forest knapp vorn, einfache Regeln klar geschlagen", tracker({2, 3}), "navy")}
<div class="body">
  <div class="two-charts">
    <div class="card chart-card"><p class="ch-t">Auswahl · Ø RMSE über 3 zeitliche Folds 2024</p>{chart_cv(facts)}<p class="ch-note">Fold 1 liegt überall am höchsten und zieht jeden Mittelwert hoch. Strich = ±1 Std.</p></div>
    <div class="card chart-card"><p class="ch-t">Bestätigung · RMSE im Testjahr 2025</p>{chart_bench(facts)}<p class="ch-note mono">RMSE = √ Ø(Ist − Prognose)² · bestraft große Fehler, die am Spotmarkt teuer sind</p></div>
  </div>
  <div class="tiles">
    <div class="tile dark">{zw("−" + de(facts['baseline_gain_pct'], 1) + "%", "glass", 40)}<p>weniger RMSE als die beste einfache Regel<br><span class="mono">Test 2025: {de(bench['Bis-zu-3-Monats-Mittel'])} → {de(bench['Random Forest'])} kWh</span></p></div>
    <div class="tile">{disc("gauge", "navy", 34)}<div><span class="tk">Testjahr 2025</span><p class="tv"><b>RMSE</b> {de(facts['test_rmse'])} kWh · <b>MAE</b> {de(facts['test_mae'])} kWh · <b>R²</b> {BERICHT['r2']}</p><p class="ts">R² ist keine Trefferquote.</p></div></div>
    <div class="tile">{disc("sliders-horizontal", "teal", 34)}<div><span class="tk">Top-3-Treiber · Permutation, kWh</span><ul class="top3">{top3_html}</ul><p class="ts">betrieblich plausibel, keine Kausalität</p></div></div>
  </div>
</div>
{footer(("04", "05", "06"))}
</section>""",
        speech=[
            "Gemessen wird mit dem RMSE, dem typischen Fehler in Kilowattstunden; große Fehler zählen stärker. Kleiner ist besser, beide Diagramme haben dieselbe Skala.",
            f"Links die Auswahl 2024: Balken sind Mittelwerte, Rauten die einzelnen Folds. Der Random Forest liegt vorn, aber nur {de(rf_gap, 1)} Prozent vor der linearen Regression. Deshalb prüfen wir ein zweites Mal im Testjahr 2025.",
            f"Dort bleibt er vorn: {de(facts['baseline_gain_pct'], 1)} Prozent weniger Fehler als die beste einfache Regel. [Pause] Am meisten nutzt er die Verbrauchshistorie, mit großem Abstand vor Produktionsplan und Wartung.",
        ],
        keywords=["RMSE: große Fehler zählen stärker", "RF nur 2,7 % vor LR → zweite Prüfung", "−15,9 % im Test", "Treiber: Historie, Plan, Wartung"],
        reading=[
            "Rauten: Fold 1 amber (Mai–Jun), Fold 2 blau (Jul–Aug), Fold 3 grün (Sep–Okt). Der Strich zeigt ±1 Standardabweichung, kein Konfidenzintervall.",
            "Die Treiberwerte stammen aus dem Bericht (Tab. D1, fünf Wiederholungen); Notebook 13 zeigt mit drei Wiederholungen dieselbe Rangfolge.",
        ],
        questions=[
            ("Warum nicht die lineare Regression, wenn sie fast gleich gut ist?",
             f"Sie ist unsere erklärbare Referenz und ein guter Fallback. Der Random Forest gewinnt die zeitliche Validierung und bleibt 2025 vorn ({de(bench['Random Forest'])} vs. {de(bench['Lineare Regression'])} kWh). Der Abstand ist klein, das sagen wir offen."),
            ("Warum kein Gradient Boosting, wie im Auftrag vorgeschlagen?",
             f"Nicht getestet. Wir haben die Zeit in zeitliche Validierung und Kalibrierung gesteckt. Der Abstand RF zu LR beträgt nur {de(rf_gap, 1)} %; der eigentliche Gewinn liegt gegenüber den Baselines. Gradient Boosting wäre ein Kandidat für den Pilot."),
            ("Warum ist der Test-RMSE kleiner als der CV-RMSE?",
             "Auch die einfachen Regeln, die gar nicht trainiert werden, sind 2025 rund 30 % besser. Der Unterschied liegt vor allem an den bewerteten Monaten: Die Folds prüfen Mai bis Oktober 2024, der Test das ganze Jahr 2025."),
            ("Welche Monate haben die größten Restfehler?",
             f"In den Folds 2024 Fold 1 (Mai–Jun) mit {de(cv['Random Forest']['folds'][0])} kWh, Fold 2 {de(cv['Random Forest']['folds'][1])} kWh, Fold 3 {de(cv['Random Forest']['folds'][2])} kWh. Bei den Hinweisen 2025 die meisten im Juni ({max(monthly)}), die wenigsten im November ({min(monthly)})."),
            ("Ist das Modell overfitted?",
             "Es gibt kein klares Signal: begrenzte Baumtiefe, zeitliche Folds und ein gutes Testjahr. Endgültig ausschließen lässt es sich erst mit weiterem Betrieb."),
        ],
    ))

    # ------------------------------------------------------------------ 7 Vom Fehler zum Prüfhinweis
    slides.append(Slide(
        "Vom Fehler zum Prüfhinweis", minutes=45 / 60, title="Residuum, Perzentil-Schwelle und Faktor",
        html=f"""
<section class="slide mist" data-screen-label="Kiko 07 Prüfhinweis">
{header("Ab wann ist eine Abweichung ungewöhnlich?", "flag", "Aus dem Prognosefehler wird ein Prüfhinweis", tracker({4, 5, 6}), "amber")}
<div class="body grid-2-3">
  <div class="chain">
    <span class="chain-wire"></span>
    <div class="clink">{disc("diff", "navy", 36)}<div><span class="fk">Residuum</span><div class="fexpr">r <span class="op">=</span> {frac("Ist − Prognose [kWh]", "Vertragsleistung [kW]")}</div></div></div>
    <div class="clink">{disc("ruler", "amber", 36)}<div><span class="fk">Schwelle</span><div class="fexpr">q99 <span class="op">=</span> {thr1} VLS-h</div><p>99. Perzentil der {de(facts['n_calibration'])} Fehlerbeträge Nov–Dez 2024</p></div></div>
    <div class="clink">{disc("flag", "amber", 36)}<div><span class="fk">Faktor</span><div class="fexpr">F <span class="op">=</span> r ÷ q99</div><p><b>F ≥ +1 oder F ≤ −1 ⇒ Prüfhinweis</b> · keine Wahrscheinlichkeit</p></div></div>
    <div class="stairs"><span>Modellabweichung</span>{icon("chevron-right", "#8A96A3", 16)}<span class="on">Prüfhinweis</span>{icon("chevron-right", "#8A96A3", 16)}<span>bestätigte Anomalie</span></div>
  </div>
  <div class="card chart-card"><p class="ch-t">Kalibrierung Nov–Dez 2024 <span>· {de(facts['n_calibration'])} Fehlerbeträge, der Größe nach sortiert</span></p>{chart_ranked(facts)}<p class="ch-note">99 von 100 Vorwärtsfehlern waren kleiner als {thr1} VLS-h; {facts['n_above']} lagen darüber.</p></div>
</div>
{merksatz("Das Modell ersetzt keine Abrechnungsentscheidung. Es markiert nur, was eine Prüfung wert ist.")}
{footer(("03", "07"))}
</section>""",
        speech=[
            "Jetzt die zweite Stufe. Nach Monatsende bilden wir den Fehler und teilen ihn durch die Vertragsleistung. Ab wann ist er zu groß?",
            f"Wir haben {de(facts['n_calibration'])} Vorwärtsfehler aus November und Dezember sortiert. 99 von 100 waren kleiner als rund {de(thr)} Vollaststunden; das ist unsere Grenze. [Pause] Der Faktor teilt einen neuen Fehler durch diese Grenze: über plus eins oder unter minus eins entsteht ein Prüfhinweis.",
            "Ein Prüfhinweis ist noch keine Anomalie. Das Modell ersetzt keine Entscheidung, es markiert nur, was eine Prüfung wert ist.",
        ],
        keywords=["Fehler ÷ kW", "99 von 100 kleiner als 144", "|F| ≥ 1 → Hinweis", "Hinweis ≠ Anomalie"],
        reading=[
            "x-Achse: Rang des Fehlers von klein nach groß. y-Achse: Fehlerbetrag in VLS-h. Links viele kleine Fehler, rechts wenige große.",
            f"In kWh bekommt jeder Zähler seine eigene Grenze: q99 × kW, zum Beispiel {kw} kW → ± {de(band)} kWh.",
            f"Die Schwelle {de(thr, 4)} entsteht durch lineare Interpolation zwischen Rang 1.383 und 1.384 (NumPy-Quantil); sie ist kein echter Zeilenwert.",
        ],
        questions=[
            ("Woher kommen die 1.397 Fehler?",
             "Aus rollierend erzeugten Prognosen: November 2024 mit einem Modell aus Januar bis Oktober, Dezember mit einem Modell aus Januar bis November. Es sind echte Vorwärtsfehler, keine Trainingsfehler."),
            ("Warum kein Isolation Forest oder eine andere unüberwachte Anomalie-Erkennung?",
             "Der Auftrag verlangt Anomalien auf Basis der Residuen. Unser Vergleich mit einem Erwartungswert berücksichtigt Produktion, Wartung und Saison, und der Faktor ist direkt erklärbar. Einen Isolation Forest haben wir nicht verglichen."),
            ("Ist das eine bestätigte Anomalie?",
             "Nein. Ein Prüfhinweis ist eine ungewöhnliche Modellabweichung. Erst die fachliche Prüfung bestätigt oder verwirft sie."),
        ],
    ))

    # ------------------------------------------------------------------ 8 Kalibrierung (dunkel)
    cal_steps = [
        ("chart-spline", "Vorwärts prognostizieren",
         f"November mit einem Modell aus Jan–Okt, Dezember aus Jan–Nov: {de(facts['n_calibration'])} echte Prognosefehler."),
        ("snowflake", "Schwelle ableiten und einfrieren", f"99. Perzentil = {thr1} VLS-h. Danach wird sie nicht mehr verändert."),
        ("calendar-check", "2025 nur anwenden",
         f"Das finale Modell (ganz 2024) prognostiziert, die feste Schwelle entscheidet: {facts['n_alerts']} Prüfhinweise."),
    ]
    steps_html = "".join(
        f'<div class="cal-step">{disc(ic, "light", 38)}<div><strong>{t}</strong><p>{b}</p></div></div>'
        for ic, t, b in cal_steps
    )
    slides.append(Slide(
        "Kalibrierung", minutes=40 / 60, title="Kalibrierung: warum vorher, und was sie für 2025 bedeutet",
        html=f"""
<section class="slide dark" data-screen-label="Kiko 08 Kalibrierung">
{header("Warum nicht einfach die Schwelle aus 2025 nehmen?", "snowflake", "Die Schwelle wird vor 2025 festgelegt und dann eingefroren", tracker({5, 6}, dark=True), "amber", dark=True)}
<div class="body cal-layout">
  <div class="cal-steps">{steps_html}</div>
  <div class="stack tight">
    <div class="dpanel"><span class="dnr">Was die Kalibrierung für 2025 bedeutet</span>{chart_cal_compare(facts)}
      <div class="cal-stats"><div><b>{de(facts['median_cal'], 1)} → {de(facts['median_2025'], 1)}</b><span>typischer Fehler (Median, VLS-h): gleich groß</span></div><div><b>{de(share, 2)} %</b><span>über der festen Grenze statt 1 %: die Extreme sind 2025 größer</span></div></div>
    </div>
    <div class="dpanel"><span class="dnr">Warum gerade Nov–Dez 2024?</span><ul><li>Jüngste Monate vor dem Testjahr</li><li>Nicht für die Modellwahl genutzt (Folds enden im Oktober)</li><li>Später geht nicht, ohne 2025 selbst zu verwenden</li></ul></div>
  </div>
</div>
{merksatz("Kalibrieren ändert nur die Grenze, nicht Modell oder Prognose. Neu kalibriert wird erst, wenn Fehler oder Hinweisvolumen über mehrere Monate abweichen.", dark=True)}
{footer(("06", "07", "10"), dark=True)}
</section>""",
        speech=[
            "Warum steht die Schwelle schon Ende 2024 fest? Weil sie vor dem Testjahr feststehen muss, genau wie im Betrieb vor dem nächsten Monat. Danach ist sie eingefroren und ändert weder Modell noch Prognose.",
            f"Hätten wir sie nachträglich aus 2025 berechnet, läge sie bei {de(facts['q99_2025_hindsight'])} statt {de(thr)}. Das wäre Leakage. Die typischen Fehler sind gleich groß, nur die Ausreißer sind 2025 größer, deshalb {de(share, 2)} statt 1 Prozent.",
        ],
        keywords=["vor dem Testjahr, wie im Betrieb", "eingefroren, nur Entscheidungsgrenze", "2025-Schwelle 175 = Leakage", "Median gleich, Extreme größer"],
        reading=[
            "Kalibrieren heißt hier: die Entscheidungsgrenze festlegen. Es wird dabei nichts trainiert, und die Prognosen bleiben identisch.",
            f"Die gestrichelte Vergleichsschwelle ({de(facts['q99_2025_hindsight'], 1)} VLS-h) ist nur eine nachträgliche Einordnung und wurde für keine Entscheidung verwendet.",
        ],
        questions=[
            ("Wird die Schwelle für 2025 angepasst?",
             f"Nein, sie bleibt bei {thr1} VLS-h. Anders ist nur die Fehlerverteilung 2025: deshalb {de(share, 2)} % statt genau 1 %."),
            ("Sind zwei Wintermonate repräsentativ?",
             "Das ist die bekannte Grenze. Die typischen Fehler 2025 sind gleich groß, die Extreme größer. Im Betrieb würden wir quartalsweise überprüfen und erst bei belegter Abweichung neu kalibrieren, zum Beispiel auf den letzten zwölf Monaten."),
            ("Würden Sie ein Canvas-Feld heute anders schreiben?",
             f"Ja, Monitoring: mit einem konkreten Auslöser, etwa „Retraining prüfen, wenn der RMSE mehrere Monate über dem Testniveau von {de(facts['test_rmse'])} kWh liegt“. Das ist ein Vorschlag, der den Bericht präzisiert, und noch nicht getestet."),
        ],
    ))

    # ------------------------------------------------------------------ 9 Band 2025
    wl_cards = "".join(
        f'<div class="wl{" on" if row["q"] == 99.0 else ""}"><span class="wl-q">q{de(row["q"], 1 if row["q"] % 1 else 0)}</span>'
        f'<span class="wl-v">{de(row["je_monat"], 1)}</span><span class="wl-u">je Monat</span></div>'
        for row in facts["workload"]
    )
    slides.append(Slide(
        "Ist gegen Prognose 2025", minutes=50 / 60, title="Die Regel angewendet auf das Testjahr 2025",
        html=f"""
<section class="slide light" data-screen-label="Kiko 09 Band">
{header("Wie viele Fälle landen auf dem Prüftisch?", "clipboard-list", f"2025: {facts['n_alerts']} von {de(facts['test_n'])} Zähler-Monaten liegen außerhalb", tracker({5, 6}))}
<div class="body band-layout">
  <div class="card chart-card">{chart_scatter(facts)}</div>
  <div class="stack tight">
    <div class="hero">{zw(de(q99['je_monat'], 1), "glass", 56)}<div><strong>Prüfhinweise je Monat</strong><p>rund {de(per_week)} pro Woche · {facts['n_alerts']} Hinweise ({de(share, 2)} %) bei {facts['alert_meters']} Zählern<br>{facts['alerts_high']} ungewöhnlich hoch ↑ · {facts['alerts_low']} ungewöhnlich niedrig ↓</p></div></div>
    <div class="wl-box"><span class="flabel">Sensitivität · Hinweise je Monat 2025</span><div class="wl-grid">{wl_cards}</div>
      <div class="tradeoff"><span>← mehr Fehlalarme, weniger übersehen</span><span>weniger Fehlalarme, mehr übersehen →</span></div>
      <p>q95 hieße {de(q95_ratio, 1)}-mal so viele Fälle wie q99. Wie viel geprüft wird, legt der Fachbereich fest.</p></div>
    <div class="chip-note">{disc("shield-check", "green", 30)}<p>Plausibilisierung ohne Labels: alle 10 physikalisch unmöglichen Werte 2025 markiert. Sanity Check, kein Qualitätsbeweis.</p></div>
  </div>
</div>
{footer(("07", "08"))}
</section>""",
        speech=[
            "Jetzt die Regel auf ganz 2025: Jeder Punkt ist ein Zähler in einem Monat, nach rechts die Prognose, nach oben der Istwert. Auf der Diagonale wäre die Prognose perfekt, das Band ist unsere Grenze.",
            f"Rote Punkte sind Prüfhinweise: rund {de(q99['je_monat'])} im Monat, gut {de(per_week, 0)} pro Woche. [Pause] Mit dem 95. Perzentil wären es {de(q95['je_monat'])}. Wie viel geprüft werden kann, entscheidet der Fachbereich, nicht das Modell.",
        ],
        keywords=["Punkt = Zähler-Monat, Diagonale = perfekt", "9,5 pro Monat, rund 2 pro Woche", "q95 = 33 → Fachbereich entscheidet", "10/10 unmögliche Werte erkannt"],
        reading=[
            "Nur in VLS gibt es ein gemeinsames, paralleles Band. In kWh hängt die Grenze von der Vertragsleistung ab.",
            f"Monatliche Hinweise 2025: {' / '.join(str(v) for v in monthly)}. Achsen bei 800 VLS-h abgeschnitten; Hinweise darüber stehen als Dreieck am Rand.",
        ],
        questions=[
            ("Ihr sagt, 2025 entscheidet nichts. Wieso zeigt ihr dann den Prüfaufwand 2025?",
             "Die q99-Grenze wurde nur aus 2024 berechnet und auf 2025 unverändert angewendet. Die Zahlen rechts sind eine nachträgliche Sensitivitätsanalyse."),
            ("Warum keine verstellbare Winkel-Linie im Plot?",
             "Unsere Regel ist |Ist − Prognose| ÷ Vertragsleistung ≥ Schwelle, also ein fester Abstand in VLS. Eine Linie mit anderer Steigung wäre eine andere Regel (Verhältnis Ist/Prognose)."),
            ("Woher weiß man, dass die Hinweise sinnvoll sind?",
             "Ohne Labels nur als Plausibilisierung: Alle 10 bekannten physikalisch unmöglichen Werte in 2025 werden erfasst. Das ist ein Sanity Check, kein Qualitätsbeweis."),
        ],
    ))

    # ------------------------------------------------------------------ 10 Fallbeispiel
    ist_vls, prog_vls = ist_aug / kw, prog_aug / kw
    slides.append(Slide(
        "Prüffall ZL-00147", minutes=35 / 60, title=f"Fallbeispiel {facts['case_id']} durchgerechnet",
        html=f"""
<section class="slide light" data-screen-label="Kiko 10 Fallbeispiel">
{header("Warum wurde ZL-00147 markiert?", "scan-search", f"{facts['case_id']}: Im August ist die Abweichung {de(f_aug, 1)}-mal so groß wie erlaubt", tracker({4, 5, 6}))}
<div class="body grid-3-2 stretch">
  <div class="card chart-card"><div class="backref">{disc("gauge", "ring", 26)}<span>Vom Methodik-Start: <b class="mono">{de(ist_aug)}</b> statt <b class="mono">{de(prog_aug)} kWh</b></span></div>{chart_case(facts, h=400)}</div>
  <div class="stack tight">
    <div class="calc">
      <span class="flabel">August 2025 · Rechenweg</span>
      <div class="calc-row"><span>Ist − Prognose</span><b>{de(ist_aug)} − {de(prog_aug)} kWh</b></div>
      <div class="calc-row sum"><span>Residuum</span><b>{signed_de(res_aug, 1)} kWh</b></div>
      <div class="calc-row"><span>in VLS ({kw} kW)</span><b>{de(ist_vls, 1)} − {de(prog_vls, 1)} = {de(ist_vls - prog_vls, 1)}</b></div>
      <div class="calc-row"><span>÷ Schwelle q99</span><b>{thr1} VLS-h</b></div>
      <div class="calc-res"><span>Faktor</span>{zw(signed_de(f_aug, 2), "red", 36)}</div>
    </div>
    <div class="icard ok">{disc("circle-check", "green", 34)}<div><strong>September zum Vergleich</strong><p>Faktor {signed_de(f_sep, 2)} → innerhalb der Grenze, kein Hinweis. Die Prognose ist erhöht, weil der August als Vormonat einfließt.</p></div></div>
  </div>
</div>
{footer(("07",))}
</section>""",
        speech=[
            f"Zurück zu unserem Fall. Erwartet waren gut {de(round(prog_aug, -2))} Kilowattstunden, gemessen über {de(math.floor(ist_aug / 1000) * 1000)}. In Vollaststunden sind das rund {de(ist_vls - prog_vls)} zu viel, geteilt durch die Grenze ergibt das den Faktor {de(f_aug, 1)}. [Pause] Die Abweichung ist also {de(f_aug, 1)}-mal so groß wie erlaubt.",
            "Der September liegt mit minus 0,68 innerhalb der Grenze, also kein Hinweis.",
        ],
        keywords=["Auflösung des Hooks", "331,8 VLS-h ÷ 144,4 = 2,30", "2,3-mal so groß wie erlaubt", "September innerhalb"],
        reading=[
            f"Das Band ist Prognose ± {de(band, 1)} kWh ({de(thr, 2)} VLS-h × {kw} kW). Nur Punkte außerhalb werden rot.",
            f"Faktor {signed_de(f_aug, 2)} heißt: Der positive Fehler ist {de(f_aug, 2)}-mal so groß wie die Schwelle. Das ist keine Wahrscheinlichkeit. Die VLS-Werte stimmen mit dem Bericht überein (480,9 − 149,1 = 331,8).",
        ],
        questions=[
            ("Warum springt die Prognose im September?",
             "Der Augustwert steckt im Vormonats- und im Drei-Monats-Merkmal. Ausgeblendet werden bisher nur physikalisch unmögliche Werte. Bestätigte Anomalien sollten im Betrieb markiert werden, bevor sie in die Historie eingehen."),
            ("Welche eine Verbesserung hätte den größten Effekt?",
             "Bestätigte Anomalien aus der Historie herausnehmen, bevor sie in die Lags eingehen. ZL-00147 zeigt es: Der August-Ausreißer hebt die September-Prognose. Dafür braucht es die Bewertungen aus dem Dashboard."),
        ],
    ))

    # ------------------------------------------------------------------ 11 Dashboard + Ausblick (dunkel)
    slides.append(Slide(
        "Prüfen und bewerten", minutes=60 / 60, title="Im Dashboard prüfen, bewerten und daraus lernen",
        html=f"""
<section class="slide dark" data-screen-label="Kiko 11 Dashboard">
{header("Was passiert mit dem Hinweis, und was lernen wir daraus?", "clipboard-check", "Prüfen, bewerten und aus dem Feedback lernen", tracker({6}, dark=True), dark=True)}
<div class="body dash-grid">
  <div class="dash-col">
    <figure class="shot-card"><figcaption>{disc("file-search", "light", 26)}Fallakte · Warum wurde der Fall markiert?</figcaption><div class="shot-wrap">{screenshot("fallakte.png", "Fallakte ZL-00147 mit Ist, Prognose, Abweichung und Schwellenfaktor")}{highlight(74.6, 44.5, 24.8, 29, "Faktor")}{highlight(0.6, 75.5, 98.8, 22.5, "Begründung", "left")}</div></figure>
    <figure class="shot-card"><figcaption>{disc("list-checks", "light", 26)}Gespeichert · Status in der Prüfwarteschlange</figcaption><div class="shot-wrap">{screenshot("warteschlange_nachher.png", "Prüfwarteschlange mit Status Bewertung abgeschlossen")}{highlight(78.8, 76, 15.4, 22, "Status")}</div></figure>
  </div>
  <figure class="shot-card"><figcaption>{disc("pencil-line", "light", 26)}Bewertung dokumentieren · Beispieleingabe</figcaption><div class="shot-wrap">{screenshot("bewertung_dialog.png", "Dialog Bewertung dokumentieren mit getrennten Bewertungsdimensionen")}{highlight(1.8, 41.2, 96.4, 10.6, "Label-Quelle")}</div></figure>
</div>
<div class="learn"><span class="rule"><code>Messwert gültig = Ja</code> + <code>Abweichung erklärt = Nein</code> ⇒ <b>bestätigte Anomalie</b></span>
  <span class="lstep">{disc("badge-check", "light", 26)}Precision messen</span>
  <span class="lstep">{disc("scan-search", "light", 26)}Stichprobe für Recall</span>
  <span class="lstep">{disc("tags", "light", 26)}Klassifikation</span></div>
<div class="closing"><p>{icon("quote", "#6CC0D2", 18)}Mein Fazit: Bei Zeitreihendaten ist die Validierung wichtiger als das komplexeste Modell.</p><span class="handover">{icon("arrow-right", "#04263F", 18)}Patrick: Ergebnisse &amp; Empfehlungen</span></div>
{footer(("07", "08", "10"), dark=True)}
</section>""",
        speech=[
            "So sieht der Fall in meinem Dashboard aus. Die Fallakte begründet in einem Satz, warum er markiert wurde. Dann dokumentiert die Fachabteilung ihre Bewertung; in der Demo habe ich beispielhaft eingetragen: Messwert gültig, Abweichung nicht erklärt.",
            "So entsteht, was uns heute fehlt: ein bestätigtes Beispiel. Daraus messen wir zuerst die Precision; für den Recall prüfen wir zusätzlich eine Stichprobe unauffälliger Monate. Mit genug Beispielen kann später ein Klassifikationsmodell die Prüfliste sortieren.",
            f"ZL-00147 ist damit einer von {facts['n_alerts']} Hinweisen in einer sortierten Liste. [Pause] Mein Fazit: Bei Zeitreihen ist die Validierung wichtiger als das komplexeste Modell. Wie Beschaffung und Netzmanagement damit arbeiten, zeigt jetzt Patrick.",
        ],
        keywords=["Fallakte → Bewertung → Status", "Label: gültig + nicht erklärt", "Precision, Recall-Stichprobe, Klassifikation", "Fazit + Übergabe Patrick"],
        reading=[
            "Screenshots aus dem Energie-Cockpit, Fall ZL-00147 · 08/2025. Die Bewertung ist eine Beispieleingabe und wird nur lokal im Browser gespeichert; kein Ticket, kein Backend.",
            "Unterschied zu Patricks Verbrauchs-Cockpit: Dort entsteht nach der Prüfung ein Ticket. Hier wird der Fall fachlich bewertet und damit gelabelt.",
        ],
        questions=[
            ("Wie viele Labels bräuchte ein Klassifikationsmodell?",
             f"Vorab nicht seriös bezifferbar. Bei rund {de(q99['je_monat'], 1)} Hinweisen pro Monat kommen im Jahr etwa 110 bewertete Fälle zusammen. Das reicht für eine erste Precision. Für Recall und ein robustes Modell braucht es zusätzlich eine Zufallsstichprobe unauffälliger Fälle und mehrere Perioden."),
            ("Ersetzt die Klassifikation dann die Regression?",
             "Nein. Die Regression liefert weiter den Erwartungswert für die Beschaffung. Die Klassifikation würde nur die Prüfliste besser priorisieren; eine Prozentangabe wäre erst nach eigener Validierung und Kalibrierung belastbar."),
            ("Was ist Precision, was ist Recall?",
             "Precision: Anteil der Prüfhinweise, die sich fachlich bestätigen. Recall: Anteil aller echten Anomalien, die wir mit einem Hinweis gefunden haben."),
        ],
    ))

    # ------------------------------------------------------------------ Backups
    order_a = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
    a1_cells = "".join(
        f'<div class="a1{" ml" if nr in ML_FIELDS else ""}">{disc(CANVAS[nr][1], "light" if nr in ML_FIELDS else "glass", 28)}'
        f'<div><span class="a1-k"><b>{nr}</b> {CANVAS[nr][0]}</span><p>{CANVAS_A1[nr]}</p></div></div>'
        for nr in order_a)
    coherence = [
        ("01 ↔ 08", "gleiche Einheiten: kWh und Fälle pro Monat"),
        ("09 → 04", "nur Wissen, das vor Monatsbeginn vorliegt"),
        ("03 → 05 → 06", "Regression → RMSE in kWh"),
        ("07 ↔ 09", "Prognose vor, Prüfung nach Monatsende"),
    ]
    coh_html = "".join(f'<li><b class="mono">{a}</b><span>{b}</span></li>' for a, b in coherence)
    slides.append(Slide(
        "Backup Canvas Wortlaut", backup=True, title="Backup: ML Canvas im Wortlaut von Tabelle A1",
        html=f"""
<section class="slide dark" data-screen-label="Kiko B1 Canvas Wortlaut">
{header("Stimmt die Folie mit dem Bericht überein?", "book-open", "ML Canvas im Wortlaut von Tabelle A1", dark=True)}
<div class="body a1-layout"><div class="a1-grid">{a1_cells}</div>
  <div class="coh">{disc("link", "light", 32)}<span class="dnr">Kohärenz</span><ul>{coh_html}</ul></div></div>
{footer(dark=True)}
</section>""",
        speech=["Nur bei Rückfragen: zeigt den exakten Wortlaut des Berichts zu jedem Feld."],
        reading=["Links der Wortlaut aus Bericht Tab. A1, rechts die vier Kohärenzbeziehungen, die die Learning Journey abfragt."],
    ))

    tuning_rows = "".join(
        f'<tr class="{"best" if i == 0 else ""}"><td>{row["depth"]}</td><td>{row["features"]}</td>'
        f'<td>{row["leaf"]}</td><td class="num">{de(row["cv"])}</td><td class="num">{de(row["std"])}</td></tr>'
        for i, row in enumerate(facts["tuning"])
    )
    slides.append(Slide(
        "Backup Hyperparameter", backup=True, title="Backup: Hyperparameter-Suche",
        html=f"""
<section class="slide light" data-screen-label="Kiko B2 Hyperparameter">
{header("Wie wurde der Random Forest eingestellt?", "sliders-horizontal", "Acht kontrollierte Kombinationen, entschieden nur in 2024", tone="navy")}
<div class="body grid-3-2">
  <table class="tbl"><thead><tr><th>Baumtiefe</th><th>Merkmalsanteil</th><th>Min. Fälle je Blatt</th><th class="num">CV-RMSE (kWh)</th><th class="num">Fold-Streuung (Std., kWh)</th></tr></thead><tbody>{tuning_rows}</tbody></table>
  <div class="stack tight">
    {icard("trees", "navy", "Tiefe 8", "Begrenzte Tiefe vermeidet sehr spezielle Einzelregeln.")}
    {icard("layers", "navy", "Mindestens 5 Fälle je Blatt", "Ein Blatt steht nicht nur für einen einzelnen Zähler-Monat.")}
    {icard("shuffle", "navy", "70 % der Merkmale", "Bäume sehen unterschiedliche Merkmale und ergänzen sich.")}
    <p class="caveat">300 Bäume, random_state = 42. Die Unterschiede sind klein; entscheidend ist die zeitliche Prüfung.</p>
  </div>
</div>
{footer(("05",))}
</section>""",
        speech=["Nur bei Rückfragen zum Tuning zeigen."],
    ))
    slides.append(Slide(
        "Backup Treiber", backup=True, title="Backup: Permutation Importance",
        html=f"""
<section class="slide light" data-screen-label="Kiko B3 Treiber">
{header("Welche Informationen trägt das Modell?", "sliders-horizontal", "Die Verbrauchshistorie trägt den Großteil der Prognose", tone="navy")}
<div class="body grid-3-2">
  <div class="card chart-card"><p class="ch-t">Anstieg des Test-RMSE, wenn eine Gruppe gemischt wird <span>(kWh, Bericht Tab. D1)</span></p>{chart_importance(BERICHT['importance'])}</div>
  <div class="stack tight">
    {icard("shuffle", "navy", "So liest man es", "Steigt der Fehler stark, war die Information wichtig für die Prognose.")}
    {icard("factory", "teal", "Plausibel", "Historie, Produktionsplan und Wartung sind betriebliche Treiber; der Kundentyp steckt bereits in der Historie.")}
    {icard("triangle-alert", "amber", "Grenze", "Wichtigkeit ist keine Kausalität. Die Vertragsleistung wird nicht gemischt, sie ist der Umrechnungsfaktor.")}
    <p class="caveat">Bericht Tab. D1 mit fünf Wiederholungen; Notebook 13 mit drei Wiederholungen zeigt dieselbe Rangfolge.</p>
  </div>
</div>
{footer(("04",))}
</section>""",
        speech=["Top-3-Treiber: Verbrauchshistorie, Produktionsplan, Wartung. Nur bei Rückfragen zeigen."],
        questions=[("Wie stark trägt das Wetter bei?",
                    f"Beim Mischen steigt der RMSE um {de(BERICHT['importance'][4][1])} kWh, bei der Historie um {de(BERICHT['importance'][0][1])} kWh. Der saisonale Produktionsplan überlagert scheinbare Wettereffekte.")],
    ))
    slides.append(Slide(
        "Backup Lags", backup=True, title="Backup: Lag-Features",
        html=f"""
<section class="slide light" data-screen-label="Kiko B4 Lags">
{header("Wie entstehen die Historien-Merkmale?", "history", "Lag-Features verschieben bekannte Historie nach vorn", tone="navy")}
<div class="body grid-3-2">
  <div class="card chart-card"><p class="ch-t">Erster Zähler im Datensatz · ZL-00000 · 2024 <span>(VLS-h)</span></p>{chart_lag(facts)}</div>
  <div class="stack tight">
    {icard("calendar-x", "navy", "Januar 2024", "Echter Kaltstart: keine Historie. Die Werte bleiben leer und werden im Fold aufgefüllt.")}
    {icard("calendar-days", "navy", "Februar und März", "Nutzen die verfügbare Historie (1 bzw. 2 Monate).")}
    {icard("calendar-range", "navy", "Ab April", "Mittel aus bis zu drei gültigen, abgeschlossenen Vormonaten (Umsetzung mit shift(1)).")}
    <p class="caveat">So bleiben 1.453 Drei-Monats-Werte erhalten; nur 700 Januar-Kaltstarts sind leer.</p>
  </div>
</div>
{footer(("04",))}
</section>""",
        speech=["Nur bei Rückfragen zu fehlenden Werten und Leakage."],
    ))
    cols = [
        ("badge-check", "Belegt", "Prognose schlägt einfache Regeln",
         [f"RMSE {de(facts['test_rmse'])} kWh, MAE {de(facts['test_mae'])} kWh", f"−{de(facts['baseline_gain_pct'], 1)} % gegenüber Ø bis zu 3 Vormonate", "Kein klares Overfitting-Signal"]),
        ("scale", "Entscheidung", "q99 ist eine Pilotannahme",
         [f"{de(q99['je_monat'], 1)} Hinweise pro Monat, {q99['hinweise']} im Jahr 2025", "Per Regler verschiebbar, ohne Retraining", "Fachbereich legt die Kapazität fest"]),
        ("circle-help", "Offen", "Keine Precision und Recall",
         ["Prüfhinweis ≠ bestätigte Anomalie", "2025 ist retrospektiv, kein Blindtest", "Pilot mit Bewertungen und Stichprobe liefert die Evidenz"]),
        ("shield-check", "Verantwortung", "Der Mensch entscheidet",
         ["Kundentypen Gewerbe, Industrie, Kommunal", "Bewertungen im Prototyp nur lokal", "Hinweisquote je Kundentyp im Pilot beobachten"]),
    ]
    cols_html = "".join(
        f'<div class="dcard">{disc(ic, "light", 32)}<span class="dnr">{k}</span><h4>{h}</h4><ul>{"".join(f"<li>{b}</li>" for b in bl)}</ul></div>'
        for ic, k, h, bl in cols)
    slides.append(Slide(
        "Backup Grenzen", backup=True, title="Backup: Grenzen und Verantwortung",
        html=f"""
<section class="slide dark" data-screen-label="Kiko B5 Grenzen">
{header("Was können wir belastbar sagen, und was nicht?", "shield-check", "Was wir belastbar sagen können und was noch Daten braucht", dark=True)}
<div class="body four-dark">{cols_html}</div>
{merksatz("Verfügbarkeit: Die Heizgradtage stehen vereinfachend für die Wetterprognose. Im Betrieb Prognose- und Planversionen zum Stichtag speichern.", dark=True)}
{footer(dark=True)}
</section>""",
        speech=["Gute Folie für kritische Rückfragen zu Grenzen, Ethik und Verantwortung."],
        questions=[("Werden bestimmte Gruppen benachteiligt? Wie steht es um den Datenschutz?",
                    "Die Daten betreffen Zähler von Gewerbe-, Industrie- und kommunalen Kunden. VLS gleicht die Anschlussgröße aus. Die Hinweisquote je Kundentyp ist noch nicht ausgewertet und gehört ins Pilot-Monitoring. Bewertungen liegen im Prototyp nur lokal im Browser.")],
    ))
    slides.append(Slide(
        "Backup Prüfaufwand", backup=True, title="Backup: Prüfaufwand statt ROI",
        html=f"""
<section class="slide light" data-screen-label="Kiko B6 Prüfaufwand">
{header("Was kostet der Betrieb, solange Euro fehlen?", "clipboard-list", "Prüfaufwand statt ROI: belegte Mengen, keine erfundenen Euro")}
<div class="body grid-3-2">
  <div class="card chart-card"><p class="ch-t">Prüfhinweise je Monat 2025 <span>(q99)</span></p>{chart_monthly(facts)}</div>
  <div class="stack tight">
    {icard("scale", "amber", "Worst Case beim Aufwand", f"q95 statt q99: {de(q95['je_monat'], 1)} statt {de(q99['je_monat'], 1)} Fälle im Monat, also {de(q95_ratio, 1)}-facher Prüfaufwand.")}
    {icard("undo-2", "navy", "Rückfall", "Ist das Modell im Pilot nicht besser: lineare Regression oder das Mittel der letzten drei Monate.")}
    {icard("clipboard-check", "teal", "Im Pilot erfassen", "Prüfzeit je Fall, Bestätigungsquote und Spotmarkt-Mengen. Erst daraus entsteht eine Euro-Rechnung.")}
  </div>
</div>
{footer(("08", "10"))}
</section>""",
        speech=["Für Rückfragen zu Kosten und ROI: bewusst keine Euro-Annahmen."],
    ))
    return slides


# --------------------------------------------------------------------------- Seiten

SYMBOLS = "→←⇒≤≥≠√≈▲"


def _symbol_faces() -> str:
    """Pfeile und Relationszeichen fehlen in den Latin-Subsets von Plex und Geist.

    Aus DejaVu (freie Lizenz, liegt mit matplotlib bei) wird ein Mini-Subset gebaut und
    per unicode-range unter denselben Familiennamen eingebettet, damit jeder Rechner
    dieselben Glyphen zeigt.
    """
    import io
    import logging

    import matplotlib
    from fontTools import subset

    logging.getLogger("fontTools").setLevel(logging.ERROR)
    from fontTools.ttLib import TTFont

    font_dir = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"
    ranges = ",".join(f"U+{ord(ch):04X}" for ch in SYMBOLS)
    faces = []
    for family, weight, file in [
        ("IBM Plex Sans", 400, "DejaVuSans.ttf"), ("IBM Plex Sans", 600, "DejaVuSans-Bold.ttf"),
        ("Geist Mono", 400, "DejaVuSansMono.ttf"), ("Geist Mono", 600, "DejaVuSansMono-Bold.ttf"),
    ]:
        font = TTFont(font_dir / file)
        options = subset.Options()
        options.flavor = "woff2"
        subsetter = subset.Subsetter(options)
        subsetter.populate(text=SYMBOLS)
        subsetter.subset(font)
        buffer = io.BytesIO()
        font.flavor = "woff2"
        font.save(buffer)
        data = base64.b64encode(buffer.getvalue()).decode()
        faces.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{ranges}}}"
        )
    return "".join(faces)


def _font_face() -> str:
    faces = []
    for family, weight, file in [
        ("IBM Plex Sans", 400, "ibm-plex-sans-latin-400-normal.woff2"),
        ("IBM Plex Sans", 500, "ibm-plex-sans-latin-500-normal.woff2"),
        ("IBM Plex Sans", 600, "ibm-plex-sans-latin-600-normal.woff2"),
        ("IBM Plex Sans", 700, "ibm-plex-sans-latin-700-normal.woff2"),
        ("Geist Mono", 400, "geist-mono-latin-400-normal.woff2"),
        ("Geist Mono", 600, "geist-mono-latin-600-normal.woff2"),
    ]:
        data = base64.b64encode((FONT_DIR / file).read_bytes()).decode()
        faces.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
            f"font-display:block;src:url(data:font/woff2;base64,{data}) format('woff2')}}"
        )
    return "".join(faces) + _symbol_faces()


CSS = """
*{box-sizing:border-box}
html,body{margin:0;background:#232C36}
body{font-family:'IBM Plex Sans','Segoe UI',sans-serif;color:#141A21;-webkit-font-smoothing:antialiased}
.deck{display:flex;flex-direction:column;align-items:center;gap:24px;padding:24px 0}
.slide{position:relative;width:1280px;height:720px;overflow:hidden;flex:none;display:flex;flex-direction:column;background:#fff}
.slide.mist{background:#F1F4F7}
.slide.dark{background:#063659;color:#fff}
.mono,code{font-family:'Geist Mono',monospace}
code{font-size:.92em;background:#EDF3F9;border-radius:4px;padding:1px 5px;color:#084878}
/* Scheiben und Zählwerk */
.disc{display:inline-grid;place-items:center;border-radius:50%;flex:none}
.disc svg{display:block}
.zw{display:inline-flex;align-items:center;gap:.06em;font-family:'Geist Mono',monospace;font-weight:600;line-height:1}
.zw b{display:inline-grid;place-items:center;width:.74em;height:1.16em;border-radius:.12em;font-weight:600}
.zw i{font-style:normal;width:.34em;text-align:center}
.zw-navy b{background:#04263F;color:#fff}.zw-navy i{color:#00718E}
.zw-glass b{background:rgba(255,255,255,.10);box-shadow:inset 0 0 0 1px rgba(255,255,255,.22);color:#fff}.zw-glass i{color:#6CC0D2}
.zw-red b{background:#B3261E;color:#fff}.zw-red i{color:#B3261E}
/* Kopf: Leitfrage + Titel */
.hd{padding:38px 72px 0;position:relative;z-index:2}
.hd-top{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:0 0 10px;min-height:32px}
.lq{display:flex;align-items:center;gap:12px;min-width:0}
.lq p{margin:0;font-size:20px;font-weight:500;color:#00718E;white-space:nowrap}
.dark .lq p{color:#6CC0D2}
.hd h2{font-size:36px;font-weight:600;letter-spacing:-.02em;line-height:1.14;margin:0;text-wrap:balance}
/* Tracker als Zählwerk aus Scheiben */
.tracker{display:flex;align-items:center;gap:6px;flex:none}
.tlabel{font-size:14px;font-weight:600;color:#005E77;margin-right:6px;white-space:nowrap}
.dark .tlabel{color:#6CC0D2}
.trk-gap{width:18px;height:0;border-top:2px dashed #B4BFCB}
.dark .trk-gap{border-top-color:rgba(255,255,255,.3)}
.cdots{display:flex;align-items:center;gap:4px;flex:none}
.cdots>span:first-child{font-size:14px;color:#657383;margin-right:6px}
.cdot{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;font:600 11px 'Geist Mono',monospace;background:#fff;color:#657383;box-shadow:inset 0 0 0 1.5px #B4BFCB}
.cdot.ml{background:#00718E;color:#fff;box-shadow:none}
/* Körper */
.body{flex:1;padding:22px 72px 0;display:flex;flex-direction:column;gap:16px;min-height:0;position:relative;z-index:1}
.body.grid-3-2,.body.grid-2-3{display:grid;align-items:start}
.grid-3-2{grid-template-columns:1.25fr 1fr;gap:22px}
.grid-2-3{grid-template-columns:1fr 1.3fr;gap:22px}
.body.stretch{align-items:stretch;padding-bottom:16px}
.stack{display:flex;flex-direction:column;gap:14px}
.stack.tight{gap:12px}
.row-3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.row-3 .icard{padding:11px 14px}.row-3 .icard p{font-size:14.5px}
.card{background:#fff;border:1px solid #D2DAE2;border-radius:10px;box-shadow:0 1px 2px rgba(4,38,63,.05),0 2px 6px rgba(4,38,63,.05)}
.chart-card{padding:16px 20px}
.chart-card.wide{padding:16px 20px 8px}
.ch-t{font-size:16px;font-weight:600;margin:0 0 8px;color:#141A21}.ch-t span{font-weight:400;color:#657383}
.ch-note{font-size:14px;line-height:1.35;color:#4E5A68;margin:4px 0 2px}
.ch-note.mono{font-size:13px;color:#084878}
.caveat{font-size:15px;color:#657383;margin:0;line-height:1.4}
/* Fußzeile mit Canvas-Bezug */
.ft{display:flex;align-items:center;gap:16px;padding:18px 72px 22px;font-size:16px;color:#6B7887;border-top:1px solid #E4E9EF;margin-top:auto;position:relative;z-index:2}
.ft img{display:block;height:26px;width:auto}
.ft .crefs{display:flex;gap:12px;margin-left:14px;padding-left:16px;border-left:1px solid #E4E9EF}
.ft .cref{display:inline-flex;align-items:center;gap:6px;font-size:14px;color:#4E5A68;white-space:nowrap}
.ft .cref b{font-family:'Geist Mono',monospace;font-weight:600;color:#00718E}
.ft .sponsor{font-size:14px;color:#657383;margin-left:14px;padding-left:16px;border-left:1px solid #E4E9EF}
.ft .who{margin-left:auto;font-weight:600;color:#4E5A68}
.ft .num{font-family:'Geist Mono',monospace;min-width:64px;text-align:right}
.ft.dark{color:#7FB4D8;border-top-color:rgba(255,255,255,.16)}
.ft.dark img{background:#fff;border-radius:4px;padding:4px 6px}
.ft.dark .who{color:#BBD7EA}
.ft.dark .crefs,.ft.dark .sponsor{border-left-color:rgba(255,255,255,.16)}
.ft.dark .cref{color:#BBD7EA}.ft.dark .cref b{color:#6CC0D2}
/* Karten mit Scheibe (ersetzen Akzentstreifen) */
.icard{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:13px 16px;box-shadow:0 1px 2px rgba(4,38,63,.05)}
.icard strong{display:block;font-size:16px;color:#084878;margin:1px 0 3px}
.icard p{margin:0;font-size:15px;line-height:1.4;color:#4E5A68}
.icard.ok{background:#F5FAF3;border-color:#CFE7C8}
.chip-note{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid #D2DAE2;border-radius:999px;padding:6px 18px 6px 6px}
.chip-note p{margin:0;font-size:15px;line-height:1.35;color:#141A21}
.merk{display:flex;gap:14px;align-items:center;margin:12px 72px 14px;background:#E3F3F7;border-radius:10px;padding:11px 20px 11px 12px;position:relative;z-index:1}
.merk p{margin:0;font-size:18px;line-height:1.35;color:#005E77;font-weight:500}
.merk.dark{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16)}
.merk.dark p{color:#fff}
/* Formeln */
.fcard{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:14px 18px}
.fk{display:block;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#00718E;margin:0 0 6px}
.fexpr{font-family:'Geist Mono',monospace;font-size:20px;font-weight:600;color:#084878;display:flex;align-items:center;flex-wrap:wrap;gap:8px;line-height:1.3}
.op{color:#00718E}
.frac{display:inline-flex;flex-direction:column;align-items:center;font-size:.8em;vertical-align:middle}
.frac span:first-child{border-bottom:2px solid #084878;padding:0 4px 3px}.frac span:last-child{padding:3px 4px 0}
.evidence{display:flex;gap:18px;align-items:center;background:#063659;color:#fff;border-radius:10px;padding:14px 20px}
.ev-v{font-family:'Geist Mono',monospace;font-size:46px;font-weight:600;white-space:nowrap;letter-spacing:-.02em}
.evidence p{margin:0;font-size:15px;line-height:1.4;color:#BBD7EA}.evidence .mono{color:#fff}
/* 1 Canvas als Pfad */
.cv{position:absolute;border-radius:10px;padding:14px 16px;z-index:1}
.cv.ml{background:#fff;border:2px solid #00718E;box-shadow:0 1px 2px rgba(4,38,63,.06),0 4px 12px rgba(4,38,63,.08)}
.cv.team{background:#F1F4F7;border:1px solid #E4E9EF}
.cv-top{display:flex;align-items:center;gap:8px;height:36px}
.cv-nr{font:600 14px 'Geist Mono',monospace;color:#00718E}
.cv.team .cv-nr{color:#657383}
.cv-name{font-size:14px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#4E5A68}
.cv h4{margin:10px 0 4px;font-size:18px;line-height:23px;font-weight:600;color:#084878}
.cv.team h4{color:#141A21}
.cv p{margin:0;font-size:15px;line-height:20px;color:#4E5A68}
.cv-own{margin-left:auto;font-size:13px;color:#657383;white-space:nowrap}
.chev{position:absolute;width:12px;height:12px;border-top:3px solid #6CC0D2;border-right:3px solid #6CC0D2;transform:rotate(45deg);z-index:1}
.cv-path{position:absolute;left:0;top:0;z-index:0}
.cv-back{position:absolute;left:1172px;top:522px;display:flex;flex-direction:column;align-items:center;gap:4px;z-index:1}
.cv-back b{font:600 14px 'Geist Mono',monospace;color:#00718E}
/* 2 Fehlerkosten */
.units{display:flex;align-items:center;gap:10px}
.ucard{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:12px 16px;flex:1;min-height:86px}
.ucard.wide{flex:1.35;background:#E3F3F7;border-color:#B2DEE7}
.uk{display:block;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#657383;margin-bottom:3px}
.ucard strong{font-size:16px;line-height:1.35;color:#141A21;font-weight:600}
.ucard .mono{color:#00718E}
.uarrow{flex:none;display:grid;place-items:center}
.matrix{display:grid;grid-template-columns:168px 1fr 1fr;gap:10px 14px;align-items:stretch}
.mhead{display:flex;gap:10px;align-items:center;padding:2px 4px}
.mhead b{display:block;font-size:16px;color:#141A21}.mhead span{font-size:14px;color:#657383}
.mrow{display:flex;flex-direction:column;justify-content:center;padding-left:4px}
.mrow b{font-size:18px;color:#141A21}.mrow span{font-size:14px;color:#657383;line-height:1.3}
.cost{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:14px 16px}
.cost strong{display:block;font-size:17px;color:#141A21;margin-bottom:2px}
.cost p{margin:0;font-size:15.5px;line-height:1.35;color:#4E5A68}
.cost p.lever{display:flex;align-items:center;gap:6px;margin-top:6px;color:#00718E;font-weight:500}
.fnote{margin:0;font-size:14px;color:#657383}
/* 3 Split mit Hook */
.slide.split{flex-direction:row;flex-wrap:wrap}
.split-l{position:relative;overflow:hidden;width:40%;height:calc(100% - 67px);background:#063659;color:#fff;padding:40px 48px 32px 56px;display:flex;flex-direction:column}
.split-l .ring{position:absolute;border-radius:50%;border:2px solid rgba(108,192,210,.2)}
.split-l .r1{width:420px;height:420px;right:-200px;top:-190px}
.split-l .r2{width:280px;height:280px;right:-120px;top:-110px;border-color:rgba(108,192,210,.12)}
.big-nr{font-family:'Geist Mono',monospace;font-size:96px;font-weight:600;line-height:.9;color:#6CC0D2;opacity:.5}
.split-l h2{font-size:38px;font-weight:600;letter-spacing:-.02em;line-height:1.1;margin:10px 0 0}
.hook{margin-top:auto;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:12px;padding:16px 18px}
.hook-top{display:flex;align-items:center;gap:10px;font-size:17px;font-weight:500;color:#6CC0D2;font-family:'Geist Mono',monospace}
.hook-lbl{display:block;font-size:14px;color:#9CC3E0;margin:12px 0 6px}
.hook-val{display:flex;align-items:baseline;gap:10px}
.hook-val>span:last-child{font-size:22px;color:#BBD7EA;font-weight:500}
.hook-exp{margin:10px 0 12px;font-size:17px;color:#BBD7EA}.hook-exp b{color:#fff}
.hook-then{display:flex;flex-direction:column;gap:8px}
.hook-then span{display:flex;align-items:center;gap:10px;font-size:15px;border-radius:8px;padding:8px 12px}
.hook-then .old{color:#BBD7EA;background:rgba(255,255,255,.05)}
.hook-then .new{color:#fff;background:#00718E;font-weight:500}
.split-r{flex:1;height:calc(100% - 67px);padding:36px 56px 14px 48px;display:flex;flex-direction:column;gap:8px}
.split-r .lq p{font-size:20px}
.flow{position:relative;display:flex;flex-direction:column;gap:4px;margin-top:6px}
.wire{position:absolute;left:19px;top:46px;bottom:26px;width:2px;background:#D2DAE2}
.grp{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#084878;margin:4px 0 2px 56px}
.grp.late{color:#00718E}
.grp span{text-transform:none;letter-spacing:0;font-weight:500;color:#657383;margin-left:6px}
.fstep{display:flex;gap:16px;align-items:center;position:relative;z-index:1;min-height:52px}
.fstep strong{font-size:17px;color:#141A21}.fstep strong .mono{color:#657383;margin-right:4px}
.fstep p{margin:1px 0 0;font-size:15px;line-height:1.3;color:#4E5A68}
.fcut{display:flex;align-items:center;gap:8px;margin:2px 0 2px 56px;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#657383;position:relative;z-index:1}
.fcut::after{content:"";flex:1;border-top:2px dashed #B4BFCB}
.story{display:flex;align-items:center;gap:8px;margin:auto 0 0;font-size:14px;color:#657383}
.split .ft{width:100%}
/* 4 Validierung */
.leftout{display:flex;align-items:center;gap:8px;flex-wrap:nowrap;background:#F7F9FB;border:1px solid #E4E9EF;border-radius:10px;padding:7px 14px;margin-bottom:12px}
.lo-k{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#657383;margin-right:4px}
.lo{font-size:14px;color:#4E5A68;background:#fff;border:1px solid #E4E9EF;border-radius:999px;padding:4px 11px;white-space:nowrap}
.lo b{color:#141A21;font-weight:600;margin-right:4px}
/* 6 Modell */
.two-charts{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.two-charts .chart-card{padding:12px 16px 6px}
.tiles{display:grid;grid-template-columns:1.05fr 1fr 1fr;gap:16px}
.tile{display:flex;gap:14px;align-items:center;background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:12px 16px}
.tile.dark{background:#063659;border-color:#04263F;flex-direction:column;align-items:flex-start;gap:8px}
.tile.dark p{margin:0;font-size:14.5px;line-height:1.35;color:#BBD7EA}.tile.dark .mono{color:#fff}
.tk{display:block;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#657383}
.tv{margin:3px 0 0;font-size:16px;color:#141A21;line-height:1.4}.tv b{color:#084878}
.ts{margin:3px 0 0;font-size:13.5px;color:#657383}
.top3{list-style:none;margin:4px 0 0;padding:0;font-size:15px}
.top3 li{display:flex;justify-content:space-between;gap:10px;color:#141A21;line-height:1.35}.top3 b{color:#00718E}
/* 7 Prüfhinweis */
.chain{position:relative;display:flex;flex-direction:column;gap:10px}
.chain-wire{position:absolute;left:34px;top:30px;height:246px;width:2px;background:#D2DAE2}
.clink{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:12px 16px;position:relative;z-index:1}
.clink .fexpr{font-size:18px}
.clink p{margin:5px 0 0;font-size:14.5px;line-height:1.35;color:#4E5A68}
.clink p b{color:#084878}
.stairs{display:flex;align-items:center;gap:6px;flex-wrap:nowrap;margin-top:2px}
.stairs span{font-size:14.5px;color:#4E5A68;background:#fff;border:1px solid #D2DAE2;border-radius:999px;padding:5px 12px;white-space:nowrap}
.stairs span.on{background:#A86505;border-color:#A86505;color:#fff;font-weight:600}
/* 8 Kalibrierung */
.cal-layout{display:grid;grid-template-columns:1fr 1.05fr;gap:22px;align-items:start}
.cal-steps{display:flex;flex-direction:column;gap:12px}
.cal-step{display:flex;gap:16px;align-items:flex-start;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:14px 18px;min-height:104px}
.cal-step strong{font-size:18px;color:#fff}.cal-step p{margin:6px 0 0;font-size:15.5px;line-height:1.4;color:#BBD7EA}
.dpanel{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:12px 18px}
.dnr{display:block;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#6CC0D2;margin-bottom:8px}
.dpanel ul{margin:0;padding-left:18px;color:#BBD7EA;font-size:15.5px;line-height:1.45}
.cal-stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:6px;border-top:1px solid rgba(255,255,255,.16);padding-top:8px}
.cal-stats b{display:block;font-family:'Geist Mono',monospace;font-size:20px;color:#fff}
.cal-stats span{font-size:14px;line-height:1.35;color:#9CC3E0}
/* 9 Band */
.band-layout{display:grid;grid-template-columns:520px 1fr;gap:22px;align-items:start}
.band-layout .chart-card{padding:12px 14px}
.hero{display:flex;gap:18px;align-items:center;background:#063659;border-radius:10px;padding:16px 20px}
.hero strong{display:block;font-size:18px;color:#fff}
.hero p{margin:4px 0 0;font-size:14.5px;line-height:1.4;color:#BBD7EA}
.wl-box{background:#F7F9FB;border:1px solid #D2DAE2;border-radius:10px;padding:12px 16px}
.wl-box p{margin:6px 0 0;font-size:14.5px;color:#4E5A68;line-height:1.4}
.flabel{display:block;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#00718E;margin-bottom:8px}
.wl-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.wl{border:1px solid #D2DAE2;border-radius:10px;padding:7px 12px;display:flex;flex-direction:column;min-width:0;background:#fff}
.wl-q{font-size:14px;color:#4E5A68;font-family:'Geist Mono',monospace}.wl-v{font-family:'Geist Mono',monospace;font-size:22px;font-weight:600}.wl-u{font-size:13.5px;color:#657383}
.wl.on{background:#063659;border-color:#04263F}.wl.on .wl-q,.wl.on .wl-u{color:#BBD7EA}.wl.on .wl-v{color:#fff}
.tradeoff{display:flex;justify-content:space-between;margin-top:8px;font-size:13.5px;color:#657383;border-top:1px dashed #B4BFCB;padding-top:6px}
/* 10 Fall */
.backref{display:flex;align-items:center;gap:10px;margin-bottom:6px;font-size:15px;color:#4E5A68}
.calc{background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:14px 20px;box-shadow:0 1px 2px rgba(4,38,63,.05)}
.calc-row{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:7px 0;border-bottom:1px solid #E4E9EF;font-size:16px;color:#4E5A68}
.calc-row b{font-family:'Geist Mono',monospace;font-weight:600;color:#141A21;white-space:nowrap}
.calc-row.sum{border-bottom:2px solid #084878}
.calc-res{display:flex;justify-content:space-between;align-items:center;padding-top:12px}
.calc-res>span:first-child{font-size:17px;font-weight:600;color:#141A21}
/* 11 Dashboard (dunkel) */
.dash-grid{display:grid;grid-template-columns:646px 1fr;gap:20px;align-items:start}
.dash-col{display:flex;flex-direction:column;gap:10px}
.shot-card{margin:0;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.16);border-radius:10px;overflow:hidden}
.shot-card figcaption{display:flex;align-items:center;gap:10px;padding:5px 12px;font-size:14.5px;font-weight:600;color:#fff}
.shot-wrap{position:relative;line-height:0;background:#fff}
.shot{display:block;width:100%;height:auto}
.shot.missing{display:grid;place-items:center;min-height:200px;color:#B3261E;font-weight:600;line-height:1.4}
.hl{position:absolute;border:3px solid #0080A0;border-radius:6px;box-shadow:0 0 0 4px rgba(0,128,160,.18);line-height:1.2}
.hl em{position:absolute;right:-3px;top:-24px;background:#00718E;color:#fff;font-style:normal;font-size:13px;font-weight:600;padding:3px 8px;border-radius:5px 5px 0 5px;white-space:nowrap}
.hl.left em{right:auto;left:-3px;border-radius:5px 5px 5px 0}
.learn{display:flex;align-items:center;gap:12px;margin:10px 72px 0;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:8px 14px;position:relative;z-index:1}
.learn .rule{font-size:14.5px;color:#BBD7EA;white-space:nowrap}
.learn .rule code{background:rgba(255,255,255,.12);color:#fff;font-size:13.5px}
.learn .rule b{color:#fff}
.lstep{display:inline-flex;align-items:center;gap:8px;font-size:14.5px;color:#fff;white-space:nowrap}
.lstep::before{content:"→";color:#6CC0D2;margin-right:2px}
.closing{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:8px 72px 12px;position:relative;z-index:1}
.closing p{display:flex;align-items:center;gap:10px;margin:0;font-size:17px;font-weight:500;color:#fff}
.handover{display:inline-flex;align-items:center;gap:8px;background:#6CC0D2;color:#04263F;font-weight:600;font-size:15px;border-radius:999px;padding:7px 16px;white-space:nowrap}
/* Backup: Canvas Wortlaut */
.a1-layout{display:grid;grid-template-columns:1fr 268px;gap:18px;align-items:start;padding-bottom:12px}
.a1-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.a1{display:flex;gap:10px;align-items:flex-start;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:10px;padding:7px 12px;min-height:84px}
.a1.ml{border-color:#6CC0D2}
.a1-k{display:block;font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#E4EFF7}
.a1-k b{font-family:'Geist Mono',monospace;color:#6CC0D2;margin-right:4px}
.a1 p{margin:2px 0 0;font-size:14px;line-height:1.32;color:#BBD7EA}
.coh{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:16px 18px}
.coh .dnr{margin:10px 0 10px}
.coh ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:14px}
.coh li b{display:block;color:#6CC0D2;font-size:15px}.coh li span{font-size:15px;color:#E4EFF7;line-height:1.4}
/* Backup: Grenzen */
.four-dark{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;align-items:stretch}
.dcard{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:18px;display:flex;flex-direction:column;gap:8px}
.dcard .dnr{margin:6px 0 0}
.dcard h4{font-size:19px;margin:0;color:#fff;font-weight:600;line-height:1.25}
.dcard ul{margin:4px 0 0;padding-left:18px;color:#BBD7EA;font-size:15px;line-height:1.45}.dcard li{margin:4px 0}
/* Tabelle */
.tbl{width:100%;border-collapse:collapse;font-size:16px;background:#fff;border:1px solid #D2DAE2;border-radius:10px;overflow:hidden}
.tbl th{background:#04263F;color:#fff;font-weight:500;text-align:left;padding:10px 12px;font-size:14.5px}
.tbl td{padding:9px 12px;border-bottom:1px solid #E4E9EF}
.tbl .num{text-align:right;font-family:'Geist Mono',monospace}
.tbl tr.best td{background:#E3F3F7;font-weight:600;color:#005E77}
/* Notizen und Präsentiermodus */
.notes{display:none}
body.show-notes .notes{display:block;width:1280px;background:#fff;border-radius:10px;padding:18px 24px;font-size:15px;line-height:1.5;color:#141A21}
.notes h5{margin:0 0 6px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#00718E}
.notes ul{margin:0 0 10px;padding-left:20px}
.hud{position:fixed;right:16px;top:14px;z-index:9;display:none;gap:10px;align-items:center;font:500 14px 'IBM Plex Sans',sans-serif;color:#BBD7EA;background:rgba(4,38,63,.9);border-radius:999px;padding:6px 14px}
.hud b{font-family:'Geist Mono',monospace;color:#fff}
html.present-mode{background:#04263F}
body.present{overflow:hidden;background:#04263F}
body.present .deck{display:block;padding:0}
body.present .slide,body.present .notes,body.present .deck-intro,body.present .backup-sep{display:none}
body.present .slide.cur{display:flex;position:fixed;left:50%;top:50%;transform-origin:center;transform:translate(-50%,-50%) scale(var(--s,1))}
body.present.show-hud .hud{display:flex}
body.present.show-notes .notes.cur{display:block;position:fixed;left:0;right:0;bottom:0;width:auto;max-height:45vh;overflow:auto;z-index:8;border-radius:0;box-shadow:0 -8px 24px rgba(0,0,0,.3)}
body.present.show-notes .notes.cur h5:not(:first-child),body.present.show-notes .notes.cur h5:not(:first-child)+ul{display:none}
.deck-intro{width:1280px;color:#BBD7EA;font-size:15px;line-height:24px}
.deck-intro b{color:#fff}
.backup-sep{width:1280px;color:#6CC0D2;font-size:14px;line-height:20px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;border-top:1px dashed #4E5A68;padding-top:14px}
@page{size:1280px 720px;margin:0}
@media print{
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body,body.present{background:#fff}
.deck,body.present .deck{display:flex;gap:0;padding:0}
.slide,body.present .slide{display:flex!important;position:relative!important;left:auto;top:auto;transform:none!important;page-break-after:always;break-after:page}
.deck-intro,.backup-sep,.notes,.hud{display:none!important}
}
"""

JS = """
(()=>{
 const slides=[...document.querySelectorAll('.slide')];
 const notes=[...document.querySelectorAll('.notes')];
 const hud=document.querySelector('.hud');
 const plan=slides.map(s=>parseFloat(s.dataset.minutes||'0'));
 const labels=slides.map(s=>s.dataset.num||'');
 let i=0,t0=null,timer=null;
 const on=()=>document.body.classList.contains('present');
 const fit=()=>document.documentElement.style.setProperty('--s',Math.min(innerWidth/1280,innerHeight/720));
 const fmt=s=>`${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`;
 const target=()=>plan.slice(0,i+1).reduce((a,b)=>a+b,0)*60;
 function mark(){history.replaceState(null,'',on()?'#present-'+(i+1):location.pathname+location.search);}
 function show(n){i=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,k)=>s.classList.toggle('cur',k===i));notes.forEach((s,k)=>s.classList.toggle('cur',k===i));tick();mark();}
 function tick(){if(!hud)return;const el=t0?(Date.now()-t0)/1000:0;hud.innerHTML=`Folie <b>${labels[i]}</b> · Zeit <b>${fmt(el)}</b> · Soll <b>${fmt(target())}</b>`;}
 function nearest(){let best=0,dist=1e9;slides.forEach((s,k)=>{const d=Math.abs(s.getBoundingClientRect().top);if(d<dist){dist=d;best=k;}});return best;}
 function present(v){if(v&&!on())i=nearest();document.body.classList.toggle('present',v);document.documentElement.classList.toggle('present-mode',v);if(v){fit();show(i);if(!t0)t0=Date.now();timer=timer||setInterval(tick,1000);}else{mark();slides[i].scrollIntoView();}}
 addEventListener('resize',fit);
 addEventListener('beforeprint',()=>{if(on())present(false);});
 addEventListener('keydown',e=>{
  if(e.ctrlKey||e.metaKey||e.altKey)return;
  const k=e.key.toLowerCase();
  if(k==='p'){present(!on());}
  else if(k==='n'){document.body.classList.toggle('show-notes');}
  else if(k==='h'){document.body.classList.toggle('show-hud');}
  else if(k==='r'){t0=Date.now();tick();}
  else if(!on())return;
  else if(['arrowright','pagedown',' '].includes(k)){e.preventDefault();show(i+1);}
  else if(['arrowleft','pageup'].includes(k)){e.preventDefault();show(i-1);}
  else if(k==='escape'){present(false);}
 });
 const m=location.hash.match(/^#present(?:-(\\d+))?$/);
 if(m){i=Math.max(0,(+m[1]||1)-1);present(true);}
})();
"""




APPENDIX = (
    '<section class="n app"><h2>Anhang · Canvas in drei Sätzen</h2><p>SWW plant die Beschaffung per Fortschreibung '
    "und sieht Auffälligkeiten oft erst im Quartal. Wir sagen je Zähler den Folgemonat per Regression voraus und "
    "vergleichen nach Monatsende mit dem Istwert. Die Prognose geht an die Beschaffung, große Abweichungen gehen als "
    "Prüfhinweis an das Netzmanagement; entscheiden tut ein Mensch.</p></section>"
    '<section class="n app"><h2>Anhang · Canvas verteidigen, ein Satz je Feld</h2><dl>'
    "<dt>01 Mehrwert</dt><dd>Der Auftrag nennt zwei Probleme, Spotmarkt-Ausgleich und Auffälligkeiten erst im Quartal, daher zwei Nutzen.</dd>"
    "<dt>02 Datenquellen</dt><dd>16.830 Monatswerte von 700 Zählern (Jan 2024 bis Dez 2025) als CSV, ohne Live-Quelle; deshalb ein monatlicher Takt.</dd>"
    "<dt>03 Vorhersage</dt><dd>Regression, weil der Verbrauch kontinuierlich ist; intern VLS, bewertet in kWh.</dd>"
    "<dt>04 Merkmale</dt><dd>Nur Vorab-Wissen: Vorjahr fehlt für 2024, Temperatur ist fast gleich den Heizgradtagen, die Anomalie-Spalte ist kein bestätigtes Label, die Vertragsleistung steckt in der Normierung.</dd>"
    "<dt>05 Lernansatz</dt><dd>Überwacht, weil der Istverbrauch bekannt ist. Der Random Forest gewinnt die zeitliche Validierung knapp, die lineare Regression bleibt erklärbare Referenz.</dd>"
    "<dt>06 Evaluation</dt><dd>RMSE in kWh, weil große Fehler am Spotmarkt teuer sind und kWh die Planungseinheit ist. Precision@K kommt, sobald Bewertungen vorliegen.</dd>"
    "<dt>07 Entscheidung</dt><dd>Ab |Faktor| ≥ 1 prüft das Netzmanagement; das Modell priorisiert, es entscheidet nicht.</dd>"
    "<dt>08 Impact</dt><dd>Belegt sind −15,9 % RMSE und 9,5 Fälle pro Monat. Euro nicht, weil Preise und Prüfkosten fehlen.</dd>"
    "<dt>09 Zeitpunkt</dt><dd>Vor Monatsbeginn, weil die Beschaffung dann plant; nach Monatsende, weil erst dann der Istwert vorliegt.</dd>"
    "<dt>10 Monitoring</dt><dd>Monatlich, weil die Daten monatlich kommen; neu trainiert wird nur bei belegter Verschlechterung.</dd>"
    "</dl></section>"
    '<section class="n app"><h2>Anhang · Weitere Rückfragen</h2><dl>'
    "<dt>Welche Metrik passt nicht?</dt><dd>Accuracy, ROC-AUC und Recall brauchen Klassen und Labels. R² ist keine Trefferquote.</dd>"
    "<dt>Warum weicht der Canvas vom Vorschlag im Auftrag ab?</dt><dd>VLS statt kWh (−6,2 % RMSE); Vertragsleistung nur zur Umrechnung; Vorjahreswert gibt es für 2024 nicht; Temperatur ist redundant zu den Heizgradtagen; Monitoring monatlich, Retraining nur bei Evidenz.</dd>"
    "<dt>Wie haben Sie KI eingesetzt?</dt><dd><b>Selbst und ehrlich ausfüllen.</b> Beispielrahmen: KI hat bei Code-Struktur, Folienlayout und sprachlicher Glättung geholfen; Analyseentscheidungen und alle Zahlen stammen aus unseren Notebooks, und ich kann jede Aussage selbst erklären.</dd>"
    "</dl></section>"
)

def _notes_html(slide: Slide) -> str:
    parts = []
    if slide.keywords:
        parts.append("<h5>Stichworte</h5><ul class=\"kw\">" + "".join(f"<li>{k}</li>" for k in slide.keywords) + "</ul>")
    if slide.speech:
        parts.append("<h5>Sprechtext</h5><ul>" + "".join(f"<li>{s}</li>" for s in slide.speech) + "</ul>")
    if slide.reading:
        parts.append("<h5>So liest du die Folie</h5><ul>" + "".join(f"<li>{s}</li>" for s in slide.reading) + "</ul>")
    if slide.questions:
        parts.append("<h5>Falls gefragt wird</h5><ul>" + "".join(
            f"<li><b>{q}</b> {a}</li>" for q, a in slide.questions) + "</ul>")
    return "".join(parts)


def _small_logo(height: int = 64) -> bytes:
    """Wortmarke auf doppelte Anzeigehöhe (2 × 26 px) verkleinern; sie steht auf jeder Folie."""
    import io

    from PIL import Image

    image = Image.open(LOGO)
    width = round(image.width * height / image.height)
    buffer = io.BytesIO()
    image.resize((width, height), Image.LANCZOS).save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def slide_numbers(slides: list[Slide]) -> list[str]:
    """Hauptfolien als 'n / Anzahl', Backups als 'B1' …"""
    main_total = sum(1 for s in slides if not s.backup)
    labels, main, backup = [], 0, 0
    for slide in slides:
        if slide.backup:
            backup += 1
            labels.append(f"B{backup}")
        else:
            main += 1
            labels.append(f"{main} / {main_total}")
    return labels


def words_per_minute(slide: Slide) -> float:
    words = sum(len(re.sub(r"<[^>]+>|\[Pause\]", " ", s).split()) for s in slide.speech)
    return words / slide.minutes if slide.minutes else 0.0


def render_deck(slides: list[Slide]) -> str:
    logo = "data:image/png;base64," + base64.b64encode(_small_logo()).decode()
    main_minutes = sum(s.minutes for s in slides if not s.backup)
    parts = [
        '<div class="deck-intro"><b>Kikos Teil</b> · ML Canvas, Methodik und Modell, Prüffall · '
        f"Sprechzeit ≈ {de(main_minutes, 0)} min. Tasten: <b>P</b> Präsentieren · <b>N</b> Sprechtext · "
        "<b>H</b> Zeitanzeige · <b>R</b> Timer zurücksetzen · <b>← →</b> blättern · <b>Esc</b> beenden.</div>"
    ]
    backup_started = False
    for slide, num in zip(slides, slide_numbers(slides)):
        if slide.backup and not backup_started:
            parts.append('<div class="backup-sep">Backup · nur bei Rückfragen</div>')
            backup_started = True
        body = slide.html.replace("{NUM}", num).replace("{LOGO}", logo)
        body = body.replace(
            '<section class="slide', f'<section data-minutes="{slide.minutes:.4f}" data-num="{num}" class="slide', 1
        )
        parts.append(body)
        parts.append(f'<aside class="notes">{_notes_html(slide)}</aside>')
    return (
        "<!DOCTYPE html>\n<html lang=\"de\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>ML Canvas, Methodik, Prüffall</title>\n"
        f"<style>{_font_face()}{CSS}</style>\n</head>\n<body>\n<div class=\"deck\">\n"
        + "\n".join(parts)
        + f"\n</div>\n<div class=\"hud\"></div>\n<script>{JS}</script>\n</body>\n</html>\n"
    )


def render_notes(slides: list[Slide]) -> str:
    rows = []
    cumulative = 0.0
    for slide, num in zip(slides, slide_numbers(slides)):
        if slide.backup:
            time = "Backup"
        else:
            cumulative += slide.minutes
            seconds = round(cumulative * 60)
            time = f"{round(slide.minutes * 60)} s · bis {seconds // 60}:{seconds % 60:02d}"
        rows.append(
            f'<section class="n"><div class="nh"><span class="nn">{num.split(" /")[0]}</span><h2>{esc(slide.title)}</h2>'
            f'<span class="nt">{time}</span></div>{_notes_html(slide)}</section>'
        )
    total = sum(s.minutes for s in slides if not s.backup)
    return (
        "<!DOCTYPE html>\n<html lang=\"de\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>Sprechzettel Kiko</title><style>"
        + _font_face()
        + """
body{margin:0;background:#F1F4F7;font-family:'IBM Plex Sans',sans-serif;color:#141A21}
main{max-width:860px;margin:0 auto;padding:32px 20px 60px}
h1{font-size:30px;margin:0 0 6px;color:#063659}.lead{color:#4E5A68;margin:0 0 24px;line-height:1.5}
.n{background:#fff;border:1px solid #D2DAE2;border-radius:10px;padding:18px 22px;margin:0 0 16px;break-inside:avoid}
.nh{display:flex;align-items:baseline;gap:12px;margin-bottom:10px}
.nn{font-family:'Geist Mono',monospace;font-weight:600;color:#00718E}
.nh h2{font-size:19px;margin:0;flex:1;color:#084878}.nt{font-family:'Geist Mono',monospace;font-size:13px;color:#657383;white-space:nowrap}
h5{margin:10px 0 4px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#00718E}
ul{margin:0;padding-left:20px;line-height:1.55;font-size:15.5px}li{margin:3px 0}
ul.kw{display:flex;flex-wrap:wrap;gap:6px;list-style:none;padding:0}ul.kw li{background:#E3F3F7;color:#005E77;border-radius:999px;padding:2px 10px;font-size:14px;margin:0}
.app h2{font-size:19px;margin:0 0 8px;color:#084878}.app dl{margin:0}.app dt{font-weight:600;margin-top:8px}.app dd{margin:2px 0 0 0;color:#4E5A68;line-height:1.5}
@media print{*{-webkit-print-color-adjust:exact;print-color-adjust:exact}body{background:#fff}.n{border-color:#B4BFCB}}
</style></head><body><main>"""
        + f"<h1>Sprechzettel · Kikos Teil</h1><p class=\"lead\">ML Canvas, Methodik und Modell, Prüffall. "
        f"Geplante Sprechzeit {de(total * 60, 0)} s ({de(total, 1)} min) plus Puffer für die Übergaben. Zahlen wie im "
        "Bericht bzw. Notebook 13. [Pause] heißt: eine Sekunde Stille nach der Zahl. Stichworte sind Stützen, "
        "nicht zum Ablesen.</p>"
        + "".join(rows)
        + APPENDIX
        + "</main></body></html>\n"
    )


def main() -> None:
    nb = Notebook.load()
    facts = extract_facts(nb)
    slides = build_slides(facts)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DECK.write_text(render_deck(slides), encoding="utf-8")
    NOTES.write_text(render_notes(slides), encoding="utf-8")
    main_slides = [s for s in slides if not s.backup]
    print(f"{DECK.relative_to(ROOT)}: {len(main_slides)} Hauptfolien + {len(slides) - len(main_slides)} Backup, "
          f"Sprechzeit {sum(s.minutes for s in main_slides):.2f} min")
    for slide in main_slides:
        print(f"  {slide.label:<28} {slide.minutes * 60:4.0f} s  {words_per_minute(slide):5.0f} Wörter/min")
    print(f"{NOTES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
