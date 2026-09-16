# Westhafen Energy Analytics

Stromverbrauch verstehen, prognostizieren und Auffälligkeiten erkennen.
IHK-Projekt, Gruppe 6.

## Design und Vorlagen verwenden

Das gemeinsame Designsystem liegt in [brand/design-system](brand/design-system/readme.md).
Die SWW-Farben, Typografie und Datenrollen verbinden Dashboard, Notebooks, Folien und Berichte.

- [Design-Startseite](brand/design-system/index.html)
- [PowerPoint-Vorlage (.potx)](brand/templates/presentations/sww-project-template.potx)
- [Bearbeitbares Beispieldeck (.pptx)](brand/templates/presentations/sww-project-template.pptx)
- [SWW-Berichtsvorlage](brand/templates/documents/sww-report-template.docx)
- [Analyse-Notebook](notebooks/00_design_system.ipynb)

Die Webansichten funktionieren mit den mitgelieferten Assets ohne Internet. Für die lokale Vorschau
genügt Node.js ab Version 22:

```sh
node scripts/preview.mjs
```

Dann **http://127.0.0.1:4173** öffnen. Der Server ist nur lokal erreichbar und gibt ausschließlich
Designsystem und Vorlagen frei. Rohdaten, Referenz-Uploads und Git-Dateien werden nicht ausgeliefert.

## Projektstruktur

```text
brand/
  design-system/        Designquellen, Regeln, Komponenten und Vorschauen
    tokens/            design-tokens.json = verbindliche Designwerte
    dist/              erzeugte CSS-, JS-, Font- und Chart-Artefakte
  templates/           PowerPoint-, Word- und Notebook-Vorlagen
  reference/           ursprüngliche Uploads und archivierter Design-Tool-Export
docs/                  Projektunterlagen, Bericht und Präsentationsmaterial
data/raw/              vorhandene Quelldaten (unverändert)
ipynb/                 bisherige Analysen (aktiver Ordner, vorerst unverändert)
notebooks/             neue, reproduzierbare Analysevorlagen
src/energy_analytics/   installierbarer Python-Code
scripts/               reproduzierbare Builds und Vorschau
tests/                 Token-, Kontrast-, Chart- und Browserprüfungen
.github/workflows/     automatisierte Prüfungen bei Push/Pull Request
```

Der bisherige Ordner `ipynb/` war beim Umbau geöffnet und ließ sich nicht umbenennen.
Bestehende Analysen und ihre Ergebnisse bleiben erhalten. Neue Notebooks kommen nach `notebooks/`.
Die vorhandene Datei `data/raw/verbrauch_bereinigt.csv` bleibt aus Kompatibilitätsgründen an ihrem
bisherigen Ort; neue Bereinigungsergebnisse gehören nach `data/processed/`.

## Python einrichten

Python 3.11–3.13. Für die exakt gesperrte Entwicklungsumgebung:

```sh
python -m pip install uv==0.11.13
python -m uv sync --frozen --all-extras
```

Alternativ nur die Notebook-Abhängigkeiten installieren: `python -m pip install -e ".[notebooks,export]"`.
Im Editor die Projektumgebung `.venv` als Python-Interpreter/Notebook-Kernel auswählen.

```python
from energy_analytics.visualization import eda, theme

eda.setup()
fig = eda.timeseries_forecast(
    ["01/2025", "02/2025"], [1200, 1350], [1180, 1320],
    title="Demodaten · Januar–Februar 2025", y_title="Verbrauch (kWh)",
)
fig.show(renderer="notebook")
```

Für Matplotlib: `plt = theme.apply_matplotlib()`. Die mitgelieferten TTF-Schriften werden
für Matplotlib lokal registriert. Für Word, PowerPoint und Kaleido bei Bedarf die TTF-Dateien
aus `brand/design-system/dist/fonts/` im eigenen Betriebssystem installieren.
Eine Installation systemweiter Schriften erfolgt nicht automatisch.

## Design ändern und prüfen

Node-Abhängigkeiten sind in `package-lock.json`, Python-Abhängigkeiten in `uv.lock` gesperrt.

```sh
npm ci
python -m uv run --frozen python scripts/build_tokens.py
npm run build
python -m uv run --frozen python scripts/build_templates.py
python -m uv run --frozen pytest -q
python -m uv run --frozen ruff check src/energy_analytics scripts tests
```

Browserprüfung: lokalen Vorschau-Server starten und in einem zweiten Terminal `npm test` ausführen.
Lokal nutzt der Test Microsoft Edge; in der Linux-CI den mit Playwright installierten Chromium.
Im Browser-Test werden alle externen Netzwerkanfragen blockiert.

Änderungen an generierten Dateien werden beim nächsten Build überschrieben. Farben und
Schriftwerte deshalb ausschließlich in `brand/design-system/tokens/design-tokens.json` pflegen.
Der CI-Workflow prüft mit `scripts/build_tokens.py --check`, ob die Exporte aktuell sind.

## Stand und Grenzen

Das Cockpit ist eine Designreferenz mit synthetischen Beispieldaten. Es gibt keine angebundene
Datenpipeline, Benutzerverwaltung, produktive Prognose oder Ticket-/E-Mail-Integration.
Die bestehenden Notebook-Analysen wurden nicht neu ausgeführt.

Das offizielle Vektorlogo sowie transparente und einfarbige Markenvarianten wurden nicht
mitgeliefert. Originale Rasterlogos werden unverändert verwendet. Details und Zuständigkeiten
stehen in [docs/design-system-handover.md](docs/design-system-handover.md).
