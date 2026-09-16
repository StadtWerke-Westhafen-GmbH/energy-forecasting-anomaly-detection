"""Execute the SWW notebook in a fresh kernel and export an offline HTML review.

Run with: uv run --all-extras --with nbclient --with nbconvert python scripts/check_eda_ci_notebook.py
Only the generated CI notebook and ignored .build previews are written.
"""

import hashlib
from html import escape
import os
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient
from nbconvert.filters.markdown import markdown2html
import plotly.io as pio
from plotly.offline import get_plotlyjs

from energy_analytics.visualization import theme
from energy_analytics.visualization import notebook as ci

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ipynb/eda_ci.ipynb"
PROTECTED = [
    ROOT / name for name in ("ipynb/eda.ipynb", "viz.py", "data/raw/verbrauch_bereinigt.csv")
]


def main():
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in PROTECTED}
    notebook = nbformat.read(TARGET, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        allow_errors=False,
        resources={"metadata": {"path": str(TARGET.parent)}},
    )
    client.km = client.create_kernel_manager()
    client.km.kernel_spec.argv = [
        sys.executable,
        "-m",
        "ipykernel_launcher",
        "-f",
        "{connection_file}",
    ]
    client.on_cell_start = lambda cell, cell_index: (
        print(f"Execute {cell_index + 1}/{len(notebook.cells)}: {cell.id}", flush=True)
        if cell.cell_type == "code"
        else None
    )
    kernel_env = dict(os.environ, IPYTHONDIR=str(ROOT / ".build/ipython"))
    client.execute(env=kernel_env)
    plots = []
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            assert output.output_type != "error"
            figure = output.get("data", {}).get("application/vnd.plotly.v1+json")
            if figure:
                assert figure["layout"]["meta"]["sww"]["period"] == "01/2024–12/2025"
                assert "IBM Plex Sans" in figure["layout"]["font"]["family"]
                plots.append(figure)
    assert len(plots) == 32, f"Unexpected chart count: {len(plots)}"
    nbformat.validate(notebook)
    for path, digest in before.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path
    nbformat.write(notebook, TARGET)
    destination = ROOT / ".build/eda-ci"
    destination.mkdir(parents=True, exist_ok=True)
    parts = []
    cover = []
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            parts.append('<section class="sww-copy">' + markdown2html(cell.source) + "</section>")
        for output in cell.get("outputs", []):
            data = output.get("data", {})
            if "application/vnd.plotly.v1+json" in data:
                figure_html = pio.to_html(
                    data["application/vnd.plotly.v1+json"],
                    full_html=False,
                    include_plotlyjs=False,
                    config={"displaylogo": False, "responsive": True},
                )
                parts.append('<section class="sww-report sww-chart">' + figure_html + "</section>")
            elif "text/html" in data and "<script" not in data["text/html"]:
                if 'class="sww-report sww-cover"' in data["text/html"]:
                    cover.append(data["text/html"])
                elif "<table" in data["text/html"] and 'class="sww-table"' not in data["text/html"]:
                    parts.append('<div class="sww-table">' + data["text/html"] + "</div>")
                else:
                    parts.append(data["text/html"])
            elif output.output_type == "stream":
                parts.append(
                    '<details class="sww-log"><summary>Ausführungsprotokoll</summary><pre>'
                    + escape(output.text) + "</pre></details>"
                )
            elif "text/plain" in data and "<IPython.core.display" not in data["text/plain"]:
                parts.append("<pre>" + escape(data["text/plain"]) + "</pre>")
    chapters = dict.fromkeys(
        (f["layout"]["meta"]["sww"].get("chapter"),
         f["layout"]["meta"]["sww"].get("chapter_title")) for f in plots
    )
    navigation = '<nav class="sww-navigation" aria-label="Analyseabschnitte">' + "".join(
        f'<a href="#sww-chapter-{escape(number, quote=True)}">'
        f'<span>{escape(number)}</span>{escape(title)}</a>'
        for number, title in chapters if number
    ) + "</nav>"
    t = theme.TOKENS
    head = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>SWW · Explorative Datenanalyse</title>{theme.notebook_css()}{ci.notebook_css()}
    <style>body{{margin:0;background:{t["surface-page"]};color:{t["text-primary"]};font-family:{theme.FONT}}}
    main{{max-width:1120px;padding:32px 24px;margin:auto}}.sww-copy{{line-height:1.65;margin:32px 0;overflow-wrap:anywhere}}
    .sww-copy table{{display:block;overflow-x:auto}}
    h1,h2,h3{{color:{t["text-brand"]}}}h2{{margin-top:48px}}a{{color:{t["text-accent"]}}}
    .anchor-link{{display:none}}details{{font-size:13px;margin:12px 0}}
    summary{{cursor:pointer;color:{t["text-brand"]};font-weight:500;line-height:1.6}}
    details[open]{{padding-bottom:16px}}summary:focus-visible,a:focus-visible{{outline:3px solid {t["text-accent"]};outline-offset:4px}}
    .sww-navigation{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:20px 0 32px}}
    .sww-navigation a{{display:flex;align-items:center;gap:12px;padding:12px 16px;
      border:1px solid {t["border-default"]};border-radius:6px;background:{t["surface-card"]};
      text-decoration:none;color:{t["text-brand"]};font-size:13px;font-weight:500}}
    .sww-navigation a:hover{{background:{t["surface-accent-subtle"]};border-color:{t["border-accent"]}}}
    .sww-navigation span{{font-size:11px;color:{t["text-accent"]}}}
    .sww-chapter{{scroll-margin-top:24px}}
    pre{{overflow:auto;font-size:12px;background:{t["surface-card"]};padding:16px;border-radius:10px}}
    table{{border-collapse:collapse;max-width:100%;font-size:13px}}th,td{{padding:8px 12px;border-bottom:1px solid {t["border-default"]}}}
    th{{text-align:left}}.sww-chart{{padding:0;overflow:hidden}}.sww-chart .plotly-graph-div{{width:100%!important}}
    @media(max-width:800px){{main{{padding:16px 12px}}.sww-navigation{{grid-template-columns:repeat(2,minmax(0,1fr))}}
      .sww-chart{{overflow-x:auto}}.sww-chart .plotly-graph-div{{min-width:760px}}}}
    </style><script>{get_plotlyjs()}</script></head><body><main>"""
    (destination / "eda_ci.html").write_text(
        head + "\n".join(cover) + navigation + "\n".join(parts) + "</main></body></html>", encoding="utf-8"
    )
    print(
        f"Executed {sum(c.cell_type == 'code' for c in notebook.cells)} code cells; validated {len(plots)} charts."
    )
    print(
        "Original notebook, viz.py and data unchanged. Offline preview: .build/eda-ci/eda_ci.html"
    )


if __name__ == "__main__":
    main()
