const { Card, KpiTile, DataTable, Tabs, Select, Badge, Tag, Alert, Button, KUNDENTYP_COLOR } = window.StadtWerkeWesthafenDesignSystem_acd94c;

const GROUPS = {
  monat: { label: "Monat", key: (row) => row.monat, name: monthLabel },
  kunde: { label: "Kunde", key: (row) => row.kunde_id, name: (value) => value },
  kundentyp: { label: "Branche", key: (row) => row.kundentyp, name: (value) => value },
};
const TOP_CUSTOMERS = 15;

function groupAlerts(alerts, group) {
  const spec = GROUPS[group];
  const buckets = new Map(group === "monat" ? DATA.months.map((m) => [m, { key: m, label: monthLabel(m), hoch: 0, niedrig: 0 }]) : []);
  alerts.forEach((row) => {
    const key = spec.key(row);
    if (!buckets.has(key)) buckets.set(key, { key, label: spec.name(key), hoch: 0, niedrig: 0 });
    buckets.get(key)[row.hoch ? "hoch" : "niedrig"] += 1;
  });
  const list = [...buckets.values()];
  if (group === "monat") return list;
  list.sort((a, b) => (b.hoch + b.niedrig) - (a.hoch + a.niedrig) || a.key.localeCompare(b.key));
  return group === "kunde" ? list.slice(0, TOP_CUSTOMERS) : list;
}

function CaseHints({ row }) {
  const repeats = DATA.alertCount[row.zaehler_id];
  return (
    <span className="vc-hints">
      <Badge status={row.hoch ? "critical" : "warn"} size="sm" icon={row.hoch ? "arrow-up" : "arrow-down"}>{row.hoch ? "Mehrverbrauch" : "Minderverbrauch"}</Badge>
      {row.wartung ? <Tag icon="wrench">Wartung geplant</Tag> : null}
      {repeats > 1 ? <Tag icon="repeat">{repeats}× auffällig</Tag> : null}
      {loadTickets()[row.id] ? <Tag icon="ticket">Ticket</Tag> : null}
    </span>
  );
}

/** Count per branch as coloured dots; the branch name is in the tooltip. */
function BranchSplit({ rows }) {
  return (
    <span className="vc-branch-split">
      {KUNDENTYPEN.map((kundentyp) => {
        const count = rows.filter((row) => row.kundentyp === kundentyp).length;
        return (
          <span key={kundentyp} title={kundentyp} aria-label={`${kundentyp}: ${count}`} className={count ? undefined : "is-empty"}>
            <i style={{ background: KUNDENTYP_COLOR[kundentyp] }} />{count}
          </span>
        );
      })}
    </span>
  );
}

/** The work list: few, plain columns; the case view holds the details. */
function Pruefliste({ alerts, onOpenCase, showMonth }) {
  const rows = alerts.map((row, index) => ({ ...row, rang: index + 1 }));
  return (
    <DataTable rows={rows} onRowClick={(row) => onOpenCase(row.id)} empty="Keine Prüfhinweise im gewählten Filter." columns={[
      { key: "rang", label: "#", numeric: true, width: 44 },
      { key: "zaehler_id", label: "Zähler / Kunde", render: (row) => <span className="vc-meter"><strong>{row.zaehler_id}</strong><small>{row.kunde_id}</small></span> },
      ...(showMonth ? [{ key: "monat", label: "Monat", render: (row) => monthLabel(row.monat) }] : []),
      { key: "kundentyp", label: "Branche", render: (row) => <Tag dotColor={KUNDENTYP_COLOR[row.kundentyp]}>{row.kundentyp}</Tag> },
      { key: "prognose", label: "Erwartet (kWh)", numeric: true, render: (row) => fmt(row.prognose) },
      { key: "ist", label: "Gemessen (kWh)", numeric: true, render: (row) => fmt(row.ist) },
      { key: "abw", label: "Abweichung", numeric: true, render: (row) => <strong>{deviationText(row)}</strong> },
      { key: "hinweis", label: "Einordnung", render: (row) => <CaseHints row={row} /> },
      { key: "aktion", label: "", render: (row) => <Button size="sm" variant="secondary" icon="arrow-right" aria-label={`Prüffall ${row.zaehler_id} öffnen`}
        onClick={(event) => { event.stopPropagation(); onOpenCase(row.id); }}>Prüfen</Button> },
    ]} />
  );
}

function MonatsAnsicht({ month, filter, onOpenCase }) {
  const alerts = filter(DATA.alerts).filter((row) => row.monat === month);
  const prevAlerts = filter(DATA.alerts).filter((row) => row.monat === addMonths(month, -1));
  const high = alerts.filter((row) => row.hoch).length;
  const repeated = alerts.filter((row) => DATA.alertCount[row.zaehler_id] > 1).length;
  const perMonth = groupAlerts(filter(DATA.alerts), "monat");
  return (
    <>
      <div className="vc-kpi-grid">
        <KpiTile variant="accent" label={`Offene Prüfhinweise ${monthLabel(month)}`} value={fmt(alerts.length)} icon="triangle-alert"
          reference={month === DATA.months[0] ? "erster Monat im Testjahr" : `Vormonat: ${prevAlerts.length}`} />
        <KpiTile label="Mehrverbrauch" value={fmt(high)} icon="arrow-up" reference={<BranchSplit rows={alerts.filter((row) => row.hoch)} />} />
        <KpiTile label="Minderverbrauch" value={fmt(alerts.length - high)} icon="arrow-down" reference={<BranchSplit rows={alerts.filter((row) => !row.hoch)} />} />
        <KpiTile label="Wiederholt auffällig" value={fmt(repeated)} icon="repeat" reference="Zähler mit mehreren Hinweisen" />
      </div>

      <Card title={<TitleHelp help="Sortiert nach Dringlichkeit: Je stärker die Abweichung die Toleranz des Anschlusses überschreitet, desto weiter oben. „Prüfen“ öffnet den Prüffall mit Verlauf, Kontext und Ticket.">{`Prüfliste ${monthLabel(month)}`}</TitleHelp>} icon="list-checks" flush
        actions={<Badge status="neutral">{alerts.length} {alerts.length === 1 ? "Fall" : "Fälle"}</Badge>} style={{ marginBottom: "var(--space-4)" }}>
        <Pruefliste alerts={alerts} onOpenCase={onOpenCase} />
      </Card>

      <Card title={<TitleHelp help="Anzahl der Prüfhinweise je Monat. Der gewählte Monat ist hinterlegt.">Prüfhinweise im Zeitverlauf</TitleHelp>} icon="chart-column-stacked">
        <Chart height={200} layout={{
          barmode: "stack", margin: { l: 44, r: 12, t: 8, b: 40 }, legend: { orientation: "h", y: 1.2 }, xaxis: { ...AXIS_MONTH, title: undefined }, yaxis: { rangemode: "tozero", tickformat: ",d", dtick: Math.max(...perMonth.map((g) => g.hoch + g.niedrig), 0) <= 6 ? 1 : undefined },
          shapes: [{ type: "rect", xref: "x", yref: "paper", x0: `${addMonths(month, -1)}-17`, x1: `${month}-15`, y0: 0, y1: 1, fillcolor: ROLE.band, line: { width: 0 }, layer: "below" }],
        }} data={[
          { type: "bar", name: "Mehrverbrauch", x: perMonth.map((g) => toDate(g.key)), y: perMonth.map((g) => g.hoch), marker: { color: ROLE.anomalie } },
          { type: "bar", name: "Minderverbrauch", x: perMonth.map((g) => toDate(g.key)), y: perMonth.map((g) => g.niedrig), marker: { color: SWWTokens.tokens["amber-500"] } },
        ]} />
      </Card>
    </>
  );
}

function JahresAnsicht({ filter, onOpenCase }) {
  const [group, setGroup] = React.useState("monat");
  const alerts = filter(DATA.alerts);
  const groups = groupAlerts(alerts, group);
  const horizontal = group !== "monat";
  const labels = groups.map((item) => (group === "monat" ? toDate(item.key) : item.label));
  const trace = (name, key, color) => (horizontal
    ? { type: "bar", orientation: "h", name, y: labels, x: groups.map((item) => item[key]), marker: { color } }
    : { type: "bar", name, x: labels, y: groups.map((item) => item[key]), marker: { color } });
  const maxCount = Math.max(1, ...groups.map((item) => item.hoch + item.niedrig));
  return (
    <>
      <Card title={<TitleHelp help={`Anzahl der Prüfhinweise ${DATA.meta.benchmark_period}, aufgeteilt in Mehr- und Minderverbrauch${group === "kunde" ? `; gezeigt werden die ${TOP_CUSTOMERS} Kunden mit den meisten Hinweisen` : ""}.`}>{`Prüfhinweise nach ${GROUPS[group].label}`}</TitleHelp>}
        icon="chart-column-stacked" style={{ marginBottom: "var(--space-4)" }}
        actions={<Select size="sm" aria-label="Gruppieren nach" value={group} onChange={(event) => setGroup(event.target.value)}
          options={Object.entries(GROUPS).map(([value, spec]) => ({ value, label: `nach ${spec.label}` }))} style={{ width: 150 }} />}>
        <Chart height={horizontal ? Math.max(200, groups.length * 26 + 70) : 280} layout={{
          barmode: "stack", legend: { orientation: "h", y: 1.12 },
          margin: horizontal ? { l: 110, r: 18, t: 18, b: 44 } : { l: 50, r: 18, t: 18, b: 50 },
          xaxis: horizontal ? { title: { text: "Prüfhinweise" }, range: [0, Math.max(3, maxCount) * 1.1], dtick: maxCount <= 10 ? 1 : undefined } : AXIS_MONTH,
          yaxis: horizontal ? { autorange: "reversed", type: "category", dtick: 1 } : { title: { text: "Prüfhinweise" }, rangemode: "tozero" },
        }} data={[trace("Mehrverbrauch", "hoch", ROLE.anomalie), trace("Minderverbrauch", "niedrig", SWWTokens.tokens["amber-500"])]} />
      </Card>
      <Card title={<TitleHelp help="Alle Prüfhinweise des Testjahres, sortiert nach Dringlichkeit. „Prüfen“ öffnet den Prüffall.">Alle Prüfhinweise im Jahr</TitleHelp>} icon="list" flush actions={<Badge status="neutral">{alerts.length} {alerts.length === 1 ? "Fall" : "Fälle"}</Badge>}>
        <Pruefliste alerts={alerts} onOpenCase={onOpenCase} showMonth />
      </Card>
    </>
  );
}

function AnomalienScreen({ onOpenCase, shell, selection, onSelection }) {
  const [tab, setTab] = React.useState("monat");
  const { month, type, kunde, direction } = selection;
  const setMonth = (value) => onSelection({ month: value });
  const setType = (value) => onSelection({ type: value });
  const setDirection = (value) => onSelection({ direction: value });
  const filter = (rows) => rows.filter((row) => (type === "all" || row.kundentyp === type)
    && (!kunde || row.kunde_id === kunde)
    && (direction === "all" || (direction === "hoch") === row.hoch));

  return (
    <VcShell {...shell} title="Prüfhinweise"
      help={{ label: "Wie entsteht ein Prüfhinweis?", text: `Nach Monatsabschluss wird der gemessene Verbrauch mit der Prognose verglichen. Liegt die Abweichung außerhalb der Toleranz des Anschlusses (±${fmt(DATA.threshold.wert, 0)} Stunden × Vertragsleistung), entsteht ein Prüfhinweis. ${DATA.meta.caveat}` }}
      filters={<>
        {tab === "monat" ? <Select size="sm" label="Abgeschlossener Monat" value={month} onChange={(event) => setMonth(event.target.value)} options={monthOptions()} /> : null}
        <Select size="sm" label="Branche" value={type} onChange={(event) => setType(event.target.value)} options={typeOptions()} />
        <CustomerFilter value={kunde} type={type} onChange={(value) => onSelection({ kunde: value })} />
        <Select size="sm" label="Richtung" value={direction} onChange={(event) => setDirection(event.target.value)} options={[
          { value: "all", label: "Mehr- und Minderverbrauch" }, { value: "hoch", label: "Nur Mehrverbrauch" }, { value: "niedrig", label: "Nur Minderverbrauch" },
        ]} />
    </>}>
    <div data-testid="screen-anomalien">
      <Tabs value={tab} onChange={setTab} style={{ marginBottom: "var(--space-4)" }} items={[
        { id: "monat", label: "Monatsansicht", icon: "calendar-days" },
        { id: "jahr", label: `Jahresübersicht ${DATA.meta.benchmark_period}`, icon: "calendar-range", count: DATA.alerts.length },
      ]} />
      {tab === "monat"
        ? <MonatsAnsicht month={month} filter={filter} onOpenCase={onOpenCase} />
        : <JahresAnsicht filter={filter} onOpenCase={onOpenCase} />}
    </div>
    </VcShell>
  );
}

Object.assign(window, { AnomalienScreen });
