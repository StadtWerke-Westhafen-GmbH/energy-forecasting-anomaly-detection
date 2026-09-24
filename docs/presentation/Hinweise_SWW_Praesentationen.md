# Die beiden SWW-Präsentationen

**ML_Modellierung_Anomaliepruefung_SWW.pptx** enthält 18 Folien als eigenständigen ML-Teil: Zielvariable, Merkmale, zeitliche Validierung, Modellvergleich, Kalibrierung, Prüfvolumen und Fallbeispiel. Die Live-Demo gehört zur Gesamtpräsentation.

**Gesamtpraesentation_IHK_SWW.pptx** enthält 39 Folien. Folien 1–25 bilden den Projektvortrag, 26–27 begleiten die Demo, 28 eröffnet das Fachgespräch. Folien 29–39 sind Vertiefung und müssen nicht im Hauptvortrag gezeigt werden. Der Ablauf orientiert sich an den 30 Minuten Vortrag und 15 Minuten Demo der gelieferten Vorlage.

Zu beiden Dateien gibt es eine PDF-Lesefassung. Die PowerPoint-Dateien enthalten bearbeitbare Diagramme und Tabellen sowie Sprechernotizen mit Quellen und Erläuterungen. Die PDF-Dateien geben die geprüften Folien als Bildseiten wieder; bearbeitbare Inhalte und Notizen stehen in PowerPoint.

## Darstellung und Demo

Die Gestaltung folgt dem SWW-Designsystem mit IBM Plex Sans und Geist Mono. Die Schriftdateien liegen unter `brand/design-system/dist/fonts`. Für die vorgesehene Darstellung in PowerPoint müssen diese Schriften verfügbar sein. Die PDF-Ansicht benötigt keine Installation.

Der Cockpit-Link erwartet den lokalen Projektserver auf Port 4173. Die Demo zeigt retrospektive Projektdaten, keine produktive Systemanbindung. Ein Original-Screenshot und die Diagramme stehen als Rückfallebene in der Präsentation bereit.

## Einheitlicher Zahlenstand

- ML-Ergebnisse: Notebook 13. Die Permutation Importance verwendet drei Wiederholungen. Der Bericht enthält an dieser Stelle teilweise Notebook 12 mit fünf Wiederholungen; daraus entstehen leicht andere Werte bei gleicher Rangfolge.
- Neue EDA-Grafiken: alle 16.800 bereinigten Zähler-Monate. Die 20 Vertragsleistungsüberschreitungen bleiben fachlich offene Plausibilitätsfälle. Ältere, gefilterte EDA-Auswertungen können geringfügig abweichen.
- Datenqualitätszahlen beziehen sich grundsätzlich auf die deduplizierte Basis. Fehlende Historienwerte vor und nach der ML-Neuberechnung werden in den Notizen getrennt erläutert.
- Ein Prüfhinweis ist keine bestätigte Anomalie. Wirtschaftliche Wirkung, Precision und Recall sind im Projekt nicht belegt; der Pilot soll die notwendige Evidenz erheben.
- Ein Prüfungstermin wurde wegen widersprüchlicher Datumsangaben in den Quellen nicht ergänzt.

Die bereitgestellten Originalpräsentationen bleiben erhalten. Paketstruktur, editierbare Diagrammdaten und gerenderte Folien wurden geprüft. Eine native Ausführung in Microsoft PowerPoint war in dieser Umgebung nicht verfügbar.
