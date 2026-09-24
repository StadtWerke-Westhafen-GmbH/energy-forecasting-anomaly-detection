"""Execute and validate the explanatory modeling learning notebook."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "notebooks" / "13_modellierung_von_grund_auf_verstehen.ipynb"
DATA_SOURCE = ROOT / "data" / "processed" / "modellierung_basis_bis_3_monate.csv"
PROTECTED = tuple(
    path
    for path in (
        DATA_SOURCE,
        ROOT / "data" / "processed" / "modellierung_basis.csv",
        ROOT / "notebooks" / "12_modeling_ihk_lernstory.ipynb",
    )
    if path.exists()
)
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


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    before = {path: _digest(path) for path in PROTECTED}
    notebook = nbformat.read(TARGET, as_version=4)
    metadata = notebook.metadata.sww
    assert metadata.builder == "scripts/build_modeling_verstehen_notebook.py"
    assert metadata.source_sha256 == _digest(DATA_SOURCE)
    assert metadata.anomaly_quantile == 0.99
    assert metadata.official_pilot_quantile == 0.99

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
    client.execute(
        env=dict(
            os.environ,
            IPYTHONDIR=str(ROOT / ".build" / "ipython-modeling-learning"),
        )
    )

    figure_cells = {
        cell.id
        for cell in notebook.cells
        for output in cell.get("outputs", [])
        if output.get("data", {}).get("application/vnd.plotly.v1+json")
    }
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert figure_cells == EXPECTED_FIGURE_CELLS
    assert not any(
        output.output_type == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )
    nbformat.validate(notebook)

    for path, digest in before.items():
        assert _digest(path) == digest, f"Protected file changed: {path}"

    if args.update:
        nbformat.write(notebook, TARGET)
    print(
        f"Validated {len(code_cells)} code cells and {len(figure_cells)} charts"
        + ("; outputs updated." if args.update else "; source notebook unchanged.")
    )


if __name__ == "__main__":
    main()
