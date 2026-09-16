# Plotly & Matplotlib theming

Four artefacts, one palette — identical to `tokens/charts.css`.

- `sww_eda.py` — **the EDA chart library for notebooks**: 15 ready figures (`timeseries_forecast`,
  `seasonality`, `histogram`, `boxplot`, `scatter_trend`, `heatmap`, `correlation`, `residual_hist`,
  `residual_bars`, `feature_importance`, `missing_values`, `parity`, `anomaly_stack`, `top_n`,
  `share_area`) plus `by_kundentyp()` and `save_for_slide()`. Each returns a `go.Figure`.
- `sww_plotly.js` — the same 15 builders for the browser (`window.SWW.*`), used by the Design-System
  cards, the dashboard and the `templates/eda-charts` gallery. `SWW.GALLERY` lists them with demo data.

- `sww_theme.py` — Plotly template + Matplotlib rcParams + helpers (`forecast_traces`,
  `anomaly_markers`, `threshold_line`) and the fixed `KUNDENTYP_COLORS` mapping.
- `sww_plotly_template.json` — the same Plotly template as plain JSON, for JS dashboards:
  `Plotly.newPlot(el, data, {template: swwTemplate.layout.template})` or merge into layout.
- `sww_matplotlib.mplstyle` — `plt.style.use("sww_matplotlib.mplstyle")`.

## Notebook quickstart

```python
import sys; sys.path.append("design_system/assets/plotly")   # path to this folder in your repo
import sww_eda
sww_eda.setup()

sww_eda.histogram(sww_eda.by_kundentyp(df, "verbrauch_kwh")).show()
sww_eda.scatter_trend({k: (g["mittlere_temperatur_c"], g["verbrauch_kwh"])
                       for k, g in df.groupby("kundentyp")}).show()
sww_eda.correlation(df[num_cols].corr()).show()
fig = sww_eda.residual_bars(test["monat"], test["residuum"], schwelle=p95)
sww_eda.save_for_slide(fig, "figs/residuen.png")                  # 1120×560 @2x for the chart slide
```

Lower-level helpers (`sww_theme.forecast_traces`, `anomaly_markers`, `threshold_line`) remain
available when a chart is not covered.

```python
import sww_theme, plotly.express as px
sww_theme.register()

fig = px.bar(df, x="kundentyp", y="verbrauch_kwh",
             color="kundentyp", color_discrete_map=sww_theme.KUNDENTYP_COLORS,
             title="Monatsverbrauch nach Kundentyp")
fig.update_layout(showlegend=False, yaxis_title="Verbrauch (kWh)", xaxis_title=None)
fig.show()
```

```python
import plotly.graph_objects as go
fig = go.Figure(sww_theme.forecast_traces(monate, ist, prognose, lower, upper))
fig.add_trace(sww_theme.anomaly_markers(anom_monate, anom_werte))
fig.update_layout(title="Prognose vs. Ist — ZW-04412", yaxis_title="Verbrauch (kWh)")
```

## Non-negotiables

1. **Ist = navy solid, Prognose = cyan dashed `4,2`, Band = cyan 16 %, Schwellwert = amber dotted,
   Anomalie = red marker.** Never swap these.
2. Horizontal gridlines only; no plot border; no vertical grid.
3. `separators=",."` so numbers read German (`1.284.500`, `12,4`), **plus** `tickformat=",d"` and
   `separatethousands=True` on value axes — without them Plotly prints `17k` instead of `17.000`.
4. Axis titles carry units in brackets: `Verbrauch (kWh)`, `Temperatur (°C)`.
5. Left-aligned titles at x=0. No centred chart titles.
6. Legend above the plot, horizontal, no frame — or drop it and label lines directly when ≤3 series.
7. Export figures for slides at `scale=2`, width 1120, height 560 (fits the 1280×720 chart slide) —
   `sww_eda.save_for_slide()` does this and bumps fonts to slide size.
8. Month axes stay horizontal and let Plotly thin the labels (`nticks=6, tickangle=0`) — never rotated labels.
9. Correlation matrices show values in-cell only from ~700 px width (`show_text`), otherwise hover.
