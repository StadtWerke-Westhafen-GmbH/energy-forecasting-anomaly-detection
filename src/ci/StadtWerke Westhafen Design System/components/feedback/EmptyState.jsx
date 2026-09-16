import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-empty{display:flex;flex-direction:column;align-items:center;text-align:center;gap:var(--space-2);padding:var(--space-12) var(--space-6);color:var(--text-secondary)}
.sww-empty--sm{padding:var(--space-8) var(--space-4)}
.sww-empty__ico{display:grid;place-items:center;width:44px;height:44px;border-radius:var(--radius-pill);background:var(--surface-sunken);border:1px solid var(--border-subtle);color:var(--text-muted);margin-bottom:var(--space-2)}
.sww-empty__ttl{font:var(--text-h4);color:var(--text-primary);margin:0}
.sww-empty__txt{font:var(--text-body);color:var(--text-muted);margin:0;max-width:52ch;text-wrap:pretty}
.sww-empty__act{margin-top:var(--space-4);display:flex;gap:var(--space-2)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-empty-css")) {
  const s = document.createElement("style"); s.id = "sww-empty-css"; s.textContent = css; document.head.appendChild(s);
}

export function EmptyState({ icon = "inbox", title, children, actions, size = "md", className = "", ...rest }) {
  return (
    <div className={["sww-empty", size === "sm" && "sww-empty--sm", className].filter(Boolean).join(" ")} {...rest}>
      <span className="sww-empty__ico"><Icon name={icon} size={24} /></span>
      <p className="sww-empty__ttl">{title}</p>
      {children ? <p className="sww-empty__txt">{children}</p> : null}
      {actions ? <div className="sww-empty__act">{actions}</div> : null}
    </div>
  );
}
