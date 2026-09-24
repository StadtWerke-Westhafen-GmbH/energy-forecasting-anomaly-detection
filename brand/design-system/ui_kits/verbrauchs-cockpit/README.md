# Verbrauchs-Cockpit

Dashboard als Actionplan: Jede Ansicht beantwortet eine Frage und führt zur nächsten Handlung.

| Ansicht | Für wen | Frage | Inhalt |
|---|---|---|---|
| **Verbrauchsprognose** | Energiebeschaffung | Wie viel Strom muss für den kommenden Monat beschafft werden? | *Monatsansicht* (Start): Beschaffungsmenge mit Spanne, Verlauf 2024 bis Zielmonat, Beschaffungsplan je Branche gegen Vormonat und Vorjahr, Treffsicherheit der letzten Prognosen. *Jahresübersicht*: Prognose und Ist über das Testjahr. |
| **Prüfhinweise** | Netzmanagement | Welche Zähler sollten nach Monatsabschluss geprüft werden? | *Monatsansicht* (Start): Prüfliste des Monats nach Dringlichkeit, Hinweise im Zeitverlauf. *Jahresübersicht*: gruppiert nach Monat, Kunde oder Branche (= `kundentyp`). |
| **Prüffall** | Netzmanagement | Warum ist der Fall auffällig, und was ist zu tun? | Verbrauch mit erwartetem Korridor, Abweichung je Monat gegen die Toleranz des Anschlusses, Einordnung gegen alle Zähler im Monat, regelbasierte Prüfempfehlung und Kontext (Wartung, Produktionsplan, Plausibilität der Vertragsleistung). |

Start: `node scripts/preview.mjs` vom Repository-Stamm, dann
`http://127.0.0.1:4173/design-system/ui_kits/verbrauchs-cockpit/index.html` (`?screen=prognose|anomalien|prueffall`).
Auf macOS geht es auch per Doppelklick auf `Cockpit starten.command` im Repository-Stamm.

## Neue Modellversion einspielen

1. Notebook `notebooks/12_modeling_ihk_lernstory.ipynb` vollständig ausführen. Die Exportzelle
   (`ihk-dashboard-export`) schreibt `forecast-data.js` und `forecast-data.json` in diesen Ordner.
2. Browser neu laden. Am Frontend ist keine Änderung nötig.

Ein anderes Notebook kann dieselben Dateien erzeugen: Es muss nur `build_payload(...)` und
`write_payload(...)` aus `energy_analytics.dashboard_export` mit den unten genannten Spalten aufrufen.
Nur nach Änderungen an `*.jsx` ist `npm run build` nötig.

## Datenvertrag (`schema_version: 1`)

`build_payload(benchmark, calibration_residuals, metrics, threshold, *, history, importance, sensitivity, final_name, threshold_quantile, meta)`

- **benchmark** (Pflicht): eine Zeile je Zähler und Monat im Testjahr mit
  `zaehler_id, kunde_id, kundentyp, monat, vertragsleistung_kw, verbrauch_kwh, prognose_kwh,
  residuum_kwh, residuum_vls, anomalie_score, anomalie, richtung`.
  Optional sind `rolling_3_kwh` (Baseline-Linie), `wartung_aktiv` und `produktionsplan_index`.
- **calibration_residuals** (Pflicht): die Residuen, aus denen die Schwelle kalibriert wurde (Nachweis der Schwelle).
- **metrics** (Pflicht): `Kandidat, Typ, RMSE (kWh), MAE (kWh), R²`, optional `CV-RMSE (kWh)`.
- **threshold** (Pflicht): Schwellwert in `threshold_unit` (Standard `VLS-h`).
- **history** (optional): Istwerte vor dem Testjahr (`zaehler_id, monat, verbrauch_kwh`) für den Zählerverlauf.
- **importance** (optional): `Featuregruppe, RMSE-Anstieg (kWh)`.
- **sensitivity** (optional): `Perzentil, Schwelle (VLS-h), Hinweise 2025, Hinweise je Monat`.

Fehlt ein optionaler Block, bleibt die zugehörige Angabe leer. Fehlt eine Pflichtspalte, bricht
der Export mit einer Meldung ab, die die fehlenden Spalten nennt. Das Frontend filtert, gruppiert und summiert nur.
Der Block `residuals` (QQ, Dezile, Monatsband) wird weiterhin exportiert. Er ist für Bericht und
Präsentation gedacht und wird im Cockpit bewusst nicht gezeigt.

## Dateien

- `lib.jsx`: Formatierung, Umwandlung der spaltenweisen Daten in Zeilen, Aggregation
- `VcShell.jsx`: Navigation (Beschaffung, Netzmanagement)
- `PrognoseScreen.jsx`, `AnomalienScreen.jsx`, `PrueffallScreen.jsx`
- `forecast-data.js/.json`: generiert, nicht manuell ändern

Das Kit nutzt die Komponenten aus `dist/js/components.js` und den Plotly-Wrapper aus
`ui_kits/energie-cockpit/Chart.jsx`.
