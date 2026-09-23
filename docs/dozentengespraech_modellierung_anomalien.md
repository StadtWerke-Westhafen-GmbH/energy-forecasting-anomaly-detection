# Auswertung des Dozentengesprächs: Modellierung und Anomalie-Dashboard

## Die Kernaussage in einem Satz

Die fehlerhafte Ursprungsspalte für das Drei-Monats-Mittel wird nicht übernommen,
sondern je Zähler aus ausschließlich vergangenen gültigen Werten neu berechnet; das
Modell prognostiziert Vollaststunden, wird zeitlich geprüft und übersetzt den späteren
Prognosefehler über eine vor 2025 festgelegte Schwelle in einen menschlich zu prüfenden
Hinweis.

## 1. Was Anuar zur CSV tatsächlich gesagt hat

| Zeitpunkt | Aussage | Konsequenz |
|---|---|---|
| ca. 31:10 | Die vorhandene Drei-Monats-Spalte wegwerfen und selbst berechnen. | Die gelieferte Lag-Spalte ist keine verlässliche Modellgrundlage. |
| ca. 31:37 | Patrick weist darauf hin, dass Januar und Februar sonst leer wären. | Das ist ein Cold-Start-Problem, kein Grund, Zählergrenzen zu vermischen. |
| ca. 31:53 | Am Anfang die jeweils verfügbaren Vormonate verwenden; den ersten Fall interpolieren oder weglassen. | Februar kann Januar nutzen, März Januar und Februar, danach bis zu drei Vormonate. Im Transkript ist einmal „April“ statt logisch „März“ zu hören. |
| ca. 32:39–38:00 | Als mathematisch aufwendige Option den 2024-Verlauf visualisieren und je Zähler eine Kurve zurückschätzen. | Polynom oder Sinus waren ein möglicher Ausblick, keine verbindliche Vorgabe. |
| ca. 35:47 | 2025 darf dafür nicht verwendet werden. | Sonst entsteht Data Leakage. |
| ca. 38:33 | Wegen der Deadline wäre auch Weglassen vertretbar. | Für die IHK zählt eine saubere, verstandene Entscheidung mehr als maximale mathematische Komplexität. |

Der feste gemeinsame Nenner des Gesprächs lautet daher:

1. Die fehlerhafte Originalspalte nicht verwenden.
2. Historie chronologisch und getrennt je `zaehler_id` neu berechnen.
3. Niemals Informationen aus 2025 zur Konstruktion von 2024-Merkmalen benutzen.
4. Keine 1.500 oder mehr Zeilen nur wegen fehlender Anfangshistorie löschen.

## 2. Unsere umgesetzte Entscheidung

Patricks Datei `data/processed/modellierung_basis.csv` bleibt unverändert. Das Skript
`scripts/build_modeling_basis_available_history.py` erzeugt daraus die versionierte Datei
`data/processed/modellierung_basis_bis_3_monate.csv`.

Die Regel lautet je Zähler:

- Januar 2024: keine Vergangenheit, deshalb `NaN`;
- Februar: Januar;
- März: Mittelwert aus Januar und Februar;
- ab April: Mittel aus bis zu drei gültigen Vormonaten;
- als `unmoeglich` markierte Messwerte werden nicht in spätere Historie getragen.

Damit werden 1.453 zuvor fehlende Historienwerte nutzbar. Exakt 700 Fehlwerte bleiben –
der echte erste Monat der 700 Zähler. Keine Zeile wird gelöscht. Fehlende Modellwerte
werden erst innerhalb des jeweiligen Trainingsfolds behandelt; dadurch lernt der Imputer
keine Statistik aus späteren Monaten.

Warum keine Polynom-Rückschätzung in der Hauptlösung? Eine solche Rückwärtsextrapolation
würde spätere Zielwerte aus 2024 in Merkmale früherer 2024-Zeitpunkte einbauen. Das wäre in
der vorwärts laufenden Validierung schwer sauber zu kapseln und für die Prüfung unnötig
kompliziert. Sie eignet sich höchstens als klar getrennte Sensitivitätsanalyse.

## 3. Was Anuar zum Notebook positiv bewertet hat

- ca. 42:50: Die Zeitachse mit Lernen, Bewerten, Kalibrieren und Testen ist gut
  präsentierbar.
- ca. 43:18: Das Historienmittel ist eine sinnvolle Baseline.
- ca. 45:36: Der Vergleich zwischen direktem kWh-Lernen und Vollaststunden ist
  interessant.
- ca. 46:12: Für die IHK ist entscheidend, dass Daten, Entscheidungen und Grenzen
  verstanden werden; nicht, dass mathematisch das letzte Promille erreicht wird.
- ca. 47:28: Der Ist-gegen-Prognose-Plot ist im Kern „die Lösung der Aufgabe“.

## 4. Die Stelle mit den Whiskern – die sichere Antwort

Bei ca. 44:15 fragte Anuar nach den Fehlerbalken.

> Jeder Balken zeigt den mittleren RMSE aus drei zeitlich vorwärts laufenden
> Prüfzeiträumen im Jahr 2024. Der Whisker ist die Standardabweichung dieser drei
> Fold-Ergebnisse. Ein langer Whisker bedeutet, dass die Modellgüte zeitlich stärker
> schwankt. Er ist kein Konfidenzintervall und keine Unsicherheit eines einzelnen
> Prognosewertes.

## 5. Modellentscheidung und aktuelle Ergebnisse

Die Auswahl wird ausschließlich mit den drei zeitlichen Prüfungen aus 2024 getroffen.
Der Random Forest hat dort den kleinsten mittleren RMSE.

| Vergleich 2024 | RMSE |
|---|---:|
| Random Forest auf VLS | 13.272 kWh |
| Lineare Regression auf VLS | 13.643 kWh |
| beste einfache Regel | 15.483 kWh |

Der Random Forest verbessert die lineare Referenz um 2,7 %. Das ist kein riesiger Abstand,
aber in allen Entscheidungsregeln zählt dieselbe vorab festgelegte Hauptmetrik. Die lineare
Regression bleibt die verständliche Referenz und ein vertretbarer Fallback.

Im retrospektiven Jahr 2025 erreicht der gewählte Random Forest:

- RMSE: 9.188 kWh;
- MAE: 3.725 kWh;
- R²: 0,901;
- 15,9 % geringeren RMSE als die beste einfache Baseline;
- 6,2 % geringeren RMSE als ein vergleichbarer Random Forest, der direkt kWh lernt.

Der VLS-Vergleich ist ein isoliertes Methodenexperiment. Das finale Modell lernt VLS und
rechnet jede Ausgabe anschließend exakt über `VLS × Vertragsleistung` in kWh zurück.

## 6. So wird aus einer Prognose ein Anomaliehinweis

1. Das Modell prognostiziert den erwarteten Monatswert.
2. Nach Monatsende trifft der Istwert ein.
3. Das Residuum wird berechnet: `Ist-VLS − Prognose-VLS`.
4. Der Betrag wird mit einer zuvor kalibrierten Schwelle verglichen.
5. Erst bei Überschreitung entsteht ein Prüfhinweis.
6. Ein Mensch prüft Messwert, Datenqualität, Produktionsplan, Wartung und möglichen
   Handlungsbedarf.

Die Schwelle stammt nur aus 1.397 rollierend prognostizierten Fällen aus November und
Dezember 2024. Das ist eine transparente Pilotannahme, aber wegen des kurzen,
winterlastigen Zeitraums keine fertige Produktionsregel.

| Perzentil | VLS-Schwelle | Hinweise 2025 | Hinweise/Monat |
|---:|---:|---:|---:|
| 95,0 % | 68,0 h | 400 | 33,3 |
| 97,5 % | 82,4 h | 256 | 21,3 |
| 99,0 % | 144,4 h | 114 | 9,5 |
| 99,5 % | 196,3 h | 69 | 5,8 |

Die Mitte der Demo ist das 99. Perzentil: 114 Hinweise auf 107 Zählern, davon 68 ungewöhnlich
hoch und 46 ungewöhnlich niedrig.

## 7. Was der Regler bedeutet – und was nicht

Bei ca. 49:41–54:09 diskutiert ihr den betrieblichen Zielkonflikt und die interaktive
Darstellung.

- Niedriges Perzentil: niedrigere Grenze, mehr Hinweise, höherer Prüfaufwand und geringeres
  Risiko, einen auffälligen Fall zu übersehen.
- Hohes Perzentil: höhere Grenze, weniger Hinweise, geringerer Prüfaufwand und höheres
  Risiko, relevante Fälle nicht vorzulegen.

Der Regler trainiert das Modell nicht neu. Er wählt nur eine von vier dokumentierten
Entscheidungsgrenzen und aktualisiert gemeinsam:

- die Anzahl der Hinweise;
- die betroffenen Zähler;
- die farbigen Punkte im Ist-Prognose-Plot;
- Monats- und Kundentypverteilung;
- die Prüfwarteschlange und den CSV-Export;
- den Schwellenfaktor im Detailfall.

Ohne bestätigte Defektlabels kann der Regler keinen objektiv optimalen „Sweet Spot“ finden.
Er macht den Zusammenhang zwischen Arbeitslast und Sensitivität verhandelbar. Precision und
Recall werden erst nach fachlicher Rückmeldung seriös berechenbar.

## 8. Warum wir den vorgeschlagenen „Winkel“ nicht wörtlich zeichnen

Unsere Regel lautet:

`|Ist − Prognose| / Vertragsleistung ≥ VLS-Schwelle`

Im gemeinsamen kWh-Plot besitzt deshalb jeder Zähler wegen seiner Vertragsleistung einen
anderen erlaubten Abstand zur Diagonalen. Eine einzige verstellbare Linie mit bestimmter
Steigung wäre dagegen eine andere Regel wie `Ist / Prognose`. Das Dashboard zeigt daher
die perfekte Diagonale und färbt die Punkte live korrekt nach der VLS-Regel. Es vermischt
nicht unbemerkt zwei verschiedene Anomaliedefinitionen.

## 9. Plausibilisierung ohne echte Anomalielabel

Die EDA-Spalte `anomalie` ist eine Quotenregel und keine Ground Truth. Beim 99-%-Szenario:

- 68 Fälle werden von EDA-Regel und Modell markiert;
- 46 Fälle findet nur das Modell;
- 603 Fälle markiert nur die EDA-Regel;
- alle 10 belegten unmöglichen Testwerte werden vom Modellhinweis erfasst.

Die zehn Treffer sind ein wichtiger Sanity Check. Sie beweisen aber noch keine allgemeine
Erkennungsqualität. Genau deshalb bleibt die Formulierung „Prüfhinweis“ und nicht
„erkannter Defekt“.

## 10. Kurzer Ablauf für die Live-Demo

1. Mit dem 99. Perzentil starten: „Das ist unsere dokumentierte Pilotannahme – 114 Fälle,
   rund 9,5 pro Monat.“
2. Auf 95 % schieben: „Die Grenze sinkt; Plot, KPIs und Warteschlange steigen gemeinsam auf
   400 Fälle.“
3. Auf 99,5 % schieben: „Jetzt priorisieren wir nur 69 besonders starke Abweichungen.“
4. Auf 99 % zurückgehen und einen roten Punkt beziehungsweise den ersten Tabellenfall öffnen.
5. Im Detailfall zeigen: Ist, Prognose, VLS-Residuum, Schwellenfaktor, DQ-/Wartungskontext.
6. Mit der menschlichen Bewertung enden: „Erst diese Rückmeldung erzeugt später echte Labels
   für Precision, Recall und eine belastbare Schwellenoptimierung.“

## 11. Sechs kurze Antworten fürs Fachgespräch

**Warum Vollaststunden?**  
Damit unterschiedlich große Anschlüsse auf einer vergleichbareren Skala gelernt werden;
für Nutzer und Bewertung wird wieder in kWh zurückgerechnet.

**Warum Random Forest?**  
Er hat im zeitlichen 2024-Vergleich den niedrigsten mittleren RMSE. Die lineare Regression
bleibt die verständliche Referenz; der Vorsprung von 2,7 % wird nicht größer dargestellt,
als er ist.

**Ist das Overfitting?**  
Es gibt kein klares Signal dafür: begrenzte Baumtiefe, drei vorwärts laufende Prüfungen und
weiterhin bessere Werte 2025. Ausschließen lässt es sich mit einem bereits bekannten
retrospektiven Test nicht; dafür braucht es einen prospektiven Pilot.

**Was ist eine Anomalie?**  
Aktuell nur ein ungewöhnlich großer Prognosefehler relativ zur Anschlussleistung. Ein
Hinweis ist noch kein Defekt und löst keine automatische Maßnahme aus.

**Warum das 99. Perzentil?**  
Als dokumentierte Pilotannahme mit beherrschbarem Volumen. Die endgültige Schwelle muss der
Fachbereich später mit Prüfkosten und bestätigten Fällen festlegen.

**Warum keine Precision und Recall?**  
Weil keine verlässlich bestätigten Anomalielabel vorliegen. Fallzahlen und bekannte
Plausibilitätsfehler kann man prüfen; Erkennungsquote und Fehlalarmquote noch nicht.
