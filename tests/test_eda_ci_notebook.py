"""Regressions for the saved SWW EDA and its per-figure presentation."""

import base64
import json
from pathlib import Path
import runpy
import subprocess
import sys

import nbformat
import pandas as pd
import plotly.io as pio
from plotly.subplots import make_subplots

from energy_analytics.visualization import eda, theme
from energy_analytics.visualization import notebook as ci

ROOT = Path(__file__).resolve().parents[1]


def test_saved_notebook_preserves_source_and_has_all_executed_charts():
    notebook = nbformat.read(ROOT / "ipynb/eda_ci.ipynb", as_version=4)
    nbformat.validate(notebook)
    # Editors save local kernel names (e.g. python3 or sww-energy-analytics).
    # Those names do not identify the interpreter or its installed packages.
    assert notebook.metadata.kernelspec.language == "python"
    assert notebook.metadata.language_info.name == "python"
    # Provenance is a snapshot, not a dependency on future edits to Patrick's original.
    assert notebook.metadata.sww.source == "ipynb/eda.ipynb"
    assert len(notebook.metadata.sww.source_sha256) == 64
    int(notebook.metadata.sww.source_sha256, 16)
    # Additional notes/empty Markdown cells are valid notebook edits.
    imported_cells = [c for c in notebook.cells if "sww_original_cell" in c.metadata]
    assert [c.metadata.sww_original_cell for c in imported_cells] == list(range(1, 77))
    code = [c for c in notebook.cells if c.cell_type == "code"]
    assert len(code) == 38
    assert all(c.execution_count is not None for c in code)
    assert not any("import viz" in c.source or "viz." in c.source for c in code)
    plots = []
    logo = ci._logo_uri(ROOT / "brand/design-system/assets/logo-sww-emblem.png")
    for cell in code:
        for output in cell.outputs:
            assert output.output_type != "error"
            data = output.get("data", {})
            figure = data.get("application/vnd.plotly.v1+json")
            if figure:
                # Re-running in Jupyter replaces outputs with Plotly MIME data.
                # The browser export adds optional PNG previews for static viewers.
                if "image/png" in data:
                    assert base64.b64decode(data["image/png"], validate=True).startswith(
                        b"\x89PNG\r\n\x1a\n"
                    )
                layout = figure["layout"]
                assert layout["font"]["family"] == theme.FONT
                assert layout["paper_bgcolor"] == theme.TOKENS["chart-paper-bg"]
                assert layout["colorway"] == theme.QUALITATIVE
                assert layout["meta"]["sww"]["period"] == "01/2024–12/2025"
                assert layout["meta"]["sww"]["chapter"] in {"01", "02", "03", "04", "05", "06"}
                assert layout["meta"]["sww"]["source"] == "verbrauch_bereinigt.csv"
                marks = [item for item in layout["images"] if item["name"] == "sww-brand-logo"]
                assert len(marks) == 1
                assert marks[0]["source"] == logo
                assert marks[0]["sizing"] == "contain"
                assert marks[0]["y"] < 0  # Logo is outside the data area.
                assert marks[0]["sizex"] == 0.10
                plot_height = layout["height"] - layout["margin"]["t"] - layout["margin"]["b"]
                assert abs(marks[0]["sizey"] * plot_height - 36) < 1e-8
                for trace in figure["data"]:
                    if trace.get("name") in theme.KUNDENTYP_COLORS:
                        color = trace.get("marker", {}).get("color") or trace.get("line", {}).get(
                            "color"
                        )
                        assert color == theme.KUNDENTYP_COLORS[trace["name"]]
                plots.append(figure)
    assert len(plots) == 32
    html = [o.get("data", {}).get("text/html", "") for c in code for o in c.outputs]
    assert sum('class="sww-report sww-cover"' in output for output in html) == 1
    assert sum('class="sww-report sww-chapter"' in output for output in html) == 6


def test_notebook_histogram_keeps_decimal_ticks_and_actual_colour():
    previous = pio.templates.default
    try:
        pio.templates.default = "plotly_dark"
        fig = eda.histogram({"Monatswerte": [0.6, 0.8, 1.2]})
        ci.stil(fig, "Index")
        ci.vorbereiten(fig)
        assert fig.layout.xaxis.tickformat == ",~g"
        assert fig.layout.template.layout.paper_bgcolor == theme.TOKENS["chart-paper-bg"]
        assert fig.data[0].opacity == 1
        assert pio.templates.default == "plotly_dark"
    finally:
        pio.templates.default = previous


def test_notebook_date_range_and_panel_legend_are_deterministic():
    dates = pd.date_range("2024-01-01", periods=24, freq="MS")
    fig = eda.seasonality(dates, {"Gewerbe": [1] * 24, "Industrie": [2] * 24})
    ci.stil(fig, "Verbrauch", y_titel="Verbrauch (GWh)")
    assert fig.layout.xaxis.tickformat == "%m/%Y"
    assert str(fig.layout.xaxis.range[1]).startswith("2025-12-08")
    panels = make_subplots(rows=2, cols=1, subplot_titles=["Roh", "Normiert"])
    for row in [1, 2]:
        panels.add_scatter(x=[1, 2], y=[1, 2], row=row, col=1)
    ci.stil(panels, "Zähler", "Langer Untertitel " * 10)
    panels.update_layout(height=840)
    ci.vorbereiten(panels)
    plot_height = panels.layout.height - panels.layout.margin.t - panels.layout.margin.b
    assert abs((panels.layout.legend.y - 1) * plot_height - 30) < 1e-8


def test_notebook_brand_footer_is_idempotent_and_preserves_analytical_objects(monkeypatch):
    monkeypatch.setattr(ci, "_LOGO", ci._logo_uri(
        ROOT / "brand/design-system/assets/logo-sww-emblem.png"
    ))
    monkeypatch.setattr(ci, "QUELLE", "Messwerte <intern>.csv")
    fig = eda.histogram({"Monatswerte": [0.6, 0.8, 1.2]})
    ci.stil(fig, "Verbrauch", "Quelle und Referenzlinien müssen erhalten bleiben.")
    ci.schwellwert(fig, 1, "Analytischer Schwellwert", achse="x")
    traces = json.loads(pio.to_json(fig))["data"]
    ci.vorbereiten(fig)
    first = pio.to_json(fig)
    ci.vorbereiten(fig)
    assert pio.to_json(fig) == first
    styled_traces = json.loads(first)["data"]
    for trace in styled_traces:
        assert trace.pop("textfont")["family"] == theme.FONT
    assert styled_traces == traces
    assert len(fig.layout.images) == 1
    assert any(a.text == "Analytischer Schwellwert" for a in fig.layout.annotations)
    footer = next(a for a in fig.layout.annotations if a.name == "sww-brand-source")
    assert "Messwerte &lt;intern&gt;.csv" in footer.text
    assert len(fig.layout.shapes) == 3  # Original threshold plus two brand rules.


def test_notebook_cover_uses_original_logo_and_escapes_dynamic_text(monkeypatch):
    import IPython.display

    rendered = []
    monkeypatch.setattr(IPython.display, "display", rendered.append)
    logo = ROOT / "brand/design-system/assets/logo-sww-full.png"
    ci.titelkarte(
        "Analyse <Westhafen>", "Daten & Qualität", "Stand: Test",
        logo=logo, metriken=[("Zähler <gesamt>", "700")], zeitraum="01/2024–12/2025",
    )
    html = rendered[0].data
    assert ci._logo_uri(logo) in html
    assert "Analyse &lt;Westhafen&gt;" in html
    assert "Zähler &lt;gesamt&gt;" in html
    assert "Daten &amp; Qualität" in html
    assert '<strong>700</strong>' in html
    assert "@font-face" in html


def test_notebook_chapter_supports_a_modeling_context(monkeypatch):
    import IPython.display

    rendered = []
    monkeypatch.setattr(IPython.display, "display", rendered.append)
    ci.abschnitt(
        "03",
        "Modellvergleich",
        "Validierung ohne Testleckage.",
        kontext="MODELLIERUNG & EVALUATION",
    )
    html = rendered[0].data
    assert "WESTHAFEN / MODELLIERUNG &amp; EVALUATION" in html
    assert "Modellvergleich" in html
    assert "Validierung ohne Testleckage." in html


def test_notebook_setup_reloads_a_cached_pre_logo_api():
    setup = runpy.run_path(str(ROOT / "scripts/build_eda_ci_notebook.py"))["SETUP"]
    notebook = nbformat.read(ROOT / "ipynb/eda_ci.ipynb", as_version=4)
    setup_cell = next(c for c in notebook.cells if c.metadata.get("sww_original_cell") == 1)
    assert setup_cell.source.split("DATA_DIR =", 1)[0] == setup
    # A separate interpreter avoids resetting module globals used by other tests.
    script = f'''
from pathlib import Path
from unittest.mock import patch
from energy_analytics.visualization import notebook as ci

for attempt in range(2):
    ci.aktiviere = lambda: None  # Simulate an import cached before logo support.
    try:
        ci.aktiviere(logo="unused.png")
    except TypeError:
        pass
    else:
        raise AssertionError("Stale API was not reproduced")
    with patch("IPython.display.display"):
        exec({setup!r}, {{}})
    assert ci.QUELLE == "verbrauch_bereinigt.csv"
    assert ci._LOGO == ci._logo_uri(Path("brand/design-system/assets/logo-sww-emblem.png"))
print("Cached API refreshed successfully on both setup executions")
'''
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_notebook_table_has_own_surface_and_preserves_data():
    data = pd.DataFrame({"Wert": [1234.5, float("nan")], "Rolle": ["<Messung>", "Prüfung"]})
    before = data.copy(deep=True)
    html = ci.tabellenansicht(data).data
    assert '<div class="sww-table">' in html
    assert "1.234,5" in html and "—" in html and "&lt;Messung&gt;" in html
    assert ".sww-table table,.sww-table td" in html
    assert f'background:{theme.TOKENS["surface-card"]} !important' in html
    assert f'color:{theme.TOKENS["text-primary"]} !important' in html
    assert f'color:{theme.TOKENS["text-inverse"]} !important' in html
    pd.testing.assert_frame_equal(data, before)
