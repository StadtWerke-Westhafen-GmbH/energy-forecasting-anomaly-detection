"""Build the reproducible SWW challenger-modeling notebook."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import textwrap

import nbformat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = ROOT / "notebooks" / "20_modeling_optimierung.ipynb"
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
            "optimization-intro",
            r"""
            # Challenger-Labor: Prognosequalität gezielt maximieren

            **Wie weit kommen wir mit sauberem Feature Engineering, einer kompakten
            Hyperparametersuche und konsequenter Zeitvalidierung?** Dieses zweite Notebook lässt
            das bestehende Modeling-Notebook unverändert und baut einen stärkeren Challenger auf.

            Die zentrale Modellidee lautet:

            $$
            z = \log\left(1 + \frac{\mathrm{Verbrauch\ (kWh)}}
            {\mathrm{Vertragsleistung\ (kW)}}\right)
            $$

            Nach der Prognose wird vollständig zurückgerechnet:

            $$
            \widehat{\mathrm{kWh}} = \max\left(\exp(\hat z)-1, 0\right)
            \cdot \mathrm{Vertragsleistung\ (kW)}.
            $$

            > **Evidenzstatus:** 2025 ist bereits bekannt und daher kein unangetasteter Test mehr.
            > Modell, Features und Hyperparameter werden ausschließlich mit den 2024-Folds
            > ausgewählt. Das 2025-Ergebnis ist ein retrospektiver Out-of-time-Benchmark. Eine
            > produktive Freigabe braucht danach einen neuen, wirklich ungesehenen Shadow-Zeitraum.

            | Kapitel | Frage |
            | --- | --- |
            | 1. Bewertungsvertrag | Was darf 2024 entscheiden – und was darf 2025 noch zeigen? |
            | 2. Feature Engineering | Welche Informationen sind zum Prognosestichtag verfügbar? |
            | 3. Modellwahl | Welche Modellfamilie, Zieltransformation und Parametrisierung gewinnt? |
            | 4. Kalibrierung | Lässt sich ein systematischer Bias vor 2025 reduzieren? |
            | 5. Rückblick 2025 | Wie groß und wie stabil ist der retrospektive Mehrwert? |
            | 6. Entscheidung | Unter welchen Bedingungen ist der Challenger einsatzfähig? |
            """,
        ),
        markdown(
            "optimization-usage",
            """
            <details><summary>Ausführung, Begriffe und bewusste Grenzen</summary>

            1. Im Projektstamm `python -m uv sync --frozen --all-extras` ausführen.
            2. Im Notebook die Projektumgebung `.venv` auswählen und **Alle ausführen**.
            3. Das Notebook nutzt feste Seeds, drei vorwärts laufende 2024-Folds und keine
               zufällige Aufteilung.

            **Lag** bedeutet zeitliche Verschiebung: `lag_1` ist der bekannte Vormonat.
            **Log** bedeutet Transformation: `log1p(x)` dämpft große Werte und kann auch null
            verarbeiten. **VLS** sind Vollaststunden, also `kWh / kW`. Ein VLS-Modell wird immer
            wieder in kWh zurückgerechnet und erst dann bewertet.

            Der Schalter `PLAN_SNAPSHOT_CONFIRMED` markiert ein konditionales Szenario: Aktueller
            Produktionsplan und Wartungsstatus dürfen nur produktiv genutzt werden, wenn ihre
            historischen, vor Monatsbeginn eingefrorenen Stände nachweisbar sind. Realisierte
            Temperatur oder Heiztage des Zielmonats bleiben ausgeschlossen.

            Der normale WAPE ist bereits mengenbezogen: große absolute Fehler gehen stärker ein.
            Zusätzliche Vertragsleistungsgewichte werden deshalb als Hypothese getestet, nicht
            automatisch verwendet.

            </details>
            """,
        ),
        code(
            "optimization-setup",
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
            from sklearn.compose import ColumnTransformer
            from sklearn.ensemble import (
                ExtraTreesRegressor,
                HistGradientBoostingRegressor,
                RandomForestRegressor,
            )
            from sklearn.impute import SimpleImputer
            from sklearn.inspection import permutation_importance
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            from sklearn.model_selection import ParameterGrid
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder

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
            RANDOM_STATE = 42
            PLAN_SNAPSHOT_CONFIRMED = False  # im Projekt noch nicht technisch nachgewiesen
            RUN_CONDITIONAL_PLAN_SCENARIO = True  # dieses Notebook quantifiziert das Potenzial
            COMPLEXITY_GATE_PP = 0.50
            CALIBRATION_GATE_PP = 0.50
            N_BOOTSTRAP = 2_000

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
                """Render the same evidence → decision → limitation rhythm."""
                display(HTML(
                    ci.notebook_css()
                    + '<section class="sww-report">'
                    + '<p class="eyebrow">BEFUND → ENTSCHEIDUNG → GRENZE</p>'
                    + f'<p><strong>Befund:</strong> {escape(str(befund))}</p>'
                    + f'<p><strong>Entscheidung:</strong> {escape(str(entscheidung))}</p>'
                    + f'<p><strong>Grenze:</strong> {escape(str(grenze))}</p>'
                    + '</section>'
                ))


            def wape(y_true, y_pred):
                actual = np.asarray(y_true, dtype=float)
                predicted = np.clip(np.asarray(y_pred, dtype=float), 0, None)
                mask = np.isfinite(actual) & np.isfinite(predicted)
                return np.abs(actual[mask] - predicted[mask]).sum() / np.abs(actual[mask]).sum() * 100


            def regression_metrics(y_true, y_pred):
                actual = np.asarray(y_true, dtype=float)
                predicted = np.clip(np.asarray(y_pred, dtype=float), 0, None)
                mask = np.isfinite(actual) & np.isfinite(predicted) & (actual > 0)
                actual, predicted = actual[mask], predicted[mask]
                error = predicted - actual
                return {
                    "n": int(len(actual)),
                    "MAE (kWh)": mean_absolute_error(actual, predicted),
                    "RMSE (kWh)": mean_squared_error(actual, predicted) ** 0.5,
                    "R²": r2_score(actual, predicted),
                    "WAPE (%)": wape(actual, predicted),
                    "Bias (%)": error.sum() / actual.sum() * 100,
                }


            def weighted_median(values, weights):
                """First weighted median; minimizes weighted absolute deviation."""
                values = np.asarray(values, dtype=float)
                weights = np.asarray(weights, dtype=float)
                valid = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
                order = np.argsort(values[valid], kind="mergesort")
                sorted_values = values[valid][order]
                sorted_weights = weights[valid][order]
                index = np.searchsorted(
                    np.cumsum(sorted_weights), sorted_weights.sum() / 2, side="left"
                )
                return float(sorted_values[min(index, len(sorted_values) - 1)])
            ''',
        ),
        code(
            "optimization-data-preparation",
            r'''
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
            assert df["verbrauch_kwh"].gt(0).all()

            df = df.sort_values(["zaehler_id", "monat"]).reset_index(drop=True)
            df["wartung_aktiv"] = df["wartung_aktiv"].astype(int)
            df["vls"] = df["verbrauch_kwh"] / df["vertragsleistung_kw"]
            df["log_vls"] = np.log1p(df["vls"])
            df["log_power"] = np.log1p(df["vertragsleistung_kw"])
            df["month_sin"] = np.sin(2 * np.pi * df["monat"].dt.month / 12)
            df["month_cos"] = np.cos(2 * np.pi * df["monat"].dt.month / 12)
            df["plan_missing"] = df["produktionsplan_index"].isna().astype(int)

            by_meter = df.groupby("zaehler_id", sort=False)
            g_kwh = by_meter["verbrauch_kwh"]
            g_vls = by_meter["vls"]

            # Jede Verbrauchshistorie beginnt mit shift(1): kein Wert aus Monat t fließt ein.
            for lag in range(1, 7):
                df[f"verbrauch_kwh_l{lag}"] = g_kwh.shift(lag)
                df[f"vls_l{lag}"] = df[f"verbrauch_kwh_l{lag}"] / df["vertragsleistung_kw"]
                df[f"logkwh_l{lag}"] = np.log1p(df[f"verbrauch_kwh_l{lag}"])

            for window in (2, 3, 4, 6):
                df[f"verbrauch_kwh_r{window}"] = g_kwh.transform(
                    lambda s, w=window: s.shift(1).rolling(w, min_periods=1).mean()
                )
                df[f"vls_r{window}"] = (
                    df[f"verbrauch_kwh_r{window}"] / df["vertragsleistung_kw"]
                )

            for window in (3, 6):
                df[f"verbrauch_kwh_s{window}"] = g_kwh.transform(
                    lambda s, w=window: s.shift(1).rolling(w, min_periods=2).std()
                )
                df[f"vls_s{window}"] = (
                    df[f"verbrauch_kwh_s{window}"] / df["vertragsleistung_kw"]
                )

            df["vls_expmean"] = g_vls.transform(
                lambda s: s.shift(1).expanding(min_periods=1).mean()
            )
            df["vls_expstd"] = g_vls.transform(
                lambda s: s.shift(1).expanding(min_periods=2).std()
            )
            df["vls_ewm3"] = g_vls.transform(
                lambda s: s.shift(1).ewm(span=3, adjust=False, min_periods=1).mean()
            )
            df["vls_trend13"] = df["vls_l1"] - df["vls_r3"]
            df["vls_trend36"] = df["vls_r3"] - df["vls_r6"]
            df["log_ratio13"] = np.log(
                (df["verbrauch_kwh_l1"] + 1) / (df["verbrauch_kwh_r3"] + 1)
            )
            df["vls_cv3"] = df["vls_s3"] / (df["vls_r3"].abs() + 1e-5)
            df["vls_cv6"] = df["vls_s6"] / (df["vls_r6"].abs() + 1e-5)

            # Plan, Arbeitstage und Wartung erhalten ausschließlich Vergangenheitsanker.
            for base in ("produktionsplan_index", "arbeitstage", "wartung_aktiv"):
                group = by_meter[base]
                df[f"{base}_l1"] = group.shift(1)
                for window in (3, 6):
                    df[f"{base}_r{window}"] = group.transform(
                        lambda s, w=window: s.shift(1).rolling(w, min_periods=1).mean()
                    )

            for base in ("produktionsplan_index", "arbeitstage"):
                for history in ("l1", "r3", "r6"):
                    df[f"{base}_ratio_{history}"] = (
                        (df[base] + 1e-4) / (df[f"{base}_{history}"] + 1e-4)
                    )
                    df[f"{base}_diff_{history}"] = df[base] - df[f"{base}_{history}"]

            # Erklärbare Startschätzungen: Historie × Planänderung × Arbeitstageänderung.
            df["expert"] = (
                df["vls_r3"]
                * df["produktionsplan_index_ratio_r3"]
                * df["arbeitstage_ratio_r3"]
            )
            df["expert_plan"] = (
                df["vls_r3"] * df["produktionsplan_index_ratio_r3"]
            )
            df["expert_lag"] = (
                df["vls_l1"]
                * df["produktionsplan_index_ratio_l1"]
                * df["arbeitstage_ratio_l1"]
            )

            # Nur für den reproduzierbaren Vergleich zum bisherigen Notebook.
            df["vls_r3_strict"] = g_kwh.transform(
                lambda s: s.shift(1).rolling(3, min_periods=3).mean()
            ) / df["vertragsleistung_kw"]
            df["logkwh_r3_strict"] = np.log1p(
                df["vls_r3_strict"] * df["vertragsleistung_kw"]
            )

            d24 = df[df["monat"].dt.year.eq(2024)].copy()
            d25 = df[df["monat"].dt.year.eq(2025)].copy()
            selection_24 = d24[d24["monat"].dt.month.le(10)].copy()
            calibration_24 = d24[d24["monat"].dt.month.ge(11)].copy()
            assert d24["monat"].max() < d25["monat"].min()
            assert len(selection_24) == 7_000 and len(calibration_24) == 1_400

            ci.ZEITRAUM = f"{df['monat'].min():%m/%Y}–{df['monat'].max():%m/%Y}"
            ci.titelkarte(
                "Challenger-Labor: maximale Prognosegüte",
                "Log-Vollaststunden, erweiterte Historien und kompakte zeitliche Modellsuche.",
                "Datenbasis: 260916_verbrauch_bereinigt.csv · "
                f"Ausgeführt: {datetime.now(timezone.utc):%d.%m.%Y %H:%M} UTC",
                logo=BASE_DIR / "brand/design-system/assets/logo-sww-full.png",
                metriken=[
                    ("Zähler", de(df["zaehler_id"].nunique(), 0)),
                    ("2024-Auswahlzeilen", de(len(selection_24), 0)),
                    ("2025-Benchmarkzeilen", de(len(d25), 0)),
                ],
                zeitraum=ci.ZEITRAUM,
            )
            ''',
        ),
        code(
            "optimization-chapter-evidence",
            '''
            ci.abschnitt(
                "01", "Bewertungsvertrag und Evidenzstatus",
                "2024 entscheidet; 2025 illustriert rückblickend; der nächste Zeitraum bestätigt prospektiv.",
                kontext="CHALLENGER-MODELLIERUNG",
            )
            ''',
        ),
        markdown(
            "optimization-evidence-rationale",
            """
            ### Was darf welche Datenphase aussagen?

            **Warum dieser Plot?** Sobald ein Ergebnis angesehen wurde, kann es unbewusst spätere
            Entscheidungen beeinflussen. Die Grafik trennt deshalb Auswahl, Kalibrierung,
            retrospektiven Benchmark und echte zukünftige Bestätigung.

            **So liest du ihn:** Nur die ersten beiden Phasen dürfen Modellbestandteile festlegen.
            2025 beantwortet nur noch: „Wie hätte der eingefrorene Prozess rückblickend
            abgeschnitten?“
            """,
        ),
        code(
            "optimization-evidence-timeline",
            r'''
            evidence = pd.DataFrame([
                ["1 · 2024 Jan–Okt", "Modellwahl", "darf entscheiden", 1],
                ["2 · 2024 Nov–Dez", "Bias-Kalibrierung", "darf entscheiden", 1],
                ["3 · 2025", "bekannter Rückblick", "darf nicht entscheiden", 0],
                ["4 · nächster Zeitraum", "Shadow-Test", "muss noch bestätigen", 2],
            ], columns=["Phase", "Rolle", "Status", "Code"])
            colors = {
                "darf entscheiden": theme.ROLE["ist"],
                "darf nicht entscheiden": theme.TOKENS["grey-400"],
                "muss noch bestätigen": theme.ROLE["schwellwert"],
            }
            fig = go.Figure()
            for status, part in evidence.groupby("Status", sort=False):
                fig.add_bar(
                    x=part["Phase"], y=[1] * len(part), name=status,
                    marker_color=colors[status], text=part["Rolle"], textposition="inside",
                    hovertemplate="%{x}<br>%{text}<extra></extra>",
                )
            ci.stil(
                fig, "Vier Evidenzstufen statt eines wiederholten Tests",
                "2025 ist bereits bekannt und bleibt vollständig außerhalb der Auswahl",
                x_titel="", y_titel="",
            )
            fig.update_layout(barmode="group", showlegend=True)
            fig.update_yaxes(visible=False, range=[0, 1.15])
            ci.zeigen(fig)
            entscheidungsbox(
                "Modellwahl und Kalibrierung enden am 31.12.2024.",
                "2025 wird erst nach dem Einfrieren des gesamten Rechenwegs ausgewertet.",
                "Weil 2025 schon aus dem ersten Notebook bekannt ist, ersetzt es keinen neuen Shadow-Test."
            )
            ''',
        ),
        markdown(
            "optimization-wape-rationale",
            r"""
            ### Warum WAPE – und warum keine automatische Zusatzgewichtung?

            **Warum dieser Plot?** WAPE addiert absolute kWh-Fehler und teilt durch den gesamten
            Verbrauch. Ein großer Anschluss beeinflusst die Kennzahl dadurch bereits stärker als
            ein kleiner. Zusätzliche Vertragsleistungsgewichte würden dieselbe Größenwirkung noch
            einmal verstärken.

            $$\mathrm{WAPE}=\frac{\sum_i|y_i-\hat y_i|}{\sum_i|y_i|}\cdot100$$
            """,
        ),
        code(
            "optimization-wape-example",
            r'''
            wape_demo = pd.DataFrame({
                "Zähler": ["klein", "mittel", "groß"],
                "Ist (kWh)": [1_000, 10_000, 100_000],
                "Prognose (kWh)": [500, 8_000, 90_000],
            })
            wape_demo["absoluter Fehler"] = (
                wape_demo["Ist (kWh)"] - wape_demo["Prognose (kWh)"]
            ).abs()
            wape_demo["Verbrauchsanteil (%)"] = (
                wape_demo["Ist (kWh)"] / wape_demo["Ist (kWh)"].sum() * 100
            )
            wape_demo["Fehlerbeitrag (%)"] = (
                wape_demo["absoluter Fehler"] / wape_demo["absoluter Fehler"].sum() * 100
            )
            fig = go.Figure([
                go.Bar(
                    name="Anteil am Verbrauch", x=wape_demo["Zähler"],
                    y=wape_demo["Verbrauchsanteil (%)"], marker_color=theme.ROLE["ist"],
                ),
                go.Bar(
                    name="Anteil am absoluten Fehler", x=wape_demo["Zähler"],
                    y=wape_demo["Fehlerbeitrag (%)"], marker_color=theme.ROLE["prognose"],
                ),
            ])
            ci.stil(
                fig, "WAPE gewichtet absolute Mengenfehler bereits",
                f"Mini-Beispiel: Gesamt-WAPE {de(wape(wape_demo['Ist (kWh)'], wape_demo['Prognose (kWh)']), 1)} %",
                x_titel="Beispielzähler", y_titel="Anteil (%)",
            )
            fig.update_layout(barmode="group")
            ci.prozent_achse(fig, "y", 0)
            ci.zeigen(fig)
            display(ci.tabellenansicht(wape_demo, 1))
            entscheidungsbox(
                "Der große Beispielzähler trägt trotz kleinerem prozentualem Fehler den größten absoluten Fehler bei.",
                "Primärmetrik bleibt WAPE in kWh; Gewichte sind ein eigener CV-Kandidat.",
                "WAPE bildet keine individuellen Kosten asymmetrischer Über- oder Unterprognosen ab."
            )
            ''',
        ),
        code(
            "optimization-chapter-features",
            '''
            ci.abschnitt(
                "02", "Feature Engineering ohne Zukunftswissen",
                "Mehr Signal aus Historie und Planung – mit klarer Stichtagslogik.",
                kontext="CHALLENGER-MODELLIERUNG",
            )
            ''',
        ),
        markdown(
            "optimization-feature-availability-rationale",
            """
            ### Welche Information ist bei einer Ein-Monats-Prognose erlaubt?

            **Warum dieser Plot?** Gute Scores sind wertlos, wenn ein Feature im Betrieb erst nach
            dem Prognosezeitpunkt vorliegt. Die Matrix ist der fachliche Leakage-Check.

            **So liest du ihn:** Grün ist verfügbar, Gelb nur unter einer dokumentierten
            Snapshot-Bedingung und Grau ausgeschlossen. Alle Verbrauchs-Rollings verwenden zuerst
            `shift(1)` und sehen den Zielmonat niemals.
            """,
        ),
        code(
            "optimization-feature-availability",
            r'''
            availability_rows = [
                "Stammdaten / Vertragsleistung",
                "Kalender des Zielmonats",
                "Verbrauchshistorie bis t−1",
                "Produktionsplan für t",
                "Wartungsstatus für t",
                "realisierte Temperatur / Heiztage t",
            ]
            availability_cols = ["Historie t−6 … t−1", "Prognosestichtag", "Ist-Monat t"]
            availability = np.array([
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [0, 0.5, 1],
                [0, 0.5, 1],
                [0, 0, 1],
            ])
            labels = np.where(
                availability == 1, "verfügbar",
                np.where(availability == 0.5, "nur Snapshot", "nicht verwenden")
            )
            fig = go.Figure(go.Heatmap(
                z=availability, x=availability_cols, y=availability_rows,
                text=labels, texttemplate="%{text}", zmin=0, zmax=1,
                colorscale=[
                    [0.0, theme.TOKENS["grey-200"]],
                    [0.49, theme.TOKENS["grey-200"]],
                    [0.5, theme.ROLE["schwellwert"]],
                    [0.51, theme.ROLE["schwellwert"]],
                    [1.0, theme.ROLE["ist"]],
                ],
                showscale=False,
                hovertemplate="%{y}<br>%{x}: %{text}<extra></extra>",
            ))
            ci.stil(
                fig, "Verfügbarkeit zum Prognosestichtag",
                "Plan und Wartung sind konditional; realisierte Zielmonats-Wetterwerte bleiben ausgeschlossen",
                x_titel="", y_titel="",
            )
            fig.update_yaxes(autorange="reversed")
            ci.zeigen(fig)
            ''',
        ),
        markdown(
            "optimization-feature-catalog",
            """
            ### Was steckt in den 58 numerischen Merkmalen?

            | Gruppe | Beispiele | Fachliche Idee |
            | --- | --- | --- |
            | Niveau | `vls_l1…l6`, `logkwh_l1…l6` | letzter Zustand und mittlere Anschlussgröße |
            | Glättung | Rolling 2/3/4/6, EWM3, expanding mean | robustes typisches Niveau |
            | Dynamik | Trends 1↔3 und 3↔6, Rolling-Std., CV | Richtung und Schwankung |
            | Kalender | Arbeitstage, Feiertage, Sinus/Kosinus | Monatslänge und Saison |
            | Planung | aktueller Plan, Plan-Lags, Ratios und Differenzen | erwartete Produktionsänderung |
            | Wartung | aktuell und Historie | geplante Verbrauchsdämpfung |
            | Expertenschätzer | `rolling VLS × Planratio × Arbeitstagsratio` | transparente fachliche Startschätzung |
            | Kategorie | Kundentyp per One-Hot-Encoding | unterschiedliche Nutzungsprofile |

            Fehlende Anlaufhistorien werden **innerhalb jeder Modellpipeline** per Median ergänzt;
            zusätzliche Missing-Indikatoren erhalten die Information, dass ein Wert fehlte. Die
            Zähler-ID wird bewusst nicht verwendet: 700 feste IDs bei nur 24 Monaten würden leicht
            auswendig gelernt. Lag 12 bleibt draußen, weil im Entwicklungsjahr keine echte
            Vorjahreshistorie zum Trainieren vorliegt.
            """,
        ),
        code(
            "optimization-feature-definitions",
            r'''
            BASIC_FEATURES = [
                "log_power", "arbeitstage", "feiertage_im_monat", "vls_l1", "vls_r3",
                "logkwh_l1", "month_sin", "month_cos",
            ]
            HISTORY_FEATURES = BASIC_FEATURES + [
                "vls_l2", "vls_l3", "vls_l4", "vls_l5", "vls_l6",
                "logkwh_l2", "logkwh_l3", "logkwh_l4", "logkwh_l5", "logkwh_l6",
                "vls_r2", "vls_r4", "vls_r6", "vls_s3", "vls_s6",
                "vls_expmean", "vls_expstd", "vls_ewm3", "vls_trend13", "vls_trend36",
                "log_ratio13", "vls_cv3", "vls_cv6",
            ]
            WORKDAY_FEATURES = [
                "arbeitstage_l1", "arbeitstage_r3", "arbeitstage_r6",
                "arbeitstage_ratio_l1", "arbeitstage_ratio_r3", "arbeitstage_ratio_r6",
                "arbeitstage_diff_l1", "arbeitstage_diff_r3", "arbeitstage_diff_r6",
            ]
            PRODUCTION_FEATURES = [
                "produktionsplan_index", "plan_missing",
                "produktionsplan_index_l1", "produktionsplan_index_r3",
                "produktionsplan_index_r6", "produktionsplan_index_ratio_l1",
                "produktionsplan_index_ratio_r3", "produktionsplan_index_ratio_r6",
                "produktionsplan_index_diff_l1", "produktionsplan_index_diff_r3",
                "produktionsplan_index_diff_r6",
            ]
            MAINTENANCE_FEATURES = [
                "wartung_aktiv", "wartung_aktiv_l1", "wartung_aktiv_r3", "wartung_aktiv_r6",
            ]
            EXPERT_FEATURES = ["expert", "expert_plan", "expert_lag"]
            FULL_NUM_FEATURES = (
                HISTORY_FEATURES + WORKDAY_FEATURES + PRODUCTION_FEATURES
                + MAINTENANCE_FEATURES + EXPERT_FEATURES
            )
            CAT_FEATURES = ["kundentyp"]
            assert len(FULL_NUM_FEATURES) == 58

            fold_definitions = [
                ("2024-04-30", "2024-05-01", "2024-06-30"),
                ("2024-06-30", "2024-07-01", "2024-08-31"),
                ("2024-08-31", "2024-09-01", "2024-10-31"),
            ]


            def make_pipeline(model, numeric_features=FULL_NUM_FEATURES):
                numeric = SimpleImputer(
                    strategy="median", add_indicator=True, keep_empty_features=True
                )
                categorical = Pipeline([
                    ("impute", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                ])
                preprocessor = ColumnTransformer([
                    ("num", numeric, numeric_features),
                    ("cat", categorical, CAT_FEATURES),
                ], sparse_threshold=0.0)
                return Pipeline([("pre", preprocessor), ("model", model)])


            def make_hgb(params, features=FULL_NUM_FEATURES):
                return make_pipeline(
                    HistGradientBoostingRegressor(
                        loss="absolute_error", early_stopping=False,
                        random_state=RANDOM_STATE, **params,
                    ),
                    features,
                )


            def predict_kwh(fitted, frame, target_mode, features=FULL_NUM_FEATURES):
                raw = fitted.predict(frame[features + CAT_FEATURES])
                if target_mode == "log_vls":
                    raw = np.expm1(raw)
                return np.clip(raw, 0, None) * frame["vertragsleistung_kw"].to_numpy()


            def run_cv(label, estimator, target_mode="log_vls", weighted=False):
                rows, predictions = [], []
                for fold, (train_end, valid_start, valid_end) in enumerate(fold_definitions, 1):
                    train = selection_24[selection_24["monat"].le(train_end)]
                    valid = selection_24[
                        selection_24["monat"].between(valid_start, valid_end)
                    ]
                    fitted = clone(estimator)
                    fit_params = {}
                    if weighted:
                        fit_params["model__sample_weight"] = train["vertragsleistung_kw"].to_numpy()
                    fitted.fit(
                        train[FULL_NUM_FEATURES + CAT_FEATURES], train[target_mode], **fit_params
                    )
                    predicted = predict_kwh(fitted, valid, target_mode)
                    rows.append({
                        "Kandidat": label, "Fold": fold,
                        "WAPE (%)": wape(valid["verbrauch_kwh"], predicted),
                        "Bias (%)": (
                            (predicted - valid["verbrauch_kwh"].to_numpy()).sum()
                            / valid["verbrauch_kwh"].sum() * 100
                        ),
                    })
                    predictions.append(pd.DataFrame({
                        "row_id": valid.index, "Fold": fold,
                        "Ist": valid["verbrauch_kwh"].to_numpy(), "Prognose": predicted,
                    }))
                return pd.DataFrame(rows), pd.concat(predictions, ignore_index=True)
            ''',
        ),
        markdown(
            "optimization-ablation-rationale",
            """
            ### Bringt jedes zusätzliche Featurepaket wirklich etwas?

            **Warum dieser Plot?** Eine Ablation entfernt beziehungsweise ergänzt ganze
            Featuregruppen bei unverändertem Referenzmodell. So wird sichtbar, ob der Gewinn aus
            Tuning oder aus zusätzlicher fachlicher Information stammt.

            **Entscheidungsregel:** Zusätzliche Komplexität ist erst dann überzeugend, wenn der
            mittlere CV-WAPE um mindestens 0,5 Prozentpunkte sinkt und mindestens zwei der drei
            Zeitfolds profitieren.
            """,
        ),
        code(
            "optimization-ablation-plot",
            r'''
            REFERENCE_PARAMS = {
                "learning_rate": 0.04, "max_iter": 400, "max_leaf_nodes": 15,
                "min_samples_leaf": 30, "l2_regularization": 1,
            }
            ablation_sets = {
                "Basiskern": BASIC_FEATURES,
                "+ Historie": HISTORY_FEATURES,
                "+ Arbeitstagsdynamik": HISTORY_FEATURES + WORKDAY_FEATURES,
                "+ Produktionsplan": (
                    HISTORY_FEATURES + WORKDAY_FEATURES + PRODUCTION_FEATURES
                    + ["expert", "expert_plan", "expert_lag"]
                ),
                "+ Wartung (voll)": FULL_NUM_FEATURES,
            }
            ablation_rows = []
            for feature_set, features in ablation_sets.items():
                fold_scores = []
                for fold, (train_end, valid_start, valid_end) in enumerate(fold_definitions, 1):
                    train = selection_24[selection_24["monat"].le(train_end)]
                    valid = selection_24[
                        selection_24["monat"].between(valid_start, valid_end)
                    ]
                    fitted = make_hgb(REFERENCE_PARAMS, features)
                    fitted.fit(train[features + CAT_FEATURES], train["log_vls"])
                    predicted = predict_kwh(fitted, valid, "log_vls", features)
                    fold_scores.append(wape(valid["verbrauch_kwh"], predicted))
                ablation_rows.append({
                    "Featurepaket": feature_set,
                    "Anzahl": len(features),
                    "CV-WAPE (%)": np.mean(fold_scores),
                    "CV-Std. (pp)": np.std(fold_scores, ddof=0),
                    "Fold-WAPE": fold_scores,
                })
            ablation = pd.DataFrame(ablation_rows)

            fig = go.Figure(go.Bar(
                x=ablation["CV-WAPE (%)"], y=ablation["Featurepaket"], orientation="h",
                marker_color=[
                    theme.ROLE["prognose"] if name == "+ Wartung (voll)"
                    else theme.TOKENS["grey-400"]
                    for name in ablation["Featurepaket"]
                ],
                error_x=dict(type="data", array=ablation["CV-Std. (pp)"], visible=True),
                text=[f"{de(value, 2)} %" for value in ablation["CV-WAPE (%)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig, "Featuregruppen-Ablation in den 2024-Folds",
                "Identisches HGB-Referenzmodell; Balken = mittlerer WAPE, Fehlerbalken = Fold-Streuung",
                x_titel="WAPE (%) — niedriger ist besser", y_titel="",
            )
            fig.update_yaxes(autorange="reversed")
            ci.prozent_achse(fig, "x", 1)
            ci.zeigen(fig)
            display(ci.tabellenansicht(
                ablation[["Featurepaket", "Anzahl", "CV-WAPE (%)", "CV-Std. (pp)"]], 2
            ))
            feature_gain = (
                ablation.iloc[0]["CV-WAPE (%)"] - ablation.iloc[-1]["CV-WAPE (%)"]
            )
            entscheidungsbox(
                f"Das volle Paket verbessert den Basiskern um {de(feature_gain, 2)} Prozentpunkte.",
                "Erweiterte Historien bleiben erhalten; Plan- und Wartungsmerkmale werden als konditionaler Challenger geführt.",
                "Ein großer Plan-Gewinn ist nur real, wenn historische Planstände am damaligen Prognosestichtag verfügbar waren."
            )
            ''',
        ),
        code(
            "optimization-chapter-selection",
            '''
            ci.abschnitt(
                "03", "Kompakte Modellsuche und Auswahl",
                "24 Baumkandidaten, drei Zielvarianten und ein bewusst strenges Komplexitäts-Gate.",
                kontext="CHALLENGER-MODELLIERUNG",
            )
            ''',
        ),
        markdown(
            "optimization-fold-rationale",
            """
            ### Wie wird ohne zufälligen Split validiert?

            **Warum dieser Plot?** Bei Zeitdaten muss Training immer vor Validierung liegen. Die
            drei Folds simulieren monatlich rollierende Ein-Schritt-Prognosen: Für Juni darf der im
            Mai bereits gemessene Verbrauch als `lag_1` vorliegen, das Modell selbst wird jedoch
            nicht mit Mai nachtrainiert.

            November/Dezember werden nicht für Hyperparameter verwendet. Sie bestimmen erst danach
            einen einzigen globalen Kalibrierfaktor.
            """,
        ),
        code(
            "optimization-fold-plot",
            r'''
            months = pd.period_range("2024-01", "2025-12", freq="M")
            rows = ["Fold 1", "Fold 2", "Fold 3", "Kalibrierung", "2025-Rückblick"]
            role_code = np.zeros((len(rows), len(months)))
            role_text = np.full((len(rows), len(months)), "nicht verwendet", dtype=object)

            def mark(row, start, end, code_value, label):
                mask = (months >= pd.Period(start, "M")) & (months <= pd.Period(end, "M"))
                role_code[row, mask] = code_value
                role_text[row, mask] = label

            mark(0, "2024-01", "2024-04", 1, "Training")
            mark(0, "2024-05", "2024-06", 2, "Validierung")
            mark(1, "2024-01", "2024-06", 1, "Training")
            mark(1, "2024-07", "2024-08", 2, "Validierung")
            mark(2, "2024-01", "2024-08", 1, "Training")
            mark(2, "2024-09", "2024-10", 2, "Validierung")
            mark(3, "2024-01", "2024-10", 1, "Training")
            mark(3, "2024-11", "2024-12", 3, "Kalibrierung")
            mark(4, "2024-01", "2024-12", 1, "finales Training")
            mark(4, "2025-01", "2025-12", 4, "bekannter Rückblick")

            fig = go.Figure(go.Heatmap(
                z=role_code, x=[period.strftime("%m/%Y") for period in months], y=rows,
                text=role_text, customdata=role_text, texttemplate="",
                zmin=0, zmax=4, showscale=False,
                colorscale=[
                    [0.00, theme.TOKENS["grey-100"]], [0.24, theme.TOKENS["grey-100"]],
                    [0.25, theme.ROLE["ist"]], [0.49, theme.ROLE["ist"]],
                    [0.50, theme.TOKENS["text-accent"]], [0.74, theme.TOKENS["text-accent"]],
                    [0.75, theme.ROLE["schwellwert"]], [0.99, theme.ROLE["schwellwert"]],
                    [1.00, theme.TOKENS["grey-400"]],
                ],
                hovertemplate="%{y}<br>%{x}: %{customdata}<extra></extra>",
            ))
            ci.stil(
                fig, "Zeitlicher Entwicklungs- und Bewertungsplan",
                "Keine zufällige Zeilenmischung; 2025 ist nicht Teil der Modellsuche",
                x_titel="Monat", y_titel="",
            )
            fig.update_yaxes(autorange="reversed")
            tick_labels = [months[i].strftime("%m/%Y") for i in range(0, 24, 2)]
            fig.update_xaxes(tickmode="array", tickvals=tick_labels, ticktext=tick_labels)
            ci.zeigen(fig)
            ''',
        ),
        markdown(
            "optimization-search-rationale",
            """
            ### Welche Modellfamilie und welche Hyperparameter gewinnen?

            **Warum diese Suche?** Getestet werden 20 bewusst plausible HGB-Konfigurationen sowie
            je zwei Extra-Trees- und Random-Forest-Kontrollen. Der Suchraum variiert Lernrate,
            Iterationen, Blattzahl, Mindestblattgröße und Regularisierung. Er bleibt klein genug,
            um nicht aus nur drei Folds zufällige Feinheiten herauszuoptimieren.

            Die Auswahl sieht ausschließlich `log1p(VLS)` in den 2024-Folds. Danach werden am
            gewählten HGB noch direktes VLS, Vertragsleistungsgewichtung und `log1p(VLS)` fair auf
            denselben Validierungszeilen verglichen. Der niedrigste Mittelwert gewinnt; ein Abstand
            unter 0,5 Prozentpunkten wird ausdrücklich als Plateau und nicht als Durchbruch
            interpretiert.
            """,
        ),
        code(
            "optimization-model-search",
            r'''
            # Stufe A: Ziel- und Gewichtungsentscheidung bei fixem H03-Referenzmodell.
            target_screen_specs = [
                ("Direktes VLS · ungewichtet", "vls", False),
                ("Direktes VLS · Vertragsleistung gewichtet", "vls", True),
                ("log1p(VLS) · ungewichtet", "log_vls", False),
            ]
            target_fold_parts = []
            for label, target_mode, weighted in target_screen_specs:
                rows, _ = run_cv(
                    label, make_hgb(REFERENCE_PARAMS), target_mode=target_mode, weighted=weighted
                )
                target_fold_parts.append(rows)
            target_fold_results = pd.concat(target_fold_parts, ignore_index=True)
            target_summary = (
                target_fold_results.groupby("Kandidat", as_index=False)
                .agg(
                    cv_wape=("WAPE (%)", "mean"),
                    cv_std=("WAPE (%)", lambda values: values.std(ddof=0)),
                    cv_bias=("Bias (%)", "mean"),
                )
                .sort_values(["cv_wape", "cv_std"])
            )
            chosen_target = target_summary.iloc[0]["Kandidat"]
            assert chosen_target == "log1p(VLS) · ungewichtet"

            # Stufe B: expliziter, vollständig reproduzierbarer Robustheitscheck.
            raw_hgb_configs = [
                (.025, 700,  7, 30, 1), (.025, 700, 15, 50, 3),
                (.040, 400, 15, 30, 1), (.030, 550, 15, 30, 1),
                (.050, 350, 15, 30, 1), (.060, 300, 15, 30, 1),
                (.080, 250, 15, 30, 1), (.040, 450,  7, 15, 0),
                (.040, 450,  7, 50, 3), (.040, 450,  7, 80, 5),
                (.030, 550, 31, 15, 0), (.030, 550, 31, 30, 1),
                (.030, 550, 31, 50, 3), (.030, 550, 31, 80, 5),
                (.050, 350, 31, 15, 1), (.050, 350, 31, 50, 5),
                (.060, 300,  7, 15, 1), (.060, 300,  7, 50, 5),
                (.025, 700, 31, 30, 3), (.080, 250, 31, 80, 5),
            ]
            singleton_grids = [
                {
                    "learning_rate": [lr], "max_iter": [iterations],
                    "max_leaf_nodes": [leaves], "min_samples_leaf": [min_leaf],
                    "l2_regularization": [l2],
                }
                for lr, iterations, leaves, min_leaf, l2 in raw_hgb_configs
            ]
            HGB_CONFIGS = list(ParameterGrid(singleton_grids))
            candidate_estimators = {
                f"H{index:02d}": make_hgb(params)
                for index, params in enumerate(HGB_CONFIGS, start=1)
            }
            candidate_estimators.update({
                "E01": make_pipeline(ExtraTreesRegressor(
                    n_estimators=400, max_depth=None, min_samples_leaf=3,
                    max_features=0.7, bootstrap=False, n_jobs=-1,
                    random_state=RANDOM_STATE,
                )),
                "E02": make_pipeline(ExtraTreesRegressor(
                    n_estimators=400, max_depth=None, min_samples_leaf=5,
                    max_features=1.0, bootstrap=False, n_jobs=-1,
                    random_state=RANDOM_STATE,
                )),
                "R01": make_pipeline(RandomForestRegressor(
                    n_estimators=300, max_depth=None, min_samples_leaf=5,
                    max_features=0.7, bootstrap=True, n_jobs=-1,
                    random_state=RANDOM_STATE,
                )),
                "R02": make_pipeline(RandomForestRegressor(
                    n_estimators=300, max_depth=16, min_samples_leaf=10,
                    max_features=1.0, bootstrap=True, n_jobs=-1,
                    random_state=RANDOM_STATE,
                )),
            })

            search_fold_parts = []
            oof_predictions = {}
            for candidate_id, estimator in candidate_estimators.items():
                family = (
                    "HGB" if candidate_id.startswith("H")
                    else "Extra Trees" if candidate_id.startswith("E")
                    else "Random Forest"
                )
                label = f"{family} · {candidate_id}"
                rows, predictions = run_cv(label, estimator, target_mode="log_vls")
                rows["ID"] = candidate_id
                rows["Familie"] = family
                search_fold_parts.append(rows)
                oof_predictions[candidate_id] = predictions

            search_folds = pd.concat(search_fold_parts, ignore_index=True)
            search_summary = (
                search_folds.groupby(["ID", "Familie", "Kandidat"], as_index=False)
                .agg(
                    cv_wape=("WAPE (%)", "mean"),
                    cv_std=("WAPE (%)", lambda values: values.std(ddof=0)),
                    cv_bias=("Bias (%)", "mean"),
                )
                .sort_values(["cv_wape", "cv_std"])
                .reset_index(drop=True)
            )
            search_winner = search_summary.iloc[0]
            search_winner_id = search_winner["ID"]
            search_winner_estimator = candidate_estimators[search_winner_id]
            assert search_winner_id == "H08"

            # Referenzen: zwei einfache Regeln und das bisherige RF aus Notebook 10.
            baseline_parts = []
            for fold, (_, valid_start, valid_end) in enumerate(fold_definitions, 1):
                valid = selection_24[
                    selection_24["monat"].between(valid_start, valid_end)
                ]
                for label, column in {
                    "Vormonat": "verbrauch_kwh_l1",
                    "3-Monats-Mittel": "verbrauch_kwh_r3",
                }.items():
                    baseline_parts.append({
                        "Kandidat": label, "Fold": fold,
                        "WAPE (%)": wape(valid["verbrauch_kwh"], valid[column]),
                    })
            baseline_folds = pd.DataFrame(baseline_parts)

            incumbent_features = [
                "log_power", "arbeitstage", "feiertage_im_monat", "vls_l1",
                "vls_r3_strict", "logkwh_l1", "logkwh_r3_strict", "month_sin", "month_cos",
            ]
            incumbent_pipe = make_pipeline(
                RandomForestRegressor(
                    n_estimators=180, max_features=0.7, max_depth=8,
                    min_samples_leaf=20, n_jobs=1, random_state=RANDOM_STATE,
                ),
                incumbent_features,
            )
            incumbent_fold_rows = []
            for fold, (train_end, valid_start, valid_end) in enumerate(fold_definitions, 1):
                train = selection_24[selection_24["monat"].le(train_end)]
                valid = selection_24[
                    selection_24["monat"].between(valid_start, valid_end)
                ]
                fitted = clone(incumbent_pipe).fit(
                    train[incumbent_features + CAT_FEATURES], train["vls"]
                )
                prediction = np.clip(
                    fitted.predict(valid[incumbent_features + CAT_FEATURES]), 0, None
                ) * valid["vertragsleistung_kw"].to_numpy()
                incumbent_fold_rows.append({
                    "Kandidat": "Bisheriger RF", "Fold": fold,
                    "WAPE (%)": wape(valid["verbrauch_kwh"], prediction),
                })
            incumbent_folds = pd.DataFrame(incumbent_fold_rows)

            # Ensemble-Screen: genau ein Mischparameter, ausschließlich OOF-Prognosen.
            best_tree_id = search_summary[
                search_summary["Familie"].ne("HGB")
            ].iloc[0]["ID"]
            left = oof_predictions[search_winner_id].sort_values(["Fold", "row_id"])
            right = oof_predictions[best_tree_id].sort_values(["Fold", "row_id"])
            assert np.array_equal(left["row_id"], right["row_id"])
            blend_rows = []
            for hgb_weight in np.linspace(0, 1, 11):
                blended = hgb_weight * left["Prognose"] + (1 - hgb_weight) * right["Prognose"]
                fold_scores = [
                    wape(left.loc[left["Fold"].eq(fold), "Ist"], blended[left["Fold"].eq(fold)])
                    for fold in (1, 2, 3)
                ]
                blend_rows.append({
                    "HGB-Gewicht": hgb_weight, "CV-WAPE (%)": np.mean(fold_scores),
                    "Fold-WAPE": fold_scores,
                })
            blend_screen = pd.DataFrame(blend_rows).sort_values("CV-WAPE (%)")
            best_blend = blend_screen.iloc[0]
            blend_gain = search_winner["cv_wape"] - best_blend["CV-WAPE (%)"]
            blend_fold_wins = sum(
                blended_score < single_score
                for blended_score, single_score in zip(
                    best_blend["Fold-WAPE"],
                    search_folds.loc[
                        search_folds["ID"].eq(search_winner_id), "WAPE (%)"
                    ].sort_index().tolist(),
                )
            )
            blend_accepted = blend_gain >= COMPLEXITY_GATE_PP and blend_fold_wins >= 2
            ''',
        ),
        code(
            "optimization-search-plot",
            r'''
            baseline_summary = (
                pd.concat([baseline_folds, incumbent_folds], ignore_index=True)
                .groupby("Kandidat", as_index=False)
                .agg(
                    cv_wape=("WAPE (%)", "mean"),
                    cv_std=("WAPE (%)", lambda values: values.std(ddof=0)),
                )
                .assign(Familie="Referenz")
            )
            family_controls = (
                search_summary[search_summary["Familie"].ne("HGB")]
                .sort_values(["cv_wape", "cv_std"])
                .groupby("Familie", as_index=False)
                .head(1)
            )
            displayed_models = (
                pd.concat([search_summary.head(8), family_controls], ignore_index=True)
                .drop_duplicates("ID")
                .sort_values(["cv_wape", "cv_std"])
            )
            plot_search = pd.concat([
                displayed_models[["Kandidat", "cv_wape", "cv_std", "Familie"]],
                baseline_summary,
            ], ignore_index=True).sort_values("cv_wape", ascending=False)
            family_colors = {
                "HGB": theme.ROLE["prognose"],
                "Extra Trees": theme.TOKENS["text-accent"],
                "Random Forest": theme.ROLE["schwellwert"],
                "Referenz": theme.TOKENS["grey-400"],
            }
            fig = go.Figure(go.Bar(
                x=plot_search["cv_wape"], y=plot_search["Kandidat"], orientation="h",
                marker_color=[family_colors[value] for value in plot_search["Familie"]],
                error_x=dict(type="data", array=plot_search["cv_std"], visible=True),
                text=[f"{de(value, 2)} %" for value in plot_search["cv_wape"]],
                textposition="outside", cliponaxis=False,
                customdata=plot_search[["Familie"]],
                hovertemplate="%{y}<br>WAPE %{x:.2f} %<br>%{customdata[0]}<extra></extra>",
            ))
            ci.stil(
                fig, "2024-Ranking der robustesten Kandidaten",
                "Top-HGBs, beste ET/RF-Kontrolle und Baselines; Fehlerbalken = Streuung der drei Zeitfolds",
                x_titel="WAPE (%) — niedriger ist besser", y_titel="",
            )
            ci.prozent_achse(fig, "x", 1)
            ci.zeigen(fig)

            search_display = displayed_models.copy()
            search_display["Parameter"] = search_display["ID"].map(
                lambda candidate_id: json.dumps(
                    HGB_CONFIGS[int(candidate_id[1:]) - 1], ensure_ascii=False, sort_keys=True
                ) if candidate_id.startswith("H") else "siehe explizite Baumkontrolle"
            )
            display(ci.tabellenansicht(
                search_display[["ID", "Familie", "cv_wape", "cv_std", "cv_bias", "Parameter"]], 3
            ))
            display(ci.tabellenansicht(
                target_summary.rename(columns={
                    "cv_wape": "CV-WAPE (%)", "cv_std": "CV-Std. (pp)",
                    "cv_bias": "CV-Bias (%)",
                }), 3
            ))

            incumbent_h03 = search_summary.loc[search_summary["ID"].eq("H03")].iloc[0]
            tuning_gain = incumbent_h03["cv_wape"] - search_winner["cv_wape"]
            entscheidungsbox(
                f"{search_winner['Kandidat']} gewinnt mit {de(search_winner['cv_wape'], 3)} % WAPE; "
                f"gegen H03 sind es nur {de(tuning_gain, 3)} Prozentpunkte.",
                f"Strikte CV-Auswahl: {search_winner_id}. Das Tuning wird als Plateau gewertet. "
                f"Das beste Ensemble gewinnt {de(blend_gain, 3)} pp und wird "
                f"{'übernommen' if blend_accepted else 'wegen des 0,5-pp-Gates verworfen'}.",
                "Nur drei Folds aus einem Kalenderjahr begrenzen die Sicherheit feiner Rangabstände."
            )
            ''',
        ),
        markdown(
            "optimization-model-card",
            """
            ### Wie ist der ausgewählte Rechenweg zu lesen?

            1. **Ziel normalisieren:** `VLS = kWh / kW`, danach `log1p(VLS)`.
            2. **Vorverarbeiten:** numerische Mediane plus Missing-Indikatoren; Kundentyp One-Hot.
            3. **Lernen:** HGB minimiert absoluten Fehler robust gegenüber einzelnen Spitzen.
            4. **Zurückrechnen:** `expm1(Prognose) × Vertragsleistung` ergibt wieder kWh.
            5. **Bewerten:** ausschließlich die zurückgerechneten kWh gehen in WAPE, MAE und RMSE ein.

            Das Modell ist nicht deshalb besser, weil „mehr Parameter“ automatisch besser wären.
            Die breite Suche landet auf einem engen Leistungsplateau. Den größten Sprung erzeugen
            die plan- und verlaufsbezogenen Features; das reine Feintuning liefert nur Hundertstel
            Prozentpunkte.
            """,
        ),
        code(
            "optimization-chapter-calibration",
            '''
            ci.abschnitt(
                "04", "Bias-Kalibrierung vor dem 2025-Rückblick",
                "Ein globaler Faktor aus November/Dezember 2024 – keine Nachjustierung am Benchmark.",
                kontext="CHALLENGER-MODELLIERUNG",
            )
            ''',
        ),
        markdown(
            "optimization-calibration-rationale",
            """
            ### Warum noch ein globaler Kalibrierfaktor?

            Ein gutes Rangmodell kann das Gesamtniveau systematisch zu niedrig oder zu hoch
            schätzen. Deshalb wird der Gewinner zunächst nur auf Januar–Oktober 2024 trainiert und
            auf November/Dezember prognostiziert. Für `Prognose × c` ist der gewichtete Median von
            `Ist / Prognose` genau der Faktor, der die Summe absoluter Fehler minimiert.

            **Warum dieser Plot?** Er zeigt gleichzeitig WAPE und absoluten Bias vor und nach der
            Korrektur. Der Faktor wird nur übernommen, wenn er im reservierten Fenster mindestens
            0,5 Prozentpunkte WAPE spart. Wird er übernommen, muss er anschließend unverändert auf
            2025 angewandt werden – selbst wenn die rohe Variante dort zufällig besser wäre.
            """,
        ),
        code(
            "optimization-calibration-plot",
            r'''
            calibration_model = clone(search_winner_estimator).fit(
                selection_24[FULL_NUM_FEATURES + CAT_FEATURES], selection_24["log_vls"]
            )
            calibration_raw = predict_kwh(
                calibration_model, calibration_24, "log_vls"
            )
            calibration_ratio = (
                calibration_24["verbrauch_kwh"].to_numpy()
                / np.maximum(calibration_raw, 1e-9)
            )
            calibration_candidate = weighted_median(
                calibration_ratio, weights=np.maximum(calibration_raw, 1e-9)
            )
            calibration_adjusted = calibration_raw * calibration_candidate
            cal_raw_metrics = regression_metrics(
                calibration_24["verbrauch_kwh"], calibration_raw
            )
            cal_adjusted_metrics = regression_metrics(
                calibration_24["verbrauch_kwh"], calibration_adjusted
            )
            calibration_gain = (
                cal_raw_metrics["WAPE (%)"] - cal_adjusted_metrics["WAPE (%)"]
            )
            calibration_accepted = calibration_gain >= CALIBRATION_GATE_PP
            calibration_factor = calibration_candidate if calibration_accepted else 1.0

            cal_plot = pd.DataFrame([
                ["Rohmodell", cal_raw_metrics["WAPE (%)"], abs(cal_raw_metrics["Bias (%)"])],
                ["Mit Faktor", cal_adjusted_metrics["WAPE (%)"], abs(cal_adjusted_metrics["Bias (%)"])],
            ], columns=["Variante", "WAPE (%)", "|Bias| (%)"])
            fig = go.Figure([
                go.Bar(
                    name="WAPE", x=cal_plot["Variante"], y=cal_plot["WAPE (%)"],
                    marker_color=theme.ROLE["prognose"],
                ),
                go.Bar(
                    name="|Bias|", x=cal_plot["Variante"], y=cal_plot["|Bias| (%)"],
                    marker_color=theme.ROLE["schwellwert"],
                ),
            ])
            ci.stil(
                fig, "Kalibrierung ausschließlich auf November/Dezember 2024",
                f"Gewichteter Medianfaktor {de(calibration_candidate, 4)}; Mindestgewinn {de(CALIBRATION_GATE_PP, 1)} pp",
                x_titel="", y_titel="Prozent",
            )
            fig.update_layout(barmode="group")
            ci.prozent_achse(fig, "y", 1)
            ci.zeigen(fig)

            cal_table = pd.DataFrame([
                {"Variante": "Rohmodell", **cal_raw_metrics},
                {"Variante": f"Faktor {de(calibration_candidate, 4)}", **cal_adjusted_metrics},
            ])
            display(ci.tabellenansicht(cal_table, 3))
            entscheidungsbox(
                f"Der Faktor {de(calibration_candidate, 4)} verändert den Kalibrier-WAPE um "
                f"{de(calibration_gain, 3)} Prozentpunkte.",
                f"Er wird {'eingefroren und auf 2025 angewandt' if calibration_accepted else 'wegen des Gates verworfen'}.",
                "Ein einzelner globaler Faktor korrigiert Niveau, aber keine zähler- oder monatsabhängigen Muster."
            )
            ''',
        ),
        code(
            "optimization-chapter-benchmark",
            '''
            ci.abschnitt(
                "05", "Retrospektiver 2025-Benchmark",
                "Der eingefrorene Challenger im Vergleich zu Regeln und bisherigem Random Forest.",
                kontext="CHALLENGER-MODELLIERUNG",
            )
            ''',
        ),
        markdown(
            "optimization-benchmark-rationale",
            """
            ### Wie nah kommen die Prognosen im bereits bekannten Jahr 2025?

            **Warum dieser Plot?** Alle Kandidaten werden auf denselben 8.400 Zähler-Monaten und in
            derselben Einheit kWh bewertet. Der kalibrierte Challenger ist das vorher festgelegte
            operative Ergebnis; das Rohmodell bleibt lediglich als Sensitivität sichtbar.

            Der bisherige Random Forest verwendet keine aktuellen Planmerkmale und bleibt deshalb
            der sichere Fallback, solange historische Plan-Snapshots nicht nachgewiesen sind.
            """,
        ),
        code(
            "optimization-final-fit",
            r'''
            final_model = clone(search_winner_estimator).fit(
                d24[FULL_NUM_FEATURES + CAT_FEATURES], d24["log_vls"]
            )
            prediction_raw_25 = predict_kwh(final_model, d25, "log_vls")
            prediction_challenger_25 = prediction_raw_25 * calibration_factor

            incumbent_model = clone(incumbent_pipe).fit(
                d24[incumbent_features + CAT_FEATURES], d24["vls"]
            )
            prediction_incumbent_25 = np.clip(
                incumbent_model.predict(d25[incumbent_features + CAT_FEATURES]), 0, None
            ) * d25["vertragsleistung_kw"].to_numpy()

            evaluation_25 = d25[[
                "zaehler_id", "monat", "kundentyp", "verbrauch_kwh", "vertragsleistung_kw"
            ]].copy()
            evaluation_25["Vormonat"] = d25["verbrauch_kwh_l1"].to_numpy()
            evaluation_25["3-Monats-Mittel"] = d25["verbrauch_kwh_r3"].to_numpy()
            evaluation_25["Bisheriger RF"] = prediction_incumbent_25
            evaluation_25["Challenger roh"] = prediction_raw_25
            evaluation_25["Challenger kalibriert"] = prediction_challenger_25

            benchmark_order = [
                "Vormonat", "3-Monats-Mittel", "Bisheriger RF",
                "Challenger roh", "Challenger kalibriert",
            ]
            benchmark_metrics = pd.DataFrame([
                {
                    "Kandidat": candidate,
                    **regression_metrics(evaluation_25["verbrauch_kwh"], evaluation_25[candidate]),
                }
                for candidate in benchmark_order
            ]).sort_values("WAPE (%)")
            primary_name = "Challenger kalibriert" if calibration_accepted else "Challenger roh"
            primary_metrics = benchmark_metrics.loc[
                benchmark_metrics["Kandidat"].eq(primary_name)
            ].iloc[0]
            incumbent_metrics = benchmark_metrics.loc[
                benchmark_metrics["Kandidat"].eq("Bisheriger RF")
            ].iloc[0]
            ''',
        ),
        code(
            "optimization-final-benchmark",
            r'''
            benchmark_plot = benchmark_metrics.sort_values("WAPE (%)", ascending=False)
            bar_colors = [
                theme.ROLE["prognose"] if candidate == primary_name
                else theme.TOKENS["text-accent"] if candidate == "Challenger roh"
                else theme.TOKENS["grey-400"]
                for candidate in benchmark_plot["Kandidat"]
            ]
            fig = go.Figure(go.Bar(
                x=benchmark_plot["WAPE (%)"], y=benchmark_plot["Kandidat"],
                orientation="h", marker_color=bar_colors,
                text=[f"{de(value, 2)} %" for value in benchmark_plot["WAPE (%)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig, "Retrospektiver Modellvergleich 2025",
                "Bereits bekannter Benchmark – keine erneute Auswahlgrundlage",
                x_titel="WAPE (%) — niedriger ist besser", y_titel="",
            )
            ci.prozent_achse(fig, "x", 1)
            ci.zeigen(fig)
            display(ci.tabellenansicht(benchmark_metrics, 3))

            relative_gain_incumbent = (
                1 - primary_metrics["WAPE (%)"] / incumbent_metrics["WAPE (%)"]
            ) * 100
            entscheidungsbox(
                f"Der eingefrorene Prozess erreicht {de(primary_metrics['WAPE (%)'], 3)} % WAPE "
                f"und {de(primary_metrics['Bias (%)'], 3)} % Bias.",
                f"Retrospektiv sind das {de(relative_gain_incumbent, 1)} % weniger WAPE als der bisherige RF.",
                "Dieser Abstand bestätigt Plausibilität, ist wegen des bereits bekannten Jahres aber kein neuer Generalisierungsbeweis."
            )
            ''',
        ),
        markdown(
            "optimization-monthly-rationale",
            """
            ### Ist der Vorteil über das Jahr stabil?

            **Warum dieser Plot?** Ein guter Jahresmittelwert kann einzelne schlechte Monate
            verdecken. Monatlicher WAPE vergleicht die drei Verfahren jeweils über alle 700 Zähler
            desselben Monats.

            **So liest du ihn:** Eine dauerhaft niedrigere Challenger-Linie ist überzeugender als
            ein Gewinn, der nur aus einem einzigen Monat stammt.
            """,
        ),
        code(
            "optimization-monthly-plot",
            r'''
            monthly_rows = []
            for month, part in evaluation_25.groupby("monat"):
                for candidate in ["3-Monats-Mittel", "Bisheriger RF", primary_name]:
                    monthly_rows.append({
                        "Monat": month, "Kandidat": candidate,
                        "WAPE (%)": wape(part["verbrauch_kwh"], part[candidate]),
                    })
            monthly_scores = pd.DataFrame(monthly_rows)
            fig = px.line(
                monthly_scores, x="Monat", y="WAPE (%)", color="Kandidat", markers=True,
                color_discrete_map={
                    "3-Monats-Mittel": theme.TOKENS["grey-400"],
                    "Bisheriger RF": theme.TOKENS["text-accent"],
                    primary_name: theme.ROLE["prognose"],
                },
            )
            ci.stil(
                fig, "Monatlicher WAPE im 2025-Rückblick",
                "Gleiche 700 Zähler je Monat; niedrigere Linie ist besser",
                x_titel="Monat", y_titel="WAPE (%)",
            )
            ci.prozent_achse(fig, "y", 0)
            fig.update_yaxes(showgrid=True, gridcolor=theme.TOKENS["grey-200"])
            ci.zeigen(fig)
            monthly_wins = sum(
                monthly_scores.loc[monthly_scores["Kandidat"].eq(primary_name), "WAPE (%)"].to_numpy()
                < monthly_scores.loc[monthly_scores["Kandidat"].eq("Bisheriger RF"), "WAPE (%)"].to_numpy()
            )
            entscheidungsbox(
                f"Der Challenger schlägt den bisherigen RF in {monthly_wins} von 12 Monaten.",
                "Monatliche Stabilität wird neben dem Jahres-WAPE berichtet.",
                "Zwölf Monate sind weiterhin nur ein Saisonzyklus."
            )
            ''',
        ),
        markdown(
            "optimization-segment-rationale",
            """
            ### Wo gewinnt oder verliert der Challenger?

            **Warum dieser Plot?** Ein Portfolio-Mittel kann Schwächen in einem Kundentyp oder
            Monat kaschieren. Jede Zelle zeigt deshalb
            `WAPE Challenger − WAPE bisheriger RF`.

            **So liest du ihn:** Blaue negative Werte sind Verbesserungen; rote positive Werte
            sind Verschlechterungen. Das ist eine Diagnose des Rückblicks, keine nachträgliche
            Grundlage zum Umbauen des Modells.
            """,
        ),
        code(
            "optimization-segment-plot",
            r'''
            segment_rows = []
            for (segment, month), part in evaluation_25.groupby(["kundentyp", "monat"]):
                incumbent_wape = wape(part["verbrauch_kwh"], part["Bisheriger RF"])
                challenger_wape = wape(part["verbrauch_kwh"], part[primary_name])
                segment_rows.append({
                    "Kundentyp": segment, "Monat": month.strftime("%m/%Y"),
                    "Differenz (pp)": challenger_wape - incumbent_wape,
                })
            segment_delta = pd.DataFrame(segment_rows)
            segment_matrix = segment_delta.pivot(
                index="Kundentyp", columns="Monat", values="Differenz (pp)"
            )
            z_limit = max(1.0, np.abs(segment_matrix.to_numpy()).max())
            fig = go.Figure(go.Heatmap(
                z=segment_matrix.to_numpy(), x=segment_matrix.columns,
                y=segment_matrix.index, zmid=0, zmin=-z_limit, zmax=z_limit,
                colorscale=theme.DIVERGING,
                text=np.vectorize(lambda value: f"{value:+.1f}")(
                    segment_matrix.to_numpy()
                ),
                texttemplate="%{text}",
                colorbar=dict(title="Δ WAPE<br>(pp)"),
                hovertemplate="%{y}<br>%{x}<br>Δ %{z:+.2f} pp<extra></extra>",
            ))
            ci.stil(
                fig, "WAPE-Differenz zum bisherigen RF nach Segment und Monat",
                "Negativ (blau) = Challenger besser; positiv (rot) = Challenger schlechter",
                x_titel="Monat", y_titel="Kundentyp",
            )
            ci.zeigen(fig)
            improved_cells = int(segment_delta["Differenz (pp)"].lt(0).sum())
            worst_cell = segment_delta.sort_values("Differenz (pp)", ascending=False).iloc[0]
            entscheidungsbox(
                f"Der Challenger verbessert {improved_cells} von {len(segment_delta)} Segment-Monat-Zellen; "
                f"die schwächste Zelle liegt bei {worst_cell['Kundentyp']} {worst_cell['Monat']} "
                f"({worst_cell['Differenz (pp)']:+.2f} pp).",
                "Segmentabweichungen werden als Monitoring-Kriterium dokumentiert, nicht nachträglich weggetunt.",
                "Kleine Segmentzellen und nur zwölf Monate machen einzelne Farbfelder unsicher."
            )
            ''',
        ),
        markdown(
            "optimization-bootstrap-rationale",
            """
            ### Ist der Abstand nur durch einige wenige Zähler entstanden?

            **Warum dieser Plot?** Beim gepaarten Cluster-Bootstrap werden ganze Zähler inklusive
            ihrer zwölf Monate gezogen. Für jede Stichprobe wird die WAPE-Differenz zwischen
            Challenger und bisherigem RF neu berechnet.

            Liegt das 95-%-Intervall vollständig unter null, verteilt sich der retrospektive
            Vorteil über das Portfolio. Das Verfahren misst jedoch nur Zählerunsicherheit – nicht
            die Unsicherheit über weitere Jahre oder neue wirtschaftliche Bedingungen.
            """,
        ),
        code(
            "optimization-bootstrap-plot",
            r'''
            meter_error = (
                evaluation_25.assign(
                    y_abs=lambda d: d["verbrauch_kwh"].abs(),
                    incumbent_abs=lambda d: (d["verbrauch_kwh"] - d["Bisheriger RF"]).abs(),
                    challenger_abs=lambda d: (d["verbrauch_kwh"] - d[primary_name]).abs(),
                )
                .groupby("zaehler_id", as_index=False)
                .agg(
                    y_abs=("y_abs", "sum"),
                    incumbent_abs=("incumbent_abs", "sum"),
                    challenger_abs=("challenger_abs", "sum"),
                )
            )
            rng = np.random.default_rng(RANDOM_STATE)
            sample_indices = rng.integers(
                0, len(meter_error), size=(N_BOOTSTRAP, len(meter_error))
            )
            sampled_y = meter_error["y_abs"].to_numpy()[sample_indices].sum(axis=1)
            sampled_incumbent = (
                meter_error["incumbent_abs"].to_numpy()[sample_indices].sum(axis=1)
                / sampled_y * 100
            )
            sampled_challenger = (
                meter_error["challenger_abs"].to_numpy()[sample_indices].sum(axis=1)
                / sampled_y * 100
            )
            bootstrap_delta = sampled_challenger - sampled_incumbent
            bootstrap_low, bootstrap_median, bootstrap_high = np.quantile(
                bootstrap_delta, [0.025, 0.5, 0.975]
            )

            fig = go.Figure(go.Histogram(
                x=bootstrap_delta, nbinsx=45, marker_color=theme.ROLE["prognose"],
                hovertemplate="Δ WAPE %{x:.2f} pp<br>Stichproben %{y}<extra></extra>",
            ))
            fig.add_vline(x=0, line_color=theme.ROLE["anomalie"], line_dash="dash")
            fig.add_vrect(
                x0=bootstrap_low, x1=bootstrap_high,
                fillcolor=theme.ROLE["band"], line_width=0,
                annotation_text="95-%-Intervall", annotation_position="top left",
            )
            ci.stil(
                fig, "Gepaarte WAPE-Differenz über 2.000 Zähler-Bootstraps",
                f"Challenger minus bisheriger RF; Median {de(bootstrap_median, 2)} pp, "
                f"95 % [{de(bootstrap_low, 2)}; {de(bootstrap_high, 2)}] pp",
                x_titel="WAPE-Differenz (Prozentpunkte)", y_titel="Bootstrap-Stichproben",
            )
            ci.zeigen(fig)
            entscheidungsbox(
                f"Das 95-%-Zählerintervall reicht von {de(bootstrap_low, 2)} bis {de(bootstrap_high, 2)} pp.",
                "Der Portfolioeffekt wird als gepaarte Differenz mit Unsicherheitsband berichtet.",
                "Der Bootstrap erzeugt keine neuen Jahre und ersetzt keinen prospektiven Shadow-Test."
            )
            ''',
        ),
        code(
            "optimization-chapter-decision",
            '''
            ci.abschnitt(
                "06", "Entscheidung und nächster belastbarer Schritt",
                "Starker konditionaler Challenger – noch keine unbedingte Produktionsfreigabe.",
                kontext="CHALLENGER-MODELLIERUNG",
            )
            ''',
        ),
        markdown(
            "optimization-interpretation",
            """
            ### Was bedeuten die Modellentscheidungen in einfachen Worten?

            - **Vollaststunden** machen einen 50-kW- und einen 5.000-kW-Anschluss besser
              vergleichbar. Die Ausgabe bleibt trotzdem kWh, weil nach der Prognose zurückgerechnet
              wird.
            - **`log1p`** verhindert, dass einzelne sehr große Zielwerte die Lernrichtung zu stark
              dominieren. Der Vorsprung gegenüber direktem VLS ist klein und wird nur als Tiebreak
              verstanden.
            - **HGB** kann Schwellen und Wechselwirkungen lernen, etwa „Plananstieg ist bei
              Industrie anders relevant als bei Gewerbe“, ohne diese Regeln einzeln vorzugeben.
            - **Lags und Rollings** geben dem Modell Gedächtnis. Durch `shift(1)` ist der aktuelle
              Verbrauch niemals Teil seiner eigenen Prognose.
            - **Plan-Ratios** übersetzen „der Produktionsplan liegt 12 % über dem üblichen Niveau“
              in ein direkt nutzbares Signal. Genau deshalb ist ihr Snapshot-Nachweis so wichtig.
            - **Kalibrierung** ändert nicht die Reihenfolge der Prognosen, sondern nur das globale
              Niveau. Sie wird vor 2025 festgelegt und danach nicht mehr optimiert.
            """,
        ),
        code(
            "optimization-scorecard",
            r'''
            rolling_cv = baseline_summary.loc[
                baseline_summary["Kandidat"].eq("3-Monats-Mittel"), "cv_wape"
            ].iloc[0]
            cv_relative_gain = (1 - search_winner["cv_wape"] / rolling_cv) * 100
            scorecard = pd.DataFrame([
                ["2024-CV gegen Rolling-3", f"{de(cv_relative_gain, 1)} % relativ besser", "bestanden"],
                ["Reines Hyperparameter-Tuning", f"{de(tuning_gain, 3)} pp gegen H03", "Plateau"],
                ["Ziel-/Gewichtungswahl", chosen_target, "bestanden"],
                ["Ensemble-Gate", f"Gewinn {de(blend_gain, 3)} pp", "bestanden" if blend_accepted else "verworfen"],
                ["Kalibrierungs-Gate", f"Gewinn {de(calibration_gain, 3)} pp", "bestanden" if calibration_accepted else "verworfen"],
                ["2025-Bias (nur Diagnose)", f"{de(primary_metrics['Bias (%)'], 3)} %", "plausibel" if abs(primary_metrics["Bias (%)"]) <= 2 else "beobachten"],
                ["Plan-Snapshot vor Monat t", "fachlich noch nachzuweisen", "offen"],
                ["Neuer ungesehener Shadow-Zeitraum", "noch nicht vorhanden", "offen"],
            ], columns=["Prüfkriterium", "Ergebnis", "Status"])
            display(ci.tabellenansicht(scorecard, 3))

            decision = (
                "Challenger im Shadow-Betrieb einsetzen"
                if PLAN_SNAPSHOT_CONFIRMED
                else "Bisherigen RF nutzen, bis Plan-Snapshots belegt sind"
            )
            entscheidungsbox(
                f"2024-CV: {de(search_winner['cv_wape'], 3)} %; retrospektiver 2025-WAPE: "
                f"{de(primary_metrics['WAPE (%)'], 3)} %.",
                decision + "; bestehender RF bleibt der dokumentierte No-Plan-Fallback.",
                "Produktivfreigabe erst nach Snapshot-Audit, neuem Shadow-Zeitraum und fachlicher Kostenbewertung."
            )
            ''',
        ),
        markdown(
            "optimization-conclusion",
            """
            ## Fazit

            Das Notebook bringt die Prognose nicht durch blindes Tuning nach vorn. Die Suche zeigt
            vielmehr ein stabiles HGB-Plateau. Der substanzielle Gewinn entsteht durch drei sauber
            kombinierte Ideen:

            1. ein fachlich normalisiertes und logarithmiertes VLS-Ziel,
            2. ausschließlich vergangenheitsbasierte Zustands-, Trend- und Stabilitätsmerkmale,
            3. Plan- und Arbeitstagsänderungen relativ zur eigenen Zählerhistorie.

            Der ausgewählte Prozess wird wieder in kWh zurückgerechnet, gegen Vormonat,
            Drei-Monats-Mittel und den bisherigen Random Forest bewertet und auf Bias, Monate,
            Kundentypen sowie Zählerunsicherheit geprüft. Damit ist die Modellentscheidung in einer
            Prüfung nicht nur mit einem guten Endwert, sondern mit einer nachvollziehbaren Kette aus
            Hypothese, Validierung, Entscheidung und Grenze begründbar.

            **Empfohlene nächste Schritte**

            1. historische Produktionsplan- und Wartungs-Snapshots technisch nachweisen,
            2. den kompletten Prozess unverändert in einem neuen Zeitraum im Shadow-Modus fahren,
            3. WAPE, Bias und Segmentdrift monatlich überwachen,
            4. erst danach Schwelle und Retraining-Zyklus produktiv freigeben,
            5. optional eine fachliche Kostenfunktion für Über- und Unterprognosen ergänzen.

            > Das Modell ersetzt keine Abrechnungs- oder Beschaffungsentscheidung. Es liefert eine
            > reproduzierbare Prognose und transparente Hinweise für die fachliche Prüfung.
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
                "builder": "scripts/build_optimized_modeling_notebook.py",
                "data_source": "data/raw/260916_verbrauch_bereinigt.csv",
                "data_sha256": data_hash,
                "design_source": "brand/design-system/tokens/design-tokens.json",
                "forecast_horizon": "rolling one month ahead",
                "development_period": "2024-01 through 2024-12",
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
