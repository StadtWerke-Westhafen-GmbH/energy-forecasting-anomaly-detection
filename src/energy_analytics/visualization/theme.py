"""SWW Plotly and Matplotlib themes from the canonical brand tokens."""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DATA = json.loads((_HERE / "_tokens.json").read_text(encoding="utf-8"))
TOKENS = _DATA["tokens"]
ROLE = _DATA["roles"]
KUNDENTYP_COLORS = _DATA["customers"]
QUALITATIVE = _DATA["palette"]
SEQUENTIAL = _DATA["sequential"]
DIVERGING = _DATA["diverging"]
FONT = TOKENS["font-chart"]
FONT_MONO = FONT
NAVY, NAVY_900 = TOKENS["navy-700"], TOKENS["navy-900"]
TEAL, CYAN, GREEN = TOKENS["teal-500"], TOKENS["cyan-500"], TOKENS["green-500"]
AMBER, RED = ROLE["schwellwert"], ROLE["anomalie"]
GREY_100, GREY_300 = TOKENS["grey-100"], TOKENS["grey-300"]
GREY_400, GREY_500, GREY_600 = TOKENS["grey-400"], TOKENS["grey-500"], TOKENS["grey-600"]
GREY_50, INK = TOKENS["grey-50"], TOKENS["text-primary"]


def template():
    import plotly.graph_objects as go

    return go.layout.Template(_DATA["plotly"])


def register(activate=True, name="sww"):
    import plotly.io as pio

    pio.templates[name] = template()
    if activate:
        pio.templates.default = name
    return pio.templates[name]


def forecast_traces(x, ist, prognose, lower=None, upper=None):
    import plotly.graph_objects as go

    x, ist, prognose = list(x), list(ist), list(prognose)
    if len(x) != len(ist) or len(x) != len(prognose):
        raise ValueError("x, ist and prognose must have equal lengths")
    if (lower is None) != (upper is None):
        raise ValueError("Provide both lower and upper prediction bounds")
    traces = []
    if lower is not None:
        lower, upper = list(lower), list(upper)
        if len(lower) != len(x) or len(upper) != len(x):
            raise ValueError("Prediction bounds must match x")
        if any(lo > hi for lo, hi in zip(lower, upper)):
            raise ValueError("Lower prediction bound exceeds upper bound")
        traces.append(
            go.Scatter(
                x=x + x[::-1],
                y=upper + lower[::-1],
                fill="toself",
                fillcolor=ROLE["band"],
                line=dict(width=0),
                hoverinfo="skip",
                name="Prognoseintervall",
            )
        )
    traces.extend(
        [
            go.Scatter(
                x=x,
                y=ist,
                name="Ist",
                mode="lines+markers",
                line=dict(color=ROLE["ist"], width=2),
                marker=dict(size=6),
            ),
            go.Scatter(
                x=x,
                y=prognose,
                name="Prognose",
                mode="lines",
                line=dict(color=ROLE["prognose"], width=2, dash="4,2"),
            ),
        ]
    )
    return traces


def anomaly_markers(x, y, name="Anomalie"):
    import plotly.graph_objects as go

    return go.Scatter(
        x=x,
        y=y,
        name=name,
        mode="markers",
        marker=dict(
            size=9, color=ROLE["anomalie"], line=dict(width=1.5, color=TOKENS["surface-card"])
        ),
    )


def threshold_line(fig, value, label="Schwellwert (95. Perzentil)"):
    fig.add_hline(
        y=value,
        line=dict(color=ROLE["schwellwert"], width=1, dash="3,3"),
        annotation_text=label,
        annotation_position="top left",
        annotation_font=dict(family=FONT, size=12, color=ROLE["schwellwert"]),
    )
    return fig


def apply_matplotlib():
    """Activate the local style and bundled fonts without changing system locale."""
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    for font in (_HERE / "fonts").glob("*.ttf"):
        font_manager.fontManager.addfont(str(font))
    plt.style.use(_HERE / "sww.mplstyle")
    return plt


def format_matplotlib_axes(ax, decimals=0):
    """Apply German formatting to the numeric y-axis, independently of OS locale."""
    from matplotlib.ticker import FuncFormatter

    def formatter(value, _position):
        return f"{value:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")

    ax.yaxis.set_major_formatter(FuncFormatter(formatter))
    return ax


def notebook_css():
    """Self-contained font CSS for IPython.display.HTML; no remote font requests."""
    import base64

    rules = []
    for weight in (400, 500, 600, 700):
        font = _HERE / f"fonts/ibm-plex-sans-{weight}.ttf"
        if font.exists():
            data = base64.b64encode(font.read_bytes()).decode("ascii")
            rules.append(
                f'@font-face{{font-family:"IBM Plex Sans";font-weight:{weight};src:url(data:font/ttf;base64,{data}) format("truetype");}}'
            )
    return "<style>" + "\n".join(rules) + "</style>"
