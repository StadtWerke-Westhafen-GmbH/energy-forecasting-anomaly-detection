# Der Machine Learning Canvas

> 📌 **NordWind-Beispiel**
> 
> Lara Hoffmann, Marketing-Leiterin der NordWind Shop GmbH, fragt vor dem Projektstart: _„Wenn wir Daten haben, wenn wir ein Modell bauen, wenn das alles laufen soll — was genau machen wir da eigentlich, und wie passt das zusammen?"_

Diese Frage beantwortet der **Machine Learning Canvas**: eine einseitige Übersicht aus zehn Feldern, die das Datenprojekt aus Geschäftssicht strukturiert.

Der Canvas ist **kein technisches Artefakt** und **keine Modellspezifikation**. Er ist ein Denkwerkzeug. Im IHK-Bericht zeigt er, dass Sie das Projekt als Ganzes verstanden haben — von der Geschäftsfrage bis zur Wartung.

Nach dieser Lektion können Sie:

-   alle 10 Felder des ML Canvas mit ihrer Bedeutung und der dazu gestellten Frage benennen,

-   die Kohärenz zwischen Prediction, Learning Approach und Evaluation überprüfen — und Inkohärenzen in fremden Canvases erkennen.

💭 **Verwandte Vorlage** — `ML_Canvas_Vorlage.docx` enthält die Canvas-Vorlage und auf Seite 2 das vollständig ausgefüllte NordWind-Beispiel. Nutzen Sie die Vorlage direkt für Ihre Gruppe.

| Kennzahl | Wert |
| --- | --- |
| Punkte | 10 von 70 |
| Zielumfang | ca. 1–2 Seiten Fließtext + ein Bild des Canvas |
| Pflicht | Alle 10 Felder, kohärent und vollständig |

Bewertet wird: **Vollständigkeit**, **Kohärenz** (passen die Felder zusammen?) und **Geschäftsbezug** (sprechen Sie über Mehrwert in EUR / Kunden / Stunden — oder nur über Modelltypen?).

![Die 10 Felder des ML Canvas mit Kohärenz-Achse](https://www.notion.so/image/attachment%3Addcfbab1-3186-4aae-8b95-198109c91ff7%3AL07_ml_canvas_raster.svg?table=block&id=b42f48ba-09d8-498a-b8f1-cf76cd3ebc1f&cache=v2)

Die 10 Felder des ML Canvas mit Kohärenz-Achse

_Die 10 Felder des ML Canvas mit Kohärenz-Achse_

Der Canvas hat zehn Felder, die in fünf Paare gruppiert sind. Bilinguale Bezeichnungen, weil die Prüfungskommission beide kennt:

| # | Englisch / Deutsch | Frage |
| --- | --- | --- |
| 1 | Value Proposition / Mehrwert | Welchen Geschäftsnutzen bringt das Projekt? |
| 2 | Data Sources / Datenquellen | Welche Daten stehen aus welchen Systemen zur Verfügung? |
| 3 | Prediction / Vorhersage | Was soll vorhergesagt werden? Klassifikation, Regression oder Anomalie-Erkennung? |
| 4 | Features / Merkmale | Welche Variablen tragen das Signal? |
| 5 | Learning Approach / Lernansatz | Welcher Modelltyp ist geeignet? |
| 6 | Evaluation / Überprüfung | Welche Metriken passen zur Aufgabe? |
| 7 | Decision / Entscheidung | Was passiert mit der Vorhersage? |
| 8 | Impact / Auswirkung | Welcher messbare Geschäftsnutzen entsteht? |
| 9 | Prediction Timing / Vorhersagezeitpunkt | Wann wird vorhergesagt? |
| 10 | Monitoring & Maintenance / Wartung | Wie wird das Modell langfristig betrieben? |

-   Wenn `Prediction` = „Klassifikation, churn ja/nein", dann darf `Evaluation` nicht „RMSE" sein, sondern muss eine Klassifikationsmetrik nennen (Recall, ROC-AUC, F1).

-   Wenn `Value Proposition` quantifiziert ist („Kosten senken"), muss `Impact` in derselben Einheit zurückgekehrt werden („EUR/Jahr").

-   Wenn `Decision` einen Schwellwert nennt („> 70 %"), muss `Prediction Timing` klar machen, wann diese Entscheidung getroffen wird.

-   Wenn `Data Sources` keine Echtzeit-Quellen kennt, kann `Prediction Timing` nicht „in Echtzeit" sein.

Die häufigste Punkteverlust-Quelle in Kapitel 2 ist genau diese Inkohärenz.

> 📌 **Beispiel-Canvas für die NordWind Shop GmbH**
> 
> Bevor wir die Tabelle zeigen, der Kontext in drei Sätzen: Die NordWind Shop GmbH verliert in den letzten vier Quartalen still Kund:innen aus ihrem Abo-Geschäft — die monatliche Kündigungsrate ist von 4 % auf 8 % gestiegen. Marketing-Leiterin Lara Hoffmann wünscht sich eine wöchentliche, priorisierte Risikoliste, mit der ihr Team und Tobias Berg aus dem Customer Success Retention-Kampagnen früher und gezielter einleiten können. Aus dieser Geschäftsfrage entsteht der folgende ML Canvas — Sie sehen, wie jedes Feld direkt an die geschäftliche Ausgangslage anknüpft.

| Feld | Inhalt |
| --- | --- |
| 1. Value Proposition / Mehrwert | Marketing erkennt abwanderungsgefährdete Kund:innen frühzeitig und kann gezielt Retention-Kampagnen einleiten, bevor diese Kund:innen tatsächlich kündigen. Geschäftsnutzen: messbare Reduktion der monatlichen Churn-Rate. |
| 2. Data Sources / Datenquellen | Kundenstammdaten (Shopify-Export), Bestell- und Abo-Historie aus dem internen Bestellsystem, Support-Tickets aus dem Helpdesk-Tool, Produktkatalog mit Kategorien — alles intern verfügbar, kein externer Datenkauf nötig. |
| 3. Prediction / Vorhersage | Binäre Klassifikation pro aktiver Abo-Kund:in: Wird diese Kund:in in den nächsten 30 Tagen keine Bestellung mehr aufgeben (Churn = 1) — ja/nein? Ausgabe pro Kund:in: Wahrscheinlichkeit zwischen 0 und 1. |
| 4. Features / Merkmale | Bestellfrequenz (letzte 90 Tage), Umsatz (letzte 30 Tage), Anzahl Support-Tickets (letzte 60 Tage), Nutzungsdauer der Plattform in Monaten, durchschnittliche Bestellgröße, Tage seit letzter Aktivität, Produktkategorie-Diversität. Bewusst weggelassen: demografische Merkmale, da nicht verlässlich erhoben. |
| 5. Learning Approach / Lernansatz | Überwachtes Lernen, binäre Klassifikation. Erste Wahl: logistische Regression (erklärbar, Koeffizienten direkt interpretierbar, im Fachgespräch leicht zu verteidigen). Vergleich: Random Forest mit `class_weight='balanced'`. |
| 6. Evaluation / Überprüfung | Recall auf der Churn-Klasse ist die Geschäfts-KPI (möglichst viele tatsächliche Kündigungen frühzeitig erkennen). ROC-AUC für das schwellwert-unabhängige Ranking. Accuracy ist hier irreführend, da Churn mit rund 8 % unterrepräsentiert ist. |
| 7. Decision / Entscheidung | Score > 70 % → Kund:in erhält automatisch eine personalisierte Retention-E-Mail mit Angebot. Score > 85 % → zusätzlich persönlicher Anruf durch das Customer-Success-Team von Tobias Berg innerhalb von 48 Stunden. |
| 8. Impact / Auswirkung | Geschätzte Reduktion der monatlichen Kündigungsquote um zwei Prozentpunkte (von 8 % auf 6 %). Bei rund 30 000 aktiven Abonnent:innen und einem durchschnittlichen Customer-Lifetime-Value von 120 EUR pro Vertrag ergibt das einen jährlich erhaltenen Umsatz von rund 190 000 EUR. |
| 9. Prediction Timing / Vorhersagezeitpunkt | Wöchentlicher Batch jeden Montagmorgen um 06:00 Uhr. Die priorisierte Liste der gefährdeten Kund:innen wird direkt in das Marketing-CRM eingespielt. Keine Echtzeit-Vorhersage nötig — die Geschäftsentscheidungen folgen einer wöchentlichen Kadenz. |
| 10. Monitoring & Maintenance / Wartung | Modell-Retraining alle drei Monate auf den jüngsten 18 Monaten Daten. Monatliches Drift-Monitoring auf die wichtigsten Feature-Verteilungen. Sechs-Wochen-Vergleich der vorhergesagten Churn-Rate mit der tatsächlich beobachteten — wenn die Abweichung > 20 % beträgt, außerplanmäßiges Retraining. |

> 📌 **Was der Canvas geleistet hat**
> 
> Dieser Canvas macht Lara Hoffmann, Tobias Berg und Sven Klein gleichermaßen klar, was das Projekt liefert — und was es nicht liefert. Lara sieht den geschäftlichen Mehrwert in einem Satz; Tobias weiß, ab welchem Score er einen Anruf erwartet; Sven sieht, dass eine wöchentliche Batch-Pipeline reicht und keine Echtzeit-Infrastruktur nötig ist. Genau diese Klarheit ist es, was Kapitel 2 im IHK-Bericht zeigt: das Projekt steht — von der Geschäftsfrage bis zur Wartung — als kohärentes Ganzes.

Im Bericht (Kapitel 2) liefern Sie zwei Dinge:

1. **Eine Tabelle** wie oben — alle 10 Felder, vollständig.

1. **Einen Fließtext** (ca. 1–2 Seiten), der die Felder erläutert und die Kohärenz herstellt.

> _„Das Projekt verfolgt einen geschäftsorientierten Ansatz: Marketing soll abwanderungsgefährdete Kund:innen frühzeitig erkennen und gezielt ansprechen können. Der Canvas strukturiert dieses Vorhaben in zehn Feldern, die wir im Folgenden begründet befüllen."_

Schließen Sie mit einem Absatz, der die **Kohärenz** explizit benennt:

> _„Die Felder 3, 5 und 6 bilden eine konsistente Einheit: Die binäre Vorhersage erfordert einen Klassifikator, dessen Bewertung über Recall geschieht — Accuracy wäre angesichts der Klassen-Imbalance nicht aussagekräftig. Die Felder 1 und 8 referenzieren beide den Geschäftsnutzen in EUR und sind damit quantitativ vergleichbar."_

Die Prüfungskommission stellt zu Kapitel 2 erfahrungsgemäß Fragen wie:

-   _„Erklären Sie Ihren Canvas in drei Sätzen — das Geschäftsproblem, die Vorhersage, die Entscheidung."_

-   _„Welche Evaluation-Metrik passt zu Ihrer Aufgabe — und welche passt nicht?"_

-   _„Welches Feld in Ihrem Canvas war am schwersten zu füllen, und warum?"_

-   _„Würden Sie ein Feld heute anders schreiben?"_

Bereiten Sie für jedes Feld einen Satz vor, mit dem Sie es verteidigen können.

-   **Felder leer.** Selbst ein vorsichtiges „derzeit nicht spezifiziert, geplant für eine spätere Phase" ist besser als ein leeres Feld.

-   **Inkohärenz** zwischen Prediction und Evaluation (Klassifikation + RMSE — sofort sichtbarer Fehler).

-   **Technische Sprache im Mehrwert-Feld.** „Wir bauen ein Klassifikationsmodell" ist kein Mehrwert. „Wir reduzieren die Kündigungsquote um zwei Prozentpunkte" ist einer.

-   **Impact ohne Zahlen.** Wenn `Impact` rein qualitativ bleibt („geringere Kosten"), verlieren Sie Punkte.

Der Machine Learning Canvas in Kapitel 2 ist 10 Punkte wert. Sie zeigen mit zehn kohärent gefüllten Feldern, dass Sie das Projekt von der Geschäftsfrage bis zur Wartung durchdacht haben. Achten Sie auf die Kohärenz zwischen Prediction, Learning Approach und Evaluation, und quantifizieren Sie sowohl Value Proposition als auch Impact in geschäftlichen Einheiten.

In der nächsten Lektion gehen wir zu Kapitel 4 des Berichts — der Workflow-Dokumentation: wie Sie die sieben Schritte von der Rohdatei bis zum Ergebnis nachvollziehbar dokumentieren.

---
*Source: https://app.masterschool.com/campus/lesson/Der-Machine-Learning-Canvas-2ab8/5ec8*  
*All content belongs to its respective owners and creators.*