"""Notebook presentation helpers using only the canonical SWW theme.

The EDA builders remain the first choice for charts. These helpers cover the
multi-panel and explanatory figures in Patrick's analysis without importing viz.py.
"""

from __future__ import annotations

import datetime as dt
import base64
from html import escape
from pathlib import Path
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
ABSCHNITT = ("", "Explorative Datenanalyse")
_LOGO = ""
QUELLE = ""
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


def _logo_uri(pfad):
    """Embed the supplied original PNG, without recolouring or remote requests."""
    data = Path(pfad).read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Bitte ein originales SWW-Logo im PNG-Format angeben.")
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def aktiviere(logo=None, quelle=""):
    """Native Plotly output for VS Code/JupyterLab, without duplicated JS bundles."""
    from IPython.display import HTML, display

    global _LOGO, ABSCHNITT, QUELLE
    _LOGO = _logo_uri(logo) if logo is not None else ""
    QUELLE = quelle
    ABSCHNITT = ("", "Explorative Datenanalyse")
    eda.setup()
    pio.renderers.default = "plotly_mimetype"
    display(HTML(theme.notebook_css() + notebook_css()))


def notebook_css():
    """Scope presentation rules to our report/output, never the editor UI."""
    t = theme.TOKENS
    mono = base64.b64encode(
        (Path(__file__).parent / "fonts/geist-mono-600.ttf").read_bytes()
    ).decode("ascii")
    return f"""<style>
    @font-face {{font-family:"Geist Mono";font-weight:600;
      src:url(data:font/ttf;base64,{mono}) format("truetype");}}
    .sww-report, .sww-table {{font-family:{theme.FONT};color:{t["text-primary"]};}}
    .sww-report {{padding:24px;background:{t["surface-card"]};border:1px solid {t["border-default"]};
      border-radius:{t["radius-card"]};box-shadow:{t["shadow-card"]};margin:16px 0;}}
    .sww-report h1,.sww-report h2 {{color:{t["text-brand"]};margin-top:0;}}
    .sww-report p {{color:{t["text-secondary"]};line-height:1.6;}}
    .sww-report .eyebrow {{font-size:12px;color:{t["text-accent"]};letter-spacing:.08em;}}
    .sww-cover {{padding:0;overflow:hidden;}}
    .sww-cover-top {{display:flex;align-items:center;justify-content:space-between;gap:32px;
      padding:40px;background:{t["surface-brand-strong"]};}}
    .sww-cover-copy {{flex:1;min-width:0;}}
    .sww-cover .sww-cover-kicker {{color:{t["text-inverse-muted"]};font-size:11px;
      font-weight:600;letter-spacing:.15em;margin:0 0 24px;text-transform:uppercase;}}
    .sww-cover h1 {{font-size:clamp(32px,4.5vw,48px);font-weight:600;line-height:1.06;
      letter-spacing:-.035em;color:{t["text-inverse"]};margin:0 0 20px;max-width:560px;}}
    .sww-cover .sww-cover-description {{color:{t["text-inverse-muted"]};font-size:16px;
      max-width:540px;margin:0 0 24px;}}
    .sww-cover .sww-period {{display:inline-block;color:{t["text-inverse"]};font-size:12px;
      border:1px solid {t["border-inverse"]};border-radius:{t["radius-pill"]};padding:7px 12px;}}
    .sww-logo-holder {{background:{t["surface-card"]};border-radius:{t["radius-card"]};
      padding:20px;flex:0 0 190px;box-sizing:content-box;}}
    .sww-logo-holder img {{display:block;width:190px;max-width:100%;height:auto;}}
    .sww-metrics {{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
      border-bottom:1px solid {t["border-subtle"]};}}
    .sww-metric {{padding:24px 32px;min-width:0;}}
    .sww-metric+.sww-metric {{border-left:1px solid {t["border-subtle"]};}}
    .sww-metric strong {{display:block;color:{t["text-brand"]};font-size:36px;font-weight:600;
      letter-spacing:-.035em;line-height:1.15;font-family:{t["font-mono"]};
      font-variant-numeric:tabular-nums;}}
    .sww-metric span {{display:block;margin-top:8px;font-size:12px;color:{t["text-secondary"]};}}
    .sww-cover .sww-cover-source {{padding:16px 32px;margin:0;font-size:11px;
      color:{t["text-muted"]};overflow-wrap:anywhere;}}
    .sww-chapter {{display:flex;align-items:center;gap:20px;margin:36px 0 20px;padding:24px;}}
    .sww-chapter-number {{display:grid;place-items:center;flex:0 0 56px;height:56px;
      border-radius:{t["radius-md"]};background:{t["surface-brand-strong"]};
      color:{t["text-inverse"]};font-size:25px;font-weight:500;}}
    .sww-chapter .eyebrow {{margin:0 0 4px;font-size:10px;}}
    .sww-chapter h2 {{margin:0;font-size:24px;letter-spacing:-.02em;}}
    .sww-chapter p {{margin:6px 0 0;font-size:13px;}}
    .sww-table {{overflow-x:auto;margin:16px 0;background:{t["surface-card"]};color-scheme:light;}}
    .sww-table table {{border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums;width:100%;}}
    /* Pair opaque surfaces with text colours, even under a dark notebook host.
       Only SWW table colours override host styles; the editor itself is untouched. */
    .sww-table table,.sww-table td {{background:{t["surface-card"]} !important;
      color:{t["text-primary"]} !important;}}
    .sww-table th,.sww-table td {{padding:8px 12px;border-bottom:1px solid {t["border-subtle"]};}}
    .sww-table th {{background:{t["surface-brand-strong"]} !important;color:{t["text-inverse"]} !important;
      text-align:left;font-weight:500;}}
    .sww-table td {{text-align:right;}}
    .sww-table tbody tr:nth-child(even) td {{background:{t["surface-sunken"]} !important;}}
    .sww-table tbody tr:hover td {{background:{t["surface-accent-subtle"]} !important;}}
    .js-plotly-plot text {{font-variant-numeric:tabular-nums;}}
    @media(max-width:700px){{
      .sww-cover-top {{padding:28px;gap:24px;flex-wrap:wrap;}}
      .sww-cover-copy {{flex-basis:100%;}}
      .sww-logo-holder {{flex-basis:180px;padding:16px;}}
      .sww-logo-holder img {{width:180px;}}
      .sww-metric {{padding:20px 16px;}}.sww-metric strong {{font-size:24px;}}
      .sww-cover .sww-cover-source {{padding:16px;}}
      .sww-chapter {{padding:20px;gap:16px;}}.sww-chapter h2 {{font-size:21px;}}
    }}
    </style>"""


def titelkarte(titel, beschreibung, kennzahlen, logo=None, *, metriken=(), zeitraum=""):
    """A real-data notebook cover; no invented project results or demo metrics."""
    from IPython.display import HTML, display

    image = ""
    if logo is not None:
        image = (
            f'<div class="sww-logo-holder"><img src="{_logo_uri(logo)}" '
            'alt="StadtWerke Westhafen GmbH – Energie für unsere Stadt"></div>'
        )
    metrics = "".join(
        f'<div class="sww-metric"><strong>{escape(str(wert))}</strong>'
        f'<span>{escape(label)}</span></div>'
        for label, wert in metriken
    )
    period = (
        f'<span class="sww-period">Bezugszeitraum {escape(zeitraum)}</span>' if zeitraum else ""
    )
    display(
        HTML(
            notebook_css() + '<section class="sww-report sww-cover"><div class="sww-cover-top">'
            '<div class="sww-cover-copy"><p class="sww-cover-kicker">'
            'Westhafen Energy Analytics / Analysebericht</p>'
            f'<h1>{escape(titel)}</h1><p class="sww-cover-description">'
            f'{escape(beschreibung)}</p>{period}</div>{image}</div>'
            f'<div class="sww-metrics">{metrics}</div>'
            f'<p class="sww-cover-source">{escape(kennzahlen)}</p></section>'
        )
    )


def abschnitt(nummer, titel, beschreibung="", *, kontext="EXPLORATIVE DATENANALYSE"):
    """A chapter opener; its identity is captured by subsequent figures."""
    from IPython.display import HTML, display

    global ABSCHNITT
    ABSCHNITT = (str(nummer), titel)
    display(HTML(
        notebook_css()
        + f'<section class="sww-report sww-chapter" id="sww-chapter-{escape(str(nummer), quote=True)}">'
        f'<span class="sww-chapter-number">{escape(str(nummer))}</span>'
        f'<div><p class="eyebrow">WESTHAFEN / {escape(str(kontext))}</p>'
        f'<h2>{escape(titel)}</h2><p>{escape(beschreibung)}</p></div></section>'
    ))


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
        meta={"sww": {
            "title": titel, "subtitle": untertitel, "period": ZEITRAUM,
            "chapter": ABSCHNITT[0], "chapter_title": ABSCHNITT[1],
            "source": QUELLE,
        }},
        legend=dict(title_text="", orientation="h", itemsizing="constant"),
        height=560,
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
    has_panels = fig._grid_ref is not None
    visible = [trace for trace in fig.data if trace.showlegend is not False]
    has_legend = fig.layout.showlegend is not False and len(visible) > 1
    title_lines = textwrap.wrap(title, width=58, break_long_words=False, break_on_hyphens=False)
    top = 104 + 26 * (len(title_lines) - 1) + 17 * len(lines) + 25 * has_legend + 30 * has_panels
    # Keep repeated preparation idempotent while reserving an export-safe brand footer.
    base_bottom = details.setdefault("content_bottom", max(fig.layout.margin.b or 48, 60))
    bottom = base_bottom + 80
    fig.layout.meta = {**(fig.layout.meta or {}), "sww": details}
    height = max(fig.layout.height or 500, top + bottom + 220)
    plot_height = height - top - bottom
    fig.update_layout(
        title=dict(
            text=(
                f'<span style="font-size:10px;color:{theme.TOKENS["text-accent"]}">'
                f'SWW / ENERGIEANALYSE {escape(details.get("chapter", ""))}</span><br>'
                + "<br>".join(escape(line) for line in title_lines)
            ),
            x=0,
            xref="container",
            xanchor="left",
            y=0.98,
            yanchor="top",
            yref="container",
            pad=dict(l=20),
            font=dict(family=theme.FONT, size=22, weight=600, color=theme.TOKENS["text-brand"]),
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
    # Use native Plotly objects: branding survives a standalone PNG/HTML export.
    # Names let us replace only our own objects and retain all analytical annotations.
    for collection in ("annotations", "shapes", "images"):
        fig.layout[collection] = tuple(
            item for item in fig.layout[collection]
            if not (item.name or "").startswith("sww-brand-")
        )
    footer_y = (-bottom + 64) / plot_height
    for start, end, color, width in (
        (0, 1, theme.TOKENS["border-subtle"], 1),
        (0, 0.08, theme.TOKENS["text-brand"], 3),
    ):
        fig.add_shape(
            name=f"sww-brand-rule-{start}-{end}", type="line", xref="paper", yref="paper",
            x0=start, x1=end, y0=footer_y, y1=footer_y, line=dict(color=color, width=width),
        )
    footer_text = escape(f'Bezugszeitraum: {period}') if period else "Explorative Datenanalyse"
    if details.get("source"):
        footer_text += "<br>Quelle: " + escape(details["source"])
    fig.add_annotation(
        name="sww-brand-source", text=footer_text,
        xref="paper", yref="paper", x=0, y=(-bottom + 22) / plot_height,
        xanchor="left", yanchor="bottom", showarrow=False, align="left",
        font=dict(family=theme.FONT, size=10, color=HELL["text_2"]),
    )
    if _LOGO:
        fig.add_layout_image(
            name="sww-brand-logo", source=_LOGO, xref="paper", yref="paper",
            x=1, y=(-bottom + 20) / plot_height, xanchor="right", yanchor="bottom",
            sizex=0.10, sizey=36 / plot_height, sizing="contain", opacity=1, layer="above",
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
    return HTML(notebook_css() + '<div class="sww-table">' + styled.to_html() + "</div>")
