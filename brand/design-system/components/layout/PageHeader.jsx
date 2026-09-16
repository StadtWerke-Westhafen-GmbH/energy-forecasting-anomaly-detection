import React from "react";

const css = `
.sww-ph{display:flex;align-items:flex-end;gap:var(--space-4);flex-wrap:wrap;padding-bottom:var(--space-5);border-bottom:1px solid var(--border-default);margin-bottom:var(--space-6)}
.sww-ph--plain{border-bottom:0;padding-bottom:0;margin-bottom:var(--space-5)}
.sww-ph__eyebrow{font:var(--text-overline);letter-spacing:var(--ls-caps);text-transform:uppercase;color:var(--text-accent);margin:0 0 6px}
.sww-ph__ttl{font:var(--text-h1);letter-spacing:var(--ls-tighter);color:var(--text-primary);margin:0}
.sww-ph__sub{font:var(--text-body);color:var(--text-secondary);margin:6px 0 0;max-width:72ch;text-wrap:pretty}
.sww-ph__meta{display:flex;align-items:center;gap:var(--space-3);margin-top:var(--space-3);font:var(--text-caption);color:var(--text-muted);flex-wrap:wrap}
.sww-ph__act{margin-left:auto;display:flex;align-items:center;gap:var(--space-2);flex-wrap:wrap}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-pageheader-css")) {
  const s = document.createElement("style"); s.id = "sww-pageheader-css"; s.textContent = css; document.head.appendChild(s);
}

export function PageHeader({ eyebrow, title, subtitle, meta, actions, plain = false, className = "", ...rest }) {
  return (
    <header className={["sww-ph", plain && "sww-ph--plain", className].filter(Boolean).join(" ")} {...rest}>
      <div style={{ minWidth: 0 }}>
        {eyebrow ? <p className="sww-ph__eyebrow">{eyebrow}</p> : null}
        <h1 className="sww-ph__ttl">{title}</h1>
        {subtitle ? <p className="sww-ph__sub">{subtitle}</p> : null}
        {meta ? <div className="sww-ph__meta">{meta}</div> : null}
      </div>
      {actions ? <div className="sww-ph__act">{actions}</div> : null}
    </header>
  );
}
