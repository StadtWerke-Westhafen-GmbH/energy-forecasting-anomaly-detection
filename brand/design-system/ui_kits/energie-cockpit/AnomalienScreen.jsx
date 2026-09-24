const {
  PageHeader, Card, DataTable, Tag, Badge, Button, IconButton, Select, Input,
  EmptyState, Alert, KpiTile, KUNDENTYP_COLOR,
} = window.StadtWerkeWesthafenDesignSystem_acd94c;

const REVIEW_META = {
  nicht_bewertet: { label: "Nicht bewertet", status: "neutral", icon: "circle" },
  in_pruefung: { label: "In Prüfung", status: "info", icon: "search" },
  rueckfrage: { label: "Rückfrage offen", status: "warn", icon: "message-circle-question" },
  abgeschlossen: { label: "Bewertung abgeschlossen", status: "ok", icon: "circle-check" },
};

function reviewFor(decisions, alertId) {
  return decisions[alertId] || { workflow: "nicht_bewertet" };
}

function ReviewBadge({ workflow }) {
  const meta = REVIEW_META[workflow] || REVIEW_META.nicht_bewertet;
  return <Badge status={meta.status} icon={meta.icon}>{meta.label}</Badge>;
}

function signed(value, formatter) {
  if (value === 0) return formatter(0);
  return `${value > 0 ? "+" : "−"}${formatter(Math.abs(value))}`;
}

function percentileLabel(value) {
  return Number(value).toLocaleString("de-DE", {
    minimumFractionDigits: Number.isInteger(value) ? 0 : 1,
    maximumFractionDigits: 1,
  });
}

function alertsForThreshold(observations, threshold) {
  const selected = observations.filter((row) => row.abs_residual_vls >= threshold);
  const counts = new Map();
  selected.forEach((row) => counts.set(row.zaehler_id, (counts.get(row.zaehler_id) || 0) + 1));
  return selected.map((row, index) => ({
    ...row,
    rank: index + 1,
    score: row.abs_residual_vls / threshold,
    repeat_alert: counts.get(row.zaehler_id) > 1,
    meter_alert_count: counts.get(row.zaehler_id),
  }));
}

function downloadCsv(rows, decisions, option) {
  const columns = [
    ["alert_id", (row) => row.alert_id],
    ["zaehler_id", (row) => row.zaehler_id],
    ["kunde_id", (row) => row.kunde_id],
    ["monat", (row) => row.month_label],
    ["kundentyp", (row) => row.kundentyp],
    ["richtung", (row) => row.direction],
    ["schwellen_perzentil", () => String(option.percentile).replace(".", ",")],
    ["schwelle_vls_stunden", () => String(option.threshold_vls).replace(".", ",")],
    ["schwellenfaktor", (row) => String(row.score).replace(".", ",")],
    ["residuum_vls", (row) => String(row.residual_vls).replace(".", ",")],
    ["ist_kwh", (row) => String(row.actual_kwh).replace(".", ",")],
    ["prognose_kwh", (row) => String(row.forecast_kwh).replace(".", ",")],
    ["abweichung_kwh", (row) => String(row.residual_kwh).replace(".", ",")],
    ["abweichung_prozent", (row) => String(row.deviation_pct).replace(".", ",")],
    ["wartung_aktiv", (row) => (row.wartung_aktiv ? "ja" : "nein")],
    ["dq_flag", (row) => (row.dq_capacity ? "ja" : "nein")],
    ["bearbeitungsstatus", (row) => reviewFor(decisions, row.alert_id).workflow],
  ];
  const quote = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const csv = [
    columns.map(([name]) => quote(name)).join(";"),
    ...rows.map((row) => columns.map(([, read]) => quote(read(row))).join(";")),
  ].join("\r\n");
  const url = URL.createObjectURL(new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `sww-pruefhinweise-p${String(option.percentile).replace(".", "-")}-2025.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function AnomalienScreen({ decisions = {}, onOpenCase, thresholdIndex, onThresholdChange }) {
  const D = window.SWWAnomalyData;
  const option = D.threshold_options[thresholdIndex];
  const threshold = option.threshold_vls;
  const activeAlerts = React.useMemo(
    () => alertsForThreshold(D.observations, threshold),
    [D, threshold],
  );
  const [month, setMonth] = React.useState("all");
  const [type, setType] = React.useState("all");
  const [direction, setDirection] = React.useState("all");
  const [workflow, setWorkflow] = React.useState("all");
  const [context, setContext] = React.useState("all");
  const [query, setQuery] = React.useState("");
  const [sort, setSort] = React.useState({ key: "score", dir: "desc" });

  const filtered = activeAlerts.filter((row) => {
    const review = reviewFor(decisions, row.alert_id);
    if (month !== "all" && row.month_key !== month) return false;
    if (type !== "all" && row.kundentyp !== type) return false;
    if (direction !== "all" && row.direction_code !== direction) return false;
    if (workflow !== "all" && review.workflow !== workflow) return false;
    if (context === "dq" && !row.dq_capacity) return false;
    if (context === "wartung" && !row.wartung_aktiv) return false;
    if (context === "wiederholt" && !row.repeat_alert) return false;
    const haystack = `${row.zaehler_id} ${row.kunde_id}`.toLowerCase();
    if (query && !haystack.includes(query.toLowerCase())) return false;
    return true;
  });

  const sorted = filtered.slice().sort((a, b) => {
    const read = (row) => {
      if (sort.key === "workflow") return reviewFor(decisions, row.alert_id).workflow;
      return row[sort.key];
    };
    const left = read(a);
    const right = read(b);
    const factor = sort.dir === "desc" ? -1 : 1;
    return left > right ? factor : left < right ? -factor : a.rank - b.rank;
  });

  const monthKeys = month === "all" ? D.monthly.map((item) => item.month_key) : [month];
  const monthSummary = monthKeys.map((key) => {
    const rows = filtered.filter((row) => row.month_key === key);
    const source = D.monthly.find((item) => item.month_key === key);
    return {
      month_key: key,
      month_label: source.month_label,
      low: rows.filter((row) => row.direction_code === "niedrig").length,
      high: rows.filter((row) => row.direction_code === "hoch").length,
    };
  });
  const segmentSummary = ["Gewerbe", "Industrie", "Kommunal"].map((kundentyp) => ({
    kundentyp,
    alerts: filtered.filter((row) => row.kundentyp === kundentyp).length,
  }));

  const alertIds = new Set(activeAlerts.map((row) => row.alert_id));
  const normalPoints = D.observations.filter((row) => !alertIds.has(row.alert_id));
  const highPoints = activeAlerts.filter((row) => row.direction_code === "hoch");
  const lowPoints = activeAlerts.filter((row) => row.direction_code === "niedrig");
  const axisMax = 1.05 * Math.max(
    ...D.observations.map((row) => Math.max(row.actual_kwh, row.forecast_kwh)),
  );
  const uniqueMeters = new Set(filtered.map((row) => row.zaehler_id)).size;
  const dqOverlap = filtered.filter((row) => row.dq_capacity).length;
  const activeReviews = filtered.filter((row) => (
    reviewFor(decisions, row.alert_id).workflow !== "nicht_bewertet"
  )).length;
  const monthsInScope = month === "all" ? 12 : 1;
  const filtersActive = [month, type, direction, workflow, context].some((v) => v !== "all") || query;
  const reset = () => {
    setMonth("all"); setType("all"); setDirection("all");
    setWorkflow("all"); setContext("all"); setQuery("");
  };

  return (
    <div data-testid="anomaly-dashboard">
      <PageHeader eyebrow="Menschlich kontrollierte Anomalieerkennung"
        title="Anomalieprüfung 2025"
        subtitle="Der Regler übersetzt denselben Modellfehler in mehr oder weniger Prüfaufwand. Ein Prüfhinweis ist noch keine bestätigte Störung."
        meta={<>
          <span>{D.meta.model_version}</span><span>·</span>
          <span>{percentileLabel(option.percentile)}. Perzentil</span><span>·</span>
          <span>±{threshold.toLocaleString("de-DE", { maximumFractionDigits: 1 })} VLS-h</span><span>·</span>
          <span>Datenstand {D.meta.as_of}</span>
        </>}
        actions={<>
          <Button variant="secondary" icon="rotate-ccw" onClick={reset} disabled={!filtersActive}>Filter zurücksetzen</Button>
          <Button variant="primary" icon="download" onClick={() => downloadCsv(sorted, decisions, option)}>CSV exportieren</Button>
        </>} />

      <Alert status="info" title="Retrospektive Demonstration" style={{ marginBottom: "var(--space-4)" }}>
        Die Hinweise wurden auf dem bereits bekannten Benchmarkjahr 2025 berechnet. Der Regler trainiert das Modell nicht neu; er ändert ausschließlich die zuvor auf Ende 2024 kalibrierte Entscheidungsgrenze. {D.meta.caveat}
      </Alert>

      <div className="anomaly-threshold-grid" style={{ marginBottom: "var(--space-4)" }}>
        <Card title="Szenario für Prüfaufwand" subtitle="Vier dokumentierte Perzentile aus dem Notebook" icon="sliders-horizontal"
          footer="Niedriger = mehr Hinweise · höher = weniger Hinweise">
          <div className="anomaly-threshold-control">
            <div className="anomaly-threshold-value">
              <span>Gewählte Arbeitshypothese</span>
              <strong>{percentileLabel(option.percentile)}. Perzentil</strong>
              <small>Schwelle ±{threshold.toLocaleString("de-DE", { maximumFractionDigits: 1 })} VLS-Stunden</small>
            </div>
            <label htmlFor="threshold-scenario">Prüfaufwand verschieben</label>
            <input id="threshold-scenario" aria-label="Perzentil der Anomalieschwelle"
              type="range" min="0" max={D.threshold_options.length - 1} step="1"
              value={thresholdIndex}
              onChange={(event) => onThresholdChange(Number(event.target.value))} />
            <div className="anomaly-threshold-scale" aria-hidden="true">
              {D.threshold_options.map((item) => <span key={item.quantile}>{percentileLabel(item.percentile)} %</span>)}
            </div>
          </div>
          <Chart height={245} layout={{
            margin: { l: 54, r: 18, t: 20, b: 48 }, showlegend: false,
            xaxis: { title: { text: "Perzentil" }, tickvals: D.threshold_options.map((item) => item.percentile), ticksuffix: " %" },
            yaxis: { title: { text: "Hinweise/Monat" }, rangemode: "tozero" },
          }} data={[
            {
              type: "scatter", mode: "lines+markers",
              x: D.threshold_options.map((item) => item.percentile),
              y: D.threshold_options.map((item) => item.alerts_per_month),
              line: { color: ROLE.residuum, width: 3 }, marker: { color: ROLE.residuum, size: 7 },
              hovertemplate: "%{x}. Perzentil<br>%{y:.1f} Hinweise/Monat<extra></extra>",
            },
            {
              type: "scatter", mode: "markers+text",
              x: [option.percentile], y: [option.alerts_per_month],
              marker: { color: ROLE.anomalie, size: 13, line: { color: "#fff", width: 2 } },
              text: [option.alerts_per_month.toLocaleString("de-DE", { maximumFractionDigits: 1 })],
              textposition: "top center", hoverinfo: "skip",
            },
          ]} />
        </Card>

        <Card title="Ist gegen Prognose" subtitle="Alle 8.398 bewertbaren Zähler-Monate 2025" icon="scatter-chart"
          footer={<><span>Diagonale = perfekte Prognose</span><span>·</span><span>Farbe und Fallzahl reagieren auf denselben Regler</span></>}>
          <Chart height={390} layout={{
            margin: { l: 76, r: 20, t: 18, b: 58 },
            xaxis: { title: { text: "Modellprognose (kWh)" }, range: [0, axisMax] },
            yaxis: { title: { text: "Tatsächlicher Verbrauch (kWh)" }, range: [0, axisMax] },
          }} data={[
            { type: "scatter", mode: "lines", name: "Ist = Prognose", x: [0, axisMax], y: [0, axisMax], line: { color: ROLE.ist, width: 2, dash: "dash" }, hoverinfo: "skip" },
            { type: "scattergl", mode: "markers", name: "kein Prüfhinweis", x: normalPoints.map((row) => row.forecast_kwh), y: normalPoints.map((row) => row.actual_kwh), marker: { color: window.SWWTokens.tokens["grey-400"], size: 5, opacity: 0.24 }, hoverinfo: "skip" },
            { type: "scatter", mode: "markers", name: "ungewöhnlich hoch", x: highPoints.map((row) => row.forecast_kwh), y: highPoints.map((row) => row.actual_kwh), customdata: highPoints.map((row) => [row.zaehler_id, row.month_label, row.residual_vls]), marker: { color: ROLE.anomalie, symbol: "triangle-up", size: 10, line: { color: "#fff", width: 1 } }, hovertemplate: "%{customdata[0]} · %{customdata[1]}<br>Prognose %{x:,.0f} kWh<br>Ist %{y:,.0f} kWh<br>VLS-Residuum %{customdata[2]:.1f} h<extra></extra>" },
            { type: "scatter", mode: "markers", name: "ungewöhnlich niedrig", x: lowPoints.map((row) => row.forecast_kwh), y: lowPoints.map((row) => row.actual_kwh), customdata: lowPoints.map((row) => [row.zaehler_id, row.month_label, row.residual_vls]), marker: { color: window.SWWTokens.tokens["red-700"], symbol: "triangle-down", size: 10, line: { color: "#fff", width: 1 } }, hovertemplate: "%{customdata[0]} · %{customdata[1]}<br>Prognose %{x:,.0f} kWh<br>Ist %{y:,.0f} kWh<br>VLS-Residuum %{customdata[2]:.1f} h<extra></extra>" },
          ]} />
        </Card>
      </div>

      <Alert status="neutral" title="Warum gibt es im kWh-Plot keine feste zweite Grenzlinie?" style={{ marginBottom: "var(--space-4)" }}>
        Die Regel lautet |Ist − Prognose| ÷ Vertragsleistung ≥ VLS-Schwelle. Deshalb hängt der erlaubte kWh-Abstand von der Größe des jeweiligen Anschlusses ab. Eine einzige Linie mit verstellbarem Winkel wäre eine andere Verhältnisregel und würde die Methodik des Notebooks verändern.
      </Alert>

      <div className="anomaly-kpi-grid" style={{ marginBottom: "var(--space-4)" }}>
        <KpiTile label="Prüfhinweise" value={filtered.length.toLocaleString("de-DE")} icon="triangle-alert"
          reference={`von ${activeAlerts.length} im gewählten Szenario`} />
        <KpiTile label="Hinweise je Monat" value={(filtered.length / monthsInScope).toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
          icon="calendar" reference="im gewählten Filter" />
        <KpiTile label="Betroffene Zähler" value={uniqueMeters.toLocaleString("de-DE")} icon="gauge"
          reference={`von ${D.summary.meters_total} Zählern`} />
        <KpiTile label="Bereits bearbeitet" value={activeReviews.toLocaleString("de-DE")} icon="clipboard-check"
          reference={`${dqOverlap} mit zusätzlichem DQ-Flag`} />
      </div>

      <div className="anomaly-chart-grid" style={{ marginBottom: "var(--space-4)" }}>
        <Card title="Prüfhinweise nach Monat" subtitle="Benchmark 01/2025–12/2025 · Anzahl" icon="chart-column-stacked"
          footer={<><span>Niedrig: Residuum-Teal</span><span>·</span><span>Hoch: Anomalie-Rot</span></>}>
          <Chart height={250} layout={{
            barmode: "stack", margin: { l: 54, r: 18, t: 18, b: 50 },
            xaxis: { title: { text: "Monat" } }, yaxis: { title: { text: "Prüfhinweise" }, rangemode: "tozero" },
          }} data={[
            { type: "bar", name: "ungewöhnlich niedrig", x: monthSummary.map((item) => item.month_label), y: monthSummary.map((item) => item.low), marker: { color: ROLE.residuum } },
            { type: "bar", name: "ungewöhnlich hoch", x: monthSummary.map((item) => item.month_label), y: monthSummary.map((item) => item.high), marker: { color: ROLE.anomalie } },
          ]} />
        </Card>
        <Card title="Prüfhinweise nach Kundentyp" subtitle="Aktueller Filter · Anzahl" icon="chart-bar"
          footer="Die Segmentzahlen reagieren auf Schwelle und Filter.">
          <Chart height={250} layout={{
            margin: { l: 92, r: 42, t: 18, b: 46 }, showlegend: false,
            xaxis: { title: { text: "Prüfhinweise" }, range: [0, Math.max(...segmentSummary.map((item) => item.alerts), 1) * 1.16] },
          }} data={[{
            type: "bar", orientation: "h",
            y: segmentSummary.map((item) => item.kundentyp),
            x: segmentSummary.map((item) => item.alerts),
            marker: { color: segmentSummary.map((item) => KT[item.kundentyp]) },
            text: segmentSummary.map((item) => String(item.alerts)), textposition: "outside", cliponaxis: false,
          }]} />
        </Card>
      </div>

      <Alert status={dqOverlap ? "warn" : "neutral"} title="Datenqualität separat behandeln" style={{ marginBottom: "var(--space-4)" }}>
        Im Benchmarkjahr existieren {D.summary.dq_flags_total} belegte Plausibilitätsfehler; {dqOverlap} davon liegen im aktuell gefilterten Hinweisbestand. Vor betrieblicher Interpretation zuerst Messwert und Stammdaten prüfen.
      </Alert>

      <Card title="Prüfwarteschlange"
        subtitle="Nach Schwellenfaktor sortiert; absolute kWh-Auswirkung bleibt als betrieblicher Kontext sichtbar."
        icon="list-filter" flush
        actions={<Badge status="neutral">{sorted.length} Treffer</Badge>}>
        <div className="anomaly-filter-grid">
          <Input size="sm" label="Suche" aria-label="Zähler oder Kunde suchen" icon="search"
            placeholder="Zähler- oder Kunden-ID" value={query} onChange={(event) => setQuery(event.target.value)} />
          <Select size="sm" label="Monat" value={month} onChange={(event) => setMonth(event.target.value)}
            options={[{ value: "all", label: "Gesamt 2025" }, ...D.monthly.map((item) => ({ value: item.month_key, label: item.month_label }))]} />
          <Select size="sm" label="Kundentyp" value={type} onChange={(event) => setType(event.target.value)}
            options={[{ value: "all", label: "Alle Kundentypen" }, ...["Gewerbe", "Industrie", "Kommunal"].map((value) => ({ value, label: value }))]} />
          <Select size="sm" label="Richtung" value={direction} onChange={(event) => setDirection(event.target.value)}
            options={[{ value: "all", label: "Beide Richtungen" }, { value: "niedrig", label: "Ungewöhnlich niedrig" }, { value: "hoch", label: "Ungewöhnlich hoch" }]} />
          <Select size="sm" label="Bearbeitungsstatus" value={workflow} onChange={(event) => setWorkflow(event.target.value)}
            options={[{ value: "all", label: "Alle Status" }, ...D.review_options.workflow]} />
          <Select size="sm" label="Kontext" value={context} onChange={(event) => setContext(event.target.value)}
            options={[{ value: "all", label: "Alle Fälle" }, { value: "dq", label: "Mit DQ-Flag" }, { value: "wartung", label: "Wartung gemeldet" }, { value: "wiederholt", label: "Wiederholt auffällig" }]} />
        </div>

        {sorted.length === 0 ? (
          <EmptyState icon="search-x" title="Keine Fälle für diese Filterkombination"
            actions={<Button variant="secondary" size="sm" onClick={reset}>Filter zurücksetzen</Button>}>
            Passen Sie Zeitraum, Filter oder das Schwellen-Szenario an.
          </EmptyState>
        ) : (
          <DataTable compact rowKey="alert_id" sort={sort} onSortChange={setSort}
            onRowClick={onOpenCase} rows={sorted}
            columns={[
              { key: "rank", label: "Rang", numeric: true, width: 64 },
              { key: "zaehler_id", label: "Zähler", mono: true, sortable: true, width: 110 },
              { key: "month_key", label: "Monat", sortable: true, width: 90, render: (row) => row.month_label },
              { key: "kundentyp", label: "Kundentyp", width: 130, render: (row) => <Tag dotColor={KUNDENTYP_COLOR[row.kundentyp]}>{row.kundentyp}</Tag> },
              { key: "direction", label: "Richtung", width: 160, render: (row) => <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span aria-hidden="true">{row.direction_code === "hoch" ? "↑" : "↓"}</span>{row.direction}</span> },
              { key: "score", label: "Faktor", numeric: true, sortable: true, width: 86, render: (row) => row.score.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) },
              { key: "actual_kwh", label: "Ist (kWh)", numeric: true, width: 118, render: (row) => row.actual_kwh.toLocaleString("de-DE", { maximumFractionDigits: 0 }) },
              { key: "forecast_kwh", label: "Prognose (kWh)", numeric: true, width: 140, render: (row) => <span style={{ color: "var(--cyan-700)" }}>{row.forecast_kwh.toLocaleString("de-DE", { maximumFractionDigits: 0 })}</span> },
              { key: "impact_abs_kwh", label: "Abweichung (kWh)", numeric: true, sortable: true, width: 152, render: (row) => signed(row.residual_kwh, (value) => value.toLocaleString("de-DE", { maximumFractionDigits: 0 })) },
              { key: "residual_vls", label: "Residuum (VLS-h)", numeric: true, sortable: true, width: 150, render: (row) => signed(row.residual_vls, (value) => value.toLocaleString("de-DE", { maximumFractionDigits: 1 })) },
              { key: "context", label: "Kontext", width: 178, render: (row) => <span className="anomaly-context-tags">{row.dq_capacity ? <Badge status="critical" size="sm" icon="database">DQ</Badge> : null}{row.wartung_aktiv ? <Badge status="info" size="sm" icon="wrench">Wartung</Badge> : null}{row.repeat_alert ? <Badge status="neutral" size="sm" icon="repeat-2">wiederholt</Badge> : null}{!row.dq_capacity && !row.wartung_aktiv && !row.repeat_alert ? <span style={{ color: "var(--text-muted)" }}>—</span> : null}</span> },
              { key: "workflow", label: "Bearbeitung", sortable: true, width: 188, render: (row) => <ReviewBadge workflow={reviewFor(decisions, row.alert_id).workflow} /> },
              { key: "action", label: "", width: 52, render: (row) => <IconButton size="sm" icon="panel-right-open" label={`Fall ${row.zaehler_id} öffnen`} onClick={(event) => { event.stopPropagation(); onOpenCase(row); }} /> },
            ]} />
        )}
        <div className="anomaly-table-footer">
          <span>{sorted.length} Hinweise · {percentileLabel(option.percentile)}. Perzentil · ±{threshold.toLocaleString("de-DE", { maximumFractionDigits: 1 })} VLS-h</span>
          <span>Bewertungen werden nur lokal in diesem Browser gespeichert.</span>
        </div>
      </Card>
    </div>
  );
}

Object.assign(window, { AnomalienScreen, ReviewBadge, REVIEW_META, alertsForThreshold });
