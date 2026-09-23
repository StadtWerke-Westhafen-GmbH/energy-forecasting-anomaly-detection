# Workflow, Datenmodell und Ergebnisse

**Kapitel 4 löst dieses Problem.** Sie dokumentieren den vollständigen Workflow von der Rohdatei bis zum Ergebnis — sodass jemand anders ihn nachvollziehen könnte. Plus: Sie präsentieren die Ergebnisse selbst, kohärent und ehrlich.

Nach dieser Lektion können Sie:

-   die sieben Workflow-Schritte (Quelle, Import, Bereinigung, Transformation, Analyse, Visualisierung, Export) für ein konkretes Datenprojekt eigenständig dokumentieren,

-   erklären, was mit „Datenmodell" in einer Single-Table-Anwendung gemeint ist — und es gegenüber einem Stern- / Joinschema abgrenzen.

| Kennzahl | Wert |
| --- | --- |
| Punkte | 20 von 70 |
| Zielumfang | ca. 3–4 Seiten |
| Pflicht | Workflow-Dokumentation, kohärentes Datenmodell, präsentierte Ergebnisse, Zuverlässigkeit der Ergebnisse |

-   **Ausarbeitung des Workflows** — alle Schritte dokumentiert?

-   **Schlüssigkeit des Datenmodells** — ist die analytische Tabelle nachvollziehbar?

-   **Saubere Dokumentation** — lesbar, konsistent, korrekt zitiert?

-   **Zuverlässigkeit des Ergebnisses** — sind die berichteten Zahlen plausibel und bewertet?

![Die sieben Workflow-Schritte](https://www.notion.so/image/attachment%3Af144e7b4-aee6-4ba3-9a93-14811c46ca42%3AL08_workflow_sieben_schritte.svg?table=block&id=4dfee5dc-ac3a-435f-9612-8a2d9a3be470&cache=v2)

Die sieben Workflow-Schritte

_Die sieben Workflow-Schritte_

Ein vollständiger Daten-Workflow besteht aus sieben Schritten. Dokumentieren Sie **jeden** mit ein bis zwei Absätzen.

| # | Schritt | Was Sie dokumentieren |
| --- | --- | --- |
| 1 | Quelle | Woher kommen die Daten? Welche Datei, welches System, welcher Zeitraum, welche Lizenz? |
| 2 | Import | Wie laden Sie die Daten? Encoding, Trennzeichen, erste Validierung. |
| 3 | Bereinigung | Welche Datenqualitäts-Probleme haben Sie behoben? Pro Problem: Diagnose, Entscheidung, Begründung. |
| 4 | Transformation | Welche neuen Spalten haben Sie konstruiert (Feature Engineering, Aggregationen, Joins)? |
| 5 | Analyse / Modellierung | EDA-Ergebnisse, Modelltyp, Trainingsablauf, Train/Test-Split. |
| 6 | Visualisierung | Welche Charts / Dashboards haben Sie erstellt — und welche Aussage sollen sie transportieren? |
| 7 | Export / Ergebnis-Übergabe | Wohin gehen die Ergebnisse (CSV, Dashboard, API)? Welcher Stakeholder konsumiert sie? |

Diese sieben Schritte sind kein Ritual — sie sind die Reihenfolge, in der **jemand anderes** Ihren Workflow neu aufbauen müsste. Wenn Schritt 3 fehlt, scheitert Schritt 4.

> _„Wir haben die Daten bereinigt und ein Modell trainiert. Die Genauigkeit liegt bei 0,72."_

**Gut** (Schritt mit Diagnose und Entscheidung):

> _„Bei der Datenqualitätsprüfung fanden wir 8.020 Zeilen, davon 20 exakte Duplikate (Spalte für Spalte identisch). Wir entfernten diese mit_ _`drop_duplicates()`_ _und reduzierten den Datensatz auf 8.000 unique Mitarbeitende. Die Duplikate stammen wahrscheinlich aus einem doppelten HR-Export — diese Annahme dokumentierten wir, ohne sie zu verifizieren."_

Der zweite Stil zeigt: **diagnostiziert, entschieden, begründet, dokumentiert.**

In den meisten Kursdatensätzen arbeiten Sie mit **einer einzelnen Tabelle** (single-table). Mit „Datenmodell" ist hier nicht ein Stern- oder Joinschema gemeint, sondern die **bereinigte analytische Tabelle** — also welche Spalten Sie am Ende haben, was sie bedeuten, welche Typen sie tragen.

Tabelle, die in Kapitel 4 stehen sollte:

| Spalte | Typ | Bedeutung | Herkunft |
| --- | --- | --- | --- |
| `kunde_id` | string | eindeutige Kunden-ID | Original |
| `bestellfrequenz_90d` | int | Anzahl Bestellungen letzte 90 Tage | konstruiert aus `bestellungen.csv` |
| `umsatz_30d` | float | Umsatz letzte 30 Tage in EUR | konstruiert aus `bestellungen.csv` |
| `support_tickets_anzahl` | int | offene + geschlossene Tickets | aus `support_tickets.csv` |
| `gekuendigt` | int (0/1) | Zielvariable | aus Bestellverhalten abgeleitet |

Wenn Sie **neue Features** konstruiert haben, beschreiben Sie kurz, **warum** Sie sie konstruiert haben.

Hier zeigen Sie der Prüfungskommission, was Ihr Modell konkret leistet. Vier Bestandteile:

In den passenden Metriken (siehe Lektion 4). Beispiel:

> _„Auf dem Test-Set (n = 2.000, stratifiziert) erreicht der Random-Forest-Klassifikator mit_ _`class_weight='balanced'`_ _eine ROC-AUC von 0,72 und einen Recall auf der Churn-Klasse von 0,43. Bei einem Schwellwert von 0,5 liegt die Precision der Churn-Klasse bei 0,34. Die Wahl der Hauptmetrik (Recall) folgt der geschäftlichen Priorität, möglichst viele tatsächliche Kündigungen früh zu erkennen — Fehlalarme sind weniger kostspielig als verpasste Churn-Fälle."_

Wo wären Sie ohne Ihr Modell? Beispiel:

> _„Die Mehrheitsklassen-Baseline (immer „kein Churn" vorhersagen) erreicht eine Accuracy von 0,83 — bei einer Recall der Churn-Klasse von 0,00. Unser Modell liegt mit 0,72 ROC-AUC deutlich über dieser Baseline und liefert vor allem die operativ wichtige Recall."_

Top-Treiber, mit Plausibilitäts-Check und ggf. Caveat:

> _„Die drei wichtigsten Features (permutationsbasiert) sind Zufriedenheit, Überstunden und Betriebszugehörigkeit. Diese Reihenfolge ist geschäftlich plausibel: niedrige Zufriedenheit ist ein direkter Frühindikator. Auffällig ist, dass_ _`gehalt_brutto`_ _in der impurity-basierten Importance auf Platz 2 erscheint, jedoch in der permutationsbasierten Auswertung auf Platz 8 zurückfällt — Gehalt korreliert mit Position, und Position trägt das eigentliche Signal."_

-   **Ergebnisse ohne Workflow.** Sie zeigen Metriken, aber nicht, wie Sie dahin gekommen sind.

-   **Workflow ohne Entscheidungen.** Sie listen Schritte, aber nicht _warum_ Sie sie so gemacht haben.

-   **Accuracy bei imbalanced classes** als Hauptmetrik.

-   **Keine Baseline.** Ein Wert ist erst aussagekräftig im Vergleich zu einer Alternative.

-   **Feature Importance ohne Caveat** bei Random Forest mit kontinuierlichen Variablen.

-   **Datenmodell-Sektion fehlt** oder wird durch eine Spaltenliste ersetzt, ohne Bedeutung zu erklären.

-   _„Bitte führen Sie mich in 90 Sekunden durch Ihren Workflow — von der Rohdatei bis zum Modell-Output."_

-   _„Welche Datenqualitätsprobleme haben Sie gefunden, und wie haben Sie sie behandelt?"_

-   _„Warum diese Train/Test-Aufteilung?"_

-   _„Welches Merkmal trägt im Modell den größten Beitrag — und ist das geschäftlich plausibel?"_

-   _„Hätten Sie mehr Zeit gehabt — welche eine Verbesserung am Modell hätte den größten Effekt?"_

Diese Fragen sind direkt aus Kapitel 4 ableitbar. Wenn Ihr Bericht solide ist, fallen Ihnen die Antworten leicht.

Kapitel 4 ist 20 Punkte wert und dokumentiert in sieben Workflow-Schritten, **wie** Sie zu Ihren Ergebnissen gekommen sind. Plus: die bereinigte analytische Tabelle als „Datenmodell", die Ergebnisse mit Baseline-Vergleich und Plausibilitäts-Check der Feature Importance, und eine ehrliche Bewertung der Modellqualität.

Wenn eine Kollegin mit Ihrem Bericht den Workflow nachbauen könnte und Ihre Wahl der Metrik versteht, haben Sie das Kapitel erfüllt. In der nächsten Lektion: wie Sie diesen Inhalt **auf Deutsch und in IHK-Formatierung** in den Bericht bringen.

---
*Source: https://app.masterschool.com/campus/lesson/Workflow--Datenmodell-und-Ergebnisse-9eaf/c4cf*  
*All content belongs to its respective owners and creators.*