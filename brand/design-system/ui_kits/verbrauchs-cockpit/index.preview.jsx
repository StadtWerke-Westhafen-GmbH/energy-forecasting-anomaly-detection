function App() {
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("screen");
  const screens = ["prognose", "anomalien", "prueffall"];
  const [screen, setScreen] = React.useState(screens.includes(requested) ? requested : "prognose");
  const [caseId, setCaseId] = React.useState(params.get("fall"));
  /* Filters shared by all screens: a month chosen in the forecast is also the month of the work list. */
  const [selection, setSelection] = React.useState({ month: DATA.months[DATA.months.length - 1], type: "all", kunde: "", direction: "all", unit: "kWh" });
  const onSelection = (change) => {
    setSelection((current) => {
      const next = { ...current, ...change };
      // A customer outside the newly chosen branch would silently empty every view.
      if (next.kunde && next.type !== "all" && CUSTOMERS[next.kunde] !== next.type) next.kunde = "";
      return next;
    });
    if (change.month) setCaseId(null);
  };
  React.useEffect(() => {
    document.getElementById("main-content")?.scrollTo({ top: 0, behavior: "auto" });
  }, [screen, caseId]);
  /* A case always belongs to a month; keep the shared month in step with it. */
  const selectCase = (id) => {
    const row = DATA.alerts.find((item) => item.id === id);
    if (row) setSelection((current) => ({ ...current, month: row.monat }));
    setCaseId(id);
  };
  const openCase = (id) => { selectCase(id); setScreen("prueffall"); };
  const shell = { screen, onNavigate: setScreen };
  if (screen === "anomalien") return <AnomalienScreen shell={shell} selection={selection} onSelection={onSelection} onOpenCase={openCase} />;
  if (screen === "prueffall") return <PrueffallScreen shell={shell} selection={selection} caseId={caseId} onSelect={selectCase} />;
  return <PrognoseScreen shell={shell} selection={selection} onSelection={onSelection} />;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
