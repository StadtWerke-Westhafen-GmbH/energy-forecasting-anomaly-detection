const { PageHeader, Card, KpiTile, Tag, Badge, Button, Select, Alert, DataTable, StatusDot, KUNDENTYP_COLOR } = window.StadtWerkeWesthafenDesignSystem_acd94c;

function ZaehlerDetailScreen({ zaehlerId, monat, onBack, onTicket }) {
  const D = window.SWWData;
  const z = D.zaehler.find((x) => x.zaehler_id === zaehlerId) || D.zaehler[0];
  const prognoseSerie = z.historie.map((v, i) => Math.round(v * (1 + (((i * 37) % 11) - 5) / 130)));
  const residuen = z.historie.map((v, i) => v - prognoseSerie[i]);
  const schwelle = Math.round(Math.max(...residuen.map(Math.abs)) * 0.55);

  return (
    <>
      <PageHeader eyebrow={<span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>Zähler-Detail</span>}
        title={z.zaehler_id + " · " + z.kunde}
        subtitle={"Monatsverbrauch, Prognose und Residuen über 24 Monate. Anomalie-Schwellwert " + D.metrik.schwelle + " % (95. Perzentil)."}
        meta={<>
          <Tag dotColor={KUNDENTYP_COLOR[z.kundentyp]}>{z.kundentyp}</Tag>
          <Tag icon="gauge">{D.fmt(z.vertragsleistung_kw)} kW Vertragsleistung</Tag>
          <Tag icon="hash">{z.kunde_id}</Tag>
          {z.wartung_aktiv ? <Tag icon="wrench">Wartung aktiv</Tag> : null}
          <Badge status={z.status} size="sm" icon={z.status === "critical" ? "octagon-alert" : z.status === "warn" ? "triangle-alert" : "check"}>{z.statusLabel}</Badge>
        </>}
        actions={<><Button variant="secondary" icon="arrow-left" onClick={onBack}>Zur Liste</Button><Button variant="primary" icon="ticket" onClick={() => onTicket(z)}>Anomalie-Ticket anlegen</Button></>} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <KpiTile label={"Ist " + monat} value={D.fmt(z.ist_kwh)} unit="kWh" icon="zap" />
        <KpiTile label={"Prognose " + monat} value={D.fmt(z.prognose_kwh)} unit="kWh" icon="trending-up" />
        <KpiTile label="Residuum" value={(z.residuum_kwh > 0 ? "+" : "−") + D.fmt(Math.abs(z.residuum_kwh))} unit="kWh"
          delta={D.fmtPct(z.abweichung_pct)} deltaTone={Math.abs(z.abweichung_pct) > 15 ? "bad" : "flat"} reference="vs. Prognose" icon="activity" />
        <KpiTile label="Ø 3 Monate" value={D.fmt(z.historie.slice(-3).reduce((a, b) => a + b, 0) / 3)} unit="kWh" icon="calendar"
          reference={"Vorjahresmonat " + D.fmt(z.historie[11]) + " kWh"} />
      </div>

      {Math.abs(z.abweichung_pct) > 15 ? (
        <Alert status={z.status === "critical" ? "critical" : "warn"} title={"Abweichung " + D.fmtPct(z.abweichung_pct) + " über Schwellwert"} style={{ marginBottom: "var(--space-4)" }}>
          Zählerauslesung und Produktionsplan prüfen. Produktionsplan-Index {String(z.produktionsplan_index).replace(".", ",")}, {z.wartung_aktiv ? "Wartung im Monat aktiv" : "keine Wartung gemeldet"}.
        </Alert>
      ) : null}

      <div style={{ display: "grid", gridTemplateColumns: "1.9fr 1fr", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
        <Card title="Prognose vs. Ist" subtitle="24 Monate, Verbrauch in kWh" icon="trending-up"
          actions={<Select size="sm" options={["24 Monate", "12 Monate"]} style={{ width: 130 }} />}
          footer={<><span>Ist navy · Prognose cyan gestrichelt · Anomalie rot</span><span>·</span><span>{D.metrik.modell} {D.metrik.version}</span></>}>
          <Chart height={280} layout={{ yaxis: { title: { text: "Verbrauch (kWh)" } }, margin: { l: 74, r: 18, t: 30, b: 42 } }}
            data={[
              { x: D.MONATE, y: z.historie, name: "Ist", mode: "lines+markers", type: "scatter", line: { color: ROLE.ist, width: 2 }, marker: { size: 5, color: ROLE.ist } },
              { x: D.MONATE, y: prognoseSerie, name: "Prognose", mode: "lines", type: "scatter", line: { color: ROLE.prognose, width: 2, dash: "4,2" } },
              { x: z.anomalieIdx.map((i) => D.MONATE[i]), y: z.anomalieIdx.map((i) => z.historie[i]), name: "Anomalie", mode: "markers", type: "scatter", marker: { size: 10, color: ROLE.anomalie, line: { width: 1.5, color: "#fff" } } },
            ]} />
        </Card>

        <Card title="Residuen" subtitle="Ist − Prognose, kWh" icon="activity" footer={"Schwellwert ± " + D.fmt(schwelle) + " kWh"}>
          <Chart height={280} layout={{
            margin: { l: 66, r: 14, t: 12, b: 42 }, showlegend: false,
            yaxis: { title: { text: "Residuum (kWh)" }, zeroline: true, zerolinecolor: "#B4BFCB", zerolinewidth: 1 },
            shapes: [
              { type: "line", xref: "paper", x0: 0, x1: 1, y0: schwelle, y1: schwelle, line: { color: ROLE.schwelle, width: 1, dash: "3,3" } },
              { type: "line", xref: "paper", x0: 0, x1: 1, y0: -schwelle, y1: -schwelle, line: { color: ROLE.schwelle, width: 1, dash: "3,3" } },
            ],
          }}
            data={[{ type: "bar", x: D.MONATE, y: residuen, marker: { color: residuen.map((r) => (Math.abs(r) > schwelle ? ROLE.anomalie : ROLE.residuum)) } }]} />
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: "var(--space-4)" }}>
        <Card title="Stammdaten & Monatsmerkmale" subtitle="Bekannt zum Monatsbeginn" icon="database" flush>
          <DataTable compact rowKey="k" columns={[{ key: "k", label: "Merkmal" }, { key: "v", label: "Wert", numeric: true }]}
            rows={[
              { k: "zaehler_id", v: z.zaehler_id }, { k: "kunde_id", v: z.kunde_id },
              { k: "kundentyp", v: z.kundentyp }, { k: "vertragsleistung_kw", v: D.fmt(z.vertragsleistung_kw) },
              { k: "arbeitstage", v: z.arbeitstage }, { k: "feiertage_im_monat", v: z.feiertage },
              { k: "mittlere_temperatur_c", v: String(z.mittlere_temperatur_c).replace(".", ",") },
              { k: "heiztage", v: D.fmt(z.heiztage) },
              { k: "produktionsplan_index", v: String(z.produktionsplan_index).replace(".", ",") },
              { k: "wartung_aktiv", v: z.wartung_aktiv },
            ]} />
        </Card>

        <Card title="Einflussfaktoren" subtitle="Feature Importance, Random-Forest-Regressor" icon="chart-column"
          footer="Gini-Importance, Training 2024">
          <Chart height={250} layout={{
            margin: { l: 210, r: 26, t: 10, b: 30 }, showlegend: false,
            xaxis: { title: { text: "Anteil" }, showgrid: true, gridcolor: "#E4E9EF", showline: false },
            yaxis: { showgrid: false, tickfont: { family: "IBM Plex Sans, sans-serif", size: 11, color: "#4E5A68" } },
          }}
            data={[{
              type: "bar", orientation: "h",
              y: D.featureImportance.map((x) => x.feature).reverse(),
              x: D.featureImportance.map((x) => x.wert).reverse(),
              marker: { color: ROLE.ist },
              text: D.featureImportance.map((x) => String(x.wert).replace(".", ",")).reverse(),
              textposition: "outside", textfont: { family: "IBM Plex Sans, sans-serif", size: 11, color: "#4E5A68" },
            }]} />
        </Card>
      </div>
    </>
  );
}
Object.assign(window, { ZaehlerDetailScreen });
