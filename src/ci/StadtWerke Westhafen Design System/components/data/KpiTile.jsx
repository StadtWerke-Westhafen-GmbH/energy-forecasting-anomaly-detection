import React from "react";
import { Icon } from "../core/Icon.jsx";
import { Sparkline } from "./Sparkline.jsx";

const css = `
.sww-kpi{container-type:inline-size;display:flex;flex-direction:column;gap:var(--space-2);min-width:0;overflow:hidden;background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-card);box-shadow:var(--shadow-card);padding:var(--space-4) var(--gutter-card)}
.sww-kpi__top{display:flex;align-items:center;gap:var(--space-2);color:var(--text-muted)}
.sww-kpi__lbl{font:var(--text-label);color:var(--text-secondary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sww-kpi__val{display:flex;align-items:baseline;gap:6px;white-space:nowrap;font:var(--text-metric);letter-spacing:var(--ls-tighter);color:var(--text-primary);font-variant-numeric:tabular-nums}
.sww-kpi__unit{font:var(--text-label);font-size:var(--fs-base);color:var(--text-muted);font-family:var(--font-mono)}
.sww-kpi__row{display:flex;align-items:center;gap:var(--space-3);margin-top:2px;min-width:0;overflow:hidden}
.sww-kpi__delta{display:inline-flex;align-items:center;gap:3px;flex:none;white-space:nowrap;font:var(--text-data);font-weight:var(--fw-medium);font-variant-numeric:tabular-nums}
.sww-kpi__delta--up{color:var(--red-600)}
.sww-kpi__delta--down{color:var(--green-700)}
.sww-kpi__delta--flat{color:var(--text-muted)}
.sww-kpi__delta--good{color:var(--green-700)}
.sww-kpi__delta--bad{color:var(--red-600)}
.sww-kpi__ref{font:var(--text-caption);color:var(--text-muted);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sww-kpi__spark{margin-left:auto;flex:0 1 88px;min-width:0;overflow:hidden;line-height:0}
.sww-kpi__spark svg{display:block;width:100%;height:auto;max-width:88px}
@container (max-width:120px){.sww-kpi__spark{display:none}}
.sww-kpi--accent{background:var(--navy-800);border-color:var(--navy-900);box-shadow:none}
.sww-kpi--accent .sww-kpi__lbl,.sww-kpi--accent .sww-kpi__top{color:var(--navy-200)}
.sww-kpi--accent .sww-kpi__val{color:#fff}
.sww-kpi--accent .sww-kpi__unit,.sww-kpi--accent .sww-kpi__ref{color:var(--navy-300)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-kpi-css")) {
  const s = document.createElement("style"); s.id = "sww-kpi-css"; s.textContent = css; document.head.appendChild(s);
}

export function KpiTile({
  label, value, unit, delta, deltaDirection, deltaTone, reference, icon,
  spark, sparkForecast, variant = "default", className = "", ...rest
}) {
  const dir = deltaDirection || (delta == null ? null : String(delta).trim().startsWith("−") || String(delta).trim().startsWith("-") ? "down" : "up");
  const toneCls = deltaTone ? `sww-kpi__delta--${deltaTone}` : `sww-kpi__delta--${dir || "flat"}`;
  return (
    <div className={["sww-kpi", variant === "accent" && "sww-kpi--accent", className].filter(Boolean).join(" ")} {...rest}>
      <div className="sww-kpi__top">
        {icon ? <Icon name={icon} size={16} /> : null}
        <span className="sww-kpi__lbl">{label}</span>
      </div>
      <div className="sww-kpi__val">{value}{unit ? <span className="sww-kpi__unit">{unit}</span> : null}</div>
      <div className="sww-kpi__row">
        {delta != null ? (
          <span className={`sww-kpi__delta ${toneCls}`}>
            {dir === "up" ? <Icon name="arrow-up-right" size={13} /> : dir === "down" ? <Icon name="arrow-down-right" size={13} /> : null}
            {delta}
          </span>
        ) : null}
        {reference ? <span className="sww-kpi__ref">{reference}</span> : null}
        {spark ? <span className="sww-kpi__spark"><Sparkline values={spark} forecast={sparkForecast}
          color={variant === "accent" ? "var(--teal-300)" : "var(--data-actual)"} /></span> : null}
      </div>
    </div>
  );
}
