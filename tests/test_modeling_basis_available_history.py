"""Checks for the derived, available-history modeling snapshot."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_modeling_basis_available_history.py"
OUTPUT = ROOT / "data" / "processed" / "modellierung_basis_bis_3_monate.csv"
PROVENANCE = OUTPUT.with_suffix(".provenance.json")


def _module():
    spec = importlib.util.spec_from_file_location("available_history", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_available_history_snapshot_is_current_and_safe():
    module = _module()
    csv_text, provenance_text = module.build_artifacts()

    assert OUTPUT.read_text(encoding="utf-8") == csv_text
    assert PROVENANCE.read_text(encoding="utf-8") == provenance_text

    frame = pd.read_csv(OUTPUT, parse_dates=["monat"])
    assert len(frame) == 16_800
    assert frame["zaehler_id"].nunique() == 700
    assert frame["letzte_3_monate_vls"].isna().sum() == 700

    example = frame[frame["zaehler_id"].eq("ZL-00000")].sort_values("monat")
    assert pd.isna(example.iloc[0]["letzte_3_monate_vls"])
    assert example.iloc[1]["letzte_3_monate_vls"] == example.iloc[0]["vollaststunden"]
    assert example.iloc[2]["letzte_3_monate_vls"] == example.iloc[:2]["vollaststunden"].mean()
    assert example.iloc[3]["letzte_3_monate_vls"] == example.iloc[:3]["vollaststunden"].mean()
