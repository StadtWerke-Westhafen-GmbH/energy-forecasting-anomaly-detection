"""SWW EDA chart library — Python twin of assets/plotly/sww_plotly.js.

Every function returns a plotly.graph_objects.Figure styled with the SWW template.
Import sww_theme first (same folder) or call sww_eda.setup().

    import sww_eda
    sww_eda.setup()                                   # registers + activates template "sww"
    fig = sww_eda.timeseries_forecast(df["monat"], df["ist"], df["prognose"], lo, hi)
    fig.show()

Typography: one family (IBM Plex Sans, tabular figures) for every axis, label and hover — never monospace.
Colour roles are fixed (see guidelines/charts.md):
    Ist navy · Prognose cyan dashed · Band cyan 16 % · Schwellwert amber dotted · Anomalie red
    Gewerbe teal · Industrie navy · Kommunal green
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

try:
    import sww_theme as T
except ImportError:  # allow running from another working directory
    import importlib.util, os
    _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sww_theme.py")
    _s = importlib.util.spec_from_file_location("sww_theme", _p)
    T = importlib.util.module_from_spec(_s); _s.loader.exec_module(T)

ROLE = T.ROLE
KT = T.KUNDENTYP_COLORS
SEQ = T.SEQUENTIAL
DIV = T.DIVERGING
GREY_100, GREY_300, GREY_500, GREY_600 = T.GREY_100, "#B4BFCB", T.GREY_500, "#4E5A68"
LABEL_FONT = dict(family=T.FONT, size=11, color=GREY_600)  # one family everywhere in charts


def setup():
    """Register and activate the SWW Plotly template."""
    return T.register(activate=True)


def _scale(colors):
    n = len(colors) - 1
    return [[i / n, c] for i, c in enumerate(colors)]


def _kt_color(name):
    return KT.get(name)


def _fmt_de(v, nd=0):
    s = f"{v:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# 01 ---------------------------------------------------------------------------
def timeseries_forecast(x, ist, prognose=None, lo=None, hi=None, anomalien=None,
                        y_title="Verbrauch (kWh)", title=None):
    """Ist (navy) vs Prognose (cyan dashed) with optional band and anomaly markers.
    anomalien: (x_values, y_values) tuple."""
    fig = go.Figure()
    x = list(x)
    if lo is not None and hi is not None:
        fig.add_trace(go.Scatter(x=x + x[::-1], y=list(hi) + list(lo)[::-1], fill="toself",
                                 fillcolor=ROLE["band"], line=dict(width=0), hoverinfo="skip",
                                 name="Konfidenzband"))
    fig.add_trace(go.Scatter(x=x, y=ist, name="Ist", mode="lines+markers",
                             line=dict(color=ROLE["ist"], width=2), marker=dict(size=5)))
    if prognose is not None:
        fig.add_trace(go.Scatter(x=x, y=prognose, name="Prognose", mode="lines",
                                 line=dict(color=ROLE["prognose"], width=2, dash="4,2")))
    if anomalien is not None:
        ax, ay = anomalien
        fig.add_trace(go.Scatter(x=ax, y=ay, name="Anomalie", mode="markers",
                                 marker=dict(size=9, color=ROLE["anomalie"], line=dict(width=1.5, color="#fff"))))
    fig.update_layout(title=title, yaxis_title=y_title, xaxis_title=None, xaxis=dict(nticks=6, tickangle=0))
    return fig


# 02 ---------------------------------------------------------------------------
def seasonality(monate, series: dict, y_title="Ø Verbrauch (kWh)", title=None):
    """series = {"Gewerbe": [12 values], ...} — monthly means per group."""
    fig = go.Figure()
    for k, v in series.items():
        fig.add_trace(go.Scatter(x=monate, y=v, name=k, mode="lines+markers",
                                 line=dict(color=_kt_color(k), width=2), marker=dict(size=5)))
    fig.update_layout(title=title, yaxis_title=y_title)
    return fig


# 03 ---------------------------------------------------------------------------
def histogram(groups: dict, x_title="Verbrauch (kWh)", nbins=40, log_x=False, title=None):
    """Overlaid, semi-transparent histograms per group (rounded bars via the template).
    log_x=True bins on log10 and labels the axis in real units — use for skewed consumption."""
    fig = go.Figure()
    for k, v in groups.items():
        x = np.log10(np.clip(np.asarray(v, float), 1, None)) if log_x else v
        fig.add_trace(go.Histogram(x=x, name=k, nbinsx=nbins, opacity=0.62, marker_color=_kt_color(k)))
    xaxis = (dict(title=x_title, tickvals=[3, 3.5, 4, 4.5, 5, 5.5, 6],
                  ticktext=["1.000", "3.000", "10.000", "30.000", "100.000", "300.000", "1 Mio."])
             if log_x else dict(title=x_title, tickformat=",d"))
    fig.update_layout(title=title, barmode="overlay", bargap=0.3, xaxis=xaxis, yaxis_title="Anzahl Zähler",
                      hovermode="closest")
    return fig


# 04 ---------------------------------------------------------------------------
def boxplot(groups: dict, y_title="Verbrauch (kWh)", title=None):
    fig = go.Figure()
    for k, v in groups.items():
        fig.add_trace(go.Box(y=v, name=k, marker=dict(color=_kt_color(k), size=3), line=dict(width=1.5),
                             boxpoints="outliers", fillcolor="rgba(255,255,255,0)"))
    fig.update_layout(title=title, showlegend=False, yaxis_title=y_title, hovermode="closest",
                      xaxis_showline=False)
    return fig


# 05 ---------------------------------------------------------------------------
def scatter_trend(groups: dict, x_title="Mitteltemperatur (°C)", y_title="Verbrauch (kWh)", title=None):
    """groups = {"Gewerbe": (x_array, y_array), ...}; adds a dashed OLS line per group."""
    fig = go.Figure()
    for k, (x, y) in groups.items():
        x, y = np.asarray(x, float), np.asarray(y, float)
        fig.add_trace(go.Scatter(x=x, y=y, name=k, mode="markers",
                                 marker=dict(size=6, color=_kt_color(k), opacity=0.75)))
        if len(x) > 1:
            b, a = np.polyfit(x, y, 1)
            xs = np.array([x.min(), x.max()])
            fig.add_trace(go.Scatter(x=xs, y=a + b * xs, mode="lines", showlegend=False, hoverinfo="skip",
                                     line=dict(color=_kt_color(k) or T.GREY_400, width=1.5, dash="3,3")))
    fig.update_layout(title=title, hovermode="closest", xaxis_title=x_title, yaxis_title=y_title,
                      xaxis=dict(showgrid=True, gridcolor=GREY_100))
    return fig


# 06 ---------------------------------------------------------------------------
def heatmap(x, y, z, z_title="kWh", title=None):
    """Sequential navy heatmap, e.g. Monat × Kundentyp."""
    fig = go.Figure(go.Heatmap(x=x, y=y, z=z, colorscale=_scale(SEQ), xgap=2, ygap=2,
                               colorbar=dict(title=dict(text=z_title, font=dict(size=11, color=GREY_500)),
                                             thickness=10, len=0.8, outlinewidth=0, tickformat=",d",
                                             tickfont=dict(family=T.FONT, size=10, color=GREY_500)),
                               hovertemplate="%{y} · %{x}<br>%{z:,d} " + z_title + "<extra></extra>"))
    fig.update_layout(title=title, hovermode="closest", xaxis=dict(showline=False, ticks=""),
                      yaxis=dict(showgrid=False, ticks="", tickformat="", automargin=True), margin=dict(l=20, r=10))
    return fig


# 07 ---------------------------------------------------------------------------
def correlation(corr_df, title=None, show_text=True):
    """Diverging correlation matrix from a pandas DataFrame (df.corr()).
    show_text=False for narrow panels (< ~700 px) — values stay available in the hover."""
    labels = list(corr_df.columns)
    z = corr_df.values
    text = [[_fmt_de(v, 2) for v in row] for row in z]
    fig = go.Figure(go.Heatmap(x=labels, y=labels, z=z, colorscale=_scale(DIV), zmin=-1, zmax=1, zmid=0,
                               text=text, texttemplate="%{text}" if show_text else None, textfont=dict(family=T.FONT, size=10),
                               xgap=2, ygap=2,
                               colorbar=dict(thickness=10, len=0.8, outlinewidth=0,
                                             tickfont=dict(family=T.FONT, size=10, color=GREY_500)),
                               hovertemplate="%{y} × %{x}<br>r = %{z:.2f}<extra></extra>"))
    fig.update_layout(title=title, hovermode="closest",
                      xaxis=dict(showline=False, ticks="", tickangle=-35, automargin=True, tickfont=dict(size=10)),
                      yaxis=dict(showgrid=False, ticks="", tickformat="", autorange="reversed", automargin=True, tickfont=dict(size=10)),
                      margin=dict(l=20, b=20, r=10))
    return fig


# 08 ---------------------------------------------------------------------------
def residual_hist(residuen, schwelle, x_title="Residuum (kWh)", nbins=40, title=None):
    fig = go.Figure(go.Histogram(x=residuen, nbinsx=nbins, marker_color=ROLE["residuum"], name="Residuen"))
    for s in (-1, 1):
        fig.add_vline(x=s * schwelle, line=dict(color=ROLE["schwellwert"], width=1, dash="3,3"))
    fig.add_annotation(x=schwelle, y=1, yref="paper", text=f"Schwellwert ±{_fmt_de(schwelle)}", showarrow=False,
                       xanchor="left", yanchor="top", font=dict(size=11, color=ROLE["schwellwert"]))
    fig.update_layout(title=title, showlegend=False, hovermode="closest", yaxis_title="Anzahl",
                      xaxis=dict(title=x_title, tickformat=",d", zeroline=True, zerolinecolor=GREY_300))
    return fig


# 09 ---------------------------------------------------------------------------
def residual_bars(x, residuen, schwelle, y_title="Residuum (kWh)", title=None):
    r = np.asarray(residuen, float)
    colors = np.where(np.abs(r) > schwelle, ROLE["anomalie"], ROLE["residuum"])
    fig = go.Figure(go.Bar(x=list(x), y=r, marker_color=list(colors), name="Residuum"))
    for s in (-1, 1):
        fig.add_hline(y=s * schwelle, line=dict(color=ROLE["schwellwert"], width=1, dash="3,3"))
    fig.update_layout(title=title, showlegend=False, xaxis=dict(nticks=6, tickangle=0),
                      yaxis=dict(title=y_title, zeroline=True, zerolinecolor=GREY_300))
    return fig


def _wrap_label(s, max_len=24):
    """Break long snake_case labels once at the underscore nearest the middle."""
    s = str(s)
    if len(s) <= max_len or "_" not in s:
        return s
    mid = len(s) // 2
    cut = min((i for i, ch in enumerate(s) if ch == "_"), key=lambda i: abs(i - mid))
    return s[: cut + 1] + "<br>" + s[cut + 1 :]


# 10 ---------------------------------------------------------------------------
def feature_importance(features, values, x_title="Anteil", title=None):
    order = np.argsort(values)
    f = [_wrap_label(features[i]) for i in order]
    v = [float(values[i]) for i in order]
    fig = go.Figure(go.Bar(y=f, x=v, orientation="h", marker_color=ROLE["ist"],
                           text=[_fmt_de(x, 3) for x in v], textposition="outside", textfont=LABEL_FONT, cliponaxis=False))
    fig.update_layout(title=title, showlegend=False, hovermode="closest",
                      xaxis=dict(title=x_title, showgrid=True, gridcolor=GREY_100, showline=False, tickformat=",.2f"),
                      yaxis=dict(showgrid=False, tickformat="", automargin=True, tickfont=LABEL_FONT), margin=dict(l=20, r=50))
    return fig


# 11 ---------------------------------------------------------------------------
def missing_values(columns, pct, title="Anteil fehlerhaft/fehlend (%)"):
    """Horizontal bars of error/missing share per column; ≥5 % red, ≥1 % amber."""
    cols, p = [_wrap_label(c) for c in list(columns)[::-1]], [float(v) for v in pct][::-1]
    colors = [ROLE["anomalie"] if v >= 5 else ROLE["schwellwert"] if v >= 1 else GREY_300 for v in p]
    fig = go.Figure(go.Bar(y=cols, x=p, orientation="h", marker_color=colors,
                           text=[_fmt_de(v, 1) + " %" for v in p], textposition="outside", textfont=LABEL_FONT, cliponaxis=False))
    fig.update_layout(showlegend=False, hovermode="closest",
                      xaxis=dict(title=title, showgrid=True, gridcolor=GREY_100, showline=False, tickformat=",.0f", ticksuffix=" %"),
                      yaxis=dict(showgrid=False, tickformat="", automargin=True, tickfont=LABEL_FONT), margin=dict(l=20, r=60))
    return fig


# 12 ---------------------------------------------------------------------------
def parity(ist, prognose, anomalie=None, x_title="Prognose (kWh)", y_title="Ist (kWh)", title=None):
    """One point per meter; distance to the diagonal is the error, red = anomaly."""
    ist, prognose = np.asarray(ist, float), np.asarray(prognose, float)
    mn, mx = min(ist.min(), prognose.min()), max(ist.max(), prognose.max())
    colors = ROLE["ist"] if anomalie is None else np.where(np.asarray(anomalie, bool), ROLE["anomalie"], ROLE["ist"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode="lines", name="Ist = Prognose", hoverinfo="skip",
                             line=dict(color=GREY_300, width=1, dash="4,4")))
    fig.add_trace(go.Scatter(x=prognose, y=ist, mode="markers", name="Zähler",
                             marker=dict(size=6, color=colors, opacity=0.8)))
    fig.update_layout(title=title, hovermode="closest", showlegend=False, yaxis_title=y_title,
                      xaxis=dict(title=x_title, tickformat=",d", showgrid=True, gridcolor=GREY_100))
    return fig


# 13 ---------------------------------------------------------------------------
def anomaly_stack(x, series: dict, title=None):
    """Anomalies per month, stacked by Kundentyp."""
    fig = go.Figure()
    for k, v in series.items():
        fig.add_trace(go.Bar(x=list(x), y=v, name=k, marker_color=_kt_color(k)))
    fig.update_layout(title=title, barmode="stack", yaxis_title="Anomalien", xaxis=dict(nticks=6, tickangle=0))
    return fig


# 14 ---------------------------------------------------------------------------
def top_n(labels, values, x_title="Verbrauch (kWh)", title=None):
    order = np.argsort(values)
    l = [labels[i] for i in order]
    v = [float(values[i]) for i in order]
    fig = go.Figure(go.Bar(y=l, x=v, orientation="h", marker_color=ROLE["ist"],
                           text=[_fmt_de(x) for x in v], textposition="outside", textfont=LABEL_FONT, cliponaxis=False))
    fig.update_layout(title=title, showlegend=False, hovermode="closest",
                      xaxis=dict(title=x_title, showgrid=True, gridcolor=GREY_100, showline=False, tickformat=",d"),
                      yaxis=dict(showgrid=False, tickformat="", automargin=True, tickfont=LABEL_FONT), margin=dict(l=20, r=70))
    return fig


# 15 ---------------------------------------------------------------------------
def share_area(x, series: dict, y_title="Anteil", title=None):
    """100 %-stacked area — share of each Kundentyp over time."""
    fig = go.Figure()
    for k, v in series.items():
        fig.add_trace(go.Scatter(x=list(x), y=v, name=k, mode="lines", stackgroup="one", groupnorm="percent",
                                 line=dict(width=0.5, color=_kt_color(k)), fillcolor=_kt_color(k)))
    fig.update_layout(title=title, yaxis=dict(title=y_title, ticksuffix=" %", tickformat=",.0f"), xaxis=dict(nticks=6, tickangle=0))
    return fig


# Convenience ------------------------------------------------------------------
def by_kundentyp(df, value_col, type_col="kundentyp"):
    """{Kundentyp: Series} in the fixed brand order — feed into histogram/boxplot."""
    return {k: df.loc[df[type_col] == k, value_col].dropna().values for k in ("Gewerbe", "Industrie", "Kommunal") if (df[type_col] == k).any()}


def save_for_slide(fig, path, width=1120, height=560, scale=2):
    """Export a chart PNG sized for the 1280×720 chart slide (needs kaleido)."""
    fig.update_layout(font_size=17, legend_font_size=17, xaxis_tickfont_size=15, yaxis_tickfont_size=15)
    fig.write_image(path, width=width, height=height, scale=scale)
    return path


__all__ = [
    "setup", "timeseries_forecast", "seasonality", "histogram", "boxplot", "scatter_trend", "heatmap",
    "correlation", "residual_hist", "residual_bars", "feature_importance", "missing_values", "parity",
    "anomaly_stack", "top_n", "share_area", "by_kundentyp", "save_for_slide",
]
