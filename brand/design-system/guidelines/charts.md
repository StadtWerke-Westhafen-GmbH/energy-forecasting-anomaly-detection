# Diagramme · SWW

Die Theme-Werte stammen aus `tokens/design-tokens.json`. Python nutzt
`energy_analytics.visualization`, der Browser `assets/plotly/sww_plotly.js`.

## Feste Rollen

| Bedeutung | Token | Zusätzliche Erkennung |
| --- | --- | --- |
| Ist | `data-actual` | durchgezogene Linie |
| Prognose | `data-forecast` | gestrichelt 4,2 |
| Prognoseintervall | `data-band` | transparente Fläche, explizites Label |
| Residuum | `data-residual` | Balken, Nulllinie |
| Schwellwert | `data-threshold` | gepunktet 3,3 und Beschriftung |
| Anomalie | `data-anomaly` | Marker bzw. hervorgehobener Balken + Text |

Kundentypfarben sind fest: Gewerbe `chart-gewerbe`, Industrie `chart-industrie`,
Kommunal `chart-kommunal`. Der kategoriale Farbzyklus reserviert Rot/Amber und Prognose-Cyan
für ihre fachlichen Rollen. Bei vielen Gruppen auch Labels, Muster oder getrennte Panels einsetzen.

## Schrift, Achsen und Zahlen

IBM Plex Sans für alle Charttexte. Einheiten in Achsentiteln, Zeitraum im Titel oder Untertitel.
Standardmäßig horizontales Raster. Horizontale Balken dürfen ein vertikales Werteraster nutzen;
Scatterplots bei Bedarf beide Richtungen. Ein Raster soll den Wertvergleich unterstützen.

Zahlen mit Dezimalkomma und Tausenderpunkt. Standard `separators=",."`, `tickformat=",~g"`.
Für Zählwerte kann `,d` verwendet werden; für Korrelationen, Anteile und andere Dezimalwerte
keine pauschale Ganzzahlformatierung erzwingen. Monatsbeschriftungen horizontal ausdünnen.

Titel linksbündig, Legende oben oder direkte Serienbeschriftung. Keine 3D-Effekte, Doppel-Y-Achsen
oder dekorativen Verläufe. Balkenvergleiche beginnen bei Null. Logarithmische Skalen ausdrücklich
kennzeichnen und ungültige Werte nicht ohne fachliche Begründung umdeuten.

## Unsicherheit

Intervallmethode und Abdeckungsniveau müssen fachlich belegt werden. Die transparente Fläche
im Mock-up ist lediglich eine Illustration. Ein Prognoseintervall für neue Beobachtungen ist
nicht mit einem Konfidenzintervall des erwarteten Mittelwerts gleichzusetzen.
Anomalieschwellwerte auf Trainings-/Validierungsdaten kalibrieren, nicht auf dem späteren Testset.

## Nutzung

```python
from energy_analytics.visualization import eda
eda.setup()
fig = eda.timeseries_forecast(monate, ist, prognose, title="Zeitraum", y_title="Verbrauch (kWh)")
fig.show(renderer="notebook")
```

```javascript
// Plotly, dist/js/tokens.js und assets/plotly/sww_plotly.js zuvor lokal laden.
SWW.render(element, SWW.GALLERY[0].build(SWW.demo()));
```

Für Folien `eda.save_for_slide(fig, "prognose.png")` verwenden. Der Export verändert die
Notebook-Figur nicht. Er setzt größere Schrift und benötigt Kaleido/Chrome.
Diagramme auf der Folie nicht so weit verkleinern, dass Achsen unlesbar werden.
