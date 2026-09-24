"""Export the exact calibration residuals used by the anomaly dashboard.

The export is intentionally based on ``_model_results`` from the dashboard data
builder so that notebook, dashboard and explanatory table cannot silently drift
apart.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from build_anomaly_dashboard_data import _model_results


ROOT = Path(__file__).resolve().parents[1]
CSV_DESTINATION = ROOT / "data" / "processed" / "kalibrierungsfehler_vls_sortiert.csv"
SUMMARY_DESTINATION = (
    ROOT / "data" / "processed" / "kalibrierungsfehler_vls_perzentile.json"
)
QUANTILES = (0.95, 0.975, 0.99, 0.995)


def build_exports() -> tuple[Path, Path]:
    """Recalculate and export all 1,397 time-forward calibration errors."""

    _, calibration, _ = _model_results()
    thresholds = {
        quantile: float(calibration["abs_residuum_vls"].quantile(quantile))
        for quantile in QUANTILES
    }

    columns = [
        "zaehler_id",
        "monat",
        "kundentyp",
        "vertragsleistung_kw",
        "vollaststunden",
        "prognose_vls",
        "residuum_vls",
        "abs_residuum_vls",
        "verbrauch_kwh",
        "prognose_kwh",
        "abweichung_kwh",
    ]
    exported = calibration[columns].sort_values(
        ["abs_residuum_vls", "monat", "zaehler_id"], kind="stable"
    ).reset_index(drop=True)
    exported.insert(0, "rang_aufsteigend", np.arange(1, len(exported) + 1))
    exported.insert(
        1,
        "empirischer_anteil_bis_hier",
        exported["rang_aufsteigend"] / len(exported),
    )
    for quantile, threshold in thresholds.items():
        label = str(quantile * 100).replace(".", "_").replace("_0", "")
        exported[f"ab_p{label}"] = exported["abs_residuum_vls"].ge(threshold)

    exported["monat"] = exported["monat"].dt.strftime("%Y-%m")
    exported.to_csv(CSV_DESTINATION, index=False, encoding="utf-8-sig")

    ordered = exported["abs_residuum_vls"]
    percentile_details = []
    for quantile, threshold in thresholds.items():
        position = (len(ordered) - 1) * quantile
        lower_index = math.floor(position)
        upper_index = math.ceil(position)
        percentile_details.append(
            {
                "quantile": quantile,
                "percentile": quantile * 100,
                "zero_based_position": position,
                "lower_rank_one_based": lower_index + 1,
                "lower_value_vls_hours": float(ordered.iloc[lower_index]),
                "upper_rank_one_based": upper_index + 1,
                "upper_value_vls_hours": float(ordered.iloc[upper_index]),
                "linear_interpolation_weight_upper": position - lower_index,
                "threshold_vls_hours": threshold,
                "calibration_values_at_or_above_threshold": int(
                    ordered.ge(threshold).sum()
                ),
            }
        )

    summary = {
        "source": "data/processed/modellierung_basis_bis_3_monate.csv",
        "model_path": "scripts/build_anomaly_dashboard_data.py::_model_results",
        "calibration_period": "2024-11 through 2024-12",
        "observations": int(len(ordered)),
        "sort": "ascending by absolute VLS residual",
        "residual_formula": "(verbrauch_kwh - prognose_kwh) / vertragsleistung_kw",
        "absolute_residual_formula": "abs(residuum_vls)",
        "quantile_method": "pandas Series.quantile default: linear interpolation",
        "minimum_abs_residual_vls_hours": float(ordered.min()),
        "median_abs_residual_vls_hours": float(ordered.median()),
        "mean_abs_residual_vls_hours": float(ordered.mean()),
        "maximum_abs_residual_vls_hours": float(ordered.max()),
        "percentiles": percentile_details,
    }
    SUMMARY_DESTINATION.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return CSV_DESTINATION, SUMMARY_DESTINATION


if __name__ == "__main__":
    csv_path, summary_path = build_exports()
    print(f"CSV: {csv_path}")
    print(f"Summary: {summary_path}")
