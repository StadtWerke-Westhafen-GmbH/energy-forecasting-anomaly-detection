import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-card{display:flex;flex-direction:column;min-width:0;background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-card);box-shadow:var(--shadow-card)}
.sww-card--flat{box-shadow:none}
.sww-card--sunken{background:var(--surface-sunken)}
.sww-card--interactive{cursor:pointer;transition:box-shadow var(--dur-fast) var(--ease-standard),border-color var(--dur-fast) var(--ease-standard)}
.sww-card--interactive:hover{box-shadow:var(--shadow-raised);border-color:var(--border-strong)}
.sww-card--interactive:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-card__rule{height:3px;border-radius:var(--radius-card) var(--radius-card) 0 0;margin:-1px -1px 0}
.sww-card__hd{display:flex;align-items:center;gap:var(--space-3);padding:var(--space-4) var(--gutter-card);border-bottom:1px solid var(--border-subtle)}
.sww-card__ttl{font:var(--text-h4);color:var(--text-primary);margin:0}
.sww-card__sub{font:var(--text-caption);color:var(--text-muted);margin:2px 0 0}
.sww-card__act{margin-left:auto;display:flex;align-items:center;gap:var(--space-2)}
.sww-card__bd{padding:var(--gutter-card);flex:1;min-width:0}
.sww-card__bd--flush{padding:0}
.sww-card__ft{padding:var(--space-3) var(--gutter-card);border-top:1px solid var(--border-subtle);font:var(--text-caption);color:var(--text-muted);display:flex;align-items:center;gap:var(--space-3)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-card-css")) {
  const s = document.createElement("style"); s.id = "sww-card-css"; s.textContent = css; document.head.appendChild(s);
}

const RULE = { ok: "var(--status-ok)", warn: "var(--status-warn)", critical: "var(--status-critical)", info: "var(--status-info)", brand: "var(--navy-700)" };

export function Card({
  title, subtitle, icon, actions, footer, status, variant = "default",
  interactive = false, flush = false, children, className = "", ...rest
}) {
  const cls = ["sww-card", variant !== "default" && `sww-card--${variant}`, interactive && "sww-card--interactive", className].filter(Boolean).join(" ");
  return (
    <section className={cls} tabIndex={interactive ? 0 : undefined} {...rest}>
      {status ? <div className="sww-card__rule" style={{ background: RULE[status] }} /> : null}
      {title ? (
        <header className="sww-card__hd">
          {icon ? <Icon name={icon} size={16} style={{ color: "var(--text-muted)" }} /> : null}
          <div style={{ minWidth: 0 }}>
            <h3 className="sww-card__ttl">{title}</h3>
            {subtitle ? <p className="sww-card__sub">{subtitle}</p> : null}
          </div>
          {actions ? <div className="sww-card__act">{actions}</div> : null}
        </header>
      ) : null}
      <div className={`sww-card__bd${flush ? " sww-card__bd--flush" : ""}`}>{children}</div>
      {footer ? <footer className="sww-card__ft">{footer}</footer> : null}
    </section>
  );
}
