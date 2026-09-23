const { PageHeader, Card, KpiTile, DataTable, Badge, Button, Alert, StatusDot, Tag } = window.StadtWerkeWesthafenDesignSystem_acd94c;

function DatenqualitaetScreen() {
  const D = window.SWWData;
  const stufen = [
    { schritt: "Rohdaten", zeilen: 16800 }, { schritt: "Duplikate entfernt", zeilen: 16762 },
    { schritt: "Negative Verbräuche entfernt", zeilen: 16751 }, { schritt: "Einheiten vereinheitlicht", zeilen: 16751 },
    { schritt: "Analytische Tabelle", zeilen: 16751 },
  ];
  return (
    <>
      <PageHeader eyebrow="Planung" title="Datenqualität"
        subtitle="Befunde der Qualitätsprüfung auf data/verbrauch.csv (700 Zähler × 24 Monate, UTF-8 mit BOM)."
        meta={<><span>16.800 Beobachtungen</span><span>·</span><span>Januar 2024 – Dezember 2025</span><span>·</span><span>Prüfung {D.metrik.stand}</span></>}
        actions={<><Button variant="secondary" icon="download" disabled>Prüfprotokoll</Button><Button variant="primary" icon="refresh-cw" disabled>Prüfung erneut ausführen</Button></>} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <KpiTile label="Beobachtungen" value="16.800" reference="700 Zähler × 24 Monate" icon="database" />
        <KpiTile label="Nach Bereinigung" value="16.751" delta="−49" deltaTone="flat" reference="0,3 % entfernt" icon="check" />
        <KpiTile label="Befunde offen" value="3" delta="−5" deltaTone="good" reference="vs. Erstprüfung" icon="triangle-alert" />
        <KpiTile label="Fehlende Zielwerte" value="0" unit="%" reference="verbrauch_kwh vollständig" icon="zap" />
      </div>

      <Alert status="critical" title="11 negative Verbräuche entfernt" style={{ marginBottom: "var(--space-4)" }}
        actions={<Button size="sm" variant="secondary" icon="ticket" disabled>Tickets ansehen</Button>}>
        Physikalisch unmögliche Werte in verbrauch_kwh. Zeilen aus dem Trainingssatz entfernt und als Zählerdefekt an Netzmanagement gemeldet.
      </Alert>

      <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <Card title="Befunde je Spalte" icon="database" flush
          actions={<Badge status="warn" size="sm" icon="triangle-alert">3 offen</Badge>}>
          <DataTable compact rowKey="k" rows={D.datenqualitaet.map((d, i) => ({ ...d, k: i }))}
            columns={[
              { key: "spalte", label: "Spalte", mono: true, width: 210 },
              { key: "typ", label: "Typ", width: 90 },
              { key: "befund", label: "Befund" },
              { key: "anteil", label: "Anteil", numeric: true, width: 80 },
              { key: "status", label: "Schwere", width: 130, render: (r) => <StatusDot status={r.status} label={r.status === "critical" ? "Kritisch" : r.status === "warn" ? "Auffällig" : r.status === "info" ? "Hinweis" : "In Ordnung"} /> },
              { key: "massnahme", label: "Maßnahme" },
            ]} />
        </Card>

        <Card title="Bereinigungspipeline" subtitle="Zeilen je Schritt" icon="activity" footer="Reproduzierbar, versioniert in der Notebook-Pipeline">
          <Chart height={250} layout={{
            margin: { l: 210, r: 60, t: 10, b: 30 }, showlegend: false,
            xaxis: { range: [16700, 16830], title: { text: "Zeilen" }, showgrid: true, gridcolor: window.SWWTokens.tokens["grey-100"], showline: false },
            yaxis: { showgrid: false, tickfont: { size: 11, color: window.SWWTokens.tokens["text-muted"] } },
          }}
            data={[{
              type: "bar", orientation: "h",
              y: stufen.map((s) => s.schritt).reverse(), x: stufen.map((s) => s.zeilen).reverse(),
              marker: { color: [ROLE.ist, ROLE.residuum, ROLE.residuum, ROLE.residuum, window.SWWTokens.tokens["chart-kommunal"]].reverse() },
              text: stufen.map((s) => D.fmt(s.zeilen)).reverse(), textposition: "outside",
              textfont: { family: "IBM Plex Sans, sans-serif", size: 11, color: window.SWWTokens.tokens["text-muted"] },
            }]} />
        </Card>
      </div>

      <Card title="Train/Test-Split" subtitle="Zeitlicher Split — keine zufällige Aufteilung" icon="calendar">
        <div style={{ display: "flex", gap: "var(--space-4)", alignItems: "stretch" }}>
          <div style={{ flex: 1, background: "var(--navy-100)", border: "1px solid var(--navy-200)", borderRadius: "var(--radius-md)", padding: "var(--space-4)" }}>
            <p style={{ font: "var(--text-overline)", letterSpacing: "var(--ls-caps)", textTransform: "uppercase", color: "var(--navy-800)", margin: "0 0 6px" }}>Training</p>
            <p style={{ font: "var(--text-metric-sm)", margin: "0 0 4px", color: "var(--navy-900)" }}>01/2024 – 12/2024</p>
            <p style={{ font: "var(--text-caption)", color: "var(--navy-800)", margin: 0 }}>8.376 Beobachtungen · 700 Zähler</p>
          </div>
          <div style={{ flex: 1, background: "var(--teal-100)", border: "1px solid var(--teal-200)", borderRadius: "var(--radius-md)", padding: "var(--space-4)" }}>
            <p style={{ font: "var(--text-overline)", letterSpacing: "var(--ls-caps)", textTransform: "uppercase", color: "var(--teal-700)", margin: "0 0 6px" }}>Test</p>
            <p style={{ font: "var(--text-metric-sm)", margin: "0 0 4px", color: "var(--teal-700)" }}>01/2025 – 12/2025</p>
            <p style={{ font: "var(--text-caption)", color: "var(--teal-700)", margin: 0 }}>8.375 Beobachtungen · R² {D.metrik.r2} · MAE {D.metrik.mae} kWh</p>
          </div>
          <div style={{ flex: 1.2, display: "flex", flexDirection: "column", gap: 8, justifyContent: "center" }}>
            <Tag icon="info">Vorjahresmerkmal erst ab 2025 verfügbar</Tag>
              <Tag icon="info">Anomalie-Definition: gewähltes VLS-Perzentil im Anomalie-Cockpit</Tag>
            <Tag icon="info">Retraining quartalsweise, Drift-Monitoring auf Temperatur</Tag>
          </div>
        </div>
      </Card>
    </>
  );
}
Object.assign(window, { DatenqualitaetScreen });
