import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-select{position:relative;display:flex;align-items:center;height:var(--control-height);background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-control);transition:var(--transition-control)}
.sww-select:hover{border-color:var(--border-strong)}
.sww-select:focus-within{border-color:var(--border-accent);box-shadow:var(--focus-ring)}
.sww-select--sm{height:var(--control-height-sm)}
.sww-select--disabled{background:var(--grey-50);border-color:var(--border-subtle);cursor:not-allowed}
.sww-select__el{appearance:none;-webkit-appearance:none;flex:1;min-width:0;height:100%;border:0;outline:none;background:transparent;font:var(--text-body);color:var(--text-primary);padding:0 32px 0 var(--space-3);cursor:pointer}
.sww-select--sm .sww-select__el{font-size:var(--fs-sm);padding:0 28px 0 var(--space-2)}
.sww-select__el:disabled{color:var(--text-disabled);cursor:not-allowed}
.sww-select__chev{position:absolute;right:10px;color:var(--text-muted);pointer-events:none}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-select-css")) {
  const s = document.createElement("style"); s.id = "sww-select-css"; s.textContent = css; document.head.appendChild(s);
}

export function Select({ label, hint, error, options = [], size = "md", disabled = false, id, className = "", style, children, ...rest }) {
  const autoId = React.useId();
  const uid = id || `sww-sel-${autoId}`;
  const cls = ["sww-select", `sww-select--${size}`, disabled && "sww-select--disabled", className].filter(Boolean).join(" ");
  return (
    <div className="sww-field" style={style}>
      {label ? <label className="sww-field__label" htmlFor={uid}>{label}</label> : null}
      <div className={cls}>
        <select className="sww-select__el" id={uid} disabled={disabled} aria-invalid={error ? true : undefined} aria-describedby={error || hint ? `${uid}-message` : undefined} {...rest}>
          {children || options.map((o) => {
            const opt = typeof o === "string" ? { value: o, label: o } : o;
            return <option key={opt.value} value={opt.value}>{opt.label}</option>;
          })}
        </select>
        <Icon className="sww-select__chev" name="chevron-down" size={16} />
      </div>
      {error ? <span id={`${uid}-message`} className="sww-field__err"><Icon name="triangle-alert" size={12} />{error}</span>
        : hint ? <span id={`${uid}-message`} className="sww-field__hint">{hint}</span> : null}
    </div>
  );
}
