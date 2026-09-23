"""Structural safeguards for the generated optimized modeling notebook."""

from __future__ import annotations

import hashlib
from pathlib import Path
import runpy

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "20_modeling_optimierung.ipynb"
EXPECTED_FIGURE_CELLS = {
    "optimization-evidence-timeline",
    "optimization-wape-example",
    "optimization-feature-availability",
    "optimization-ablation-plot",
    "optimization-fold-plot",
    "optimization-search-plot",
    "optimization-calibration-plot",
    "optimization-final-benchmark",
    "optimization-monthly-plot",
    "optimization-segment-plot",
    "optimization-bootstrap-plot",
}


def _plotly_figure_cells(notebook) -> set[str]:
    return {
        cell.id
        for cell in notebook.cells
        for output in cell.get("outputs", [])
        if output.get("data", {}).get("application/vnd.plotly.v1+json")
    }


def test_optimized_modeling_notebook_is_valid_and_reproducible(tmp_path):
    saved = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(saved)
    assert len({cell.id for cell in saved.cells}) == len(saved.cells)

    metadata = saved.metadata.sww
    assert metadata.builder == "scripts/build_optimized_modeling_notebook.py"
    assert metadata.data_source == "data/raw/260916_verbrauch_bereinigt.csv"
    assert metadata.development_period == "2024-01 through 2024-12"
    assert metadata.test_period == "2025-01 through 2025-12"
    assert len(metadata.data_sha256) == 64
    assert metadata.data_sha256 == hashlib.sha256(
        (ROOT / metadata.data_source).read_bytes()
    ).hexdigest()

    code_cells = [cell for cell in saved.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert not any(
        output.output_type == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )
    assert _plotly_figure_cells(saved) == EXPECTED_FIGURE_CELLS

    build_notebook = runpy.run_path(
        str(ROOT / "scripts" / "build_optimized_modeling_notebook.py")
    )["build_notebook"]
    rebuilt_path = build_notebook(tmp_path / "optimized-modeling.ipynb")
    rebuilt = nbformat.read(rebuilt_path, as_version=4)
    assert [(cell.id, cell.cell_type, cell.source) for cell in saved.cells] == [
        (cell.id, cell.cell_type, cell.source) for cell in rebuilt.cells
    ]
    # Kernel execution enriches ``language_info`` with interpreter-specific fields.
    assert saved.metadata.sww == rebuilt.metadata.sww
    assert saved.metadata.kernelspec == rebuilt.metadata.kernelspec
    assert saved.metadata.language_info.name == rebuilt.metadata.language_info.name


def test_optimized_modeling_notebook_encodes_the_method_contract():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    sources = "\n".join(cell.source for cell in notebook.cells)
    code_sources = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "code"
    )

    required_code_fragments = {
        "np.log1p",
        "np.expm1",
        "PLAN_SNAPSHOT_CONFIRMED",
        "ParameterGrid",
        "weighted_median",
        "shift(1)",
        "HistGradientBoostingRegressor",
        "ExtraTreesRegressor",
    }
    assert all(fragment in code_sources for fragment in required_code_fragments)
    assert "2025 ist bereits bekannt" in sources
    assert "train_test_split" not in code_sources


def test_all_optimized_modeling_charts_use_the_shared_ci_renderer():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    shown_cells = {
        cell.id: cell.source
        for cell in notebook.cells
        if cell.cell_type == "code" and "ci.zeigen(" in cell.source
    }

    assert set(shown_cells) == EXPECTED_FIGURE_CELLS
    assert all(
        "ci.stil(" in source and "ci.zeigen(" in source
        for source in shown_cells.values()
    )
