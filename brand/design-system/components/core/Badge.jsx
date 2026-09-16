import React from "react";
import { Icon } from "./Icon.jsx";

const css = `
.sww-badge{display:inline-flex;align-items:center;gap:var(--space-1);border-radius:var(--radius-pill);border:1px solid;font-family:var(--font-sans);font-weight:var(--fw-medium);font-size:var(--fs-xs);line-height:1;padding:4px 8px 4px 7px;white-space:nowrap}
.sww-badge--sm{font-size:var(--fs-2xs);padding:3px 7px 3px 6px}
.sww-badge--ok{background:var(--status-ok-bg);border-color:var(--status-ok-border);color:var(--green-700)}
.sww-badge--warn{background:var(--status-warn-bg);border-color:var(--status-warn-border);color:var(--amber-700)}
.sww-badge--critical{background:var(--status-critical-bg);border-color:var(--status-critical-border);color:var(--red-600)}
.sww-badge--info{background:var(--status-info-bg);border-color:var(--status-info-border);color:var(--teal-700)}
.sww-badge--neutral{background:var(--status-neutral-bg);border-color:var(--status-neutral-border);color:var(--grey-600)}
.sww-badge--brand{background:var(--surface-brand-subtle);border-color:var(--navy-200);color:var(--navy-800)}
.sww-badge--solid{border-color:transparent;color:#fff}
.sww-badge--solid.sww-badge--ok{background:var(--status-ok)}
.sww-badge--solid.sww-badge--warn{background:var(--amber-600)}
.sww-badge--solid.sww-badge--critical{background:var(--red-500)}
.sww-badge--solid.sww-badge--info{background:var(--teal-600)}
.sww-badge--solid.sww-badge--neutral{background:var(--grey-500)}
.sww-badge--solid.sww-badge--brand{background:var(--navy-700)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-badge-css")) {
  const s = document.createElement("style"); s.id = "sww-badge-css"; s.textContent = css; document.head.appendChild(s);
}

/** Anomaly severity vocabulary — see readme.md > CONTENT FUNDAMENTALS. */
export const SEVERITY = {
  geprueft: { status: "ok", icon: "check", label: "Geprüft" },
  hinweis: { status: "info", icon: "info", label: "Hinweis" },
  auffaellig: { status: "warn", icon: "triangle-alert", label: "Auffällig" },
  kritisch: { status: "critical", icon: "octagon-alert", label: "Kritisch" },
};

export function Badge({ status = "neutral", size = "md", icon, solid = false, children, className = "", ...rest }) {
  const cls = ["sww-badge", `sww-badge--${status}`, `sww-badge--${size}`, solid && "sww-badge--solid", className].filter(Boolean).join(" ");
  return (
    <span className={cls} {...rest}>
      {icon ? <Icon name={icon} size={14} /> : null}
      {children}
    </span>
  );
}
