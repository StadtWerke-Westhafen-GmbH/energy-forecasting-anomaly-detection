import React from "react";
import { Icon } from "./Icon.jsx";

const css = `
.sww-btn{display:inline-flex;align-items:center;justify-content:center;gap:var(--space-2);font-family:var(--font-sans);font-weight:var(--fw-medium);letter-spacing:var(--ls-tight);border-radius:var(--radius-control);border:1px solid transparent;cursor:pointer;white-space:nowrap;text-decoration:none;transition:var(--transition-control)}
.sww-btn:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-btn--sm{height:var(--control-height-sm);padding:0 var(--space-3);font-size:var(--fs-sm)}
.sww-btn--md{height:var(--control-height);padding:0 var(--space-4);font-size:var(--fs-base)}
.sww-btn--lg{height:var(--control-height-lg);padding:0 var(--space-5);font-size:var(--fs-md)}
.sww-btn--block{width:100%}
.sww-btn--primary{background:var(--navy-700);color:#fff;box-shadow:var(--shadow-xs)}
.sww-btn--primary:hover:not(:disabled){background:var(--navy-800)}
.sww-btn--primary:active:not(:disabled){background:var(--navy-900);box-shadow:none}
.sww-btn--accent{background:var(--teal-600);color:#fff;box-shadow:var(--shadow-xs)}
.sww-btn--accent:hover:not(:disabled){background:var(--teal-700)}
.sww-btn--accent:active:not(:disabled){background:var(--teal-700);box-shadow:none}
.sww-btn--secondary{background:var(--surface-card);color:var(--text-primary);border-color:var(--border-default);box-shadow:var(--shadow-xs)}
.sww-btn--secondary:hover:not(:disabled){background:var(--surface-hover);border-color:var(--border-strong)}
.sww-btn--secondary:active:not(:disabled){background:var(--surface-active);box-shadow:none}
.sww-btn--ghost{background:transparent;color:var(--text-accent)}
.sww-btn--ghost:hover:not(:disabled){background:var(--teal-100)}
.sww-btn--ghost:active:not(:disabled){background:var(--teal-200)}
.sww-btn--danger{background:var(--red-500);color:#fff}
.sww-btn--danger:hover:not(:disabled){background:var(--red-600)}
.sww-btn--danger:active:not(:disabled){background:var(--red-700)}
.sww-btn:disabled{cursor:not-allowed;background:var(--grey-50);color:var(--text-disabled);border-color:var(--border-subtle);box-shadow:none}
.sww-btn--onNavy.sww-btn--secondary{background:rgba(255,255,255,.1);color:#fff;border-color:var(--border-inverse);box-shadow:none}
.sww-btn--onNavy.sww-btn--secondary:hover:not(:disabled){background:rgba(255,255,255,.18);border-color:rgba(255,255,255,.3)}
.sww-btn--onNavy:focus-visible{box-shadow:var(--focus-ring-inverse)}
.sww-btn__spin{width:1em;height:1em;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:sww-btn-spin .7s linear infinite}
@keyframes sww-btn-spin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.sww-btn__spin{animation-duration:2s}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-button-css")) {
  const s = document.createElement("style"); s.id = "sww-button-css"; s.textContent = css; document.head.appendChild(s);
}

export function Button({
  variant = "primary", size = "md", icon, iconAfter, loading = false, fullWidth = false,
  onNavy = false, disabled = false, type = "button", href, children, className = "", ...rest
}) {
  const cls = [
    "sww-btn", `sww-btn--${variant}`, `sww-btn--${size}`,
    fullWidth && "sww-btn--block", onNavy && "sww-btn--onNavy", className,
  ].filter(Boolean).join(" ");
  const iconSize = size === "lg" ? 20 : 16;
  const inner = (
    <>
      {loading ? <span className="sww-btn__spin" /> : icon ? <Icon name={icon} size={iconSize} /> : null}
      {children}
      {iconAfter && !loading ? <Icon name={iconAfter} size={iconSize} /> : null}
    </>
  );
  if (href && !disabled) return <a className={cls} href={href} {...rest}>{inner}</a>;
  return <button className={cls} type={type} disabled={disabled || loading} {...rest}>{inner}</button>;
}
