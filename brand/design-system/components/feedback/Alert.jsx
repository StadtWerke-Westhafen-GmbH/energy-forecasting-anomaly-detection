import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-alert{display:flex;gap:var(--space-3);padding:var(--space-3) var(--space-4);border:1px solid;border-radius:var(--radius-control);font:var(--text-body)}
.sww-alert__ico{flex:none;margin-top:1px}
.sww-alert__bd{min-width:0;flex:1}
.sww-alert__ttl{font:var(--text-h4);font-size:var(--fs-base);margin:0 0 2px}
.sww-alert__txt{margin:0;color:var(--text-secondary);text-wrap:pretty}
.sww-alert__act{margin-top:var(--space-3);display:flex;gap:var(--space-2)}
.sww-alert__x{flex:none;align-self:flex-start;border:0;background:transparent;color:inherit;opacity:.6;cursor:pointer;padding:2px;border-radius:var(--radius-sm)}
.sww-alert__x:hover{opacity:1;background:rgba(4,38,63,.07)}
.sww-alert--info{background:var(--status-info-bg);border-color:var(--status-info-border);color:var(--teal-700)}
.sww-alert--ok{background:var(--status-ok-bg);border-color:var(--status-ok-border);color:var(--green-700)}
.sww-alert--warn{background:var(--status-warn-bg);border-color:var(--status-warn-border);color:var(--amber-700)}
.sww-alert--critical{background:var(--status-critical-bg);border-color:var(--status-critical-border);color:var(--red-600)}
.sww-alert--neutral{background:var(--surface-sunken);border-color:var(--border-default);color:var(--text-primary)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-alert-css")) {
  const s = document.createElement("style"); s.id = "sww-alert-css"; s.textContent = css; document.head.appendChild(s);
}

const DEFAULT_ICON = { info: "info", ok: "circle-check", warn: "triangle-alert", critical: "octagon-alert", neutral: "info" };

export function Alert({ status = "info", title, icon, actions, onDismiss, children, className = "", ...rest }) {
  return (
    <div className={["sww-alert", `sww-alert--${status}`, className].filter(Boolean).join(" ")} role={status === "critical" ? "alert" : "status"} {...rest}>
      <Icon className="sww-alert__ico" name={icon || DEFAULT_ICON[status]} size={16} />
      <div className="sww-alert__bd">
        {title ? <p className="sww-alert__ttl">{title}</p> : null}
        {children ? <p className="sww-alert__txt">{children}</p> : null}
        {actions ? <div className="sww-alert__act">{actions}</div> : null}
      </div>
      {onDismiss ? <button className="sww-alert__x" type="button" aria-label="Schließen" onClick={onDismiss}><Icon name="x" size={14} /></button> : null}
    </div>
  );
}
