"""Regressions for the saved SWW EDA and its per-figure presentation."""

import base64
from pathlib import Path

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
    assert notebook.metadata.kernelspec.name == "sww-energy-analytics"
    assert notebook.metadata.kernelspec.display_name == "Python (SWW .venv)"
    # Provenance is a snapshot, not a dependency on future edits to Patrick's original.
    assert notebook.metadata.sww.source == "ipynb/eda.ipynb"
    assert len(notebook.metadata.sww.source_sha256) == 64
    int(notebook.metadata.sww.source_sha256, 16)
    assert [c.metadata.sww_original_cell for c in notebook.cells[2:]] == list(range(1, 77))
    code = [c for c in notebook.cells if c.cell_type == "code"]
    assert len(code) == 38
    assert all(c.execution_count is not None for c in code)
    assert not any("import viz" in c.source or "viz." in c.source for c in code)
    plots = []
    for cell in code:
        for output in cell.outputs:
            assert output.output_type != "error"
            data = output.get("data", {})
            figure = data.get("application/vnd.plotly.v1+json")
            if figure:
                assert base64.b64decode(data["image/png"]).startswith(b"\x89PNG\r\n\x1a\n")
                layout = figure["layout"]
                assert layout["font"]["family"] == theme.FONT
                assert layout["paper_bgcolor"] == theme.TOKENS["chart-paper-bg"]
                assert layout["colorway"] == theme.QUALITATIVE
                assert layout["meta"]["sww"]["period"] == "01/2024–12/2025"
                for trace in figure["data"]:
                    if trace.get("name") in theme.KUNDENTYP_COLORS:
                        color = trace.get("marker", {}).get("color") or trace.get("line", {}).get(
                            "color"
                        )
                        assert color == theme.KUNDENTYP_COLORS[trace["name"]]
                plots.append(figure)
    assert len(plots) == 32


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
