const { PageHeader, Card, DataTable, Tabs, Tag, StatusDot, Badge, Button, IconButton, Select, Input, Checkbox, Dialog, EmptyState, Alert, KUNDENTYP_COLOR, Sparkline } = window.StadtWerkeWesthafenDesignSystem_acd94c;

function AnomalienScreen({ monat, onOpenZaehler }) {
  const D = window.SWWData;
  const [tab, setTab] = React.useState("alle");
  const [typ, setTyp] = React.useState("all");
  const [q, setQ] = React.useState("");
  const [sort, setSort] = React.useState({ key: "abweichung_pct", dir: "desc" });
  const [sel, setSel] = React.useState(null);
  const [ticket, setTicket] = React.useState(null);

  let rows = D.zaehler.filter((z) => {
    if (tab === "kritisch" && z.status !== "critical") return false;
    if (tab === "auffaellig" && z.status !== "warn") return false;
    if (tab === "geprueft" && !z.geprueft) return false;
    if (typ !== "all" && z.kundentyp !== typ) return false;
    if (q && !(z.zaehler_id + " " + z.kunde).toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });
  rows = rows.slice().sort((a, b) => {
    const k = sort.key, m = sort.dir === "desc" ? -1 : 1;
    const av = k === "abweichung_pct" ? Math.abs(a[k]) : a[k], bv = k === "abweichung_pct" ? Math.abs(b[k]) : b[k];
    return av > bv ? m : av < bv ? -m : 0;
  });

  const counts = {
    alle: D.zaehler.length, kritisch: D.zaehler.filter((z) => z.status === "critical").length,
    auffaellig: D.zaehler.filter((z) => z.status === "warn").length, geprueft: D.zaehler.filter((z) => z.geprueft).length,
  };

  return (
    <>
      <PageHeader eyebrow="Frühwarnung" title={"Anomalien " + monat}
        subtitle={"Zähler mit absoluter prozentualer Abweichung über dem Schwellwert von " + D.metrik.schwelle + " % (95. Perzentil der Residuen)."}
        meta={<><span>{rows.length} von 700 Zählern</span><span>·</span><span>Stand {D.metrik.stand}</span></>}
        actions={<><Button variant="secondary" icon="download" disabled>Export CSV</Button><Button variant="primary" icon="file-chart-column" disabled>Bericht erzeugen</Button></>} />

      <Alert status="warn" title="Einheiten gemischt" style={{ marginBottom: "var(--space-4)" }}
        actions={<Button size="sm" variant="secondary" icon="database" disabled>Zur Datenqualität</Button>}>
        412 Werte in verbrauch_kwh lagen als MWh-Text vor und wurden auf kWh umgerechnet.
      </Alert>

      <Card flush>
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", padding: "var(--space-3) var(--gutter-card)", borderBottom: "1px solid var(--border-subtle)", flexWrap: "wrap" }}>
          <Tabs value={tab} onChange={setTab} variant="pills" items={[
            { id: "alle", label: "Alle", count: counts.alle },
            { id: "kritisch", label: "Kritisch", count: counts.kritisch },
            { id: "auffaellig", label: "Auffällig", count: counts.auffaellig },
            { id: "geprueft", label: "Geprüft", count: counts.geprueft },
          ]} />
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
            <Input size="sm" aria-label="Zähler oder Kunde suchen" icon="search" placeholder="Zähler oder Kunde" value={q} onChange={(e) => setQ(e.target.value)} style={{ width: 210 }} />
            <Select size="sm" aria-label="Kundentyp filtern" value={typ} onChange={(e) => setTyp(e.target.value)} style={{ width: 170 }}
              options={[{ value: "all", label: "Alle Kundentypen" }, { value: "Gewerbe", label: "Gewerbe" }, { value: "Industrie", label: "Industrie" }, { value: "Kommunal", label: "Kommunal" }]} />
            <IconButton icon="filter" label="Weitere Filter" bordered disabled />
          </div>
        </div>

        {rows.length === 0 ? (
          <EmptyState icon="triangle-alert" title="Keine Anomalien über dem Schwellwert"
            actions={<Button variant="secondary" size="sm" onClick={() => { setQ(""); setTyp("all"); setTab("alle"); }}>Filter zurücksetzen</Button>}>
            {"Schwellwert: 95. Perzentil der absoluten prozentualen Abweichung (" + D.metrik.schwelle + " %)."}
          </EmptyState>
        ) : (
          <DataTable rowKey="zaehler_id" sort={sort} onSortChange={setSort} selectedKey={sel} onRowClick={(r) => setSel(r.zaehler_id)}
            columns={[
              { key: "check", label: <Checkbox indeterminate aria-label="Alle auswählen" />, width: 44, render: () => <Checkbox aria-label="Zeile auswählen" /> },
              { key: "zaehler_id", label: "Zähler", mono: true, width: 108, sortable: true },
              { key: "kunde", label: "Kunde" },
              { key: "kundentyp", label: "Kundentyp", width: 148, render: (r) => <Tag dotColor={KUNDENTYP_COLOR[r.kundentyp]}>{r.kundentyp}</Tag> },
              { key: "vertragsleistung_kw", label: "Leistung (kW)", numeric: true, sortable: true, render: (r) => D.fmt(r.vertragsleistung_kw) },
              { key: "prognose_kwh", label: "Prognose (kWh)", numeric: true, render: (r) => D.fmt(r.prognose_kwh) },
              { key: "ist_kwh", label: "Ist (kWh)", numeric: true, sortable: true, render: (r) => D.fmt(r.ist_kwh) },
              { key: "residuum_kwh", label: "Residuum (kWh)", numeric: true, render: (r) => (r.residuum_kwh > 0 ? "+" : "−") + D.fmt(Math.abs(r.residuum_kwh)) },
              { key: "abweichung_pct", label: "Abweichung", numeric: true, sortable: true, render: (r) => <span style={{ fontWeight: 600, color: Math.abs(r.abweichung_pct) > 30 ? "var(--red-600)" : Math.abs(r.abweichung_pct) > 15 ? "var(--amber-700)" : "var(--text-secondary)" }}>{D.fmtPct(r.abweichung_pct)}</span> },
              { key: "trend", label: "24 Monate", width: 104, render: (r) => <Sparkline values={r.historie.map((v) => v / 1000)} anomalyIndices={r.anomalieIdx} /> },
              { key: "status", label: "Status", width: 136, render: (r) => <StatusDot status={r.status} label={r.statusLabel} /> },
              { key: "akt", label: "", width: 96, render: (r) => (
                <span style={{ display: "flex", gap: 4 }}>
                  <IconButton size="sm" icon="external-link" label="Zähler öffnen" onClick={(e) => { e.stopPropagation(); onOpenZaehler(r.zaehler_id); }} />
                  <IconButton size="sm" icon="ticket" label="Ticket anlegen" onClick={(e) => { e.stopPropagation(); setTicket(r); }} />
                </span>) },
            ]}
            rows={rows} />
        )}
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", padding: "var(--space-3) var(--gutter-card)", borderTop: "1px solid var(--border-subtle)", font: "var(--text-caption)", color: "var(--text-muted)" }}>
          <span>{rows.length} Zeilen · sortiert nach {sort.key}</span>
          <span style={{ marginLeft: "auto", display: "flex", gap: "var(--space-2)" }}>
            <IconButton size="sm" icon="chevron-left" label="Vorherige Seite" bordered disabled />
            <span style={{ font: "var(--text-data)", alignSelf: "center" }}>1 / 1</span>
            <IconButton size="sm" icon="chevron-right" label="Nächste Seite" bordered disabled />
          </span>
        </div>
      </Card>

      <Dialog open={Boolean(ticket)} onClose={() => setTicket(null)} title="Anomalie-Ticket anlegen"
        subtitle={ticket ? ticket.zaehler_id + " · " + ticket.kunde + " · " + monat : ""}
        footer={<Button variant="primary" onClick={() => setTicket(null)}>Beispiel schließen</Button>}>
        {ticket ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
            <p style={{ margin: 0 }}>
              Abweichung {D.fmtPct(ticket.abweichung_pct)} gegenüber der Prognose ({D.fmt(ticket.prognose_kwh)} kWh).
              Dieses Formular demonstriert den Prüfprozess; es wird kein Ticket versendet.
            </p>
            <Select label="Prüfgrund" options={["Zählerauslesung prüfen", "Leitungsverlust vermuten", "Abrechnungsfehler prüfen", "Produktionsplan abweichend"]} />
            <Input label="Notiz" placeholder="Kurzbeschreibung für Netzmanagement" />
            <Checkbox label="Netzmanagement per E-Mail informieren (Beispiel)" disabled />
          </div>
        ) : null}
      </Dialog>
    </>
  );
}
Object.assign(window, { AnomalienScreen });
