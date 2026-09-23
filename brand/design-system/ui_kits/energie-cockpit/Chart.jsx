/* Plotly wrapper that applies the SWW template from assets/plotly/. */
const SWW_PLOT = window.SWWTokens.plotly.layout;

function deepClone(value) {
  if (Array.isArray(value)) return value.map(deepClone);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, deepClone(item)]));
  }
  return value;
}

function deepMerge(a, b) {
  const out = deepClone(a || {});
  Object.keys(b || {}).forEach((k) => {
    out[k] = b[k] && typeof b[k] === "object" && !Array.isArray(b[k])
      && a && typeof a[k] === "object"
      ? deepMerge(a[k] || {}, b[k])
      : deepClone(b[k]);
  });
  return out;
}

function Chart({ data, layout = {}, height = 260, config }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!ref.current || !window.Plotly) return;
    const el = ref.current;
    let raf = 0;
    let drawing = false;
    let redrawRequested = false;
    let disposed = false;
    const schedule = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(draw);
    };
    const draw = async () => {
      if (drawing) {
        redrawRequested = true;
        return;
      }
      drawing = true;
      const w = el.clientWidth || (el.parentElement && el.parentElement.clientWidth) || 600;
      try {
        await window.Plotly.react(
          el,
          deepClone(data),
          deepMerge(deepMerge(SWW_PLOT, { height, width: w, autosize: false }), layout),
          { displayModeBar: false, responsive: false, ...config },
        );
      } finally {
        drawing = false;
        if (redrawRequested && !disposed) {
          redrawRequested = false;
          schedule();
        }
      }
    };
    const ro = new ResizeObserver(schedule);
    ro.observe(el);
    schedule();
    return () => {
      disposed = true;
      ro.disconnect();
      cancelAnimationFrame(raf);
      window.Plotly.purge(el);
    };
  }, [data, layout, height, config]);
  return <div ref={ref} style={{ width: "100%", height, minWidth: 0, overflow: "hidden" }} />;
}

const ROLE = { ...window.SWWTokens.roles, schwelle: window.SWWTokens.roles.schwellwert };
const KT = window.SWWTokens.customers;

Object.assign(window, { Chart, SWW_PLOT, ROLE, KT });
