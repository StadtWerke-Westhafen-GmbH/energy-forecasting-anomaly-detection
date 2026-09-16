"""Notebook presentation helpers using only the canonical SWW theme.

The EDA builders remain the first choice for charts. These helpers cover the
multi-panel and explanatory figures in Patrick's analysis without importing viz.py.
"""

from __future__ import annotations

import datetime as dt
from html import escape
import textwrap

import numpy as np
import plotly.io as pio

from . import eda, theme

SERIE = theme.QUALITATIVE
KUNDENTYP = theme.KUNDENTYP_COLORS
SEQUENZIELL = theme.SEQUENTIAL
DIVERGIEREND = theme.DIVERGING
MONATSFORMAT = "%m/%Y"
ZEITRAUM = ""
GROESSE_KLEIN = 10
HIST_GAP = 0.3
DECKKRAFT_UEBERLAGERT = float(theme.TOKENS["chart-overlay-opacity"])
HELL = {
    "text": theme.TOKENS["text-primary"],
    "text_2": theme.TOKENS["text-muted"],
    "flaeche": theme.TOKENS["surface-card"],
    "gedaempft": theme.TOKENS["grey-400"],
    "achse": theme.TOKENS["grey-300"],
    "invers": theme.TOKENS["text-inverse"],
}
LABEL_SCHRIFT = dict(family=theme.FONT, size=11, color=HELL["text_2"])
LINIE_REFERENZ = dict(color=HELL["achse"], width=1, dash="4,4")


def aktiviere():
    """Native Plotly output for VS Code/JupyterLab, without duplicated JS bundles."""
    from IPython.display import HTML, display

    eda.setup()
    pio.renderers.default = "plotly_mimetype"
    display(HTML(theme.notebook_css() + notebook_css()))


def notebook_css():
    """Scope presentation rules to our report/output, never the editor UI."""
    t = theme.TOKENS
    return f"""<style>
    .sww-report, .sww-table {{font-family:{theme.FONT};color:{t["text-primary"]};}}
    .sww-report {{padding:24px;background:{t["surface-card"]};border:1px solid {t["border-default"]};
      border-radius:{t["radius-card"]};box-shadow:{t["shadow-card"]};margin:16px 0;}}
    .sww-report h1,.sww-report h2 {{color:{t["text-brand"]};margin-top:0;}}
    .sww-report p {{color:{t["text-secondary"]};line-height:1.6;}}
    .sww-report .eyebrow {{font-size:12px;color:{t["text-accent"]};letter-spacing:.08em;}}
    .sww-table {{overflow-x:auto;margin:16px 0;}}
    .sww-table table {{border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums;}}
    .sww-table th,.sww-table td {{padding:8px 12px;border-bottom:1px solid {t["border-subtle"]};}}
    .sww-table th {{background:{t["surface-page"]};text-align:left;font-weight:600;}}
    .sww-table td {{text-align:right;}}
    .js-plotly-plot text {{font-variant-numeric:tabular-nums;}}
    </style>"""


def titelkarte(titel, beschreibung, kennzahlen, logo=None):
    """A real-data notebook cover; no invented project results or demo metrics."""
    import base64
    from IPython.display import HTML, display

    image = ""
    if logo is not None:
        data = base64.b64encode(logo.read_bytes()).decode("ascii")
        image = f'<img src="data:image/png;base64,{data}" alt="StadtWerke Westhafen" style="width:200px;height:auto;margin-bottom:24px">'
    display(
        HTML(
            f'<section class="sww-report">{image}<p class="eyebrow">WESTHAFEN ENERGY ANALYTICS · EDA</p>'
            f"<h1>{escape(titel)}</h1><p>{escape(beschreibung)}</p>"
            f"<p><strong>{escape(kennzahlen)}</strong></p></section>"
        )
    )


def _datum(values):
    if values is None or len(values) == 0:
        return False
    arr = np.asarray(values)
    return np.issubdtype(arr.dtype, np.datetime64) or isinstance(arr.flat[0], dt.date)


def stil(fig, titel, untertitel="", x_titel=None, y_titel=None):
    """Attach the actual brand template to each figure, not just global defaults."""
    fig.update_layout(
        template=theme.template(),
        font=dict(family=theme.FONT, size=12, color=theme.TOKENS["text-primary"]),
        paper_bgcolor=theme.TOKENS["chart-paper-bg"],
        plot_bgcolor=theme.TOKENS["chart-plot-bg"],
        separators=",.",
        colorway=list(SERIE),
        meta={"sww": {"title": titel, "subtitle": untertitel, "period": ZEITRAUM}},
        legend=dict(title_text="", orientation="h", itemsizing="constant"),
        height=500,
    )
    if x_titel is not None:
        fig.update_xaxes(title_text=x_titel)
    if y_titel is not None:
        fig.update_yaxes(title_text=y_titel)
    fig.update_xaxes(automargin=True, tickangle=0, separatethousands=True, tickformat=",~g")
    fig.update_yaxes(automargin=True, separatethousands=True)
    fig.update_annotations(font=dict(family=theme.FONT, size=12, color=HELL["text"]))
    date_ranges = {}
    for trace in fig.data:
        if trace.type in {"scatter", "scattergl"} and _datum(trace.x):
            axis = "xaxis" + (trace.xaxis or "x")[1:]
            fig.layout[axis].update(tickformat=MONATSFORMAT, hoverformat=MONATSFORMAT, nticks=6)
            values = np.asarray(trace.x, dtype="datetime64[ms]")
            date_ranges.setdefault(axis, []).extend([values.min(), values.max()])
        if trace.type == "box":
            trace.update(fillcolor="rgba(0,0,0,0)", line_width=1.5)
        if trace.type == "heatmap":
            trace.update(xgap=2, ygap=2)
    kinds = {trace.type for trace in fig.data}
    for axis, values in date_ranges.items():
        pad = np.timedelta64(7, "D")
        fig.layout[axis].range = [str(min(values) - pad), str(max(values) + pad)]
    if kinds == {"histogram"} and len(fig.data) == 1:
        fig.update_traces(opacity=1)
    if kinds & {"box", "heatmap", "histogram", "bar"}:
        hover_pro_marke(fig)
    if "box" in kinds:
        fig.update_xaxes(showline=False)
    if "heatmap" in kinds:
        fig.update_xaxes(showline=False, ticks="", nticks=0)
        fig.update_yaxes(showgrid=False, ticks="", tickformat="", nticks=0)
        fig.update_coloraxes(colorbar=dict(thickness=10, outlinewidth=0, len=0.8))
    if any(trace.type == "bar" and trace.orientation == "h" for trace in fig.data):
        gitter_x(fig)
    return fig


def vorbereiten(fig):
    """Reserve separate space for title, wrapped caption, legend and panel labels."""
    details = (fig.layout.meta or {}).get("sww", {})
    title = details.get("title", fig.layout.title.text or "")
    caption = details.get("subtitle", "")
    period = details.get("period", ZEITRAUM)
    lines = textwrap.wrap(caption, width=105, break_long_words=False, break_on_hyphens=False)
    subtitle = "<br>".join(escape(line) for line in lines)
    if period:
        subtitle += ("<br>" if subtitle else "") + escape(f"Bezugszeitraum: {period}")
    has_panels = fig._grid_ref is not None
    visible = [trace for trace in fig.data if trace.showlegend is not False]
    has_legend = fig.layout.showlegend is not False and len(visible) > 1
    top = 72 + 17 * (len(lines) + bool(period)) + 25 * has_legend + 30 * has_panels
    bottom = max(fig.layout.margin.b or 48, 60)
    height = max(fig.layout.height or 500, top + bottom + 220)
    plot_height = height - top - bottom
    fig.update_layout(
        title=dict(
            text=escape(title),
            x=0,
            xref="container",
            xanchor="left",
            y=0.98,
            yanchor="top",
            yref="container",
            pad=dict(l=20),
            font=dict(family=theme.FONT, size=15, weight=600, color=HELL["text"]),
            subtitle=dict(
                text=subtitle, font=dict(family=theme.FONT, size=12, color=HELL["text_2"])
            ),
        ),
        margin=dict(t=top, b=bottom),
        height=height,
        showlegend=has_legend,
        legend=dict(
            y=1 + (30 if has_panels else 10) / plot_height,
            yanchor="bottom",
            x=0,
            xanchor="left",
            font=dict(family=theme.FONT, size=12, color=HELL["text_2"]),
        ),
    )
    # Explicit fonts also cover annotations and labels inserted after stil().
    fig.update_annotations(font_family=theme.FONT)
    for trace in fig.data:
        if "textfont" in trace._valid_props:
            trace.textfont.family = theme.FONT
        if trace.type == "bar" and trace.textposition == "outside":
            trace.cliponaxis = False
    for key in fig.layout:
        if key.startswith(("xaxis", "yaxis")):
            axis = fig.layout[key]
            axis.tickfont.family = theme.FONT
            axis.title.font.family = theme.FONT
            if axis.type == "log" and not axis.tickformat:
                axis.tickformat = ",~r"
    return fig


def zeigen(fig):
    vorbereiten(fig).show(config={"displaylogo": False, "responsive": True})


def hover_pro_marke(fig):
    return fig.update_layout(hovermode="closest")


def gitter_x(fig):
    fig.update_xaxes(showgrid=True, gridcolor=theme.TOKENS["data-grid"], showline=False)
    return fig.update_yaxes(showgrid=False, tickformat="", nticks=0)


def log_achse(fig, achse="y", **kwargs):
    getattr(fig, f"update_{achse}axes")(type="log", tickformat=",~r", **kwargs)
    return fig


def prozent_achse(fig, achse="y", stellen=0, **kwargs):
    getattr(fig, f"update_{achse}axes")(tickformat=f",.{stellen}f", ticksuffix=" %", **kwargs)
    return fig


def balken_kappen(fig, n_kategorien, flaeche_px=900, max_px=24):
    return fig.update_traces(
        width=min(0.8, max_px * n_kategorien / flaeche_px), selector=dict(type="bar")
    )


def label_umbruch(text, max_zeichen=24):
    return eda._wrap_label(text, max_zeichen)


def farben_datenqualitaet(anteile):
    return [
        theme.ROLE["anomalie"]
        if p >= 5
        else theme.ROLE["schwellwert"]
        if p >= 1
        else theme.TOKENS["grey-300"]
        for p in anteile
    ]


def _linie(fig, wert, text, achse, position, style, **kwargs):
    method = fig.add_hline if achse == "y" else fig.add_vline
    extra = (
        dict(
            annotation_text=text,
            annotation_position=position,
            annotation_font=dict(family=theme.FONT, size=11, color=style["color"]),
        )
        if text
        else {}
    )
    method(**{achse: wert}, line=style, **extra, **kwargs)
    return fig


def referenzlinie(fig, wert, text="", achse="y", position="top left", **kwargs):
    return _linie(fig, wert, text, achse, position, LINIE_REFERENZ, **kwargs)


def schwellwert(fig, wert, text="Schwellwert", achse="y", position="top left", **kwargs):
    return _linie(
        fig,
        wert,
        text,
        achse,
        position,
        dict(color=theme.ROLE["schwellwert"], width=1, dash="3,3"),
        **kwargs,
    )


def tabellenansicht(daten, dezimalstellen=1):
    """A styled HTML table, with German formatting and escaped cell contents."""
    from IPython.display import HTML

    styled = daten.style.format(
        precision=dezimalstellen, thousands=".", decimal=",", na_rep="—", escape="html"
    )
    return HTML('<div class="sww-table">' + styled.to_html() + "</div>")
