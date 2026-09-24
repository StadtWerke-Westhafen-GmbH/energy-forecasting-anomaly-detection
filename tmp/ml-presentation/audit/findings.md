# Inhalts- und Faktenprüfung der Modellierungspräsentation

## Verlässliche lokale Quellen

- Aktuelles Deck: `docs/presentation/Modellierung_Anomaliepruefung_IHK.pptx`, 18 Folien, 13 Kernfolien und 5 Backups, keine nativen Charts, 30 Medien.
- Aktuelle berechnete Ergebnisse: `notebooks/13_modellierung_von_grund_auf_verstehen.ipynb` und `brand/design-system/ui_kits/energie-cockpit/anomaly-data.js`.
- Methodenimplementierung: `scripts/build_modeling_verstehen_notebook.py`, `scripts/build_anomaly_dashboard_data.py`.
- Unrunde Kalibrierungsdaten: `data/processed/kalibrierungsfehler_vls_sortiert.csv`, `data/processed/kalibrierungsfehler_vls_perzentile.json`.
- Die SHA-256 der aktuellen Modellierungsbasis stimmt mit der Dashboard-Metadatei überein.
- `README_modellierung_basis.md` beschreibt teils einen älteren Stand: n=8.390/8.400, starres Drei-Monats-Fenster, HistGradientBoosting-Beispiel. Für die neue Präsentation aktuelle Notebook-Ergebnisse verwenden.

## Alle Folien und ihre zu erhaltenden Inhalte

| Nr. | Inhalt | Zentrale Zahlen/Aussagen |
|---|---|---|
| 1 | Titel | Folgemonatsprognose, q99-Prüfhinweise, menschliche Entscheidung |
| 2 | Prüfprozess | Prognose vor Monatsbeginn, Ist nach Monatsende, Residuum, Fachprüfung |
| 3 | Zielvariable VLS | 10.000 kWh / 50 kW = 200 h, 40.000 / 200 = 200 h, Rückrechnung über Vertragsleistung |
| 4 | Zeitliche Validierung | 3 Folds 2024; Jan–Apr zu Mai–Jun, Jan–Jun zu Jul–Aug, Jan–Aug zu Sep–Okt; Nov–Dez Kalibrierung; 2025 Benchmark |
| 5 | Modellwahl | Linear/RF; Tiefe 8/unbegrenzt, Blatt 5/20, Merkmale 0,7/1,0; 8 × 3 = 24 Fits; Auswahl nach CV-RMSE |
| 6 | CV-Ergebnis | RF 13.272, Linear 13.643, Bis-zu-3-Monats-Mittel 15.483, Vormonat 18.460 kWh; RF 2,7 % besser als linear |
| 7 | Retrospektiver Benchmark | RF RMSE 9.188, MAE 3.725 kWh; Linear 9.414, Historienmittel 10.922, Vormonat 12.386; 15,9 % besser; n=8.398 außer Vormonat n=8.388 |
| 8 | Gruppierte Permutation | RMSE-Anstieg: Historie 7.349, Produktion 717, Wartung 578, Kalender 232, Wetter 193, Jahreszeit 115, Kundentyp 5 kWh |
| 9 | Kalibrierung | n=1.397; q99=144,354704864 h; 1.383 Fehler bis Schwelle, 14 darüber; Index 1.382,04; Interpolation Rang 1.383/1.384 |
| 10 | q99-Pilotvolumen | 114 / 8.398 = 1,36 %, 9,5 Hinweise/Monat, 107 Zähler; Grenze unverändert aus 2024 |
| 11 | Konkreter Fall | ZL-00147, 49 kW, q99 entspricht 7.073,4 kWh; August Ist 23.563,5, Prognose 7.303,9, Residuum +16.259,6 kWh = +331,8 h, Faktor +2,30; September Faktor −0,68 |
| 12 | Live-Demo | 2 Minuten, q99/Umfang, zwei hohe/zwei niedrige Fälle, Fall öffnen, Kontext, Bewertung dokumentieren, Label |
| 13 | Fazit | 15,9 % RMSE-Vorteil, 9,5 Fälle/Monat, bestätigte Labels fehlen; spätere Klassifikation ist Ausblick |
| 14 | RMSE/MAE | Didaktik: A=[10,10,10,10], B=[0,0,0,40] kWh; MAE beide 10; RMSE A=10/B=20; kein Projektmodell-Ergebnis |
| 15 | VLS vs direkte kWh | Gleicher Modelltyp, eigene identische zeitliche Tuninglogik; 9.799,909 vs 9.188,397 kWh, 6,2 % Vorteil im konkreten Versuch |
| 16 | Sensitivität | q95=68,0 h/400/33,3 pro Monat; q97,5=82,4 h/256/21,3; q99=144,4 h/114/9,5; q99,5=196,3 h/69/5,8 |
| 17 | Fold-Details und RF | Exakt RF-Folds 17.537,588 / 8.223,484 / 14.056,150 kWh; Mittel 13.272,407; SD(pop) 3.842,640; Tiefe 8, Blatt 5, Feature-Anteil 0,7, 300 Bäume, seed 42 |
| 18 | Begriffsklärung | Ausreißer, Modellabweichung, Prüfhinweis, fachlich bestätigte Anomalie; Precision/Recall erst mit Labels inklusive Prüfung von Nicht-Hinweisen |

## Zwei konkrete Korrekturen

1. Alte Folie 17 nennt Fold 2 fälschlich **8.224** kWh. Notebook-Array: 8.223,484, daher gerundet **8.223** kWh.
2. Alte Folie 6 nennt einen „konsistenten Sieg“. RF gewinnt den Mittelwert und Fold 1/2, liegt jedoch in Fold 3 mit 14.056 schlechter als linear mit 13.763. Besser: „2,7 % geringerer mittlerer Validierungsfehler“. Kein statistisch gesicherter Vorteil behaupten.

## Fachliche Einschränkungen für sichtbare Hinweise oder Notizen

- Ergebnisse 2025 sind retrospektiv. Kein unberührter Blindtest und kein Nachweis einer produktiven Einbindung.
- Das finale Modell trainiert auf 8.389 bereinigten Fällen aus 2024. 2025 nutzt den fest trainierten Prädiktor mit den jeweils schon eingetroffenen Vormonatswerten. Es ist eine Folge einzelner Monatsprognosen, keine am 1. Januar erzeugte Jahresprognose.
- Die Entwicklung schließt einen rekonstruierten Zielwert zusätzlich aus, der Benchmark zwei. Daher n=8.389/8.398, trotz ursprünglicher Splitzählung 8.390/8.400.
- Das Historienmittel heißt fachlich „Mittel aus bis zu drei Vormonaten“. Nur im ersten Monat fehlen alle Historienwerte. Imputation erfolgt ausschließlich im jeweiligen Trainingsfold.
- Vertragsleistung ist bei der VLS-Methode Umrechnungsfaktor und kein Prädiktor. VLS sind normierter Verbrauch, keine tatsächlich gemessene Laufzeit.
- Heizgradtage sind als Merkmal nur zulässig, wenn ein zum Prognosezeitpunkt verfügbarer Prognosewert vorliegt. Wartung und Produktionsplan müssen entsprechend vorab bekannt sein. Die Slides sollten diese Verfügbarkeit nicht als produktiv geprüft darstellen.
- Whisker = Populationsstandardabweichung der drei Fold-RMSE (ddof=0). Weder Konfidenzintervall noch Unsicherheit einer einzelnen Prognose.
- Permutation Importance quantifiziert die Modellabhängigkeit von einer Informationsgruppe. Sie beweist keine Kausalität. Die Auswertung nutzt bekannte Daten aus 2025.
- Kalibrierung nur November/Dezember: kurze, winterlastige Basis. q99 ist Pilotannahme und keine optimale Produktionsregel.
- q99=99. Perzentil bezeichnet eine Position in der Kalibrierungsfehlerverteilung. Weder 99 % Defektwahrscheinlichkeit noch eine garantierte 1-%-Hinweisquote im nächsten Jahr.
- Regel: Betrag des VLS-Residuums **größer oder gleich** der Schwelle. Die vorhandenen Fälle liegen nicht exakt auf der Grenze, daher beeinflusst diese Präzisierung keine Fallzahl.
- In einem VLS-Plot ist ein gemeinsames paralleles Band von ±144,3547 h korrekt. In einem gemeinsamen kWh-Plot ist die erlaubte Abweichung je Zähler verschieden. Eine einzige kWh-Grenze oder veränderte Steigung wäre eine andere Regel.
- Im Fallbeispiel ist der Faktor bewusst vorzeichenbehaftet. Dashboard-Scores verwenden den Betrag. Nicht versehentlich die positive September-Dashboardzahl +0,6821 als vorzeichenbehafteten Faktor bezeichnen.
- EDA-Anomaliemarkierungen sind eine Referenzregel ohne Ground Truth. 10/10 unmögliche Testwerte erfasst ist ein Plausibilitätstest, kein Nachweis allgemeiner Precision/Recall.
- 114 Hinweise bestehen aus 68 hohen und 46 niedrigen Abweichungen. Keine bestätigten Defekte, keine automatischen Maßnahmen.
- Zusätzliche Labels nur für bereits markierte Fälle reichen zur Recall-Schätzung nicht. Auch Nicht-Hinweise müssen stichprobenartig fachlich geprüft werden.

## Daten für editierbare neue Charts

- `native_chart_data.json`: CV-Mittel/SD/Folds, Benchmark mit Fallzahlen, Importance, Monatszahlen, Perzentile, Normalisierungsbeispiel, Metrikbeispiel, ZL-00147-Zeitreihe samt signierten Faktoren, vollständige q99-Kurve und VLS-Scatter.
- `chart_data.json`: 11 originale Plotly-Spezifikationen mit bereits decodierten Zahlenlisten.
- `fact_summary.json`: Meta, Schwellenoptionen, Summen, Monate, Kundentypen, ZL-00147.
- `anomaly_data.json`: vollständiger bestehender Dashboard-Datensatz.
- `../source_content.json`: komplette Folientexte und Notizen, Medienverknüpfungen und Original-Chartinventar.

Für die neue Zeitleiste volle Monatsblöcke zeichnen: Der ursprüngliche Plotly-Plot beendet Trainingsbalken am Monatsanfang des letzten enthaltenen Trainingsmonats und wirkt dadurch um einen Monat kürzer. Die Modelllogik schließt April/Juni/August jeweils vollständig als Beobachtungsmonat ein.
