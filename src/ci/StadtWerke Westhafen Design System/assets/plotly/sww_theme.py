"""SWW chart theme for Python notebooks — Plotly + Matplotlib.

Usage (Plotly):
    import sww_theme
    sww_theme.register()                     # registers and activates template "sww"
    fig = px.line(df, x="monat", y="verbrauch_kwh")
    fig.show()

Usage (Matplotlib):
    import sww_theme
    sww_theme.apply_matplotlib()

Colour roles are identical to tokens/charts.css. Do not invent new colours in notebooks —
a reader who learns "cyan = Prognose" on a slide must find the same in the dashboard.
"""

# --- Brand palette (mirrors tokens/colors.css) -------------------------------
NAVY = "#084878"
NAVY_900 = "#04263F"
TEAL = "#0080A0"
CYAN = "#0090C8"
GREEN = "#58A858"
AMBER = "#C77E11"
RED = "#B3261E"
GREY_500 = "#6B7887"
GREY_400 = "#8C99A7"
GREY_100 = "#E4E9EF"
GREY_50 = "#F1F4F7"
INK = "#141A21"

# Categorical order
QUALITATIVE = [NAVY, TEAL, GREEN, CYAN, AMBER, "#6CC0D2", "#4E5A68", RED]

# Fixed Kundentyp mapping — never reassign
KUNDENTYP_COLORS = {"Gewerbe": TEAL, "Industrie": NAVY, "Kommunal": GREEN}

# Domain roles
ROLE = {
    "ist": NAVY,
    "prognose": CYAN,
    "band": "rgba(0,144,200,0.16)",
    "residuum": TEAL,
    "schwellwert": AMBER,
    "anomalie": RED,
}

# Sequential ramp (Verbrauch, Heiztage heatmaps)
SEQUENTIAL = ["#E4EFF7", "#BBD7EA", "#7FB4D8", "#3E90C4", "#0F6FAE", "#084878", "#04263F"]

# Diverging ramp (Residuen: Unter- <-> Überverbrauch)
DIVERGING = ["#005E77", "#1C9BB8", "#B2DEE7", "#F1F4F7", "#F3C6C1", "#D2564B", "#951C15"]

FONT = "IBM Plex Sans, Segoe UI, sans-serif"
FONT_MONO = FONT  # charts use one family — no monospace in plots; kept for backwards compatibility


def template():
    """Return the SWW plotly.graph_objects.layout.Template."""
    import plotly.graph_objects as go

    axis = dict(
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor=GREY_100,
        linewidth=1,
        ticks="outside",
        ticklen=4,
        tickcolor=GREY_100,
        tickfont=dict(family=FONT_MONO, size=11, color=GREY_500),
        title=dict(font=dict(family=FONT, size=12, color=GREY_500)),
        automargin=True,
    )
    return go.layout.Template(
        layout=go.Layout(
            font=dict(family=FONT, size=12, color=INK),
            title=dict(
                font=dict(family=FONT, size=15, color=INK),
                x=0, xanchor="left", y=0.96, pad=dict(b=12),
            ),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            colorway=QUALITATIVE,
            colorscale=dict(
                sequential=[[i / (len(SEQUENTIAL) - 1), c] for i, c in enumerate(SEQUENTIAL)],
                diverging=[[i / (len(DIVERGING) - 1), c] for i, c in enumerate(DIVERGING)],
            ),
            xaxis={**axis},
            # horizontal gridlines only — the one grid direction SWW charts use
            yaxis={**axis, "showgrid": True, "gridcolor": GREY_100, "gridwidth": 1, "showline": False,
                   # German thousands separator instead of Plotly's English "17k" SI fallback
                   "tickformat": ",d", "separatethousands": True},
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(family=FONT, size=12, color=GREY_500),
                bgcolor="rgba(0,0,0,0)", title=dict(text=""),
            ),
            margin=dict(l=64, r=24, t=64, b=48),
            hoverlabel=dict(
                bgcolor="#FFFFFF", bordercolor=GREY_100,
                font=dict(family=FONT_MONO, size=12, color=INK), align="left",
            ),
            hovermode="x unified",
            separators=",.",           # German: decimal comma, dot thousands
            bargap=0.36,
            barcornerradius=4,        # rounded bar ends (plotly >= 5.19); remove on older versions
            colorbar=dict(outlinewidth=0, ticks="outside", thickness=10, len=0.7),
        )
    )


def register(activate=True, name="sww"):
    import plotly.io as pio
    pio.templates[name] = template()
    if activate:
        pio.templates.default = name
    return pio.templates[name]


# --- Helpers for the forecast / anomaly product ------------------------------

def forecast_traces(x, ist, prognose, lower=None, upper=None):
    """Ist (navy solid) + Prognose (cyan dashed) + optional Konfidenzband."""
    import plotly.graph_objects as go
    traces = []
    if lower is not None and upper is not None:
        traces += [
            go.Scatter(x=list(x) + list(x)[::-1], y=list(upper) + list(lower)[::-1],
                       fill="toself", fillcolor=ROLE["band"], line=dict(width=0),
                       hoverinfo="skip", showlegend=True, name="Konfidenzband"),
        ]
    traces += [
        go.Scatter(x=x, y=ist, name="Ist", mode="lines+markers",
                   line=dict(color=ROLE["ist"], width=2),
                   marker=dict(size=6, color=ROLE["ist"])),
        go.Scatter(x=x, y=prognose, name="Prognose", mode="lines",
                   line=dict(color=ROLE["prognose"], width=2, dash="4,2")),
    ]
    return traces


def anomaly_markers(x, y, name="Anomalie"):
    import plotly.graph_objects as go
    return go.Scatter(x=x, y=y, name=name, mode="markers",
                      marker=dict(size=9, color=ROLE["anomalie"],
                                  line=dict(width=1.5, color="#FFFFFF")))


def threshold_line(fig, value, label="Schwellwert (95. Perzentil)"):
    fig.add_hline(y=value, line=dict(color=ROLE["schwellwert"], width=1, dash="3,3"),
                  annotation_text=label, annotation_position="top left",
                  annotation_font=dict(family=FONT, size=11, color=ROLE["schwellwert"]))
    return fig


def apply_matplotlib():
    """Point rcParams at the bundled .mplstyle and set the SWW cycle."""
    import os
    import matplotlib.pyplot as plt
    from cycler import cycler
    style = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sww_matplotlib.mplstyle")
    if os.path.exists(style):
        plt.style.use(style)
    plt.rcParams["axes.prop_cycle"] = cycler(color=QUALITATIVE)
    return plt
