"""Structural safeguards for the presentation-first modeling story notebook."""

from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import runpy

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "11_modeling_pruefungsstory.ipynb"
EXPECTED_FIGURE_CELLS = {
    "story-process-overview",
    "story-time-split",
    "story-model-comparison",
    "story-test-benchmark",
    "story-portfolio",
    "story-calibration-distribution",
    "story-threshold",
    "story-alerts",
    "story-case",
    "story-operations-flow",
    "story-outlook",
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


def _core_sww_metadata(metadata) -> dict[str, str]:
    """Return reproducibility metadata, excluding the generation timestamp."""
    keys = {
        "builder",
        "data_source",
        "source_sha256",
        "development_period",
        "benchmark_period",
        "forecast_horizon",
    }
    return {key: metadata[key] for key in keys}


def test_modeling_story_notebook_is_valid_executed_and_reproducible(tmp_path):
    saved = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(saved)
    assert len({cell.id for cell in saved.cells}) == len(saved.cells)

    metadata = saved.metadata.sww
    assert metadata.builder == "scripts/build_modeling_story_notebook.py"
    assert metadata.data_source == "data/raw/260916_verbrauch_bereinigt.csv"
    assert metadata.development_period == "01/2024\u201312/2024"
    assert metadata.benchmark_period == "01/2025\u201312/2025"
    assert metadata.forecast_horizon == "1 Monat"
    assert len(metadata.source_sha256) == 64
    assert metadata.source_sha256 == hashlib.sha256(
        (ROOT / metadata.data_source).read_bytes()
    ).hexdigest()
    generated_at = datetime.fromisoformat(
        str(metadata.generated_at_utc).replace("Z", "+00:00")
    )
    assert generated_at.utcoffset() is not None

    code_cells = [cell for cell in saved.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert not any(
        output.output_type == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )
    assert _plotly_figure_cells(saved) == EXPECTED_FIGURE_CELLS

    build_notebook = runpy.run_path(
        str(ROOT / "scripts" / "build_modeling_story_notebook.py")
    )["build_notebook"]
    rebuilt_path = build_notebook(tmp_path / "modeling-story.ipynb")
    rebuilt = nbformat.read(rebuilt_path, as_version=4)
    assert _authored_cells(saved) == _authored_cells(rebuilt)
    assert _core_sww_metadata(saved.metadata.sww) == _core_sww_metadata(
        rebuilt.metadata.sww
    )
    # Kernel execution enriches language_info with interpreter-specific fields.
    assert saved.metadata.kernelspec == rebuilt.metadata.kernelspec
    assert saved.metadata.language_info.name == rebuilt.metadata.language_info.name


def test_modeling_story_notebook_encodes_the_exam_contract():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    sources = "\n".join(cell.source for cell in notebook.cells)
    code_sources = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "code"
    )

    required_fragments = {
        "Vollaststunden",
        "ANOMALY_QUANTILE",
        "robust_scale",
        "shift(1)",
        "RandomForestRegressor",
        "Das Modell ersetzt keine",
        "keine gelabelten",
    }
    assert all(fragment in sources for fragment in required_fragments)
    assert "train_test_split" not in code_sources


def test_all_story_charts_use_the_shared_ci_renderer():
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
