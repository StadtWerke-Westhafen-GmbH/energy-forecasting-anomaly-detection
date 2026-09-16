# SWW · Verbindliche Gestaltungsregeln

Das Design verbindet Hafeninfrastruktur und Energieanalyse. Große Navy-Flächen geben Struktur,
Teal markiert Interaktion, weiße Flächen halten Daten lesbar. Der bestehende SWW-Markenentwurf
ist die Grundlage der Überarbeitung; Markenassets werden nicht nachgezeichnet.

## Sprache und Zahlen

Deutsch, sachlich, präzise. In Bedienoberflächen kurze Handlungsbezeichnungen wie „Anomalien prüfen“.
Im Fließtext „Sie“. Eine Anomalie ist ein Prüfhinweis, keine bewiesene Störung.
Jede Kennzahl trägt Zeitraum, Einheit und nötigen Vergleichsmaßstab.

Dezimalkomma, Punkt als Tausendertrennzeichen, Leerzeichen vor der Einheit:
`14.820 kWh`, `12,4 %`, `−8,3 % gegenüber Prognose`. Prozentsätze benötigen eine Bezugsgröße.
Monate: `MM/JJJJ`; Tagesangaben: `TT.MM.JJJJ`. Keine ungesicherte Genauigkeit vortäuschen.

> Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges.

## Farben

Verbindliche Werte und Referenzen stehen ausschließlich in `tokens/design-tokens.json`.
Semantische Tokens verwenden, zum Beispiel `--text-primary`, `--status-warn` oder `--data-forecast`.
Die Basisfarben der Marke bleiben erhalten; lesbare Text- und Statusvarianten verwenden dunklere
Stufen derselben Farbfamilie.

- Navy: Struktur, Überschriften, primäre Aktionen und Ist-Werte.
- Teal: Interaktion; in Diagrammen außerdem Residuen/Gewerbe mit ausdrücklicher Beschriftung.
- Cyan: Prognose/Modellausgabe, ergänzt durch eine gestrichelte Linie.
- Grün: positive Zustände; Kommunal als fest benannte Kundengruppe.
- Amber und Rot: Schwellwerte/Prüfhinweise bzw. Anomalien/kritische Zustände.

Rot, Amber und Prognose-Cyan gehören nicht in den beliebigen kategorialen Farbzyklus.
Status niemals ausschließlich über Farbe vermitteln. Für positive oder negative Änderungen
entscheidet die fachliche Bedeutung, ob Grün/Rot sinnvoll ist; das Vorzeichen allein reicht nicht.

## Typografie und Layout

IBM Plex Sans für Text und Diagramme; Geist Mono für IDs, Code und große Kennzahlen.
Webfonts werden lokal geladen. Matplotlib verwendet die mitgelieferten TTF-Dateien.
Office und Kaleido brauchen installierte Schriften für exakt gleiche Umbrüche.

Dashboard: 4-px-Abstandsraster, 24-px-Seitenabstand, 16-px-Gaps, 10-px-Kartenradius.
Weiße Karten mit dezenter Kante und Schatten, kompakte Tabellen. Schmale Ansichten dürfen
umfließen; lange Tabellen scrollen horizontal in ihrem Container. Hinweise nicht durch
abgeschnittene Textzeilen oder zu kleine Schrift unlesbar machen.

Folien: 16:9, 32-pt-Titel, etwa 20–24 pt Inhalt. Quellen und Fußzeilen kleiner, aber lesbar.
Ein Gedanke pro Folie. Große Tabellen oder Canvas-Details auf mehrere Folien aufteilen.

## Interaktion und Zugänglichkeit

Sichtbarer, deckender Fokusring; Dialoge erhalten den Fokus, halten Tab darin und geben den
Fokus beim Schließen zurück. Formulare haben Labels, beschriebene Fehlermeldungen und
programmatisch verknüpfte Hinweise. Tabs unterstützen Pfeiltasten, Pos1 und Ende.
Bewegung bleibt funktional; `prefers-reduced-motion` berücksichtigen.

Getestete kleine Textpaare erreichen mindestens 4,5:1 gemäß
[WCAG-Kontrastanforderung](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
Dies deckt ausgewählte Farbkombinationen ab und ersetzt keinen vollständigen Anwendungsaudit.

## Assets und Herkunft

Originale Logos unter `assets/`; Ausgangsdatei unter `brand/reference/uploads/sww-logo.png`.
Die Logos haben einen weißen Hintergrund. Auf Navy einen weißen Halter verwenden, Proportionen
beibehalten und genug Freiraum lassen. Transparente SVG-/PNG- und einfarbige Versionen sind offen.

Lucide-Icons werden lokal gebündelt, monochrom und mit Textlabel verwendet.
Font-/Icon-Lizenzen liegen in `dist/licenses/`. Kein Ersatzlogo automatisch erzeugen oder
eine eingebettete Rastergrafik als echtes Vektorlogo ausgeben.
