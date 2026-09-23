"""Build an inline explainer for the calibrated anomaly percentiles."""

from __future__ import annotations

import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "visualizations" / "perzentil-rangkurve.html"


def main() -> None:
    dashboard = runpy.run_path(str(ROOT / "scripts" / "build_anomaly_dashboard_data.py"))
    _, calibration, _ = dashboard["_model_results"]()
    values = sorted(round(float(value), 4) for value in calibration["abs_residuum_vls"])

    fragment = r'''
<div id="percentile-rank-explainer" class="percentile-rank-explainer">
  <h2>Sortierte historische Prognosefehler</h2>
  <div class="viz-controls">
    <label class="form-label" for="percentile-rank-control">
      Gewähltes Perzentil: <output id="percentile-rank-output" class="tabular-nums">97,5 %</output>
    </label>
    <input id="percentile-rank-control" class="form-range" type="range"
      min="90" max="99.5" step="0.5" value="97.5" aria-label="Perzentil auswählen">
  </div>
  <div id="percentile-rank-summary" class="percentile-rank-summary tabular-nums" aria-live="polite"></div>
  <svg id="percentile-rank-chart" class="percentile-rank-chart" role="img"
    aria-labelledby="percentile-rank-title percentile-rank-desc">
    <title id="percentile-rank-title">Rangkurve der absoluten VLS-Prognosefehler</title>
    <desc id="percentile-rank-desc">Alle Kalibrierungsfehler sind aufsteigend sortiert. Eine verstellbare Grenze zeigt das gewählte Perzentil und die darüberliegenden Fehler.</desc>
  </svg>
  <div class="percentile-rank-legend text-small" aria-label="Legende">
    <span><i class="percentile-rank-swatch percentile-rank-swatch-normal" aria-hidden="true"></i>bis zur Schwelle</span>
    <span><i class="percentile-rank-swatch percentile-rank-swatch-tail" aria-hidden="true"></i>oberhalb der Schwelle</span>
  </div>
  <div id="percentile-rank-tooltip" class="tooltip" role="tooltip" hidden></div>
</div>

<style>
  #percentile-rank-explainer { position: relative; width: 100%; }
  #percentile-rank-explainer .percentile-rank-summary { margin: .5rem 0 .75rem; color: var(--foreground); font-weight: 500; }
  #percentile-rank-explainer .percentile-rank-chart { display: block; width: 100%; min-height: 360px; overflow: visible; }
  #percentile-rank-explainer .percentile-rank-axis,
  #percentile-rank-explainer .percentile-rank-frame,
  #percentile-rank-explainer .percentile-rank-grid { fill: none; stroke: var(--border); }
  #percentile-rank-explainer .percentile-rank-grid { stroke-width: 1; opacity: .65; }
  #percentile-rank-explainer .percentile-rank-frame { stroke-width: 1; }
  #percentile-rank-explainer .percentile-rank-label,
  #percentile-rank-explainer .percentile-rank-tick,
  #percentile-rank-explainer .percentile-rank-annotation { fill: var(--foreground); font-size: 12px; }
  #percentile-rank-explainer .percentile-rank-tick { fill: var(--muted-foreground); }
  #percentile-rank-explainer .percentile-rank-base-line { fill: none; stroke: var(--viz-series-1); stroke-width: 2.5; }
  #percentile-rank-explainer .percentile-rank-tail-line { fill: none; stroke: var(--destructive); stroke-width: 3; }
  #percentile-rank-explainer .percentile-rank-tail-area { fill: var(--destructive); opacity: .07; }
  #percentile-rank-explainer .percentile-rank-threshold { stroke: var(--foreground); stroke-width: 1.5; stroke-dasharray: 5 4; }
  #percentile-rank-explainer .percentile-rank-guide { stroke: var(--muted-foreground); stroke-width: 1; }
  #percentile-rank-explainer .percentile-rank-marker { fill: var(--popover); stroke: var(--foreground); stroke-width: 2; }
  #percentile-rank-explainer .percentile-rank-hit { fill: transparent; }
  #percentile-rank-explainer .percentile-rank-legend { display: flex; flex-wrap: wrap; gap: 1rem; color: var(--muted-foreground); }
  #percentile-rank-explainer .percentile-rank-legend span { display: inline-flex; align-items: center; gap: .4rem; }
  #percentile-rank-explainer .percentile-rank-swatch { width: 1.25rem; height: .2rem; display: inline-block; }
  #percentile-rank-explainer .percentile-rank-swatch-normal { background: var(--viz-series-1); }
  #percentile-rank-explainer .percentile-rank-swatch-tail { background: var(--destructive); }
</style>

<script>
(() => {
  const root = document.getElementById("percentile-rank-explainer");
  const svg = document.getElementById("percentile-rank-chart");
  const control = document.getElementById("percentile-rank-control");
  const output = document.getElementById("percentile-rank-output");
  const summary = document.getElementById("percentile-rank-summary");
  const tooltip = document.getElementById("percentile-rank-tooltip");
  const values = __VALUES__;
  const ns = "http://www.w3.org/2000/svg";
  const de1 = new Intl.NumberFormat("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const de0 = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 0 });

  const saved = window.openai && window.openai.widgetState && window.openai.widgetState.modelContent;
  if (saved && Number(saved.percentile) >= 90 && Number(saved.percentile) <= 99.5) {
    control.value = String(saved.percentile);
  }

  function node(name, attrs = {}, text = "") {
    const item = document.createElementNS(ns, name);
    Object.entries(attrs).forEach(([key, value]) => item.setAttribute(key, String(value)));
    if (text) item.textContent = text;
    return item;
  }

  function quantile(percentile) {
    const position = (values.length - 1) * percentile / 100;
    const lower = Math.floor(position);
    const upper = Math.ceil(position);
    const weight = position - lower;
    return values[lower] * (1 - weight) + values[upper] * weight;
  }

  function niceTicks(maximum, count) {
    const rough = maximum / count;
    const power = 10 ** Math.floor(Math.log10(rough));
    const ratio = rough / power;
    const multiple = ratio >= 5 ? 5 : ratio >= 2 ? 2 : 1;
    const step = multiple * power;
    const ticks = [];
    for (let value = 0; value <= maximum + step / 2; value += step) ticks.push(value);
    return ticks;
  }

  function pathFor(points, x, y) {
    return points.map((point, index) => `${index ? "L" : "M"}${x(point.p).toFixed(2)},${y(point.v).toFixed(2)}`).join(" ");
  }

  function draw() {
    const percentile = Number(control.value);
    const threshold = quantile(percentile);
    const below = values.filter((value) => value <= threshold).length;
    const above = values.length - below;
    output.value = `${de1.format(percentile)} %`;
    output.textContent = output.value;
    summary.textContent = `${de0.format(below)} von ${de0.format(values.length)} Fehlern liegen bis ${de1.format(threshold)} VLS-h · ${de0.format(above)} liegen darüber`;

    const width = Math.max(320, Math.round(root.getBoundingClientRect().width));
    const height = width < 480 ? 380 : 420;
    const margin = width < 480 ? { top: 28, right: 16, bottom: 64, left: 62 } : { top: 28, right: 24, bottom: 64, left: 72 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const maxValue = Math.max(...values) * 1.06;
    const x = (p) => margin.left + p / 100 * innerWidth;
    const y = (v) => margin.top + innerHeight - v / maxValue * innerHeight;
    const all = values.map((v, index) => ({ p: index / (values.length - 1) * 100, v }));
    const position = (values.length - 1) * percentile / 100;
    const lower = Math.floor(position);
    const upper = Math.ceil(position);
    const cutoff = { p: percentile, v: threshold };
    const base = [...all.slice(0, lower + 1), cutoff];
    const tail = [cutoff, ...all.slice(upper)];

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("height", String(height));
    while (svg.lastChild && !["title", "desc"].includes(svg.lastChild.tagName)) svg.removeChild(svg.lastChild);

    const yTicks = niceTicks(maxValue, 5);
    yTicks.forEach((tick) => {
      if (tick > maxValue) return;
      svg.appendChild(node("line", { class: "percentile-rank-grid", x1: margin.left, x2: width - margin.right, y1: y(tick), y2: y(tick) }));
      svg.appendChild(node("text", { class: "percentile-rank-tick", x: margin.left - 10, y: y(tick) + 4, "text-anchor": "end" }, de0.format(tick)));
    });
    const xTicks = width < 480 ? [0, 50, 100] : [0, 25, 50, 75, 100];
    xTicks.forEach((tick) => {
      svg.appendChild(node("text", { class: "percentile-rank-tick", x: x(tick), y: height - margin.bottom + 24, "text-anchor": tick === 0 ? "start" : tick === 100 ? "end" : "middle" }, `${de0.format(tick)} %`));
    });

    svg.appendChild(node("rect", { class: "percentile-rank-tail-area", x: x(percentile), y: margin.top, width: x(100) - x(percentile), height: innerHeight }));
    svg.appendChild(node("rect", { class: "percentile-rank-frame", "data-chart-frame": "", x: margin.left, y: margin.top, width: innerWidth, height: innerHeight }));
    svg.appendChild(node("path", { class: "percentile-rank-base-line", d: pathFor(base, x, y) }));
    svg.appendChild(node("path", { class: "percentile-rank-tail-line", d: pathFor(tail, x, y) }));
    svg.appendChild(node("line", { class: "percentile-rank-threshold", x1: x(percentile), x2: x(percentile), y1: margin.top, y2: margin.top + innerHeight }));
    svg.appendChild(node("line", { class: "percentile-rank-threshold", x1: margin.left, x2: width - margin.right, y1: y(threshold), y2: y(threshold) }));
    svg.appendChild(node("circle", { cx: x(percentile), cy: y(threshold), r: 5, fill: "var(--destructive)" }));

    const anchor = percentile > 82 ? "end" : "start";
    const labelX = x(percentile) + (anchor === "end" ? -7 : 7);
    svg.appendChild(node("text", { class: "percentile-rank-annotation", x: labelX, y: margin.top + 15, "text-anchor": anchor }, `${de1.format(percentile)}. Perzentil`));
    svg.appendChild(node("text", { class: "percentile-rank-annotation", x: margin.left + 6, y: Math.max(margin.top + 30, y(threshold) - 8), "text-anchor": "start" }, `Schwelle ${de1.format(threshold)} VLS-h`));
    svg.appendChild(node("text", { class: "percentile-rank-label", "data-axis": "x", x: margin.left + innerWidth / 2, y: height - 13, "text-anchor": "middle" }, "Anteil der sortierten Kalibrierungsfehler"));
    const yLabel = node("text", { class: "percentile-rank-label", "data-axis": "y", x: 15, y: margin.top + innerHeight / 2, "text-anchor": "middle", transform: `rotate(-90 15 ${margin.top + innerHeight / 2})` }, "Absolute Abweichung (VLS-h)");
    svg.appendChild(yLabel);

    const guide = node("line", { class: "percentile-rank-guide", y1: margin.top, y2: margin.top + innerHeight, visibility: "hidden", "data-chart-hover-guide": "" });
    const marker = node("circle", { class: "percentile-rank-marker", r: 4, visibility: "hidden", "data-chart-hover-marker": "" });
    const hit = node("rect", { class: "percentile-rank-hit", x: margin.left, y: margin.top, width: innerWidth, height: innerHeight, "data-chart-hit": "", "data-chart-hover-overlay": "cross-series" });
    svg.appendChild(guide); svg.appendChild(marker); svg.appendChild(hit);

    hit.addEventListener("pointermove", (event) => {
      const rect = svg.getBoundingClientRect();
      const svgX = (event.clientX - rect.left) / rect.width * width;
      const pct = Math.max(0, Math.min(100, (svgX - margin.left) / innerWidth * 100));
      const index = Math.max(0, Math.min(values.length - 1, Math.round(pct / 100 * (values.length - 1))));
      const pointPct = index / (values.length - 1) * 100;
      guide.setAttribute("x1", x(pointPct)); guide.setAttribute("x2", x(pointPct)); guide.setAttribute("visibility", "visible");
      marker.setAttribute("cx", x(pointPct)); marker.setAttribute("cy", y(values[index])); marker.setAttribute("visibility", "visible");
      tooltip.hidden = false;
      tooltip.textContent = `Rang ${de0.format(index + 1)} von ${de0.format(values.length)} · ${de1.format(pointPct)} % · ${de1.format(values[index])} VLS-h`;
      const rootRect = root.getBoundingClientRect();
      const left = Math.min(rootRect.width - 220, Math.max(4, event.clientX - rootRect.left + 12));
      const top = Math.max(4, event.clientY - rootRect.top - 42);
      tooltip.style.left = `${left}px`; tooltip.style.top = `${top}px`;
    });
    hit.addEventListener("pointerleave", () => {
      guide.setAttribute("visibility", "hidden"); marker.setAttribute("visibility", "hidden"); tooltip.hidden = true;
    });
  }

  control.addEventListener("input", draw);
  control.addEventListener("change", () => {
    if (window.openai && window.openai.setWidgetState) {
      window.openai.setWidgetState({ modelContent: { percentile: Number(control.value) }, privateContent: null }).catch(() => {});
    }
  });
  window.addEventListener("openai:set_globals", (event) => {
    const state = event.detail && event.detail.globals && event.detail.globals.widgetState;
    const percentile = state && state.modelContent && Number(state.modelContent.percentile);
    if (percentile >= 90 && percentile <= 99.5) { control.value = String(percentile); draw(); }
  });
  new ResizeObserver(draw).observe(root);
  draw();
})();
</script>
'''.strip()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(fragment.replace("__VALUES__", json.dumps(values)), encoding="utf-8")
    print(f"Wrote {len(values)} sorted calibration errors to {OUTPUT}")


if __name__ == "__main__":
    main()
