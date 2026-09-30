# Gemeinsame Präsentation Gruppe 6

`Gruppe6_Praesentation_SWW.pptx` ist die gemeinsame Präsentation für den 01.10.2026. Sie folgt dem Aufbau unserer Team-Vorlage und hat durchgehend das SWW-Design aus Kikos Teil. `Gruppe6_Praesentation_SWW_Vorschau.pdf` zeigt alle Folien zum schnellen Durchsehen.

## Aufbau

| Folien | Inhalt | Wer |
|---|---|---|
| 1–2 | Titel, Agenda (Kapitel, Minuten, Personen) | Iana eröffnet |
| 3–5 | Ausgangssituation, Datenstruktur, Datenqualität | Iana |
| 6–16 | ML Canvas, Methodik und Modell, Prüffall | Kiko |
| 17–20 | Ergebnisse für SWW, Verbrauchs-Cockpit, Empfehlungen, Fazit | Patrick |
| 21 | Schluss: Antwort auf die Projektfrage, Fragen | alle |
| B1–B8 | Backup: Kikos Detailfolien, Datenqualität im Detail, Ethik | je nach Frage |
| M1–M10 | Folienmuster zum Weiterbauen | vor dem Termin löschen |

Oben rechts zeigt jede Inhaltsfolie das Kapitel und wer spricht. Ausnahmen sind die Canvas-Folie mit ihren zehn Feldpunkten und die blau-weiße Kapitelfolie mit der großen Nummer. Unten stehen die Canvas-Felder der Folie und der Name. So sieht die Kommission sofort, wer welchen Teil verantwortet.

## In Google Slides öffnen

1. In Google Drive hochladen, dann *Öffnen mit → Google Präsentationen*.
2. Schriften prüfen: Überschriften und Text sind **IBM Plex Sans**, Zahlen **Geist Mono**. Beide gibt es in Google Fonts. Falls eine Folie in einer Ersatzschrift erscheint: *Schriftart → Weitere Schriftarten* und die beiden hinzufügen.
3. Einmal alle Folien durchklicken. Die Datei ist mit einem Validator und einer Vorschau geprüft, den echten Import in Google Slides konnten wir vorab nicht testen.

Diagramme sind absichtlich Bilder. Google Slides wandelt PowerPoint-Diagramme beim Import ohnehin in Bilder um und zeichnet sie dabei neu, sodass Beschriftungen verrutschen würden. Alle Texte sind normale Textfelder und lassen sich bearbeiten.

## Was ihr prüfen müsst

Die Folien von Iana und Patrick sind **Entwürfe aus dem Bericht**. In den Sprechernotizen steht jeweils, woher der Inhalt stammt, ein Vorschlag für den Sprechtext und was noch offen ist.

**Iana**
- Folien 3–5 und B7: Inhalte stammen aus deinen Vorlage-Folien. „Heiztage“ heißt jetzt „Heizgradtage“, die Spaltennamen folgen dem Datensatz.
- Die Ansprechpartner Stefan Lechtenberg und Anke Bürger kommen aus Bericht und Canvas. Streich sie, wenn du sie nicht nennen willst.

**Patrick**
- Folie 17 wiederholt Kikos Kennzahlen nicht, sondern zeigt ihre Wirkung je Bereich. Die zwei EDA-Aussagen stammen aus deinem Fazit im Bericht.
- Folie 18 nutzt den Screenshot des Verbrauchs-Cockpits (Fall ZL-00561). Falls es einen neueren Stand gibt, ersetze ihn mit Muster M9.
- Folie 20: Jede Person sagt ihren eigenen Satz, das stärkt die individuelle Sichtbarkeit.

**Alle**
- Minuten in der Agenda stoppen. Kikos Teil ist mit 9:30 gemessen, die übrigen Zeiten sind Schätzungen.
- Kikos Fazit steht auf Folie 16 und Folie 20. Einer von beiden Sätzen kann weg.
- Backup B8 (Ethik) ist ein Team-Entwurf. Legt fest, wer bei Rückfragen antwortet.
- Vor dem Termin den Abschnitt „Folienmuster“ (M1–M10) löschen.
- Seitenzahlen sind Textfelder („6 / 21“, „B7“). Wer Folien einfügt oder löscht, muss danach die Seitenzahlen und Verweise wie „Backup B7“ oder „Folie 16“ auf allen folgenden Folien anpassen.

## Eigene Folien bauen

Die Folienmuster M1–M10 hinten in der Datei sind für eigene Folien gedacht. Eine Musterfolie markieren, duplizieren (Strg+D) und an die richtige Stelle ziehen, dann die Platzhalter in [eckigen Klammern] ersetzen. M1 fasst die Regeln zusammen. M10 ist ein Baukasten mit allen Scheiben, Chips, Merksatz-Bändern und dem Zählwerk zum Kopieren.

## Neu erzeugen (nur vor der Übergabe)

```bash
node scripts/export_team_charts.mjs              # Diagramme aus Kikos HTML-Deck als PNG
.venv/Scripts/python.exe scripts/build_team_pptx.py
.venv/Scripts/python.exe -m pytest tests/test_team_pptx.py
```

Achtung: Das Neu-Erzeugen überschreibt alle Änderungen, die in Google Slides gemacht wurden. Sobald ihr dort arbeitet, ist die Google-Datei das Original.

Technik: `build_team_pptx.py` nutzt Kikos Bausteine aus `build_kiko_pptx.py` und passt sie für Google Slides an (`team_kit.py`). Die Team-Folien stehen in `team_slides.py`, die Muster in `team_patterns.py`. Icons sind Lucide-Icons (ISC-Lizenz), Schriften unter `brand/design-system/dist/fonts` (OFL).
