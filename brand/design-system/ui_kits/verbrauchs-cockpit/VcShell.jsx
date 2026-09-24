const { SidebarNav } = window.StadtWerkeWesthafenDesignSystem_acd94c;

/* Beschaffung plans the next month; Netzmanagement works the list, then each case. */
const VC_NAV = [
  { id: "prognose", label: "Verbrauchsprognose", icon: "chart-line", group: "Beschaffung" },
  { id: "anomalien", label: "Prüfhinweise", icon: "triangle-alert", group: "Netzmanagement", alert: true },
  { id: "prueffall", label: "Prüffall", icon: "search", group: "Netzmanagement" },
];

function VcShell({ screen, onNavigate, title, help, filters, children }) {
  const { meta } = DATA;
  const items = VC_NAV.map((item) => (item.id === "anomalien" ? { ...item, count: DATA.alerts.length } : item));
  return (
    <div className="sww-app" style={{ display: "flex", height: "100vh", overflow: "hidden", background: "var(--surface-page)" }}>
      <SidebarNav items={items} value={screen} onChange={onNavigate}
        logoSrc="../../assets/logo-sww-wordmark.png" markSrc="../../assets/logo-sww-emblem.png"
        footer={<>{meta.model}<br />Datenstand {meta.as_of}</>} />
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <header style={{
          height: "var(--topbar-height)", flex: "none", display: "flex", alignItems: "center", gap: "var(--space-4)",
          padding: "0 var(--gutter-page)", background: "var(--surface-card)", borderBottom: "1px solid var(--border-default)",
        }}>
          <h1 style={{ font: "var(--text-h1)", color: "var(--text-primary)", margin: 0 }}>{title}</h1>
          {help ? <HelpTip label={help.label} heading={help.label}>{help.text}</HelpTip> : null}
          <div className="vc-header-filters">{filters}</div>
        </header>
        <main id="main-content" tabIndex={-1} style={{ flex: 1, overflow: "auto", padding: "var(--space-6) var(--gutter-page) var(--space-10)" }}>
          <div style={{ maxWidth: "var(--content-max)", margin: "0 auto" }}>{children}</div>
        </main>
      </div>
    </div>
  );
}

Object.assign(window, { VcShell, VC_NAV });
