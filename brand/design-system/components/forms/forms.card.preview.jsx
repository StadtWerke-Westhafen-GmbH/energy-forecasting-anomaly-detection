
const { Input, Select, Checkbox, Switch } = window.StadtWerkeWesthafenDesignSystem_acd94c;
function Demo(){return (<div className="col" style={{gap:18}}>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:16}}>
    <Input label="Zähler-ID" icon="search" placeholder="ZW-04412" />
    <Input label="Schwellwert" numeric suffix="%" defaultValue="18,0" hint="95. Perzentil der Residuen" />
    <Input label="Vertragsleistung" numeric suffix="kW" defaultValue="-40" error="Wert muss > 0 sein" />
  </div>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:16}}>
    <Select label="Monat" options={["01/2025","02/2025","03/2025"]} defaultValue="03/2025" />
    <Select label="Kundentyp" options={[{value:"all",label:"Alle Kundentypen"},{value:"Gewerbe",label:"Gewerbe"},{value:"Industrie",label:"Industrie"},{value:"Kommunal",label:"Kommunal"}]} />
    <Input label="Gesperrt" disabled placeholder="Nicht verfügbar" />
  </div>
  <div><p className="lbl">Checkbox · Switch</p><div className="row" style={{gap:28,alignItems:'flex-start'}}>
    <Checkbox label="Nur Anomalien über Schwellwert" defaultChecked />
    <Checkbox label="Wartungsmonate ausschließen" hint="wartung_aktiv = 1" />
    <Checkbox label="Alle Zähler" indeterminate />
    <Checkbox label="Gesperrt" disabled defaultChecked />
    <Switch label="Konfidenzband anzeigen" defaultChecked />
    <Switch label="Auto-Refresh" hint="alle 15 Minuten" />
  </div></div>
</div>);}
ReactDOM.createRoot(document.getElementById("root")).render(<Demo />);
