"""Build the presentation-first SWW forecasting and anomaly notebook."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import textwrap

import nbformat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = ROOT / "notebooks" / "11_modeling_pruefungsstory.ipynb"
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
            "story-intro",
            """
            # Vom Verbrauch zur prüfbaren Auffälligkeit

            **Prüfungsfassung der Verbrauchsprognose und Anomalieerkennung.** Dieses Notebook
            erzählt nicht möglichst viel Technik, sondern eine klare Entscheidungsgeschichte:

            > Wir prognostizieren zuerst, welcher Monatsverbrauch für einen Zähler plausibel wäre.
            > Weicht der gemessene Verbrauch ungewöhnlich stark davon ab, entsteht ein
            > priorisierter Prüfhinweis – noch keine automatische Fehlerdiagnose.

            ### Ergebnis auf einen Blick

            | Erklärbares Hauptmodell | Beste Baseline | Prüfhinweise 2025 | Challenger-Ausblick |
            | ---: | ---: | ---: | ---: |
            | **17,10 % WAPE** | **20,17 % WAPE** | **105 · 8,8 je Monat** | **12,04 % WAPE** |

            Die 105 Hinweise stammen aus der in dieser Revision rollierend erzeugten
            Out-of-time-Kalibrierung. Die Kennzahlen werden weiter unten vollständig hergeleitet.

            | Kapitel | Leitfrage |
            | --- | --- |
            | 1. Auftrag | Welches Geschäftsproblem lösen Prognose und Anomaliehinweis? |
            | 2. Modellentscheidung | Warum Baseline, Vollaststunden und zeitliche Validierung? |
            | 3. Prognoseergebnis | Ist der Random Forest besser als einfache Regeln? |
            | 4. Anomalieprozess | Wie wird aus einem Prognosefehler ein prüfbarer Hinweis? |
            | 5. Einsatz | Was sieht ein Mensch und wie wird der Fall bearbeitet? |
            | 6. Ausblick | Wie weit könnte ein komplexerer Challenger noch kommen? |

            Die ausführliche technische Suche bleibt in `10_modeling.ipynb`. Der optimierte
            Challenger bleibt in `20_modeling_optimierung.ipynb`. Hier steht die nachvollziehbare
            Präsentation im Mittelpunkt.
            """,
        ),
        markdown(
            "story-how-to-use",
            """
            <details><summary>So nutzt du dieses Notebook zur Prüfungsvorbereitung</summary>

            - Lies zuerst nur Überschriften, Diagramme und die blauen **„So kannst du es sagen“**-Karten.
            - Die aufklappbaren **„Wenn nachgefragt wird“**-Abschnitte sind dein Fachgespräch-Anhang.
            - Du musst keine Baumparameter auswendig lernen. Du musst begründen können, warum eine
              Baseline, ein zeitlicher Split und eine menschliche Prüfung notwendig sind.
            - 2025 wird ehrlich als bereits bekannter retrospektiver Benchmark bezeichnet.

            Ausführung: im Projektstamm `python -m uv sync --frozen --all-extras`, anschließend die
            Projektumgebung `.venv` als Kernel wählen und **Alle ausführen**.

            </details>
            """,
        ),
        code(
            "story-setup",
            r'''
            from datetime import datetime, timezone
            from html import escape
            from importlib import reload
            from importlib.util import find_spec
            from pathlib import Path
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
            from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import Ridge
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
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
            RANDOM_STATE = 42
            ANOMALY_QUANTILE = 0.99
            MIN_RELATIVE_CV_GAIN = 0.05

            ci.aktiviere(
                logo=BASE_DIR / "brand/design-system/assets/logo-sww-emblem.png",
                quelle="data/raw/260916_verbrauch_bereinigt.csv",
            )


            def de(value, digits=1):
                """German display format for narrative text."""
                if value is None or not np.isfinite(value):
                    return "—"
                return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


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


            def sprechtext(text):
                display(HTML(
                    ci.notebook_css()
                    + '<section class="sww-report" style="border-left:5px solid '
                    + theme.ROLE["prognose"] + ';">'
                    + '<p class="eyebrow">SO KANNST DU ES SAGEN</p>'
                    + f'<p style="font-size:15px"><strong>„{escape(str(text))}“</strong></p>'
                    + '</section>'
                ))


            def entscheidungsbox(befund, entscheidung, grenze):
                display(HTML(
                    ci.notebook_css()
                    + '<section class="sww-report">'
                    + '<p class="eyebrow">BEFUND → ENTSCHEIDUNG → GRENZE</p>'
                    + f'<p><strong>Befund:</strong> {escape(str(befund))}</p>'
                    + f'<p><strong>Entscheidung:</strong> {escape(str(entscheidung))}</p>'
                    + f'<p><strong>Grenze:</strong> {escape(str(grenze))}</p>'
                    + '</section>'
                ))
            ''',
        ),
        code(
            "story-data-preparation",
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
            df["stunden_im_monat"] = df["monat"].dt.days_in_month * 24
            df["dq_vertragsleistung"] = (
                df["verbrauch_kwh"]
                > df["vertragsleistung_kw"] * df["stunden_im_monat"]
            )

            # Historische Merkmale werden neu berechnet und sehen den Zielmonat niemals.
            g_kwh = df.groupby("zaehler_id", sort=False)["verbrauch_kwh"]
            df["lag_1_kwh"] = g_kwh.shift(1)
            df["rolling_3_kwh"] = g_kwh.transform(
                lambda s: s.shift(1).rolling(3, min_periods=3).mean()
            )
            df["lag_12_kwh"] = g_kwh.shift(12)

            df["ziel_vls"] = df["verbrauch_kwh"] / df["vertragsleistung_kw"]
            df["lag_1_vls"] = df["lag_1_kwh"] / df["vertragsleistung_kw"]
            df["rolling_3_vls"] = df["rolling_3_kwh"] / df["vertragsleistung_kw"]
            df["log_lag_1_kwh"] = np.log1p(df["lag_1_kwh"])
            df["log_rolling_3_kwh"] = np.log1p(df["rolling_3_kwh"])
            df["monat_sin"] = np.sin(2 * np.pi * df["monat"].dt.month / 12)
            df["monat_cos"] = np.cos(2 * np.pi * df["monat"].dt.month / 12)
            df["log_vertragsleistung_kw"] = np.log1p(df["vertragsleistung_kw"])

            d24 = (
                df[df["monat"].dt.year.eq(2024)]
                .sort_values(["monat", "zaehler_id"])
                .reset_index(drop=True)
            )
            d25 = (
                df[df["monat"].dt.year.eq(2025)]
                .sort_values(["monat", "zaehler_id"])
                .reset_index(drop=True)
            )
            selection_24 = d24[d24["monat"].dt.month.le(10)].reset_index(drop=True)
            calibration_24 = d24[d24["monat"].dt.month.ge(11)].reset_index(drop=True)
            assert len(df) == 16_800 and df["zaehler_id"].nunique() == 700
            assert d24["monat"].max() < d25["monat"].min()

            ci.ZEITRAUM = f"{df['monat'].min():%m/%Y}–{df['monat'].max():%m/%Y}"
            ci.titelkarte(
                "Vom Verbrauch zur prüfbaren Auffälligkeit",
                "Eine verständliche Prognose als Grundlage für einen menschlich kontrollierten Anomalieprozess.",
                "Datenbasis: 260916_verbrauch_bereinigt.csv · "
                f"Ausgeführt: {datetime.now(timezone.utc):%d.%m.%Y %H:%M} UTC",
                logo=BASE_DIR / "brand/design-system/assets/logo-sww-full.png",
                metriken=[
                    ("Zähler", de(df["zaehler_id"].nunique(), 0)),
                    ("Monatswerte", de(len(df), 0)),
                    ("Kalendermonate", de(df["monat"].nunique(), 0)),
                ],
                zeitraum=ci.ZEITRAUM,
            )
            ''',
        ),
        code(
            "story-chapter-business",
            '''
            ci.abschnitt(
                "01", "Geschäftsauftrag: vorhersagen, vergleichen, prüfen",
                "Eine Prognose unterstützt die Mengenplanung; ihr Fehler wird zum Anomaliesignal.",
                kontext="IHK-PRÜFUNGSSTORY",
            )
            ''',
        ),
        markdown(
            "story-business-rationale",
            """
            ### Warum brauchen wir überhaupt ein Prognosemodell?

            Der gleiche Messwert kann je nach Zähler normal oder ungewöhnlich sein. 20.000 kWh
            sind für einen kleinen Gewerbeanschluss sehr viel, für einen großen Industrieanschluss
            möglicherweise wenig. Eine starre Verbrauchsgrenze reicht deshalb nicht.

            Das Modell erzeugt für jeden Zähler und Monat einen **individuellen Erwartungswert**.
            Erst die Abweichung zwischen Erwartung und gemessenem Istwert wird bewertet.
            """,
        ),
        code(
            "story-process-overview",
            r'''
            stages = pd.DataFrame({
                "x": [0, 1, 2, 3, 4],
                "Stufe": [
                    "Historie und\nStammdaten", "Erwarteten\nVerbrauch berechnen",
                    "Istwert\neinlesen", "Abweichung\nbewerten", "Prüfhinweis an\nFachbereich",
                ],
                "Kurz": ["Daten", "Prognose", "Messung", "Score", "Mensch"],
            })
            fig = go.Figure(go.Scatter(
                x=stages["x"], y=[0] * len(stages), mode="markers+text",
                marker=dict(
                    size=[64, 72, 64, 72, 72],
                    color=[
                        theme.ROLE["ist"], theme.ROLE["prognose"],
                        theme.TOKENS["text-accent"], theme.ROLE["residuum"],
                        theme.ROLE["schwellwert"],
                    ],
                    line=dict(color=theme.TOKENS["surface-card"], width=3),
                ),
                text=stages["Kurz"], textposition="middle center",
                textfont=dict(color=theme.TOKENS["text-inverse"], size=12),
                customdata=stages["Stufe"],
                hovertemplate="%{customdata}<extra></extra>",
                showlegend=False,
            ))
            for left, right in zip(stages["x"][:-1], stages["x"][1:]):
                fig.add_annotation(
                    x=right - 0.18, y=0, ax=left + 0.18, ay=0,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=2, arrowsize=1.2,
                    arrowwidth=2, arrowcolor=theme.TOKENS["grey-400"],
                )
            for x, label in zip(stages["x"], stages["Stufe"]):
                fig.add_annotation(x=x, y=-0.42, text=label.replace("\n", "<br>"), showarrow=False)
            ci.stil(
                fig, "Vom Monatswert zum bearbeitbaren Prüfhinweis",
                "Das Modell priorisiert Fälle; die Ursache wird anschließend fachlich geprüft",
                x_titel="", y_titel="",
            )
            fig.update_xaxes(visible=False, range=[-0.45, 4.45])
            fig.update_yaxes(visible=False, range=[-0.75, 0.55])
            fig.update_layout(height=460)
            ci.zeigen(fig)
            sprechtext(
                "Ich automatisiere keine Fehlerentscheidung. Das Modell berechnet zuerst einen "
                "plausiblen Verbrauch. Nur ungewöhnlich große Abweichungen werden priorisiert "
                "und anschließend von einem Menschen geprüft."
            )
            ''',
        ),
        markdown(
            "story-business-questions",
            """
            <details><summary>Wenn nachgefragt wird: Prognosefehler oder echte Anomalie?</summary>

            Ein großer Prognosefehler ist zunächst nur ein **Hinweis**. Mögliche Ursachen sind
            beispielsweise ein Ablesefehler, eine geplante Wartung, Produktionsstillstand,
            Leitungsverlust oder ein echtes ungewöhnliches Verbrauchsverhalten. Ohne bestätigte
            Falllabels darf das Modell nicht behaupten, welche Ursache vorliegt.

            **Prüfungsantwort:** „Die Prognose liefert die Referenz. Der Algorithmus priorisiert;
            der Fachbereich diagnostiziert.“

            </details>
            """,
        ),
        code(
            "story-chapter-model",
            '''
            ci.abschnitt(
                "02", "Eine faire und erklärbare Modellentscheidung",
                "Vollaststunden machen Zähler vergleichbarer; Zeitfalten schützen vor Zukunftswissen.",
                kontext="PROGNOSE ALS REFERENZ",
            )
            ''',
        ),
        markdown(
            "story-glossary",
            """
            ### Sechs Begriffe, die für die Geschichte genügen

            | Begriff | Bedeutung in diesem Projekt |
            | --- | --- |
            | **Baseline** | Eine einfache Referenzregel, die ein ML-Modell zuerst schlagen muss. |
            | **Vollaststunden (VLS)** | Rechnerische Normierung: Verbrauch in kWh geteilt durch Vertragsleistung in kW. Keine gemessene Maschinenlaufzeit. |
            | **WAPE** | Summe aller absoluten Fehler geteilt durch die gesamte Ist-Energie. Niedriger ist besser. |
            | **Zeitfold** | Training auf früheren Monaten, Prüfung auf späteren Monaten. |
            | **Residuum** | Abweichung zwischen Ist und Prognose; hier relativ und robust normiert. |
            | **Prüfhinweis** | Ein ungewöhnlicher Fall für einen Menschen – keine automatisch bestätigte Störung. |

            **Wichtig:** 17 % WAPE bedeutet nicht „83 % Genauigkeit“ und auch nicht, dass jeder
            Zähler genau 17 % danebenliegt. Große Verbraucher wiegen bei WAPE stärker, weil mehr
            kWh in die Summe eingehen.
            """,
        ),
        code(
            "story-vls-example",
            r'''
            vls_example = pd.DataFrame([
                ["Kleiner Anschluss", 100, 150, 15_000],
                ["Großer Anschluss", 1_000, 150, 150_000],
                ["Konkretes Beispiel", 300, 100, 30_000],
            ], columns=["Beispiel", "Vertragsleistung (kW)", "VLS", "Verbrauch (kWh)"])
            display(ci.tabellenansicht(vls_example, 0))
            sprechtext(
                "Vollaststunden sind keine echten Laufzeiten. Sie teilen den Verbrauch durch die "
                "Anschlussgröße, damit das Modell große und kleine Zähler auf einer vergleichbareren "
                "Skala lernt. Für Nutzer und Bewertung rechne ich anschließend wieder in kWh zurück."
            )
            ''',
        ),
        code(
            "story-time-split",
            r'''
            timeline = pd.DataFrame([
                ["Fold 1 · Training", "2024-01-01", "2024-04-30", "Training"],
                ["Fold 1 · Prüfung", "2024-05-01", "2024-06-30", "Validierung"],
                ["Fold 2 · Training", "2024-01-01", "2024-06-30", "Training"],
                ["Fold 2 · Prüfung", "2024-07-01", "2024-08-31", "Validierung"],
                ["Fold 3 · Training", "2024-01-01", "2024-08-31", "Training"],
                ["Fold 3 · Prüfung", "2024-09-01", "2024-10-31", "Validierung"],
                ["Schwellenkalibrierung", "2024-11-01", "2024-12-31", "Kalibrierung"],
                ["Retrospektiver Benchmark", "2025-01-01", "2025-12-31", "Benchmark"],
            ], columns=["Phase", "Start", "Ende", "Rolle"])
            timeline[["Start", "Ende"]] = timeline[["Start", "Ende"]].apply(pd.to_datetime)
            fig = px.timeline(
                timeline, x_start="Start", x_end="Ende", y="Phase", color="Rolle",
                color_discrete_map={
                    "Training": theme.ROLE["ist"],
                    "Validierung": theme.TOKENS["text-accent"],
                    "Kalibrierung": theme.ROLE["schwellwert"],
                    "Benchmark": theme.TOKENS["grey-400"],
                },
            )
            ci.stil(
                fig, "Nur die Vergangenheit darf die Zukunft erklären",
                "Drei vorwärts laufende Folds · eigenes Kalibrierungsfenster · späterer 2025-Benchmark",
                x_titel="Monat", y_titel="",
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_xaxes(tickformat="%m/%Y", dtick="M2")
            ci.zeigen(fig)
            sprechtext(
                "Ich teile nicht zufällig. Bei jeder Prüfung liegt das Training zeitlich davor. "
                "Für eine Juni-Prognose darf der inzwischen bekannte Mai-Verbrauch verwendet werden; "
                "der Juni-Verbrauch selbst bleibt unsichtbar."
            )
            ''',
        ),
        markdown(
            "story-model-rationale",
            """
            ### Welche Informationen erhält das Hauptmodell?

            - Anschlussgröße und Kundentyp
            - Vormonatsverbrauch und Mittel der vorherigen drei Monate – stets mit `shift(1)`
            - Arbeitstage, Feiertage und Jahreszeit

            Produktionsplan, Wartung und tatsächlich eingetretene Heiztage bleiben aus dem
            **erklärbaren Hauptmodell** heraus. Reale Heiztage kennt man vor Monatsbeginn nicht.
            Plan- und Wartungsdaten sind nur dann produktiv zulässig, wenn nachweisbar ist, dass
            genau der historische Stichtagsstand gespeichert wurde. Sie erscheinen deshalb erst
            im Challenger-Ausblick.

            Als Baselines dienen der unveränderte **Vormonat** und das **Drei-Monats-Mittel**.
            Ein komplexeres Modell ist nur sinnvoll, wenn es diese Regeln stabil schlägt.
            """,
        ),
        code(
            "story-model-pipeline",
            r'''
            NUM_FEATURES = [
                "log_vertragsleistung_kw", "arbeitstage", "feiertage_im_monat",
                "lag_1_vls", "rolling_3_vls", "log_lag_1_kwh",
                "log_rolling_3_kwh", "monat_sin", "monat_cos",
            ]
            CAT_FEATURES = ["kundentyp"]
            X_COLUMNS = ["vertragsleistung_kw", *NUM_FEATURES, *CAT_FEATURES]

            fold_definitions = [
                ("2024-04-01", "2024-05-01", "2024-06-30"),
                ("2024-06-01", "2024-07-01", "2024-08-31"),
                ("2024-08-01", "2024-09-01", "2024-10-31"),
            ]
            cv_2024 = []
            for train_end, valid_start, valid_end in fold_definitions:
                train_idx = np.flatnonzero(selection_24["monat"].le(pd.Timestamp(train_end)))
                valid_idx = np.flatnonzero(selection_24["monat"].between(
                    pd.Timestamp(valid_start), pd.Timestamp(valid_end)
                ))
                assert selection_24.iloc[train_idx]["monat"].max() < selection_24.iloc[valid_idx]["monat"].min()
                cv_2024.append((train_idx, valid_idx))

            category_pipe = Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ])
            linear_pre = ColumnTransformer([
                ("num", Pipeline([
                    ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
                    ("scale", StandardScaler()),
                ]), NUM_FEATURES),
                ("cat", category_pipe, CAT_FEATURES),
            ])
            tree_pre = ColumnTransformer([
                ("num", SimpleImputer(strategy="median", keep_empty_features=True), NUM_FEATURES),
                ("cat", category_pipe, CAT_FEATURES),
            ], sparse_threshold=0.0)

            # Die Parameter sind das Ergebnis der Suche im technischen Notebook 10.
            # Hier werden sie fixiert, damit die Prüfungsstory reproduzierbar bleibt.
            candidates = {
                "Ridge": Pipeline([
                    ("pre", linear_pre), ("model", Ridge(alpha=0.1)),
                ]),
                "Random Forest": Pipeline([
                    ("pre", tree_pre),
                    ("model", RandomForestRegressor(
                        n_estimators=180, max_features=0.7, max_depth=8,
                        min_samples_leaf=20, n_jobs=1, random_state=RANDOM_STATE,
                    )),
                ]),
                "HistGradientBoosting": Pipeline([
                    ("pre", tree_pre),
                    ("model", HistGradientBoostingRegressor(
                        loss="absolute_error", learning_rate=0.10, max_iter=300,
                        max_leaf_nodes=7, min_samples_leaf=100,
                        l2_regularization=1.0, early_stopping=False,
                        random_state=RANDOM_STATE,
                    )),
                ]),
            }

            def predict_kwh(estimator, frame):
                vls = np.clip(estimator.predict(frame[X_COLUMNS]), 0, None)
                return vls * frame["vertragsleistung_kw"].to_numpy(float)
            ''',
        ),
        code(
            "story-model-comparison",
            r'''
            cv_rows = []
            for fold, (train_idx, valid_idx) in enumerate(cv_2024, start=1):
                train = selection_24.iloc[train_idx]
                valid = selection_24.iloc[valid_idx]
                for model_name, estimator in candidates.items():
                    fitted = clone(estimator).fit(train[X_COLUMNS], train["ziel_vls"])
                    cv_rows.append({
                        "Kandidat": f"Vollaststunden · {model_name}",
                        "Typ": "Modell", "Fold": fold,
                        "WAPE (%)": wape(valid["verbrauch_kwh"], predict_kwh(fitted, valid)),
                    })
                for baseline_name, column in {
                    "Vormonat": "lag_1_kwh",
                    "3-Monats-Mittel": "rolling_3_kwh",
                }.items():
                    cv_rows.append({
                        "Kandidat": baseline_name, "Typ": "Baseline", "Fold": fold,
                        "WAPE (%)": wape(valid["verbrauch_kwh"], valid[column]),
                    })

            cv_detail = pd.DataFrame(cv_rows)
            cv_summary = (
                cv_detail.groupby(["Kandidat", "Typ"], as_index=False)
                .agg(
                    **{"CV-WAPE (%)": ("WAPE (%)", "mean")},
                    **{"Fold-Streuung (%)": ("WAPE (%)", lambda values: values.std(ddof=0))},
                )
                .sort_values("CV-WAPE (%)")
                .reset_index(drop=True)
            )
            best_model = cv_summary[cv_summary["Typ"].eq("Modell")].iloc[0]
            best_baseline_cv = cv_summary[cv_summary["Typ"].eq("Baseline")].iloc[0]
            relative_cv_gain = 1 - best_model["CV-WAPE (%)"] / best_baseline_cv["CV-WAPE (%)"]
            assert best_model["Kandidat"] == "Vollaststunden · Random Forest"
            assert relative_cv_gain >= MIN_RELATIVE_CV_GAIN

            ordered = cv_summary.sort_values("CV-WAPE (%)", ascending=False)
            fig = go.Figure(go.Bar(
                x=ordered["CV-WAPE (%)"], y=ordered["Kandidat"], orientation="h",
                marker_color=[
                    theme.ROLE["prognose"]
                    if name == best_model["Kandidat"]
                    else theme.TOKENS["grey-400"]
                    if kind == "Baseline"
                    else theme.TOKENS["grey-300"]
                    for name, kind in zip(ordered["Kandidat"], ordered["Typ"])
                ],
                error_x=dict(type="data", array=ordered["Fold-Streuung (%)"], visible=True),
                text=[f"{de(value, 1)} %" for value in ordered["CV-WAPE (%)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig, "Zeitlicher Modellvergleich 2024",
                "Mittel aus drei vorwärts laufenden Prüfungen · Fehlerbalken zeigen die Fold-Streuung",
                x_titel="WAPE (%) – niedriger ist besser", y_titel="",
            )
            ci.prozent_achse(fig, "x", 0)
            ci.gitter_x(fig)
            ci.zeigen(fig)
            display(ci.tabellenansicht(cv_summary, 2))

            cv_gap_pp = best_baseline_cv["CV-WAPE (%)"] - best_model["CV-WAPE (%)"]
            entscheidungsbox(
                f"Random Forest erreicht {de(best_model['CV-WAPE (%)'], 2)} % CV-WAPE; "
                f"das Drei-Monats-Mittel {de(best_baseline_cv['CV-WAPE (%)'], 2)} %.",
                f"Der Vorsprung beträgt {de(cv_gap_pp, 2)} Prozentpunkte beziehungsweise "
                f"{de(relative_cv_gain * 100, 1)} % relativ und überschreitet das vorab gesetzte 5-%-Gate.",
                "Nur drei Folds aus einem Jahr: Der Vergleich stützt die Wahl, garantiert aber keine Zukunftsleistung."
            )
            sprechtext(
                f"Die Differenz beträgt {de(cv_gap_pp, 2)} Prozentpunkte. Bezogen auf die Baseline "
                f"sind das {de(relative_cv_gain * 100, 1)} Prozent relative Verbesserung. "
                "Beide Angaben sind richtig, beantworten aber unterschiedliche Fragen."
            )
            ''',
        ),
        markdown(
            "story-model-questions",
            """
            <details><summary>Wenn nachgefragt wird: Warum Random Forest und kein neuronales Netz?</summary>

            Ein Random Forest ist ein Team vieler Entscheidungsbäume. Einzelne Bäume sehen leicht
            unterschiedliche Stichproben; gemittelt entsteht eine stabilere Prognose. Das Verfahren
            kann nichtlineare Wechselwirkungen abbilden, bleibt bei 16.800 Zeilen aber besser
            begründbar als ein neuronales Netz. Gewählt wurde es nicht nach Geschmack, sondern weil
            es den zeitlichen Vergleich 2024 gewann.

            Die gezeigten Parameter (`max_depth`, `min_samples_leaf`, `max_features`) steuern vor
            allem Baumtiefe, Blattgröße und zufällige Merkmalsauswahl. Für die Präsentation genügt:
            **Die Suche war auf 2024 begrenzt; stärkere Begrenzung der Bäume reduziert Overfitting.**

            </details>
            """,
        ),
        code(
            "story-fit-models",
            r'''
            selected_rf = candidates["Random Forest"]
            selection_model = clone(selected_rf).fit(
                selection_24[X_COLUMNS], selection_24["ziel_vls"]
            )
            final_model = clone(selected_rf).fit(d24[X_COLUMNS], d24["ziel_vls"])
            ''',
        ),
        code(
            "story-chapter-results",
            '''
            ci.abschnitt(
                "03", "Prognoseergebnis: belastbar besser als die Baseline",
                "2025 zeigt den Nutzen in kWh – und zugleich die Grenzen eines retrospektiven Benchmarks.",
                kontext="PROGNOSE ALS REFERENZ",
            )
            ''',
        ),
        code(
            "story-test-benchmark",
            r'''
            scored_25 = d25.copy()
            scored_25["prognose_kwh"] = predict_kwh(final_model, scored_25)
            final_candidates = {
                "Random Forest · Vollaststunden": "prognose_kwh",
                "3-Monats-Mittel": "rolling_3_kwh",
                "Vorjahresmonat": "lag_12_kwh",
                "Vormonat": "lag_1_kwh",
            }
            common = scored_25[["verbrauch_kwh", *final_candidates.values()]].notna().all(axis=1)
            final_rows = []
            for name, column in final_candidates.items():
                final_rows.append({
                    "Kandidat": name,
                    **regression_metrics(
                        scored_25.loc[common, "verbrauch_kwh"], scored_25.loc[common, column]
                    ),
                })
            final_metrics = pd.DataFrame(final_rows).sort_values("WAPE (%)").reset_index(drop=True)
            champion_metrics = final_metrics.set_index("Kandidat").loc["Random Forest · Vollaststunden"]
            baseline_metrics = final_metrics[~final_metrics["Kandidat"].eq("Random Forest · Vollaststunden")]
            best_baseline = baseline_metrics.sort_values("WAPE (%)").iloc[0]
            improvement = 1 - champion_metrics["WAPE (%)"] / best_baseline["WAPE (%)"]

            ordered = final_metrics.sort_values("WAPE (%)", ascending=False)
            fig = go.Figure(go.Bar(
                x=ordered["WAPE (%)"], y=ordered["Kandidat"], orientation="h",
                marker_color=[
                    theme.ROLE["prognose"] if name == "Random Forest · Vollaststunden"
                    else theme.TOKENS["grey-400"] for name in ordered["Kandidat"]
                ],
                text=[f"{de(value, 2)} %" for value in ordered["WAPE (%)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig, "Retrospektiver Benchmark 2025",
                f"Alle Verfahren auf denselben {de(common.sum(), 0)} Zähler-Monaten",
                x_titel="WAPE (%) – niedriger ist besser", y_titel="",
            )
            ci.prozent_achse(fig, "x", 0)
            ci.gitter_x(fig)
            ci.zeigen(fig)
            display(ci.tabellenansicht(final_metrics, 2))

            test_gap_pp = best_baseline["WAPE (%)"] - champion_metrics["WAPE (%)"]
            entscheidungsbox(
                f"Random Forest erreicht {de(champion_metrics['WAPE (%)'], 2)} % WAPE und "
                f"{de(champion_metrics['MAE (kWh)'], 0)} kWh MAE. Die beste einfache Regel "
                f"erreicht {de(best_baseline['WAPE (%)'], 2)} % WAPE.",
                f"Das sind {de(test_gap_pp, 2)} Prozentpunkte beziehungsweise "
                f"{de(improvement * 100, 1)} % relative Verbesserung.",
                "2025 ist zeitlich später, wurde aber bereits in der EDA gesehen: retrospektiver Benchmark, kein unangesehener Blindtest."
            )
            sprechtext(
                f"Der Modellfehler entspricht in Summe {de(champion_metrics['WAPE (%)'], 2)} Prozent "
                "der tatsächlich verbrauchten Energie. Das ist keine Genauigkeitsquote pro Zähler."
            )
            ''',
        ),
        markdown(
            "story-wape-detail",
            """
            <details><summary>Wenn nachgefragt wird: Warum WAPE, MAE, R² und Bias?</summary>

            - **WAPE** ist die Hauptkennzahl: absoluter Gesamtfehler relativ zur gesamten Energie.
              Kleine Istwerte lassen die Kennzahl nicht explodieren wie bei MAPE.
            - **MAE** sagt, wie viele kWh ein Zähler-Monat im Mittel absolut danebenliegt.
            - **R²** beschreibt erklärte Streuung, ist aber allein kein geschäftlicher Fehlerwert.
            - **Bias** zeigt eine systematische Über- oder Unterschätzung. Positive und negative
              Einzelfehler dürfen im WAPE nicht gegeneinander verschwinden.

            Große Verbraucher wiegen bei WAPE stärker. Deshalb werden später zusätzlich Segmente,
            Richtung und einzelne Fälle geprüft.

            </details>
            """,
        ),
        code(
            "story-portfolio",
            r'''
            portfolio = (
                scored_25.groupby("monat", as_index=False)
                .agg(ist_kwh=("verbrauch_kwh", "sum"), prognose_kwh=("prognose_kwh", "sum"))
            )
            portfolio_metrics = regression_metrics(portfolio["ist_kwh"], portfolio["prognose_kwh"])
            fig = eda.timeseries_forecast(
                portfolio["monat"], portfolio["ist_kwh"] / 1e6,
                portfolio["prognose_kwh"] / 1e6,
                y_title="Energie (GWh)",
            )
            ci.stil(
                fig, "Portfolio-Sicht für Mengenplanung",
                f"Aggregierter WAPE {de(portfolio_metrics['WAPE (%)'], 2)} % · Bias {de(portfolio_metrics['Bias (%)'], 2)} %",
                x_titel="Monat", y_titel="Energie (GWh)",
            )
            fig.update_xaxes(tickformat="%m/%Y", dtick="M2")
            ci.zeigen(fig)
            sprechtext(
                f"Auf Portfolioebene sinkt der WAPE auf {de(portfolio_metrics['WAPE (%)'], 2)} Prozent, "
                "weil Über- und Unterschätzungen verschiedener Zähler sich beim Summieren teilweise "
                "ausgleichen. Für Anomalien bleibt deshalb die zählerscharfe Sicht entscheidend."
            )
            ''',
        ),
        code(
            "story-chapter-anomalies",
            '''
            ci.abschnitt(
                "04", "Kernaufgabe: von der Prognose zum Prüfhinweis",
                "Eine ungewöhnlich große Modellabweichung wird priorisiert – nicht automatisch diagnostiziert.",
                kontext="RESIDUALBASIERTE ANOMALIEERKENNUNG",
            )
            ''',
        ),
        markdown(
            "story-anomaly-principle",
            """
            ### Was bedeutet „Anomalie“ in diesem Projekt?

            ```text
            Ist ungefähr Prognose       → üblicher Modellfehler
            Ist deutlich über Prognose  → ungewöhnlich hoher Verbrauch
            Ist deutlich unter Prognose → ungewöhnlich niedriger Verbrauch
            ```

            Ein absoluter kWh-Fehler wäre für kleine und große Anschlüsse schlecht vergleichbar.
            Deshalb wird zuerst eine **relative logarithmische Abweichung** gebildet:

            `Log-Residuum = log(1 + Ist) − log(1 + Prognose)`

            Innerhalb jedes Kundentyps wird diese Abweichung anschließend robust mit Median und
            MAD normiert. Median und MAD reagieren deutlich weniger auf Extremfälle als Mittelwert
            und Standardabweichung. Der Betrag ist der Anomalie-Score.

            > Der Score ist keine Fehlerwahrscheinlichkeit und kein klassischer Z-Wert in
            > Standardabweichungen. Er ist eine robuste Priorisierungszahl.
            """,
        ),
        code(
            "story-anomaly-example",
            r'''
            anomaly_example = pd.DataFrame([
                [10_000, 10_200, "+2 %", "eher gewöhnlich"],
                [10_000, 2_000, "−80 %", "ungewöhnlich niedrig"],
                [10_000, 25_000, "+150 %", "ungewöhnlich hoch"],
            ], columns=["Prognose (kWh)", "Ist (kWh)", "relative Abweichung", "erste Einordnung"])
            display(ci.tabellenansicht(anomaly_example, 0))
            sprechtext(
                "Ich suche nicht einfach hohe Verbräuche. Ich suche Werte, die gemessen an der "
                "individuellen Erwartung und am typischen Fehler des Kundentyps ungewöhnlich sind."
            )
            ''',
        ),
        code(
            "story-calibration-distribution",
            r'''
            # Rollierende Out-of-time-Residuen: Für jeden Kalibriermonat wird nur die
            # davor bekannte Historie verwendet. Die Modellspezifikation bleibt fix.
            calibration_parts = []
            for month in sorted(calibration_24["monat"].unique()):
                train = d24[d24["monat"].lt(month)]
                valid = d24[d24["monat"].eq(month)].copy()
                rolling_model = clone(selected_rf).fit(train[X_COLUMNS], train["ziel_vls"])
                valid["prognose_kwh"] = predict_kwh(rolling_model, valid)
                calibration_parts.append(valid)
            calibration_residuals = pd.concat(calibration_parts, ignore_index=True)
            calibration_residuals["residuum_log"] = (
                np.log1p(calibration_residuals["verbrauch_kwh"])
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
            calibration_residuals["anomalie_score"] = calibration_residuals["score_signiert"].abs()
            anomaly_threshold = calibration_residuals["anomalie_score"].quantile(ANOMALY_QUANTILE)

            fig = eda.residual_hist(
                calibration_residuals["score_signiert"], anomaly_threshold,
                x_title="Robust normierte relative Abweichung", nbins=60,
            )
            if fig.layout.annotations:
                fig.layout.annotations[0].text = f"Schwelle ±{de(anomaly_threshold, 2)}"
            ci.stil(
                fig, "Was war im Kalibrierungsfenster ungewöhnlich?",
                "Rollierende Prognosen für November und Dezember 2024 · getrennt von Auswahl und Benchmark",
                x_titel="Signierter Anomalie-Score", y_titel="Anzahl",
            )
            ci.zeigen(fig)
            sprechtext(
                f"Die Schwelle von {de(anomaly_threshold, 2)} stammt ausschließlich aus zwei "
                "rollierend prognostizierten Monaten 2024. Sie wird danach unverändert auf 2025 "
                "angewendet. Der Wert ist keine Wahrscheinlichkeit."
            )
            ''',
        ),
        code(
            "story-threshold",
            r'''
            threshold_rows = []
            for quantile in (0.90, 0.95, 0.975, 0.99, 0.995):
                threshold = calibration_residuals["anomalie_score"].quantile(quantile)
                alerts = calibration_residuals["anomalie_score"].ge(threshold).sum()
                threshold_rows.append({
                    "Perzentil": quantile * 100,
                    "Schwelle": threshold,
                    "Prüfhinweise je Monat": alerts / calibration_residuals["monat"].nunique(),
                })
            threshold_table = pd.DataFrame(threshold_rows)
            fig = go.Figure(go.Scatter(
                x=threshold_table["Perzentil"], y=threshold_table["Prüfhinweise je Monat"],
                mode="lines+markers+text",
                line=dict(color=theme.ROLE["residuum"], width=3),
                marker=dict(size=9),
                text=[de(value, 1) for value in threshold_table["Prüfhinweise je Monat"]],
                textposition="top center",
            ))
            ci.stil(
                fig, "Sensitivität gegen Prüfaufwand",
                "Eine niedrigere Schwelle findet mehr Kandidaten, erzeugt aber mehr Arbeit und Fehlalarme",
                x_titel="Perzentil der Kalibrierungsfehler", y_titel="Prüfhinweise je Monat",
            )
            ci.referenzlinie(
                fig, ANOMALY_QUANTILE * 100,
                f"Arbeitshypothese {de(ANOMALY_QUANTILE * 100, 1)} %",
                achse="x", position="top left",
            )
            ci.zeigen(fig)
            display(ci.tabellenansicht(threshold_table, 2))
            sprechtext(
                "Das 99. Perzentil ist keine mathematisch optimale Wahrheit. Es ist eine "
                "dokumentierte Arbeitshypothese, die Sensitivität gegen eine ungefähr tragbare "
                "Prüfmenge abwägt. Mit bestätigten Fällen würde ich diese Schwelle neu optimieren."
            )
            ''',
        ),
        code(
            "story-alerts",
            r'''
            scored_25["residuum_log"] = (
                np.log1p(scored_25["verbrauch_kwh"])
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
            scored_25["abweichung_kwh"] = scored_25["verbrauch_kwh"] - scored_25["prognose_kwh"]
            scored_25["abweichung_prozent"] = (
                scored_25["abweichung_kwh"] / scored_25["prognose_kwh"].clip(lower=1) * 100
            )

            alert_counts = (
                scored_25[scored_25["anomalie"]]
                .groupby(["monat", "richtung"], observed=True).size()
                .unstack(fill_value=0)
                .reindex(columns=["ungewöhnlich niedrig", "ungewöhnlich hoch"], fill_value=0)
            )
            fig = eda.anomaly_stack(
                alert_counts.index,
                {column: alert_counts[column] for column in alert_counts.columns},
            )
            total_alerts = int(scored_25["anomalie"].sum())
            alerts_per_month = total_alerts / scored_25["monat"].nunique()
            alert_rate = total_alerts / len(scored_25) * 100
            unique_alert_meters = scored_25.loc[scored_25["anomalie"], "zaehler_id"].nunique()
            ci.stil(
                fig, "Prüfhinweise 2025: Richtung und Monatslast",
                f"{total_alerts} von {de(len(scored_25), 0)} Zähler-Monaten · {de(alerts_per_month, 1)} Hinweise je Monat",
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

            dq_total = int(scored_25["dq_vertragsleistung"].sum())
            dq_overlap = int((scored_25["dq_vertragsleistung"] & scored_25["anomalie"]).sum())
            direction_counts = scored_25.loc[scored_25["anomalie"], "richtung"].value_counts()
            entscheidungsbox(
                f"Die feste Regel erzeugt {total_alerts} Hinweise ({de(alert_rate, 2)} %) bei "
                f"{unique_alert_meters} unterschiedlichen Zählern; im Mittel {de(alerts_per_month, 1)} je Monat.",
                "Hohe und niedrige Abweichungen gehen gemeinsam mit Segment und Kontext in eine priorisierte Arbeitsliste.",
                f"Zusätzlich existieren {dq_total} harte Kapazitäts-Plausibilitätsflags; {dq_overlap} überschneiden sich. "
                "Datenqualitätsregel und Verbrauchsanomalie bleiben zwei getrennte Hinweisarten."
            )
            ''',
        ),
        markdown(
            "story-alert-interpretation",
            """
            ### Was ist mit diesen Hinweisen belegt – und was nicht?

            | Vertretbare Aussage | Nicht vertretbare Aussage |
            | --- | --- |
            | Die feste Regel priorisiert reproduzierbar ungewöhnliche Modellabweichungen. | Alle markierten Fälle sind technische Defekte. |
            | Die Menge ist als monatliche Arbeitsliste sichtbar. | Das 99. Perzentil ist statistisch optimal. |
            | Segmentquoten und Richtung können kontrolliert werden. | Der Score nennt automatisch die Ursache. |
            | Die Schwelle stammt nicht aus 2025. | 2025 muss deshalb exakt 1 % Hinweise enthalten. |

            Das 99. Perzentil gilt für die Kalibrierungsmonate. Eine spätere Verteilung darf sich
            verschieben. Ohne **gelabelte reale Anomalien** lassen sich Precision, Recall und die
            Zahl übersehener Störungen nicht seriös berechnen.
            """,
        ),
        code(
            "story-case",
            r'''
            case_row = scored_25.loc[scored_25["anomalie_score"].idxmax()]
            case_id = case_row["zaehler_id"]
            case = scored_25[scored_25["zaehler_id"].eq(case_id)].sort_values("monat")
            flagged = case[case["anomalie"]]
            fig = eda.timeseries_forecast(
                case["monat"], case["verbrauch_kwh"], case["prognose_kwh"],
                anomalien=(flagged["monat"], flagged["verbrauch_kwh"]),
                y_title="Verbrauch (kWh)",
            )
            ci.stil(
                fig, f"Vom Score zum prüfbaren Fall · {case_id}",
                "Automatisch gewählt: höchster Anomalie-Score im Benchmarkjahr",
                x_titel="Monat", y_titel="Verbrauch (kWh)",
            )
            fig.update_xaxes(tickformat="%m/%Y", dtick="M2")
            ci.zeigen(fig)

            case_card = pd.DataFrame({
                "Merkmal": [
                    "Monat", "Kundentyp", "Ist (kWh)", "Prognose (kWh)",
                    "Abweichung (kWh)", "Abweichung (%)", "Score",
                    "Richtung", "Wartung aktiv", "Produktionsplan-Index",
                    "Kapazitäts-Plausibilitätsflag",
                ],
                "Wert": [
                    case_row["monat"].strftime("%m/%Y"), case_row["kundentyp"],
                    de(case_row["verbrauch_kwh"], 2), de(case_row["prognose_kwh"], 2),
                    de(case_row["abweichung_kwh"], 2), de(case_row["abweichung_prozent"], 2),
                    de(case_row["anomalie_score"], 2), case_row["richtung"],
                    "ja" if case_row["wartung_aktiv"] else "nein",
                    de(case_row["produktionsplan_index"], 2),
                    "ja" if case_row["dq_vertragsleistung"] else "nein",
                ],
            })
            display(ci.tabellenansicht(case_card, 2))
            sprechtext(
                f"Bei {case_id} liegt der Istwert {de(abs(case_row['abweichung_prozent']), 1)} Prozent "
                f"{'unter' if case_row['abweichung_kwh'] < 0 else 'über'} der Prognose. "
                f"Wartung ist {'aktiv' if case_row['wartung_aktiv'] else 'nicht aktiv'} und damit nur "
                "ein Kontext für die Prüfung, kein vom Modell bewiesener Grund."
            )
            ''',
        ),
        markdown(
            "story-case-questions",
            """
            <details><summary>Wenn nachgefragt wird: Erkennt das Modell Wartung oder einen Defekt?</summary>

            Nein. Wartung wurde im Hauptmodell nicht als Eingabe verwendet und dient hier nur als
            Kontextinformation. Selbst wenn bei einem markierten Fall `wartung_aktiv = 1` steht,
            ist das eine plausible Prüfspur, keine Kausaldiagnose. Das Modell ersetzt keine
            technische Untersuchung und keine fachliche Entscheidung.

            </details>
            """,
        ),
        code(
            "story-chapter-operations",
            '''
            ci.abschnitt(
                "05", "Vom Notebook in einen kontrollierten Arbeitsprozess",
                "Der Wert entsteht erst, wenn ein Hinweis geprüft, entschieden und zurückgemeldet wird.",
                kontext="MENSCHLICHE ENTSCHEIDUNG",
            )
            ''',
        ),
        code(
            "story-operations-flow",
            r'''
            process = pd.DataFrame({
                "x": list(range(5)),
                "Titel": ["Priorisieren", "Daten prüfen", "Kontext prüfen", "Handeln", "Lernen"],
                "Detail": [
                    "Score, Richtung, Auswirkung",
                    "Messwert und Plausibilitätsflag",
                    "Wartung, Stillstand, Produktion",
                    "Fachprüfung oder Ticket",
                    "Ursache als Label zurückspielen",
                ],
            })
            fig = go.Figure(go.Scatter(
                x=process["x"], y=[0] * len(process), mode="markers+text",
                marker=dict(
                    size=70, color=[
                        theme.ROLE["residuum"], theme.TOKENS["text-accent"],
                        theme.ROLE["ist"], theme.ROLE["schwellwert"], theme.ROLE["prognose"],
                    ], line=dict(color=theme.TOKENS["surface-card"], width=3),
                ),
                text=process["Titel"], textposition="middle center",
                textfont=dict(color=theme.TOKENS["text-inverse"], size=11),
                customdata=process["Detail"], hovertemplate="%{customdata}<extra></extra>",
                showlegend=False,
            ))
            for left, right in zip(process["x"][:-1], process["x"][1:]):
                fig.add_annotation(
                    x=right - 0.18, y=0, ax=left + 0.18, ay=0,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=2, arrowwidth=2,
                    arrowcolor=theme.TOKENS["grey-400"],
                )
            for x, detail in zip(process["x"], process["Detail"]):
                fig.add_annotation(x=x, y=-0.42, text=detail.replace(", ", "<br>"), showarrow=False)
            ci.stil(
                fig, "Ein Alert ist der Anfang, nicht das Ende",
                "Die Rückmeldung aus der Fachprüfung schafft erst die Labels für eine echte Erkennungsbewertung",
                x_titel="", y_titel="",
            )
            fig.update_xaxes(visible=False, range=[-0.5, 4.5])
            fig.update_yaxes(visible=False, range=[-0.75, 0.55])
            fig.update_layout(height=470)
            ci.zeigen(fig)

            operations_table = pd.DataFrame([
                [1, "Messwert und Datenqualität prüfen", "gültig / korrigieren"],
                [2, "Wartung, Stillstand, Produktionsänderung abgleichen", "erklärt / ungeklärt"],
                [3, "Betrieb oder Kundenbetreuung einbeziehen", "prüfen / Ticket"],
                [4, "Ursache und Entscheidung dokumentieren", "Anomalielabel"],
                [5, "Schwelle und Modell regelmäßig überwachen", "beibehalten / anpassen"],
            ], columns=["Schritt", "Prüfung", "möglicher Ausgang"])
            display(ci.tabellenansicht(operations_table, 0))
            sprechtext(
                "Das spätere Dashboard sollte nicht nur rote Punkte zeigen. Es muss Ist, Prognose, "
                "Abweichung, Kontext und eine dokumentierbare Entscheidung zusammenführen. Genau "
                "diese Rückmeldungen ermöglichen später Precision und Recall."
            )
            ''',
        ),
        code(
            "story-chapter-outlook",
            '''
            ci.abschnitt(
                "06", "Ausblick: mehr Genauigkeit ist möglich – mit Bedingungen",
                "Der optimierte Challenger zeigt Potenzial, bleibt aber bewusst außerhalb der Hauptentscheidung.",
                kontext="FORSCHUNGSSTAND STATT PRODUKTIONSFREIGABE",
            )
            ''',
        ),
        markdown(
            "story-outlook-rationale",
            """
            ### Warum der optimierte Wert nur als Ausblick erscheint

            Im separaten Notebook `20_modeling_optimierung.ipynb` wurde nach der verständlichen
            Hauptlösung ein komplexerer Challenger untersucht. Er verwendet deutlich mehr
            historische Merkmale sowie Produktionsplan- und Wartungsinformationen. Der größte
            Gewinn stammt **nicht** aus einem riesigen Hyperparameter-Tuning, sondern aus diesem
            breiteren Feature-Set.

            Für die IHK-Aufgabe gelten Plan und Wartung laut Projektbeschreibung als zu Monatsbeginn
            bekannt. Im echten Betrieb müssen dafür aber versionierte historische Plan-Snapshots
            nachgewiesen werden: Nicht der später korrigierte Plan, sondern nur der Stand, der am
            Prognosestichtag tatsächlich verfügbar war.
            """,
        ),
        code(
            "story-outlook",
            r'''
            CHALLENGER_WAPE = 12.041
            CHALLENGER_CV_WAPE = 14.561
            challenger_gain = 1 - CHALLENGER_WAPE / champion_metrics["WAPE (%)"]
            outlook = pd.DataFrame([
                ["Erklärbarer Random Forest", champion_metrics["WAPE (%)"], "Hauptlösung"],
                ["Optimierter Challenger", CHALLENGER_WAPE, "noch nicht freigegeben"],
            ], columns=["Modellstatus", "2025-WAPE (%)", "Einordnung"])
            fig = go.Figure(go.Bar(
                x=outlook["2025-WAPE (%)"], y=outlook["Modellstatus"], orientation="h",
                marker_color=[theme.ROLE["prognose"], theme.ROLE["schwellwert"]],
                text=[f"{de(value, 2)} %" for value in outlook["2025-WAPE (%)"]],
                textposition="outside", cliponaxis=False,
            ))
            ci.stil(
                fig, "Hauptlösung und optimierter Challenger",
                "Retrospektiver 2025-Vergleich · Challenger-Wert aus Notebook 20",
                x_titel="WAPE (%) – niedriger ist besser", y_titel="",
            )
            ci.prozent_achse(fig, "x", 0)
            ci.gitter_x(fig)
            ci.zeigen(fig)

            challenger_evidence = pd.DataFrame([
                ["2024-CV-WAPE", f"{de(CHALLENGER_CV_WAPE, 2)} %", "nur Modellwahl 2024"],
                ["2025-WAPE", f"{de(CHALLENGER_WAPE, 2)} %", "retrospektiver Benchmark"],
                ["Relativer Abstand zur Hauptlösung", f"{de(challenger_gain * 100, 1)} %", "Potenzial, kein Freigabenachweis"],
                ["Zusatzgewinn reines Tuning", "ca. 0,08 Prozentpunkte", "klein"],
                ["Haupttreiber", "Plan-, Wartungs- und Historienfeatures", "Snapshot-Nachweis nötig"],
            ], columns=["Nachweis", "Wert", "Einordnung"])
            display(ci.tabellenansicht(challenger_evidence, 2))
            entscheidungsbox(
                f"Der Challenger erreicht rückblickend {de(CHALLENGER_WAPE, 2)} % WAPE – rund "
                f"{de(challenger_gain * 100, 1)} % weniger als die Hauptlösung.",
                "Er wird als nächster Kandidat im Schattenbetrieb geprüft, aber nicht nachträglich zum Hauptmodell erklärt.",
                "Bessere Prognose bedeutet nicht automatisch bessere Anomalieerkennung; dafür fehlen bestätigte Anomalielabels."
            )
            sprechtext(
                "Der Challenger zeigt, wohin sich das Projekt entwickeln kann. Sein Vorteil kommt "
                "vor allem aus zusätzlichen Planinformationen. Deshalb trenne ich Forschungswert "
                "und freigegebene Hauptlösung und fordere vor Einsatz einen prospektiven Schattenbetrieb."
            )
            ''',
        ),
        markdown(
            "story-challenger-warning",
            """
            <details><summary>Wenn nachgefragt wird: Warum nicht sofort das Modell mit 12,04 % nehmen?</summary>

            1. Der Wert wurde retrospektiv auf einem bereits bekannten Jahr ermittelt.
            2. Der Gewinn hängt stark von Plan- und Wartungsmerkmalen ab; ihre historischen
               Stichtagsstände müssen für einen realistischen Betrieb gesichert sein.
            3. Mehr Prognosegenauigkeit garantiert keine besseren Alerts. Ein komplexes Modell
               könnte eine echte betriebliche Veränderung teilweise „wegerklären“.
            4. Vor Freigabe braucht es Schattenbetrieb, Driftkontrolle und bestätigte Fälle.

            Deshalb ist 12,04 % ein fachlich interessanter Challenger-Wert – kein Versprechen.

            </details>
            """,
        ),
        code(
            "story-chapter-conclusion",
            '''
            ci.abschnitt(
                "07", "Fazit: erklärbarer Nutzen mit klaren Grenzen",
                "Prognose, Alertregel und menschliche Prüfung bilden gemeinsam die Lösung.",
                kontext="ENTSCHEIDUNG UND NÄCHSTE SCHRITTE",
            )
            ''',
        ),
        code(
            "story-final-scorecard",
            r'''
            scorecard = pd.DataFrame([
                ["Prognose", f"{de(champion_metrics['WAPE (%)'], 2)} % WAPE", "Random Forest auf Vollaststunden"],
                ["Baseline", f"{de(best_baseline['WAPE (%)'], 2)} % WAPE", str(best_baseline["Kandidat"])],
                ["Verbesserung", f"{de(improvement * 100, 1)} % relativ", f"{de(test_gap_pp, 2)} Prozentpunkte"],
                ["Prüfhinweise", f"{total_alerts} im Jahr 2025", f"{de(alerts_per_month, 1)} je Monat"],
                ["Schwelle", f"{de(ANOMALY_QUANTILE * 100, 0)}. Perzentil", f"Score {de(anomaly_threshold, 2)}"],
                ["Challenger", f"{de(CHALLENGER_WAPE, 2)} % WAPE", "Ausblick, keine Freigabe"],
            ], columns=["Baustein", "Ergebnis", "Bedeutung"])
            display(ci.tabellenansicht(scorecard, 2))
            display(HTML(
                ci.notebook_css()
                + '<section class="sww-report">'
                + '<p class="eyebrow">DREI ABSCHLUSSBOTSCHAFTEN</p>'
                + '<ol>'
                + '<li>Vollaststunden schaffen eine vergleichbarere Erwartung für unterschiedlich große Anschlüsse.</li>'
                + '<li>Der Random Forest schlägt die beste einfache Baseline im zeitlichen Vergleich.</li>'
                + '<li>Aus Residuen entsteht eine transparente, menschlich prüfbare Alertliste – keine automatische Diagnose.</li>'
                + '</ol></section>'
            ))
            ''',
        ),
        markdown(
            "story-limitations",
            """
            ### Was ich bewusst nicht überbehaupte

            - Es liegen nur zwei vollständige Jahreszyklen vor.
            - Die Schwelle basiert auf nur zwei Kalendermonaten.
            - Es gibt **keine gelabelten Anomalien**; Precision und Recall sind deshalb unbekannt.
            - 2025 war bereits Teil der EDA und ist kein vollständig unangesehener Blindtest.
            - Monatliche Daten erlauben keine Echtzeit-Störungserkennung.
            - Die zeitliche Trennung reduziert Leakage und klassisches Overfitting, schließt
              künftige Drift oder Testwissen aber nicht vollständig aus.

            **Saubere Aussage zu Overfitting:** Es gibt keinen deutlichen Hinweis auf klassisches
            Overfitting, weil der Random Forest über mehrere Zeitfolds und auch 2025 besser als die
            Baseline abschneidet. Wegen kurzer Historie und bekanntem Benchmark ist die Sicherheit
            dennoch begrenzt. Der nächste belastbare Nachweis ist ein prospektiver Schattenbetrieb.
            """,
        ),
        markdown(
            "story-faq",
            """
            ## Kritische Prüferfragen – kurze, sichere Antworten

            | Frage | Antwort |
            | --- | --- |
            | Warum kein fester kWh-Grenzwert? | Normal hängt von Anschlussgröße, Kundentyp, Monat und Historie ab. Das Modell erzeugt eine individuelle Referenz. |
            | Ist VLS eine echte Laufzeit? | Nein, hier ist es die rechnerische Normierung kWh geteilt durch kW. Die Ausgabe wird wieder in kWh umgerechnet. |
            | Was ist die Vormonats-Baseline? | Für den nächsten Monat wird genau der zuletzt bekannte Monatsverbrauch angenommen. |
            | Warum zusätzlich das Drei-Monats-Mittel? | Es glättet einzelne Monatsschwankungen und war die stärkste einfache Referenz. |
            | Warum Random Forest? | Er gewann den ausschließlich mit 2024 durchgeführten zeitlichen Vergleich und kann nichtlineare Zusammenhänge abbilden. |
            | Warum kein zufälliger Split? | Ein zufälliger Split vermischt Vergangenheit und Zukunft und überschätzt dadurch den realen Einsatz. |
            | Warum darf Juni den Mai-Verbrauch nutzen? | Es ist eine monatlich rollierende Ein-Monats-Prognose; bei der Juni-Prognose ist Mai bekannt. |
            | Was bedeutet WAPE? | Summe absoluter Fehler geteilt durch gesamte Ist-Energie; nicht Fehler jedes einzelnen Zählers und nicht „100 minus Genauigkeit“. |
            | Prozentpunkte oder Prozent? | Die direkte Differenz sind Prozentpunkte; geteilt durch den Baseline-Wert ergibt sie die relative Verbesserung. |
            | Ist 2025 ein echter Blindtest? | Nein, ein zeitlich späterer retrospektiver Benchmark. Deshalb folgt ein prospektiver Schattenbetrieb. |
            | Ist das Modell overfitted? | Kein klarer klassischer Hinweis, weil es Baselines in Zeitfolds und 2025 schlägt; kurze Historie und bekanntes 2025 begrenzen die Aussage. |
            | Was ist hier eine Anomalie? | Eine ungewöhnlich große, robust normierte Modellabweichung, die eine Prüfung auslöst – noch kein Defekt. |
            | Ist Score 6 eine Wahrscheinlichkeit? | Nein. Der Score ist weder Wahrscheinlichkeit noch klassische Anzahl von Standardabweichungen. |
            | Warum das 99. Perzentil? | Es ist eine dokumentierte Kapazitätsannahme für Sensitivität versus Prüfaufwand, nicht mathematisch optimal. |
            | Warum entstehen später nicht exakt 1 % Alerts? | Die Fehlerverteilung kann sich gegenüber den zwei Kalibrierungsmonaten verändern. |
            | Wie gut erkennt das System echte Störungen? | Ohne bestätigte Labels können Precision und Recall noch nicht seriös berechnet werden. |
            | Erkennt es Wartung? | Nein. Wartung ist Kontext für den Menschen, nicht automatisch erkannte Ursache. |
            | Warum nicht sofort der 12,04-%-Challenger? | Zusätzliche Planmerkmale benötigen Snapshot-Nachweis, Schattenbetrieb und eine eigene Alert-Evaluation. |
            | Macht eine bessere Prognose automatisch bessere Alerts? | Nein. Das muss gegen bestätigte Anomaliefälle geprüft werden. |
            """,
        ),
        code(
            "story-closing-script",
            r'''
            closing_text = f"""
            <section class="sww-report" style="border-left:5px solid {theme.ROLE['prognose']};">
              <p class="eyebrow">90-SEKUNDEN-SPRECHTEXT</p>
              <p><strong>„Ausgangspunkt unseres Projekts ist nicht nur die Frage, wie viel Energie
              im nächsten Monat verbraucht wird. Wir möchten erkennen, welcher Verbrauch so
              ungewöhnlich ist, dass sich eine Prüfung lohnt. Dafür erzeugen wir zunächst eine
              individuelle Erwartung für jeden der 700 Zähler.</strong></p>
              <p><strong>Weil sich die Anschlüsse stark unterscheiden, prognostizieren wir
              Vollaststunden – Verbrauch geteilt durch Vertragsleistung – und rechnen anschließend
              wieder in kWh zurück. Das Modell nutzt nur Informationen, die zum jeweiligen
              Prognosezeitpunkt vorliegen, und wird zeitlich vorwärts validiert.</strong></p>
              <p><strong>Unser Random Forest erreicht 2025 einen WAPE von
              {de(champion_metrics['WAPE (%)'], 2)} Prozent gegenüber
              {de(best_baseline['WAPE (%)'], 2)} Prozent der besten Baseline. Für die
              Anomalieerkennung betrachten wir danach nicht den Verbrauch allein, sondern seine
              robuste Abweichung von dieser Erwartung.</strong></p>
              <p><strong>Die separat auf Ende 2024 kalibrierte Schwelle erzeugt 2025
              {total_alerts} priorisierte Prüfhinweise, im Mittel {de(alerts_per_month, 1)} pro
              Monat. Das sind keine automatisch erkannten Defekte, sondern Fälle für eine
              menschliche Prüfung. Ein Challenger erreicht zwar {de(CHALLENGER_WAPE, 2)} Prozent,
              benötigt aber zusätzliche Planmerkmale und einen Praxistest. Deshalb bleibt der
              verständlichere Random Forest unsere belastbare Hauptlösung.“</strong></p>
            </section>
            """
            display(HTML(ci.notebook_css() + closing_text))
            ''',
        ),
        markdown(
            "story-next-step",
            """
            ### Anschlussprojekt: Dashboard für die Bearbeitung

            Das nächste sinnvolle Artefakt ist kein weiteres Ranking, sondern ein Arbeitsdashboard:

            1. KPI-Leiste für offene Hinweise, hohe/niedrige Richtung und Datenqualitätsfälle,
            2. priorisierte Alerttabelle mit Score, kWh-Auswirkung, Kundentyp und Kontext,
            3. Detailansicht mit Ist-/Prognoseverlauf und Schwellenbegründung,
            4. dokumentierbare Entscheidung: bestätigt, erklärt, Datenfehler oder unklar,
            5. Monitoring von Alertquote, Drift und Rückmeldungsqualität.

            Damit wird aus der Analyse ein kontrollierter Lernkreislauf – und aus späteren
            Rückmeldungen entsteht die Ground Truth für eine echte Anomalie-Evaluation.
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
                "builder": "scripts/build_modeling_story_notebook.py",
                "data_source": "data/raw/260916_verbrauch_bereinigt.csv",
                "source_sha256": data_hash,
                "design_source": "brand/design-system/tokens/design-tokens.json",
                "development_period": "01/2024–12/2024",
                "benchmark_period": "01/2025–12/2025",
                "test_period": "01/2025–12/2025",
                "forecast_horizon": "1 Monat",
                "random_state": 42,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
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
