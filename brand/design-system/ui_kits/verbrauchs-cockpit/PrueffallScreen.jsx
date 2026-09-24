const { Card, Button, Badge, Tag, Select, Input, Switch, Alert, KUNDENTYP_COLOR } = window.StadtWerkeWesthafenDesignSystem_acd94c;

const RECIPIENTS = [
  { value: "Zählerservice / Messstellenbetrieb", label: "Zählerservice / Messstellenbetrieb" },
  { value: "Servicetechnik Netz", label: "Servicetechnik Netz" },
  { value: "Installateur (extern)", label: "Installateur (extern)" },
  { value: "Kundenbetreuung", label: "Kundenbetreuung" },
];
const PRIORITIES = [{ value: "hoch", label: "Hoch" }, { value: "mittel", label: "Mittel" }, { value: "niedrig", label: "Niedrig" }];

function hoursInMonth(key) {
  const [y, m] = key.split("-").map(Number);
  return new Date(Date.UTC(y, m, 0)).getUTCDate() * 24;
}

/** Rule-based checks; they pre-fill the ticket, a person decides. */
function recommendations(row, context) {
  const steps = row.hoch
    ? ["Zählerstand und Ablesung auf Übertragungs- oder Einheitenfehler prüfen.",
      "Mit dem Kunden klären, ob Produktion oder Betrieb ausgeweitet wurden.",
      "Bei unerklärtem Mehrverbrauch Leitungsverluste bzw. nicht erfasste Verbraucher prüfen."]
    : ["Zählerfunktion prüfen (Stillstand, Defekt, fehlende Übertragung).",
      "Mit dem Kunden klären, ob Betrieb ruhte (Stillstand, Betriebsferien, Umbau).",
      "Ablesung bzw. Schätzwert auf Plausibilität prüfen."];
  if (context.overCapacity) steps.unshift("Messfehler wahrscheinlich: Verbrauch liegt über dem Maximum der Vertragsleistung.");
  if (row.wartung) steps.push(row.hoch ? "Geplante Wartung prüfen: Mehrverbrauch durch Wartungsarbeiten plausibel?" : "Geplante Wartung prüfen: Stillstand während der Wartung plausibel?");
  if (context.repeats > 1) steps.push(`Zähler ist im Testjahr ${context.repeats}× auffällig: Vor-Ort-Termin priorisieren.`);
  return steps;
}

/** Selected case, falling back to the most urgent case of the selected month. */
function resolveCase(caseId, month = DATA.months[DATA.months.length - 1]) {
  return DATA.alerts.find((item) => item.id === caseId)
    || DATA.alerts.filter((item) => item.monat === month)[0] || DATA.alerts[0];
}

function inDays(days) {
  const d = new Date(); d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function ticketText(row, context) {
  return [
    `Zähler ${row.zaehler_id} (${row.kunde_id}, ${row.kundentyp}, ${fmt(row.kw)} kW)`,
    `Monat ${monthLabel(row.monat)}: gemessen ${fmt(row.ist)} kWh, erwartet ${fmt(row.prognose)} kWh (${deviationText(row)}).`,
    "",
    "Bitte prüfen:",
    ...recommendations(row, context).map((step) => `- ${step}`),
  ].join("\n");
}

/** Hand-over to installer/technician. Stored in this browser; e-mail opens the local mail program. */
function TicketPanel({ row, context, handle }) {
  const initial = () => ({
    empfaenger: RECIPIENTS[0].value,
    prioritaet: row.score >= 3 ? "hoch" : row.score >= 1.5 ? "mittel" : "niedrig",
    faellig: inDays(row.score >= 3 ? 3 : 7),
    text: ticketText(row, context),
  });
  const [form, setForm] = React.useState(initial);
  const [tickets, setTickets] = React.useState(loadTickets);
  React.useEffect(() => { setForm(initial()); }, [row.id]);
  const existing = tickets[row.id];
  const update = (key) => (event) => setForm((current) => ({ ...current, [key]: event.target.value }));
  const save = (next) => { setTickets(next); writeStore(TICKET_KEY, next); };
  const create = () => save({
    ...tickets,
    [row.id]: { ...form, nummer: `T-${row.monat.replace("-", "")}-${row.zaehler_id.replace("ZL-", "")}`, erstellt: new Date().toLocaleString("de-DE") },
  });
  const discard = () => { const next = { ...tickets }; delete next[row.id]; save(next); };
  const mailto = (ticket) => `mailto:?subject=${encodeURIComponent(`${ticket.nummer} · Prüfauftrag ${row.zaehler_id} · Priorität ${ticket.prioritaet}`)}&body=${encodeURIComponent(`An: ${ticket.empfaenger}\nFällig bis: ${ticket.faellig}\n\n${ticket.text}`)}`;

  return (
    <Card title={<TitleHelp help="Prüfauftrag an Technik oder Installateur weitergeben.">Ticket erstellen</TitleHelp>} icon="ticket" actions={handle}>
      {existing ? (
        <div className="vc-ticket">
          <Alert status="ok" title={`Ticket ${existing.nummer} angelegt`}>
            An {existing.empfaenger} · Priorität {existing.prioritaet} · fällig bis {new Date(existing.faellig).toLocaleDateString("de-DE")} · erstellt {existing.erstellt}
          </Alert>
          <div className="vc-ticket__actions">
            <Button variant="primary" icon="mail" href={mailto(existing)}>Per E-Mail senden</Button>
            <Button variant="ghost" icon="rotate-ccw" onClick={discard}>Ticket verwerfen</Button>
          </div>
        </div>
      ) : (
        <div className="vc-ticket">
          <div className="vc-ticket__row">
            <Select label="Empfänger" value={form.empfaenger} onChange={update("empfaenger")} options={RECIPIENTS} />
            <Select label="Priorität" value={form.prioritaet} onChange={update("prioritaet")} options={PRIORITIES} />
            <Input label="Fällig bis" type="date" value={form.faellig} onChange={update("faellig")} />
          </div>
          <label className="vc-textarea">
            <span className="sww-field__label">Auftrag</span>
            <textarea rows={7} value={form.text} onChange={update("text")} />
          </label>
          <div className="vc-ticket__actions">
            <Button variant="primary" icon="send" onClick={create}>Ticket erstellen</Button>
          </div>
        </div>
      )}
    </Card>
  );
}

function PrueffallScreen({ caseId, onSelect, shell, selection }) {
  const [showHistory, setShowHistory] = React.useState(false);
  const row = resolveCase(caseId, selection.month);
  const meterRows = DATA.rows.filter((item) => item.zaehler_id === row.zaehler_id);
  const history = DATA.historyByMeter[row.zaehler_id] || [];
  const tolerance = DATA.threshold.wert * row.kw;
  const monthList = DATA.alerts.filter((item) => item.monat === row.monat);
  const position = monthList.findIndex((item) => item.id === row.id);
  const repeats = DATA.alertCount[row.zaehler_id];
  const avgPlan = meterRows.filter((item) => item.plan != null).reduce((a, b, _, all) => a + b.plan / all.length, 0);
  const context = { repeats, overCapacity: row.ist > row.kw * hoursInMonth(row.monat) };
  const monthResiduals = DATA.rows.filter((item) => item.monat === row.monat).map((item) => item.residuum);
  const share = (monthResiduals.filter((value) => Math.abs(value) >= Math.abs(row.residuum)).length / monthResiduals.length) * 100;
  const actual = showHistory ? [...history, ...meterRows] : meterRows;
  const x = (items) => items.map((item) => toDate(item.monat));
  const historyYear = HISTORY_MONTHS.length ? HISTORY_MONTHS[0].slice(0, 4) : "Vorjahr";

  const panels = [
    {
      id: "korridor", wide: true, render: (handle) => (
        <Card title={<TitleHelp help="Verbrauch in kWh je Monat. Liegt der gemessene Wert außerhalb des Korridors, entsteht ein Prüfhinweis.">Verbrauch und erwarteter Korridor</TitleHelp>} icon="chart-line"
          actions={<div className="vc-card-controls">
            <Switch label={`${historyYear} einblenden`} checked={showHistory} onChange={(event) => setShowHistory(event.target.checked)} />{handle}
          </div>}>
          <Chart height={320} layout={{
            margin: { l: 70, r: 24, t: 18, b: 50 }, legend: { orientation: "h", y: 1.12 },
            xaxis: { ...AXIS_MONTH, dtick: showHistory ? "M2" : "M1" }, yaxis: { title: { text: "kWh" }, rangemode: "tozero", tickformat: ",.0f" },
          }} data={[
            { type: "scatter", mode: "lines", x: x(meterRows), y: meterRows.map((item) => item.prognose + tolerance), line: { width: 0 }, showlegend: false, hoverinfo: "skip" },
            { type: "scatter", mode: "lines", name: "Erwarteter Korridor", x: x(meterRows), y: meterRows.map((item) => Math.max(0, item.prognose - tolerance)), line: { width: 0 }, fill: "tonexty", fillcolor: ROLE.band, hoverinfo: "skip" },
            { type: "scatter", mode: "lines", name: "Erwartet (Prognose)", x: x(meterRows), y: meterRows.map((item) => item.prognose), line: { color: ROLE.prognose, dash: "dash", width: 2 } },
            { type: "scatter", mode: "lines+markers", name: "Gemessen (Ist)", x: x(actual), y: actual.map((item) => item.ist), line: { color: ROLE.ist, width: 2.5 } },
            { type: "scatter", mode: "markers", name: "Prüfhinweis", x: x(meterRows.filter((item) => item.anomalie)), y: meterRows.filter((item) => item.anomalie).map((item) => item.ist),
              marker: { color: ROLE.anomalie, size: 14, symbol: "circle-open", line: { width: 3 } } },
          ]} />
        </Card>
      ),
    },
    {
      id: "abweichung", render: (handle) => (
        <Card title={<TitleHelp help={`Gemessen minus erwartet in kWh. Die gestrichelten Linien markieren die Toleranz dieses Anschlusses. ${repeats > 1 ? `${repeats} Monate außerhalb der Toleranz: wiederkehrendes Muster.` : "Nur dieser Monat liegt außerhalb der Toleranz: Einzelereignis."}`}>Abweichung je Monat</TitleHelp>} icon="chart-column" actions={handle}>
          <Chart height={260} layout={{
            margin: { l: 70, r: 12, t: 12, b: 46 }, showlegend: false, xaxis: AXIS_MONTH, yaxis: { title: { text: "kWh" }, zeroline: true, tickformat: ",.0f" },
            shapes: thresholdShapes(tolerance),
          }} data={[{
            type: "bar", x: x(meterRows), y: meterRows.map((item) => item.residuum_kwh),
            marker: { color: meterRows.map((item) => (item.anomalie ? ROLE.anomalie : SWWTokens.tokens["grey-400"])) },
            hovertemplate: "%{x|%m/%Y}: %{y:,.0f} kWh<extra></extra>",
          }]} />
        </Card>
      ),
    },
    {
      id: "einordnung", render: (handle) => (
        <Card title={<TitleHelp help={`Abweichung je kW Anschlussleistung in Stunden. So werden große und kleine Anschlüsse vergleichbar; die rote Linie ist dieser Zähler. Nur ${fmt(share, 1)} % aller ${fmt(monthResiduals.length)} Zähler weichen in diesem Monat mindestens so stark ab.`}>{`Einordnung unter allen Zählern im ${monthLabel(row.monat)}`}</TitleHelp>} icon="chart-column" actions={handle}>
          <Chart height={260} layout={{
            margin: { l: 54, r: 12, t: 12, b: 46 }, showlegend: false, bargap: 0.04,
            xaxis: { title: { text: "Abweichung (h)" } }, yaxis: { title: { text: "Zähler" } },
            shapes: [...thresholdShapes(DATA.threshold.wert, "x"), { type: "line", yref: "paper", y0: 0, y1: 1, x0: row.residuum, x1: row.residuum, line: { color: ROLE.anomalie, width: 3 } }],
            annotations: [{ x: row.residuum, yref: "paper", y: 1, text: row.zaehler_id, showarrow: false, yanchor: "bottom", font: { color: ROLE.anomalie, size: 11 } }],
          }} data={[{ type: "histogram", x: monthResiduals, nbinsx: 60, marker: { color: ROLE.residuum } }]} />
        </Card>
      ),
    },
    { id: "ticket", render: (handle) => <TicketPanel row={row} context={context} handle={handle} /> },
    {
      id: "kontext", render: (handle) => (
        <Card title={<TitleHelp help="Informationen, die die Abweichung erklären könnten.">Kontext des Falls</TitleHelp>} icon="info" actions={handle}>
          <dl className="vc-facts">
            <div><dt>Kunde</dt><dd><Tag icon="building-2">{row.kunde_id}</Tag></dd></div>
            <div><dt>Branche</dt><dd><Tag dotColor={KUNDENTYP_COLOR[row.kundentyp]}>{row.kundentyp}</Tag></dd></div>
            <div><dt>Vertragsleistung</dt><dd><Tag icon="zap">{fmt(row.kw)} kW</Tag></dd></div>
            <div><dt>Wartung im Monat</dt><dd>{row.wartung == null ? <Tag icon="circle-help">keine Angabe</Tag> : row.wartung ? <Tag icon="wrench">geplant</Tag> : <Tag icon="circle-check">nicht geplant</Tag>}</dd></div>
            <div><dt>Produktionsplan</dt><dd>{row.plan == null ? <Tag icon="circle-help">keine Angabe</Tag> : <Tag icon="factory">{fmt(row.plan, 2)} · Ø {fmt(avgPlan, 2)}</Tag>}</dd></div>
            <div><dt>Plausibilität Vertragsleistung</dt><dd>{context.overCapacity ? <Badge status="critical" size="sm" icon="triangle-alert">über Maximum</Badge> : <Badge status="ok" size="sm" icon="circle-check">plausibel</Badge>}</dd></div>
            <div><dt>Hinweise dieses Zählers</dt><dd className="vc-hints">{meterRows.filter((item) => item.anomalie).map((item) => <Tag key={item.monat} icon="triangle-alert">{monthLabel(item.monat)}</Tag>)}</dd></div>
          </dl>
        </Card>
      ),
    },
  ];

  return (
    <VcShell {...shell} title={`Prüffall – ${row.zaehler_id}`}
      help={{
        label: "Wie entsteht ein Prüfhinweis?",
        text: `Die Toleranz richtet sich nach der Anschlussgröße: ±${fmt(DATA.threshold.wert, 0)} Stunden × Vertragsleistung. Sie wurde vor dem Testjahr so festgelegt, dass nur rund ${fmt((1 - (DATA.threshold.quantil ?? 0.99)) * 100, 0)} % der Monate auffallen. ${DATA.meta.caveat}`,
      }}
      filters={<>
        <Select size="sm" label="Fall wählen" value={row.id} onChange={(event) => onSelect(event.target.value)} style={{ minWidth: 320 }}
          options={DATA.alerts.slice().sort((a, b) => b.monat.localeCompare(a.monat) || b.score - a.score)
            .map((item) => ({ value: item.id, label: `${monthLabel(item.monat)} · ${item.zaehler_id} · ${deviationText(item)}` }))} />
        <div className="vc-toolbar__nav">
          <Button size="sm" variant="secondary" icon="chevron-left" aria-label="Vorheriger Fall" disabled={position <= 0} onClick={() => onSelect(monthList[position - 1].id)} />
          <span>Fall {position + 1} von {monthList.length} · {monthLabel(row.monat)}</span>
          <Button size="sm" variant="secondary" icon="chevron-right" aria-label="Nächster Fall" disabled={position >= monthList.length - 1} onClick={() => onSelect(monthList[position + 1].id)} />
        </div>
      </>}>
      <div data-testid="screen-prueffall">
        <div className="vc-definition">
          <div><span className="vc-definition__lbl">Erwartet</span><strong>{fmt(row.prognose)} kWh</strong><span>Modellprognose zu Monatsbeginn</span></div>
          <div><span className="vc-definition__lbl">Gemessen</span><strong>{fmt(row.ist)} kWh</strong><span>Ist nach Monatsabschluss</span></div>
          <div><span className="vc-definition__lbl">Abweichung</span><strong>{signed(row.residuum_kwh)} kWh</strong><span>{deviationText(row)} gegenüber der Erwartung</span></div>
          <div><span className="vc-definition__lbl">Toleranz für diesen Anschluss</span><strong>±{fmt(tolerance)} kWh</strong><span>{fmt(row.score, 1)}-fach überschritten</span></div>
        </div>
        <DraggableGrid items={panels} storageKey="sww-vc-prueffall-layout-v1" />
      </div>
    </VcShell>
  );
}

Object.assign(window, { PrueffallScreen, resolveCase });
