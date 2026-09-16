import React from "react";
import { Icon } from "./Icon.jsx";

const css = `
.sww-tag{display:inline-flex;align-items:center;gap:6px;border-radius:var(--radius-pill);border:1px solid var(--border-default);background:var(--surface-card);color:var(--text-secondary);font-family:var(--font-sans);font-size:var(--fs-xs);font-weight:var(--fw-medium);line-height:1;padding:5px 9px;transition:var(--transition-control)}
.sww-tag--clickable{cursor:pointer}
.sww-tag--clickable:hover{background:var(--surface-hover);border-color:var(--border-strong);color:var(--text-primary)}
.sww-tag--selected{background:var(--surface-accent-subtle);border-color:var(--teal-300);color:var(--teal-700)}
.sww-tag:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-tag__dot{width:7px;height:7px;border-radius:50%;flex:none}
.sww-tag__x{display:inline-flex;margin:-2px -3px -2px 1px;padding:2px;border:0;background:transparent;color:inherit;border-radius:var(--radius-pill);cursor:pointer;opacity:.7}
.sww-tag__x:hover{opacity:1;background:rgba(4,38,63,.08)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-tag-css")) {
  const s = document.createElement("style"); s.id = "sww-tag-css"; s.textContent = css; document.head.appendChild(s);
}

/** Fixed Kundentyp colours — identical to tokens/charts.css and sww_theme.py. */
export const KUNDENTYP_COLOR = { Gewerbe: "var(--chart-gewerbe)", Industrie: "var(--chart-industrie)", Kommunal: "var(--chart-kommunal)" };

export function Tag({ children, dotColor, icon, selected = false, onRemove, onClick, className = "", ...rest }) {
  const clickable = Boolean(onClick);
  const cls = ["sww-tag", clickable && "sww-tag--clickable", selected && "sww-tag--selected", className].filter(Boolean).join(" ");
  const Node = clickable ? "button" : "span";
  return (
    <Node className={cls} onClick={onClick} type={clickable ? "button" : undefined} {...rest}>
      {dotColor ? <span className="sww-tag__dot" style={{ background: dotColor }} /> : null}
      {icon ? <Icon name={icon} size={14} /> : null}
      {children}
      {onRemove ? (
        <button className="sww-tag__x" type="button" aria-label="Entfernen" onClick={(e) => { e.stopPropagation(); onRemove(e); }}>
          <Icon name="x" size={12} />
        </button>
      ) : null}
    </Node>
  );
}
