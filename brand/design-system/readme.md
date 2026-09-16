# SWW Designsystem

Gemeinsame Gestaltung für Westhafen Energy Analytics. Die vorhandene Markenrichtung bleibt:
Hafen-Navy, Elbe-Teal, klare Typografie und fachlich eindeutige Diagramme.

## Einstieg

Vom Repository-Stamm `node scripts/preview.mjs` starten und http://127.0.0.1:4173 öffnen.
Alle Schriften, Icons und Skripte kommen vom lokalen Server. Die Vorschau funktioniert nach
dem Checkout auch ohne `npm install`, weil die geprüften Browserartefakte mitgeliefert werden.

- [Gestaltungsregeln](guidelines/brand-guide.md)
- [Diagrammregeln](guidelines/charts.md)
- [Präsentationen](guidelines/slides.md)
- [Startseite](index.html)
- [Energie-Cockpit](ui_kits/energie-cockpit/index.html)
- [Diagrammgalerie](templates/eda-charts/index.html)
- [Vorlagen](../templates/README.md)

## Verbindliche Werte

`tokens/design-tokens.json` ist die Quelle für Farben, Schriften, Abstände, Radien,
Schatten und semantische Rollen. JSON wurde bewusst gewählt: Python und JavaScript können
es ohne zusätzliche Parser lesen. Verweise zwischen Werten werden beim Build aufgelöst;
fehlende Werte und Zyklen sind Fehler.

`python scripts/build_tokens.py` erzeugt CSS, JavaScript, Plotly-JSON, Matplotlib-Style und
Python-Ressourcen. Die Dateien in `tokens/*.css` sind nur Kompatibilitätseinstiege.

| Inhalt | Ort |
| --- | --- |
| Designwerte | `tokens/design-tokens.json` |
| Allgemeine Elementregeln | `tokens/base.css` |
| React-Komponenten und Verträge | `components/` |
| Browser-Chartfunktionen | `assets/plotly/sww_plotly.js` |
| Python-Chartfunktionen | `src/energy_analytics/visualization/` im Repository |
| Erzeugte Browserartefakte | `dist/` |
| Markenassets | `assets/` |
| Ursprünglicher Tool-Export | `../reference/export/` |
| Office-/Notebook-Vorlagen | `../templates/` |

## Entwicklung

Vom Repository-Stamm:

```sh
python -m uv sync --frozen --all-extras
npm ci
python -m uv run --frozen python scripts/build_tokens.py
npm run build
python -m uv run --frozen python scripts/build_templates.py
```

Webseiten binden `styles.css` ein. Chartseiten laden zusätzlich `dist/vendor/plotly.min.js`,
`dist/js/tokens.js` und `assets/plotly/sww_plotly.js` in dieser Reihenfolge.

JSX wird beim Build übersetzt; Babel und CDN-Skripte werden nicht mehr im Browser benötigt.
React-Vorschauen teilen sich `dist/js/runtime.js` und `dist/js/components.js`.
Die Dateien `*.preview.jsx` enthalten die Einstiegspunkte ihrer HTML-Vorschauen.

In Python:

```python
from energy_analytics.visualization import eda, theme
eda.setup()
```

Keine `sys.path`-Anpassung erforderlich. Die früheren `sww_theme`-/`sww_eda`-Dateien sind
Kompatibilitätsimporte für eine bereits installierte Projektumgebung.

## Qualität und Herkunft

Kontrastpaare werden gegen 4,5:1 für kleinen Text geprüft. Dies ist keine pauschale
Barrierefreiheitszertifizierung. Tastaturbedienung, Skalierung und Inhalte müssen auch
in einer späteren Produktanwendung geprüft werden.

Fonts und Icons werden aus fest versionierten npm-Paketen übernommen; Lizenztexte liegen in
`dist/licenses/`. Die TTF-Schriften sind verlustfreie Containerkonvertierungen der
mitgelieferten WOFF2-Dateien. Markenrechte an SWW-Assets werden dadurch nicht neu vergeben.

Der ursprüngliche Markenentwurf wurde aus dem Rasterlogo und der IHK-Aufgabenstellung abgeleitet.
Das ursprüngliche Konzept ist als historische Referenz in
`../reference/export/original-design-guide.md` erhalten. Aktuelle Regeln stehen in `guidelines/`.
