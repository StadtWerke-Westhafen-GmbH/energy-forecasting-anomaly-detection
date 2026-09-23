"""Regression checks for the model-derived anomaly dashboard export."""

from __future__ import annotations

import hashlib
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "260916_verbrauch_bereinigt.csv"
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
    assert round(payload["meta"]["threshold_score"], 2) == 6.33
    assert round(payload["meta"]["benchmark_wape_pct"], 2) == 17.10
    assert payload["meta"]["labels_available"] is False

    summary = payload["summary"]
    assert summary == {
        "observations": 8_400,
        "meters_total": 700,
        "alerts_total": 105,
        "meters_affected": 100,
        "alerts_per_month": 8.75,
        "alert_rate_pct": 1.25,
        "high": 20,
        "low": 85,
        "dq_flags_total": 10,
        "dq_overlap": 6,
    }
    assert sum(row["alerts"] for row in payload["monthly"]) == 105
    assert sum(row["alerts"] for row in payload["segments"]) == 105

    alerts = payload["alerts"]
    assert len({row["alert_id"] for row in alerts}) == 105
    assert alerts[0]["alert_id"] == "ZL-00390-2025-03"
    assert alerts[0]["wartung_aktiv"] is True
    assert alerts[0]["dq_capacity"] is False
    assert round(alerts[0]["score"], 2) == 19.57

    series = payload["meters"]["ZL-00390"]["series"]
    assert len(series) == 24
    assert all(row["forecast_kwh"] is None for row in series[:10])
    assert series[10]["phase"] == "Kalibrierung"
    assert series[-1]["phase"] == "Benchmark"

