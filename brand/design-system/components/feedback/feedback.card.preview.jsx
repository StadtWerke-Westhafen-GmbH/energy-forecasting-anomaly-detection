
const { Alert, Dialog, EmptyState, Button, Card } = window.StadtWerkeWesthafenDesignSystem_acd94c;
function Demo(){const [open,setOpen]=React.useState(false);
 return (<div className="col" style={{gap:14}}>
  <Alert status="warn" title="Einheiten gemischt">412 Werte in verbrauch_kwh liegen als MWh-Text vor und wurden umgerechnet.</Alert>
  <Alert status="critical" title="14 kritische Anomalien offen" actions={<Button size="sm" variant="secondary">Zur Liste</Button>}>Abweichung über 30 % in 03/2025 — Netzmanagement informiert.</Alert>
  <Alert status="ok" title="Modelllauf abgeschlossen" onDismiss={()=>{}}>Training 2024, Test 2025. R² 0,912 · MAE 4.180 kWh.</Alert>
  <Alert status="neutral">Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges.</Alert>
  <div style={{display:'grid',gridTemplateColumns:'1fr 220px',gap:16,alignItems:'center'}}>
    <Card variant="flat" flush><EmptyState size="sm" icon="triangle-alert" title="Keine Anomalien über dem Schwellwert"
      actions={<Button variant="secondary" size="sm">Filter zurücksetzen</Button>}>Schwellwert: 95. Perzentil der absoluten prozentualen Abweichung (18,0 %).</EmptyState></Card>
    <Button variant="primary" onClick={()=>setOpen(true)}>Dialog zeigen</Button>
  </div>
  <Dialog open={open} onClose={()=>setOpen(false)} title="Anomalie-Ticket anlegen" subtitle="Zähler ZW-04412 · 03/2025"
    footer={<><Button variant="secondary" onClick={()=>setOpen(false)}>Abbrechen</Button><Button variant="primary" icon="check">Ticket anlegen</Button></>}>
    <p style={{margin:0}}>Abweichung +38,2 % über dem Schwellwert. Das Ticket geht an Netzmanagement (Anke Bürger).</p>
  </Dialog>
</div>);}
ReactDOM.createRoot(document.getElementById("root")).render(<Demo />);
