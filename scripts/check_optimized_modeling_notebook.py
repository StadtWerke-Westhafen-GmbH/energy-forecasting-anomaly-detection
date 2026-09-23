"""Execute and validate the optimized modeling notebook in a fresh kernel.

By default execution happens in memory. Pass ``--update`` to persist verified
outputs in ``notebooks/20_modeling_optimierung.ipynb``.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "notebooks" / "20_modeling_optimierung.ipynb"
PROTECTED = (
    ROOT / "data" / "raw" / "260916_verbrauch_bereinigt.csv",
    ROOT / "data" / "raw" / "verbrauch.csv",
    ROOT / "notebooks" / "00_design_system.ipynb",
    ROOT / "notebooks" / "10_modeling.ipynb",
)
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


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update",
        action="store_true",
        help="write the successfully executed notebook back to its source path",
    )
    args = parser.parse_args()

    before = {path: _digest(path) for path in PROTECTED}
    notebook = nbformat.read(TARGET, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=1_800,
        kernel_name="python3",
        allow_errors=False,
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.km = client.create_kernel_manager()
    client.km.kernel_spec.argv = [
        sys.executable,
        "-m",
        "ipykernel_launcher",
        "-f",
        "{connection_file}",
    ]
    client.on_cell_start = lambda cell, cell_index: (
        print(f"Execute {cell_index + 1}/{len(notebook.cells)}: {cell.id}", flush=True)
        if cell.cell_type == "code"
        else None
    )
    kernel_env = dict(
        os.environ,
        IPYTHONDIR=str(ROOT / ".build" / "ipython-modeling-optimization"),
    )
    client.execute(env=kernel_env)

    figures = []
    figure_cells = set()
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            assert output.output_type != "error", cell.id
            figure = output.get("data", {}).get("application/vnd.plotly.v1+json")
            if figure:
                meta = figure["layout"]["meta"]["sww"]
                assert meta["source"] == "data/raw/260916_verbrauch_bereinigt.csv"
                assert meta["period"] == "01/2024–12/2025"
                figures.append(figure)
                figure_cells.add(cell.id)

    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert figure_cells == EXPECTED_FIGURE_CELLS
    assert len(figures) == len(EXPECTED_FIGURE_CELLS)
    nbformat.validate(notebook)

    for path, digest in before.items():
        assert _digest(path) == digest, f"Protected file changed: {path}"

    if args.update:
        nbformat.write(notebook, TARGET)
    print(
        f"Validated {len(code_cells)} code cells and {len(figures)} charts"
        + ("; outputs updated." if args.update else "; source notebook unchanged.")
    )


if __name__ == "__main__":
    main()
