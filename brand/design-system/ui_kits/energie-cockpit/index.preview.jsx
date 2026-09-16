
const { Dialog, Button, Select, Input, Checkbox } = window.StadtWerkeWesthafenDesignSystem_acd94c;
const TITLES = {uebersicht:"Übersicht",anomalien:"Anomalien",zaehler:"Zähler-Detail",beschaffung:"Beschaffung",qualitaet:"Datenqualität"};
function App(){
  const [screen,setScreen]=React.useState("uebersicht");
  const [monat,setMonat]=React.useState("03/2025");
  const [zaehlerId,setZaehlerId]=React.useState("ZW-04412");
  const [ticket,setTicket]=React.useState(null);
  const open=(id)=>{ if(id){setZaehlerId(id);setScreen("zaehler");} else setScreen("anomalien"); };
  return (
    <Shell screen={screen} onNavigate={setScreen} title={TITLES[screen]} monat={monat} onMonthChange={setMonat}>
      {screen==="uebersicht"?<UebersichtScreen monat={monat} onOpenZaehler={open} />:null}
      {screen==="anomalien"?<AnomalienScreen monat={monat} onOpenZaehler={open} />:null}
      {screen==="zaehler"?<ZaehlerDetailScreen zaehlerId={zaehlerId} monat={monat} onBack={()=>setScreen("anomalien")} onTicket={setTicket} />:null}
      {screen==="beschaffung"?<BeschaffungScreen monat={monat} />:null}
      {screen==="qualitaet"?<DatenqualitaetScreen />:null}
      <Dialog open={Boolean(ticket)} onClose={()=>setTicket(null)} title="Anomalie-Ticket anlegen"
        subtitle={ticket?ticket.zaehler_id+" · "+ticket.kunde+" · "+monat:""}
        footer={<Button variant="primary" onClick={()=>setTicket(null)}>Beispiel schließen</Button>}>
        {ticket?<div style={{display:"flex",flexDirection:"column",gap:"var(--space-4)"}}>
          <p style={{margin:0}}>Abweichung {window.SWWData.fmtPct(ticket.abweichung_pct)} gegenüber der Prognose. Dieses Formular zeigt einen möglichen Prüfprozess. Es wird kein Ticket versendet.</p>
          <Select label="Prüfgrund" options={["Zählerauslesung prüfen","Leitungsverlust vermuten","Abrechnungsfehler prüfen","Produktionsplan abweichend"]} />
          <Input label="Notiz" placeholder="Kurzbeschreibung für Netzmanagement" />
          <Checkbox label="Netzmanagement per E-Mail informieren (Beispiel)" disabled />
        </div>:null}
      </Dialog>
    </Shell>
  );
}
ReactDOM.createRoot(document.getElementById("root")).render(<App />);
