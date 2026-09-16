# EDA-Notebooks

- `eda.ipynb`: Patricks Original, unverändert.
- `eda_ci.ipynb`: eigenständige SWW-Designfassung mit denselben sechs Analyseabschnitten,
  38 ausgeführten Codezellen und 32 neu erzeugten Diagrammen.

## Öffnen und ausführen

Im Projektstamm `python -m uv sync --frozen --all-extras` ausführen. Die Projektumgebung
wird in VS Code als Standard-Interpreter vorgeschlagen. Für einen eindeutig benannten
Notebook-Kernel unter Windows einmal im Projektstamm registrieren:

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --user --name sww-energy-analytics --display-name "Python (SWW .venv)"
```

Auf diesem Rechner ist der Eintrag bereits eingerichtet. Er verweist direkt auf den Python-
Interpreter der Projekt-`.venv`; es werden keine Pakete global installiert. Nach einem
Verschieben des Projektordners muss der Registrierungsbefehl erneut ausgeführt werden.

`eda_ci.ipynb` neu öffnen und oben rechts **Python (SWW .venv)** auswählen, falls noch ein
anderer Kernel aktiv ist; anschließend Kernel neu starten und **Alle ausführen** wählen.
Ein bereits laufender Editor kann seine frühere Auswahl behalten. Die Registrierung folgt
der [IPython-Anleitung](https://ipython.readthedocs.io/en/stable/install/kernel_install.html).
Die [VS-Code-Standardeinstellung](https://code.visualstudio.com/docs/python/settings-reference)
ersetzt keine bereits gespeicherte Kernel-/Interpreterauswahl.

Die erste Codezelle prüft fehlende Pakete vor den Imports und nennt im Fehlerfall den
tatsächlich aktiven Interpreter sowie den richtigen Kernel.
Die gespeicherte Fassung enthält interaktive Plotly-Ausgaben und gerenderte PNG-Vorschauen.
Die PNGs zeigen auch ohne Plotly-Erweiterung den geprüften Stand mit den lokalen SWW-Schriften.
Je nach Notebook-Frontend kann die interaktive Schriftübernahme anders behandelt werden;
die Offline-HTML-Vorschau enthält Fonts und Plotly vollständig eingebettet.

Die Daten kommen unverändert aus `data/raw/verbrauch_bereinigt.csv`. Sentinel-Rekonstruktion
und Plausibilitätsfilter erfolgen wie im Original nur im Arbeitsspeicher. Die übernommenen
Befunde sind keine erneute fachliche Freigabe; Hinweise stehen am Anfang des Notebooks.

## Gestaltung

Verbindliche Quelle: `brand/design-system/tokens/design-tokens.json`.
Das Notebook verwendet die Chart-Bausteine aus `energy_analytics.visualization.eda` und
die Notebook-Darstellung aus `energy_analytics.visualization.notebook`, nicht `viz.py`.
Änderungen an Tokens zuerst mit `python scripts/build_tokens.py` erzeugen, anschließend
den Kernel neu starten und alle Zellen ausführen.

## Ausgaben reproduzieren und prüfen

Aus dem Projektstamm:

```sh
python -m uv run --frozen --all-extras --with nbclient --with nbconvert python scripts/check_eda_ci_notebook.py
node scripts/check_eda_ci_browser.mjs
```

Der erste Schritt führt die vorhandene CI-Fassung in einem frischen Kernel aus, aktualisiert
ihre Ausgaben und erzeugt `.build/eda-ci/eda_ci.html` ohne CDN-Abhängigkeiten. Der zweite
prüft alle 32 Diagramme im Browser mit gesperrten externen Anfragen und ergänzt die PNGs
im Notebook. Lokal wird Microsoft Edge verwendet, in einer CI ein installierter
Playwright-Chromium. Die zusätzlichen Prüfwerkzeuge werden über `uv --with` bereitgestellt;
die Projekt-Lockdatei wird dabei nicht verändert.

`scripts/build_eda_ci_notebook.py` dokumentiert die ursprüngliche Übertragung. Mit `--force`
würde es die CI-Fassung aus Patricks Ausgangsversion neu erzeugen und eigene Änderungen
sowie Ausgaben darin ersetzen. Für die normale Arbeit daher nur das Notebook ausführen.
Keines der Skripte verändert `eda.ipynb`, `viz.py` oder die CSV-Dateien.
