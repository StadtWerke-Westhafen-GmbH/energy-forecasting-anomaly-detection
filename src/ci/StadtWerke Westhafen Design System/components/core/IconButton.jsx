import React from "react";
import { Icon } from "./Icon.jsx";

const css = `
.sww-iconbtn{display:inline-flex;align-items:center;justify-content:center;border-radius:var(--radius-control);border:1px solid transparent;background:transparent;color:var(--text-secondary);cursor:pointer;transition:var(--transition-control)}
.sww-iconbtn:hover:not(:disabled){background:var(--surface-hover);color:var(--text-primary)}
.sww-iconbtn:active:not(:disabled){background:var(--surface-active)}
.sww-iconbtn:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-iconbtn:disabled{cursor:not-allowed;color:var(--text-disabled);background:transparent}
.sww-iconbtn--sm{width:var(--control-height-sm);height:var(--control-height-sm)}
.sww-iconbtn--md{width:var(--control-height);height:var(--control-height)}
.sww-iconbtn--bordered{border-color:var(--border-default);background:var(--surface-card);box-shadow:var(--shadow-xs)}
.sww-iconbtn--bordered:hover:not(:disabled){border-color:var(--border-strong)}
.sww-iconbtn--onNavy{color:var(--navy-200)}
.sww-iconbtn--onNavy:hover:not(:disabled){background:rgba(255,255,255,.1);color:#fff}
.sww-iconbtn--onNavy:focus-visible{box-shadow:var(--focus-ring-inverse)}
.sww-iconbtn[aria-pressed="true"]{background:var(--surface-accent-subtle);color:var(--teal-700)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-iconbutton-css")) {
  const s = document.createElement("style"); s.id = "sww-iconbutton-css"; s.textContent = css; document.head.appendChild(s);
}

export function IconButton({ icon, label, size = "md", bordered = false, onNavy = false, pressed, className = "", ...rest }) {
  const cls = ["sww-iconbtn", `sww-iconbtn--${size}`, bordered && "sww-iconbtn--bordered", onNavy && "sww-iconbtn--onNavy", className].filter(Boolean).join(" ");
  return (
    <button className={cls} type="button" title={label} aria-label={label} aria-pressed={pressed} {...rest}>
      <Icon name={icon} size={size === "sm" ? 14 : 16} />
    </button>
  );
}
