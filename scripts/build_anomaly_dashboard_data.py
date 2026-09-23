"""Build the static 2025 anomaly-dashboard data from the reproducible RF-VLS path."""

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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "260916_verbrauch_bereinigt.csv"
DESTINATION = (
    ROOT
    / "brand"
    / "design-system"
    / "ui_kits"
    / "energie-cockpit"
    / "anomaly-data.js"
)
RANDOM_STATE = 42
ANOMALY_QUANTILE = 0.99
NUM_FEATURES = [
    "log_vertragsleistung_kw",
    "arbeitstage",
    "feiertage_im_monat",
    "lag_1_vls",
    "rolling_3_vls",
    "log_lag_1_kwh",
    "log_rolling_3_kwh",
    "monat_sin",
    "monat_cos",
]
CAT_FEATURES = ["kundentyp"]
X_COLUMNS = ["vertragsleistung_kw", *NUM_FEATURES, *CAT_FEATURES]


def _round(value: float | int, digits: int = 4) -> float:
    return round(float(value), digits)


def _optional_round(value: float | int, digits: int = 2) -> float | None:
    return None if pd.isna(value) else _round(value, digits)


def _wape(actual, predicted) -> float:
    actual = np.asarray(actual, dtype=float)
    predicted = np.clip(np.asarray(predicted, dtype=float), 0, None)
    valid = np.isfinite(actual) & np.isfinite(predicted)
    return float(np.abs(actual[valid] - predicted[valid]).sum() / np.abs(actual[valid]).sum() * 100)


def _robust_scale(values) -> float:
    values = np.asarray(values, dtype=float)
    center = np.median(values)
    mad = np.median(np.abs(values - center))
    return max(float(1.4826 * mad), 1e-6)


def _prepare() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = pd.read_csv(SOURCE, parse_dates=["monat"])
    expected = {
        "zaehler_id",
        "kunde_id",
        "kundentyp",
        "vertragsleistung_kw",
        "monat",
        "monat_idx",
        "arbeitstage",
        "feiertage_im_monat",
        "mittlere_temperatur_c",
        "heiztage",
        "produktionsplan_index",
        "wartung_aktiv",
        "vormonat_verbrauch_kwh",
        "letzte_3_monate_durchschnitt_kwh",
        "vorjahr_monat_verbrauch_kwh",
        "verbrauch_kwh",
    }
    if set(frame.columns) != expected:
        raise ValueError("Das Quelldatenschema hat sich geändert.")
    if frame.duplicated(["zaehler_id", "monat"]).any():
        raise ValueError("Zähler und Monat müssen eindeutig sein.")
    if not frame["vertragsleistung_kw"].gt(0).all() or not frame["verbrauch_kwh"].gt(0).all():
        raise ValueError("Leistung und Verbrauch müssen positiv sein.")

    frame = frame.sort_values(["zaehler_id", "monat"]).reset_index(drop=True)
    frame["wartung_aktiv"] = frame["wartung_aktiv"].astype(int)
    frame["stunden_im_monat"] = frame["monat"].dt.days_in_month * 24
    frame["dq_vertragsleistung"] = (
        frame["verbrauch_kwh"]
        > frame["vertragsleistung_kw"] * frame["stunden_im_monat"]
    )

    history = frame.groupby("zaehler_id", sort=False)["verbrauch_kwh"]
    frame["lag_1_kwh"] = history.shift(1)
    frame["rolling_3_kwh"] = history.transform(
        lambda values: values.shift(1).rolling(3, min_periods=3).mean()
    )
    frame["ziel_vls"] = frame["verbrauch_kwh"] / frame["vertragsleistung_kw"]
    frame["lag_1_vls"] = frame["lag_1_kwh"] / frame["vertragsleistung_kw"]
    frame["rolling_3_vls"] = frame["rolling_3_kwh"] / frame["vertragsleistung_kw"]
    frame["log_lag_1_kwh"] = np.log1p(frame["lag_1_kwh"])
    frame["log_rolling_3_kwh"] = np.log1p(frame["rolling_3_kwh"])
    frame["monat_sin"] = np.sin(2 * np.pi * frame["monat"].dt.month / 12)
    frame["monat_cos"] = np.cos(2 * np.pi * frame["monat"].dt.month / 12)
    frame["log_vertragsleistung_kw"] = np.log1p(frame["vertragsleistung_kw"])

    development = (
        frame[frame["monat"].dt.year.eq(2024)]
        .sort_values(["monat", "zaehler_id"])
        .reset_index(drop=True)
    )
    benchmark = (
        frame[frame["monat"].dt.year.eq(2025)]
        .sort_values(["monat", "zaehler_id"])
        .reset_index(drop=True)
    )
    calibration = development[development["monat"].dt.month.ge(11)].copy()
    if len(frame) != 16_800 or frame["zaehler_id"].nunique() != 700:
        raise ValueError("Erwartet werden 16.800 Beobachtungen und 700 Zähler.")
    return frame, development, benchmark, calibration


def _estimator() -> Pipeline:
    category_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            (
                "num",
                SimpleImputer(strategy="median", keep_empty_features=True),
                NUM_FEATURES,
            ),
            ("cat", category_pipe, CAT_FEATURES),
        ],
        sparse_threshold=0.0,
    )
    return Pipeline(
        [
            ("pre", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=180,
                    max_features=0.7,
                    max_depth=8,
                    min_samples_leaf=20,
                    n_jobs=1,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def _predict_kwh(estimator: Pipeline, frame: pd.DataFrame) -> np.ndarray:
    predicted_vls = np.clip(estimator.predict(frame[X_COLUMNS]), 0, None)
    return predicted_vls * frame["vertragsleistung_kw"].to_numpy(float)


def _score(
    frame: pd.DataFrame,
    residual_reference: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    scored = frame.copy()
    scored["residuum_log"] = np.log1p(scored["verbrauch_kwh"]) - np.log1p(
        scored["prognose_kwh"].clip(lower=0)
    )
    scored = scored.join(residual_reference, on="kundentyp")
    scored["score_signiert"] = (
        scored["residuum_log"] - scored["mitte"]
    ) / scored["skala"]
    scored["anomalie_score"] = scored["score_signiert"].abs()
    scored["anomalie"] = scored["anomalie_score"].ge(threshold)
    scored["richtung_code"] = np.where(scored["score_signiert"].ge(0), "hoch", "niedrig")
    scored["richtung"] = np.where(
        scored["score_signiert"].ge(0),
        "ungewöhnlich hoch",
        "ungewöhnlich niedrig",
    )
    scored["abweichung_kwh"] = scored["verbrauch_kwh"] - scored["prognose_kwh"]
    scored["abweichung_prozent"] = (
        scored["abweichung_kwh"] / scored["prognose_kwh"].clip(lower=1) * 100
    )
    return scored


def _model_results():
    frame, development, benchmark, calibration = _prepare()
    estimator = _estimator()

    calibration_parts = []
    for month in sorted(calibration["monat"].unique()):
        training = development[development["monat"].lt(month)]
        holdout = development[development["monat"].eq(month)].copy()
        fitted = clone(estimator).fit(training[X_COLUMNS], training["ziel_vls"])
        holdout["prognose_kwh"] = _predict_kwh(fitted, holdout)
        calibration_parts.append(holdout)
    calibration_scored = pd.concat(calibration_parts, ignore_index=True)
    calibration_scored["residuum_log"] = np.log1p(
        calibration_scored["verbrauch_kwh"]
    ) - np.log1p(calibration_scored["prognose_kwh"].clip(lower=0))
    residual_reference = (
        calibration_scored.groupby("kundentyp", observed=True)["residuum_log"]
        .agg(mitte="median", skala=_robust_scale)
    )
    calibration_scored = calibration_scored.join(residual_reference, on="kundentyp")
    calibration_scored["score_signiert"] = (
        calibration_scored["residuum_log"] - calibration_scored["mitte"]
    ) / calibration_scored["skala"]
    calibration_scored["anomalie_score"] = calibration_scored["score_signiert"].abs()
    threshold = float(calibration_scored["anomalie_score"].quantile(ANOMALY_QUANTILE))
    calibration_scored["anomalie"] = calibration_scored["anomalie_score"].ge(threshold)

    final_model = clone(estimator).fit(development[X_COLUMNS], development["ziel_vls"])
    benchmark = benchmark.copy()
    benchmark["prognose_kwh"] = _predict_kwh(final_model, benchmark)
    benchmark_scored = _score(benchmark, residual_reference, threshold)
    return frame, calibration_scored, benchmark_scored, threshold


def _series_for_meter(
    meter_id: str,
    frame: pd.DataFrame,
    calibration: pd.DataFrame,
    benchmark: pd.DataFrame,
    threshold: float,
) -> list[dict]:
    base = frame[frame["zaehler_id"].eq(meter_id)].copy()
    base["prognose_kwh"] = np.nan
    base["anomalie_score"] = np.nan
    base["anomalie"] = False
    base["phase"] = "Historie"

    calibration_meter = calibration[calibration["zaehler_id"].eq(meter_id)]
    for row in calibration_meter.itertuples():
        mask = base["monat"].eq(row.monat)
        base.loc[mask, "prognose_kwh"] = row.prognose_kwh
        base.loc[mask, "anomalie_score"] = row.anomalie_score
        base.loc[mask, "anomalie"] = row.anomalie_score >= threshold
        base.loc[mask, "phase"] = "Kalibrierung"

    benchmark_meter = benchmark[benchmark["zaehler_id"].eq(meter_id)]
    for row in benchmark_meter.itertuples():
        mask = base["monat"].eq(row.monat)
        base.loc[mask, "prognose_kwh"] = row.prognose_kwh
        base.loc[mask, "anomalie_score"] = row.anomalie_score
        base.loc[mask, "anomalie"] = bool(row.anomalie)
        base.loc[mask, "phase"] = "Benchmark"

    return [
        {
            "month_key": row.monat.strftime("%Y-%m"),
            "month_label": row.monat.strftime("%m/%Y"),
            "actual_kwh": _round(row.verbrauch_kwh, 2),
            "forecast_kwh": _optional_round(row.prognose_kwh, 2),
            "score": _optional_round(row.anomalie_score, 4),
            "is_alert": bool(row.anomalie),
            "phase": row.phase,
        }
        for row in base.sort_values("monat").itertuples()
    ]


def build_payload() -> dict:
    frame, calibration, benchmark, threshold = _model_results()
    alerts = benchmark[benchmark["anomalie"]].copy()
    alerts["impact_abs_kwh"] = alerts["abweichung_kwh"].abs()
    alert_counts_by_meter = alerts["zaehler_id"].value_counts()
    alerts = alerts.sort_values(
        ["anomalie_score", "impact_abs_kwh"], ascending=[False, False]
    ).reset_index(drop=True)
    alerts["rank"] = np.arange(1, len(alerts) + 1)

    alert_rows = []
    for row in alerts.itertuples():
        alert_rows.append(
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
                "baseline_3m_kwh": _optional_round(row.rolling_3_kwh, 2),
                "residual_kwh": _round(row.abweichung_kwh, 2),
                "impact_abs_kwh": _round(row.impact_abs_kwh, 2),
                "deviation_pct": _round(row.abweichung_prozent, 2),
                "score": _round(row.anomalie_score, 4),
                "direction": row.richtung,
                "direction_code": row.richtung_code,
                "wartung_aktiv": bool(row.wartung_aktiv),
                "produktionsplan_index": _optional_round(row.produktionsplan_index, 3),
                "arbeitstage": int(row.arbeitstage),
                "feiertage": int(row.feiertage_im_monat),
                "dq_capacity": bool(row.dq_vertragsleistung),
                "repeat_alert": int(alert_counts_by_meter[row.zaehler_id]) > 1,
                "meter_alert_count": int(alert_counts_by_meter[row.zaehler_id]),
            }
        )

    affected_meters = sorted(alerts["zaehler_id"].unique())
    meters = {}
    for meter_id in affected_meters:
        first = frame[frame["zaehler_id"].eq(meter_id)].iloc[0]
        meters[meter_id] = {
            "zaehler_id": meter_id,
            "kunde_id": first["kunde_id"],
            "kundentyp": first["kundentyp"],
            "vertragsleistung_kw": _round(first["vertragsleistung_kw"], 2),
            "series": _series_for_meter(
                meter_id,
                frame,
                calibration,
                benchmark,
                threshold,
            ),
        }

    monthly = []
    for month in sorted(benchmark["monat"].unique()):
        month_rows = alerts[alerts["monat"].eq(month)]
        monthly.append(
            {
                "month_key": pd.Timestamp(month).strftime("%Y-%m"),
                "month_label": pd.Timestamp(month).strftime("%m/%Y"),
                "alerts": int(len(month_rows)),
                "high": int(month_rows["richtung_code"].eq("hoch").sum()),
                "low": int(month_rows["richtung_code"].eq("niedrig").sum()),
                "dq_overlap": int(month_rows["dq_vertragsleistung"].sum()),
            }
        )

    segments = []
    for segment, group in benchmark.groupby("kundentyp", observed=True):
        segment_alerts = alerts[alerts["kundentyp"].eq(segment)]
        segments.append(
            {
                "kundentyp": segment,
                "observations": int(len(group)),
                "alerts": int(len(segment_alerts)),
                "rate_pct": _round(len(segment_alerts) / len(group) * 100, 4),
            }
        )

    total_alerts = int(len(alerts))
    dq_total = int(benchmark["dq_vertragsleistung"].sum())
    dq_overlap = int(alerts["dq_vertragsleistung"].sum())
    high_count = int(alerts["richtung_code"].eq("hoch").sum())
    low_count = int(alerts["richtung_code"].eq("niedrig").sum())
    benchmark_wape = _wape(benchmark["verbrauch_kwh"], benchmark["prognose_kwh"])
    baseline_wape = _wape(benchmark["verbrauch_kwh"], benchmark["rolling_3_kwh"])

    payload = {
        "meta": {
            "title": "Anomalieprüfung 2025",
            "source": "data/raw/260916_verbrauch_bereinigt.csv",
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "data_period": "01/2024–12/2025",
            "benchmark_period": "01/2025–12/2025",
            "calibration_period": "11/2024–12/2024",
            "as_of": "31.12.2025",
            "model": "Random-Forest-Regressor auf Vollaststunden",
            "model_version": "RF-VLS 1.0",
            "benchmark_wape_pct": _round(benchmark_wape, 4),
            "baseline_wape_pct": _round(baseline_wape, 4),
            "threshold_quantile": ANOMALY_QUANTILE,
            "threshold_score": _round(threshold, 4),
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
            "alerts_total": total_alerts,
            "meters_affected": int(alerts["zaehler_id"].nunique()),
            "alerts_per_month": _round(total_alerts / benchmark["monat"].nunique(), 4),
            "alert_rate_pct": _round(total_alerts / len(benchmark) * 100, 4),
            "high": high_count,
            "low": low_count,
            "dq_flags_total": dq_total,
            "dq_overlap": dq_overlap,
        },
        "monthly": monthly,
        "segments": segments,
        "alerts": alert_rows,
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
    if total_alerts != 105 or len(affected_meters) != 100:
        raise AssertionError("Die freigegebene Story erwartet 105 Hinweise bei 100 Zählern.")
    if high_count != 20 or low_count != 85:
        raise AssertionError("Die Richtungsverteilung hat sich unerwartet geändert.")
    return payload


def render(payload: dict) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
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
