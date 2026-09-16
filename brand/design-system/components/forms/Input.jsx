import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-field{display:flex;flex-direction:column;gap:6px;min-width:0}
.sww-field__label{font:var(--text-label);color:var(--text-secondary)}
.sww-field__req{color:var(--red-500);margin-left:2px}
.sww-field__hint{font:var(--text-caption);color:var(--text-muted)}
.sww-field__err{font:var(--text-caption);color:var(--red-600);display:flex;align-items:center;gap:4px}
.sww-input{display:flex;align-items:center;gap:var(--space-2);height:var(--control-height);padding:0 var(--space-3);background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-control);color:var(--text-primary);transition:var(--transition-control)}
.sww-input:hover{border-color:var(--border-strong)}
.sww-input:focus-within{border-color:var(--border-accent);box-shadow:var(--focus-ring)}
.sww-input--sm{height:var(--control-height-sm);padding:0 var(--space-2);font-size:var(--fs-sm)}
.sww-input--invalid{border-color:var(--red-500)}
.sww-input--invalid:focus-within{box-shadow:0 0 0 3px rgba(179,38,30,.25)}
.sww-input--disabled{background:var(--grey-50);border-color:var(--border-subtle);color:var(--text-disabled);cursor:not-allowed}
.sww-input__el{flex:1;min-width:0;border:0;background:transparent;outline:none;font:var(--text-body);color:inherit}
.sww-input__el::placeholder{color:var(--text-muted)}
.sww-input__el:disabled{cursor:not-allowed}
.sww-input--numeric .sww-input__el{font-family:var(--font-mono);font-variant-numeric:tabular-nums;text-align:right}
.sww-input__affix{font:var(--text-data);color:var(--text-muted);flex:none}
.sww-input__ico{color:var(--text-muted);flex:none}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-input-css")) {
  const s = document.createElement("style"); s.id = "sww-input-css"; s.textContent = css; document.head.appendChild(s);
}

export function Input({
  label, hint, error, required = false, size = "md", icon, suffix, numeric = false,
  disabled = false, id, className = "", style, ...rest
}) {
  const autoId = React.useId();
  const uid = id || `sww-in-${autoId}`;
  const cls = ["sww-input", `sww-input--${size}`, numeric && "sww-input--numeric", error && "sww-input--invalid", disabled && "sww-input--disabled", className].filter(Boolean).join(" ");
  return (
    <div className="sww-field" style={style}>
      {label ? <label className="sww-field__label" htmlFor={uid}>{label}{required ? <span className="sww-field__req">*</span> : null}</label> : null}
      <div className={cls}>
        {icon ? <Icon className="sww-input__ico" name={icon} size={16} /> : null}
        <input className="sww-input__el" id={uid} required={required} disabled={disabled} aria-invalid={error ? true : undefined} aria-describedby={error || hint ? `${uid}-message` : undefined} {...rest} />
        {suffix ? <span className="sww-input__affix">{suffix}</span> : null}
      </div>
      {error ? <span id={`${uid}-message`} className="sww-field__err"><Icon name="triangle-alert" size={12} />{error}</span>
        : hint ? <span id={`${uid}-message`} className="sww-field__hint">{hint}</span> : null}
    </div>
  );
}
