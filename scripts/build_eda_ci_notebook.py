"""Create a separate SWW edition of Patrick's EDA; never modify the original."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re

import nbformat

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ipynb/eda.ipynb"
DESTINATION = ROOT / "ipynb/eda_ci.ipynb"

SETUP = """from pathlib import Path
from datetime import datetime, timezone
from importlib.util import find_spec
import sys

# Prüfen, bevor der erste Drittanbieter-Import einen unklaren Fehler auslöst.
benoetigte_pakete = ("numpy", "pandas", "plotly", "IPython", "energy_analytics", "scipy", "jinja2")
fehlende_pakete = [name for name in benoetigte_pakete if find_spec(name) is None]
if fehlende_pakete:
    raise RuntimeError(
        f"Im aktuellen Notebook-Kernel fehlen: {', '.join(fehlende_pakete)}. "
        f"Aktiver Interpreter: {sys.executable}. "
        "Bitte oben rechts den Kernel 'Python (SWW .venv)' oder die Projekt-.venv "
        "auswählen, den Kernel neu starten und alle Zellen ausführen. "
        "Falls die Projektumgebung noch fehlt: im Projektstamm "
        "`python -m uv sync --frozen --all-extras` ausführen."
    )

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display

try:
    from energy_analytics.visualization import eda, theme
    from energy_analytics.visualization import notebook as ci
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Bitte im Projektstamm `python -m uv sync --frozen --all-extras` ausführen "
        "und anschließend die Projektumgebung .venv als Notebook-Kernel auswählen."
    ) from exc

BASE_DIR = next(
    (folder for folder in (Path.cwd(), *Path.cwd().parents)
     if (folder / "pyproject.toml").is_file() and (folder / "brand/design-system").is_dir()),
    None,
)
if BASE_DIR is None:
    raise FileNotFoundError("Bitte das Notebook innerhalb des Projektordners starten.")

ci.aktiviere()
# Ausschließlich die vorhandene Datei lesen; keine Bereinigung auf Datenträger schreiben.
"""

INTRO = """# Explorative Datenanalyse · SWW Corporate Identity

Eigenständige Designfassung von Patricks [eda.ipynb](eda.ipynb). Die sechs Analyseabschnitte,
Berechnungen und Befundtexte bleiben als inhaltliche Grundlage erhalten. Die Diagramme
verwenden ausschließlich die zentrale SWW-Farbpalette, IBM Plex Sans und die Bausteine aus
`energy_analytics.visualization` — ohne Import von `viz.py`.

**Datenbasis:** `data/raw/verbrauch_bereinigt.csv`, 700 Zähler über 2024–2025.
Es werden die vorhandenen Projektdaten analysiert, keine Demo- oder Zufallsdaten erzeugt.

| Abschnitt | Inhalt |
| --- | --- |
| 1. Überblick | Spalten, Rollen, Füllgrad und Plausibilität |
| 2. Univariate Analyse | Verteilung jeder Variable |
| 3. Zähler | Unterschiede zwischen und innerhalb der Zähler |
| 4. Kundentyp | Niveau, Normierung und Saison |
| 5. Bivariate Analyse | Zusammenhänge und mögliche Treiber |
| 6. Fehlwerte | Zeitliche Muster und Modellierungsfolgen |
| Fazit | Aus dem Original übernommene Modellierungsempfehlungen |
"""

USAGE = """## Ausführung und Gestaltungsregeln

1. Im Projektstamm einmal `python -m uv sync --frozen --all-extras` ausführen.
2. Den Kernel **Python (SWW .venv)** oder die Projektumgebung `.venv` auswählen und **Alle ausführen** starten.
3. Die gespeicherten Ausgaben zeigen den zuletzt geprüften Stand. Bei Änderungen an den
   Design-Tokens erst `python scripts/build_tokens.py` ausführen, dann den Kernel neu starten.

Gewerbe bleibt Teal, Industrie Navy und Kommunal Grün. Messwerte ohne Kundengruppierung
verwenden Navy; Cyan bleibt Prognosen vorbehalten. Schwellen sind Amber und gepunktet.
Zahlen verwenden Dezimalkomma und Tausenderpunkt, jedes Diagramm nennt den Bezugszeitraum.
Die [Brand-Galerie](../brand/design-system/templates/eda-charts/index.html) ist die Referenz.
Die interaktiven Diagramme nutzen den Plotly-Renderer von JupyterLab oder VS Code.
Schriften werden lokal eingebettet; die Analyse lädt keine Ressourcen von einem CDN.
Die geprüfte Fassung enthält zusätzlich PNG-Vorschauen für Betrachter ohne Plotly-Unterstützung.
Nach erneuter Ausführung können diese mit den Prüfschritten in [README.md](README.md)
aktualisiert werden. Eine eigenständige Offline-HTML-Vorschau entsteht dabei ebenfalls.

**Inhaltliche Abgrenzung:** Dies ist eine Designübertragung, keine neue fachliche Freigabe.
Sentinel-Rekonstruktion, Filterung und Befunde stammen aus Patricks Notebook. Insbesondere die
Interpretation der Vertragsleistung als harte physikalische Obergrenze muss fachlich geprüft
werden. Die Rekonstruktion aus einer Folgezeile ist rückblickende EDA und darf nicht ungeprüft
in eine Prognose-Pipeline übernommen werden. Keine Quelldatei wird überschrieben.
"""


def transform(index, source):
    source = source.replace("viz.", "ci.")
    source = source.replace('"#ffffff"', 'theme.TOKENS["text-inverse"]')
    source = source.replace("fig.show()", "ci.zeigen(fig)")
    # Old per-figure header offsets are replaced by the shared, caption-aware layout.
    source = re.sub(r", (?:margin_t|legend_y)=[0-9.]+", "", source)
    source = source.replace("ci.DIVERGIEREND[::-1]", "ci.DIVERGIEREND")
    if index == 1:
        source = SETUP + source[source.index("DATA_DIR =") :]
        source += """

ci.titelkarte(
    "Explorative Datenanalyse",
    "SWW-Designfassung von Patricks Analyse · Datenbasis: data/raw/verbrauch_bereinigt.csv",
    f"{len(df):,} Monatswerte · {df['zaehler_id'].nunique()} Zähler · {ci.ZEITRAUM} · "
    f"Ausgeführt: {datetime.now(timezone.utc):%d.%m.%Y %H:%M} UTC".replace(",", "."),
    logo=BASE_DIR / "brand/design-system/assets/logo-sww-wordmark.png",
)
"""
    elif index == 4:
        source = source.replace(
            'fehl["spalte"] = fehl["spalte"].map(ci.label_umbruch)',
            "# Lange Spaltennamen werden einmal im SWW-Baustein umgebrochen.",
        )
        source = source.replace(
            'fig = px.bar(fehl, x="fehlend %", y="spalte", text="fehlend",\n'
            "             color_discrete_sequence=[ci.SERIE[0]])",
            'fig = eda.missing_values(fehl["spalte"].tolist()[::-1], '
            'fehl["fehlend %"].tolist()[::-1])\n'
            'fig.update_traces(text=fehl["fehlend"].tolist())',
        )
    elif index == 9:
        source = source.replace(
            'fig = px.histogram(df, x="auslastung_prozent", nbins=150,\n'
            "                   color_discrete_sequence=[ci.SERIE[0]])",
            'fig = eda.histogram({"Monatswerte": df["auslastung_prozent"]}, nbins=150)',
        )
    elif index == 18:
        end = source.index("ci.stil(")
        source = (
            'fig = eda.histogram(eda.by_kundentyp(zaehler, "vertragsleistung_kw"), '
            'nbins=40, log_x=True)\nfig.update_layout(barmode="stack")\n' + source[end:]
        )
    elif index == 27:
        source = source.replace(
            'fig = px.histogram(df, x="produktionsplan_index", nbins=50,\n'
            "                   color_discrete_sequence=[ci.SERIE[0]])",
            'fig = eda.histogram({"Monatswerte": df["produktionsplan_index"]}, nbins=50)',
        )
    elif index == 31:
        source = source.replace(
            "fig = px.histogram(abw[innen], nbins=100, color_discrete_sequence=[ci.SERIE[0]])",
            'fig = eda.histogram({"Monatswerte": abw[innen]}, nbins=100)',
        )
    elif index == 36:
        end = source.index("ci.stil(")
        source = (
            'fig = eda.histogram(eda.by_kundentyp(zaehler, "mittel_kwh"), '
            "nbins=50, log_x=True)\n" + source[end:]
        )
    elif index == 38:
        end = source.index("ci.stil(")
        source = (
            'fig = eda.boxplot({typ: gruppe["variationskoeffizient"] * 100 '
            'for typ, gruppe in zaehler.groupby("kundentyp", observed=True)})\n' + source[end:]
        )
    elif index == 39:
        source = source.replace(
            "ci.log_achse(fig, dtick=1, row=1, col=1)",
            "ci.log_achse(fig, dtick=1, row=1, col=1)\n"
            'fig.update_yaxes(title_text="Verbrauch (kWh, log)", row=1, col=1)\n'
            'fig.update_yaxes(title_text="Faktor zum Zählermittel", row=1, col=2)',
        )
    elif index == 44:
        source = source.replace(
            'fig = px.line(zeitreihe, x="monat", y="gwh", color="kundentyp", markers=True, **TYP_STIL)',
            'verlauf = zeitreihe.pivot(index="monat", columns="kundentyp", values="gwh")\n'
            "fig = eda.seasonality(verlauf.index, {typ: verlauf[typ] for typ in TYPEN})",
        )
    elif index == 50:
        source = source.replace(
            'fig = px.imshow(kmat.mask(maske), text_auto=".2f", aspect="auto", zmin=-1, zmax=1,\n'
            "                color_continuous_scale=ci.DIVERGIEREND)",
            "matrix_anzeige = kmat.mask(maske).copy()\n"
            "matrix_anzeige.columns = [ci.label_umbruch(name) for name in matrix_anzeige.columns]\n"
            "fig = eda.correlation(matrix_anzeige)\n"
            'fig.update_traces(text=[["" if pd.isna(wert) else de(wert, 2) '
            "for wert in zeile] for zeile in matrix_anzeige.to_numpy()])",
        )
        source = source.replace(
            'height=640, coloraxis_colorbar_title_text="ρ"',
            "height=780, margin_l=245, margin_b=180",
        )
        source = source.replace(
            "ci.zeigen(fig)", 'fig.update_traces(colorbar_title_text="ρ")\nci.zeigen(fig)'
        )
    elif index == 73:
        source = source.replace("markers=True)", "markers=True, color_discrete_sequence=ci.SERIE)")
    return source


def build(destination=DESTINATION):
    original = nbformat.read(SOURCE, as_version=4)
    if len(original.cells) != 77 or "import viz" not in original.cells[1].source:
        raise ValueError("Patricks Notebook hat sich strukturell geändert; Zuordnung neu prüfen.")
    notebook = nbformat.v4.new_notebook()
    notebook.metadata = {
        "kernelspec": {
            "display_name": "Python (SWW .venv)",
            "language": "python",
            "name": "sww-energy-analytics",
        },
        "language_info": {"name": "python"},
        "sww": {
            "source": "ipynb/eda.ipynb",
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "design_source": "brand/design-system/tokens/design-tokens.json",
        },
    }
    notebook.cells = [
        nbformat.v4.new_markdown_cell(INTRO, id="sww-introduction"),
        nbformat.v4.new_markdown_cell(USAGE, id="sww-usage"),
    ]
    for index, cell in enumerate(original.cells[1:], start=1):
        source = transform(index, cell.source) if cell.cell_type == "code" else cell.source
        if cell.cell_type == "markdown":
            source = source.replace("`cleaning.ipynb`", "dem Datenbereinigungs-Notebook")
        factory = (
            nbformat.v4.new_code_cell if cell.cell_type == "code" else nbformat.v4.new_markdown_cell
        )
        new_cell = factory(source, id=f"sww-original-{index:02d}")
        new_cell.metadata["sww_original_cell"] = index
        notebook.cells.append(new_cell)
    nbformat.validate(notebook)
    nbformat.write(notebook, destination)
    print(f"Created {destination.relative_to(ROOT)} ({len(notebook.cells)} cells).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="Overwrite the generated CI edition only"
    )
    args = parser.parse_args()
    if DESTINATION.exists() and not args.force:
        parser.error("eda_ci.ipynb exists; use --force only to intentionally regenerate it")
    build()
