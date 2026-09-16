"""
Visualisierungs-Template Stadtwerke Westhafen
=============================================

Einheitlicher Plotly-Stil fuer EDA, Modellierung und Praesentation - umgesetzt
nach dem SWW-Design-System (brand/design-system/).

Quellen der Regeln:
    tokens/design-tokens.json   Farben, Schrift, Groessen (ueber _tokens.json)
    guidelines/charts.md        Farbrollen, Achsen, Zahlenformat, Unsicherheit
    guidelines/brand-guide.md   Sprache, Zahlen (Dezimalkomma, MM/JJJJ), Typografie
    guidelines/slides.md        Export fuer Folien
    assets/plotly/sww_plotly.js und energy_analytics.visualization.eda
                                Konstruktion der 15 Referenzdiagramme

viz.py enthaelt keine eigenen Hex-Werte. Aendert sich das Design-System,
genuegt `python scripts/build_tokens.py` und ein Kernel-Neustart.

Verwendung im Notebook:

    import viz
    viz.aktiviere()                      # Template + Schrift aktivieren
    viz.ZEITRAUM = "01/2024–12/2025"     # Bezugszeitraum fuer alle Titel

    fig = px.line(...)
    viz.stil(fig, "Titel", "Aussage", y_titel="Verbrauch (kWh)")
    fig.show()

Regeln, die automatisch greifen (Template bzw. stil()):
    - IBM Plex Sans in allen Diagrammtexten, Titel 15 px halbfett linksbuendig,
      sonst 12 px; Ziffern tabellarisch (im Notebook)
    - Dezimalkomma und Tausenderpunkt (separators=",."), y-Format ",~g"
    - Datumsachsen im Format MM/JJJJ, Achsenbeschriftung waagerecht, max. 6 Ticks
    - Raster nur auf der Werteachse (horizontale Balken: x-Raster)
    - Legende oben ohne Titel; eine Serie -> keine Legende
    - Hover: Zeitreihen "x unified", Balken/Boxen/Streuung/Heatmaps an der Marke
    - Balkenabstand 0,36, Eckenradius 4 px; Boxen ohne Fuellung
    - Heatmaps mit 2-px-Fugen und schmaler Farbskala
    - Zeitraum im Titel ("Titel · 01/2024–12/2025")

Feste Farbrollen (Non-negotiables, SKILL.md):
    KUNDENTYP   Gewerbe teal · Industrie navy · Kommunal gruen
    ROLLE       Ist navy durchgezogen · Prognose cyan gestrichelt (4,2) ·
                Band cyan 16 % · Schwellwert amber gepunktet (3,3) · Anomalie rot
    SERIE       kategorialer Zyklus ohne Rot/Amber/Cyan - nie fuer Kundentypen
    STATUS      reserviert, nie als Serienfarbe; Status nie nur ueber Farbe
Einheiten stehen in runden Klammern im Achsentitel: "Verbrauch (kWh)".
Keine 3D-Effekte, keine Doppel-Y-Achsen, keine Verlaeufe; Balken beginnen bei 0;
Log-Achsen ausdruecklich kennzeichnen.
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

try:
    from energy_analytics.visualization import eda
    from energy_analytics.visualization import theme as _T
except ImportError:  # Paket nicht installiert -> src/ neben viz.py nutzen
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from energy_analytics.visualization import eda
    from energy_analytics.visualization import theme as _T

_TOK = _T.TOKENS


def _px(token: str) -> float:
    """'12px' -> 12.0"""
    return float(_TOK[token].removesuffix("px"))


# =========================================================
# Farben (tokens/design-tokens.json -> chart.*)
# =========================================================

# --- Kategoriale Serienfarben (feste Reihenfolge, Navy zuerst) ---
SERIE = list(_T.QUALITATIVE)

# --- Kundentyp: in JEDER Abbildung dieselbe Farbe ---
KUNDENTYP = dict(_T.KUNDENTYP_COLORS)
KUNDENTYP_REIHENFOLGE = list(KUNDENTYP)

# --- Fachliche Rollen fuer Prognose und Anomalieerkennung ---
ROLLE = dict(_T.ROLE)

# Streudiagramme/Bubble: max. 3 Serien, sonst wird die Trennung unzuverlaessig.
# Mehr Auspraegungen -> Facetten (facet_col) oder Restkategorie "Sonstige".
SERIE_STREU_MAX = 3

# --- Sequenziell: Navy hell -> dunkel (Heatmaps, Magnitude), 7 Stufen ---
SEQUENZIELL = list(_T.SEQUENTIAL)

# --- Divergierend: Teal <- grau -> Rot, Mitte = 0 (Residuen, Korrelationen) ---
DIVERGIEREND = list(_T.DIVERGING)

# --- Status: reserviert, nie als Serienfarbe verwenden ---
STATUS = {"gut": _TOK["status-ok"], "warnung": _TOK["status-warn"],
          "ernst": _TOK["data-threshold"], "kritisch": _TOK["data-anomaly"]}

# --- Flaechen, Schrift, Linien ---
HELL = {
    "flaeche":   _TOK["chart-plot-bg"],   # Diagrammflaeche
    "text":      _TOK["text-primary"],    # Primaertext (Titel, Werte)
    "text_2":    _TOK["text-secondary"],  # Achsen, Legende, Wertlabels
    "gedaempft": _TOK["grey-400"],        # neutrale Serien, Quellenangabe
    "gitter":    _TOK["data-grid"],       # Rasterlinie und Achslinie
    "achse":     _TOK["grey-300"],        # Nulllinie, Referenz- und Identitaetslinien
    "rand":      _TOK["border-default"],  # Rahmen des Hover-Labels
}

# =========================================================
# Typografie und Masse (tokens chart-*, fs-*, fw-*)
# =========================================================

SCHRIFT = _T.FONT                         # IBM Plex Sans - nie Monospace im Diagramm
GROESSE = _px("chart-font-size")          # 12: Achsen, Legende, Hover, Untertitel
GROESSE_TITEL = _px("chart-title-size")   # 15
GROESSE_LABEL = _px("fs-2xs")             # 11: Wertlabels, Annotationen
GROESSE_KLEIN = _px("fs-3xs")             # 10: Farbskala, dichte Matrizen
GEWICHT_TITEL = int(_TOK["fw-semibold"])  # 600
LINIE = _px("chart-line-width")           # 2
MARKER = _px("chart-marker-size")         # 6
BALKENABSTAND = float(_TOK["chart-bar-gap"])              # 0.36
ECKENRADIUS = _px("chart-bar-radius")                     # 4
DECKKRAFT_UEBERLAGERT = float(_TOK["chart-overlay-opacity"])  # 0.62, ueberlagerte Histogramme
DECKKRAFT_STREU = 0.75                    # Streudiagramme (eda.scatter_trend)
HIST_GAP = 0.3                            # Histogramme (eda.histogram)

# --- Linienstile der Rollen (guidelines/charts.md) ---
STRICH = {"prognose": "4,2", "schwellwert": "3,3", "trend": "3,3", "referenz": "4,4"}
LINIE_REFERENZ = dict(color=HELL["achse"], width=1, dash=STRICH["referenz"])
LINIE_SCHWELLWERT = dict(color=ROLLE["schwellwert"], width=1, dash=STRICH["schwellwert"])
LABEL_SCHRIFT = dict(family=SCHRIFT, size=GROESSE_LABEL, color=HELL["text_2"])

# --- Datenqualitaet: Anteil fehlerhaft/fehlend (eda.missing_values) ---
DATENQUALITAET_KRITISCH = 5.0   # ab 5 % rot
DATENQUALITAET_WARNUNG = 1.0    # ab 1 % amber, darunter grau

# =========================================================
# Sprache und Zahlen (guidelines/brand-guide.md)
# =========================================================

MONATSFORMAT = "%m/%Y"          # MM/JJJJ
TAGESFORMAT = "%d.%m.%Y"        # TT.MM.JJJJ
ZEITRAUM = ""                   # Bezugszeitraum, wird an jeden Titel gehaengt
MODELL_HINWEIS = ("Das Modell ersetzt keine Abrechnungsentscheidung — "
                  "es flaggt nur Untersuchungswürdiges.")

EXPORT_DIR = Path("abbildungen")


def zahl(wert: float, stellen: int = 0) -> str:
    """Zahl im deutschen Format: 14820.5 -> '14.820,5'."""
    return eda._fmt_de(wert, stellen)


def _pruefe_modus(modus: str) -> None:
    # Das Design-System definiert (noch) keine Dark-Tokens
    if modus != "hell":
        raise ValueError(f"Nur modus='hell' wird unterstuetzt, nicht {modus!r}")


# =========================================================
# Template-Definition
# =========================================================

def _template() -> go.layout.Template:
    """Design-System-Template (dist/plotly/template.json) plus Titelblock,
    Farbskala und Trace-Defaults der Referenzdiagramme."""
    t = _T.template()
    farbskala = dict(
        thickness=10, len=0.8, outlinewidth=0,
        tickfont=dict(family=SCHRIFT, size=GROESSE_KLEIN, color=HELL["text_2"]),
        title=dict(font=dict(family=SCHRIFT, size=GROESSE_LABEL, color=HELL["text_2"])),
    )
    t.layout.update(
        # --- Titelblock: Titel = Gegenstand + Zeitraum, Untertitel = Aussage ---
        title=dict(
            font=dict(size=GROESSE_TITEL, color=HELL["text"], weight=GEWICHT_TITEL),
            subtitle=dict(font=dict(family=SCHRIFT, size=GROESSE, color=HELL["text_2"])),
            x=0, xref="paper", xanchor="left",
            y=0.95, yref="container", yanchor="top",
        ),
        # Tausenderpunkt auch auf der x-Achse (y hat ",~g" aus dem Design-System)
        xaxis=dict(separatethousands=True),
        legend=dict(y=1.03, itemsizing="constant", borderwidth=0),
        # Design-System-Raender; oben Platz fuer Titel + Untertitel + Legende
        margin=dict(l=64, r=24, t=115, b=48),
        height=460,
        bargroupgap=0.12,
        boxgap=0.4,
        violingap=0.4,
        coloraxis=dict(colorbar=farbskala),
    )
    t.data.scatter = [go.Scatter(line=dict(width=LINIE), marker=dict(size=MARKER))]
    t.data.scattergl = [go.Scattergl(line=dict(width=LINIE), marker=dict(size=MARKER))]
    t.data.box = [go.Box(marker=dict(size=3), line=dict(width=1.5),
                         fillcolor="rgba(255,255,255,0)")]
    t.data.heatmap = [go.Heatmap(xgap=2, ygap=2, colorbar=farbskala)]
    return t


pio.templates["sww"] = _template()

# Ziffern gleich breit - Spalten und Achsenwerte stehen buendig
_NOTEBOOK_CSS = ("<style>.js-plotly-plot text, .dataframe td "
                 "{font-variant-numeric: tabular-nums;}</style>")


def aktiviere(modus: str = "hell", schrift: bool = True) -> None:
    """Setzt das Template als Standard fuer alle folgenden Plots.

    schrift=True bettet IBM Plex Sans ins Notebook ein (lokal, ohne Netzwerk),
    damit die Diagramme nicht auf eine Ersatzschrift ausweichen.
    """
    _pruefe_modus(modus)
    pio.templates.default = "sww"
    if schrift:
        try:
            from IPython import get_ipython
            from IPython.display import HTML, display
        except ImportError:
            return
        if get_ipython() is not None:
            display(HTML(_T.notebook_css() + _NOTEBOOK_CSS))


# =========================================================
# stil(): Titelblock + typabhaengige Regeln
# =========================================================

def _ist_datum(werte) -> bool:
    if werte is None or len(werte) == 0:
        return False
    arr = np.asarray(werte)
    if np.issubdtype(arr.dtype, np.datetime64):
        return True
    return isinstance(arr.flat[0], (_dt.date, np.datetime64))


def _typregeln(fig: go.Figure) -> None:
    """Konstruktionsregeln der Referenzdiagramme je Diagrammtyp."""
    typen = {s.type for s in fig.data}
    markenhover = False

    # Log-Achsen: ausgeschriebene Zahlen (",~r": 1.000.000 statt 1e+6 oder 10k)
    for name in [k for k in fig.layout if k.startswith(("xaxis", "yaxis"))]:
        achse = fig.layout[name]
        if achse.type == "log" and achse.tickformat is None:
            achse.tickformat = ",~r"

    # Titel der Teildiagramme: kleiner als der Haupttitel
    if fig._grid_ref is not None:
        fig.update_annotations(font=dict(size=GROESSE + 1, color=HELL["text"],
                                         weight=GEWICHT_TITEL))

    # Datumsachsen: MM/JJJJ, auch im Hover
    datum_achsen = {s.xaxis or "x" for s in fig.data
                    if s.type in ("scatter", "scattergl", "bar") and _ist_datum(s.x)}
    for ref in datum_achsen:
        name = "xaxis" if ref == "x" else f"xaxis{ref[1:]}"
        achse = fig.layout[name]
        if achse.tickformat is None:
            achse.tickformat = MONATSFORMAT
        if achse.hoverformat is None:
            achse.hoverformat = MONATSFORMAT

    # Horizontale Balken: Werteachse ist x
    balken = [s for s in fig.data if s.type == "bar"]
    if balken and all(s.orientation == "h" for s in balken):
        gitter_x(fig)
        markenhover = True

    # Boxplots: keine Achslinie unter den Kategorien
    if typen & {"box", "violin"}:
        fig.update_xaxes(showline=False)
        markenhover = True

    # Heatmaps: keine Achslinien, keine Ticks, kein Raster
    if "heatmap" in typen:
        # nticks=0: jede Kategorie beschriften (Template begrenzt sonst auf 6)
        fig.update_xaxes(showline=False, ticks="", nticks=0)
        fig.update_yaxes(showgrid=False, ticks="", tickformat="", nticks=0)
        markenhover = True

    # Histogramme und reine Streudiagramme: Tooltip an der Marke
    if "histogram" in typen:
        markenhover = True
    streu = [s for s in fig.data if s.type in ("scatter", "scattergl")
             and s.mode == "markers" and s.x is not None and len(s.x) > 50]
    if streu:
        fig.update_xaxes(showgrid=True, gridcolor=HELL["gitter"])  # Streuung: beide Raster
        markenhover = True

    if markenhover:
        fig.update_layout(hovermode="closest")


def stil(fig: go.Figure, titel: str, untertitel: str = "",
         x_titel: str | None = None, y_titel: str | None = None,
         quelle: str = "", zeitraum: str | None = None) -> go.Figure:
    """Titelblock, Achsentitel, Quellenangabe und typabhaengige Regeln setzen.

    Der Untertitel traegt die Aussage des Diagramms ("Der Verbrauch sinkt im
    Sommer um 40 %"), der Titel den Gegenstand und den Bezugszeitraum.
    zeitraum=None nimmt viz.ZEITRAUM, "" laesst ihn weg.
    Achsentitel mit Einheit in runden Klammern: "Verbrauch (kWh)".
    """
    zeitraum = ZEITRAUM if zeitraum is None else zeitraum
    text = f"{titel} · {zeitraum}" if zeitraum else titel
    fig.update_layout(title=dict(text=text,
                                 subtitle=dict(text=untertitel) if untertitel else None))
    # "" loescht den automatischen Spaltennamen, None laesst ihn stehen
    if x_titel is not None:
        fig.update_xaxes(title_text=x_titel)
    if y_titel is not None:
        fig.update_yaxes(title_text=y_titel)
    _typregeln(fig)
    if quelle:
        fig.add_annotation(
            text=quelle, xref="paper", yref="paper", x=0, y=-0.18,
            showarrow=False, xanchor="left",
            font=dict(size=GROESSE_LABEL, color=HELL["text_2"]),
        )
    # Eine Serie braucht keine Legende - der Titel sagt bereits, was geplottet ist
    sichtbare = [s for s in fig.data if s.showlegend is not False]
    fig.update_layout(showlegend=len(sichtbare) > 1, legend_title_text="")
    return fig


# =========================================================
# Hilfsfunktionen fuer einzelne Regeln
# =========================================================

def balken_kappen(fig: go.Figure, n_kategorien: int,
                  flaeche_px: int = 900, max_px: int = 24) -> go.Figure:
    """Begrenzt die Balkenbreite auf max. 24 px - Balken fuellen nie den Slot.

    Plotly rechnet Balkenbreiten in Datenschritten, nicht in Pixeln. Bei wenigen
    Kategorien werden Balken sonst absurd breit.
    """
    fig.update_traces(width=min(0.8, max_px * n_kategorien / flaeche_px),
                      selector=dict(type="bar"))
    return fig


def hover_pro_marke(fig: go.Figure) -> go.Figure:
    """Fuer Balken, Boxplots und Streudiagramme: Tooltip an der Marke statt
    Fadenkreuz auf der X-Achse."""
    fig.update_layout(hovermode="closest")
    return fig


def gitter_x(fig: go.Figure, modus: str = "hell") -> go.Figure:
    """Horizontale Balken: Raster auf die Werteachse x, Kategorien ohne Raster."""
    _pruefe_modus(modus)
    fig.update_xaxes(showgrid=True, gridcolor=HELL["gitter"], gridwidth=1,
                     showline=False, ticks="")
    fig.update_yaxes(showgrid=False, showline=True, linecolor=HELL["gitter"],
                     tickformat="", automargin=True, tickfont=LABEL_SCHRIFT,
                     nticks=0)  # jede Kategorie beschriften
    return fig


def log_achse(fig: go.Figure, achse: str = "y", **kw) -> go.Figure:
    """Logarithmische Achse mit ausgeschriebenen Zahlen (1.000.000 statt 1e+6).
    Die Achse zusaetzlich im Titel als 'log' kennzeichnen."""
    getattr(fig, f"update_{achse}axes")(type="log", tickformat=",~r", **kw)
    return fig


def prozent_achse(fig: go.Figure, achse: str = "y", stellen: int = 0,
                  **kw) -> go.Figure:
    """Prozentachse mit Leerzeichen vor dem Zeichen ('12 %'). Werte in Prozent."""
    getattr(fig, f"update_{achse}axes")(tickformat=f",.{stellen}f", ticksuffix=" %", **kw)
    return fig


def wertlabels(fig: go.Figure, vorlage: str | None = None,
               position: str = "outside") -> go.Figure:
    """Wertlabels an Balken: 11 px, Sekundaertext, nicht abgeschnitten."""
    kw = dict(textposition=position, textfont=LABEL_SCHRIFT, cliponaxis=False)
    if vorlage:
        kw["texttemplate"] = vorlage
    fig.update_traces(selector=dict(type="bar"), **kw)
    return fig


def label_umbruch(text: str, max_zeichen: int = 24) -> str:
    """Lange snake_case-Namen einmal am mittleren Unterstrich umbrechen."""
    return eda._wrap_label(text, max_zeichen)


def farben_datenqualitaet(anteile_prozent) -> list[str]:
    """Balkenfarben fuer Fehlwertanteile: >= 5 % rot, >= 1 % amber, sonst grau."""
    return [ROLLE["anomalie"] if p >= DATENQUALITAET_KRITISCH
            else ROLLE["schwellwert"] if p >= DATENQUALITAET_WARNUNG
            else HELL["achse"] for p in anteile_prozent]


def _linie(fig, wert, achse, linie, text, farbe, position, **kw):
    add = fig.add_hline if achse == "y" else fig.add_vline
    arg = {"y" if achse == "y" else "x": wert}
    extra = {}
    if text:
        extra = dict(annotation_text=text, annotation_position=position,
                     annotation_font=dict(family=SCHRIFT, size=GROESSE_LABEL, color=farbe))
    add(**arg, line=linie, **extra, **kw)
    return fig


def schwellwert(fig: go.Figure, wert: float, text: str = "Schwellwert",
                achse: str = "y", position: str = "top left", **kw) -> go.Figure:
    """Schwellwert/Grenze: amber, gepunktet 3,3, immer beschriftet (Rolle, nicht Farbe allein)."""
    return _linie(fig, wert, achse, LINIE_SCHWELLWERT, text, ROLLE["schwellwert"],
                  position, **kw)


def referenzlinie(fig: go.Figure, wert: float, text: str = "",
                  achse: str = "y", position: str = "top left", **kw) -> go.Figure:
    """Neutrale Bezugslinie (Mittel = 1, Heizgrenze, 0 %): grau, 1 px, gestrichelt 4,4."""
    return _linie(fig, wert, achse, LINIE_REFERENZ, text, HELL["text_2"], position, **kw)


def diagonale(fig: go.Figure, x, y, name: str) -> go.Figure:
    """Identitaets- oder Bezugsgerade (z. B. 'Ist = Prognose') wie im Parity-Plot."""
    fig.add_scatter(x=list(x), y=list(y), mode="lines", name=name,
                    line=LINIE_REFERENZ, hoverinfo="skip")
    return fig


def endlabel(fig: go.Figure, x, y, text: str, farbe: str,
             versatz: int = 8) -> go.Figure:
    """Direktbeschriftung am Linienende - Alternative zur Legende, sparsam einsetzen.

    Beschriftet wird der Endpunkt, der Extremwert oder die eine Serie, um die
    es geht. Die Schrift bleibt in Textfarbe, die Identitaet traegt die Linie.
    """
    fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                       xanchor="left", xshift=versatz,
                       font=dict(size=GROESSE, color=HELL["text"]))
    fig.add_scatter(x=[x], y=[y], mode="markers", showlegend=False,
                    hoverinfo="skip", marker=dict(size=MARKER + 2, color=farbe))
    return fig


# --- Prognose und Anomalien (Modellierung) ---
prognose_spuren = _T.forecast_traces      # Ist navy, Prognose cyan 4,2, Band cyan 16 %
anomalie_marker = _T.anomaly_markers      # rote Marker mit weissem Ring


def tabellenansicht(daten, dezimalstellen: int = 1):
    """Tabellenansicht zum Diagramm - jede Zahl bleibt ohne Hover erreichbar.

    Deutsches Zahlenformat, Ziffern tabellarisch. Braucht jinja2.
    """
    return (daten.round(dezimalstellen)
                 .style.format(thousands=".", decimal=",", precision=dezimalstellen)
                 .set_properties(**{"font-variant-numeric": "tabular-nums"}))


# =========================================================
# Export
# =========================================================

def speichern(fig: go.Figure, name: str, breite: int = 1000,
              hoehe: int | None = None) -> None:
    """Speichert interaktiv als HTML und statisch als PNG (Dokumentation).

    PNG braucht kaleido; IBM Plex Sans muss dafuer systemweit installiert sein
    (brand/design-system/dist/fonts/).
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    fig.write_html(EXPORT_DIR / f"{name}.html", include_plotlyjs="cdn")
    fig.write_image(EXPORT_DIR / f"{name}.png", width=breite,
                    height=hoehe or fig.layout.height or 460, scale=2)


def folie(fig: go.Figure, name: str) -> Path:
    """PNG fuer die Chart-Folie (1120x560, groessere Schrift), Notebook-Figur bleibt
    unveraendert. Statisches Bild hat keinen Hover: noetige Labels muessen im Bild
    oder als Folientext stehen. Voraussetzungen wie speichern().
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    return eda.save_for_slide(fig, EXPORT_DIR / f"{name}_folie.png")
