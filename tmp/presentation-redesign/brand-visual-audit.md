# Brand- und Sichtprüfung

Quelle: `docs/presentation/Modellierung_Anomaliepruefung_IHK.pptx`, 18 Folien, 16:9.
Alle Folien über Artifact Tool als PNG gerendert (`source-render/slide-01.png` bis `slide-18.png`). Alle 18 in drei Montagen visuell geprüft; Diagrammfolien 4, 6, 7, 8, 9, 10, 11, 14, 16 zusätzlich einzeln gelesen.

Vier HTML-Referenzen über Playwright/Chrome mit lokalen Fonts gerendert und visuell geprüft: `reference-render/TitleSlide.png`, `SectionSlide.png`, `ChartSlide.png`, `KpiSlide.png`.

## Ergebnis

- Das bestehende Deck hat eine nachvollziehbare Erzählfolge und passende SWW-Farben. Es leidet primär an sehr kleinen Schriftgrößen, schwacher Größenhierarchie und redundantem Mikrotext.
- Haupttitel haben 25,5 pt, sehr viele Textläufe 8–12 pt. Brand-Referenz verlangt 32 pt Titel und ca. 20–24 pt Inhalt.
- Die meisten Charts nehmen eine passende Fläche ein, ihre Labels und Achsen sind jedoch viel zu klein. Export mit wesentlich größeren Chartfonts ist notwendig.
- Originalchart für Fallbeispiel (11) zeigt besonders schlecht lesbare Faktorachse. Die Zeilen/Karten des Fazits (13) und Glossars (18) sollten vergrößert oder aufgeteilt werden.
- Ein einheitlicher, ruhiger Quellenfuß ist sinnvoll. Lange Notebook-Pfade in Fußnoten können durch kurze Quellenbezeichnung mit ausführlicher Notiz ersetzt werden.
- Die HTML-Referenz hat eine starke Navy-Titelseite mit großem Logo, viel größere Schrift, breite Diagramme und klare Kennzahlen. Diese Hierarchie übernehmen.
- Die `SectionSlide.html`-Referenz ist selbst rechts abgeschnitten; ihre Flexbreite inkl. Padding überläuft. Nicht direkt nachbauen.
- Historische Zahlen und Aussagen aus HTML-Referenzen sind Demo, nicht aktuelle Projektergebnisse.

## Diagrammsemantik

Ist `#084878` durchgezogen. Prognose `#0090C8` gestrichelt. Residuum `#0080A0`. Schwelle `#A86505` gepunktet. Prüfhinweis `#B3261E` Marker plus Text. Charts durchgehend IBM Plex Sans, keine Geist Mono innerhalb von Plots. Einheiten und Zeitraum sichtbar halten.

## Abgelesene Diagrammwerte aus Quelle

- CV-RMSE: Random Forest 13.272; linear 13.643; bis-zu-3-Monats-Mittel 15.483; Vormonat 18.460 kWh.
- Benchmark 2025 RMSE: Random Forest 9.188; linear 9.414; bis-zu-3-Monats-Mittel 10.922; Vormonat 12.386 kWh.
- Gruppierte Permutation Importance (RMSE-Anstieg kWh): Verbrauchshistorie 7.349; Produktionsplan 717; Wartung 578; Kalender 232; Wetterprognose 193; Jahreszeit 115; Kundentyp 5.
- Kalibrierung: 1.397 OOF-Fehler, q99 144,3547 VLS-h, 1.383 bis zur Schwelle, 14 darüber. Originalgrafik zeigt nur Quantile 80–100%.
- 2025 Hinweise: 114/8.398 =1,36%, 107 unterschiedliche Zähler, 9,5 pro Monat.
- Didaktik MAE/RMSE: A gleichmäßig 10/10, B Einzelpeak 10/20 kWh, jeweils vier Fehlerbeträge.
- Sensitivität: q95 68,0 VLS-h/33,3 Hinweise pro Monat; q97,5 82,4/21,3; q99 144,4/9,5; q99,5 196,3/5,8.

Werte wurden dem Content-Agent zur Prüfung gegen Notebook übermittelt.
