"""Safeguards for the Learning-Journey-aligned IHK modeling notebook."""

from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import runpy

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "12_modeling_ihk_lernstory.ipynb"
EXPECTED_FIGURE_CELLS = {
    "ihk-time-split",
    "ihk-model-comparison",
    "ihk-benchmark",
    "ihk-target-comparison",
    "ihk-feature-importance",
    "ihk-calibration",
    "ihk-threshold",
    "ihk-alerts",
    "ihk-actual-vs-predicted",
    "ihk-case",
}


def _plotly_figure_cells(notebook) -> set[str]:
    return {
        cell.id
        for cell in notebook.cells
        for output in cell.get("outputs", [])
        if output.get("data", {}).get("application/vnd.plotly.v1+json")
    }


def _authored_cells(notebook) -> list[tuple[str, str, str]]:
    return [(cell.id, cell.cell_type, cell.source) for cell in notebook.cells]


def _core_sww_metadata(metadata) -> dict[str, object]:
    keys = {
        "builder",
        "data_source",
        "source_sha256",
        "development_period",
        "benchmark_period",
        "forecast_horizon",
        "primary_metric",
        "learning_journey_aligned",
    }
    return {key: metadata[key] for key in keys}


def test_ihk_notebook_is_valid_executed_and_reproducible(tmp_path):
    saved = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(saved)
    assert len({cell.id for cell in saved.cells}) == len(saved.cells)

    metadata = saved.metadata.sww
    assert metadata.builder == "scripts/build_modeling_ihk_lernstory_notebook.py"
    assert metadata.data_source == "data/processed/modellierung_basis_bis_3_monate.csv"
    assert metadata.development_period == "01/2024\u201312/2024"
    assert metadata.benchmark_period == "01/2025\u201312/2025"
    assert metadata.forecast_horizon == "1 Monat"
    assert metadata.primary_metric == "RMSE (kWh)"
    assert metadata.learning_journey_aligned is True
    assert metadata.source_sha256 == hashlib.sha256(
        (ROOT / metadata.data_source).read_bytes()
    ).hexdigest()
    generated_at = datetime.fromisoformat(
        str(metadata.generated_at_utc).replace("Z", "+00:00")
    )
    assert generated_at.utcoffset() is not None

    code_cells = [cell for cell in saved.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert all("hide-input" in cell.metadata.get("tags", []) for cell in code_cells)
    assert not any(
        output.output_type == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )
    assert _plotly_figure_cells(saved) == EXPECTED_FIGURE_CELLS

    build_notebook = runpy.run_path(
        str(ROOT / "scripts" / "build_modeling_ihk_lernstory_notebook.py")
    )["build_notebook"]
    rebuilt_path = build_notebook(tmp_path / "modeling-ihk-story.ipynb")
    rebuilt = nbformat.read(rebuilt_path, as_version=4)
    assert _authored_cells(saved) == _authored_cells(rebuilt)
    assert _core_sww_metadata(saved.metadata.sww) == _core_sww_metadata(
        rebuilt.metadata.sww
    )


def test_ihk_notebook_encodes_the_exam_contract():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    sources = "\n".join(cell.source for cell in notebook.cells)
    code_sources = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "code"
    )

    required_fragments = {
        "Vollaststunden",
        "LinearRegression",
        "RandomForestRegressor",
        "DIRECT_KWH_X_COLUMNS",
        "direct_kwh_forest_estimator",
        "mean_squared_error",
        "mean_absolute_error",
        "r2_score",
        "Permutation Importance",
        "ziel_rekonstruiert",
        "shift(1)",
        "rolling(3, min_periods=1)",
        "heizgradtage",
        "vormonat_vls",
        "letzte_3_monate_vls",
        "pruefhinweis",
        "RF_PARSIMONY_TOLERANCE",
        "One-Step-Ahead",
        "winterlastige Kalibrierung",
        "Ist gegen Prognose: Abstand zur Diagonalen zeigt den Fehler",
        "So liest du den Ist-Prognose-Plot in 20 Sekunden",
        "Das Modell ersetzt keine",
        "Precision und Recall",
        "LEARNING JOURNEY",
    }
    assert all(fragment in sources for fragment in required_fragments)
    assert "train_test_split" not in code_sources
    assert "WAPE" not in sources
    assert "border-left" not in sources
    assert "Missing-Flags" not in sources

    model_definition = next(
        cell.source for cell in notebook.cells if cell.id == "ihk-model-definition"
    )
    assert '"heizgradtage"' in model_definition
    assert '"mittlere_temperatur_c"' not in model_definition


def test_all_ihk_charts_use_the_shared_ci_renderer():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    plot_cells = {
        cell.id: cell.source
        for cell in notebook.cells
        if cell.id in EXPECTED_FIGURE_CELLS
    }

    assert set(plot_cells) == EXPECTED_FIGURE_CELLS
    assert all(
        "ci.stil(" in source and "ci.zeigen(fig)" in source
        for source in plot_cells.values()
    )


def test_canvas_uses_the_five_group_learning_journey_layout():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    setup = next(cell.source for cell in notebook.cells if cell.id == "ihk-setup")
    canvas = next(cell.source for cell in notebook.cells if cell.id == "ihk-canvas")

    groups = {
        "Nutzen & Daten",
        "Ziel & Signale",
        "Modell & Nachweis",
        "Handlung & Wirkung",
        "Zeitpunkt & Betrieb",
    }
    assert all(group in canvas for group in groups)
    assert "sww-canvas-map" in setup
    assert "sww-canvas-stage" in setup
    assert "Kohärenzcheck" in canvas
    assert "Value Proposition / Mehrwert" not in canvas


def test_saved_outputs_contain_the_verified_key_results():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    html = "\n".join(
        output.get("data", {}).get("text/html", "")
        for cell in notebook.cells
        for output in cell.get("outputs", [])
    )

    assert "9.188 kWh" in html
    assert "9.800 kWh" in html
    assert "6,2 %" in html
    assert "15,9 %" in html
    assert "4 von 4" in html
    assert "14,3 %" in html
    assert "114" in html
    assert "144,4 VLS-Stunden" in html
