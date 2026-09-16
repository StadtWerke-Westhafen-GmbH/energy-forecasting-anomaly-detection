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
Anschließend lädt sie `theme`, `eda` und `notebook` gezielt neu, damit ein bereits laufender
Kernel auch Änderungen an der Design-API übernimmt. Das verhindert beispielsweise
`aktiviere() got an unexpected keyword argument 'logo'` durch einen alten Import im Speicher.
Nach einem Update die Datei neu öffnen und **Alle ausführen** starten; ein vollständiger
Kernel-Neustart bleibt bei Änderungen an installierten Paketen sinnvoll.
Die gespeicherte Fassung enthält interaktive Plotly-Ausgaben. Der Browser-Prüfschritt unten
ergänzt PNG-Vorschauen, die beim erneuten Ausführen im Notebook wieder entfallen können.
Die optionalen PNGs zeigen auch ohne Plotly-Erweiterung den geprüften Stand mit den lokalen SWW-Schriften.
Je nach Notebook-Frontend kann die interaktive Schriftübernahme anders behandelt werden;
die Offline-HTML-Vorschau enthält Fonts und Plotly vollständig eingebettet.

Beim Speichern darf der Editor den Kernel-Namen und Anzeigenamen an die lokale Umgebung
anpassen, etwa auf `python3` und `westhafen-energy-analytics (3.11.9)`. Der automatisierte
Test prüft deshalb Python als Sprache, alle 32 interaktiven Diagramme und ihre SWW-Gestaltung,
nicht den rechnerabhängigen Kernel-Namen. Vorhandene PNG-Vorschauen werden ebenfalls geprüft;
für reine Notebook-Ausführung sind sie nicht erforderlich. Ob die benötigten Pakete im
aktiven Interpreter verfügbar sind, prüft weiterhin die erste Codezelle.

Die Daten kommen unverändert aus `data/raw/verbrauch_bereinigt.csv`. Sentinel-Rekonstruktion
und Plausibilitätsfilter erfolgen wie im Original nur im Arbeitsspeicher. Die übernommenen
Befunde sind keine erneute fachliche Freigabe; Hinweise stehen am Anfang des Notebooks.

## Gestaltung

Verbindliche Quelle: `brand/design-system/tokens/design-tokens.json`.
Das Notebook verwendet die Chart-Bausteine aus `energy_analytics.visualization.eda` und
die Notebook-Darstellung aus `energy_analytics.visualization.notebook`, nicht `viz.py`.
Änderungen an Tokens zuerst mit `python scripts/build_tokens.py` erzeugen, anschließend
den Kernel neu starten und alle Zellen ausführen.

Der Bericht verwendet ein Navy-Cover mit dem originalen Vollsignet, drei aus den Daten
berechnete Kennzahlen und sechs nummerierte Kapitelauftakte. Diagramme haben kräftigere
Navy-Titel sowie eine eigene Fußzeile mit Quelle, Zeitraum und kleinem originalem SWW-Emblem
ohne ausgeschriebenen Firmennamen. Die Bildmarke sitzt dezent unten rechts (36 px hoch),
während das vollständige Signet auf dem Cover bleibt.
Das Logo ist als lokale PNG-Daten-URI direkt in Plotly eingebettet: Es bleibt in einzelnen
Diagrammexporten erhalten und überdeckt keine Daten. Es wird weder verändert noch nachgebaut.
IBM Plex Sans bleibt die einzige Diagrammschrift; Geist Mono akzentuiert nur die Cover-Kennzahlen.
Die Offline-HTML-Fassung beginnt mit dem Cover und bietet Sprunglinks zu den sechs Abschnitten.
SWW-Tabellen behalten auch in dunklen Notebook-Themes ihre deckenden hellen Datenzellen
und dunkle Schrift. Kopf- und Indexzellen bleiben Navy mit weißer Schrift; Streifen und
Hover verwenden feste CI-Farben. Diese Regeln sind auf `.sww-table` begrenzt und verändern
nicht das Editor-Theme. Der Browsercheck prüft die gespeicherte Tabellenausgabe isoliert
auf hellem und dunklem Hintergrund, einschließlich Hover-Zustand.

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
