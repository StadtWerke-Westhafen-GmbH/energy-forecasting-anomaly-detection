const { Card, KpiTile, DataTable, Tabs, Select, Switch, Alert, Tag, KUNDENTYP_COLOR } = window.StadtWerkeWesthafenDesignSystem_acd94c;

const UNITS = { MWh: { factor: 1000, label: "MWh" }, kWh: { factor: 1, label: "kWh" } };
const pctDiff = (value, reference) => (reference ? ((value - reference) / reference) * 100 : null);
const TOLERANCE_PCT = 5;
const HIT = () => SWWTokens.tokens["green-600"];
const MISS = () => SWWTokens.tokens["amber-600"];
const isHit = (item) => Math.abs(pctDiff(item.prognose, item.ist)) <= TOLERANCE_PCT;

/** Converts kWh into the chosen display unit and formats it German-style. */
function unitHelpers(unit) {
  const u = UNITS[unit];
  const v = (kwh) => (kwh == null ? null : kwh / u.factor);
  return { label: u.label, v, f: (kwh) => (kwh == null ? "—" : fmt(v(kwh))) };
}

/** Mean absolute monthly deviation of the summed forecast in the given months. */
function meanAbsPct(items) {
  const values = items.filter((item) => item.prognose != null && item.ist).map((item) => Math.abs(pctDiff(item.prognose, item.ist)));
  return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;
}

function deviationBars(items, height) {
  return (
    <Chart height={height} layout={{
      margin: { l: 50, r: 12, t: 12, b: 46 }, showlegend: false, xaxis: AXIS_MONTH, yaxis: { title: { text: "Abweichung (%)" }, zeroline: true },
      shapes: [{ type: "rect", xref: "paper", x0: 0, x1: 1, y0: -TOLERANCE_PCT, y1: TOLERANCE_PCT, fillcolor: ROLE.band, line: { width: 0 }, layer: "below" }],
    }} data={[{
      type: "bar", x: items.map((t) => toDate(t.monat)), y: items.map((t) => pctDiff(t.prognose, t.ist)),
      marker: { color: items.map((t) => (isHit(t) ? HIT() : MISS())) },
      hovertemplate: "%{x|%m/%Y}: %{y:+.1f} %<extra></extra>",
    }]} />
  );
}

function UnitSwitch({ unit, onUnit }) {
  return <Tabs variant="pills" value={unit} onChange={onUnit} aria-label="Einheit" items={[{ id: "MWh", label: "MWh" }, { id: "kWh", label: "kWh" }]} />;
}

/**
 * Past months: forecast point joined to the actual value (green = within ±5 %, amber = beyond).
 * Target month (optional): forecast with a fan-shaped range starting at the last known actual.
 */
function ForecastChart({ series, target, band, unit, showHistory, height = 400 }) {
  const { label, v, f } = unitHelpers(unit);
  const firstTest = series.find((item) => item.prognose != null)?.monat;
  const prev = target ? addMonths(target, -1) : null;
  const known = series.filter((item) => !target || item.monat < target);
  const main = known.filter((item) => item.monat >= firstTest || item.monat === prev);
  const history = known.filter((item) => item.monat < firstTest);
  const past = known.filter((item) => item.prognose != null);
  const connectors = (hit) => {
    const x = []; const y = [];
    past.filter((item) => isHit(item) === hit).forEach((item) => { x.push(toDate(item.monat), toDate(item.monat), null); y.push(v(item.prognose), v(item.ist), null); });
    return { type: "scatter", mode: "lines", x, y, hoverinfo: "skip", showlegend: false, line: { color: hit ? HIT() : MISS(), width: 3 } };
  };
  const forecastMarkers = (hit) => {
    const items = past.filter((item) => isHit(item) === hit);
    return {
      type: "scatter", mode: "markers", x: items.map((t) => toDate(t.monat)), y: items.map((t) => v(t.prognose)),
      name: hit ? `Prognose traf (±${TOLERANCE_PCT} %)` : `Prognose > ${TOLERANCE_PCT} % daneben`,
      marker: { color: "#fff", size: 11, line: { color: hit ? HIT() : MISS(), width: 3 } },
      customdata: items.map((t) => [f(t.prognose), f(t.ist), signed(pctDiff(t.prognose, t.ist), 1, " %")]),
      hovertemplate: `%{x|%m/%Y}<br>Prognose %{customdata[0]} ${label}<br>Ist %{customdata[1]} ${label}<br>Abweichung %{customdata[2]}<extra></extra>`,
    };
  };
  const current = target ? series.find((item) => item.monat === target) : null;
  const anchor = target ? series.find((item) => item.monat === prev) : null;
  const start = showHistory || !firstTest ? series[0].monat : (prev && prev < firstTest ? prev : firstTest);
  const end = target ? addMonths(target, 1) : addMonths(series[series.length - 1].monat, 1);

  const data = [];
  if (showHistory && history.length) {
    const bridge = [...history, ...main.slice(0, 1)];
    data.push({ type: "scatter", mode: "lines+markers", name: "Ist Vorjahr", x: bridge.map((t) => toDate(t.monat)), y: bridge.map((t) => v(t.ist)),
      line: { color: SWWTokens.tokens["grey-400"], width: 2 }, marker: { size: 5 }, hovertemplate: `%{x|%m/%Y}: %{y:,.0f} ${label}<extra>Ist</extra>` });
  }
  data.push(connectors(true), connectors(false));
  data.push({ type: "scatter", mode: "lines+markers", name: "Ist", x: main.map((t) => toDate(t.monat)), y: main.map((t) => v(t.ist)),
    line: { color: ROLE.ist, width: 2.5 }, marker: { size: 7 }, hovertemplate: `%{x|%m/%Y}: %{y:,.0f} ${label}<extra>Ist</extra>` });
  if (past.length) data.push(forecastMarkers(true), forecastMarkers(false));

  const shapes = [];
  const annotations = [];
  if (target && current) {
    const hasAnchor = anchor && anchor.ist != null;
    if (band != null && hasAnchor) {
      data.push({ type: "scatter", mode: "lines", name: `Spanne ±${fmt((band / current.prognose) * 100, 1)} %`, fill: "toself", fillcolor: "rgba(0,144,200,0.28)", line: { width: 0 }, hoverinfo: "skip",
        x: [toDate(prev), toDate(target), toDate(target), toDate(prev)], y: [v(anchor.ist), v(current.prognose + band), v(current.prognose - band), v(anchor.ist)] });
    }
    if (hasAnchor) {
      data.push({ type: "scatter", mode: "lines", showlegend: false, hoverinfo: "skip", x: [toDate(prev), toDate(target)], y: [v(anchor.ist), v(current.prognose)], line: { color: ROLE.prognose, width: 2.5, dash: "dash" } });
    }
    data.push({ type: "scatter", mode: "markers", name: `Prognose ${monthLabel(target)}`, x: [toDate(target)], y: [v(current.prognose)],
      marker: { color: ROLE.prognose, size: 18, symbol: "diamond", line: { color: "#fff", width: 2 } },
      error_y: band != null ? { type: "data", array: [v(band)], color: ROLE.prognose, thickness: 2, width: 12 } : undefined,
      hovertemplate: `Prognose ${monthLabel(target)}: %{y:,.0f} ${label}<extra></extra>` });
    data.push({ type: "scatter", mode: "markers", name: `Ist ${monthLabel(target)} (nach Monatsabschluss)`, visible: "legendonly", x: [toDate(target)], y: [v(current.ist)],
      marker: { color: ROLE.ist, size: 13, symbol: "circle-open", line: { width: 3 } } });
    shapes.push({ type: "rect", xref: "x", yref: "paper", x0: `${prev}-16`, x1: `${target}-16`, y0: 0, y1: 1, fillcolor: "rgba(0,144,200,0.06)", line: { width: 0 }, layer: "below" });
    annotations.push({
      x: toDate(target), y: v(current.prognose + (band || 0)), yanchor: "bottom", showarrow: false, yshift: 10,
      text: `<b>${f(current.prognose)} ${label}</b>${band != null ? `<br>± ${f(band)} ${label}` : ""}`, font: { color: ROLE.prognose, size: 13 }, align: "center",
    });
  }

  return (
    <Chart height={height} layout={{
      margin: { l: unit === "kWh" ? 96 : 70, r: 40, t: 40, b: 50 }, legend: { orientation: "h", y: 1.14 },
      xaxis: { ...AXIS_MONTH, dtick: showHistory ? "M2" : "M1", range: [`${addMonths(start, -1)}-20`, `${end}-10`] },
      yaxis: { title: { text: label }, tickformat: ",.0f" },
      shapes, annotations,
    }} data={data} />
  );
}

function PlanungsAnsicht({ type, kunde, target, unit, onUnit }) {
  const [showHistory, setShowHistory] = React.useState(false);
  const { label, f } = unitHelpers(unit);
  const series = timeline(type, kunde);
  const prev = addMonths(target, -1);
  const lastYear = addMonths(target, -12);
  const at = (key) => series.find((item) => item.monat === key);
  const current = at(target);
  const pastForecasts = series.filter((item) => item.monat < target && item.prognose != null);
  const spread = meanAbsPct(pastForecasts);
  const forecast = current.prognose;
  const band = spread != null ? (forecast * spread) / 100 : null;
  const prevIst = at(prev)?.ist;
  const lastYearIst = at(lastYear)?.ist;
  const gain = DATA.bestBaseline ? (1 - DATA.finalModel.rmse / DATA.bestBaseline.rmse) * 100 : null;

  const plan = KUNDENTYPEN.filter((k) => (kunde ? CUSTOMERS[kunde] === k : type === "all" || k === type)).map((kundentyp) => {
    const s = timeline(kundentyp, kunde);
    const find = (key) => s.find((item) => item.monat === key);
    return { id: kundentyp, kundentyp, prognose: find(target).prognose, vormonat: find(prev)?.ist, vorjahr: find(lastYear)?.ist };
  });
  if (plan.length > 1) plan.push({ id: "summe", kundentyp: "Gesamt", prognose: forecast, vormonat: prevIst, vorjahr: lastYearIst });

  return (
    <>
      <div className="vc-kpi-grid">
        <KpiTile variant="accent" label={`Beschaffungsmenge ${monthLabel(target)}`} value={f(forecast)} unit={label} icon="shopping-cart"
          reference={band != null ? `Spanne ±${f(band)} ${label}` : "noch keine Erfahrungswerte"} />
        <KpiTile label={`vs. Vormonat ${monthLabel(prev)}`} value={signed(pctDiff(forecast, prevIst), 1)} unit="%" icon="arrow-left-right"
          reference={prevIst != null ? `Ist ${f(prevIst)} ${label}` : "kein Vormonat"} />
        <KpiTile label={`vs. Vorjahresmonat ${monthLabel(lastYear)}`} value={lastYearIst != null ? signed(pctDiff(forecast, lastYearIst), 1) : "—"} unit="%" icon="calendar-clock"
          reference={lastYearIst != null ? `Ist ${f(lastYearIst)} ${label}` : "keine Vorjahresdaten"} />
        <KpiTile label="Treffsicherheit bisher" value={spread != null ? `±${fmt(spread, 1)}` : "—"} unit="%" icon="target"
          reference={pastForecasts.length ? `Ø Monatsabweichung seit ${monthLabel(pastForecasts[0].monat)}` : "erster Prognosemonat"} />
      </div>

      <Card title={<TitleHelp help={`Monatssumme ${scopeLabel(type, kunde)} in ${label}. Kreise = frühere Prognosen: grün lag höchstens ±${TOLERANCE_PCT} % daneben, orange mehr. Die Raute ist die Prognose für ${monthLabel(target)}; ${band != null ? `die Spanne entspricht der durchschnittlichen Abweichung der bisherigen Prognosen (±${fmt(spread, 1)} %)` : "für den ersten Prognosemonat gibt es noch keine Spanne"}. Das spätere Ist des Monats lässt sich über die Legende einblenden.`}>Verbrauchsverlauf und Prognose</TitleHelp>} icon="chart-line"
        actions={<div className="vc-card-controls">
          <Switch label={`${HISTORY_MONTHS.length ? HISTORY_MONTHS[0].slice(0, 4) : "Vorjahr"} einblenden`} checked={showHistory} onChange={(event) => setShowHistory(event.target.checked)} />
          <UnitSwitch unit={unit} onUnit={onUnit} />
        </div>}
        style={{ marginBottom: "var(--space-4)" }}>
        <ForecastChart series={series} target={target} band={band} unit={unit} showHistory={showHistory} />
      </Card>

      <div className="vc-chart-grid">
        <Card title={<TitleHelp help={`Prognose je Branche in ${label}, verglichen mit dem Ist des Vormonats und des Vorjahresmonats.`}>{`Beschaffungsplan ${monthLabel(target)}`}</TitleHelp>} icon="clipboard-list" flush>
          <DataTable rows={plan} columns={[
            { key: "kundentyp", label: "Branche", render: (row) => (row.id === "summe" ? <strong>Gesamt</strong> : <Tag dotColor={KUNDENTYP_COLOR[row.kundentyp]}>{row.kundentyp}</Tag>) },
            { key: "prognose", label: "Prognose", numeric: true, render: (row) => <strong>{f(row.prognose)}</strong> },
            { key: "vormonat", label: `Ist ${monthLabel(prev)}`, numeric: true, render: (row) => f(row.vormonat) },
            { key: "dv", label: "Δ Vormonat", numeric: true, render: (row) => signed(pctDiff(row.prognose, row.vormonat), 1, " %") },
            { key: "vorjahr", label: `Ist ${monthLabel(lastYear)}`, numeric: true, render: (row) => f(row.vorjahr) },
            { key: "dj", label: "Δ Vorjahr", numeric: true, render: (row) => signed(pctDiff(row.prognose, row.vorjahr), 1, " %") },
          ]} />
        </Card>
        <Card title={<TitleHelp help={`Abweichung (Prognose − Ist) ÷ Ist je Monat. Das blaue Band markiert ±${TOLERANCE_PCT} %. Positiv = zu viel beschafft, negativ = Nachkauf am Spotmarkt.${gain != null ? ` Im Testjahr ${fmt(gain, 0)} % genauer als die einfache Fortschreibung (${DATA.bestBaseline.kandidat}).` : ""}`}>Wie treffsicher waren die letzten Prognosen?</TitleHelp>} icon="target">
          {pastForecasts.length ? deviationBars(pastForecasts, 240)
            : <Alert status="info" title="Noch keine Erfahrungswerte">Für den ersten Prognosemonat liegen noch keine Vergleiche mit Istwerten vor.</Alert>}
        </Card>
      </div>
    </>
  );
}

function RueckblickAnsicht({ type, kunde, unit, onUnit }) {
  const { label, f } = unitHelpers(unit);
  const series = timeline(type, kunde);
  const test = series.filter((item) => item.prognose != null);
  const ist = sum(test, "ist");
  const prognose = sum(test, "prognose");
  const within = test.filter(isHit).length;
  const gain = DATA.bestBaseline ? (1 - DATA.finalModel.rmse / DATA.bestBaseline.rmse) * 100 : null;
  return (
    <>
      <div className="vc-kpi-grid">
        <KpiTile variant="accent" label="Jahresprognose" value={f(prognose)} unit={label} icon="chart-line"
          delta={signed(pctDiff(prognose, ist), 1, " %")} deltaTone="flat" reference="vs. Ist" />
        <KpiTile label="Ist im Testjahr" value={f(ist)} unit={label} icon="gauge" reference={DATA.meta.benchmark_period} />
        <KpiTile label="Ø Monatsabweichung" value={`±${fmt(meanAbsPct(test), 1)}`} unit="%" icon="target" reference={`${within} von ${test.length} Monaten innerhalb ±${TOLERANCE_PCT} %`} />
        <KpiTile label="Vorsprung vor Fortschreibung" value={gain != null ? fmt(gain, 0) : "—"} unit="%" icon="trending-up" reference="geringerer Fehler je Zähler" />
      </div>
      <Card title={<TitleHelp help={`Monatssumme ${scopeLabel(type, kunde)} in ${label}. Jede Prognose entstand einen Monat im Voraus. Grün = höchstens ±${TOLERANCE_PCT} % daneben, orange = mehr.`}>Prognose und Ist im Zeitverlauf</TitleHelp>} icon="chart-line"
        actions={<div className="vc-card-controls"><UnitSwitch unit={unit} onUnit={onUnit} /></div>} style={{ marginBottom: "var(--space-4)" }}>
        <ForecastChart series={test} unit={unit} showHistory={false} height={360} />
      </Card>
      <Card title={<TitleHelp help={`Abweichung (Prognose − Ist) ÷ Ist je Monat. Das blaue Band markiert ±${TOLERANCE_PCT} %. Positiv = zu viel beschafft, negativ = Nachkauf am Spotmarkt.`}>Monatliche Abweichung</TitleHelp>} icon="chart-column">
        {deviationBars(test, 260)}
      </Card>
    </>
  );
}

function PrognoseScreen({ shell, selection, onSelection }) {
  const [tab, setTab] = React.useState("planung");
  const { month: target, type, kunde, unit } = selection;
  const setTarget = (month) => onSelection({ month });
  const setType = (value) => onSelection({ type: value });
  const setUnit = (value) => onSelection({ unit: value });
  return (
    <VcShell {...shell} title="Verbrauchsprognose"
      help={{ label: "Wie entsteht die Prognose?", text: `Das Modell (${DATA.meta.model}) prognostiziert den Verbrauch jeweils einen Monat voraus. Planungsstand ist das Ende des Vormonats: Bis dahin sind die Istwerte bekannt. Die Jahresübersicht zeigt, wie gut die Prognosen im Testjahr ${DATA.meta.benchmark_period} getroffen haben.` }}
      filters={<>
      {tab === "planung" ? <Select size="sm" label="Prognose für Monat" value={target} onChange={(event) => setTarget(event.target.value)} options={monthOptions()} /> : null}
      <Select size="sm" label="Branche" value={type} onChange={(event) => setType(event.target.value)} options={typeOptions()} />
      <CustomerFilter value={kunde} type={type} onChange={(value) => onSelection({ kunde: value })} />
    </>}>
      <div data-testid="screen-prognose">
        <Tabs value={tab} onChange={setTab} style={{ marginBottom: "var(--space-4)" }} items={[
          { id: "planung", label: "Monatsansicht", icon: "calendar-days" },
          { id: "rueckblick", label: `Jahresübersicht ${DATA.meta.benchmark_period}`, icon: "calendar-range" },
        ]} />
        {tab === "planung"
          ? <PlanungsAnsicht type={type} kunde={kunde} target={target} unit={unit} onUnit={setUnit} />
          : <RueckblickAnsicht type={type} kunde={kunde} unit={unit} onUnit={setUnit} />}
      </div>
    </VcShell>
  );
}

Object.assign(window, { PrognoseScreen });
