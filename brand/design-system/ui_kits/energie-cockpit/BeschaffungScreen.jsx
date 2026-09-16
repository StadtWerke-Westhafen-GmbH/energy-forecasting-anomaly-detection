const { PageHeader, Card, KpiTile, DataTable, Badge, Button, Select, Alert, StatusDot, Tabs } = window.StadtWerkeWesthafenDesignSystem_acd94c;

function BeschaffungScreen({ monat }) {
  const D = window.SWWData;
  const [view, setView] = React.useState("menge");

  const typen = ["Gewerbe", "Industrie", "Kommunal"];
  const anteil = { Gewerbe: 0.27, Industrie: 0.58, Kommunal: 0.15 };

  return (
    <>
      <PageHeader eyebrow="Planung" title="Beschaffungsplanung 04/2025"
        subtitle="Prognostizierte Abnahmemenge je Monat als Grundlage der Terminbeschaffung; Restmenge geht in den Spotmarkt."
        meta={<><span>Sponsor: Stefan Lechtenberg, Energiebeschaffung</span><span>·</span><span>Stand {D.metrik.stand}</span></>}
        actions={<><Button variant="secondary" icon="download" disabled>Plan exportieren</Button><Button variant="primary" icon="check" disabled>Beschaffung freigeben</Button></>} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <KpiTile variant="accent" label="Prognose 04/2025" value="14.820" unit="MWh" reference="Konfidenzband ± 640 MWh" icon="trending-up" />
        <KpiTile label="Bereits beschafft" value="14.500" unit="MWh" reference="97,8 % der Prognose" icon="shopping-cart" />
        <KpiTile label="Offene Spotmenge" value="320" unit="MWh" delta="+120" deltaTone="bad" reference="vs. Plan 03/2025" icon="activity" />
        <KpiTile label="Spot-Kostenrisiko" value="38.400" unit="EUR" reference="bei 120 EUR/MWh Spread" icon="triangle-alert" />
      </div>

      <Alert status="info" title="Prognosefehler wirkt direkt auf die Spotmenge" style={{ marginBottom: "var(--space-4)" }}>
        MAE {D.metrik.mae} kWh pro Zähler entspricht rund 290 MWh Portfolio-Unsicherheit je Monat. Terminbeschaffung deckt daher 97–98 %, nicht 100 %.
      </Alert>

      <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <Card title="Prognostizierte Abnahme nach Kundentyp" subtitle="Nächste 6 Monate, MWh" icon="chart-column"
          actions={<Tabs variant="pills" value={view} onChange={setView} items={[{ id: "menge", label: "Menge" }, { id: "anteil", label: "Anteil" }]} />}
          footer="Terminbeschaffung monatlich zum Monatsbeginn">
          <Chart height={270} layout={{ barmode: view === "anteil" ? "stack" : "group", margin: { l: 62, r: 16, t: 30, b: 40 }, yaxis: { title: { text: view === "anteil" ? "Anteil (MWh)" : "MWh" } } }}
            data={typen.map((t) => ({
              type: "bar", name: t, x: D.beschaffung.map((b) => b.monat),
              y: D.beschaffung.map((b) => Math.round(b.prognose_mwh * anteil[t])),
              marker: { color: KT[t] },
            }))} />
        </Card>

        <Card title="Prognose vs. beschaffte Menge" subtitle="Differenz = Spotmarkt-Exposure" icon="shopping-cart" footer="Positiv = Zukauf, negativ = Verkauf">
          <Chart height={270} layout={{ margin: { l: 58, r: 16, t: 30, b: 40 }, yaxis: { title: { text: "MWh" } } }}
            data={[
              { type: "bar", name: "Beschafft", x: D.beschaffung.map((b) => b.monat), y: D.beschaffung.map((b) => b.beschafft_mwh), marker: { color: ROLE.ist } },
              { type: "scatter", mode: "lines+markers", name: "Prognose", x: D.beschaffung.map((b) => b.monat), y: D.beschaffung.map((b) => b.prognose_mwh), line: { color: ROLE.prognose, width: 2, dash: "4,2" }, marker: { size: 6, color: ROLE.prognose } },
            ]} />
        </Card>
      </div>

      <Card title="Beschaffungsplan" subtitle="Rollierend 6 Monate" icon="calendar" flush
        actions={<Select size="sm" options={["6 Monate", "12 Monate"]} style={{ width: 130 }} />}>
        <DataTable rowKey="monat"
          columns={[
            { key: "monat", label: "Monat", mono: true, width: 100 },
            { key: "prognose_mwh", label: "Prognose (MWh)", numeric: true, render: (r) => D.fmt(r.prognose_mwh) },
            { key: "band", label: "Konfidenzband", numeric: true },
            { key: "beschafft_mwh", label: "Beschafft (MWh)", numeric: true, render: (r) => D.fmt(r.beschafft_mwh) },
            { key: "spot_mwh", label: "Spot offen (MWh)", numeric: true, render: (r) => D.fmt(r.spot_mwh) },
            { key: "deckung", label: "Deckung", numeric: true, render: (r) => new Intl.NumberFormat("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format((r.beschafft_mwh / r.prognose_mwh) * 100) + " %" },
            { key: "kosten_eur", label: "Termin­kosten (EUR)", numeric: true },
            { key: "status", label: "Status", width: 150, render: (r) => <StatusDot status={r.status} label={r.status === "ok" ? "Gedeckt" : "Spot nötig"} /> },
          ]}
          rows={D.beschaffung} />
      </Card>
    </>
  );
}
Object.assign(window, { BeschaffungScreen });
