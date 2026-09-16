import React from "react";

const css = `
.sww-switch{display:inline-flex;align-items:center;gap:var(--space-3);cursor:pointer;font:var(--text-body);color:var(--text-primary)}
.sww-switch--disabled{cursor:not-allowed;color:var(--text-disabled)}
.sww-switch__wrap{position:relative;flex:none;width:34px;height:20px}
.sww-switch__in{position:absolute;inset:0;opacity:0;margin:0;cursor:inherit}
.sww-switch__track{position:absolute;inset:0;background:var(--grey-300);border-radius:var(--radius-pill);transition:background-color var(--dur-fast) var(--ease-standard)}
.sww-switch__knob{position:absolute;top:2px;left:2px;width:16px;height:16px;background:#fff;border-radius:50%;box-shadow:var(--shadow-sm);transition:transform var(--dur-fast) var(--ease-standard)}
.sww-switch__in:checked~.sww-switch__track{background:var(--teal-500)}
.sww-switch__in:checked~.sww-switch__knob{transform:translateX(14px)}
.sww-switch__in:focus-visible~.sww-switch__track{box-shadow:var(--focus-ring)}
.sww-switch__in:disabled~.sww-switch__track{background:var(--grey-200)}
.sww-switch__txt{display:flex;flex-direction:column;gap:2px}
.sww-switch__hint{font:var(--text-caption);color:var(--text-muted)}
@media (prefers-reduced-motion:reduce){.sww-switch__knob{transition:none}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-switch-css")) {
  const s = document.createElement("style"); s.id = "sww-switch-css"; s.textContent = css; document.head.appendChild(s);
}

export function Switch({ label, hint, disabled = false, className = "", style, ...rest }) {
  return (
    <label className={["sww-switch", disabled && "sww-switch--disabled", className].filter(Boolean).join(" ")} style={style}>
      <span className="sww-switch__wrap">
        <input className="sww-switch__in" type="checkbox" role="switch" disabled={disabled} {...rest} />
        <span className="sww-switch__track" />
        <span className="sww-switch__knob" />
      </span>
      {label ? <span className="sww-switch__txt">{label}{hint ? <span className="sww-switch__hint">{hint}</span> : null}</span> : null}
    </label>
  );
}
