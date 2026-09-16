# SWW-Vorlagen

- `presentations/sww-project-template.potx`: echte PowerPoint-Vorlagendatei.
- `presentations/sww-project-template.pptx`: dieselben zehn Folien als bearbeitbares Deck.
- `documents/sww-report-template.docx`: SWW-Berichtsvorlage mit Formatvorlagen und Tabellen.
- `documents/Berichtsvorlage_IHK.docx`: unveränderte, ursprünglich gelieferte IHK-Vorlage.
- `notebooks/sww-analysis-template.ipynb`: Startpunkt für neue Analysen.

PowerPoint-Text, Formen, Tabellen und Beispielchart sind bearbeitbar. Das Logo bleibt ein
Rasterbild, bis ein offizielles Vektorasset vorliegt. Die zehn Beispielseiten lassen sich
duplizieren; sie sind keine zehn zusätzlich programmierten Folienmaster-Layouts.

Die TTF-Dateien unter `../design-system/dist/fonts/` können für Office lokal installiert werden.
Sie sind nicht in die Office-Dateien eingebettet. Bei fehlenden Schriften kann Office eine
Ersatzschrift verwenden; dann Umbrüche vor dem Export prüfen.

Platzhalter in eckigen Klammern ausfüllen und synthetische Chartdaten vor der Abgabe ersetzen.
Die SWW-Berichtsvorlage ergänzt das Projekt; verbindliche Format- und Umfangsvorgaben der IHK
gehen vor.

Erzeugung: `python scripts/build_templates.py` nach dem Token- und Web-Build, mit den
Entwicklungsabhängigkeiten aus `uv.lock`. Erzeugte Vorlagen werden überschrieben; eigene
Präsentationen und Berichte unter `docs/` speichern. Eigene Notebooks unter `notebooks/` speichern.
