"""Build the presentation-ready SWW forecasting and anomaly notebook."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import textwrap

import nbformat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = ROOT / "notebooks" / "10_modeling.ipynb"
DATA_SOURCE = ROOT / "data" / "raw" / "260916_verbrauch_bereinigt.csv"


def _dedent(source: str) -> str:
    return textwrap.dedent(source).strip() + "\n"


def markdown(cell_id: str, source: str):
    return nbformat.v4.new_markdown_cell(_dedent(source), id=cell_id)


def code(cell_id: str, source: str):
    return nbformat.v4.new_code_cell(_dedent(source), id=cell_id)


def build_notebook(destination: Path) -> Path:
    data_hash = hashlib.sha256(DATA_SOURCE.read_bytes()).hexdigest()

    cells = [
        markdown(
            "modeling-intro",
            """
            # Verbrauchsprognose und Anomalieerkennung

            **Von der EDA zur belastbaren Modellentscheidung.** Dieses Notebook vergleicht zwei
            fachlich begründete Zielvarianten, mehrere Modellklassen und einfache Baselines unter
            einer strikt zeitlichen Validierung. Erst nach der Auswahl innerhalb von 2024 wird das
            gewählte Modell einmalig auf 2025 bewertet.

            > **Prognosevertrag:** Am Ende des Monats *t−1* wird der Verbrauch jedes bekannten
            > Zählers für den Folgemonat *t* prognostiziert. Tatsächlich beobachtete Vormonatswerte
            > dürfen deshalb bei der rollierenden Ein-Monats-Prognose verwendet werden.

            | Akt | Leitfrage |
            | --- | --- |
            | 1. Datenbasis | Welche Beobachtungen und Qualitätsannahmen gehen ins Modell ein? |
            | 2. Versuchsaufbau | Wie verhindern Zeit-Split und Features eine Testleckage? |
            | 3. Modellwahl | Welche Zielvariante, Modellklasse und Parametrisierung generalisiert 2024 am stabilsten? |
            | 4. Finaler Test | Schlägt der eingefrorene Gewinner 2025 die Baselines? |
            | 5. Anomalien | Wie werden Residuen zu transparenten Prüfhinweisen? |
            | 6. Fazit | Welcher Nutzen ist belegt und welche Grenzen bleiben? |
            """,
        ),
        markdown(
            "modeling-usage",
            """
            <details><summary>Ausführung, Abgrenzung und Gestaltungsregeln</summary>

            1. Im Projektstamm `python -m uv sync --frozen --all-extras` ausführen.
            2. Im Notebook die Projektumgebung `.venv` als Kernel wählen und **Alle ausführen**.
            3. Die Hyperparametersuche verwendet feste Seeds und ausschließlich zeitliche Folds in 2024.

            **Lag ist nicht Log:** `lag_1` und `rolling_3` sind zeitlich verschobene historische
            Merkmale. `log1p(kWh)` ist eine alternative Transformation der Zielvariable. Beide
            Zielvarianten sehen dieselben Modellinformationen und werden nach der Rücktransformation
            mit denselben kWh-Metriken verglichen.

            Die 20 Beobachtungen über der rechnerischen Vertragsleistung werden standardmäßig nur
            markiert. `EXCLUDE_CAPACITY_FLAGS` darf erst nach fachlicher Bestätigung auf `True`
            gesetzt werden. Reale Heiztage werden grundsätzlich nicht als Prognosefeature genutzt.
            Produktionsplan und Wartung bleiben mit `PLAN_FEATURES_CONFIRMED = False` ebenfalls
            ausgeschlossen, bis historische Planstände zum jeweiligen Prognosestichtag belegt sind.

            Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges.

            </details>
            """,
        ),
        code(
            "modeling-setup",
            r'''
            from datetime import datetime, timezone
            from html import escape
            from importlib import reload
            from importlib.util import find_spec
            from pathlib import Path
            import json
            import sys

            benoetigt = (
                "numpy", "pandas", "plotly", "sklearn", "IPython", "energy_analytics"
            )
            fehlend = [name for name in benoetigt if find_spec(name) is None]
            if fehlend:
                raise RuntimeError(
                    f"Im aktiven Kernel fehlen: {', '.join(fehlend)}. "
                    f"Interpreter: {sys.executable}. Bitte im Projektstamm "
                    "`python -m uv sync --frozen --all-extras` ausführen und die .venv wählen."
                )

            import numpy as np
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            from IPython.display import HTML, display

            from sklearn.base import clone
            from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
            from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import Ridge
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            from sklearn.model_selection import GridSearchCV
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler

            from energy_analytics.visualization import eda, theme
            from energy_analytics.visualization import notebook as ci

            BASE_DIR = next(
                (
                    folder
                    for folder in (Path.cwd(), *Path.cwd().parents)
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

            DATA_PATH = BASE_DIR / "data/raw/260916_verbrauch_bereinigt.csv"
            RAW_PATH = BASE_DIR / "data/raw/verbrauch.csv"
            RANDOM_STATE = 42
            EXCLUDE_CAPACITY_FLAGS = False
            PLAN_FEATURES_CONFIRMED = False
            MIN_RELATIVE_CV_GAIN = 0.05
            ANOMALY_QUANTILE = 0.99

            ci.aktiviere(
                logo=BASE_DIR / "brand/design-system/assets/logo-sww-emblem.png",
                quelle="data/raw/260916_verbrauch_bereinigt.csv",
            )

            def de(value, digits=1):
                """German display format for narrative text."""
                if value is None or not np.isfinite(value):
                    return "—"
                return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


            def entscheidungsbox(befund, entscheidung, grenze):
                """Render the same evidence → decision → limitation rhythm after each result."""
                display(HTML(
                    ci.notebook_css()
                    + '<section class="sww-report">'
                    + '<p class="eyebrow">BEFUND → ENTSCHEIDUNG → GRENZE</p>'
                    + f'<p><strong>Befund:</strong> {escape(str(befund))}</p>'
                    + f'<p><strong>Entscheidung:</strong> {escape(str(entscheidung))}</p>'
                    + f'<p><strong>Grenze:</strong> {escape(str(grenze))}</p>'
                    + '</section>'
                ))


            def regression_metrics(y_true, y_pred):
                y_true = np.asarray(y_true, dtype=float)
                y_pred = np.asarray(y_pred, dtype=float)
                mask = np.isfinite(y_true) & np.isfinite(y_pred) & (y_true > 0)
                y_true, y_pred = y_true[mask], y_pred[mask]
                error = y_pred - y_true
                return {
                    "n": int(len(y_true)),
                    "MAE (kWh)": mean_absolute_error(y_true, y_pred),
                    "RMSE (kWh)": mean_squared_error(y_true, y_pred) ** 0.5,
                    "R²": r2_score(y_true, y_pred),
                    "WAPE (%)": np.abs(error).sum() / np.abs(y_true).sum() * 100,
                    "Bias (%)": error.sum() / y_true.sum() * 100,
                    "Median APE (%)": np.median(np.abs(error) / y_true) * 100,
                }
            ''',
        ),
        code(
            "modeling-data-preparation",
            r'''
            raw = pd.read_csv(RAW_PATH)
            df = pd.read_csv(DATA_PATH, parse_dates=["monat"])

            expected = {
                "zaehler_id", "kunde_id", "kundentyp", "vertragsleistung_kw", "monat",
                "monat_idx", "arbeitstage", "feiertage_im_monat", "mittlere_temperatur_c",
                "heiztage", "produktionsplan_index", "wartung_aktiv",
                "vormonat_verbrauch_kwh", "letzte_3_monate_durchschnitt_kwh",
                "vorjahr_monat_verbrauch_kwh", "verbrauch_kwh",
            }
            assert expected == set(df.columns), "Das Datenschema hat sich unerwartet geändert."
            assert not df.duplicated(["zaehler_id", "monat"]).any()
            assert df["vertragsleistung_kw"].gt(0).all()
            assert df["verbrauch_kwh"].notna().all()
            assert df["verbrauch_kwh"].gt(0).all()

            df = df.sort_values(["zaehler_id", "monat"]).reset_index(drop=True)
            df["wartung_aktiv"] = df["wartung_aktiv"].astype(int)
            df["stunden_im_monat"] = df["monat"].dt.days_in_month * 24
            df["dq_vertragsleistung"] = (
                df["verbrauch_kwh"]
                > df["vertragsleistung_kw"] * df["stunden_im_monat"]
            )

            # Die fachlich noch nicht bestätigten Kapazitätsfälle werden standardmäßig behalten.
            confirmed_invalid = df["dq_vertragsleistung"] & EXCLUDE_CAPACITY_FLAGS
            df["target_fuer_lags"] = df["verbrauch_kwh"].mask(confirmed_invalid)

            # Alle historischen Merkmale werden neu und strikt innerhalb eines Zählers berechnet.
            g_kwh = df.groupby("zaehler_id", sort=False)["target_fuer_lags"]
            df["lag_1_kwh"] = g_kwh.shift(1)
            df["rolling_3_kwh"] = g_kwh.transform(
                lambda s: s.shift(1).rolling(3, min_periods=3).mean()
            )
            df["lag_12_kwh"] = g_kwh.shift(12)

            df["ziel_vls"] = df["target_fuer_lags"] / df["vertragsleistung_kw"]
            df["lag_1_vls"] = df["lag_1_kwh"] / df["vertragsleistung_kw"]
            df["rolling_3_vls"] = df["rolling_3_kwh"] / df["vertragsleistung_kw"]
            df["log_lag_1_kwh"] = np.log1p(df["lag_1_kwh"])
            df["log_rolling_3_kwh"] = np.log1p(df["rolling_3_kwh"])

            df["monat_sin"] = np.sin(2 * np.pi * df["monat"].dt.month / 12)
            df["monat_cos"] = np.cos(2 * np.pi * df["monat"].dt.month / 12)
            df["log_vertragsleistung_kw"] = np.log1p(df["vertragsleistung_kw"])
            df["produktionsplan_fehlend"] = df["produktionsplan_index"].isna().astype(int)

            # Diagnose des gelieferten Rolling-Features; dieses wird ausdrücklich nicht modelliert.
            supplied = df["letzte_3_monate_durchschnitt_kwh"]
            recomputed_partial = g_kwh.transform(
                lambda s: s.shift(1).rolling(3, min_periods=1).mean()
            )
            rolling_mismatch = (
                supplied.isna().ne(recomputed_partial.isna())
                | ((supplied - recomputed_partial).abs() > 0.01)
            )
            position_in_meter = df.groupby("zaehler_id", sort=False).cumcount()
            start_window_mismatch = rolling_mismatch & position_in_meter.lt(2)
            later_rolling_mismatch = rolling_mismatch & ~position_in_meter.lt(2)
            later_rolling_max_delta = (
                (supplied - recomputed_partial).abs()[later_rolling_mismatch].max()
            )

            model_df = df[df["target_fuer_lags"].notna()].copy()
            d24 = (
                model_df[model_df["monat"].dt.year.eq(2024)]
                .sort_values(["monat", "zaehler_id"])
                .reset_index(drop=True)
            )
            d25 = (
                model_df[model_df["monat"].dt.year.eq(2025)]
                .sort_values(["monat", "zaehler_id"])
                .reset_index(drop=True)
            )
            assert d24["monat"].max() < d25["monat"].min()

            ci.ZEITRAUM = (
                f"{df['monat'].min():%m/%Y}–{df['monat'].max():%m/%Y}"
            )
            ci.titelkarte(
                "Verbrauchsprognose und Anomalieerkennung",
                "Zeitlich validierter Modellvergleich mit Vollaststunden und log1p(kWh).",
                "Datenbasis: 260916_verbrauch_bereinigt.csv · "
                f"Ausgeführt: {datetime.now(timezone.utc):%d.%m.%Y %H:%M} UTC",
                logo=BASE_DIR / "brand/design-system/assets/logo-sww-full.png",
                metriken=[
                    ("Zähler im Portfolio", de(df["zaehler_id"].nunique(), 0)),
                    ("Monatswerte im Modell", de(len(model_df), 0)),
                    ("Zeitlich getrennte Testwerte", de(len(d25), 0)),
                ],
                zeitraum=ci.ZEITRAUM,
            )
            ''',
        ),
        code(
            "modeling-chapter-data",
            '''
            ci.abschnitt(
                "01", "Datenbasis und Qualitätsannahmen",
                "Vom Rohimport zur transparent abgegrenzten Modellstichprobe.",
                kontext="MODELLIERUNG UND EVALUATION",
            )
            ''',
        ),
        markdown(
            "modeling-funnel-rationale",
            """
            ### Welche Daten werden tatsächlich modelliert?

            **Warum dieser Plot?** Ein Modellvergleich ist nur nachvollziehbar, wenn sichtbar bleibt,
            welche Zeilen bereinigt, rekonstruiert, ausgeschlossen oder lediglich markiert wurden.
            Die rechnerische Vertragsleistungsüberschreitung wird deshalb getrennt ausgewiesen und
            nicht stillschweigend als Messfehler behandelt.
            """,
        ),
        code(
            "modeling-funnel-plot",
            r'''
            funnel = pd.DataFrame({
                "Stufe": [
                    "Rohimport",
                    "Nach 30 Duplikaten",
                    "3 Sentinels rekonstruiert",
                    "Modellstichprobe",
                ],
                "Zeilen": [len(raw), len(df), len(df), len(model_df)],
            })
            fig = go.Figure(go.Bar(
                x=funnel["Zeilen"], y=funnel["Stufe"], orientation="h",
                marker_color=theme.ROLE["ist"],
                text=[de(v, 0) for v in funnel["Zeilen"]], textposition="inside",
            ))
            ci.stil(
                fig,
                "Datenqualitäts-Funnel",
                f"{df['dq_vertragsleistung'].sum()} Vertragsleistungsfälle markiert; "
                f"Ausschluss derzeit {'aktiv' if EXCLUDE_CAPACITY_FLAGS else 'nicht aktiv'}",
                x_titel="Monatswerte", y_titel="",
            )
            fig.update_yaxes(categoryorder="array", categoryarray=funnel["Stufe"][::-1])
            ci.gitter_x(fig)
            ci.zeigen(fig)

            quality = pd.DataFrame([
                ["Exakte Duplikate", int(raw.duplicated().sum()), "entfernt", "gleiche Beobachtung doppelt"],
                ["Sentinel-Zielwerte", 3, "rekonstruiert", "Wert aus dokumentierter Folgezeile"],
                ["Vertragsleistungsflag", int(df["dq_vertragsleistung"].sum()), "markiert", "fachliche Grenze unbestätigt"],
                ["Rolling-3 · erste 2 Zeilen je Zähler", int(start_window_mismatch.sum()), "nicht verwendet", "nicht aus eigener sichtbarer Historie reproduzierbar"],
                ["Rolling-3 · spätere Zeilen", int(later_rolling_mismatch.sum()), "neu berechnet", f"maximale Differenz {de(later_rolling_max_delta, 3)} kWh"],
            ], columns=["Qualitätsproblem", "Anzahl", "Behandlung", "Begründung"])
            display(ci.tabellenansicht(quality, 0))
            ''',
        ),
        code(
            "modeling-funnel-decision",
            r'''
            entscheidungsbox(
                f"Die Modellstichprobe umfasst {de(len(model_df), 0)} Monatswerte. "
                f"Beim gelieferten Rolling-3 betreffen {de(start_window_mismatch.sum(), 0)} "
                "Abweichungen die ersten zwei sichtbaren Zeilen je Zähler; danach verbleiben "
                f"{de(later_rolling_mismatch.sum(), 0)} Differenzen von höchstens "
                f"{de(later_rolling_max_delta, 3)} kWh.",
                "Alle Lag- und Rolling-Features werden im Notebook neu je Zähler erzeugt. "
                "Die 20 Vertragsleistungsfälle bleiben bis zur fachlichen Freigabe erhalten.",
                "Die Vertragsleistung ist ohne Domänenbestätigung keine bewiesene physikalische Obergrenze."
            )
            ''',
        ),
        code(
            "modeling-chapter-experiment",
            '''
            ci.abschnitt(
                "02", "Versuchsaufbau und Feature Engineering",
                "Zielvarianten, Prognoseinformationen und zeitliche Validierung.",
                kontext="MODELLIERUNG UND EVALUATION",
            )
            ''',
        ),
        markdown(
            "modeling-target-rationale",
            """
            ### Vollaststunden oder logarithmierter Verbrauch?

            **Warum dieser Plot?** Die Vertragsleistung erklärt einen großen Teil der
            Größenunterschiede zwischen den Zählern. Vollaststunden entfernen dieses Niveau
            explizit; `log1p(kWh)` behandelt die stark rechtsschiefe Verteilung multiplikativ.
            Die Grafik begründet, warum beide Varianten ernsthaft getestet werden — entscheiden
            darf anschließend ausschließlich die 2024-Validierung.
            """,
        ),
        code(
            "modeling-target-plot",
            r'''
            sample = model_df.sample(min(4000, len(model_df)), random_state=RANDOM_STATE)
            corr = np.corrcoef(
                np.log1p(model_df["vertragsleistung_kw"]),
                np.log1p(model_df["target_fuer_lags"]),
            )[0, 1]
            fig = px.scatter(
                sample,
                x="vertragsleistung_kw", y="target_fuer_lags", color="kundentyp",
                log_x=True, log_y=True, opacity=0.45,
                color_discrete_map=theme.KUNDENTYP_COLORS,
                category_orders={"kundentyp": ["Gewerbe", "Industrie", "Kommunal"]},
                hover_data=["zaehler_id", "monat"],
            )
            ci.stil(
                fig,
                "Vertragsleistung gegen Monatsverbrauch",
                f"Log-Log-Korrelation {de(corr, 2)} — Größe und Verbrauchsniveau sind eng gekoppelt",
                x_titel="Vertragsleistung (kW, logarithmisch)",
                y_titel="Verbrauch (kWh, logarithmisch)",
            )
            fig.update_traces(marker_size=6, marker_line_width=0)
            ci.zeigen(fig)
            entscheidungsbox(
                f"Die Log-Log-Korrelation beträgt {de(corr, 2)}.",
                "Vollaststunden werden als fachlich erklärbares Primärziel und log1p(kWh) "
                "als Challenger unter identischen Features getestet.",
                "Korrelation belegt keine Kausalität und entscheidet noch nicht über die bessere Prognose."
            )
            ''',
        ),
        markdown(
            "modeling-split-rationale",
            """
            ### Wie bleibt 2025 außerhalb der Modellwahl?

            **Warum dieser Plot?** Ein zufälliger Zeilensplit würde Zukunft und Vergangenheit
            mischen. Drei vorwärts laufende Folds bis Oktober 2024 wählen Zielvariante, Modell und
            Hyperparameter. November und Dezember bleiben als separates Kalibrierungsfenster für
            die Anomalieschwelle reserviert; 2025 bleibt bis zum finalen Benchmark gesperrt.
            Innerhalb eines Validierungsblocks wird monatlich rollierend prognostiziert.
            """,
        ),
        code(
            "modeling-split-plot",
            r'''
            timeline = pd.DataFrame([
                ["CV 1 · Training", "2024-01-01", "2024-04-30", "Training"],
                ["CV 1 · Validierung", "2024-05-01", "2024-06-30", "Validierung"],
                ["CV 2 · Training", "2024-01-01", "2024-06-30", "Training"],
                ["CV 2 · Validierung", "2024-07-01", "2024-08-31", "Validierung"],
                ["CV 3 · Training", "2024-01-01", "2024-08-31", "Training"],
                ["CV 3 · Validierung", "2024-09-01", "2024-10-31", "Validierung"],
                ["Schwellenkalibrierung", "2024-11-01", "2024-12-31", "Kalibrierung"],
                ["Finales Training", "2024-01-01", "2024-12-31", "Training"],
                ["Out-of-time-Test", "2025-01-01", "2025-12-31", "Test"],
            ], columns=["Phase", "Start", "Ende", "Rolle"])
            timeline[["Start", "Ende"]] = timeline[["Start", "Ende"]].apply(pd.to_datetime)
            fig = px.timeline(
                timeline, x_start="Start", x_end="Ende", y="Phase", color="Rolle",
                color_discrete_map={
                    "Training": theme.ROLE["ist"],
                    "Validierung": theme.TOKENS["text-accent"],
                    "Kalibrierung": theme.ROLE["schwellwert"],
                    "Test": theme.TOKENS["grey-400"],
                },
            )
            ci.stil(
                fig, "Zeitliche Modellselektion",
                "Imputation, Encoding, Zielwahl und Hyperparameter werden nur in 2024 gelernt",
                x_titel="Monat", y_titel="",
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_xaxes(tickformat="%m/%Y", dtick="M2")
            ci.zeigen(fig)
            ''',
        ),
        code(
            "modeling-feature-table",
            r'''
            features = pd.DataFrame([
                ["log_vertragsleistung_kw", "ja", "log1p", "aufnehmen"],
                ["arbeitstage / Feiertage", "ja", "numerisch", "aufnehmen"],
                ["Monat", "ja", "Sinus und Kosinus", "aufnehmen"],
                ["Produktionsplan / Wartung", "Snapshot nicht belegt", "Median/Indikator", "standardmäßig ausschließen"],
                ["realisierte Heiztage", "nein", "—", "Leakage: ausschließen"],
                ["lag_1 / rolling_3", "ja bei 1-Monats-Horizont", "VLS und log1p(kWh)", "zählerweise neu berechnen"],
                ["Kundentyp", "ja", "One-Hot", "aufnehmen"],
                ["Vorjahresverbrauch", "2024 strukturell leer", "—", "nur Test-Baseline"],
                ["aktuelle Abweichung/Auslastung", "nein", "—", "Leakage: ausschließen"],
            ], columns=["Feature", "Zum Stichtag bekannt?", "Transformation", "Entscheidung"])
            display(ci.tabellenansicht(features, 0))
            entscheidungsbox(
                "Das Standard-Feature-Set enthält nur Stammdaten, Kalenderdaten und mit shift(1) "
                "erzeugte Vergangenheit.",
                "Beide Zielvarianten erhalten dieselben VLS- und logarithmischen Lag-Repräsentationen.",
                "Planmerkmale dürfen erst nach Nachweis historischer Stichtags-Snapshots über den "
                "Konfigurationsschalter aktiviert werden."
            )
            ''',
        ),
        code(
            "modeling-pipeline-definition",
            r'''
            CORE_NUM_FEATURES = [
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
            PLAN_NUM_FEATURES = [
                "produktionsplan_index", "produktionsplan_fehlend", "wartung_aktiv"
            ]
            NUM_FEATURES = CORE_NUM_FEATURES + (
                PLAN_NUM_FEATURES if PLAN_FEATURES_CONFIRMED else []
            )
            CAT_FEATURES = ["kundentyp"]
            MODEL_FEATURES = NUM_FEATURES + CAT_FEATURES
            # Die rohe Vertragsleistung ist nur für die Rückrechnung des VLS-Scores nötig.
            X_COLUMNS = ["vertragsleistung_kw"] + MODEL_FEATURES

            selection_24 = d24[d24["monat"].le("2024-10-31")].reset_index(drop=True)
            calibration_24 = d24[d24["monat"].ge("2024-11-01")].reset_index(drop=True)
            fold_definitions = [
                ("2024-04-01", "2024-05-01", "2024-06-30"),
                ("2024-06-01", "2024-07-01", "2024-08-31"),
                ("2024-08-01", "2024-09-01", "2024-10-31"),
            ]
            cv_2024 = []
            for train_end, valid_start, valid_end in fold_definitions:
                train_idx = np.flatnonzero(selection_24["monat"].le(pd.Timestamp(train_end)))
                valid_idx = np.flatnonzero(
                    selection_24["monat"].between(pd.Timestamp(valid_start), pd.Timestamp(valid_end))
                )
                assert selection_24.iloc[train_idx]["monat"].max() < selection_24.iloc[valid_idx]["monat"].min()
                assert set(train_idx).isdisjoint(valid_idx)
                cv_2024.append((train_idx, valid_idx))

            category_pipe = Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ])
            linear_numeric = Pipeline([
                ("impute", SimpleImputer(
                    strategy="median", keep_empty_features=True
                )),
                ("scale", StandardScaler()),
            ])
            tree_numeric = SimpleImputer(
                strategy="median", keep_empty_features=True
            )

            linear_pre = ColumnTransformer([
                ("num", linear_numeric, NUM_FEATURES),
                ("cat", category_pipe, CAT_FEATURES),
            ])
            tree_pre = ColumnTransformer([
                ("num", tree_numeric, NUM_FEATURES),
                ("cat", category_pipe, CAT_FEATURES),
            ], sparse_threshold=0.0)

            model_spaces = {
                "Ridge": (
                    Pipeline([("pre", linear_pre), ("model", Ridge())]),
                    {"model__alpha": [0.1, 1.0, 10.0, 100.0]},
                ),
                "Random Forest": (
                    Pipeline([
                        ("pre", tree_pre),
                        ("model", RandomForestRegressor(
                            n_estimators=180, max_features=0.7,
                            n_jobs=1, random_state=RANDOM_STATE
                        )),
                    ]),
                    {
                        "model__max_depth": [8, None],
                        "model__min_samples_leaf": [5, 20],
                    },
                ),
                "HistGradientBoosting": (
                    Pipeline([
                        ("pre", tree_pre),
                        ("model", HistGradientBoostingRegressor(
                            loss="absolute_error", max_iter=300,
                            l2_regularization=1.0, early_stopping=False,
                            random_state=RANDOM_STATE,
                        )),
                    ]),
                    {
                        "model__learning_rate": [0.05, 0.10],
                        "model__max_leaf_nodes": [7, 15],
                        "model__min_samples_leaf": [50, 100],
                    },
                ),
            }

            def _wape(y_true, y_pred):
                y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
                return np.abs(y_true - y_pred).sum() / np.abs(y_true).sum()


            def neg_wape_vls(estimator, X, y_vls):
                power = X["vertragsleistung_kw"].to_numpy(float)
                actual = np.asarray(y_vls, float) * power
                predicted = np.clip(estimator.predict(X), 0, None) * power
                return -_wape(actual, predicted)


            def neg_mae_vls(estimator, X, y_vls):
                power = X["vertragsleistung_kw"].to_numpy(float)
                actual = np.asarray(y_vls, float) * power
                predicted = np.clip(estimator.predict(X), 0, None) * power
                return -mean_absolute_error(actual, predicted)


            def neg_wape_kwh(estimator, X, y_kwh):
                return -_wape(y_kwh, np.clip(estimator.predict(X), 0, None))


            def neg_mae_kwh(estimator, X, y_kwh):
                return -mean_absolute_error(y_kwh, np.clip(estimator.predict(X), 0, None))


            def predict_kwh(target_mode, estimator, X):
                raw_prediction = np.clip(estimator.predict(X), 0, None)
                if target_mode == "vls":
                    return raw_prediction * X["vertragsleistung_kw"].to_numpy(float)
                return raw_prediction
            ''',
        ),
        code(
            "modeling-chapter-selection",
            '''
            ci.abschnitt(
                "03", "Modellvergleich und Auswahl",
                "Baselines, Zielvarianten und Hyperparameter im zeitlichen 2024-Backtest.",
                kontext="MODELLIERUNG UND EVALUATION",
            )
            ''',
        ),
        markdown(
            "modeling-search-rationale",
            """
            ### Welches Modell generalisiert innerhalb 2024 am stabilsten?

            **Warum dieser Vergleich?** Ein komplexes Modell ist nur gerechtfertigt, wenn es die
            einfachen historischen Regeln stabil schlägt. Pro Modellfamilie werden mehrere
            Parametrisierungen geprüft. Auswahlmetrik ist WAPE nach der Rückrechnung in kWh;
            die Streuung zwischen den Zeitfolds dient als Stabilitätsmaß. Zusätzlich muss der
            beste ML-Kandidat die beste Baseline im CV um mindestens 5 % relativ schlagen — ein
            bewusst gesetztes Komplexitäts-Gate gegen nur marginale Verbesserungen.
            """,
        ),
        code(
            "modeling-baseline-cv",
            r'''
            baseline_columns = {
                "Vormonat": "lag_1_kwh",
                "3-Monats-Mittel": "rolling_3_kwh",
            }
            baseline_fold_rows = []
            for fold, (_, valid_idx) in enumerate(cv_2024, start=1):
                valid = selection_24.iloc[valid_idx]
                for name, column in baseline_columns.items():
                    scores = regression_metrics(valid["target_fuer_lags"], valid[column])
                    baseline_fold_rows.append({"Kandidat": name, "Fold": fold, **scores})
            baseline_cv = pd.DataFrame(baseline_fold_rows)
            baseline_summary = (
                baseline_cv.groupby("Kandidat", as_index=False)
                .agg(
                    cv_wape=("WAPE (%)", "mean"),
                    cv_wape_std=("WAPE (%)", lambda values: values.std(ddof=0)),
                    cv_mae=("MAE (kWh)", "mean"),
                )
            )
            ''',
        ),
        code(
            "modeling-grid-search",
            r'''
            X_selection = selection_24[X_COLUMNS]
            y_selection_vls = selection_24["ziel_vls"]
            y_selection_kwh = selection_24["target_fuer_lags"]

            searches = {}
            ranking_rows = []

            for model_name, (pipeline, param_grid) in model_spaces.items():
                search_vls = GridSearchCV(
                    clone(pipeline), param_grid,
                    scoring={"wape_kwh": neg_wape_vls, "mae_kwh": neg_mae_vls},
                    refit="wape_kwh", cv=cv_2024, n_jobs=1,
                    return_train_score=False, error_score="raise",
                )
                search_vls.fit(X_selection, y_selection_vls)
                searches[("vls", model_name)] = search_vls
                ranking_rows.append({
                    "Ziel": "Vollaststunden",
                    "Zielmodus": "vls",
                    "Modell": model_name,
                    "CV-WAPE (%)": -search_vls.best_score_ * 100,
                    "CV-Std. (%)": search_vls.cv_results_["std_test_wape_kwh"][search_vls.best_index_] * 100,
                    "CV-MAE (kWh)": -search_vls.cv_results_["mean_test_mae_kwh"][search_vls.best_index_],
                    "Parameter": search_vls.best_params_,
                })

                log_estimator = TransformedTargetRegressor(
                    regressor=clone(pipeline), func=np.log1p, inverse_func=np.expm1,
                    check_inverse=True,
                )
                log_grid = {f"regressor__{key}": values for key, values in param_grid.items()}
                search_log = GridSearchCV(
                    log_estimator, log_grid,
                    scoring={"wape_kwh": neg_wape_kwh, "mae_kwh": neg_mae_kwh},
                    refit="wape_kwh", cv=cv_2024, n_jobs=1,
                    return_train_score=False, error_score="raise",
                )
                search_log.fit(X_selection, y_selection_kwh)
                searches[("log_kwh", model_name)] = search_log
                ranking_rows.append({
                    "Ziel": "log1p(kWh)",
                    "Zielmodus": "log_kwh",
                    "Modell": model_name,
                    "CV-WAPE (%)": -search_log.best_score_ * 100,
                    "CV-Std. (%)": search_log.cv_results_["std_test_wape_kwh"][search_log.best_index_] * 100,
                    "CV-MAE (kWh)": -search_log.cv_results_["mean_test_mae_kwh"][search_log.best_index_],
                    "Parameter": search_log.best_params_,
                })

            cv_ranking = pd.DataFrame(ranking_rows).sort_values(
                ["CV-WAPE (%)", "CV-Std. (%)"]
            ).reset_index(drop=True)
            winner = cv_ranking.iloc[0]
            winner_key = (winner["Zielmodus"], winner["Modell"])
            selection_champion = searches[winner_key].best_estimator_

            best_baseline_cv = baseline_summary.sort_values("cv_wape").iloc[0]
            relative_cv_gain = 1 - winner["CV-WAPE (%)"] / best_baseline_cv["cv_wape"]
            complexity_gate_passed = relative_cv_gain >= MIN_RELATIVE_CV_GAIN

            # Erst nach abgeschlossener Auswahl wird der Champion auf ganz 2024 refittet.
            X24 = d24[X_COLUMNS]
            y24_vls = d24["ziel_vls"]
            y24_kwh = d24["target_fuer_lags"]
            y24_winner = y24_vls if winner_key[0] == "vls" else y24_kwh
            champion = clone(selection_champion).fit(X24, y24_winner)
            ''',
        ),
        code(
            "modeling-validation-plot",
            r'''
            candidates = pd.concat([
                cv_ranking.assign(
                    Kandidat=lambda d: d["Ziel"] + " · " + d["Modell"],
                    Typ="Modell",
                )[["Kandidat", "CV-WAPE (%)", "CV-Std. (%)", "Typ"]],
                baseline_summary.rename(columns={
                    "cv_wape": "CV-WAPE (%)", "cv_wape_std": "CV-Std. (%)"
                }).assign(Typ="Baseline")[["Kandidat", "CV-WAPE (%)", "CV-Std. (%)", "Typ"]],
            ], ignore_index=True).sort_values("CV-WAPE (%)", ascending=False)

            colors = [
                theme.TOKENS["grey-400"] if kind == "Baseline"
                else theme.ROLE["prognose"]
                for kind in candidates["Typ"]
            ]
            fig = go.Figure(go.Bar(
                x=candidates["CV-WAPE (%)"], y=candidates["Kandidat"],
                orientation="h", marker_color=colors,
                error_x=dict(type="data", array=candidates["CV-Std. (%)"], visible=True),
                text=[f"{de(v, 1)} %" for v in candidates["CV-WAPE (%)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig, "Zeitlicher Validierungsvergleich 2024",
                "Balken: mittlerer WAPE; Fehlerbalken: Streuung der drei vorwärts laufenden Folds",
                x_titel="WAPE (%) — niedriger ist besser", y_titel="",
            )
            ci.prozent_achse(fig, "x", 0)
            ci.gitter_x(fig)
            ci.zeigen(fig)

            shown = cv_ranking.copy()
            shown["Parameter"] = shown["Parameter"].map(
                lambda p: json.dumps(p, ensure_ascii=False, sort_keys=True)
            )
            display(ci.tabellenansicht(
                shown[["Ziel", "Modell", "CV-WAPE (%)", "CV-Std. (%)", "CV-MAE (kWh)", "Parameter"]],
                2,
            ))
            entscheidungsbox(
                f"Der niedrigste 2024-CV-WAPE stammt von {winner['Ziel']} mit "
                f"{winner['Modell']} ({de(winner['CV-WAPE (%)'], 2)} %).",
                f"Der relative Vorsprung zur besten Baseline ({best_baseline_cv['Kandidat']}) "
                f"beträgt {de(relative_cv_gain * 100, 1)} %. Damit ist das vorab gesetzte "
                f"Komplexitäts-Gate von {de(MIN_RELATIVE_CV_GAIN * 100, 0)} % "
                f"{'bestanden' if complexity_gate_passed else 'nicht bestanden'}.",
                "Drei Zeitfolds bilden nur ein Jahr ab; kleine Rangunterschiede sind nicht automatisch praktisch relevant."
            )
            ''',
        ),
        code(
            "modeling-chapter-test",
            '''
            ci.abschnitt(
                "04", "Finale Out-of-time-Evaluation",
                "Der eingefrorene Gewinner gegen drei einfache Baselines im Jahr 2025.",
                kontext="MODELLIERUNG UND EVALUATION",
            )
            ''',
        ),
        markdown(
            "modeling-test-rationale",
            """
            ### Schlägt das gewählte Modell die einfachen Regeln?

            **Warum dieser Plot?** Der zentrale Erfolgsnachweis ist nicht ein hoher isolierter
            R²-Wert, sondern der faire Vergleich auf denselben Testzeilen. Visualisiert wird WAPE;
            MAE, RMSE, R², Bias und Stichprobengröße stehen ergänzend in der Tabelle.
            """,
        ),
        code(
            "modeling-final-evaluation",
            r'''
            X25 = d25[X_COLUMNS]
            predicted_25 = predict_kwh(winner_key[0], champion, X25)
            scored_25 = d25.copy()
            scored_25["prognose_kwh"] = predicted_25

            final_candidates = {
                f"Gewähltes Modell · {winner['Modell']}": "prognose_kwh",
                "Vormonat": "lag_1_kwh",
                "3-Monats-Mittel": "rolling_3_kwh",
                "Vorjahresmonat": "lag_12_kwh",
            }
            common = scored_25[["target_fuer_lags", *final_candidates.values()]].notna().all(axis=1)
            final_rows = []
            for name, column in final_candidates.items():
                final_rows.append({
                    "Kandidat": name,
                    **regression_metrics(
                        scored_25.loc[common, "target_fuer_lags"],
                        scored_25.loc[common, column],
                    ),
                })
            final_metrics = pd.DataFrame(final_rows).sort_values("WAPE (%)").reset_index(drop=True)

            champion_name = f"Gewähltes Modell · {winner['Modell']}"
            champion_metrics = final_metrics.set_index("Kandidat").loc[champion_name]
            baseline_metrics = final_metrics[~final_metrics["Kandidat"].eq(champion_name)]
            best_baseline = baseline_metrics.sort_values("WAPE (%)").iloc[0]
            improvement = 1 - champion_metrics["WAPE (%)"] / best_baseline["WAPE (%)"]

            plot_order = final_metrics.sort_values("WAPE (%)", ascending=False)
            fig = go.Figure(go.Bar(
                x=plot_order["WAPE (%)"], y=plot_order["Kandidat"], orientation="h",
                marker_color=[
                    theme.ROLE["prognose"] if name == champion_name else theme.TOKENS["grey-400"]
                    for name in plot_order["Kandidat"]
                ],
                text=[f"{de(v, 2)} %" for v in plot_order["WAPE (%)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig, "Finaler Benchmark im Testjahr 2025",
                f"Alle Kandidaten auf denselben {de(common.sum(), 0)} Zähler-Monaten",
                x_titel="WAPE (%) — niedriger ist besser", y_titel="",
            )
            ci.prozent_achse(fig, "x", 0)
            ci.gitter_x(fig)
            ci.zeigen(fig)
            display(ci.tabellenansicht(final_metrics, 2))

            entscheidungsbox(
                f"Das gewählte Modell erreicht {de(champion_metrics['WAPE (%)'], 2)} % WAPE "
                f"und {de(champion_metrics['MAE (kWh)'], 0)} kWh MAE. Die beste Baseline "
                f"ist {best_baseline['Kandidat']} mit {de(best_baseline['WAPE (%)'], 2)} % WAPE.",
                f"Die relative WAPE-Verbesserung beträgt {de(improvement * 100, 1)} %. "
                "Die Modellwahl bleibt unverändert, auch wenn eine Baseline im Test besser sein sollte.",
                "2025 wurde bereits in der vorausgehenden Gesamt-EDA betrachtet und ist daher ein "
                "Out-of-time-Benchmark, kein vollkommen ungesehener Datensatz."
            )
            ''',
        ),
        markdown(
            "modeling-portfolio-rationale",
            """
            ### Ist das Modell auch für die Beschaffungsmenge brauchbar?

            **Warum dieser Plot?** Zählerfehler können sich bei der Aggregation gegenseitig
            aufheben. Beschaffungstauglichkeit und Zählergenauigkeit sind deshalb zwei getrennte
            Qualitätsdimensionen.
            """,
        ),
        code(
            "modeling-portfolio-plot",
            r'''
            portfolio = (
                scored_25.groupby("monat", as_index=False)
                .agg(ist_kwh=("target_fuer_lags", "sum"), prognose_kwh=("prognose_kwh", "sum"))
            )
            portfolio_metrics = regression_metrics(portfolio["ist_kwh"], portfolio["prognose_kwh"])
            fig = eda.timeseries_forecast(
                portfolio["monat"], portfolio["ist_kwh"] / 1e6,
                portfolio["prognose_kwh"] / 1e6,
                y_title="Portfolioverbrauch (GWh)",
            )
            ci.stil(
                fig, "Portfolio-Ist gegen Portfolio-Prognose",
                f"Aggregierter WAPE {de(portfolio_metrics['WAPE (%)'], 2)} % · "
                f"Bias {de(portfolio_metrics['Bias (%)'], 2)} %",
                y_titel="Portfolioverbrauch (GWh)",
            )
            ci.zeigen(fig)
            entscheidungsbox(
                f"Auf Portfolioebene beträgt der WAPE {de(portfolio_metrics['WAPE (%)'], 2)} % "
                f"bei einem Bias von {de(portfolio_metrics['Bias (%)'], 2)} %.",
                "Beschaffungsnutzen wird separat von der zählerweisen Prognosegüte berichtet.",
                "Ein niedriger Portfoliofehler kann durch Fehlerkompensation entstehen."
            )
            ''',
        ),
        markdown(
            "modeling-parity-rationale",
            """
            ### Wo liegt das Modell systematisch falsch?

            **Warum dieser Plot?** Der Parity-Plot zeigt Über- und Unterprognosen über die gesamte
            Größenordnung. Die Segmenttabelle prüft zusätzlich, ob ein gemeinsames Modell einzelne
            Kundentypen benachteiligt.
            """,
        ),
        code(
            "modeling-parity-plot",
            r'''
            fig = eda.parity(
                scored_25["target_fuer_lags"], scored_25["prognose_kwh"],
                x_title="Prognose (kWh)", y_title="Ist (kWh)",
            )
            ci.stil(
                fig, "Ist gegen Prognose im Testjahr",
                "Punkte oberhalb der Diagonale sind Unterprognosen; darunter liegen Überprognosen",
                x_titel="Prognose (kWh)", y_titel="Ist (kWh)",
            )
            fig.update_traces(marker_opacity=0.35, selector=dict(mode="markers"))
            ci.zeigen(fig)

            segment_rows = []
            for customer_type, part in scored_25.groupby("kundentyp", observed=True):
                segment_rows.append({
                    "Kundentyp": customer_type,
                    **regression_metrics(part["target_fuer_lags"], part["prognose_kwh"]),
                })
            segment_metrics = pd.DataFrame(segment_rows)
            display(ci.tabellenansicht(segment_metrics, 2))
            ''',
        ),
        markdown(
            "modeling-importance-rationale",
            """
            ### Welche Informationen tragen zur Prognose bei?

            **Warum dieser Plot?** Eine gruppierte Permutation Importance misst post-hoc den
            WAPE-Anstieg, wenn zusammengehörige Merkmale gemeinsam vertauscht werden. So bleiben
            beispielsweise Sinus/Kosinus und die beiden Darstellungen der Verbrauchshistorie
            konsistent. Diese reine Testdiagnose verändert weder Modellwahl noch Kennzahlen.
            """,
        ),
        code(
            "modeling-permutation-importance",
            r'''
            rng = np.random.default_rng(RANDOM_STATE)
            X_importance = X25.copy()
            base_wape = regression_metrics(
                scored_25["target_fuer_lags"], scored_25["prognose_kwh"]
            )["WAPE (%)"]
            feature_groups = {
                "Vertragsleistung inkl. Rückrechnung": [
                    "vertragsleistung_kw", "log_vertragsleistung_kw"
                ],
                "Verbrauchshistorie": [
                    "lag_1_vls", "rolling_3_vls",
                    "log_lag_1_kwh", "log_rolling_3_kwh",
                ],
                "Kalenderlage": [
                    "arbeitstage", "feiertage_im_monat", "monat_sin", "monat_cos"
                ],
                "Kundentyp": ["kundentyp"],
            }
            if PLAN_FEATURES_CONFIRMED:
                feature_groups["Produktionsplan"] = [
                    "produktionsplan_index", "produktionsplan_fehlend"
                ]
                feature_groups["Wartung"] = ["wartung_aktiv"]

            importance_rows = []
            for feature_group, columns in feature_groups.items():
                deltas = []
                for _ in range(5):
                    shuffled = X_importance.copy()
                    permutation = rng.permutation(len(shuffled))
                    shuffled.loc[:, columns] = X_importance.iloc[permutation][columns].to_numpy()
                    permuted_prediction = predict_kwh(winner_key[0], champion, shuffled)
                    permuted_wape = regression_metrics(
                        scored_25["target_fuer_lags"], permuted_prediction
                    )["WAPE (%)"]
                    deltas.append(permuted_wape - base_wape)
                importance_rows.append({
                    "Feature": feature_group,
                    "WAPE-Anstieg": np.mean(deltas),
                    "Streuung": np.std(deltas),
                })
            importance = pd.DataFrame(importance_rows).sort_values("WAPE-Anstieg")

            fig = eda.feature_importance(
                importance["Feature"].tolist(), importance["WAPE-Anstieg"].tolist(),
                x_title="WAPE-Anstieg (Prozentpunkte)",
            )
            order = np.argsort(importance["WAPE-Anstieg"].to_numpy())
            fig.update_traces(error_x=dict(
                type="data", array=importance["Streuung"].to_numpy()[order], visible=True
            ))
            ci.stil(
                fig, "Gruppierte Permutation Importance · post-hoc 2025",
                "Mittelwert und Streuung aus fünf gemeinsamen Permutationen je Merkmalsgruppe",
                x_titel="WAPE-Anstieg (Prozentpunkte)", y_titel="",
            )
            ci.zeigen(fig)

            top_features = importance.nlargest(3, "WAPE-Anstieg")["Feature"].tolist()
            entscheidungsbox(
                "Die stärksten prädiktiven Merkmalsgruppen sind " + ", ".join(top_features) + ".",
                "Das Ergebnis dient ausschließlich als nachgelagerte Erklärung und erzeugt "
                "Hypothesen für ein künftiges Monitoring.",
                "Der 2025-Holdout wird hier nach Abschluss der Leistungsbewertung geöffnet; "
                "die Importance ist nicht kausal und darf nicht zur nachträglichen Modellauswahl dienen."
            )
            ''',
        ),
        code(
            "modeling-chapter-anomaly",
            '''
            ci.abschnitt(
                "05", "Residualbasierte Anomalieerkennung",
                "Ein separates 2024-Holdout übersetzt Prognosefehler in eine robuste Prüfregel.",
                kontext="MODELLIERUNG UND EVALUATION",
            )
            ''',
        ),
        markdown(
            "modeling-residual-rationale",
            """
            ### Woher kommt die Anomalieschwelle?

            **Warum dieser Plot?** Die Schwelle darf nicht aus dem Testjahr, den Auswahlfolds oder
            In-sample-Residuen stammen. Der bis Oktober ausgewählte und trainierte Champion wird
            deshalb unverändert auf November und Dezember 2024 angewendet. Die logarithmischen
            Residuen werden je Kundentyp robust um Median und MAD skaliert.
            """,
        ),
        code(
            "modeling-calibration-holdout",
            r'''
            X_calibration = calibration_24[X_COLUMNS]
            calibration_prediction = predict_kwh(
                winner_key[0], selection_champion, X_calibration
            )
            calibration_residuals = calibration_24[[
                "zaehler_id", "monat", "kundentyp", "target_fuer_lags"
            ]].copy()
            calibration_residuals["prognose_kwh"] = calibration_prediction
            calibration_residuals["residuum_log"] = (
                np.log1p(calibration_residuals["target_fuer_lags"])
                - np.log1p(calibration_residuals["prognose_kwh"].clip(lower=0))
            )

            def robust_scale(values):
                values = np.asarray(values, float)
                center = np.median(values)
                mad = np.median(np.abs(values - center))
                return max(1.4826 * mad, 1e-6)

            residual_reference = (
                calibration_residuals.groupby("kundentyp", observed=True)["residuum_log"]
                .agg(mitte="median", skala=robust_scale)
            )
            calibration_residuals = calibration_residuals.join(
                residual_reference, on="kundentyp"
            )
            calibration_residuals["score_signiert"] = (
                calibration_residuals["residuum_log"] - calibration_residuals["mitte"]
            ) / calibration_residuals["skala"]
            calibration_residuals["anomalie_score"] = (
                calibration_residuals["score_signiert"].abs()
            )
            anomaly_threshold = calibration_residuals["anomalie_score"].quantile(
                ANOMALY_QUANTILE
            )

            fig = eda.residual_hist(
                calibration_residuals["score_signiert"], anomaly_threshold,
                x_title="Robust skaliertes Log-Residuum", nbins=60,
            )
            if fig.layout.annotations:
                fig.layout.annotations[0].text = f"Schwellwert ±{de(anomaly_threshold, 2)}"
            ci.stil(
                fig, "Kalibrierungsresiduen · November–Dezember 2024",
                f"Separates Holdout · Schwelle: {de(ANOMALY_QUANTILE * 100, 1)}. Perzentil",
                x_titel="Robust skaliertes Log-Residuum", y_titel="Anzahl",
            )
            fig.update_xaxes(tickformat=",~g")
            ci.zeigen(fig)
            ''',
        ),
        markdown(
            "modeling-threshold-rationale",
            """
            ### Welche Alertmenge ist operativ tragbar?

            **Warum dieser Plot?** Eine statistische Schwelle ist zugleich eine Entscheidung über
            Arbeitsaufwand und das Verhältnis von übersehenen zu unnötigen Prüfhinweisen. Die
            Alternativen werden sichtbar gemacht; 99 % ist eine dokumentierte Arbeitshypothese.
            """,
        ),
        code(
            "modeling-threshold-plot",
            r'''
            threshold_options = []
            for quantile in (0.90, 0.95, 0.975, 0.99, 0.995):
                threshold = calibration_residuals["anomalie_score"].quantile(quantile)
                alerts = int(calibration_residuals["anomalie_score"].ge(threshold).sum())
                threshold_options.append({
                    "Perzentil": quantile * 100,
                    "Schwelle": threshold,
                    "Alerts je Monat": alerts / calibration_residuals["monat"].nunique(),
                })
            threshold_table = pd.DataFrame(threshold_options)
            fig = go.Figure(go.Scatter(
                x=threshold_table["Perzentil"], y=threshold_table["Alerts je Monat"],
                mode="lines+markers+text", line=dict(color=theme.ROLE["residuum"], width=2),
                marker=dict(size=8),
                text=[de(v, 1) for v in threshold_table["Alerts je Monat"]],
                textposition="top center",
            ))
            ci.stil(
                fig, "Kalibrierungsniveau gegen Prüfaufwand",
                "Erwartete monatliche Hinweise aus dem separaten Kalibrierungsfenster 2024",
                x_titel="Perzentil des absoluten Anomalie-Scores",
                y_titel="Prüfhinweise je Monat",
            )
            ci.referenzlinie(
                fig, ANOMALY_QUANTILE * 100,
                f"Arbeitshypothese {de(ANOMALY_QUANTILE * 100, 1)} %",
                achse="x", position="top left",
            )
            ci.zeigen(fig)
            display(ci.tabellenansicht(threshold_table, 2))
            ''',
        ),
        markdown(
            "modeling-alert-distribution-rationale",
            """
            ### Wann und in welchen Segmenten entsteht Prüfaufwand?

            **Warum dieser Plot?** Die feste Kalibrierungsregel wird unverändert auf 2025
            angewendet. Der Monatsverlauf zeigt Lastspitzen für den Prüfprozess; die ergänzende
            Segmenttabelle macht sichtbar, ob ein Kundentyp überproportional häufig markiert wird.
            Einzelne Hinweise bleiben anschließend anhand von Ist, Prognose und Kontext prüfbar.
            """,
        ),
        code(
            "modeling-test-anomalies",
            r'''
            scored_25["residuum_log"] = (
                np.log1p(scored_25["target_fuer_lags"])
                - np.log1p(scored_25["prognose_kwh"].clip(lower=0))
            )
            scored_25 = scored_25.join(residual_reference, on="kundentyp")
            scored_25["score_signiert"] = (
                scored_25["residuum_log"] - scored_25["mitte"]
            ) / scored_25["skala"]
            scored_25["anomalie_score"] = scored_25["score_signiert"].abs()
            scored_25["anomalie"] = scored_25["anomalie_score"].ge(anomaly_threshold)
            scored_25["richtung"] = np.where(
                scored_25["score_signiert"].ge(0),
                "ungewöhnlich hoch", "ungewöhnlich niedrig",
            )
            scored_25["abweichung_kwh"] = (
                scored_25["target_fuer_lags"] - scored_25["prognose_kwh"]
            )
            scored_25["abweichung_prozent"] = (
                scored_25["abweichung_kwh"]
                / scored_25["prognose_kwh"].clip(lower=1) * 100
            )

            anomaly_counts = (
                scored_25[scored_25["anomalie"]]
                .groupby(["monat", "kundentyp"], observed=True)
                .size().unstack(fill_value=0)
                .reindex(columns=["Gewerbe", "Industrie", "Kommunal"], fill_value=0)
            )
            fig = eda.anomaly_stack(
                anomaly_counts.index,
                {column: anomaly_counts[column] for column in anomaly_counts.columns},
            )
            ci.stil(
                fig, "Prüfhinweise im Testjahr",
                f"Feste 2024-Schwelle · insgesamt {int(scored_25['anomalie'].sum())} Hinweise",
                x_titel="Monat", y_titel="Anzahl Prüfhinweise",
            )
            fig.update_xaxes(tickformat="%m/%Y", dtick="M2")
            ci.zeigen(fig)

            alert_segments = (
                scored_25.groupby("kundentyp", observed=True)["anomalie"]
                .agg(Beobachtungen="size", Prüfhinweise="sum", Quote="mean")
                .reset_index().rename(columns={"kundentyp": "Kundentyp"})
            )
            alert_segments["Quote (%)"] = alert_segments.pop("Quote") * 100
            display(ci.tabellenansicht(alert_segments, 2))

            top_anomalies = (
                scored_25[scored_25["anomalie"]]
                .sort_values("anomalie_score", ascending=False)
                [[
                    "zaehler_id", "monat", "kundentyp", "target_fuer_lags",
                    "prognose_kwh", "abweichung_kwh", "abweichung_prozent",
                    "anomalie_score", "richtung", "wartung_aktiv", "produktionsplan_index",
                    "dq_vertragsleistung",
                ]]
                .head(20)
                .rename(columns={
                    "target_fuer_lags": "Ist (kWh)",
                    "prognose_kwh": "Prognose (kWh)",
                    "abweichung_kwh": "Abweichung (kWh)",
                    "abweichung_prozent": "Abweichung (%)",
                    "anomalie_score": "Score",
                })
            )
            display(ci.tabellenansicht(top_anomalies, 2))
            ''',
        ),
        markdown(
            "modeling-case-rationale",
            """
            ### Wie sieht ein konkreter Prüfhinweis aus?

            **Warum dieser Plot?** Ein einzelner, regelbasiert ausgewählter Fall verbindet Score,
            Verbrauchsverlauf und Prognose. Dadurch wird deutlich, dass der Algorithmus keine
            Fehlerursache diagnostiziert, sondern einen priorisierten Untersuchungsfall erzeugt.
            """,
        ),
        code(
            "modeling-case-plot",
            r'''
            if scored_25["anomalie"].any():
                case_id = scored_25.loc[
                    scored_25["anomalie_score"].idxmax(), "zaehler_id"
                ]
                case = scored_25[scored_25["zaehler_id"].eq(case_id)].sort_values("monat")
                flagged = case[case["anomalie"]]
                fig = eda.timeseries_forecast(
                    case["monat"], case["target_fuer_lags"], case["prognose_kwh"],
                    anomalien=(flagged["monat"], flagged["target_fuer_lags"]),
                    y_title="Verbrauch (kWh)",
                )
                ci.stil(
                    fig, f"Fallbeispiel {case_id}",
                    "Automatisch gewählt: höchster Anomalie-Score im Testjahr",
                    y_titel="Verbrauch (kWh)",
                )
                ci.zeigen(fig)

            alerts_per_month = scored_25["anomalie"].sum() / scored_25["monat"].nunique()
            entscheidungsbox(
                f"Die feste 2024-Schwelle erzeugt 2025 insgesamt "
                f"{int(scored_25['anomalie'].sum())} Hinweise beziehungsweise "
                f"{de(alerts_per_month, 1)} pro Monat.",
                "Hinweise werden mit Richtung, Kontext und Datenqualitätsflag an eine menschliche "
                "Prüfung übergeben.",
                "Ohne gelabelte reale Anomalien sind keine belastbaren Precision-/Recall-Aussagen "
                "möglich; die globale Schwelle optimiert den Gesamtaufwand, nicht gleiche Segmentquoten."
            )
            ''',
        ),
        code(
            "modeling-chapter-conclusion",
            '''
            ci.abschnitt(
                "06", "Fazit und Einsatzentscheidung",
                "Ergebnis, Nutzen, Grenzen und nächste fachliche Schritte.",
                kontext="MODELLIERUNG UND EVALUATION",
            )
            ''',
        ),
        code(
            "modeling-scorecard",
            r'''
            result_scorecard = pd.DataFrame([
                ["Gewähltes Ziel", winner["Ziel"]],
                ["Gewähltes Modell", winner["Modell"]],
                ["Feature-Set", "operativ konservativ" if not PLAN_FEATURES_CONFIRMED else "bestätigte Planmerkmale"],
                ["2024 CV-WAPE", f"{de(winner['CV-WAPE (%)'], 2)} %"],
                ["Komplexitäts-Gate", f"{de(relative_cv_gain * 100, 1)} % CV-Vorsprung · " + ("bestanden" if complexity_gate_passed else "nicht bestanden")],
                ["2025 Test-WAPE", f"{de(champion_metrics['WAPE (%)'], 2)} %"],
                ["2025 Test-MAE", f"{de(champion_metrics['MAE (kWh)'], 0)} kWh"],
                ["2025 Test-RMSE", f"{de(champion_metrics['RMSE (kWh)'], 0)} kWh"],
                ["2025 Test-R²", de(champion_metrics["R²"], 3)],
                ["Verbesserung zur besten Baseline", f"{de(improvement * 100, 1)} %"],
                ["Anomalieschwelle", f"{de(ANOMALY_QUANTILE * 100, 1)}. Perzentil · Score {de(anomaly_threshold, 2)}"],
                ["Prüfhinweise 2025", f"{int(scored_25['anomalie'].sum())} · {de(alerts_per_month, 1)} je Monat"],
                ["Top-3-Merkmalsgruppen · post-hoc", ", ".join(top_features)],
            ], columns=["Prüffrage", "Ergebnis"])
            display(ci.tabellenansicht(result_scorecard, 2))

            model_beats_baseline = (
                complexity_gate_passed
                and champion_metrics["WAPE (%)"] < best_baseline["WAPE (%)"]
            )
            einsatz = (
                "Das Modell zeigt einen messbaren Mehrwert gegenüber der stärksten Baseline."
                if model_beats_baseline
                else "Die stärkste Baseline ist im Test mindestens gleichwertig; ein komplexeres "
                     "Modell ist derzeit nicht ausreichend gerechtfertigt."
            )
            entscheidungsbox(
                einsatz,
                "Die Prognose kann als Entscheidungsunterstützung und die Residualregel als "
                "priorisierter Prüfprozess weiterentwickelt werden.",
                "Nur 24 Monate Historie, ungeklärte Vertragsleistungsflags, zwei Monate "
                "Schwellenkalibrierung und keine echten Anomalielabels begrenzen die Aussage."
            )
            ''',
        ),
        markdown(
            "modeling-final-text",
            """
            ## Schlussfolgerung

            Die Modellwahl folgt einer nachvollziehbaren Kette: Datenqualitätsannahmen werden
            offengelegt, historische Features werden zählerweise neu berechnet, Zielvarianten und
            Hyperparameter werden bis Oktober 2024 verglichen, die Schwelle wird separat in
            November/Dezember kalibriert und der Gewinner wird erst danach auf 2025 bewertet.
            Die Rückrechnung stellt sicher, dass Vollaststunden und
            `log1p(kWh)` immer auf derselben geschäftlichen Einheit verglichen werden.

            **Geschäftlicher Nutzen**

            - zählerweise Monatsprognosen als Grundlage der Mengenplanung,
            - separate Portfolioauswertung für die Beschaffung,
            - transparente Prüfhinweise für ungewöhnlich hohe oder niedrige Verbräuche.

            **Grenzen**

            - nur zwei vollständige Jahreszyklen,
            - keine gelabelten echten Anomalien,
            - Vertragsleistung als harte Grenze fachlich nicht bestätigt,
            - reale Heiztage sind ausgeschlossen; Produktionsplan und Wartung benötigen vor einer
              Aktivierung nachweisbare historische Stichtags-Snapshots.

            **Nächste Schritte**

            1. kanonischen `data/raw → data/processed`-Lauf festschreiben,
            2. Vertragsleistungsfälle fachlich prüfen und Sensitivität berichten,
            3. längere Historie und archivierte Wetterprognosen ergänzen,
            4. Kosten von Über- und Unterbeschaffung in die Zielmetrik aufnehmen,
            5. Hinweise mit dem Netzmanagement labeln und die Schwelle anschließend neu bewerten.

            > Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges.
            """,
        ),
    ]

    notebook = nbformat.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "westhafen-energy-analytics (3.11.9)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
            "sww": {
                "builder": "scripts/build_modeling_notebook.py",
                "data_source": "data/raw/260916_verbrauch_bereinigt.csv",
                "data_sha256": data_hash,
                "design_source": "brand/design-system/tokens/design-tokens.json",
                "forecast_horizon": "rolling one month ahead",
                "train_period": "2024-01 through 2024-12",
                "test_period": "2025-01 through 2025-12",
                "random_state": 42,
            },
        },
    )
    nbformat.validate(notebook)
    destination.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    destination = args.output
    if not destination.is_absolute():
        destination = ROOT / destination
    print(build_notebook(destination))


if __name__ == "__main__":
    main()
