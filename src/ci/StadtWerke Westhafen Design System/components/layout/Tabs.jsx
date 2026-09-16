import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-tabs{display:flex;align-items:stretch;gap:var(--space-5);border-bottom:1px solid var(--border-default)}
.sww-tabs__t{position:relative;display:inline-flex;align-items:center;gap:var(--space-2);padding:0 2px var(--space-3);border:0;background:transparent;font:var(--text-label);font-size:var(--fs-base);color:var(--text-secondary);cursor:pointer;transition:var(--transition-control)}
.sww-tabs__t:hover{color:var(--text-primary)}
.sww-tabs__t:focus-visible{outline:none;box-shadow:var(--focus-ring);border-radius:var(--radius-xs)}
.sww-tabs__t[aria-selected="true"]{color:var(--text-brand);font-weight:var(--fw-semibold)}
.sww-tabs__t[aria-selected="true"]::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:var(--teal-500);border-radius:2px 2px 0 0}
.sww-tabs__t:disabled{color:var(--text-disabled);cursor:not-allowed}
.sww-tabs__n{font:var(--text-data);font-size:var(--fs-2xs);background:var(--grey-100);color:var(--text-secondary);border-radius:var(--radius-pill);padding:2px 6px}
.sww-tabs__t[aria-selected="true"] .sww-tabs__n{background:var(--surface-accent-subtle);color:var(--teal-700)}
.sww-tabs--pills{border-bottom:0;gap:var(--space-1);background:var(--grey-100);padding:3px;border-radius:var(--radius-control);display:inline-flex}
.sww-tabs--pills .sww-tabs__t{padding:6px var(--space-3);border-radius:var(--radius-sm)}
.sww-tabs--pills .sww-tabs__t[aria-selected="true"]{background:var(--surface-card);box-shadow:var(--shadow-xs)}
.sww-tabs--pills .sww-tabs__t[aria-selected="true"]::after{display:none}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-tabs-css")) {
  const s = document.createElement("style"); s.id = "sww-tabs-css"; s.textContent = css; document.head.appendChild(s);
}

export function Tabs({ items = [], value, onChange, variant = "underline", className = "", ...rest }) {
  return (
    <div className={["sww-tabs", variant === "pills" && "sww-tabs--pills", className].filter(Boolean).join(" ")} role="tablist" {...rest}>
      {items.map((it) => (
        <button key={it.id} className="sww-tabs__t" role="tab" type="button"
          aria-selected={it.id === value} disabled={it.disabled}
          onClick={() => onChange && onChange(it.id)}>
          {it.icon ? <Icon name={it.icon} size={16} /> : null}
          {it.label}
          {it.count != null ? <span className="sww-tabs__n">{it.count}</span> : null}
        </button>
      ))}
    </div>
  );
}
