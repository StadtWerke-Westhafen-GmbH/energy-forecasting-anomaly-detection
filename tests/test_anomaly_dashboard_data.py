"""Regression checks for the model-derived anomaly dashboard export."""

from __future__ import annotations

import hashlib
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "modellierung_basis_bis_3_monate.csv"
OUTPUT = (
    ROOT
    / "brand"
    / "design-system"
    / "ui_kits"
    / "energie-cockpit"
    / "anomaly-data.js"
)


def test_anomaly_dashboard_export_matches_the_reproducible_story():
    module = runpy.run_path(str(ROOT / "scripts" / "build_anomaly_dashboard_data.py"))
    payload = module["build_payload"]()
    rendered = module["render"](payload)

    assert OUTPUT.read_text(encoding="utf-8") == rendered
    assert payload["meta"]["source_sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert payload["meta"]["threshold_quantile"] == 0.99
    assert round(payload["meta"]["threshold_vls"], 2) == 144.35
    assert round(payload["meta"]["benchmark_rmse_kwh"], 0) == 9_188
    assert round(payload["meta"]["benchmark_mae_kwh"], 0) == 3_725
    assert round(payload["meta"]["benchmark_r2"], 3) == 0.901
    assert payload["meta"]["labels_available"] is False

    summary = payload["summary"]
    assert summary == {
        "observations": 8_398,
        "meters_total": 700,
        "alerts_total": 114,
        "meters_affected": 107,
        "alerts_per_month": 9.5,
        "alert_rate_pct": 1.3575,
        "high": 68,
        "low": 46,
        "dq_flags_total": 10,
        "dq_overlap": 10,
    }
    assert sum(row["alerts"] for row in payload["monthly"]) == 114
    assert sum(row["alerts"] for row in payload["segments"]) == 114

    options = payload["threshold_options"]
    assert [row["percentile"] for row in options] == [95.0, 97.5, 99.0, 99.5]
    assert [row["alerts"] for row in options] == [400, 256, 114, 69]
    assert [round(row["threshold_vls"], 2) for row in options] == [67.99, 82.43, 144.35, 196.30]
    assert len(payload["observations"]) == 8_398
    assert len({row["alert_id"] for row in payload["observations"]}) == 8_398
    assert len(payload["meters"]) == 265

    alerts = payload["alerts"]
    assert len({row["alert_id"] for row in alerts}) == 114
    assert alerts[0]["alert_id"] == "ZL-00307-2025-04"
    assert alerts[0]["wartung_aktiv"] is False
    assert alerts[0]["dq_capacity"] is True
    assert round(alerts[0]["score"], 2) == 5.44

    series = payload["meters"]["ZL-00307"]["series"]
    assert len(series) == 24
    assert all(row["forecast_kwh"] is None for row in series[:10])
    assert series[10]["phase"] == "Kalibrierung"
    assert series[-1]["phase"] == "Benchmark"

