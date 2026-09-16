/* Plotly wrapper that applies the SWW template from assets/plotly/. */
const SWW_PLOT = window.SWWTokens.plotly.layout;

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
  }, [data, layout, height, config]);
  return <div ref={ref} style={{ width: "100%", height, minWidth: 0, overflow: "hidden" }} />;
}

const ROLE = { ...window.SWWTokens.roles, schwelle: window.SWWTokens.roles.schwellwert };
const KT = window.SWWTokens.customers;

Object.assign(window, { Chart, SWW_PLOT, ROLE, KT });
