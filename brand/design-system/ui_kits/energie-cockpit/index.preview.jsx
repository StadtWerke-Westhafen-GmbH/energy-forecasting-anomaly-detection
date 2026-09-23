const { Dialog, Button, Select, Input, Alert } = window.StadtWerkeWesthafenDesignSystem_acd94c;

const TITLES = {
  uebersicht: "Übersicht",
  anomalien: "Anomalieprüfung",
  zaehler: "Prüffall",
  beschaffung: "Beschaffung",
  qualitaet: "Datenqualität",
};
const STORAGE_KEY = "sww-anomaly-reviews-v1";

function loadDecisions() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch (_) {
    return {};
  }
}

function ReviewDialog({ alert, current, onClose, onSave }) {
  const D = window.SWWAnomalyData;
  const [form, setForm] = React.useState({});
  React.useEffect(() => {
    if (!alert) return;
    setForm({
      workflow: current?.workflow || "in_pruefung",
      measurement: current?.measurement || "unklar",
      explained: current?.explained || "unklar",
      cause: current?.cause || "Noch ungeklärt",
      action: current?.action || "Noch offen",
      owner: current?.owner || "",
      note: current?.note || "",
    });
  }, [alert, current]);
  const update = (key) => (event) => setForm((value) => ({ ...value, [key]: event.target.value }));
  const save = () => onSave(alert.alert_id, { ...form, updated_at: new Date().toISOString() });

  return (
    <Dialog open={Boolean(alert)} onClose={onClose} size="lg"
      title="Bewertung dokumentieren"
      subtitle={alert ? `${alert.zaehler_id} · ${alert.month_label} · Score ${alert.score.toLocaleString("de-DE", { maximumFractionDigits: 2 })}` : ""}
      footer={<>
        <Button variant="secondary" onClick={onClose}>Abbrechen</Button>
        <Button variant="primary" icon="save" onClick={save}>Lokal speichern</Button>
      </>}>
      {alert ? (
        <div className="anomaly-review-form">
          <Alert status="info" title="Getrennte Bewertungsdimensionen">
            Dokumentieren Sie Messwert, Erklärung und Handlungsbedarf getrennt. So entstehen später belastbare Labels; weder Ticket noch E-Mail werden versendet.
          </Alert>
          <Select label="Bearbeitungsstatus" value={form.workflow || "in_pruefung"} onChange={update("workflow")}
            options={D.review_options.workflow} />
          <div className="anomaly-review-form__pair">
            <Select label="Messwert gültig?" value={form.measurement || "unklar"} onChange={update("measurement")}
              options={D.review_options.tri_state} />
            <Select label="Abweichung erklärt?" value={form.explained || "unklar"} onChange={update("explained")}
              options={D.review_options.tri_state} />
          </div>
          <div className="anomaly-review-form__pair">
            <Select label="Wahrscheinliche Ursache" value={form.cause || "Noch ungeklärt"} onChange={update("cause")}
              options={D.review_options.causes} />
            <Select label="Handlungsbedarf" value={form.action || "Noch offen"} onChange={update("action")}
              options={D.review_options.actions} />
          </div>
          <Input label="Verantwortliche Person oder Rolle" placeholder="z. B. Messwesen" value={form.owner || ""} onChange={update("owner")} />
          <Input label="Prüfnotiz" placeholder="Beobachtung, Rückfrage oder Entscheidung" value={form.note || ""} onChange={update("note")} />
        </div>
      ) : null}
    </Dialog>
  );
}

function App() {
  const D = window.SWWAnomalyData;
  const requestedScreen = new URLSearchParams(window.location.search).get("screen");
  const initialScreen = Object.hasOwn(TITLES, requestedScreen) ? requestedScreen : "uebersicht";
  const [screen, setScreen] = React.useState(initialScreen);
  const [monat, setMonat] = React.useState("03/2025");
  const [alertId, setAlertId] = React.useState(D.alerts[0].alert_id);
  const [reviewAlert, setReviewAlert] = React.useState(null);
  const [decisions, setDecisions] = React.useState(loadDecisions);

  React.useEffect(() => {
    document.getElementById("main-content")?.scrollTo({ top: 0, behavior: "auto" });
  }, [screen, alertId]);

  const openCase = (value) => {
    const id = typeof value === "string" ? value : value?.alert_id;
    const match = D.alerts.find((item) => item.alert_id === id || item.zaehler_id === id) || D.alerts[0];
    setAlertId(match.alert_id);
    setScreen("zaehler");
  };
  const navigate = (next) => {
    setScreen(next);
    if (next === "zaehler" && !alertId) setAlertId(D.alerts[0].alert_id);
  };
  const saveDecision = (id, decision) => {
    setDecisions((current) => {
      const next = { ...current, [id]: decision };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
    setReviewAlert(null);
  };

  return (
    <Shell screen={screen} onNavigate={navigate} title={TITLES[screen]} monat={monat} onMonthChange={setMonat}>
      {screen === "uebersicht" ? <UebersichtScreen monat={monat} onOpenZaehler={openCase} /> : null}
      {screen === "anomalien" ? <AnomalienScreen decisions={decisions} onOpenCase={openCase} /> : null}
      {screen === "zaehler" ? <ZaehlerDetailScreen alertId={alertId} decisions={decisions}
        onBack={() => setScreen("anomalien")} onReview={setReviewAlert} /> : null}
      {screen === "beschaffung" ? <BeschaffungScreen monat={monat} /> : null}
      {screen === "qualitaet" ? <DatenqualitaetScreen /> : null}
      <ReviewDialog alert={reviewAlert}
        current={reviewAlert ? decisions[reviewAlert.alert_id] : null}
        onClose={() => setReviewAlert(null)} onSave={saveDecision} />
    </Shell>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
