"""Safeguards for the explanatory modeling learning notebook."""

from __future__ import annotations

import hashlib
from pathlib import Path
import runpy

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "13_modellierung_von_grund_auf_verstehen.ipynb"
EXPECTED_FIGURE_CELLS = {
    "learn-vls-example",
    "learn-lag-plot",
    "learn-time-split",
    "learn-metrics-example",
    "learn-cv-comparison",
    "learn-benchmark",
    "learn-vls-vs-kwh",
    "learn-feature-importance",
    "learn-ranked-errors",
    "learn-vls-boundary-plot",
    "learn-threshold-workload",
    "learn-case-timeseries",
    "learn-factor-plot",
}


def _figure_cells(notebook) -> set[str]:
    return {
        cell.id
        for cell in notebook.cells
        for output in cell.get("outputs", [])
        if output.get("data", {}).get("application/vnd.plotly.v1+json")
    }


def _authored_cells(notebook) -> list[tuple[str, str, str]]:
    return [(cell.id, cell.cell_type, cell.source) for cell in notebook.cells]


def test_learning_notebook_is_executed_and_reproducible(tmp_path):
    saved = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(saved)
    assert len({cell.id for cell in saved.cells}) == len(saved.cells)
    assert _figure_cells(saved) == EXPECTED_FIGURE_CELLS

    code_cells = [cell for cell in saved.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert all("hide-input" in cell.metadata.get("tags", []) for cell in code_cells)
    assert not any(
        output.output_type == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )

    metadata = saved.metadata.sww
    data_path = ROOT / metadata.data_source
    assert metadata.builder == "scripts/build_modeling_verstehen_notebook.py"
    assert metadata.official_exam_notebook == "notebooks/12_modeling_ihk_lernstory.ipynb"
    assert metadata.learning_quantile == 0.975
    assert metadata.official_pilot_quantile == 0.99
    assert metadata.source_sha256 == hashlib.sha256(data_path.read_bytes()).hexdigest()

    build = runpy.run_path(
        str(ROOT / "scripts" / "build_modeling_verstehen_notebook.py")
    )["build_notebook"]
    rebuilt_path = build(tmp_path / "learning.ipynb")
    rebuilt = nbformat.read(rebuilt_path, as_version=4)
    assert _authored_cells(saved) == _authored_cells(rebuilt)


def test_learning_notebook_covers_the_full_explanation_chain():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    sources = "\n".join(cell.source for cell in notebook.cells)
    required = {
        "kW, kWh und Vollaststunden",
        "shift(1)",
        "Data Leakage",
        "Vormonat",
        "Bis-zu-3-Monats-Mittel",
        "Lineare Regression",
        "Random Forest",
        "Hyperparameter",
        "RMSE",
        "MAE",
        "R²",
        "Whisker",
        "1.362",
        "82,4304",
        "Schwellenfaktor",
        "Faktor ist keine Wahrscheinlichkeit",
        "ZL-00147",
        "Precision und Recall",
        "Das Modell ersetzt keine Abrechnungsentscheidung",
    }
    assert all(fragment in sources for fragment in required)
    assert "train_test_split" not in sources
    assert "WAPE" not in sources


def test_learning_notebook_outputs_show_the_verified_case_and_metrics():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    html = "\n".join(
        output.get("data", {}).get("text/html", "")
        for cell in notebook.cells
        for output in cell.get("outputs", [])
    )
    assert "13.272 kWh" in html
    assert "9.188 kWh" in html
    assert "15,9 Prozent" in html
    assert "82,4304 VLS-h" in html
    assert "4,026" in html
    assert "1,195" in html
    assert "zwei getrennte monatliche Prüfhinweise" in html
