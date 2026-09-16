import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-dlg__scrim{position:fixed;inset:0;background:var(--scrim);backdrop-filter:var(--blur-scrim);display:grid;place-items:center;padding:var(--space-6);z-index:60;animation:sww-dlg-fade var(--dur-base) var(--ease-out)}
.sww-dlg{width:100%;background:var(--surface-card);border-radius:var(--radius-xl);box-shadow:var(--shadow-overlay);display:flex;flex-direction:column;max-height:86vh;animation:sww-dlg-in var(--dur-base) var(--ease-out)}
.sww-dlg--sm{max-width:420px}.sww-dlg--md{max-width:560px}.sww-dlg--lg{max-width:820px}
.sww-dlg__hd{display:flex;align-items:flex-start;gap:var(--space-3);padding:var(--space-5) var(--space-6) var(--space-4)}
.sww-dlg__ttl{font:var(--text-h3);margin:0;color:var(--text-primary)}
.sww-dlg__sub{font:var(--text-caption);color:var(--text-muted);margin:4px 0 0}
.sww-dlg__x{margin-left:auto;border:0;background:transparent;color:var(--text-muted);cursor:pointer;padding:4px;border-radius:var(--radius-sm)}
.sww-dlg__x:hover{background:var(--surface-hover);color:var(--text-primary)}
.sww-dlg__bd{padding:0 var(--space-6) var(--space-5);overflow:auto;font:var(--text-body);color:var(--text-secondary)}
.sww-dlg__ft{display:flex;align-items:center;gap:var(--space-2);justify-content:flex-end;padding:var(--space-4) var(--space-6);border-top:1px solid var(--border-subtle);background:var(--surface-sunken);border-radius:0 0 var(--radius-xl) var(--radius-xl)}
@keyframes sww-dlg-fade{from{opacity:0}to{opacity:1}}
@keyframes sww-dlg-in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.sww-dlg,.sww-dlg__scrim{animation:none}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-dialog-css")) {
  const s = document.createElement("style"); s.id = "sww-dialog-css"; s.textContent = css; document.head.appendChild(s);
}

export function Dialog({ open = false, title, subtitle, size = "md", footer, onClose, children, className = "", ...rest }) {
  React.useEffect(() => {
    if (!open || !onClose) return;
    const h = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", h);
    return () => document.removeEventListener("keydown", h);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="sww-dlg__scrim" onClick={onClose ? (e) => { if (e.target === e.currentTarget) onClose(); } : undefined}>
      <div className={["sww-dlg", `sww-dlg--${size}`, className].filter(Boolean).join(" ")} role="dialog" aria-modal="true" aria-label={typeof title === "string" ? title : undefined} {...rest}>
        <header className="sww-dlg__hd">
          <div style={{ minWidth: 0 }}>
            <h2 className="sww-dlg__ttl">{title}</h2>
            {subtitle ? <p className="sww-dlg__sub">{subtitle}</p> : null}
          </div>
          {onClose ? <button className="sww-dlg__x" type="button" aria-label="Schließen" onClick={onClose}><Icon name="x" size={18} /></button> : null}
        </header>
        <div className="sww-dlg__bd">{children}</div>
        {footer ? <footer className="sww-dlg__ft">{footer}</footer> : null}
      </div>
    </div>
  );
}
