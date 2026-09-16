import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-check{display:inline-flex;align-items:flex-start;gap:var(--space-2);cursor:pointer;font:var(--text-body);color:var(--text-primary)}
.sww-check--disabled{cursor:not-allowed;color:var(--text-disabled)}
.sww-check__box{position:relative;flex:none;width:16px;height:16px;margin-top:2px;border:1px solid var(--border-strong);border-radius:var(--radius-xs);background:var(--surface-card);display:grid;place-items:center;color:#fff;transition:var(--transition-control)}
.sww-check:hover .sww-check__box{border-color:var(--teal-500)}
.sww-check__in{position:absolute;inset:0;opacity:0;margin:0;cursor:inherit}
.sww-check__in:checked+.sww-check__box,.sww-check__in:indeterminate+.sww-check__box{background:var(--teal-500);border-color:var(--teal-500)}
.sww-check__in:focus-visible+.sww-check__box{box-shadow:var(--focus-ring)}
.sww-check__in:disabled+.sww-check__box{background:var(--grey-50);border-color:var(--border-default);color:var(--text-disabled)}
.sww-check__in:disabled:checked+.sww-check__box{background:var(--grey-300);border-color:var(--grey-300)}
.sww-check__wrap{position:relative;display:flex;align-items:flex-start}
.sww-check__txt{display:flex;flex-direction:column;gap:2px}
.sww-check__hint{font:var(--text-caption);color:var(--text-muted)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-checkbox-css")) {
  const s = document.createElement("style"); s.id = "sww-checkbox-css"; s.textContent = css; document.head.appendChild(s);
}

export function Checkbox({ label, hint, indeterminate = false, disabled = false, className = "", style, ...rest }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) ref.current.indeterminate = indeterminate; }, [indeterminate]);
  return (
    <label className={["sww-check", disabled && "sww-check--disabled", className].filter(Boolean).join(" ")} style={style}>
      <span className="sww-check__wrap">
        <input ref={ref} className="sww-check__in" type="checkbox" disabled={disabled} {...rest} />
        <span className="sww-check__box"><Icon name={indeterminate ? "minus" : "check"} size={12} /></span>
      </span>
      {label ? <span className="sww-check__txt">{label}{hint ? <span className="sww-check__hint">{hint}</span> : null}</span> : null}
    </label>
  );
}
