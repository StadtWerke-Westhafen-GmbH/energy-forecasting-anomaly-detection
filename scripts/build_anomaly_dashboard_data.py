"""Build the interactive anomaly-dashboard data from the verified IHK model path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "modellierung_basis_bis_3_monate.csv"
CUSTOMER_SOURCE = ROOT / "data" / "raw" / "260916_verbrauch_bereinigt.csv"
DESTINATION = (
    ROOT
    / "brand"
    / "design-system"
    / "ui_kits"
    / "energie-cockpit"
    / "anomaly-data.js"
)
RANDOM_STATE = 42
DEFAULT_QUANTILE = 0.99
THRESHOLD_QUANTILES = (0.95, 0.975, 0.99, 0.995)
NUM_FEATURES = [
    "monat_idx",
    "arbeitstage",
    "feiertage_im_monat",
    "heizgradtage",
    "produktionsplan_index",
    "wartung_aktiv",
    "vormonat_vls",
    "letzte_3_monate_vls",
]
CAT_FEATURES = ["kundentyp"]
X_COLUMNS = [*NUM_FEATURES, *CAT_FEATURES, "vertragsleistung_kw"]


def _round(value: float | int, digits: int = 4) -> float:
    return round(float(value), digits)


def _optional_round(value: float | int, digits: int = 2) -> float | None:
    return None if pd.isna(value) else _round(value, digits)


def _rmse(actual, predicted) -> float:
    return float(mean_squared_error(actual, predicted) ** 0.5)


def _customer_mapping() -> pd.Series:
    source = pd.read_csv(CUSTOMER_SOURCE, usecols=["zaehler_id", "kunde_id"])
    if source.groupby("zaehler_id", observed=True)["kunde_id"].nunique().max() != 1:
        raise ValueError("Die Kunden-ID ist nicht eindeutig einem Zähler zugeordnet.")
    return source.drop_duplicates("zaehler_id").set_index("zaehler_id")["kunde_id"]


def _prepare() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = pd.read_csv(SOURCE, parse_dates=["monat"])
    expected = [
        "zaehler_id", "monat", "jahr", "split", "vollaststunden",
        "verbrauch_kwh", "vertragsleistung_kw", "kundentyp", "monat_idx",
        "arbeitstage", "feiertage_im_monat", "heizgradtage",
        "produktionsplan_index", "wartung_aktiv", "vormonat_vls",
        "letzte_3_monate_vls", "vorjahr_vls", "anomalie", "unmoeglich",
        "ziel_rekonstruiert",
    ]
    if frame.columns.tolist() != expected:
        raise ValueError("Das Schema der Modellierungsbasis hat sich geändert.")
    if frame.duplicated(["zaehler_id", "monat"]).any():
        raise ValueError("Zähler und Monat müssen eindeutig sein.")
    if len(frame) != 16_800 or frame["zaehler_id"].nunique() != 700:
        raise ValueError("Erwartet werden 16.800 Beobachtungen und 700 Zähler.")
    if not np.allclose(
        frame["vollaststunden"],
        frame["verbrauch_kwh"] / frame["vertragsleistung_kw"],
    ):
        raise ValueError("Vollaststunden und Rückrechnung widersprechen sich.")

    frame = frame.sort_values(["monat", "zaehler_id"]).reset_index(drop=True)
    frame["wartung_aktiv"] = frame["wartung_aktiv"].astype(int)
    frame["kunde_id"] = frame["zaehler_id"].map(_customer_mapping())
    if frame["kunde_id"].isna().any():
        raise ValueError("Für mindestens einen Zähler fehlt die Kundenanzeige.")

    development = frame[
        frame["split"].eq("train") & ~frame["ziel_rekonstruiert"]
    ].copy()
    benchmark = frame[
        frame["split"].eq("test") & ~frame["ziel_rekonstruiert"]
    ].copy()
    calibration = development[development["monat"].dt.month.ge(11)].copy()
    if len(development) != 8_389 or len(calibration) != 1_397 or len(benchmark) != 8_398:
        raise ValueError("Die freigegebenen Entwicklungs- und Testmengen haben sich geändert.")
    return frame, development, benchmark, calibration


def _estimator() -> Pipeline:
    numeric = Pipeline(
        [
            (
                "impute",
                SimpleImputer(
                    strategy="median",
                    add_indicator=True,
                    keep_empty_features=True,
                ),
            )
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessor = ColumnTransformer(
        [("num", numeric, NUM_FEATURES), ("cat", categorical, CAT_FEATURES)],
        sparse_threshold=0.0,
    )
    return Pipeline(
        [
            ("pre", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=300,
                    max_features=0.7,
                    max_depth=8,
                    min_samples_leaf=5,
                    n_jobs=-1,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def _predict(estimator: Pipeline, frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    predicted_vls = np.clip(estimator.predict(frame[X_COLUMNS]), 0, None)
    predicted_kwh = predicted_vls * frame["vertragsleistung_kw"].to_numpy(float)
    return predicted_vls, predicted_kwh


def _score(frame: pd.DataFrame) -> pd.DataFrame:
    scored = frame.copy()
    scored["residuum_vls"] = scored["vollaststunden"] - scored["prognose_vls"]
    scored["abs_residuum_vls"] = scored["residuum_vls"].abs()
    scored["abweichung_kwh"] = scored["verbrauch_kwh"] - scored["prognose_kwh"]
    scored["impact_abs_kwh"] = scored["abweichung_kwh"].abs()
    scored["abweichung_prozent"] = (
        scored["abweichung_kwh"] / scored["prognose_kwh"].clip(lower=1) * 100
    )
    scored["richtung_code"] = np.where(scored["residuum_vls"].ge(0), "hoch", "niedrig")
    scored["richtung"] = np.where(
        scored["residuum_vls"].ge(0),
        "ungewöhnlich hoch",
        "ungewöhnlich niedrig",
    )
    return scored


def _model_results():
    frame, development, benchmark, calibration = _prepare()
    estimator = _estimator()

    calibration_parts = []
    for month in sorted(calibration["monat"].unique()):
        training = development[development["monat"].lt(month)]
        holdout = development[development["monat"].eq(month)].copy()
        fitted = clone(estimator).fit(training[X_COLUMNS], training["vollaststunden"])
        holdout["prognose_vls"], holdout["prognose_kwh"] = _predict(fitted, holdout)
        calibration_parts.append(holdout)
    calibration_scored = _score(pd.concat(calibration_parts, ignore_index=True))

    final_model = clone(estimator).fit(development[X_COLUMNS], development["vollaststunden"])
    benchmark = benchmark.copy()
    benchmark["prognose_vls"], benchmark["prognose_kwh"] = _predict(final_model, benchmark)
    benchmark_scored = _score(benchmark)
    return frame, calibration_scored, benchmark_scored


def _threshold_options(calibration: pd.DataFrame, benchmark: pd.DataFrame) -> list[dict]:
    options = []
    for quantile in THRESHOLD_QUANTILES:
        threshold = float(calibration["abs_residuum_vls"].quantile(quantile))
        alerts = benchmark[benchmark["abs_residuum_vls"].ge(threshold)]
        options.append(
            {
                "quantile": quantile,
                "percentile": quantile * 100,
                "threshold_vls": _round(threshold, 4),
                "alerts": int(len(alerts)),
                "alerts_per_month": _round(len(alerts) / 12, 4),
                "meters_affected": int(alerts["zaehler_id"].nunique()),
                "high": int(alerts["richtung_code"].eq("hoch").sum()),
                "low": int(alerts["richtung_code"].eq("niedrig").sum()),
            }
        )
    return options


def _observation_rows(benchmark: pd.DataFrame, default_threshold: float) -> list[dict]:
    ranked = benchmark.sort_values(
        ["abs_residuum_vls", "impact_abs_kwh"], ascending=[False, False]
    ).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)
    rows = []
    for row in ranked.itertuples():
        rows.append(
            {
                "alert_id": f"{row.zaehler_id}-{row.monat:%Y-%m}",
                "rank": int(row.rank),
                "zaehler_id": row.zaehler_id,
                "kunde_id": row.kunde_id,
                "kundentyp": row.kundentyp,
                "month_key": row.monat.strftime("%Y-%m"),
                "month_label": row.monat.strftime("%m/%Y"),
                "vertragsleistung_kw": _round(row.vertragsleistung_kw, 2),
                "actual_kwh": _round(row.verbrauch_kwh, 2),
                "forecast_kwh": _round(row.prognose_kwh, 2),
                "actual_vls": _round(row.vollaststunden, 4),
                "forecast_vls": _round(row.prognose_vls, 4),
                "residual_vls": _round(row.residuum_vls, 4),
                "abs_residual_vls": _round(row.abs_residuum_vls, 4),
                "residual_kwh": _round(row.abweichung_kwh, 2),
                "impact_abs_kwh": _round(row.impact_abs_kwh, 2),
                "deviation_pct": _round(row.abweichung_prozent, 2),
                "score": _round(row.abs_residuum_vls / default_threshold, 4),
                "direction": row.richtung,
                "direction_code": row.richtung_code,
                "wartung_aktiv": bool(row.wartung_aktiv),
                "produktionsplan_index": _optional_round(row.produktionsplan_index, 3),
                "arbeitstage": int(row.arbeitstage),
                "feiertage": int(row.feiertage_im_monat),
                "dq_capacity": bool(row.unmoeglich),
                "eda_reference": bool(row.anomalie),
            }
        )
    return rows


def _enrich_alerts(rows: list[dict], threshold: float) -> list[dict]:
    selected = [row.copy() for row in rows if row["abs_residual_vls"] >= threshold]
    counts: dict[str, int] = {}
    for row in selected:
        counts[row["zaehler_id"]] = counts.get(row["zaehler_id"], 0) + 1
    for rank, row in enumerate(selected, start=1):
        row["rank"] = rank
        row["score"] = _round(row["abs_residual_vls"] / threshold, 4)
        row["repeat_alert"] = counts[row["zaehler_id"]] > 1
        row["meter_alert_count"] = counts[row["zaehler_id"]]
    return selected


def _series_for_meter(
    meter_id: str,
    frame: pd.DataFrame,
    calibration: pd.DataFrame,
    benchmark: pd.DataFrame,
    default_threshold: float,
) -> list[dict]:
    base = frame[frame["zaehler_id"].eq(meter_id)].copy()
    base["prognose_kwh"] = np.nan
    base["prognose_vls"] = np.nan
    base["residuum_vls"] = np.nan
    base["phase"] = "Historie"

    for scored, phase in ((calibration, "Kalibrierung"), (benchmark, "Benchmark")):
        subset = scored[scored["zaehler_id"].eq(meter_id)]
        for row in subset.itertuples():
            mask = base["monat"].eq(row.monat)
            base.loc[mask, "prognose_kwh"] = row.prognose_kwh
            base.loc[mask, "prognose_vls"] = row.prognose_vls
            base.loc[mask, "residuum_vls"] = row.residuum_vls
            base.loc[mask, "phase"] = phase

    return [
        {
            "month_key": row.monat.strftime("%Y-%m"),
            "month_label": row.monat.strftime("%m/%Y"),
            "actual_kwh": _round(row.verbrauch_kwh, 2),
            "forecast_kwh": _optional_round(row.prognose_kwh, 2),
            "actual_vls": _round(row.vollaststunden, 4),
            "forecast_vls": _optional_round(row.prognose_vls, 4),
            "residual_vls": _optional_round(row.residuum_vls, 4),
            "score": (
                None
                if pd.isna(row.residuum_vls)
                else _round(abs(row.residuum_vls) / default_threshold, 4)
            ),
            "is_alert": (
                False
                if pd.isna(row.residuum_vls)
                else bool(abs(row.residuum_vls) >= default_threshold)
            ),
            "phase": row.phase,
        }
        for row in base.sort_values("monat").itertuples()
    ]


def build_payload() -> dict:
    frame, calibration, benchmark = _model_results()
    threshold_options = _threshold_options(calibration, benchmark)
    default_option = next(
        option for option in threshold_options if option["quantile"] == DEFAULT_QUANTILE
    )
    default_threshold = float(default_option["threshold_vls"])
    observations = _observation_rows(benchmark, default_threshold)
    alerts = _enrich_alerts(observations, default_threshold)

    lowest_threshold = threshold_options[0]["threshold_vls"]
    affected_meters = sorted(
        {
            row["zaehler_id"]
            for row in observations
            if row["abs_residual_vls"] >= lowest_threshold
        }
    )
    meters = {}
    for meter_id in affected_meters:
        first = frame[frame["zaehler_id"].eq(meter_id)].iloc[0]
        meters[meter_id] = {
            "zaehler_id": meter_id,
            "kunde_id": first["kunde_id"],
            "kundentyp": first["kundentyp"],
            "vertragsleistung_kw": _round(first["vertragsleistung_kw"], 2),
            "series": _series_for_meter(
                meter_id, frame, calibration, benchmark, default_threshold
            ),
        }

    monthly = []
    for month in sorted(benchmark["monat"].unique()):
        month_key = pd.Timestamp(month).strftime("%Y-%m")
        month_rows = [row for row in alerts if row["month_key"] == month_key]
        monthly.append(
            {
                "month_key": month_key,
                "month_label": pd.Timestamp(month).strftime("%m/%Y"),
                "alerts": len(month_rows),
                "high": sum(row["direction_code"] == "hoch" for row in month_rows),
                "low": sum(row["direction_code"] == "niedrig" for row in month_rows),
                "dq_overlap": sum(row["dq_capacity"] for row in month_rows),
            }
        )

    segments = []
    for segment, group in benchmark.groupby("kundentyp", observed=True):
        segment_alerts = [row for row in alerts if row["kundentyp"] == segment]
        segments.append(
            {
                "kundentyp": segment,
                "observations": int(len(group)),
                "alerts": len(segment_alerts),
                "rate_pct": _round(len(segment_alerts) / len(group) * 100, 4),
            }
        )

    benchmark_rmse = _rmse(benchmark["verbrauch_kwh"], benchmark["prognose_kwh"])
    benchmark_mae = float(
        mean_absolute_error(benchmark["verbrauch_kwh"], benchmark["prognose_kwh"])
    )
    benchmark_r2 = float(r2_score(benchmark["verbrauch_kwh"], benchmark["prognose_kwh"]))
    dq_total = int(benchmark["unmoeglich"].sum())
    dq_overlap = sum(row["dq_capacity"] for row in alerts)

    payload = {
        "meta": {
            "title": "Anomalieprüfung 2025",
            "source": "data/processed/modellierung_basis_bis_3_monate.csv",
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "display_mapping_source": "data/raw/260916_verbrauch_bereinigt.csv",
            "display_mapping_sha256": hashlib.sha256(CUSTOMER_SOURCE.read_bytes()).hexdigest(),
            "data_period": "01/2024–12/2025",
            "benchmark_period": "01/2025–12/2025",
            "calibration_period": "11/2024–12/2024",
            "as_of": "31.12.2025",
            "model": "Random-Forest-Regressor auf Vollaststunden",
            "model_version": "RF-VLS 2.0",
            "benchmark_rmse_kwh": _round(benchmark_rmse, 4),
            "benchmark_mae_kwh": _round(benchmark_mae, 4),
            "benchmark_r2": _round(benchmark_r2, 6),
            "threshold_quantile": DEFAULT_QUANTILE,
            "threshold_vls": default_threshold,
            "threshold_score": default_threshold,
            "calibration_observations": int(len(calibration)),
            "labels_available": False,
            "retrospective": True,
            "caveat": (
                "Das Modell ersetzt keine Abrechnungsentscheidung — "
                "es flaggt nur Untersuchungswürdiges."
            ),
        },
        "summary": {
            "observations": int(len(benchmark)),
            "meters_total": int(benchmark["zaehler_id"].nunique()),
            "alerts_total": len(alerts),
            "meters_affected": len({row["zaehler_id"] for row in alerts}),
            "alerts_per_month": _round(len(alerts) / 12, 4),
            "alert_rate_pct": _round(len(alerts) / len(benchmark) * 100, 4),
            "high": sum(row["direction_code"] == "hoch" for row in alerts),
            "low": sum(row["direction_code"] == "niedrig" for row in alerts),
            "dq_flags_total": dq_total,
            "dq_overlap": dq_overlap,
        },
        "threshold_options": threshold_options,
        "monthly": monthly,
        "segments": segments,
        "observations": observations,
        "alerts": alerts,
        "meters": meters,
        "review_options": {
            "workflow": [
                {"value": "nicht_bewertet", "label": "Nicht bewertet"},
                {"value": "in_pruefung", "label": "In Prüfung"},
                {"value": "rueckfrage", "label": "Rückfrage offen"},
                {"value": "abgeschlossen", "label": "Bewertung abgeschlossen"},
            ],
            "tri_state": [
                {"value": "unklar", "label": "Unklar"},
                {"value": "ja", "label": "Ja"},
                {"value": "nein", "label": "Nein"},
            ],
            "causes": [
                "Noch ungeklärt",
                "Geplante Wartung",
                "Ungeplanter Stillstand",
                "Produktionsänderung",
                "Mess- oder Datenfehler",
                "Kunden- oder Betriebsänderung",
                "Modellabweichung",
                "Sonstige Ursache",
            ],
            "actions": [
                "Noch offen",
                "Kein Handlungsbedarf",
                "Rückfrage stellen",
                "Messwesen prüfen",
                "Technische Prüfung",
                "Wartungs- oder Serviceticket",
                "Datenkorrektur",
            ],
        },
    }
    if default_option["alerts"] != len(alerts):
        raise AssertionError("Standardszenario und exportierte Alertliste widersprechen sich.")
    if not all(
        option["alerts"] == sum(
            row["abs_residual_vls"] >= option["threshold_vls"]
            for row in observations
        )
        for option in threshold_options
    ):
        raise AssertionError("Die Szenariozahlen sind nicht aus den Beobachtungen reproduzierbar.")
    return payload


def render(payload: dict) -> str:
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return (
        "/* Generated by scripts/build_anomaly_dashboard_data.py. Do not edit. */\n"
        f"window.SWWAnomalyData = {serialized};\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when the generated file is stale")
    args = parser.parse_args()
    content = render(build_payload())
    if args.check:
        if not DESTINATION.exists() or DESTINATION.read_text(encoding="utf-8") != content:
            raise SystemExit(f"Generated dashboard data is stale: {DESTINATION}")
        print(f"Dashboard data is current: {DESTINATION}")
        return
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(content, encoding="utf-8", newline="\n")
    print(DESTINATION)


if __name__ == "__main__":
    main()
