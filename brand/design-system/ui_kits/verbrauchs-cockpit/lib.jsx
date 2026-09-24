/* Shared helpers for the Verbrauchs-Cockpit. Reads only window.SWWForecastData (see README). */
const KUNDENTYPEN = ["Gewerbe", "Industrie", "Kommunal"];

function fmt(value, digits = 0) {
  if (value == null || !Number.isFinite(value)) return "—";
  return Number(value).toLocaleString("de-DE", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function signed(value, digits = 0, unit = "") {
  if (value == null || !Number.isFinite(value)) return "—";
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";
  return `${sign}${fmt(Math.abs(value), digits)}${unit}`;
}

function monthLabel(key) {
  const [year, month] = key.split("-");
  return `${month}/${year}`;
}

function sum(rows, key) {
  return rows.reduce((total, row) => total + (row[key] ?? 0), 0);
}

function errorMetrics(rows) {
  const n = rows.length;
  if (!n) return { rmse: null, mae: null, r2: null };
  const mean = sum(rows, "ist") / n;
  let se = 0; let ae = 0; let tss = 0;
  rows.forEach((row) => {
    const error = row.ist - row.prognose;
    se += error * error; ae += Math.abs(error); tss += (row.ist - mean) ** 2;
  });
  return { rmse: Math.sqrt(se / n), mae: ae / n, r2: tss ? 1 - se / tss : null };
}

/** Turns the columnar export into row objects once; everything else derives from these. */
const DATA = (() => {
  const D = window.SWWForecastData;
  const r = D.rows;
  const rows = r.zaehler_id.map((id, i) => ({
    id: `${id}-${r.monat[i]}`,
    zaehler_id: id,
    kunde_id: r.kunde_id[i],
    kundentyp: r.kundentyp[i],
    monat: r.monat[i],
    kw: r.vertragsleistung_kw[i],
    ist: r.verbrauch_kwh[i],
    prognose: r.prognose_kwh[i],
    baseline: r.rolling_3_kwh ? r.rolling_3_kwh[i] : null,
    residuum_kwh: r.residuum_kwh[i],
    residuum: r.residuum_vls[i],
    score: r.anomalie_score[i],
    anomalie: r.anomalie[i],
    hoch: r.residuum_vls[i] >= 0,
    richtung: r.richtung[i],
    wartung: r.wartung_aktiv ? r.wartung_aktiv[i] : null,
    plan: r.produktionsplan_index ? r.produktionsplan_index[i] : null,
  }));
  const meters = {};
  rows.forEach((row) => {
    meters[row.zaehler_id] ||= { zaehler_id: row.zaehler_id, kunde_id: row.kunde_id, kundentyp: row.kundentyp, kw: row.kw };
  });
  const history = {};
  const historyRows = [];
  if (D.history) {
    D.history.zaehler_id.forEach((id, i) => {
      const item = { zaehler_id: id, monat: D.history.monat[i], ist: D.history.verbrauch_kwh[i], kundentyp: meters[id]?.kundentyp, kunde_id: meters[id]?.kunde_id };
      (history[id] ||= []).push(item);
      historyRows.push(item);
    });
  }
  const alerts = rows.filter((row) => row.anomalie).sort((a, b) => b.score - a.score);
  const alertCount = {};
  alerts.forEach((row) => { alertCount[row.zaehler_id] = (alertCount[row.zaehler_id] || 0) + 1; });
  const finalModel = D.metrics.find((item) => item.final) || D.metrics[0];
  const bestBaseline = D.metrics.filter((item) => item.typ === "Baseline")
    .sort((a, b) => a.rmse - b.rmse)[0];
  return { ...D, rows, alerts, alertCount, meters, historyByMeter: history, historyRows, finalModel, bestBaseline };
})();

/** Month keys before the test year that exist in the history block. */
const HISTORY_MONTHS = [...new Set(DATA.historyRows.map((row) => row.monat))].sort();

function addMonths(key, n) {
  const [y, m] = key.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + n, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

function monthEnd(key) {
  const [y, m] = key.split("-").map(Number);
  const d = new Date(Date.UTC(y, m, 0));
  return `${String(d.getUTCDate()).padStart(2, "0")}.${String(m).padStart(2, "0")}.${y}`;
}

/** Monthly totals over history + test year: ist always, prognose only in the test year. */
function timeline(type = "all", kunde = "") {
  const pick = (row) => (type === "all" || row.kundentyp === type) && (!kunde || row.kunde_id === kunde);
  const byMonth = new Map();
  const add = (monat, key, value) => {
    if (!byMonth.has(monat)) byMonth.set(monat, { monat, ist: 0, prognose: null });
    const item = byMonth.get(monat);
    item[key] = (item[key] ?? 0) + value;
  };
  DATA.historyRows.filter(pick).forEach((row) => add(row.monat, "ist", row.ist));
  DATA.rows.filter(pick).forEach((row) => { add(row.monat, "ist", row.ist); add(row.monat, "prognose", row.prognose); });
  return [...byMonth.values()].sort((a, b) => a.monat.localeCompare(b.monat));
}

/** Plain-language deviation of one case relative to its forecast. */
function deviationText(row) {
  const pct = row.prognose ? (row.residuum_kwh / row.prognose) * 100 : null;
  return pct == null ? "—" : signed(pct, 0, " %");
}

function monthlyTotals(rows, months = DATA.months) {
  return months.map((monat) => {
    const inMonth = rows.filter((row) => row.monat === monat);
    const baselineRows = inMonth.filter((row) => row.baseline != null);
    return {
      monat,
      ist: sum(inMonth, "ist"),
      prognose: sum(inMonth, "prognose"),
      baseline: baselineRows.length === inMonth.length ? sum(inMonth, "baseline") : null,
      hinweise: inMonth.filter((row) => row.anomalie).length,
      n: inMonth.length,
    };
  });
}

function typeOptions(allLabel = "Alle Branchen") {
  return [{ value: "all", label: allLabel }, ...KUNDENTYPEN.map((value) => ({ value, label: value }))];
}

/** Customer id → branch, for the customer filter. */
const CUSTOMERS = (() => {
  const map = {};
  DATA.rows.forEach((row) => { map[row.kunde_id] ||= row.kundentyp; });
  return map;
})();

function scopeLabel(type, kunde) {
  if (kunde) return `Kunde ${kunde}`;
  return type === "all" ? "aller Zähler" : type;
}

/** Searchable customer filter (type to narrow the list); empty = all customers of the chosen branch. */
function CustomerFilter({ value, type, onChange }) {
  const { Input } = window.StadtWerkeWesthafenDesignSystem_acd94c;
  const [draft, setDraft] = React.useState(value);
  React.useEffect(() => { setDraft(value); }, [value]);
  const listId = React.useId();
  const options = Object.keys(CUSTOMERS).filter((id) => type === "all" || CUSTOMERS[id] === type).sort();
  const commit = (next) => {
    const id = next.trim().toUpperCase();
    if (!id) onChange("");
    else if (options.includes(id)) onChange(id);
  };
  return (
    <div className="vc-customer">
      <Input size="sm" label="Kunde" icon="search" placeholder="Alle Kunden" list={listId} value={draft}
        onChange={(event) => { setDraft(event.target.value); commit(event.target.value); }}
        onBlur={() => setDraft(value)} />
      <datalist id={listId}>{options.map((id) => <option key={id} value={id} />)}</datalist>
    </div>
  );
}

function monthOptions() {
  return DATA.months.map((value) => ({ value, label: monthLabel(value) }));
}

const AXIS_MONTH = { tickformat: "%m/%Y", dtick: "M2", title: { text: "Monat" } };

function toDate(key) {
  return `${key}-01`;
}

function thresholdShapes(value, axis = "y") {
  const line = { color: ROLE.schwellwert, width: 1.5, dash: "dash" };
  return [value, -value].map((v) => (axis === "y"
    ? { type: "line", xref: "paper", x0: 0, x1: 1, y0: v, y1: v, line }
    : { type: "line", yref: "paper", y0: 0, y1: 1, x0: v, x1: v, line }));
}

/** Small question-mark icon; the explanation appears on hover or keyboard focus. */
function HelpTip({ label, heading, small, children }) {
  const { Icon } = window.StadtWerkeWesthafenDesignSystem_acd94c;
  const id = React.useId();
  return (
    <span className={`vc-help${small ? " vc-help--sm" : ""}`}>
      <button type="button" className="vc-help__btn" aria-label={label} aria-describedby={id}><Icon name="circle-help" size={small ? 16 : 20} /></button>
      <span role="tooltip" id={id} className="vc-help__pop">{heading ? <strong>{heading}</strong> : null}{children}</span>
    </span>
  );
}

/** Card title with its explanation behind a small question mark. */
function TitleHelp({ children, help }) {
  return <span className="vc-ttl">{children}<HelpTip small label={`Erläuterung zu ${children}`}>{help}</HelpTip></span>;
}

/** Reads/writes a small JSON value in localStorage; the page keeps working if storage is blocked. */
function readStore(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch (_) { return fallback; }
}
function writeStore(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* storage blocked */ }
}

const TICKET_KEY = "sww-vc-tickets-v1";
const loadTickets = () => readStore(TICKET_KEY, {});

/**
 * Panels that can be rearranged by dragging their grip handle; the order is remembered per browser.
 * items: [{ id, wide, render: (handle) => node }]
 */
function DraggableGrid({ items, storageKey }) {
  const { Icon, Button } = window.StadtWerkeWesthafenDesignSystem_acd94c;
  const defaults = items.map((item) => item.id);
  const [order, setOrder] = React.useState(() => {
    const saved = readStore(storageKey, null);
    return Array.isArray(saved) && saved.length === defaults.length && defaults.every((id) => saved.includes(id)) ? saved : defaults;
  });
  const [dragging, setDragging] = React.useState(null);
  const [over, setOver] = React.useState(null);
  const armed = React.useRef(null);
  const source = React.useRef(null);
  const move = (from, to) => {
    if (!from || from === to) return;
    const next = order.slice();
    const a = next.indexOf(from); const b = next.indexOf(to);
    [next[a], next[b]] = [next[b], next[a]];
    setOrder(next); writeStore(storageKey, next);
  };
  const byId = Object.fromEntries(items.map((item) => [item.id, item]));
  const custom = order.join() !== defaults.join();
  return (
    <>
      <div className="vc-drag-grid">
        {order.map((id) => {
          const item = byId[id];
          const handle = (
            <span className="vc-drag-handle" title="Ziehen, um das Feld zu verschieben" aria-hidden="true"
              onMouseDown={() => { armed.current = id; }} onMouseUp={() => { armed.current = null; }}>
              <Icon name="grip-vertical" size={16} />
            </span>
          );
          return (
            <div key={id} className={`vc-drag-item${item.wide ? " is-wide" : ""}${dragging === id ? " is-dragging" : ""}${over === id && dragging !== id ? " is-over" : ""}`}
              draggable
              onDragStart={(event) => {
                if (armed.current !== id) { event.preventDefault(); return; }
                source.current = id;
                event.dataTransfer.effectAllowed = "move";
                event.dataTransfer.setData("text/plain", id);
                setTimeout(() => setDragging(id), 0); // restyling the source inside dragstart would cancel the drag
              }}
              onDragOver={(event) => { if (source.current) { event.preventDefault(); event.dataTransfer.dropEffect = "move"; if (over !== id) setOver(id); } }}
              onDragLeave={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setOver((current) => (current === id ? null : current)); }}
              onDrop={(event) => { event.preventDefault(); move(source.current, id); setOver(null); }}
              onDragEnd={() => { source.current = null; armed.current = null; setDragging(null); setOver(null); }}>
              {item.render(handle)}
            </div>
          );
        })}
      </div>
      {custom ? (
        <div className="vc-drag-reset">
          <Button size="sm" variant="ghost" icon="rotate-ccw" onClick={() => { setOrder(defaults); writeStore(storageKey, defaults); }}>Anordnung zurücksetzen</Button>
        </div>
      ) : null}
    </>
  );
}

Object.assign(window, {
  HelpTip, TitleHelp, CustomerFilter, CUSTOMERS, scopeLabel, readStore, writeStore, TICKET_KEY, loadTickets, DraggableGrid,
  KUNDENTYPEN, fmt, signed, monthLabel, sum, errorMetrics, DATA, monthlyTotals,
  typeOptions, monthOptions, AXIS_MONTH, toDate, thresholdShapes,
  HISTORY_MONTHS, addMonths, monthEnd, timeline, deviationText,
});
