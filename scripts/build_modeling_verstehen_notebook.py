"""Build the SWW learning notebook for understanding the modeling end to end."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import textwrap

import nbformat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = ROOT / "notebooks" / "13_modellierung_von_grund_auf_verstehen.ipynb"
DATA_SOURCE = ROOT / "data" / "processed" / "modellierung_basis_bis_3_monate.csv"


def _dedent(source: str) -> str:
    return textwrap.dedent(source).strip() + "\n"


def markdown(cell_id: str, source: str):
    return nbformat.v4.new_markdown_cell(_dedent(source), id=cell_id)


def code(cell_id: str, source: str, *, hidden: bool = True):
    cell = nbformat.v4.new_code_cell(_dedent(source), id=cell_id)
    if hidden:
        cell.metadata["tags"] = ["hide-input"]
        cell.metadata["jupyter"] = {"source_hidden": True}
    return cell


def build_notebook(destination: Path = DEFAULT_DESTINATION) -> Path:
    source_hash = hashlib.sha256(DATA_SOURCE.read_bytes()).hexdigest()
    cells = [
        code(
            "learn-setup",
            """
            from datetime import datetime, timezone
            from html import escape
            from importlib import reload
            from importlib.util import find_spec
            from pathlib import Path
            import sys

            required = ("numpy", "pandas", "plotly", "sklearn", "IPython", "energy_analytics")
            missing = [name for name in required if find_spec(name) is None]
            if missing:
                raise RuntimeError(
                    f"Im aktiven Kernel fehlen: {', '.join(missing)}. "
                    "Bitte im Projektstamm `python -m uv sync --frozen --all-extras` "
                    "ausführen und anschließend den Kernel aus `.venv` wählen."
                )

            import numpy as np
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            from IPython.display import HTML, display

            from sklearn.base import BaseEstimator, RegressorMixin, clone
            from sklearn.compose import ColumnTransformer
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            from sklearn.model_selection import ParameterGrid
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler

            from energy_analytics.visualization import eda, theme
            from energy_analytics.visualization import notebook as ci

            BASE_DIR = next(
                (
                    folder for folder in (Path.cwd(), *Path.cwd().parents)
                    if (folder / "pyproject.toml").is_file()
                    and (folder / "brand/design-system").is_dir()
                ),
                None,
            )
            if BASE_DIR is None:
                raise FileNotFoundError("Bitte das Notebook innerhalb des Projektordners starten.")

            theme = reload(theme)
            eda = reload(eda)
            ci = reload(ci)
            DATA_PATH = BASE_DIR / "data/processed/modellierung_basis_bis_3_monate.csv"
            RANDOM_STATE = 42
            OFFICIAL_QUANTILE = 0.99
            LEARNING_QUANTILE = 0.975

            ci.aktiviere(
                logo=BASE_DIR / "brand/design-system/assets/logo-sww-emblem.png",
                quelle="data/processed/modellierung_basis_bis_3_monate.csv",
            )


            def de(value, digits=1):
                if value is None or not np.isfinite(value):
                    return "—"
                return (
                    f"{float(value):,.{digits}f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )


            def learning_css():
                t = theme.TOKENS
                return f'''
                <style>
                .learn {{font-family:{theme.FONT};color:{t["text-primary"]};}}
                .learn * {{box-sizing:border-box;}}
                .learn-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));
                  gap:12px;margin:14px 0 18px;}}
                .learn-card {{background:{t["surface-card"]};border:1px solid {t["border-default"]};
                  border-radius:{t["radius-card"]};box-shadow:{t["shadow-card"]};padding:17px;}}
                .learn-card .kicker {{display:block;color:{t["text-accent"]};font-size:10px;
                  font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:5px;}}
                .learn-card h3 {{color:{t["text-brand"]};font-size:16px;margin:0 0 7px;}}
                .learn-card p {{color:{t["text-secondary"]};font-size:13px;line-height:1.52;margin:0;}}
                .learn-formula {{background:{t["surface-brand-subtle"]};border:1px solid {t["border-brand"]};
                  border-radius:{t["radius-card"]};padding:18px;margin:14px 0;text-align:center;}}
                .learn-formula strong {{display:block;color:{t["text-brand"]};font-family:{t["font-mono"]};
                  font-size:19px;line-height:1.45;}}
                .learn-formula span {{display:block;color:{t["text-secondary"]};font-size:12px;
                  margin-top:7px;line-height:1.45;}}
                .learn-note {{background:{t["surface-sunken"]};border:1px solid {t["border-subtle"]};
                  border-radius:{t["radius-card"]};padding:15px 17px;margin:12px 0;}}
                .learn-note strong {{display:block;color:{t["text-brand"]};margin-bottom:4px;}}
                .learn-note p {{color:{t["text-secondary"]};font-size:13px;line-height:1.55;margin:0;}}
                .learn-check {{background:{t["surface-card"]};border:1px solid {t["border-default"]};
                  border-radius:{t["radius-card"]};margin:12px 0;overflow:hidden;}}
                .learn-check summary {{padding:14px 16px;color:{t["text-brand"]};font-weight:600;cursor:pointer;}}
                .learn-check .answer {{padding:0 16px 16px;color:{t["text-secondary"]};
                  font-size:13px;line-height:1.55;}}
                .learn-steps {{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));
                  gap:10px;margin:14px 0 18px;}}
                .learn-step {{background:{t["surface-card"]};border:1px solid {t["border-default"]};
                  border-radius:{t["radius-card"]};padding:15px;min-height:120px;}}
                .learn-step .nr {{display:grid;place-items:center;width:28px;height:28px;border-radius:999px;
                  background:{t["surface-brand-strong"]};color:{t["text-inverse"]};font-weight:600;
                  margin-bottom:9px;}}
                .learn-step strong {{display:block;color:{t["text-brand"]};font-size:13px;}}
                .learn-step span {{display:block;color:{t["text-secondary"]};font-size:12px;
                  line-height:1.45;margin-top:5px;}}
                .learn-table {{width:100%;border-collapse:collapse;background:{t["surface-card"]};
                  font-size:12px;margin:12px 0;}}
                .learn-table th {{background:{t["surface-brand-strong"]};color:{t["text-inverse"]};
                  padding:9px 11px;text-align:left;font-weight:500;}}
                .learn-table td {{padding:9px 11px;border-bottom:1px solid {t["border-subtle"]};
                  color:{t["text-primary"]};vertical-align:top;}}
                .learn-table tr:nth-child(even) td {{background:{t["surface-sunken"]};}}
                .learn-sentence {{background:{t["surface-card"]};border:1px solid {t["border-brand"]};
                  border-radius:{t["radius-card"]};padding:16px;margin:14px 0;color:{t["text-brand"]};
                  font-size:15px;line-height:1.55;}}
                @media(max-width:720px){{.learn-grid,.learn-steps{{grid-template-columns:1fr;}}}}
                </style>
                '''


            display(HTML(learning_css()))


            def cards(items):
                body = "".join(
                    '<article class="learn-card">'
                    f'<span class="kicker">{escape(str(kicker))}</span>'
                    f'<h3>{escape(str(title))}</h3><p>{escape(str(text))}</p></article>'
                    for kicker, title, text in items
                )
                display(HTML(f'<div class="learn learn-grid">{body}</div>'))


            def formula(expression, explanation):
                display(HTML(
                    '<div class="learn learn-formula">'
                    f'<strong>{escape(str(expression))}</strong>'
                    f'<span>{escape(str(explanation))}</span></div>'
                ))


            def note(title, text):
                display(HTML(
                    '<aside class="learn learn-note">'
                    f'<strong>{escape(str(title))}</strong><p>{escape(str(text))}</p></aside>'
                ))


            def check(question, answer):
                display(HTML(
                    '<details class="learn learn-check">'
                    f'<summary>Selbstcheck: {escape(str(question))}</summary>'
                    f'<div class="answer">{escape(str(answer))}</div></details>'
                ))


            def steps(items):
                body = "".join(
                    '<article class="learn-step">'
                    f'<span class="nr">{number}</span><strong>{escape(str(title))}</strong>'
                    f'<span>{escape(str(text))}</span></article>'
                    for number, title, text in items
                )
                display(HTML(f'<div class="learn learn-steps">{body}</div>'))


            def simple_table(frame):
                display(HTML(
                    '<div class="learn" style="overflow-x:auto">'
                    + frame.to_html(index=False, border=0, classes="learn-table", escape=True)
                    + '</div>'
                ))


            def exam_sentence(text):
                display(HTML(
                    f'<div class="learn learn-sentence"><strong>So kannst du es sagen:</strong> '
                    f'{escape(str(text))}</div>'
                ))


            def plot_reading(see, meaning, limit):
                cards([
                    ("So liest du den Plot", "Beobachtung", see),
                    ("Bedeutung", "Schlussfolgerung", meaning),
                    ("Saubere Grenze", "Nicht überinterpretieren", limit),
                ])
            """,
        ),
        code(
            "learn-analysis",
            """
            df = pd.read_csv(DATA_PATH, parse_dates=["monat"])
            expected_columns = [
                "zaehler_id", "monat", "jahr", "split", "vollaststunden",
                "verbrauch_kwh", "vertragsleistung_kw", "kundentyp", "monat_idx",
                "arbeitstage", "feiertage_im_monat", "heizgradtage",
                "produktionsplan_index", "wartung_aktiv", "vormonat_vls",
                "letzte_3_monate_vls", "vorjahr_vls", "anomalie", "unmoeglich",
                "ziel_rekonstruiert",
            ]
            assert df.columns.tolist() == expected_columns
            assert len(df) == 16_800 and df["zaehler_id"].nunique() == 700
            assert not df.duplicated(["zaehler_id", "monat"]).any()
            assert df["vertragsleistung_kw"].gt(0).all()
            assert np.allclose(
                df["vollaststunden"],
                df["verbrauch_kwh"] / df["vertragsleistung_kw"],
            )

            df = df.sort_values(["zaehler_id", "monat"]).reset_index(drop=True)
            df["wartung_aktiv"] = df["wartung_aktiv"].astype(int)
            df["vormonat_kwh"] = df["vormonat_vls"] * df["vertragsleistung_kw"]
            df["letzte_3_monate_kwh"] = (
                df["letzte_3_monate_vls"] * df["vertragsleistung_kw"]
            )

            valid_history = df["vollaststunden"].mask(df["unmoeglich"].astype(bool))
            grouped_history = valid_history.groupby(df["zaehler_id"], sort=False)
            expected_lag_1 = grouped_history.shift(1)
            expected_lag_3 = grouped_history.transform(
                lambda values: values.shift(1).rolling(3, min_periods=1).mean()
            )
            assert np.allclose(df["vormonat_vls"], expected_lag_1, equal_nan=True)
            assert np.allclose(df["letzte_3_monate_vls"], expected_lag_3, equal_nan=True)

            df = df.sort_values(["monat", "zaehler_id"]).reset_index(drop=True)
            development = df[
                df["split"].eq("train") & ~df["ziel_rekonstruiert"]
            ].copy()
            benchmark = df[
                df["split"].eq("test") & ~df["ziel_rekonstruiert"]
            ].copy()
            selection = development[development["monat"].dt.month.le(10)].reset_index(drop=True)
            calibration = development[development["monat"].dt.month.ge(11)].reset_index(drop=True)
            assert len(development) == 8_389
            assert len(calibration) == 1_397
            assert len(benchmark) == 8_398

            NUM_FEATURES = [
                "monat_idx", "arbeitstage", "feiertage_im_monat", "heizgradtage",
                "produktionsplan_index", "wartung_aktiv", "vormonat_vls",
                "letzte_3_monate_vls",
            ]
            CAT_FEATURES = ["kundentyp"]
            X_COLUMNS = [*NUM_FEATURES, *CAT_FEATURES, "vertragsleistung_kw"]
            DIRECT_NUM_FEATURES = [
                "monat_idx", "arbeitstage", "feiertage_im_monat", "heizgradtage",
                "produktionsplan_index", "wartung_aktiv", "vormonat_kwh",
                "letzte_3_monate_kwh", "vertragsleistung_kw",
            ]
            DIRECT_COLUMNS = [*DIRECT_NUM_FEATURES, *CAT_FEATURES]


            def make_preprocessor(numeric_features, scale=False):
                numeric_steps = [(
                    "impute",
                    SimpleImputer(
                        strategy="median", add_indicator=True, keep_empty_features=True,
                    ),
                )]
                if scale:
                    numeric_steps.append(("scale", StandardScaler()))
                return ColumnTransformer(
                    [
                        ("num", Pipeline(numeric_steps), numeric_features),
                        (
                            "cat",
                            Pipeline([
                                ("impute", SimpleImputer(strategy="most_frequent")),
                                ("onehot", OneHotEncoder(
                                    handle_unknown="ignore", sparse_output=False,
                                )),
                            ]),
                            CAT_FEATURES,
                        ),
                    ],
                    sparse_threshold=0.0,
                )


            class VLSRegressor(RegressorMixin, BaseEstimator):
                # Intern auf VLS trainieren, nach außen in kWh prognostizieren.

                def __init__(self, pipeline):
                    self.pipeline = pipeline

                def fit(self, X, y):
                    self.pipeline_ = clone(self.pipeline)
                    self.pipeline_.fit(X, np.asarray(y, dtype=float))
                    return self

                def predict_vls(self, X):
                    return np.clip(self.pipeline_.predict(X), 0, None)

                def predict(self, X):
                    return self.predict_vls(X) * X["vertragsleistung_kw"].to_numpy(float)


            def linear_estimator():
                return VLSRegressor(Pipeline([
                    ("pre", make_preprocessor(NUM_FEATURES, scale=True)),
                    ("model", LinearRegression()),
                ]))


            def forest_estimator(params):
                return VLSRegressor(Pipeline([
                    ("pre", make_preprocessor(NUM_FEATURES)),
                    ("model", RandomForestRegressor(
                        n_estimators=300,
                        n_jobs=-1,
                        random_state=RANDOM_STATE,
                        **params,
                    )),
                ]))


            def direct_estimator(params):
                return Pipeline([
                    ("pre", make_preprocessor(DIRECT_NUM_FEATURES)),
                    ("model", RandomForestRegressor(
                        n_estimators=300,
                        n_jobs=-1,
                        random_state=RANDOM_STATE,
                        **params,
                    )),
                ])


            def metrics(actual, predicted):
                actual = np.asarray(actual, dtype=float)
                predicted = np.clip(np.asarray(predicted, dtype=float), 0, None)
                mask = np.isfinite(actual) & np.isfinite(predicted)
                actual, predicted = actual[mask], predicted[mask]
                return {
                    "n": int(mask.sum()),
                    "RMSE (kWh)": mean_squared_error(actual, predicted) ** 0.5,
                    "MAE (kWh)": mean_absolute_error(actual, predicted),
                    "R²": r2_score(actual, predicted),
                }


            fold_definitions = [
                ("2024-04-01", "2024-05-01", "2024-06-30"),
                ("2024-06-01", "2024-07-01", "2024-08-31"),
                ("2024-08-01", "2024-09-01", "2024-10-31"),
            ]
            folds = []
            for train_end, valid_start, valid_end in fold_definitions:
                train_idx = np.flatnonzero(selection["monat"].le(pd.Timestamp(train_end)))
                valid_idx = np.flatnonzero(selection["monat"].between(
                    pd.Timestamp(valid_start), pd.Timestamp(valid_end)
                ))
                assert selection.iloc[train_idx]["monat"].max() < selection.iloc[valid_idx]["monat"].min()
                folds.append((train_idx, valid_idx))

            parameter_grid = list(ParameterGrid({
                "max_depth": [8, None],
                "min_samples_leaf": [5, 20],
                "max_features": [0.7, 1.0],
            }))

            tuning_rows = []
            for params in parameter_grid:
                scores = []
                for train_idx, valid_idx in folds:
                    train = selection.iloc[train_idx]
                    valid = selection.iloc[valid_idx]
                    fitted = forest_estimator(params).fit(
                        train[X_COLUMNS], train["vollaststunden"]
                    )
                    scores.append(metrics(
                        valid["verbrauch_kwh"], fitted.predict(valid[X_COLUMNS])
                    )["RMSE (kWh)"])
                tuning_rows.append({
                    **params,
                    "CV-RMSE (kWh)": np.mean(scores),
                    "Fold-Streuung (kWh)": np.std(scores, ddof=0),
                })
            tuning_results = pd.DataFrame(tuning_rows).sort_values("CV-RMSE (kWh)").reset_index(drop=True)
            best_row = tuning_results.iloc[0]
            best_rf_params = {
                "max_depth": None if pd.isna(best_row["max_depth"]) else int(best_row["max_depth"]),
                "min_samples_leaf": int(best_row["min_samples_leaf"]),
                "max_features": float(best_row["max_features"]),
            }

            comparison_rows = []
            model_factories = {
                "Lineare Regression": linear_estimator,
                "Random Forest": lambda: forest_estimator(best_rf_params),
            }
            for fold_number, (train_idx, valid_idx) in enumerate(folds, start=1):
                train = selection.iloc[train_idx]
                valid = selection.iloc[valid_idx]
                for name, factory in model_factories.items():
                    fitted = factory().fit(train[X_COLUMNS], train["vollaststunden"])
                    comparison_rows.append({
                        "Kandidat": name,
                        "Typ": "Modell",
                        "Fold": fold_number,
                        **metrics(valid["verbrauch_kwh"], fitted.predict(valid[X_COLUMNS])),
                    })
                for name, column in {
                    "Vormonat": "vormonat_kwh",
                    "Bis-zu-3-Monats-Mittel": "letzte_3_monate_kwh",
                }.items():
                    mask = valid[column].notna()
                    comparison_rows.append({
                        "Kandidat": name,
                        "Typ": "Baseline",
                        "Fold": fold_number,
                        **metrics(valid.loc[mask, "verbrauch_kwh"], valid.loc[mask, column]),
                    })
            comparison_detail = pd.DataFrame(comparison_rows)
            comparison = (
                comparison_detail.groupby(["Kandidat", "Typ"], as_index=False)
                .agg(
                    **{"CV-RMSE (kWh)": ("RMSE (kWh)", "mean")},
                    **{"Fold-Streuung (kWh)": ("RMSE (kWh)", lambda x: x.std(ddof=0))},
                    **{"CV-MAE (kWh)": ("MAE (kWh)", "mean")},
                    **{"CV-R²": ("R²", "mean")},
                )
                .sort_values("CV-RMSE (kWh)")
                .reset_index(drop=True)
            )
            selected_name = (
                comparison[comparison["Typ"].eq("Modell")]
                .sort_values("CV-RMSE (kWh)").iloc[0]["Kandidat"]
            )
            selected_factory = model_factories[selected_name]

            fitted_models = {}
            benchmark_predictions = {}
            for name, factory in model_factories.items():
                fitted = factory().fit(development[X_COLUMNS], development["vollaststunden"])
                fitted_models[name] = fitted
                benchmark_predictions[name] = fitted.predict(benchmark[X_COLUMNS])

            benchmark_rows = []
            for name, prediction in benchmark_predictions.items():
                benchmark_rows.append({
                    "Kandidat": name, "Typ": "Modell",
                    **metrics(benchmark["verbrauch_kwh"], prediction),
                })
            for name, column in {
                "Vormonat": "vormonat_kwh",
                "Bis-zu-3-Monats-Mittel": "letzte_3_monate_kwh",
            }.items():
                mask = benchmark[column].notna()
                benchmark_rows.append({
                    "Kandidat": name, "Typ": "Baseline",
                    **metrics(benchmark.loc[mask, "verbrauch_kwh"], benchmark.loc[mask, column]),
                })
            benchmark_metrics = pd.DataFrame(benchmark_rows).sort_values("RMSE (kWh)").reset_index(drop=True)
            selected_metrics = benchmark_metrics.set_index("Kandidat").loc[selected_name]

            direct_tuning_rows = []
            for params in parameter_grid:
                scores = []
                for train_idx, valid_idx in folds:
                    train = selection.iloc[train_idx]
                    valid = selection.iloc[valid_idx]
                    fitted = direct_estimator(params).fit(
                        train[DIRECT_COLUMNS], train["verbrauch_kwh"]
                    )
                    scores.append(metrics(
                        valid["verbrauch_kwh"], fitted.predict(valid[DIRECT_COLUMNS])
                    )["RMSE (kWh)"])
                direct_tuning_rows.append({**params, "CV-RMSE (kWh)": np.mean(scores)})
            direct_tuning = pd.DataFrame(direct_tuning_rows).sort_values("CV-RMSE (kWh)").reset_index(drop=True)
            direct_row = direct_tuning.iloc[0]
            direct_params = {
                "max_depth": None if pd.isna(direct_row["max_depth"]) else int(direct_row["max_depth"]),
                "min_samples_leaf": int(direct_row["min_samples_leaf"]),
                "max_features": float(direct_row["max_features"]),
            }
            direct_model = direct_estimator(direct_params).fit(
                development[DIRECT_COLUMNS], development["verbrauch_kwh"]
            )
            direct_prediction = direct_model.predict(benchmark[DIRECT_COLUMNS])
            direct_metrics = metrics(benchmark["verbrauch_kwh"], direct_prediction)

            calibration_parts = []
            for month in sorted(calibration["monat"].unique()):
                training = development[development["monat"].lt(month)]
                holdout = development[development["monat"].eq(month)].copy()
                fitted = selected_factory().fit(training[X_COLUMNS], training["vollaststunden"])
                holdout["prognose_kwh"] = fitted.predict(holdout[X_COLUMNS])
                holdout["prognose_vls"] = (
                    holdout["prognose_kwh"] / holdout["vertragsleistung_kw"]
                )
                calibration_parts.append(holdout)
            calibration_scored = pd.concat(calibration_parts, ignore_index=True)
            calibration_scored["residuum_vls"] = (
                calibration_scored["vollaststunden"] - calibration_scored["prognose_vls"]
            )
            calibration_scored["abs_residuum_vls"] = calibration_scored["residuum_vls"].abs()
            sorted_errors = np.sort(calibration_scored["abs_residuum_vls"].to_numpy(float))

            benchmark_scored = benchmark.copy()
            benchmark_scored["prognose_kwh"] = benchmark_predictions[selected_name]
            benchmark_scored["prognose_vls"] = (
                benchmark_scored["prognose_kwh"] / benchmark_scored["vertragsleistung_kw"]
            )
            benchmark_scored["residuum_kwh"] = (
                benchmark_scored["verbrauch_kwh"] - benchmark_scored["prognose_kwh"]
            )
            benchmark_scored["residuum_vls"] = (
                benchmark_scored["vollaststunden"] - benchmark_scored["prognose_vls"]
            )
            benchmark_scored["abs_residuum_vls"] = benchmark_scored["residuum_vls"].abs()

            threshold_rows = []
            for quantile in (0.95, 0.975, 0.99, 0.995):
                threshold = float(np.quantile(sorted_errors, quantile))
                alerts = benchmark_scored["abs_residuum_vls"].ge(threshold)
                threshold_rows.append({
                    "Perzentil": quantile * 100,
                    "Schwelle (VLS-h)": threshold,
                    "Hinweise 2025": int(alerts.sum()),
                    "Hinweise je Monat": alerts.sum() / 12,
                })
            threshold_table = pd.DataFrame(threshold_rows)
            official_threshold = float(np.quantile(sorted_errors, OFFICIAL_QUANTILE))
            learning_threshold = float(np.quantile(sorted_errors, LEARNING_QUANTILE))

            benchmark_scored["faktor_97_5"] = (
                benchmark_scored["abs_residuum_vls"] / learning_threshold
            )
            benchmark_scored["hinweis_97_5"] = benchmark_scored["faktor_97_5"].ge(1)
            benchmark_scored["faktor_99"] = (
                benchmark_scored["abs_residuum_vls"] / official_threshold
            )
            benchmark_scored["hinweis_99"] = benchmark_scored["faktor_99"].ge(1)

            case_id = "ZL-00147"
            case_history = benchmark_scored[
                benchmark_scored["zaehler_id"].eq(case_id)
            ].sort_values("monat").copy()
            assert int(case_history["hinweis_97_5"].sum()) == 2

            eligible_meter = (
                df[df["jahr"].eq(2024) & ~df["unmoeglich"]]
                .groupby("zaehler_id", observed=True).size()
            )
            lag_meter_id = eligible_meter[eligible_meter.eq(12)].index[0]
            lag_example = df[
                df["zaehler_id"].eq(lag_meter_id) & df["jahr"].eq(2024)
            ].sort_values("monat").copy()

            feature_groups = {
                "Verbrauchshistorie": ["vormonat_vls", "letzte_3_monate_vls"],
                "Produktionsplan": ["produktionsplan_index"],
                "Wartung": ["wartung_aktiv"],
                "Kalender": ["arbeitstage", "feiertage_im_monat"],
                "Jahreszeit": ["monat_idx"],
                "Wetterprognose": ["heizgradtage"],
                "Kundentyp": ["kundentyp"],
            }
            final_model = fitted_models[selected_name]
            baseline_rmse = selected_metrics["RMSE (kWh)"]
            rng = np.random.default_rng(RANDOM_STATE)
            importance_rows = []
            for group_name, columns in feature_groups.items():
                increases = []
                for _ in range(3):
                    order = rng.permutation(len(benchmark))
                    permuted = benchmark[X_COLUMNS].copy()
                    for column in columns:
                        permuted[column] = permuted[column].to_numpy()[order]
                    increases.append(
                        metrics(
                            benchmark["verbrauch_kwh"], final_model.predict(permuted)
                        )["RMSE (kWh)"] - baseline_rmse
                    )
                importance_rows.append({
                    "Featuregruppe": group_name,
                    "RMSE-Anstieg (kWh)": np.mean(increases),
                })
            importance = pd.DataFrame(importance_rows).sort_values("RMSE-Anstieg (kWh)")

            ci.ZEITRAUM = f"{df['monat'].min():%m/%Y}–{df['monat'].max():%m/%Y}"
            """,
        ),
        code(
            "learn-cover",
            """
            ci.titelkarte(
                "Modellierung von Grund auf verstehen",
                "Dein Lernnotebook: von kW, kWh und Vollaststunden bis zum Perzentil, "
                "Schwellenfaktor und fachlichen Prüfhinweis.",
                "Begleitnotebook zu 12_modeling_ihk_lernstory.ipynb · "
                f"Ausgeführt: {datetime.now(timezone.utc):%d.%m.%Y %H:%M} UTC",
                logo=BASE_DIR / "brand/design-system/assets/logo-sww-full.png",
                metriken=[
                    ("Zähler", de(df["zaehler_id"].nunique(), 0)),
                    ("Zähler-Monate", de(len(df), 0)),
                    ("Lernziel", "sicher erklären"),
                ],
                zeitraum="01/2024–12/2025",
            )
            """,
        ),
        markdown(
            "learn-welcome",
            """
            <div class="learn learn-note">
              <strong>Vorweg: Du musst dich dafür nicht schlecht fühlen.</strong>
              <p>Hier liegen mehrere einzeln überschaubare Themen übereinander: Einheiten,
              Zeitreihen, Modelltraining, Fehlermaße und Anomalieentscheidungen. Wenn ein
              Zwischenschritt nicht mehr präsent ist, wirkt die gesamte Kette plötzlich
              kompliziert. Dieses Notebook baut sie deshalb langsam wieder auf.</p>
            </div>

            **So benutzt du das Notebook:** Lies zunächst nur Überschriften, Formeln und
            Diagramme. Öffne anschließend die Selbstchecks. Die technischen Codezellen sind
            standardmäßig eingeklappt, bleiben aber vollständig reproduzierbar.

            Am Ende solltest du drei Fragen ohne Code beantworten können:

            1. Wie entsteht unsere Folgemonatsprognose?
            2. Wie wird aus einem Prognosefehler ein Prüfhinweis?
            3. Was darf dieses Ergebnis aussagen – und was noch nicht?
            """,
        ),
        code(
            "learn-mental-model",
            """
            steps([
                (1, "Vergangenheit", "Nur Informationen, die vor dem Prognosemonat bekannt sind."),
                (2, "Modell", "Lineare Referenz und Random Forest schätzen Vollaststunden."),
                (3, "Rückrechnung", "Prognose-VLS × Vertragsleistung ergibt kWh."),
                (4, "Istwert", "Nach Monatsende trifft der gemessene Verbrauch ein."),
                (5, "Residuum", "Ist minus Prognose wird leistungsbezogen beurteilt."),
                (6, "Prüfhinweis", "Erst die Schwellenüberschreitung startet eine menschliche Prüfung."),
            ])
            note(
                "Der rote Faden",
                "Prognose und Anomalieerkennung sind zwei Schritte: Vor Monatsbeginn wird "
                "prognostiziert. Erst nach Eintreffen des Istwerts kann eine Abweichung "
                "als Prüfhinweis markiert werden.",
            )
            """,
        ),
        code(
            "learn-section-units",
            """
            ci.abschnitt(
                "01", "Einheiten und Zielvariable",
                "kW, kWh und Vollaststunden zuerst auseinanderhalten.",
                kontext="LERNPFAD / GRUNDLAGEN",
            )
            """,
        ),
        code(
            "learn-units-cards",
            """
            cards([
                ("Leistung", "kW", "Wie groß ist die vereinbarte beziehungsweise mögliche Leistung des Anschlusses?"),
                ("Energiemenge", "kWh", "Wie viel elektrische Energie wurde über den Monat tatsächlich verbraucht?"),
                ("Vergleichsgröße", "VLS-Stunden", "Wie groß ist der Verbrauch im Verhältnis zur Vertragsleistung?"),
            ])
            formula(
                "Vollaststunden = Verbrauch in kWh ÷ Vertragsleistung in kW",
                "Die Einheit ist rechnerisch eine Stunde. VLS sind hier eine Normalisierung, keine gemessene Laufzeit.",
            )
            """,
        ),
        code(
            "learn-vls-example",
            """
            vls_example = pd.DataFrame({
                "Zähler": ["A · kleiner Anschluss", "B · großer Anschluss"],
                "Verbrauch (kWh)": [10_000, 40_000],
                "Vertragsleistung (kW)": [50, 200],
            })
            vls_example["VLS (h)"] = (
                vls_example["Verbrauch (kWh)"] / vls_example["Vertragsleistung (kW)"]
            )

            from plotly.subplots import make_subplots
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Verbrauch", "Auf Leistung normiert"),
            )
            fig.add_trace(go.Bar(
                x=vls_example["Zähler"], y=vls_example["Verbrauch (kWh)"],
                marker_color=theme.ROLE["ist"], name="Verbrauch", showlegend=False,
                text=[f"{de(v, 0)} kWh" for v in vls_example["Verbrauch (kWh)"]],
                textposition="outside",
            ), row=1, col=1)
            fig.add_trace(go.Bar(
                x=vls_example["Zähler"], y=vls_example["VLS (h)"],
                marker_color=theme.ROLE["residuum"], name="VLS", showlegend=False,
                text=[f"{de(v, 0)} h" for v in vls_example["VLS (h)"]],
                textposition="outside",
            ), row=1, col=2)
            ci.stil(
                fig,
                "VLS machen unterschiedlich große Anschlüsse vergleichbarer",
                "Rechenbeispiel · B verbraucht viermal so viel, besitzt aber auch viermal so viel Vertragsleistung",
                x_titel="",
                y_titel="",
            )
            fig.update_yaxes(title_text="Verbrauch (kWh)", row=1, col=1)
            fig.update_yaxes(title_text="Vollaststunden (h)", row=1, col=2)
            ci.zeigen(fig)
            plot_reading(
                "Links unterscheiden sich die Energiemengen stark; rechts sind beide Auslastungswerte gleich.",
                "40.000 kWh ÷ 200 kW und 10.000 kWh ÷ 50 kW ergeben jeweils 200 VLS-Stunden.",
                "VLS bedeuten nicht, dass beide Anlagen exakt 200 reale Stunden unter Volllast liefen.",
            )
            exam_sentence(
                "kWh misst die Energiemenge. VLS setzen diese Menge zur Vertragsleistung ins Verhältnis, "
                "damit unterschiedlich große Anschlüsse fairer verglichen werden können."
            )
            check(
                "12.000 kWh bei 60 kW Vertragsleistung – wie viele VLS sind das?",
                "12.000 ÷ 60 = 200 VLS-Stunden.",
            )
            """,
        ),
        code(
            "learn-target-flow",
            """
            cards([
                ("Interne Zielgröße", "Prognose in VLS", "Das Modell lernt den leistungsbezogenen Verbrauch des Folgemonats."),
                ("Operative Ausgabe", "Rückrechnung in kWh", "Prognose-VLS × Vertragsleistung liefert die Mengenprognose."),
                ("Nach Monatsende", "Vergleich mit dem Istwert", "Erst jetzt kann ein Residuum und danach ein Prüfhinweis entstehen."),
            ])
            formula(
                "Prognose in kWh = Prognose in VLS × Vertragsleistung in kW",
                "Die Modellierung ist normiert; Planung, Bewertung und Kommunikation erfolgen wieder in kWh.",
            )
            check(
                "Wann kann ein Prüfhinweis entstehen – vor oder nach dem Prognosemonat?",
                "Erst nach Monatsende, weil dafür der tatsächliche Istverbrauch benötigt wird. Die Prognose selbst entsteht vorher.",
            )
            """,
        ),
        code(
            "learn-section-time",
            """
            ci.abschnitt(
                "02", "Zeitreihen, Merkmale und Leakage",
                "Welche Informationen darf eine Folgemonatsprognose tatsächlich kennen?",
                kontext="LERNPFAD / DATEN",
            )
            """,
        ),
        code(
            "learn-dataset-overview",
            """
            cards([
                ("Beobachtung", "Ein Zähler-Monat", "Eine Tabellenzeile beschreibt genau einen Zähler in genau einem Monat."),
                ("Zeitraum", "24 Monate", "Jeder der 700 Zähler besitzt Werte von Januar 2024 bis Dezember 2025."),
                ("Prognosehorizont", "Ein Monat voraus", "Der jeweils nächste Monat wird aus der bis dahin verfügbaren Information geschätzt."),
            ])
            formula(
                "16.800 Zeilen = 700 Zähler × 24 Monate",
                "Die Zeilen sind nicht unabhängig wie zufällige Einzelmessungen, sondern je Zähler zeitlich geordnet.",
            )
            """,
        ),
        markdown(
            "learn-feature-table",
            """
            | Merkmal | Was steckt dahinter? | Darf es vor Monatsbeginn bekannt sein? |
            |---|---|---|
            | Vormonat-VLS | letzter gültiger Monatswert desselben Zählers | ja |
            | Mittel aus bis zu 3 Vormonaten | geglättete jüngste Historie | ja |
            | Monat | saisonale Lage im Jahr | ja |
            | Arbeits- und Feiertage | Kalendereffekt | ja |
            | Heizgradtage | temperaturbezogener Bedarf | nur als Prognosewert |
            | Produktionsplan | erwartete betriebliche Aktivität | ja, wenn geplant |
            | geplante Wartung | bekannter Stillstand oder Eingriff | ja, wenn geplant |
            | Kundentyp | Gewerbe, Industrie oder Kommunal | ja |

            **Merkregel:** Ein fachlich interessantes Merkmal ist nur dann zulässig, wenn
            dieselbe Information im späteren Echtbetrieb zum Prognosezeitpunkt verfügbar wäre.
            """,
        ),
        code(
            "learn-lag-plot",
            """
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=lag_example["monat"], y=lag_example["vollaststunden"],
                name="Ist-VLS des Monats", mode="lines+markers",
                line=dict(color=theme.ROLE["ist"], width=2), marker=dict(size=6),
            ))
            fig.add_trace(go.Scatter(
                x=lag_example["monat"], y=lag_example["vormonat_vls"],
                name="Vormonat als Merkmal", mode="lines+markers",
                line=dict(color=theme.ROLE["prognose"], width=2, dash="4,2"), marker=dict(size=5),
            ))
            fig.add_trace(go.Scatter(
                x=lag_example["monat"], y=lag_example["letzte_3_monate_vls"],
                name="bis zu 3 Vormonate", mode="lines+markers",
                line=dict(color=theme.ROLE["residuum"], width=2, dash="3,3"), marker=dict(size=5),
            ))
            ci.stil(
                fig,
                f"Lag-Features verschieben bekannte Historie nach vorn · {lag_meter_id}",
                "Beispieljahr 2024 · der Merkmalswert eines Monats enthält den aktuellen Istwert ausdrücklich nicht",
                x_titel="Monat",
                y_titel="Vollaststunden (h)",
            )
            ci.zeigen(fig)
            lag_table = lag_example.head(4)[[
                "monat", "vollaststunden", "vormonat_vls", "letzte_3_monate_vls"
            ]].copy()
            lag_table["Monat"] = lag_table.pop("monat").dt.strftime("%m/%Y")
            lag_table = lag_table.rename(columns={
                "vollaststunden": "Ist-VLS",
                "vormonat_vls": "Vormonat-VLS",
                "letzte_3_monate_vls": "Bis-zu-3-Monats-Mittel",
            })
            for column in ["Ist-VLS", "Vormonat-VLS", "Bis-zu-3-Monats-Mittel"]:
                lag_table[column] = lag_table[column].map(lambda value: de(value, 1))
            simple_table(lag_table)
            plot_reading(
                "Im Januar fehlen beide Historienmerkmale. Im Februar steht Januar bereit; im März Januar und Februar.",
                "Ab April besteht das Historienmittel aus bis zu drei gültigen, abgeschlossenen Vormonaten desselben Zählers.",
                "Der Istwert des aktuellen oder eines zukünftigen Monats darf niemals in sein eigenes Merkmal einfließen.",
            )
            exam_sentence(
                "Lag-Features werden je Zähler mit shift(1) gebildet. Dadurch kennt das Modell nur abgeschlossene Vormonate."
            )
            check(
                "Welche Monate darf das Drei-Monats-Mittel für März 2024 enthalten?",
                "Nur Januar und Februar 2024. März selbst und alle späteren Monate sind ausgeschlossen.",
            )
            """,
        ),
        code(
            "learn-history-policy",
            """
            cards([
                ("Januar 2024", "Echter Kaltstart", "Keine Vergangenheit im Datensatz: Historienwerte bleiben leer."),
                ("Februar und März", "Verfügbare Historie", "Februar nutzt Januar; März nutzt Januar und Februar."),
                ("Ab April", "Bis zu drei Monate", "Es werden höchstens drei gültige Vormonate desselben Zählers gemittelt."),
            ])
            note(
                "Warum keine 1.500 Zeilen löschen?",
                "Die verfügbare Anfangshistorie wird genutzt. So gewinnen wir 1.453 zuvor fehlende "
                "Drei-Monats-Werte zurück; nur die 700 echten Januar-Kaltstarts bleiben leer. "
                "Die fehlenden Startwerte behandelt der Imputer erst innerhalb des jeweiligen Trainingsfolds.",
            )
            """,
        ),
        code(
            "learn-time-split",
            """
            timeline_rows = []
            for number, (train_end, valid_start, valid_end) in enumerate(fold_definitions, 1):
                timeline_rows.extend([
                    {"Zeile": f"Fold {number}", "Start": "2024-01-01", "Ende": train_end, "Rolle": "Lernen"},
                    {"Zeile": f"Fold {number}", "Start": valid_start, "Ende": valid_end, "Rolle": "Bewerten"},
                ])
            timeline_rows.extend([
                {"Zeile": "Schwelle", "Start": "2024-11-01", "Ende": "2024-12-31", "Rolle": "Kalibrieren"},
                {"Zeile": "Benchmark", "Start": "2025-01-01", "Ende": "2025-12-31", "Rolle": "Test"},
            ])
            timeline = pd.DataFrame(timeline_rows)
            timeline[["Start", "Ende"]] = timeline[["Start", "Ende"]].apply(pd.to_datetime)
            fig = px.timeline(
                timeline, x_start="Start", x_end="Ende", y="Zeile", color="Rolle",
                color_discrete_map={
                    "Lernen": theme.ROLE["ist"],
                    "Bewerten": theme.TOKENS["teal-500"],
                    "Kalibrieren": theme.ROLE["schwellwert"],
                    "Test": theme.TOKENS["grey-400"],
                },
            )
            ci.stil(
                fig,
                "Vergangenheit erklärt Zukunft – niemals umgekehrt",
                "Drei zeitliche Modellprüfungen 2024 · Kalibrierung Ende 2024 · retrospektiver Test 2025",
                x_titel="Monat",
                y_titel="",
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_xaxes(tickformat="%m/%Y", dtick="M2")
            ci.zeigen(fig)
            plot_reading(
                "Jeder Bewertungsblock liegt vollständig nach seinem Trainingsblock.",
                "Damit ahmt die Validierung die echte Aufgabe nach: Aus vergangenen Monaten wird ein späterer Monat vorhergesagt.",
                "2025 wurde inzwischen angesehen und ist deshalb ein retrospektiver Benchmark, kein künftig unangesehener Blindtest.",
            )
            exam_sentence(
                "Wir mischen die Zeitreihe nicht zufällig, weil sonst spätere Monate in das Training früherer Prognosen geraten könnten."
            )
            """,
        ),
        code(
            "learn-leakage",
            """
            cards([
                ("Verboten", "Zukunftswerte zurückfüllen", "2025 darf keine fehlende Historie aus 2024 erklären."),
                ("Verboten", "Vorverarbeitung auf allen Daten", "Median und Kategorien dürfen nicht schon aus späteren Prüfmonaten gelernt werden."),
                ("Zulässig", "Pipeline je Fold", "Imputation und Modell werden ausschließlich auf dem aktuellen Trainingsblock angepasst."),
            ])
            note(
                "Data Leakage in einem Satz",
                "Leakage bedeutet, dass das Modell beim Lernen Informationen erhält, die in der echten Zukunftsprognose noch nicht verfügbar wären."
            )
            check(
                "Darf reales Dezemberwetter für eine Prognose verwendet werden, die Ende November erstellt wird?",
                "Nein. Verwendbar wäre nur eine Ende November verfügbare Wetterprognose für Dezember.",
            )
            """,
        ),
        code(
            "learn-section-model",
            """
            ci.abschnitt(
                "03", "Baselines, Modelle und Bewertung",
                "Komplexität muss einen messbaren Mehrwert gegenüber einfachen Regeln liefern.",
                kontext="LERNPFAD / MODELLWAHL",
            )
            """,
        ),
        code(
            "learn-baselines",
            """
            cards([
                ("Baseline 1", "Vormonat", "Die Prognose für den nächsten Monat entspricht dem letzten Monatswert."),
                ("Baseline 2", "Bis-zu-3-Monats-Mittel", "Die jüngsten ein bis drei Monate werden gemittelt und geglättet."),
                ("Prüffrage", "Schlägt ML eine einfache Regel?", "Nur dann rechtfertigen zusätzliche Merkmale und Modellpflege ihren Aufwand."),
            ])
            note(
                "Eine starke Baseline ist nichts Schlechtes",
                "Bei stabilen Verbrauchsreihen kann der Vormonat bereits viel erklären. "
                "Der Random Forest muss nicht spektakulär wirken, sondern reproduzierbar besser sein."
            )
            """,
        ),
        code(
            "learn-model-intuition",
            """
            cards([
                ("Referenz", "Lineare Regression", "Bildet die Prognose als gewichtete Summe der Merkmale. Gut erklärbar, aber begrenzt flexibel."),
                ("Kandidat", "Random Forest", "Viele Entscheidungsbäume lernen nichtlineare Regeln und werden für die Prognose gemittelt."),
                ("Entscheidung", "Gleiche zeitliche Prüfung", "Nicht die modernste Methode gewinnt, sondern der kleinste Validierungs-RMSE."),
            ])
            exam_sentence(
                "Die lineare Regression ist unsere verständliche Referenz. Der Random Forest wird gewählt, wenn seine zusätzliche Flexibilität im selben zeitlichen Test messbar hilft."
            )
            """,
        ),
        markdown(
            "learn-hyperparameters",
            """
            ### Parameter oder Hyperparameter?

            **Modellparameter** werden beim Training aus den Daten gelernt. Bei einer linearen
            Regression sind das beispielsweise die Gewichte der Merkmale.

            **Hyperparameter** legen vor dem Training fest, wie flexibel das Modell lernen darf:

            | Hyperparameter | Einfache Bedeutung | Zu flexibel bedeutet häufig … |
            |---|---|---|
            | `n_estimators = 300` | Anzahl der Bäume | hauptsächlich mehr Rechenzeit |
            | `max_depth` | maximale Baumtiefe | sehr spezielle Regeln |
            | `min_samples_leaf` | Mindestfälle in einem Blatt | kleine Sondergruppen werden auswendig gelernt |
            | `max_features` | Merkmalsanteil je Aufteilung | Bäume ähneln sich stärker |

            Wir prüfen acht kontrollierte Kombinationen ausschließlich in den drei zeitlichen
            Folds von 2024. Das Testjahr 2025 entscheidet keinen Hyperparameter.
            """,
        ),
        code(
            "learn-tuning-table",
            """
            tuning_view = tuning_results.copy()
            tuning_view["max_depth"] = tuning_view["max_depth"].map(
                lambda value: "unbegrenzt" if pd.isna(value) else str(int(value))
            )
            tuning_view["min_samples_leaf"] = tuning_view["min_samples_leaf"].astype(int)
            tuning_view["max_features"] = tuning_view["max_features"].map(lambda x: de(x, 1))
            tuning_view["CV-RMSE (kWh)"] = tuning_view["CV-RMSE (kWh)"].map(lambda x: de(x, 0))
            tuning_view["Fold-Streuung (kWh)"] = tuning_view["Fold-Streuung (kWh)"].map(lambda x: de(x, 0))
            tuning_view = tuning_view.rename(columns={
                "max_depth": "Baumtiefe",
                "min_samples_leaf": "Mindestfälle im Blatt",
                "max_features": "Merkmalsanteil",
            })
            simple_table(tuning_view)
            cards([
                ("Gewinner", "Tiefe 8", "Die beste Konfiguration begrenzt die Tiefe und vermeidet unnötig spezielle Einzelregeln."),
                ("Gewinner", "Mindestens 5 Fälle", "Ein Blatt darf nicht nur einen einzelnen Zähler-Monat repräsentieren."),
                ("Gewinner", "70 % der Merkmale", "Unterschiedliche Bäume sehen unterschiedliche Merkmalsauswahlen und ergänzen sich."),
            ])
            check(
                "Warum wählen wir Hyperparameter nicht anhand des Jahres 2025?",
                "Sonst würde 2025 indirekt Teil des Trainingsprozesses und könnte nicht mehr als getrennte spätere Prüfung dienen.",
            )
            """,
        ),
        code(
            "learn-metrics-example",
            """
            toy = pd.DataFrame({
                "Fall": ["A", "B", "C"],
                "Ist (kWh)": [100, 120, 80],
                "Prognose (kWh)": [90, 130, 100],
            })
            toy["Fehler"] = toy["Ist (kWh)"] - toy["Prognose (kWh)"]
            toy["|Fehler|"] = toy["Fehler"].abs()
            toy["Fehler²"] = toy["Fehler"] ** 2
            toy_mae = toy["|Fehler|"].mean()
            toy_rmse = np.sqrt(toy["Fehler²"].mean())
            toy_r2 = r2_score(toy["Ist (kWh)"], toy["Prognose (kWh)"])
            simple_table(toy)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=toy["Fall"], y=toy["|Fehler|"], name="absoluter Fehler",
                marker_color=theme.ROLE["residuum"],
            ))
            fig.add_trace(go.Bar(
                x=toy["Fall"], y=np.sqrt(toy["Fehler²"]), name="Wurzel des quadrierten Fehlers",
                marker_color=theme.TOKENS["navy-300"], opacity=0.55,
            ))
            ci.stil(
                fig,
                "Ein größerer Einzelfehler beeinflusst den RMSE stärker",
                "Didaktisches Zahlenbeispiel · nicht die Projektbewertung",
                x_titel="Beispielfall",
                y_titel="Fehlerbetrag (kWh)",
            )
            fig.update_layout(barmode="group")
            ci.zeigen(fig)
            cards([
                ("MAE", f"{de(toy_mae, 1)} kWh", "Durchschnitt der absoluten Fehler; direkt als typische Abweichung lesbar."),
                ("RMSE", f"{de(toy_rmse, 1)} kWh", "Quadriert zuerst; dadurch erhalten große Fehler mehr Gewicht."),
                ("R²", de(toy_r2, 2), "Vergleich zur Mittelwertprognose; keine Trefferquote und kein Fehler in kWh."),
            ])
            formula(
                "MAE = Mittelwert(|Ist − Prognose|) · RMSE = √Mittelwert((Ist − Prognose)²)",
                "Unsere Hauptmetrik ist RMSE in kWh, weil große Mengenfehler betrieblich besonders relevant sind.",
            )
            check(
                "Bedeutet R² = 0,90, dass 90 % aller Prognosen richtig sind?",
                "Nein. R² beschreibt den Anteil der im konkreten Datensatz erklärten Streuung, nicht den Anteil richtiger Einzelprognosen.",
            )
            """,
        ),
        code(
            "learn-cv-comparison",
            """
            ordered = comparison.sort_values("CV-RMSE (kWh)", ascending=False)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=ordered["CV-RMSE (kWh)"], y=ordered["Kandidat"], orientation="h",
                name="Mittelwert",
                marker_color=[
                    theme.ROLE["prognose"] if name == selected_name
                    else theme.TOKENS["grey-400"] if kind == "Baseline"
                    else theme.TOKENS["navy-300"]
                    for name, kind in zip(ordered["Kandidat"], ordered["Typ"])
                ],
                error_x=dict(type="data", array=ordered["Fold-Streuung (kWh)"], visible=True),
                text=[f"{de(value, 0)} kWh" for value in ordered["CV-RMSE (kWh)"]],
                textposition="inside", insidetextanchor="start",
                textfont=dict(color=theme.TOKENS["text-inverse"]),
            ))
            detail_order = ordered["Kandidat"].tolist()
            for fold in sorted(comparison_detail["Fold"].unique()):
                values = comparison_detail[comparison_detail["Fold"].eq(fold)].set_index("Kandidat")
                fig.add_trace(go.Scatter(
                    x=[values.loc[name, "RMSE (kWh)"] for name in detail_order],
                    y=detail_order,
                    mode="markers",
                    name=f"Fold {fold}",
                    marker=dict(size=8, symbol="diamond", line=dict(width=1, color=theme.TOKENS["surface-card"])),
                    hovertemplate=f"Fold {fold}<br>RMSE %{{x:,.0f}} kWh<extra></extra>",
                ))
            ci.stil(
                fig,
                "Random Forest erzielt den niedrigsten mittleren Validierungsfehler",
                "Balken = Mittel aus drei zeitlichen Folds · Punkte = einzelne Folds · Whisker = Standardabweichung",
                x_titel="RMSE (kWh) – niedriger ist besser",
                y_titel="",
            )
            ci.gitter_x(fig)
            ci.zeigen(fig)
            cv_view = comparison[["Kandidat", "CV-RMSE (kWh)", "Fold-Streuung (kWh)"]].copy()
            cv_view["CV-RMSE (kWh)"] = cv_view["CV-RMSE (kWh)"].map(lambda x: de(x, 0))
            cv_view["Fold-Streuung (kWh)"] = cv_view["Fold-Streuung (kWh)"].map(lambda x: de(x, 0))
            simple_table(cv_view)
            plot_reading(
                "Die Diamanten zeigen die drei echten Fold-Werte; der Balken fasst sie als Mittelwert zusammen.",
                "Der Random Forest erreicht im Mittel 13.272 kWh RMSE und liegt damit vor linearer Regression und Baselines.",
                "Der Whisker ist nur die Standardabweichung der drei Fold-RMSE – kein Konfidenzintervall und keine Einzelprognoseunsicherheit.",
            )
            exam_sentence(
                "Die Balkenhöhe ist der mittlere RMSE der drei zeitlichen Folds. Der Whisker zeigt, wie stark diese drei Werte schwanken."
            )
            """,
        ),
        code(
            "learn-benchmark",
            """
            ordered = benchmark_metrics.sort_values("RMSE (kWh)", ascending=False)
            fig = go.Figure(go.Bar(
                x=ordered["RMSE (kWh)"], y=ordered["Kandidat"], orientation="h",
                marker_color=[
                    theme.ROLE["prognose"] if name == selected_name
                    else theme.TOKENS["grey-400"] if kind == "Baseline"
                    else theme.TOKENS["navy-300"]
                    for name, kind in zip(ordered["Kandidat"], ordered["Typ"])
                ],
                text=[f"{de(value, 0)} kWh" for value in ordered["RMSE (kWh)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig,
                "Das ausgewählte Modell bleibt auch 2025 vor den Baselines",
                f"Retrospektiver One-Step-Ahead-Benchmark · {de(len(benchmark), 0)} bewertbare Zähler-Monate",
                x_titel="RMSE (kWh) – niedriger ist besser",
                y_titel="",
            )
            ci.gitter_x(fig)
            ci.zeigen(fig)
            best_baseline = benchmark_metrics[benchmark_metrics["Typ"].eq("Baseline")].iloc[0]
            baseline_gain = 1 - selected_metrics["RMSE (kWh)"] / best_baseline["RMSE (kWh)"]
            cards([
                ("RMSE", f"{de(selected_metrics['RMSE (kWh)'], 0)} kWh", "Große Fehler zählen stärker; Hauptmetrik der Modellentscheidung."),
                ("MAE", f"{de(selected_metrics['MAE (kWh)'], 0)} kWh", "Durchschnittliche absolute Abweichung je Zähler-Monat."),
                ("R²", de(selected_metrics["R²"], 3), "Das Modell erklärt einen großen Teil der Streuung des Testjahres."),
                ("Gegen Baseline", f"{de(baseline_gain * 100, 1)} % besser", "Relativer RMSE-Vorteil gegenüber dem Bis-zu-3-Monats-Mittel."),
            ])
            exam_sentence(
                "Der Random Forest wurde mit 2024 ausgewählt und erreicht 2025 einen RMSE von rund 9.188 kWh – 15,9 Prozent weniger als die beste einfache Baseline."
            )
            """,
        ),
        code(
            "learn-vls-vs-kwh",
            """
            target_compare = pd.DataFrame({
                "Zielansatz": ["Direkt kWh", "VLS → kWh"],
                "RMSE (kWh)": [direct_metrics["RMSE (kWh)"], selected_metrics["RMSE (kWh)"]],
            })
            fig = go.Figure(go.Bar(
                x=target_compare["Zielansatz"], y=target_compare["RMSE (kWh)"],
                marker_color=[theme.TOKENS["grey-400"], theme.ROLE["prognose"]],
                text=[f"{de(v, 0)} kWh" for v in target_compare["RMSE (kWh)"]],
                textposition="outside",
            ))
            ci.stil(
                fig,
                "VLS helfen auch im fairen Vergleich desselben Modelltyps",
                "Random Forest gegen Random Forest · beide Varianten werden 2025 in kWh bewertet",
                x_titel="Interne Zielvariable",
                y_titel="RMSE (kWh) – niedriger ist besser",
            )
            ci.zeigen(fig)
            target_gain = 1 - selected_metrics["RMSE (kWh)"] / direct_metrics["RMSE (kWh)"]
            plot_reading(
                "Der VLS-Ansatz erreicht 9.188 kWh, das direkt auf kWh trainierte Modell rund 9.800 kWh RMSE.",
                f"Für diesen Datensatz sinkt der Test-RMSE damit um {de(target_gain * 100, 1)} Prozent.",
                "Das beweist keine allgemeine Überlegenheit von VLS; es ist ein Ergebnis dieses Datensatzes und Versuchsaufbaus.",
            )
            check(
                "Warum werden beide Modelle am Ende in kWh bewertet?",
                "Weil kWh die betriebliche Ziel- und Planungseinheit ist. Ein Vergleich in verschiedenen Einheiten wäre nicht fair.",
            )
            """,
        ),
        code(
            "learn-feature-importance",
            """
            fig = go.Figure(go.Bar(
                x=importance["RMSE-Anstieg (kWh)"], y=importance["Featuregruppe"],
                orientation="h", marker_color=theme.ROLE["ist"],
                text=[f"{de(max(v, 0), 0)} kWh" for v in importance["RMSE-Anstieg (kWh)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig,
                "Welche Informationsgruppen fehlen dem Modell am stärksten?",
                "Gruppierte Permutation Importance auf dem retrospektiven Benchmarkjahr 2025",
                x_titel="RMSE-Anstieg nach zufälligem Mischen (kWh)",
                y_titel="",
            )
            ci.gitter_x(fig)
            ci.zeigen(fig)
            plot_reading(
                "Eine Gruppe wird zufällig gemischt; steigt der Fehler stark, war ihre Information für die Prognose nützlich.",
                "Historie und Planinformationen tragen einen wesentlichen Teil der Prognoseleistung.",
                "Wichtigkeit ist keine Kausalität. Korrelierte Merkmale können sich Bedeutung teilen; kleine negative Werte bedeuten ungefähr null.",
            )
            """,
        ),
        code(
            "learn-overfitting",
            """
            cards([
                ("Schutz 1", "Zeitliche Folds", "Das Modell muss in drei späteren Zeitfenstern funktionieren, die es nicht trainiert haben."),
                ("Schutz 2", "Begrenzte Bäume", "Tiefe 8 und mindestens fünf Fälle pro Blatt begrenzen sehr spezielle Regeln."),
                ("Schutz 3", "Späteres Jahr", "2025 bleibt nach der Modellwahl als getrennte retrospektive Prüfung bestehen."),
                ("Schutz 4", "Baselines", "Das Modell muss einfache, realistische Regeln messbar schlagen."),
            ])
            note(
                "Ist Overfitting damit ausgeschlossen?",
                "Nein. Es gibt kein klares Signal dafür, weil 2025 weiterhin gute Werte liefert. "
                "Das ist aber kein Beweis für alle zukünftigen Jahre. Dafür braucht es einen "
                "prospektiven Pilot, laufendes Monitoring und weitere unangesehene Perioden."
            )
            exam_sentence(
                "Wir sehen kein offensichtliches Overfitting-Signal, können es mit einem bereits bekannten retrospektiven Jahr aber nicht endgültig ausschließen."
            )
            """,
        ),
        code(
            "learn-section-anomaly",
            """
            ci.abschnitt(
                "04", "Vom Prognosefehler zum Prüfhinweis",
                "Residuum, sortierte Fehler, Perzentil und Schwellenfaktor ohne Sprung erklären.",
                kontext="LERNPFAD / ANOMALIEERKENNUNG",
            )
            """,
        ),
        code(
            "learn-residual",
            """
            cards([
                ("Positives Residuum", "Ist liegt über Prognose", "Der tatsächliche Verbrauch ist höher als vom Modell erwartet."),
                ("Negatives Residuum", "Ist liegt unter Prognose", "Der tatsächliche Verbrauch ist niedriger als vom Modell erwartet."),
                ("Betrag", "Stärke ohne Richtung", "Für die Schwelle zählt zunächst, wie groß der Fehler ist; die Richtung bleibt separat erhalten."),
            ])
            formula(
                "VLS-Residuum = Ist-VLS − Prognose-VLS = (Ist-kWh − Prognose-kWh) ÷ Vertragsleistung",
                "Ein Prüfhinweis ist ein ungewöhnlich großer leistungsbezogener Prognosefehler, noch kein bestätigter Defekt.",
            )
            check(
                "Ist ein Residuum von −100 VLS-Stunden kleiner oder weniger wichtig als +100?",
                "Beide haben denselben Betrag 100 und werden gleich stark bewertet. Das Vorzeichen unterscheidet nur ungewöhnlich niedrig von ungewöhnlich hoch.",
            )
            """,
        ),
        code(
            "learn-ranked-errors",
            """
            n_errors = len(sorted_errors)
            ranks = np.arange(1, n_errors + 1)
            percentile_positions = (ranks - 1) / (n_errors - 1) * 100
            position_975 = (n_errors - 1) * LEARNING_QUANTILE
            lower_index = int(np.floor(position_975))
            upper_index = int(np.ceil(position_975))
            interpolation_weight = position_975 - lower_index
            lower_value = sorted_errors[lower_index]
            upper_value = sorted_errors[upper_index]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=percentile_positions[: upper_index],
                y=sorted_errors[: upper_index],
                mode="lines", name="bis zur Schwelle",
                line=dict(color=theme.ROLE["ist"], width=2.5),
                hovertemplate="Rang %{customdata:,d}<br>Anteil %{x:.1f} %<br>|Fehler| %{y:.1f} VLS-h<extra></extra>",
                customdata=ranks[: upper_index],
            ))
            fig.add_trace(go.Scatter(
                x=percentile_positions[upper_index - 1 :],
                y=sorted_errors[upper_index - 1 :],
                mode="lines", name="oberhalb der Schwelle",
                line=dict(color=theme.ROLE["anomalie"], width=3),
                hovertemplate="Rang %{customdata:,d}<br>Anteil %{x:.1f} %<br>|Fehler| %{y:.1f} VLS-h<extra></extra>",
                customdata=ranks[upper_index - 1 :],
            ))
            fig.add_trace(go.Scatter(
                x=[LEARNING_QUANTILE * 100], y=[learning_threshold],
                mode="markers", name="97,5-%-Schwelle",
                marker=dict(color=theme.ROLE["schwellwert"], size=11, line=dict(color=theme.TOKENS["surface-card"], width=2)),
                hovertemplate=f"97,5. Perzentil<br>{de(learning_threshold, 4)} VLS-h<extra></extra>",
            ))
            ci.stil(
                fig,
                "Das Perzentil ist eine Position in der sortierten Fehlerliste",
                f"{de(n_errors, 0)} absolute Out-of-Fold-Fehler aus November und Dezember 2024",
                x_titel="Position in den sortierten Fehlern",
                y_titel="Absoluter Prognosefehler (VLS-h)",
            )
            fig.update_xaxes(ticksuffix=" %", range=[0, 100])
            ci.referenzlinie(fig, 97.5, "97,5 %", achse="x", position="top left")
            ci.schwellwert(fig, learning_threshold, f"{de(learning_threshold, 1)} VLS-h")
            ci.zeigen(fig)
            plot_reading(
                f"Alle {de(n_errors, 0)} absoluten Fehler sind von klein nach groß sortiert; links häufige kleine, rechts seltene große Fehler.",
                f"Beim 97,5. Perzentil liegen 1.362 Fehler bis {de(learning_threshold, 1)} VLS-h und 35 darüber.",
                "97,5 Prozent beziehen sich auf den Rang der Kalibrierungsfehler – nicht auf Verbrauch, Gesamtleistung oder Defektwahrscheinlichkeit.",
            )
            """,
        ),
        code(
            "learn-percentile-calculation",
            """
            formula(
                "Position = (1.397 − 1) × 0,975 = 1.361,1 (nullbasiert)",
                "Die Position liegt 10 Prozent des Weges zwischen dem 1.362. und 1.363. sortierten Fehler.",
            )
            formula(
                f"{de(lower_value, 4)} + 0,1 × ({de(upper_value, 4)} − {de(lower_value, 4)}) = {de(learning_threshold, 4)} VLS-h",
                "Pandas verwendet hier lineare Interpolation. Darum muss 82,4304 selbst kein beobachteter Fehler sein.",
            )
            around = pd.DataFrame({
                "Aufsteigender Rang": ranks[lower_index - 3 : upper_index + 4],
                "Absoluter Fehler (VLS-h)": sorted_errors[lower_index - 3 : upper_index + 4],
            })
            around["Absoluter Fehler (VLS-h)"] = around["Absoluter Fehler (VLS-h)"].map(lambda x: de(x, 4))
            simple_table(around)
            cards([
                ("Unter der Grenze", "1.362 Fälle", "Diese historischen Fehler sind höchstens 82,4304 VLS-Stunden groß."),
                ("Über der Grenze", "35 Fälle", "Diese rund 2,5 Prozent bilden den seltenen oberen Rand der absoluten Fehler."),
                ("Nicht gemeint", "Keine Leistungsquote", "97,5 Prozent sind weder Anteil des Verbrauchs noch Anteil der Vertragsleistung."),
            ])
            exam_sentence(
                "Das 97,5. Perzentil ist die Rangposition, unter der ungefähr 97,5 Prozent der historischen absoluten Prognosefehler liegen."
            )
            check(
                "Warum gibt es die Schwelle 82,4304 nicht zwingend als echten Zeilenwert?",
                "Weil sie durch lineare Interpolation zwischen Rang 1.362 mit 82,4129 und Rang 1.363 mit 82,5876 berechnet wird.",
            )
            """,
        ),
        code(
            "learn-meter-threshold",
            """
            capacity_examples = pd.DataFrame({
                "Vertragsleistung (kW)": [10, 49, 50, 100, 500],
            })
            capacity_examples["kWh-Grenze bei 97,5 %"] = (
                capacity_examples["Vertragsleistung (kW)"] * learning_threshold
            )
            capacity_examples["kWh-Grenze bei 97,5 %"] = capacity_examples[
                "kWh-Grenze bei 97,5 %"
            ].map(lambda x: de(x, 1))
            formula(
                "Individuelle kWh-Grenze = gemeinsame VLS-Schwelle × Vertragsleistung des Zählers",
                "82,4304 VLS-Stunden gelten gemeinsam; in kWh erhält jeder Zähler eine seiner Größe entsprechende Grenze.",
            )
            simple_table(capacity_examples)
            exam_sentence(
                "Die Perzentilschwelle ist nicht pro Zähler neu geschätzt. Sie ist in VLS gemeinsam und wird erst durch die Vertragsleistung zur individuellen kWh-Grenze."
            )
            """,
        ),
        code(
            "learn-vls-boundary-plot",
            """
            active = benchmark_scored["hinweis_97_5"]
            normal = benchmark_scored[~active]
            alerts_975 = benchmark_scored[active]
            axis_max = 1.03 * max(
                benchmark_scored["vollaststunden"].max(),
                benchmark_scored["prognose_vls"].max(),
            )
            line_x = np.linspace(0, axis_max, 200)
            fig = go.Figure()
            fig.add_trace(go.Scattergl(
                x=normal["prognose_vls"], y=normal["vollaststunden"],
                mode="markers", name="kein Prüfhinweis",
                marker=dict(color=theme.TOKENS["grey-400"], size=5, opacity=0.28),
                hovertemplate="Prognose %{x:.1f} VLS-h<br>Ist %{y:.1f} VLS-h<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=alerts_975["prognose_vls"], y=alerts_975["vollaststunden"],
                mode="markers", name="Prüfhinweis",
                marker=dict(color=theme.ROLE["anomalie"], size=8, symbol="diamond", opacity=0.85),
                customdata=np.c_[alerts_975["zaehler_id"], alerts_975["monat"].dt.strftime("%m/%Y"), alerts_975["residuum_vls"]],
                hovertemplate="%{customdata[0]} · %{customdata[1]}<br>Prognose %{x:.1f} VLS-h<br>Ist %{y:.1f} VLS-h<br>Residuum %{customdata[2]:.1f} VLS-h<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=line_x, y=line_x, mode="lines", name="Ist = Prognose",
                line=dict(color=theme.ROLE["ist"], width=2), hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=line_x, y=line_x + learning_threshold, mode="lines",
                name="obere Grenze", line=dict(color=theme.ROLE["schwellwert"], width=1.5, dash="3,3"),
                hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=line_x, y=np.maximum(0, line_x - learning_threshold), mode="lines",
                name="untere Grenze", line=dict(color=theme.ROLE["schwellwert"], width=1.5, dash="3,3"),
                hoverinfo="skip",
            ))
            ci.stil(
                fig,
                "In VLS wird die gemeinsame Fehlergrenze als Band sichtbar",
                "Benchmark 2025 · Lernbeispiel mit 97,5. Perzentil und ±82,4 VLS-Stunden",
                x_titel="Prognose (VLS-h)",
                y_titel="Ist (VLS-h)",
            )
            fig.update_xaxes(range=[0, axis_max])
            fig.update_yaxes(range=[0, axis_max])
            ci.zeigen(fig)
            plot_reading(
                "Die Navy-Diagonale bedeutet perfekte Prognose. Die beiden gepunkteten Linien liegen jeweils 82,4 VLS-Stunden entfernt.",
                "Punkte außerhalb dieses Bandes überschreiten die gewählte Grenze und werden als Prüfhinweis markiert.",
                "Im gemeinsamen kWh-Plot wäre ein einziges paralleles Band falsch, weil die kWh-Grenze von der jeweiligen Vertragsleistung abhängt.",
            )
            """,
        ),
        code(
            "learn-threshold-workload",
            """
            fig = go.Figure(go.Scatter(
                x=threshold_table["Perzentil"], y=threshold_table["Hinweise je Monat"],
                mode="lines+markers+text",
                line=dict(color=theme.ROLE["residuum"], width=3),
                marker=dict(size=9),
                text=[de(value, 1) for value in threshold_table["Hinweise je Monat"]],
                textposition="top center",
                hovertemplate="%{x}. Perzentil<br>%{y:.1f} Hinweise/Monat<extra></extra>",
            ))
            ci.stil(
                fig,
                "Ein höheres Perzentil reduziert den Prüfaufwand",
                "Die Schwellen stammen aus Ende 2024; die Fallzahlen werden auf dem Benchmarkjahr 2025 gezählt",
                x_titel="Perzentil der Kalibrierungsfehler",
                y_titel="Prüfhinweise je Monat",
            )
            ci.referenzlinie(fig, 99, "Pilotannahme im Prüfungsnotebook", achse="x", position="top left")
            ci.zeigen(fig)
            threshold_view = threshold_table.copy()
            threshold_view["Perzentil"] = threshold_view["Perzentil"].map(lambda x: f"{de(x, 1)} %")
            threshold_view["Schwelle (VLS-h)"] = threshold_view["Schwelle (VLS-h)"].map(lambda x: de(x, 1))
            threshold_view["Hinweise je Monat"] = threshold_view["Hinweise je Monat"].map(lambda x: de(x, 1))
            simple_table(threshold_view)
            cards([
                ("Niedrigeres Perzentil", "Mehr Sensitivität", "Niedrigere Grenze, mehr Fälle und mehr fachlicher Prüfaufwand."),
                ("Höheres Perzentil", "Stärkere Priorisierung", "Höhere Grenze, weniger Fälle und höheres Risiko, schwächere Auffälligkeiten nicht vorzulegen."),
                ("Dashboard-Regler", "Kein Retraining", "Der Regler ändert nur die Entscheidungsgrenze auf bereits vorhandenen Prognosefehlern."),
            ])
            note(
                "Warum sind 2025 nicht exakt 2,5 Prozent auffällig?",
                "Das 97,5. Perzentil beschreibt die Fehlerverteilung der Kalibrierung Ende 2024. "
                "Auf 2025 wird die feste Grenze nur angewendet; die spätere Verteilung darf anders aussehen."
            )
            """,
        ),
        code(
            "learn-section-case",
            """
            ci.abschnitt(
                "05", "Ein echter Fall vollständig durchgerechnet",
                "ZL-00147 verbindet Ist, Prognose, zwei Monatsabweichungen und den Schwellenfaktor.",
                kontext="LERNPFAD / FALLBEISPIEL",
            )
            """,
        ),
        code(
            "learn-case-timeseries",
            """
            case_alerts = case_history[case_history["hinweis_97_5"]]
            fig = eda.timeseries_forecast(
                case_history["monat"],
                case_history["verbrauch_kwh"],
                case_history["prognose_kwh"],
                anomalien=(case_alerts["monat"], case_alerts["verbrauch_kwh"]),
                y_title="Verbrauch (kWh)",
            )
            fig.data[-1].update(name="Prüfhinweis", hoverinfo="skip", hovertemplate=None)
            fig.update_layout(hovermode="x unified")
            ci.stil(
                fig,
                f"Ein Zähler kann in verschiedenen Monaten getrennt auffällig sein · {case_id}",
                "Benchmark 2025 · rote Marker nach der 97,5-%-Lernschwelle",
                x_titel="Monat",
                y_titel="Verbrauch (kWh)",
            )
            ci.zeigen(fig)
            plot_reading(
                "August und September 2025 tragen jeweils einen roten Marker, weil beide Monate ihre eigene Schwellenprüfung überschreiten.",
                "Das sind zwei unterschiedliche Zähler-Monate desselben Zählers – kein doppelter Datensatz und kein doppeltes Zählen desselben Monats.",
                "Der rote Marker besitzt absichtlich keinen eigenen Zahlen-Hover. So erscheinen Istwert und Prüfhinweis nicht mehr mit demselben Wert doppelt.",
            )
            """,
        ),
        code(
            "learn-factor-explanation",
            """
            formula(
                "Schwellenfaktor = |VLS-Residuum| ÷ gewählte VLS-Schwelle",
                "Kleiner 1: innerhalb der Grenze · genau 1: auf der Grenze · größer 1: Prüfhinweis. Der Faktor ist keine Wahrscheinlichkeit."
            )
            selected_months = case_history[case_history["monat"].dt.month.isin([8, 9])].copy()
            case_table = selected_months[[
                "monat", "verbrauch_kwh", "prognose_kwh", "residuum_kwh",
                "residuum_vls", "faktor_97_5", "hinweis_97_5",
            ]].copy()
            case_table["Monat"] = case_table.pop("monat").dt.strftime("%m/%Y")
            case_table = case_table.rename(columns={
                "verbrauch_kwh": "Ist (kWh)",
                "prognose_kwh": "Prognose (kWh)",
                "residuum_kwh": "Residuum (kWh)",
                "residuum_vls": "Residuum (VLS-h)",
                "faktor_97_5": "Faktor",
                "hinweis_97_5": "Prüfhinweis",
            })
            for column in ["Ist (kWh)", "Prognose (kWh)", "Residuum (kWh)"]:
                case_table[column] = case_table[column].map(lambda x: de(x, 1))
            case_table["Residuum (VLS-h)"] = case_table["Residuum (VLS-h)"].map(lambda x: de(x, 3))
            case_table["Faktor"] = case_table["Faktor"].map(lambda x: de(x, 3))
            case_table["Prüfhinweis"] = case_table["Prüfhinweis"].map({True: "ja", False: "nein"})
            simple_table(case_table)

            august = selected_months[selected_months["monat"].dt.month.eq(8)].iloc[0]
            september = selected_months[selected_months["monat"].dt.month.eq(9)].iloc[0]
            individual_kwh_threshold = learning_threshold * august["vertragsleistung_kw"]
            cards([
                ("Gemeinsame Schwelle", f"{de(learning_threshold, 4)} VLS-h", "Aus dem 97,5. Perzentil der 1.397 Kalibrierungsfehler."),
                ("Zählergröße", f"{de(august['vertragsleistung_kw'], 0)} kW", "Vertragsleistung von ZL-00147."),
                ("Individuelle kWh-Grenze", f"{de(individual_kwh_threshold, 1)} kWh", "82,4304 VLS-h × 49 kW."),
            ])
            formula(
                f"August: |{de(august['residuum_kwh'], 1)} kWh| ÷ 49 kW ÷ {de(learning_threshold, 4)} h = {de(august['faktor_97_5'], 3)}",
                "Der Augustfehler ist rund viermal so groß wie die gewählte Grenze: ungewöhnlich hoch."
            )
            formula(
                f"September: |{de(september['residuum_kwh'], 1)} kWh| ÷ 49 kW ÷ {de(learning_threshold, 4)} h = {de(september['faktor_97_5'], 3)}",
                "Der Septemberfehler liegt rund 19 Prozent über der Grenze: ungewöhnlich niedrig."
            )
            """,
        ),
        code(
            "learn-factor-plot",
            """
            colors = np.where(
                case_history["hinweis_97_5"],
                theme.ROLE["anomalie"],
                theme.ROLE["residuum"],
            )
            status = np.where(case_history["hinweis_97_5"], "Prüfhinweis", "innerhalb der Grenze")
            fig = go.Figure(go.Bar(
                x=case_history["monat"], y=case_history["faktor_97_5"],
                marker_color=colors,
                customdata=np.c_[
                    case_history["abs_residuum_vls"],
                    np.repeat(learning_threshold, len(case_history)),
                    status,
                ],
                hovertemplate=(
                    "%{x|%m/%Y}<br>|VLS-Residuum| %{customdata[0]:.1f} h"
                    "<br>Schwelle %{customdata[1]:.1f} h<br>Faktor %{y:.2f}"
                    "<br>Status: %{customdata[2]}<extra></extra>"
                ),
            ))
            ci.stil(
                fig,
                f"Der Faktor zeigt die Stärke relativ zur Grenze · {case_id}",
                "Benchmark 2025 · Lernschwelle 97,5. Perzentil = ±82,4 VLS-Stunden",
                x_titel="Monat",
                y_titel="Schwellenfaktor",
            )
            fig.update_xaxes(type="date", tickformat="%m/%Y", dtick="M3")
            ci.schwellwert(fig, 1, "Grenze 1,00")
            ci.zeigen(fig)
            plot_reading(
                "Blaue Balken bleiben unter 1. Die zwei roten Balken im August und September überschreiten 1.",
                "August erreicht Faktor 4,03, September 1,19. Deshalb entstehen zwei getrennte monatliche Prüfhinweise.",
                "Faktor 4 bedeutet vierfache Schwellenüberschreitung, nicht 400 Prozent Defektwahrscheinlichkeit.",
            )
            exam_sentence(
                "Der Faktor teilt den absoluten VLS-Fehler durch die gewählte Schwelle. Ab Faktor 1 wird der Zähler-Monat vorgelegt; das ist noch kein bestätigter Defekt."
            )
            check(
                "Warum ist der September ebenfalls rot, obwohl der Ausschlag viel kleiner als im August ist?",
                "Sein Faktor beträgt 1,19 und liegt damit trotzdem über der Entscheidungsgrenze 1,00. Jeder Monat wird separat bewertet.",
            )
            """,
        ),
        code(
            "learn-quantile-change-case",
            """
            cards([
                ("97,5. Perzentil", "August und September", "Bei ±82,4 VLS-h überschreiten beide Monate die Grenze."),
                ("99. Perzentil", "Nur August", "Bei ±144,4 VLS-h bleibt August auffällig; September fällt unter Faktor 1."),
                ("Wirkung des Reglers", "Gleiche Prognosen", "Nur die Entscheidungsschwelle ändert sich. Das Modell wird nicht erneut trainiert."),
            ])
            note(
                "Lernbeispiel und Pilotannahme auseinanderhalten",
                "Die Detailrechnung verwendet 97,5 Prozent, weil sie zu deinem Screenshot mit "
                "zwei roten Monaten gehört. Im Prüfungsnotebook ist 99 Prozent als dokumentierte "
                "Pilotannahme voreingestellt. Beide stammen aus derselben Kalibrierungslogik."
            )
            """,
        ),
        code(
            "learn-section-limits",
            """
            ci.abschnitt(
                "06", "Grenzen, Betrieb und Prüfungssicherheit",
                "Was wir belastbar sagen können – und welche Aussagen noch Daten benötigen.",
                kontext="LERNPFAD / EINORDNUNG",
            )
            """,
        ),
        code(
            "learn-labels",
            """
            cards([
                ("Statistischer Ausreißer", "Extremer Wert", "Ein Wert liegt ungewöhnlich weit von einer Vergleichsverteilung entfernt."),
                ("Modellanomalie", "Unerwarteter Fehler", "Ist und Modellprognose unterscheiden sich stärker als die kalibrierte Grenze."),
                ("Prüfhinweis", "Arbeitsauftrag", "Ein Mensch soll Datenqualität, Kontext und mögliche Ursache prüfen."),
                ("Bestätigte Anomalie", "Fachliches Label", "Erst die Untersuchung bestätigt, ob wirklich ein relevanter Sachverhalt vorlag."),
            ])
            note(
                "Warum noch keine Precision und Recall?",
                "Uns fehlt derzeit für alle Fälle eine verlässliche Rückmeldung, welche Hinweise "
                "tatsächlich relevante Anomalien waren und welche nicht. Ohne diese Ground Truth "
                "wären Trefferquote und Fehlalarmquote nur erfunden."
            )
            exam_sentence(
                "Ohne bestätigte Labels messen wir ungewöhnliche Modellabweichungen, noch keine endgültige Defekterkennung."
            )
            """,
        ),
        code(
            "learn-workflow",
            """
            steps([
                (1, "Schwelle wählen", "Der Fachbereich legt ein vertretbares monatliches Prüfvolumen fest."),
                (2, "Liste priorisieren", "Starke Faktoren, kWh-Auswirkung und Datenqualitätsflags werden sichtbar."),
                (3, "Fall öffnen", "Ist, Prognose, Residuum und Historie werden gemeinsam betrachtet."),
                (4, "Kontext prüfen", "Wartung, Produktion, Stammdaten und Messwertqualität werden ergänzt."),
                (5, "Entscheidung dokumentieren", "Bestätigen, verwerfen oder zur weiteren Prüfung geben."),
                (6, "Aus Feedback lernen", "Erst bestätigte Ergebnisse ermöglichen später Precision, Recall und Schwellenoptimierung."),
            ])
            note(
                "Verbindliche fachliche Grenze",
                "Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges."
            )
            """,
        ),
        markdown(
            "learn-glossary",
            """
            ### Mini-Glossar

            | Begriff | Bedeutung in diesem Projekt |
            |---|---|
            | Zielvariable | der Wert, den das Modell lernt: Vollaststunden des Folgemonats |
            | Feature | Information, die vor dem Prognosemonat verfügbar ist |
            | Baseline | einfache Vergleichsregel wie Vormonat oder Historienmittel |
            | Fold | ein zeitlich getrennter Trainings- und Bewertungsdurchlauf |
            | Hyperparameter | vorab gewählte Einstellung für die Lernflexibilität |
            | Prognose | vom Modell erwarteter Wert |
            | Residuum | Ist minus Prognose |
            | absoluter Fehler | Betrag des Residuums ohne Richtung |
            | Kalibrierung | Festlegung der Schwelle auf vorgelagerten Fehlern |
            | Perzentil | Position in einer sortierten Werteverteilung |
            | Schwellenfaktor | absoluter VLS-Fehler geteilt durch VLS-Schwelle |
            | Prüfhinweis | Schwelle überschritten; fachliche Untersuchung erforderlich |
            | Data Leakage | unzulässige Nutzung zukünftiger oder fremder Prüfinformation |
            | Overfitting | gute Anpassung an bekannte Daten, aber schwache Übertragung auf neue Daten |
            """,
        ),
        code(
            "learn-exam-questions",
            """
            checks = [
                ("Was ist der Unterschied zwischen kW, kWh und VLS?", "kW ist Leistung, kWh eine Energiemenge. VLS teilen kWh durch kW und normalisieren damit den Verbrauch auf die Anschlussgröße."),
                ("Warum lernen wir VLS?", "Damit große und kleine Anschlüsse auf einer vergleichbareren Skala gelernt werden. Für Nutzer rechnen wir anschließend wieder in kWh zurück."),
                ("Was ist ein Lag?", "Ein bereits abgeschlossener früherer Wert, der als Merkmal für einen späteren Monat verwendet wird."),
                ("Warum kein zufälliger Split?", "Weil spätere Monate sonst Informationen für frühere Prognosen liefern könnten. Vergangenheit muss Zukunft erklären."),
                ("Wozu dienen Baselines?", "Sie zeigen, ob das Machine-Learning-Modell einfache betriebliche Regeln tatsächlich schlägt."),
                ("Was zeigt der Whisker?", "Die Standardabweichung der drei zeitlichen Fold-RMSE, nicht ein Konfidenzintervall und keine Einzelprognoseunsicherheit."),
                ("Was bedeutet das 97,5. Perzentil?", "Ungefähr 97,5 Prozent der sortierten absoluten Kalibrierungsfehler liegen bis zur Grenze von 82,4 VLS-Stunden."),
                ("Ist die Schwelle pro Zähler?", "In VLS ist sie gemeinsam. In kWh wird sie durch Multiplikation mit der jeweiligen Vertragsleistung zählerspezifisch."),
                ("Was ist der Faktor?", "Der absolute VLS-Fehler geteilt durch die gewählte VLS-Schwelle. Über 1 entsteht ein Prüfhinweis."),
                ("Ist Faktor 4 eine Wahrscheinlichkeit?", "Nein. Der Fehler ist viermal so groß wie die Schwelle; über die Defektwahrscheinlichkeit sagt das allein nichts."),
                ("Warum zwei rote Monate?", "Jeder Zähler-Monat wird einzeln bewertet. August und September können deshalb zwei getrennte Hinweise desselben Zählers sein."),
                ("Ist das Modell overfitted?", "Es gibt kein klares Signal, weil es in zeitlichen Folds und 2025 gut abschneidet. Ausschließen lässt es sich erst mit weiterem prospektivem Betrieb."),
                ("Warum keine Precision und Recall?", "Weil noch keine vollständigen fachlich bestätigten Anomalielabel vorliegen."),
            ]
            for question, answer in checks:
                check(question, answer)
            """,
        ),
        code(
            "learn-one-minute-story",
            """
            exam_sentence(
                "Wir prognostizieren die Vollaststunden des Folgemonats mit ausschließlich vorher bekannten Informationen und rechnen das Ergebnis für die Nutzung in kWh zurück. "
                "Ein lineares Modell dient als verständliche Referenz, der Random Forest gewinnt die zeitliche Validierung und schlägt 2025 auch die einfachen Baselines. "
                "Nach Eintreffen des Istwerts bilden wir das leistungsbezogene Residuum. Eine vorher auf 2024 kalibrierte Perzentilschwelle übersetzt den Fehler in einen Prüfhinweis. "
                "Der Schwellenfaktor zeigt nur, wie stark die Grenze überschritten wurde. Die abschließende Bewertung bleibt beim Menschen."
            )
            cards([
                ("Du verstehst die Daten", "Einheiten und Zeitbezug", "Du kannst kW, kWh, VLS, Lags und Leakage auseinanderhalten."),
                ("Du verstehst das Modell", "Vergleich statt Bauchgefühl", "Du kannst Baseline, Modellwahl, Hyperparameter, RMSE und Whisker erklären."),
                ("Du verstehst den Hinweis", "Vom Fehler zur Entscheidung", "Du kannst Perzentil, individuelle kWh-Grenze, Faktor und menschliche Prüfung verbinden."),
            ])
            note(
                "Wenn du irgendwo hängen bleibst",
                "Gehe nicht sofort zum Random Forest zurück. Frage zuerst: Welche Einheit sehe ich? "
                "Welcher Zeitpunkt wird prognostiziert? Ist der Istwert schon bekannt? Welche "
                "Grenze wird gerade verwendet? Mit diesen vier Fragen lässt sich fast jeder Plot einordnen."
            )
            """,
        ),
    ]

    notebook = nbformat.v4.new_notebook(cells=cells)
    notebook.metadata.update(
        {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
            "sww": {
                "builder": "scripts/build_modeling_verstehen_notebook.py",
                "data_source": "data/processed/modellierung_basis_bis_3_monate.csv",
                "source_sha256": source_hash,
                "purpose": "Lern- und Nachschlageheft zur IHK-Modellierung",
                "official_exam_notebook": "notebooks/12_modeling_ihk_lernstory.ipynb",
                "learning_quantile": 0.975,
                "official_pilot_quantile": 0.99,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            },
        }
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    output = build_notebook(args.output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
