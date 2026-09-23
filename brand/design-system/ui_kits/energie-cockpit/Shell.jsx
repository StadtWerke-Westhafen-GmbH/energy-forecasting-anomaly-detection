const { SidebarNav, IconButton, Select, Badge, Icon } = window.StadtWerkeWesthafenDesignSystem_acd94c;

const NAV = [
  { id: "uebersicht", label: "Übersicht", icon: "layout-dashboard", group: "Betrieb" },
  { id: "anomalien", label: "Anomalieprüfung", icon: "triangle-alert", group: "Betrieb", alert: true },
  { id: "zaehler", label: "Prüffall", icon: "gauge", group: "Betrieb" },
  { id: "beschaffung", label: "Beschaffung", icon: "shopping-cart", group: "Planung" },
  { id: "qualitaet", label: "Datenqualität", icon: "database", group: "Planung" },
];

function TopBar({ title, onMonthChange, monat, screen }) {
  const anomalyMode = screen === "anomalien" || screen === "zaehler";
  return (
    <header style={{
      height: "var(--topbar-height)", flex: "none", display: "flex", alignItems: "center", gap: "var(--space-4)",
      padding: "0 var(--gutter-page)", background: "var(--surface-card)", borderBottom: "1px solid var(--border-default)",
    }}>
      <span style={{ font: "var(--text-h4)", color: "var(--text-primary)" }}>{title}</span>
      <Badge status="neutral" size="sm" icon="calendar">{anomalyMode ? "Benchmark 2025" : monat}</Badge>
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
        {!anomalyMode ? <Select size="sm" aria-label="Beispielmonat" value={monat} onChange={(e) => onMonthChange(e.target.value)}
          options={["03/2025"]} style={{ width: 130 }} /> : null}
        <a href="../../index.html" style={{font:'var(--text-caption)'}}>Designsystem</a>
        <span style={{ width: 1, height: 24, background: "var(--border-default)" }} />
        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{
            width: 28, height: 28, borderRadius: "50%", background: "var(--navy-100)", color: "var(--navy-800)",
            display: "grid", placeItems: "center", font: "var(--text-label)", fontSize: "var(--fs-xs)",
          }}>HM</span>
          <span style={{ font: "var(--text-caption)", color: "var(--text-secondary)" }}>Henrik Maaß</span>
        </span>
      </div>
    </header>
  );
}

function Shell({ screen, onNavigate, title, monat, onMonthChange, children }) {
  const { metrik } = window.SWWData;
  const anomaly = window.SWWAnomalyData;
  const anomalyMode = screen === "anomalien" || screen === "zaehler";
  const navItems = NAV.map((item) => item.id === "anomalien"
    ? { ...item, count: anomaly.summary.alerts_total }
    : item);
  return (
    <div className="sww-app" style={{ display: "flex", height: "100vh", overflow: "hidden", background: "var(--surface-page)" }}>
      <SidebarNav items={navItems} value={screen} onChange={onNavigate}
        logoSrc="../../assets/logo-sww-wordmark.png" markSrc="../../assets/logo-sww-emblem.png"
        footer={anomalyMode
          ? <>{anomaly.meta.model_version}<br />Retrospektiv · Stand {anomaly.meta.as_of}</>
          : <>Modell {metrik.version} · {metrik.modell}<br />Stand {metrik.stand}</>} />
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <TopBar title={title} monat={monat} onMonthChange={onMonthChange} screen={screen} />
        <div className="sww-demo-note">{anomalyMode
          ? "Retrospektive Projektdaten 2025 · Keine Live-Anbindung · Bewertungen bleiben lokal in diesem Browser"
          : "Designvorlage · Synthetische Beispieldaten · Keine Live-Prognosen oder Ticketübermittlung"}</div>
        <main id="main-content" tabIndex={-1} style={{ flex: 1, overflow: "auto", padding: "var(--space-6) var(--gutter-page) var(--space-10)" }}>
          <div style={{ maxWidth: "var(--content-max)", margin: "0 auto" }}>{children}</div>
        </main>
      </div>
    </div>
  );
}

Object.assign(window, { Shell, TopBar, NAV });
