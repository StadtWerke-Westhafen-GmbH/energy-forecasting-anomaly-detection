import React from "react";

const css = `
.sww-spark{display:block;overflow:visible}
.sww-spark__wrap{display:inline-flex;align-items:center;gap:var(--space-2)}
.sww-spark__val{font:var(--text-data);color:var(--text-secondary);font-variant-numeric:tabular-nums}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-sparkline-css")) {
  const s = document.createElement("style"); s.id = "sww-sparkline-css"; s.textContent = css; document.head.appendChild(s);
}

function path(values, w, h, pad) {
  const min = Math.min(...values), max = Math.max(...values);
  const span = max - min || 1;
  const step = values.length > 1 ? (w - pad * 2) / (values.length - 1) : 0;
  return values.map((v, i) => {
    const x = pad + i * step;
    const y = pad + (h - pad * 2) * (1 - (v - min) / span);
    return `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(" ");
}

export function Sparkline({
  values = [], forecast, width = 88, height = 28, color = "var(--data-actual)",
  forecastColor = "var(--data-forecast)", markLast = true, anomalyIndices = [], className = "", ...rest
}) {
  if (!values.length) return null;
  const pad = 3;
  const all = forecast ? values.concat(forecast) : values;
  const min = Math.min(...all), max = Math.max(...all), span = max - min || 1;
  const step = all.length > 1 ? (width - pad * 2) / (all.length - 1) : 0;
  const pt = (v, i) => [pad + i * step, pad + (height - pad * 2) * (1 - (v - min) / span)];
  const d = values.map((v, i) => { const [x, y] = pt(v, i); return `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`; }).join(" ");
  const fd = forecast
    ? forecast.map((v, i) => { const [x, y] = pt(v, values.length - 1 + i + (i === 0 ? 0 : 0)); return `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`; }).join(" ")
    : null;
  const [lx, ly] = pt(values[values.length - 1], values.length - 1);
  return (
    <svg className={`sww-spark ${className}`} width={width} height={height} viewBox={`0 0 ${width} ${height}`}
      role="img" aria-hidden="true" {...rest}>
      <path d={d} fill="none" stroke={color} strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
      {fd ? <path d={fd} fill="none" stroke={forecastColor} strokeWidth="1.75" strokeDasharray="4 2" strokeLinecap="round" /> : null}
      {anomalyIndices.map((i) => { const [x, y] = pt(values[i], i); return <circle key={i} cx={x} cy={y} r="2.75" fill="var(--data-anomaly)" stroke="#fff" strokeWidth="1" />; })}
      {markLast ? <circle cx={lx} cy={ly} r="2.25" fill={color} /> : null}
    </svg>
  );
}

Sparkline.pathFor = path;
