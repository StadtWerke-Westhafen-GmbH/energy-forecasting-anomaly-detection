"""Structural safeguards for the generated modeling notebook."""

from __future__ import annotations

import hashlib
from pathlib import Path
import runpy

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "10_modeling.ipynb"


def test_modeling_notebook_is_valid_and_reproducible(tmp_path):
    saved = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(saved)
    assert len({cell.id for cell in saved.cells}) == len(saved.cells)
    assert saved.metadata.sww.builder == "scripts/build_modeling_notebook.py"
    assert saved.metadata.sww.train_period == "2024-01 through 2024-12"
    assert saved.metadata.sww.test_period == "2025-01 through 2025-12"
    assert len(saved.metadata.sww.data_sha256) == 64
    assert saved.metadata.sww.data_sha256 == hashlib.sha256(
        (ROOT / saved.metadata.sww.data_source).read_bytes()
    ).hexdigest()
    code_cells = [cell for cell in saved.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert not any(
        output.output_type == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )

    build_notebook = runpy.run_path(
        str(ROOT / "scripts" / "build_modeling_notebook.py")
    )["build_notebook"]
    rebuilt_path = build_notebook(tmp_path / "modeling.ipynb")
    rebuilt = nbformat.read(rebuilt_path, as_version=4)
    assert [(c.id, c.cell_type, c.source) for c in saved.cells] == [
        (c.id, c.cell_type, c.source) for c in rebuilt.cells
    ]
    # Kernel execution enriches ``language_info`` with interpreter-specific fields.
    # The authored metadata and all sources must still remain deterministic.
    assert saved.metadata.sww == rebuilt.metadata.sww
    assert saved.metadata.kernelspec == rebuilt.metadata.kernelspec
    assert saved.metadata.language_info.name == rebuilt.metadata.language_info.name


def test_modeling_notebook_encodes_the_decision_contract():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    sources = "\n".join(cell.source for cell in notebook.cells)
    code_sources = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "code"
    )

    required_ids = {
        "modeling-target-plot",
        "modeling-pipeline-definition",
        "modeling-grid-search",
        "modeling-final-evaluation",
        "modeling-calibration-holdout",
        "modeling-scorecard",
    }
    assert required_ids.issubset({cell.id for cell in notebook.cells})
    assert "ziel_vls" in code_sources
    assert "TransformedTargetRegressor" in code_sources
    assert "GridSearchCV" in code_sources
    assert "cv_2024" in code_sources
    assert "rolling_3_kwh" in code_sources
    assert "train_test_split" not in code_sources
    assert "Das Modell ersetzt keine Abrechnungsentscheidung" in sources


def test_all_modeling_charts_use_the_shared_ci_renderer():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    code_sources = [cell.source for cell in notebook.cells if cell.cell_type == "code"]
    chart_cells = [source for source in code_sources if "fig = " in source]
    assert len(chart_cells) >= 10
    assert all("ci.stil(" in source and "ci.zeigen(fig)" in source for source in chart_cells)
