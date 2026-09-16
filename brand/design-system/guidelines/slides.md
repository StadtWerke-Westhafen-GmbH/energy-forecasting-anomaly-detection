# Präsentationen

Die bearbeitbaren Vorlagen liegen unter `brand/templates/presentations/`:

- `sww-project-template.potx`: PowerPoint-Vorlagendatei.
- `sww-project-template.pptx`: zehn bearbeitbare Beispielseiten.

Die Seiten enthalten echte Textfelder, Formen, eine Tabelle und ein natives PowerPoint-Diagramm.
Sie lassen sich duplizieren. Die bereitgestellten Seiten sind keine zusätzlichen Folienmaster-Layouts.
Die Office-Theme-Farben und -Schriften werden aus den gemeinsamen Tokens erzeugt.

## Gestaltung

16:9, 33,87 × 19,05 cm. Titel 32 pt, Fließtext etwa 20–24 pt, Fußzeile 10–12 pt.
IBM Plex Sans für Texte; Geist Mono für große Kennzahlen.
Die TTFs unter `brand/design-system/dist/fonts/` vor einer finalen Präsentation lokal installieren;
Schriften sind nicht eingebettet.

Navy für Titel, Kapiteltrenner und hervorgehobene Kernaussagen. Weiße Inhaltsfolien für Diagramme
und Tabellen. Ein Gedanke pro Seite, Überschrift als Aussage. Quellen, Zeitraum und Einheit
angeben. Platzhalter und synthetische Daten vor der Abgabe ersetzen.

## Diagramme

Der native Chart ist ein bearbeitbares Beispiel. Echte Projektergebnisse aus dem Notebook
exportieren und mit belegter Aussage, Einheit und Testzeitraum einfügen:

```python
eda.save_for_slide(fig, "prognose.png")
```

Daten sind weiterhin im Notebook nachvollziehbar. Ein statisches Bild erhält keine interaktiven
Hover-Erklärungen: nötige Labels müssen im Bild oder als Folientext sichtbar sein.

## HTML-Referenzen

`templates/projekt-praesentation/index.html` zeigt die zehn ursprünglichen HTML-Layouts.
Sie demonstrieren den Stil; die Office-Vorlage verwendet bewusst ausfüllbare Platzhalter.
Die ursprünglichen Layoutbeispiele enthalten historische Demowerte und sind keine Ergebnisse.

Vor Abgabe die Office-Datei in der Zielanwendung prüfen: Umbrüche, fehlende Fonts,
Diagrammbeschriftungen und verbindliche IHK-Vorgaben.
