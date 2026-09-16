# Übergabe · SWW-Designsystem

Stand: 16.09.2026, Version 0.1.0.

## Was verwendet wird

`brand/design-system/tokens/design-tokens.json` enthält die verbindlichen Designwerte.
Die Build-Skripte erzeugen daraus Browser- und Python-Themes sowie Office-Vorlagen.
CSS, Python, JavaScript und Plotly verwenden identische Schwellwert- und Kundentypfarben.
Die generierten Token-Ausgaben werden durch einen Aktualitätscheck abgesichert.

Die ursprünglich mitgelieferte SWW-Design-Skill und ihre Regeln wurden für die neue Gestaltung
herangezogen. Die technische Integration wurde modernisiert: lokale Pakete und Fonts,
Build zur Entwicklungszeit, installierbares Python-Paket, editierbare Office-Vorlagen.

## Geänderte Pfade

| Bisher | Jetzt |
| --- | --- |
| `src/ci/StadtWerke Westhafen Design System/` | `brand/design-system/` |
| `doc/` | `docs/` |
| `doc/Berichtsvorlage_IHK.docx` | `brand/templates/documents/Berichtsvorlage_IHK.docx` |
| `assets/plotly/sww_eda.py`, `sww_theme.py` | `src/energy_analytics/visualization/` mit Kompatibilitätsimporten |
| globale Hex-Werte in mehreren Theme-Dateien | `tokens/design-tokens.json` und generierte Exporte |
| generierte Tool-Dateien und `.dc.html`-Templates | `brand/reference/export/` (archiviert) |

Der von einem anderen Prozess geöffnete Ordner `ipynb/` konnte nicht umbenannt werden.
Die dortigen Analysen wurden unverändert belassen. `notebooks/00_design_system.ipynb`
zeigt den neuen Importweg. Eine spätere Umbenennung der alten Notebooks sollte bei geschlossenem
Kernel erfolgen; relative Datenpfade müssen danach geprüft werden.

## Prüfungen

Lokal bestanden: 20 Python-Tests und Browserprüfungen für alle 58 HTML-Vorschauen.
Die Codezellen des neuen Beispielnotebooks wurden zusätzlich erfolgreich ausgeführt;
die bestehenden Analyse-Notebooks wurden nicht ausgeführt oder verändert.

- Statische und semantische Tokenprüfung inklusive unbekannter Referenzen und Zyklen.
- Ausgewählte UI-Text-Kontraste, einschließlich grüner Solid-Badges und invertierter KPI-Statuswerte.
- Alle 15 Plotly-Funktionen, tatsächliches Matplotlib-Rendering und konsistente Datenfarben.
- PPTX/POTX-Paketstruktur, editierbarer Chart, DOCX-Struktur und Notebook-Schema.
- Alle HTML-Vorschauen im Browser bei blockierten externen Netzwerkanfragen.
- Dialog-Fokus und mobile Startseite; weitere Prüfschritte im Testcode dokumentiert.

Die Office-Dateien sind strukturell geprüft. Microsoft PowerPoint/Word oder LibreOffice standen
für eine native visuelle Endkontrolle nicht zur Verfügung. Vor einer Abgabe einmal in der
Zielanwendung öffnen und Textumbrüche prüfen. Browseransichten wurden gerendert und angesehen.

## Offene externe Inputs

1. Offizielles Vektorlogo sowie transparente und einfarbige Varianten bereitstellen.
2. Corporate-Font-Vorgaben bestätigen, falls eigene Lizenzschriften existieren.
3. Verbindliche IHK-Formatvorgaben bei der eigentlichen Abgabe mit der Originalvorlage abgleichen.

Das Cockpit ist weiterhin eine Designreferenz mit Demodaten. Reale Datenanbindung, Prognosemodelle,
Authentifizierung, Speicherung und Ticketversand sind eigenständige Implementierungsaufgaben.
Aus den Beispieldaten dürfen keine fachlichen Ergebnisse des Projekts abgeleitet werden.

## Wartung

Versionierte Quellen und die zum direkten Öffnen notwendigen Ausgaben werden eingecheckt.
`node_modules`, `.venv`, Caches und Prüf-Screenshots sind ignoriert. Abhängigkeiten sind
über `package-lock.json` und `uv.lock` festgeschrieben. `npm ci` und `uv sync --frozen`
installieren reproduzierbar. Fremdlizenzen stehen bei den lokalen Distributionsdateien.

Die unveränderte Original-Logo-Datei und die Aufgabenstellung wurden per SHA-256 als Duplikate
identifiziert; nur die zusätzlichen Kopien wurden entfernt. Originale sind weiter vorhanden.
Git enthält außerdem die vorherigen Pfade in der Historie.
