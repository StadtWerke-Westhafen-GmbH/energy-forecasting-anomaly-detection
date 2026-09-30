# Team-Präsentation Gruppe 6 – Umsetzungsplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gemeinsame, Google-Slides-taugliche PPTX für Gruppe 6 im SWW-Design mit Kikos 17 Folien, Entwürfen für Iana und Patrick, Backup und Folienmustern.

**Architecture:** `build_team_pptx.py` lädt `build_kiko_pptx.py` per `runpy` und ersetzt einzelne Funktionen in dessen Globals (Kapitelleiste, Google-Modus). Kikos Folien entstehen mit den bestehenden Buildern; Bereiche mit nativen Diagrammen werden danach durch PNG-Ausschnitte aus Kikos HTML-Deck ersetzt. Neue Folien bauen `team_kit.py` (Rahmen, Karten) und `team_slides.py` / `team_patterns.py` aus denselben Grundbausteinen.

**Tech Stack:** Python 3 + python-pptx, lxml, Pillow; Node + Playwright für Diagramm-PNGs; pytest.

**Spec:** `docs/superpowers/specs/2026-09-30-team-praesentation-design.md`

## Global Constraints

- Folie 1280 × 720 CSS-px, 1 px = 9525 EMU, Schrift px × 0,75 = pt (wie `build_kiko_pptx.py`).
- Schriften nur `IBM Plex Sans`, `Geist Mono`; keine SVG-Bilder; keine Chart-Parts im Paket.
- Keine `a:alpha` in der Ausgabe; keine `cap="all"` (Versalien als echte Großbuchstaben).
- Leitfragen enden mit „?“ und haben höchstens 58 Zeichen; Titel ist die Antwort.
- Datum 01.10.2026; Namen: Iana Kraievska, Patrick Olmo Hederer, Kiko Ramon Lukas.
- Zahlen wie Bericht (`docs/IHK_Bericht_Gruppe_6_final.docx`) und Ianas Vorlage-Folien; `dashboard.png` (synthetisch) nie verwenden.
- Kikos Einzel-Deck (`build_kiko_*.py`, Ausgaben unter `docs/presentation/kiko/`) bleibt byte-gleich.

## Review Focus

- Textfeld ohne Umbruch, das in Google Slides breiter läuft → muss mit 10 % Reserve einzeilig bleiben (Test: jede `wrap="none"`-Box ist ≥ gemessene Breite × 1,08).
- Diagramm-Ersatz trifft falsche Formen (z. B. Kartenrahmen um das Diagramm) → nur Formen vollständig innerhalb des SVG-Rechtecks löschen (Sichtprüfung Render + Test: Kartenrahmen je Diagrammfolie bleibt).
- HTML- und PPTX-Foliensatz laufen auseinander (neue Kiko-Folie) → Build bricht mit klarer Meldung ab (Test).
- Transparente Formen auf Karten statt auf Folienhintergrund → Mischfarbe sichtbar falsch (Sichtprüfung der dunklen Folien).
- Kikos Einzel-Deck ändert sich unbeabsichtigt → bestehende Tests `test_kiko_pptx.py` laufen weiter grün.

---

### Task 1: Diagramm-PNGs aus Kikos HTML-Deck

**Files:** Create `scripts/export_team_charts.mjs`; Output `docs/presentation/team/assets/charts/s{NN}_svg{II}.png` + `charts.json`.

- [ ] Skript öffnet `docs/presentation/kiko/Kiko_ML_Canvas_Methodik_Prueffall.html` mit `deviceScaleFactor: 3`, blendet Intro/Trenner aus (wie `export_kiko_praesentation.mjs`), iteriert `section.slide` und alle `svg` mit Breite ≥ 200 px; speichert Element-Screenshot und `{slide, svg, x, y, w, h}` (relativ zur Folie) in `charts.json`.
- [ ] Lauf: `node scripts/export_team_charts.mjs` → erwartet ≥ 8 PNGs.

### Task 2: Team-Build mit Google-Modus und Kikos Folien

**Files:** Create `scripts/build_team_pptx.py`, `tests/test_team_pptx.py`.

**Interfaces (Produces):** `K` (Globals von build_kiko_pptx), `google_mode(K)`, `build(path) -> Path`, `CHAPTERS`, `OUT`.

- [ ] Test zuerst: Paket ohne `ppt/charts/`, ohne `.svg`, ohne `a:alpha`, ohne `cap="all"`, nur zwei Schriftnamen; Folie „ML Canvas“ an Position 6.
- [ ] Google-Modus: `_rgba` mischt Alpha gegen den aktuellen Folienhintergrund (`page` merkt ihn sich); `text` schreibt Versalien aus und gibt `wrap=False`-Boxen 10 % Reserve (links/rechts/mittig je nach Ausrichtung).
- [ ] Diagramm-Ersatz: `place_chart`/`_combo` zeichnen auf eine Hilfsfolie, die am Ende entfernt wird; nach jedem Kiko-Builder werden für jede Folie mit Diagramm alle Formen vollständig innerhalb eines Rechtecks aus `charts.json` gelöscht und das PNG eingesetzt.
- [ ] Kapitelleiste statt Schrittleiste (`tracker` ersetzt): sechs Scheiben 01–06, Paare je Person, aktives Kapitel gefüllt; Label „03 · ML Canvas · Kiko“.
- [ ] Nummerierung: Hauptfolien „n / N“, Backups „B1…“, Muster „M1…“.
- [ ] Tests grün: `.venv/Scripts/python.exe -m pytest tests/test_team_pptx.py -q`.

### Task 3: Team-Folien (Titel, Agenda, Iana, Patrick, Backup)

**Files:** Create `scripts/team_kit.py`, `scripts/team_slides.py`; Modify `tests/test_team_pptx.py`.

**Interfaces:** `team_kit.frame(prs, K, *, bg, question, qicon, title, chapter, speaker, refs, num, notes) -> slide`; `icard(s, x, y, w, h, icon, tone, head, body)`; `merk(s, x, y, w, text, dark)`; `table(s, x, y, widths, rows, header=True)`.

Inhalte (Zahlen wörtlich):

| Folie | Leitfrage | Titel | Kern |
|---|---|---|---|
| Titel | – | Prognose des monatlichen Energieverbrauchs und Erkennung von Anomalien | Split; Projektfrage der Vorlage; 3 Namen + Rollen; „Gruppe 6 · IHK Data Analyst · 01.10.2026“ |
| Agenda | Wer erzählt welchen Teil? | Sechs Kapitel, drei Stimmen, 30 Minuten | 01 Ausgangssituation 3 min, 02 Daten 4 min (Iana) · 03 ML Canvas, 04 Methodik (Kiko, 9:30) · 05 Ergebnisse, 06 Empfehlungen (Patrick) |
| Iana 1 | Warum braucht SWW eine Prognose? | Planung per Hand, Auffälliges erst im Quartal | 700 Großkunden, ~180 Mio. EUR; Probleme→Folgen; Ziel + Abgrenzung; Lechtenberg / Bürger |
| Iana 2 | Welche Daten stehen zur Verfügung? | 700 Zähler, 24 Monate, sechs Merkmalsgruppen | 6 Kacheln wie Vorlage-Folie 5; 16.830 → 16.800 Zeilen, 16 Spalten |
| Iana 3 | Was war an den Rohdaten nicht in Ordnung? | Vier Problemarten, jede mit begründeter Maßnahme | Tabelle wie Vorlage-Folie 6; Merksatz Lastspitzen |
| Patrick 1 | Was hat das Projekt für SWW ergeben? | Genauer planen, früher prüfen | Beschaffung: −15,9 % RMSE; Netzmanagement: 9,5 Hinweise/Monat; Datenqualität: 10/10 unmögliche Werte |
| Patrick 2 | Wie arbeitet die Fachabteilung damit? | Das Verbrauchs-Cockpit führt vom Hinweis zum Prüffall | Screenshot `verbrauchs-cockpit-prueffall.png` + 4 nummerierte Hinweise |
| Patrick 3 | Was empfehlen wir SWW? | Erst im Schatten testen, dann ausrollen | Empfehlung 1 Schattenpilot, 2 Feedback-Labels; 4 nächste Schritte; Ausblick |
| Patrick 4 | Was nehmen wir mit? | Drei Rollen, drei Erkenntnisse | je 1 Satz aus Bericht 3.6 |
| Schluss | – | Ihre Fragen | dunkel; Antwort auf die Projektfrage in einem Satz |
| Backup | – | Trenner, Datenqualität im Detail (Vorlage-Folie 15), Ethik | Ethik: ausgeschlossene Merkmale, Gruppen, Letztentscheidung, Datenschutz (Pilot festlegen) |

- [ ] Tests zuerst: Folienfolge (Titel, Agenda, Iana×3, Kiko×11, Patrick×4, Schluss, Backups, Muster), Leitfragen-Regel, Namen, Ianas Zahlen (16.830, 16.800, 11.316, 505, 8.400, 700, 30, 20), Notizen „Entwurf aus Bericht“ auf Iana-/Patrick-Folien.
- [ ] Umsetzung, Build, Tests grün.

### Task 4: Folienmuster

**Files:** Create `scripts/team_patterns.py`; Modify `tests/test_team_pptx.py`.

- [ ] Muster M1–M10: Regeln · 3 Karten · Text + Bild · Tabelle · Kennzahlen (Zählwerk) · Prozesskette · Split · dunkler Merksatz · Screenshot + Hinweise · Baukasten (alle Scheiben-Töne, Chips, Merksatz-Band, Zählwerk). Platzhalter in [eckigen Klammern], Notizen mit Gebrauchsanweisung.
- [ ] Test: 10 Musterfolien, jede mit Notiz, alle Platzhalter in eckigen Klammern.

### Task 5: Vorschau, Validierung, Doku

**Files:** Create `docs/presentation/team/README.md`; Output `folien/*.png`, `Gruppe6_Praesentation_SWW_Vorschau.pdf`.

- [ ] QA-Render aller Folien (Renderer aus dem Scratchpad), Sichtprüfung jeder Folie, Korrekturen.
- [ ] pptx-Validator: „All validations PASSED!“.
- [ ] Gesamte Suite: `.venv/Scripts/python.exe -m pytest -q`.
- [ ] README: Aufbau, Google-Import (Schriften prüfen), wer was prüft, offene Punkte.
