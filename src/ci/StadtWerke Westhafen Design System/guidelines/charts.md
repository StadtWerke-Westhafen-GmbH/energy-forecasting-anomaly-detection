# Charts — Konstruktionsregeln

Charts sind die wichtigste visuelle Fläche dieser Marke. Sie folgen deshalb strengeren Regeln als
alles andere. Implementierung: `assets/plotly/sww_theme.py` (Notebook), `assets/plotly/sww_plotly_template.json`
(JS), `assets/plotly/sww_matplotlib.mplstyle` (statische Report-Grafiken),
`ui_kits/energie-cockpit/Chart.jsx` (Dashboard).

## Feste Farbrollen

| Rolle | Farbe | Darstellung |
| --- | --- | --- |
| Ist (realisiert) | `--data-actual` #084878 | durchgezogen, 2 px, Marker 6 px |
| Prognose (Modell) | `--data-forecast` #0090C8 | gestrichelt `4 2`, 2 px, keine Marker |
| Konfidenzband | `--data-band` cyan 16 % | Fläche, keine Kontur |
| Residuum | `--data-residual` #0080A0 | Balken |
| Schwellwert | `--data-threshold` #C77E11 | 1 px gepunktet `3 3` + Annotation |
| Anomalie | `--data-anomaly` #B3261E | gefüllter Marker 9 px, weiße Kontur 1,5 px |
| Kundentyp | Gewerbe #0080A0 · Industrie #084878 · Kommunal #58A858 | nie neu zuordnen |

Cyan bedeutet **immer** Modellausgabe. Wird Cyan für UI-Chrome verwendet, verliert die Konvention
ihren Wert — deshalb ist Cyan außerhalb von Charts verboten.

## Balken

- Balkenenden **abgerundet** (`barcornerradius: 4`, Token `--chart-bar-radius`), Balkenabstand 36 %
  (`bargap: 0.36`) — Balken lesen sich als Stäbe, nicht als Fläche.
- **Überlagerte Verteilungen** (Histogramme je Kundentyp) mit 62 % Deckkraft (`--chart-overlay-opacity`),
  `barmode="overlay"`; die Mischfarben in der Überlappung sind gewollt.
- Schiefe Verteilungen (Verbrauch über drei Größenordnungen) auf **log-Achse** mit echten Einheiten
  als Tick-Beschriftung (`1.000 · 3.000 · 10.000 …`) — `histogram(..., log_x=True)`.

## Achsen und Raster

- Nur **horizontale** Gridlines, `--data-grid` #E4E9EF, 1 px. Keine vertikalen, kein Rahmen.
- X-Achse mit 1 px Linie #E4E9EF und Ticks außen; Y-Achse ohne Linie.
- Achsenbeschriftungen in IBM Plex Sans 11 px `--grey-500`, tabellarische Ziffern. **Keine Monospace in
  Charts** — Geist Mono bleibt der UI (IDs, Kennzahlen-Kacheln, Tabellen), Diagramme laufen in einer Schrift. Achsentitel mit Einheit in Klammern:
  `Verbrauch (kWh)`, `Temperatur (°C)`, `Residuum (kWh)`.
- Kein `range`-Trick, der die Null abschneidet, wenn Balken verglichen werden.

## Titel, Legende, Labels

- Charttitel linksbündig (x = 0), 15 px Semibold. Im Dashboard trägt die `Card` den Titel, der Chart
  selbst bleibt titellos.
- Legende horizontal über dem Plot, ohne Rahmen. Bei ≤ 3 Serien besser die Linie direkt am Ende
  beschriften und die Legende weglassen.
- Zahlen im Chart mit `separators=",."` — `1.284.500`, `12,4`. Zusätzlich auf jeder
  Wertachse `tickformat=",d"` und `separatethousands=True` setzen: ohne das fällt Plotly auf die
  englische SI-Kurzform zurück und beschriftet die Achse mit `17k` statt `17.000`.
- Hover: weißer Grund, Rahmen #E4E9EF, Plex Sans 12 px, `hovermode="x unified"`.

## Chart-Typen je Frage

| Frage | Chart |
| --- | --- |
| Prognose vs. Ist über Zeit | Linie (Ist) + gestrichelte Linie (Prognose) + Band |
| Residuen pro Monat | Balken, zweiseitiger Schwellwert als gepunktete Linien, Überschreitungen rot |
| Verbrauch nach Kundentyp | Balken in Kundentyp-Farben, keine Legende |
| Saisonalität | Heatmap Monat × Kundentyp, sequentielle Navy-Skala |
| Über-/Unterverbrauch | Diverging-Skala teal → grau → rot, Mittelpunkt exakt 0 |
| Feature Importance | Horizontale Balken, sortiert, Werte außen als Label (Plex Sans) |
| Temperaturabhängigkeit | Scatter mit Trendlinie, Punkte nach Kundentyp gefärbt |

## Was nicht vorkommt

Keine Tortendiagramme. Keine 3D-Achsen. Keine Doppel-Y-Achsen. Keine Verlaufsfüllungen unter
Linien (nur das Konfidenzband). Keine Animation beim Re-Render (nur 420 ms Erstzeichnung).
Keine Datenbeschriftung an jedem Punkt — nur am Extremwert oder am Ende der Serie.
