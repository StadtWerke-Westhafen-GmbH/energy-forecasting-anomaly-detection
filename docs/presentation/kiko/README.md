# Kikos Präsentationsteil: ML Canvas, Methodik und Modell, Prüffall

## Aktuelle Fassung für den Drive: `Kiko_ML_Folien_SWW.pptx`

Nach der Abstimmung im Team ist der Teil reduziert und steht in den Folienlayouts des Designsystems
(`brand/design-system/templates/projekt-praesentation/index.html`): Label über dem Titel, schlichte
Karten ohne Icon-Scheiben. Neun Hauptfolien (etwa 8:30 Minuten) und vier Backups:

1 Kapitel · 2 ML Canvas (sechs ML-Felder, Iana und Patrick nur verwiesen) · 3 Zeitliche Validierung ·
4 Zielgröße VLS · 5 Warum RMSE (Beispiel aus Notebook 13) · 6 Modellwahl 2024 · 7 Schwelle als
Abwägung · 8 Prüffall ZL-00147 mit Bewertung · 9 Ausblick Klassifikationsmodell, Übergabe an Patrick.
Backups: Hyperparameter, Lag-Merkmale, Kalibrierung Nov–Dez 2024, Canvas-Wortlaut.

Ergebnisse des Testjahrs 2025 (RMSE 9.188 kWh, −15,9 %, MAE, R², Treiber, Hinweiszahlen) zeigt Patrick;
sie stehen bewusst nicht auf diesen Folien. Die Notizen jeder Folie enthalten Stichworte, einen Sprechtext zum Ablesen, „So verstehst du es“ (Hintergrund in einfachen Worten) und Antworten auf Rückfragen; der Text liegt in `scripts/kiko_ml_notizen.py`.
Vorschau: `Kiko_ML_Folien_SWW_Vorschau.pdf`.

```bash
.venv/Scripts/python.exe scripts/build_kiko_ml_folien.py      # Layouts in scripts/sww_layouts.py
.venv/Scripts/python.exe -m pytest tests/test_kiko_ml_folien.py
```

## Frühere Fassung (v3)

Elf Hauptfolien (9:30 Minuten plus 30 Sekunden Puffer für die Übergaben) und sechs Backup-Folien im
SWW-Präsentationsdesign (`brand/reference/export/templates/projekt-praesentation`). Kennzahlen und
Diagrammdaten stammen aus den gespeicherten Ausgaben von Notebook 13
(`notebooks/13_modellierung_von_grund_auf_verstehen.ipynb`); Werte, die nur im Bericht stehen
(R², Treiber aus Tab. D1, 92 % Streuung, Canvas-Wortlaut Tab. A1), sind im Generator als `BERICHT`
bzw. `CANVAS_A1` hinterlegt und per Test gegen den Bericht geprüft. Nichts wird neu trainiert.

**Folienfolge:** 1 ML Canvas (alle zehn Felder als Kette) · 2 Fehlerkosten · 3 Roter Faden mit Einstieg
ZL-00147 · 4 Validierung · 5 Zielgröße VLS · 6 Modellwahl und Test · 7 Vom Fehler zum Prüfhinweis ·
8 Kalibrierung · 9 Testjahr 2025 · 10 Fallbeispiel ZL-00147 · 11 Dashboard, Fazit, Übergabe.
Backups: B1 Canvas-Wortlaut Tab. A1 · B2 Hyperparameter · B3 Treiber · B4 Lags · B5 Grenzen und
Verantwortung · B6 Prüfaufwand statt ROI.

**Designsprache:** Jede Folie beginnt mit einer Leitfrage (Scheibe + Frage), der Titel ist die Antwort.
Icon-Scheiben stehen für Konzepte (gleiche Scheibe = gleiches Konzept), die Scheiben oben rechts zeigen
den roten Faden, die Fußzeile das belegte Canvas-Feld. Zählwerk-Ziffern markieren die vier Kernzahlen.
Icons: Lucide (ISC-Lizenz, `node_modules/lucide-static`).

| Datei | Zweck |
|---|---|
| `Kiko_ML_Canvas_Methodik_Prueffall.pptx` | Bearbeitbare PowerPoint-Fassung der 17 Folien: Textfelder, native Diagramme mit Daten, Icon-Scheiben, Notizen |
| `Kiko_ML_Canvas_Methodik_Prueffall.html` | Foliensatz, offline lauffähig (Fonts, Logo, Screenshots eingebettet) |
| `Kiko_ML_Canvas_Methodik_Prueffall.pdf` | Druck- und Rückfallfassung, 16:9 |
| `folien/*.png` | Einzelfolien (2560 × 1440, ohne Seitenzahl) zum Einfügen in die gemeinsame Präsentation |
| `Kiko_Sprechzettel.html` | Sprechtext, Lesehilfe und mögliche Rückfragen je Folie |
| `assets/*.png` | Screenshots aus dem Energie-Cockpit (Prüffall ZL-00147 · 08/2025) |
| `assets/icons/*.png` | Lucide-Icons als PNG (`name__FARBE.png`) für die Icon-Scheiben der PowerPoint-Fassung |
| `schriften/` | IBM Plex Sans und Geist Mono (TTF, SIL Open Font License) für die PowerPoint-Fassung |

## PowerPoint-Fassung

Vor dem Öffnen die Schriften aus `schriften/` installieren (Windows: Rechtsklick → *Installieren*,
macOS: Doppelklick → *Installieren*). Ohne sie ersetzt PowerPoint die Schrift, und Texte können
anders umbrechen. Zeichen wie → ≥ √ ergänzt PowerPoint automatisch aus Systemschriften.

- Diagramme sind echte PowerPoint-Diagramme; die Daten lassen sich über *Daten bearbeiten* ansehen.
- Zahlenformate folgen der Office-Sprache: in deutschem Office 13.272, in englischem 13,272.
- Die farbigen Fold-Rauten und Streuungsstriche auf Folie 6 sind Formen über dem Diagramm, keine Datenreihe.
- Icon-Scheiben sind Gruppen aus Kreisform (Farbe über *Formfüllung* änderbar) und Icon-Bild; Zählwerk-Ziffern
  sind Gruppen „Zählwerk …“ aus Zellen und Ziffern. Versal-Labels nutzen *Alle Großbuchstaben*, der Text bleibt normal.
- Stichworte, Sprechtext, Lesehilfe und vorbereitete Antworten stehen in den Notizen jeder Folie.
- Einzige bewusste Abweichung: Auf B6 steht „Ø 9,5 je Monat“ in der Titelzeile, weil die Beschriftung im
  HTML die Säulenzahl „10“ (Dez) überdeckt. Schriftschnitt 500 (Medium) erscheint in PowerPoint als Regular.
- In Google Slides werden Diagramme beim Import zu Bildern; Texte bleiben bearbeitbar.

## Präsentieren und üben

Foliensatz im Browser öffnen, dann **P** drücken (oder `#present` an die URL hängen). Der
Modus startet bei der Folie, die gerade im Bild ist:
**← →** blättern, **N** Sprechtext einblenden, **H** Zeitanzeige (Folie, verstrichene Zeit,
Sollzeit bis Folienende) ein/aus, **R** Timer zurücksetzen, **Esc** beenden.
Sprechtext und Zeitanzeige sind für das Üben gedacht; bei gespiegeltem Beamer ausgeblendet lassen
und den Sprechzettel auf einem zweiten Gerät nutzen.

## Neu erzeugen

```bash
python scripts/build_kiko_praesentation.py      # HTML + Sprechzettel (braucht matplotlib, fonttools, Pillow aus der .venv)
node scripts/export_kiko_praesentation.mjs      # PNG je Folie + PDF, prüft Überlauf (KEEP_NUM=1: PNGs mit Seitenzahl)
python scripts/build_kiko_pptx.py               # PowerPoint-Fassung aus denselben Daten und Texten
python -m pytest tests/test_kiko_praesentation.py tests/test_kiko_pptx.py
node scripts/render_icons.mjs <ordner> '[{"name":"gauge","color":"#FFFFFF"}]'   # Icons als PNG (build_kiko_pptx.py ruft das bei fehlenden Icons selbst auf)
```

Die Screenshots in `assets/` wurden mit Playwright aus dem lokalen Energie-Cockpit
(`node scripts/preview.mjs`, Ansicht Anomalieprüfung → Prüffall) aufgenommen. Die Bewertung
im Dashboard wird nur lokal im Browser gespeichert.
