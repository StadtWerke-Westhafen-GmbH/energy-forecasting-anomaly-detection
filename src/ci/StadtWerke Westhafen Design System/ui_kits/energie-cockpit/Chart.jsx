/* Plotly wrapper that applies the SWW template from assets/plotly/. */
const SWW_PLOT = {
  font: { family: "IBM Plex Sans, Segoe UI, sans-serif", size: 12, color: "#141A21" },
  paper_bgcolor: "#FFFFFF",
  plot_bgcolor: "#FFFFFF",
  colorway: ["#084878", "#0080A0", "#58A858", "#0090C8", "#C77E11", "#6CC0D2", "#4E5A68", "#B3261E"],
  separators: ",.",
  margin: { l: 58, r: 18, t: 14, b: 36 },
  hovermode: "x unified",
  hoverlabel: { bgcolor: "#FFFFFF", bordercolor: "#E4E9EF", font: { family: "IBM Plex Sans, sans-serif", size: 12, color: "#141A21" } },
  legend: { orientation: "h", yanchor: "bottom", y: 1.02, xanchor: "left", x: 0, font: { size: 12, color: "#6B7887" } },
  xaxis: { showgrid: false, zeroline: false, showline: true, linecolor: "#E4E9EF", ticks: "outside", ticklen: 4, tickcolor: "#E4E9EF", tickfont: { family: "IBM Plex Sans, sans-serif", size: 11, color: "#6B7887" } },
  yaxis: { showgrid: true, gridcolor: "#E4E9EF", zeroline: false, showline: false, tickformat: ",d", separatethousands: true, tickfont: { family: "IBM Plex Sans, sans-serif", size: 11, color: "#6B7887" }, title: { font: { size: 12, color: "#6B7887" } } },
  bargap: 0.36,
  barcornerradius: 4,
};

function deepMerge(a, b) {
  const out = Array.isArray(a) ? a.slice() : { ...a };
  Object.keys(b || {}).forEach((k) => {
    out[k] = b[k] && typeof b[k] === "object" && !Array.isArray(b[k]) && a && typeof a[k] === "object" ? deepMerge(a[k] || {}, b[k]) : b[k];
  });
  return out;
}

function Chart({ data, layout = {}, height = 260, config }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!ref.current || !window.Plotly) return;
    const el = ref.current;
    let raf = 0;
    const draw = () => {
      const w = el.clientWidth || (el.parentElement && el.parentElement.clientWidth) || 600;
      window.Plotly.react(el, data, deepMerge(deepMerge(SWW_PLOT, { height, width: w, autosize: false }), layout), {
        displayModeBar: false, responsive: false, ...config,
      });
    };
    const ro = new ResizeObserver(() => { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); });
    ro.observe(el);
    draw();
    return () => { ro.disconnect(); cancelAnimationFrame(raf); window.Plotly.purge(el); };
  }, [data, layout, height]);
  return <div ref={ref} style={{ width: "100%", height, minWidth: 0, overflow: "hidden" }} />;
}

const ROLE = { ist: "#084878", prognose: "#0090C8", band: "rgba(0,144,200,0.16)", residuum: "#0080A0", schwelle: "#C77E11", anomalie: "#B3261E" };
const KT = { Gewerbe: "#0080A0", Industrie: "#084878", Kommunal: "#58A858" };

Object.assign(window, { Chart, SWW_PLOT, ROLE, KT });
