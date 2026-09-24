"""Datenvertrag und Export für das Verbrauchs-Cockpit.

Das Modeling-Notebook übergibt seine Ergebnis-DataFrames an :func:`build_payload`;
:func:`write_payload` schreibt daraus ``forecast-data.js`` (für das Dashboard) und eine
gleichnamige ``.json``-Datei. Das Frontend filtert, gruppiert und summiert nur.
Alle Analysewerte (Residuen-Statistiken, QQ-Punkte, Dezile) entstehen hier.

Ändert sich das Modell, bleibt der Vertrag gleich: Solange die Pflichtspalten geliefert
werden, zeigt das Dashboard die neuen Zahlen ohne Codeänderung.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

SCHEMA_VERSION = 1

#: Eine Zeile je Zähler und Monat im Testjahr.
REQUIRED_BENCHMARK_COLUMNS = (
    "zaehler_id",
    "kunde_id",
    "kundentyp",
    "monat",
    "vertragsleistung_kw",
    "verbrauch_kwh",
    "prognose_kwh",
    "residuum_kwh",
    "residuum_vls",
    "anomalie_score",
    "anomalie",
    "richtung",
)
#: Werden übernommen, wenn vorhanden. ``rolling_3_kwh`` ist die Baseline im Prognose-Chart.
OPTIONAL_BENCHMARK_COLUMNS = ("rolling_3_kwh", "wartung_aktiv", "produktionsplan_index")
REQUIRED_HISTORY_COLUMNS = ("zaehler_id", "monat", "verbrauch_kwh")
REQUIRED_METRIC_COLUMNS = ("Kandidat", "Typ", "RMSE (kWh)", "MAE (kWh)", "R²")

DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[2]
    / "brand/design-system/ui_kits/verbrauchs-cockpit/forecast-data.js"
)
DEFAULT_META = {
    "title": "Verbrauchs-Cockpit",
    "model": "Random Forest (VLS)",
    "model_version": "RF-VLS",
    "source": "notebooks/12_modeling_ihk_lernstory.ipynb",
    "train_period": "01/2024–12/2024",
    "benchmark_period": "01/2025–12/2025",
    "calibration_period": "11/2024–12/2024",
    "retrospective": True,
    "caveat": (
        "Das Modell ersetzt keine Abrechnungsentscheidung — "
        "es flaggt nur Untersuchungswürdiges."
    ),
}


def _require(frame: pd.DataFrame, columns, name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name}: fehlende Pflichtspalten {', '.join(missing)}")


def _clean(value, digits: int | None = None):
    """Make one value JSON-safe (NaN → None, numpy → Python)."""
    if value is None:
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.strftime("%Y-%m")
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        if not math.isfinite(float(value)):
            return None
        return round(float(value), digits) if digits is not None else float(value)
    return str(value)


def _column(series: pd.Series, digits: int | None = None) -> list:
    return [_clean(value, digits) for value in series.tolist()]


def _quantiles(values: pd.Series, qs) -> list[float]:
    return [_clean(values.quantile(q), 2) for q in qs]


def _metrics_block(metrics: pd.DataFrame, final_name: str | None) -> list[dict]:
    _require(metrics, REQUIRED_METRIC_COLUMNS, "metrics")
    rows = []
    for row in metrics.to_dict("records"):
        rows.append({
            "kandidat": str(row["Kandidat"]),
            "typ": str(row["Typ"]),
            "final": row["Kandidat"] == final_name,
            "cv_rmse": _clean(row.get("CV-RMSE (kWh)"), 1),
            "rmse": _clean(row["RMSE (kWh)"], 1),
            "mae": _clean(row["MAE (kWh)"], 1),
            "r2": _clean(row["R²"], 4),
        })
    return sorted(rows, key=lambda item: item["rmse"] if item["rmse"] is not None else 1e18)


def _residual_block(
    benchmark: pd.DataFrame,
    calibration_residuals: pd.Series,
    qq_points: int = 199,
) -> dict:
    residual = benchmark["residuum_vls"].astype(float)
    forecast_scaled = benchmark["prognose_kwh"] / benchmark["vertragsleistung_kw"]

    # QQ-Plot: standardisierte Testresiduen gegen Normalverteilungs-Quantile.
    standardized = (residual - residual.mean()) / residual.std(ddof=1)
    probabilities = (np.arange(1, qq_points + 1) - 0.5) / qq_points
    normal = NormalDist()
    qq = {
        "theoretisch": [round(normal.inv_cdf(p), 4) for p in probabilities],
        "beobachtet": [_clean(v, 4) for v in np.quantile(standardized.dropna(), probabilities)],
    }

    deciles = []
    decile_index = pd.qcut(forecast_scaled, 10, labels=False, duplicates="drop")
    for decile, group in residual.groupby(decile_index):
        deciles.append({
            "dezil": int(decile) + 1,
            "prognose": _clean(forecast_scaled[group.index].median(), 2),
            "mittel": _clean(group.mean(), 2),
            "p10": _clean(group.quantile(0.10), 2),
            "p90": _clean(group.quantile(0.90), 2),
            "n": int(len(group)),
        })

    monthly = []
    for month, group in benchmark.groupby("monat"):
        values = group["residuum_vls"]
        monthly.append({
            "monat": _clean(pd.Timestamp(month)),
            "mittel": _clean(values.mean(), 2),
            "median": _clean(values.median(), 2),
            "p05": _clean(values.quantile(0.05), 2),
            "p95": _clean(values.quantile(0.95), 2),
            "hinweise": int(group["anomalie"].sum()),
        })

    by_type = []
    for segment, group in benchmark.groupby("kundentyp", observed=True):
        values = group["residuum_vls"]
        q05, q25, q50, q75, q95 = _quantiles(values, (0.05, 0.25, 0.5, 0.75, 0.95))
        by_type.append({
            "kundentyp": str(segment), "n": int(len(values)), "mittel": _clean(values.mean(), 2),
            "q05": q05, "q25": q25, "median": q50, "q75": q75, "q95": q95,
        })

    return {
        "kalibrierung": _column(pd.Series(calibration_residuals, dtype=float), 2),
        "qq": qq,
        "dezile": deciles,
        "monate": monthly,
        "kundentypen": by_type,
        "spearman_abs_prognose": _clean(
            forecast_scaled.corr(residual.abs(), method="spearman"), 3
        ),
    }


def build_payload(
    benchmark: pd.DataFrame,
    calibration_residuals,
    metrics: pd.DataFrame,
    threshold: float,
    *,
    history: pd.DataFrame | None = None,
    importance: pd.DataFrame | None = None,
    sensitivity: pd.DataFrame | None = None,
    final_name: str | None = None,
    threshold_quantile: float | None = None,
    threshold_unit: str = "VLS-h",
    meta: dict | None = None,
) -> dict:
    """Assemble the dashboard payload from notebook result frames.

    ``benchmark``: eine Zeile je Zähler und Monat im Testjahr, mindestens
    :data:`REQUIRED_BENCHMARK_COLUMNS`. ``calibration_residuals``: die Residuen,
    aus denen die Schwelle kalibriert wurde. ``metrics``: Modellvergleich mit
    :data:`REQUIRED_METRIC_COLUMNS`, optional ``CV-RMSE (kWh)``.
    ``importance`` (``Featuregruppe``, ``RMSE-Anstieg (kWh)``) und ``sensitivity``
    (``Perzentil``, ``Schwelle (VLS-h)``, ``Hinweise 2025``, ``Hinweise je Monat``)
    sind optional; fehlen sie, zeigt das Dashboard einen leeren Zustand.
    """
    _require(benchmark, REQUIRED_BENCHMARK_COLUMNS, "benchmark")
    frame = benchmark.copy()
    frame["monat"] = pd.to_datetime(frame["monat"])
    frame = frame.sort_values(["monat", "zaehler_id"]).reset_index(drop=True)
    if frame.duplicated(["zaehler_id", "monat"]).any():
        raise ValueError("benchmark: Zähler und Monat müssen eindeutig sein.")

    columns = [*REQUIRED_BENCHMARK_COLUMNS]
    columns += [column for column in OPTIONAL_BENCHMARK_COLUMNS if column in frame.columns]
    digits = {
        "vertragsleistung_kw": 1, "verbrauch_kwh": 0, "prognose_kwh": 0, "residuum_kwh": 0,
        "residuum_vls": 2, "anomalie_score": 3, "rolling_3_kwh": 0,
        "produktionsplan_index": 3,
    }
    rows = {column: _column(frame[column], digits.get(column)) for column in columns}
    rows["anomalie"] = [bool(value) for value in frame["anomalie"]]
    if "wartung_aktiv" in rows:
        rows["wartung_aktiv"] = [bool(value) for value in frame["wartung_aktiv"]]

    history_block = None
    if history is not None:
        _require(history, REQUIRED_HISTORY_COLUMNS, "history")
        past = history.copy()
        past["monat"] = pd.to_datetime(past["monat"])
        past = past[past["monat"].lt(frame["monat"].min())].sort_values(["zaehler_id", "monat"])
        history_block = {
            "zaehler_id": _column(past["zaehler_id"]),
            "monat": _column(past["monat"]),
            "verbrauch_kwh": _column(past["verbrauch_kwh"], 0),
        }

    importance_block = None
    if importance is not None:
        ordered = importance.sort_values("RMSE-Anstieg (kWh)", ascending=False)
        importance_block = [
            {"gruppe": str(row["Featuregruppe"]), "rmse_anstieg": _clean(row["RMSE-Anstieg (kWh)"], 1)}
            for row in ordered.to_dict("records")
        ]

    sensitivity_block = None
    if sensitivity is not None:
        sensitivity_block = [
            {
                "perzentil": _clean(row["Perzentil"], 2),
                "schwelle": _clean(row["Schwelle (VLS-h)"], 2),
                "hinweise": int(row["Hinweise 2025"]),
                "je_monat": _clean(row["Hinweise je Monat"], 2),
                "gewaehlt": threshold_quantile is not None
                and math.isclose(row["Perzentil"], threshold_quantile * 100),
            }
            for row in sensitivity.to_dict("records")
        ]

    months = sorted(frame["monat"].unique())
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            **DEFAULT_META,
            **(meta or {}),
            "as_of": pd.Timestamp(months[-1]).to_period("M").end_time.strftime("%d.%m.%Y"),
            "generated_at": datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC"),
        },
        "threshold": {
            "wert": _clean(threshold, 2),
            "einheit": threshold_unit,
            "quantil": threshold_quantile,
            "n_kalibrierung": int(len(calibration_residuals)),
            "regel": "|Residuum| ≥ Schwelle",
            "residuum": "(Ist − Prognose) ÷ Vertragsleistung",
        },
        "months": [pd.Timestamp(month).strftime("%Y-%m") for month in months],
        "metrics": _metrics_block(metrics, final_name),
        "importance": importance_block,
        "sensitivity": sensitivity_block,
        "rows": rows,
        "history": history_block,
        "residuals": _residual_block(frame, calibration_residuals),
    }


def write_payload(payload: dict, path: str | Path = DEFAULT_OUTPUT) -> Path:
    """Write ``forecast-data.js`` and a sibling ``.json`` file; return the JS path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    path.write_text(
        "/* Generated by energy_analytics.dashboard_export. Do not edit. */\n"
        f"window.SWWForecastData = {text};\n",
        encoding="utf-8",
    )
    path.with_suffix(".json").write_text(text, encoding="utf-8")
    return path
