const { PageHeader, Card, KpiTile, DataTable, Tag, StatusDot, Badge, Button, Alert, Switch, KUNDENTYP_COLOR, Sparkline } = window.StadtWerkeWesthafenDesignSystem_acd94c;

function UebersichtScreen({ monat, onOpenZaehler }) {
  const D = window.SWWData;
  const [band, setBand] = React.useState(true);
  const top = D.zaehler.slice().sort((a, b) => Math.abs(b.abweichung_pct) - Math.abs(a.abweichung_pct)).slice(0, 6);

  const traces = [];
  if (band) traces.push({
    x: D.MONATE.concat(D.MONATE.slice().reverse()),
    y: D.portfolioBandHi.concat(D.portfolioBandLo.slice().reverse()),
    fill: "toself", fillcolor: ROLE.band, line: { width: 0 }, hoverinfo: "skip", name: "Konfidenzband", type: "scatter",
  });
  traces.push(
    { x: D.MONATE, y: D.portfolioIst, name: "Ist", mode: "lines+markers", type: "scatter",
      line: { color: ROLE.ist, width: 2 }, marker: { size: 5, color: ROLE.ist } },
    { x: D.MONATE, y: D.portfolioPrognose, name: "Prognose", mode: "lines", type: "scatter",
      line: { color: ROLE.prognose, width: 2, dash: "4,2" } },
  );

  return (
    <>
      <PageHeader eyebrow="Betrieb" title={"Portfolio-Übersicht " + monat}
        subtitle="Monatsverbrauch von 700 Zählern, Prognose zum Monatsbeginn gegen realisierten Verbrauch."
        meta={<><span>700 Zähler</span><span>·</span><span>Mittel- und Niederspannung</span><span>·</span><span>Stand {D.metrik.stand}</span></>}
        actions={<><Button variant="secondary" icon="download">Export</Button><Button variant="primary" icon="trending-up">Prognose 04/2025</Button></>} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <KpiTile label="Prognose 04/2025" value="14.820" unit="MWh" delta="+2,1 %" reference="vs. Ist 03/2025" icon="trending-up" spark={D.portfolioIst.slice(-12).map(v => v / 1000)} />
        <KpiTile label={"Ist " + monat} value="14.514" unit="MWh" delta="−1,3 %" reference="vs. 02/2025" icon="zap" />
        <KpiTile label="Prognosegüte Test 2025" value={"R² " + D.metrik.r2} reference={"MAE " + D.metrik.mae + " kWh · RMSE " + D.metrik.rmse + " kWh"} icon="activity" />
        <KpiTile variant="accent" label="Offene Anomalien" value="128" delta="+18" deltaTone="bad" reference="vs. 02/2025" icon="triangle-alert" spark={D.anomalienVerlauf} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.9fr 1fr", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <Card title="Prognose vs. Ist — Portfolio" subtitle="24 Monate, Verbrauch in MWh" icon="trending-up"
          actions={<Switch label="Konfidenzband" checked={band} onChange={(e) => setBand(e.target.checked)} />}
          footer={<><span>Training 2024 · Test 2025 (zeitlicher Split)</span><span>·</span><span>{D.metrik.modell} {D.metrik.version}</span></>}>
          <Chart data={traces} height={272} layout={{ yaxis: { title: { text: "Verbrauch (MWh)" } }, margin: { l: 66, r: 18, t: 30, b: 42 } }} />
        </Card>

        <Card title="Anomalien nach Kundentyp" subtitle={monat} icon="chart-column"
          footer="Schwellwert: 95. Perzentil der absoluten Abweichung">
          <Chart height={272} layout={{ margin: { l: 44, r: 12, t: 12, b: 40 }, showlegend: false, yaxis: { title: { text: "Zähler" } } }}
            data={[{
              type: "bar", x: Object.keys(D.anomalienNachTyp), y: Object.values(D.anomalienNachTyp),
              marker: { color: Object.keys(D.anomalienNachTyp).map((k) => KT[k]) },
              text: Object.values(D.anomalienNachTyp), textposition: "outside",
              textfont: { family: "IBM Plex Sans, sans-serif", size: 12, color: "#4E5A68" },
            }]} />
        </Card>
      </div>

      <Alert status="neutral" icon="info" style={{ marginBottom: "var(--space-4)" }}>
        Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges.
      </Alert>

      <Card title="Größte Abweichungen" subtitle={"Top 6 nach absoluter prozentualer Abweichung, " + monat} icon="triangle-alert" flush
        actions={<><Badge status="critical" size="sm">14 kritisch</Badge><Button variant="ghost" size="sm" iconAfter="arrow-right" onClick={() => onOpenZaehler(null)}>Alle Anomalien</Button></>}>
        <DataTable rowKey="zaehler_id" onRowClick={(r) => onOpenZaehler(r.zaehler_id)}
          columns={[
            { key: "zaehler_id", label: "Zähler", mono: true, width: 110 },
            { key: "kunde", label: "Kunde" },
            { key: "kundentyp", label: "Kundentyp", width: 150, render: (r) => <Tag dotColor={KUNDENTYP_COLOR[r.kundentyp]}>{r.kundentyp}</Tag> },
            { key: "prognose_kwh", label: "Prognose (kWh)", numeric: true, render: (r) => D.fmt(r.prognose_kwh) },
            { key: "ist_kwh", label: "Ist (kWh)", numeric: true, render: (r) => D.fmt(r.ist_kwh) },
            { key: "abweichung_pct", label: "Abweichung", numeric: true, render: (r) => <span style={{ color: Math.abs(r.abweichung_pct) > 30 ? "var(--red-600)" : Math.abs(r.abweichung_pct) > 15 ? "var(--amber-700)" : "var(--text-secondary)" }}>{D.fmtPct(r.abweichung_pct)}</span> },
            { key: "trend", label: "24 Monate", width: 110, render: (r) => <Sparkline values={r.historie.map(v => v / 1000)} anomalyIndices={r.anomalieIdx} /> },
            { key: "status", label: "Status", width: 140, render: (r) => <StatusDot status={r.status} label={r.statusLabel} /> },
          ]}
          rows={top} />
      </Card>
    </>
  );
}
Object.assign(window, { UebersichtScreen });
