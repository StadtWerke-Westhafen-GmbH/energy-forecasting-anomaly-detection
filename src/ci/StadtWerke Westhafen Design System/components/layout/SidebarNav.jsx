import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-sb{display:flex;flex-direction:column;width:var(--sidebar-width);flex:none;background:var(--navy-800);color:#fff;height:100%;overflow:hidden}
.sww-sb--collapsed{width:var(--sidebar-width-collapsed)}
.sww-sb__brand{display:flex;align-items:center;gap:var(--space-3);padding:var(--space-4);border-bottom:1px solid var(--border-inverse);min-height:var(--topbar-height);box-sizing:border-box}
.sww-sb__logo{background:#fff;border-radius:var(--radius-sm);padding:5px 7px;display:block}
.sww-sb__logo img{display:block;height:24px;width:auto}
.sww-sb__mark{background:#fff;border-radius:var(--radius-sm);padding:3px;display:grid;place-items:center}
.sww-sb__mark img{display:block;height:26px;width:auto}
.sww-sb__grp{font:var(--text-overline);letter-spacing:var(--ls-caps);text-transform:uppercase;color:var(--navy-300);padding:var(--space-5) var(--space-4) var(--space-2)}
.sww-sb__list{list-style:none;margin:0;padding:var(--space-2) var(--space-2) 0;display:flex;flex-direction:column;gap:2px;overflow-y:auto}
.sww-sb__i{display:flex;align-items:center;gap:var(--space-3);width:100%;padding:0 var(--space-3);height:var(--control-height);border:0;background:transparent;color:var(--navy-100);font:var(--text-label);font-size:var(--fs-base);text-align:left;border-radius:var(--radius-control);cursor:pointer;transition:var(--transition-control)}
.sww-sb__i:hover{background:rgba(255,255,255,.08);color:#fff}
.sww-sb__i:focus-visible{outline:none;box-shadow:var(--focus-ring-inverse)}
.sww-sb__i[aria-current="page"]{background:var(--teal-600);color:#fff;font-weight:var(--fw-semibold)}
.sww-sb__n{margin-left:auto;font:var(--text-data);font-size:var(--fs-2xs);background:rgba(255,255,255,.14);border-radius:var(--radius-pill);padding:2px 6px}
.sww-sb__i[aria-current="page"] .sww-sb__n{background:rgba(255,255,255,.22)}
.sww-sb__n--alert{background:var(--red-500)}
.sww-sb__ft{margin-top:auto;padding:var(--space-4);border-top:1px solid var(--border-inverse);font:var(--text-caption);color:var(--navy-300)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-sidebar-css")) {
  const s = document.createElement("style"); s.id = "sww-sidebar-css"; s.textContent = css; document.head.appendChild(s);
}

export function SidebarNav({
  items = [], value, onChange, collapsed = false, footer,
  logoSrc = "assets/logo-sww-wordmark.png", markSrc = "assets/logo-sww-emblem.png",
  className = "", ...rest
}) {
  const groups = [];
  items.forEach((it) => {
    const g = it.group || "";
    const last = groups[groups.length - 1];
    if (last && last.name === g) last.items.push(it); else groups.push({ name: g, items: [it] });
  });
  return (
    <nav className={["sww-sb", collapsed && "sww-sb--collapsed", className].filter(Boolean).join(" ")} {...rest}>
      <div className="sww-sb__brand">
        {collapsed
          ? <span className="sww-sb__mark"><img src={markSrc} alt="SWW" /></span>
          : <span className="sww-sb__logo"><img src={logoSrc} alt="StadtWerke Westhafen GmbH" /></span>}
      </div>
      {groups.map((g, gi) => (
        <React.Fragment key={g.name || gi}>
          {g.name && !collapsed ? <div className="sww-sb__grp">{g.name}</div> : null}
          <ul className="sww-sb__list">
            {g.items.map((it) => (
              <li key={it.id}>
                <button className="sww-sb__i" type="button" title={it.label}
                  aria-current={it.id === value ? "page" : undefined}
                  onClick={() => onChange && onChange(it.id)}>
                  <Icon name={it.icon} size={20} />
                  {collapsed ? null : it.label}
                  {!collapsed && it.count != null
                    ? <span className={`sww-sb__n${it.alert ? " sww-sb__n--alert" : ""}`}>{it.count}</span>
                    : null}
                </button>
              </li>
            ))}
          </ul>
        </React.Fragment>
      ))}
      {footer && !collapsed ? <div className="sww-sb__ft">{footer}</div> : null}
    </nav>
  );
}
