"""Contract checks for the Verbrauchs-Cockpit export (energy_analytics.dashboard_export)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from energy_analytics.dashboard_export import (
    REQUIRED_BENCHMARK_COLUMNS,
    build_payload,
    write_payload,
)

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ROOT / "brand/design-system/ui_kits/verbrauchs-cockpit/forecast-data.json"


def _benchmark(meters: int = 12, threshold: float = 50.0) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    months = pd.date_range("2025-01-01", periods=12, freq="MS")
    frame = pd.DataFrame(
        [(f"ZL-{m:05d}", f"KD-{m:06d}", ["Gewerbe", "Industrie", "Kommunal"][m % 3], month)
         for m in range(meters) for month in months],
        columns=["zaehler_id", "kunde_id", "kundentyp", "monat"],
    )
    frame["vertragsleistung_kw"] = 100.0 + frame.index % 7
    frame["prognose_kwh"] = 15_000 + rng.normal(0, 500, len(frame))
    frame["verbrauch_kwh"] = frame["prognose_kwh"] + rng.normal(0, 2_000, len(frame))
    frame.loc[5, "verbrauch_kwh"] += 20_000
    frame["residuum_kwh"] = frame["verbrauch_kwh"] - frame["prognose_kwh"]
    frame["residuum_vls"] = frame["residuum_kwh"] / frame["vertragsleistung_kw"]
    frame["anomalie_score"] = frame["residuum_vls"].abs() / threshold
    frame["anomalie"] = frame["anomalie_score"].ge(1)
    frame["richtung"] = np.where(frame["residuum_vls"].ge(0), "ungewöhnlich hoch", "ungewöhnlich niedrig")
    frame["rolling_3_kwh"] = 15_000.0
    return frame


def _metrics() -> pd.DataFrame:
    return pd.DataFrame([
        {"Kandidat": "Random Forest", "Typ": "Modell", "RMSE (kWh)": 1.0, "MAE (kWh)": 1.0, "R²": 0.9},
        {"Kandidat": "Vormonat", "Typ": "Baseline", "RMSE (kWh)": 2.0, "MAE (kWh)": 2.0, "R²": 0.8},
    ])


def test_missing_required_column_names_the_column():
    frame = _benchmark().drop(columns=["residuum_vls"])
    with pytest.raises(ValueError, match="residuum_vls"):
        build_payload(frame, [1.0, -1.0], _metrics(), 50.0)


def test_optional_blocks_may_be_missing_and_output_is_valid_js(tmp_path):
    frame = _benchmark()
    payload = build_payload(frame, np.linspace(-60, 60, 200), _metrics(), 50.0, final_name="Random Forest")
    assert payload["importance"] is None and payload["sensitivity"] is None and payload["history"] is None
    assert len(payload["rows"]["zaehler_id"]) == len(frame)
    assert sum(payload["rows"]["anomalie"]) == int(frame["anomalie"].sum()) >= 1
    assert payload["metrics"][0]["final"] is True
    assert len(payload["residuals"]["qq"]["theoretisch"]) == len(payload["residuals"]["qq"]["beobachtet"])
    assert [row["monat"] for row in payload["residuals"]["monate"]] == payload["months"]

    path = write_payload(payload, tmp_path / "forecast-data.js")
    text = path.read_text(encoding="utf-8")
    assert text.startswith("/* Generated") and "window.SWWForecastData = " in text
    assert json.loads(text.split("= ", 1)[1].rstrip().rstrip(";")) == payload
    assert json.loads(path.with_suffix(".json").read_text(encoding="utf-8")) == payload


def test_nan_values_become_null():
    frame = _benchmark()
    frame.loc[0, "rolling_3_kwh"] = np.nan
    payload = build_payload(frame, [1.0, 2.0], _metrics(), 50.0)
    assert payload["rows"]["rolling_3_kwh"].count(None) == 1
    json.dumps(payload, allow_nan=False)


def test_shipped_export_matches_official_notebook_12():
    payload = json.loads(SHIPPED.read_text(encoding="utf-8"))
    assert set(REQUIRED_BENCHMARK_COLUMNS) <= set(payload["rows"])
    assert len(payload["rows"]["zaehler_id"]) == 8_398
    assert payload["meta"]["source"] == "notebooks/12_modeling_ihk_lernstory.ipynb"
    assert payload["threshold"]["n_kalibrierung"] == 1_397
    assert payload["threshold"]["wert"] == pytest.approx(144.35, abs=0.01)
    assert sum(payload["rows"]["anomalie"]) == 114
    directions = pd.Series(payload["rows"]["richtung"])[
        np.asarray(payload["rows"]["anomalie"], dtype=bool)
    ].value_counts()
    assert directions.to_dict() == {
        "ungewöhnlich hoch": 68,
        "ungewöhnlich niedrig": 46,
    }
    final = next(row for row in payload["metrics"] if row["final"])
    assert (round(final["rmse"]), round(final["mae"]), round(final["r2"], 3)) == (
        9_188,
        3_725,
        0.901,
    )
