# Chart-Themes verwenden

Aktuelle Python-Implementierung: `src/energy_analytics/visualization/` im Repository.
Nach `python -m pip install -e ".[notebooks,export]"`:

```python
from energy_analytics.visualization import eda, theme
eda.setup()
```

`eda` bietet 15 Diagrammtypen, `by_kundentyp()` und `save_for_slide()`.
`theme` bietet das Plotly-Template, feste Farben, Matplotlib-Stil und Notebook-Font-CSS.
`sww_eda.py` und `sww_theme.py` in diesem Ordner sind reine Kompatibilitätsimporte.

`sww_plotly.js` bietet dieselben Diagrammtypen im Browser. Vorher das lokale Plotly
und `../../dist/js/tokens.js` laden. Farben und das gemeinsame Layout werden daraus gelesen.

`sww_plotly_template.json` und `sww_matplotlib.mplstyle` werden beim Build aus
`dist/plotly/template.json` und `dist/matplotlib/sww.mplstyle` kopiert.
JSON-Nutzung: `Plotly.newPlot(el, data, {template: swwTemplate})`.

[Diagrammregeln](../../guidelines/charts.md) · [Interaktive Galerie](../../templates/eda-charts/index.html)
