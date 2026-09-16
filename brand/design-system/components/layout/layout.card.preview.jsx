
const { Card, PageHeader, Tabs, SidebarNav, Button, Badge, Select } = window.StadtWerkeWesthafenDesignSystem_acd94c;
function Demo(){
  const [tab,setTab]=React.useState("kritisch");
  const [nav,setNav]=React.useState("anomalien");
  return (<div className="wrap">
    <div style={{height:340,borderRadius:'var(--radius-card)',overflow:'hidden',border:'1px solid var(--border-default)'}}>
      <SidebarNav value={nav} onChange={setNav} logoSrc="../../assets/logo-sww-wordmark.png" markSrc="../../assets/logo-sww-emblem.png"
        footer="Modell v2.3 · Stand 01.04.2025"
        items={[{id:"uebersicht",label:"Übersicht",icon:"layout-dashboard",group:"Betrieb"},
                {id:"anomalien",label:"Anomalien",icon:"triangle-alert",group:"Betrieb",count:128,alert:true},
                {id:"zaehler",label:"Zähler",icon:"gauge",group:"Betrieb"},
                {id:"beschaffung",label:"Beschaffung",icon:"shopping-cart",group:"Planung"},
                {id:"qualitaet",label:"Datenqualität",icon:"database",group:"Planung"}]} />
    </div>
    <div className="col" style={{gap:16}}>
      <PageHeader eyebrow="Frühwarnung" title="Anomalien 03/2025"
        subtitle="Zähler mit absoluter Abweichung über dem 95-Perzentil-Schwellwert."
        meta={<><span>128 von 700 Zählern</span><span>·</span><span>Stand 01.04.2025, 06:00</span></>}
        actions={<Button variant="secondary" size="sm" icon="download">Export</Button>} />
      <Tabs value={tab} onChange={setTab} items={[{id:"alle",label:"Alle",count:128},{id:"kritisch",label:"Kritisch",icon:"octagon-alert",count:14},{id:"auffaellig",label:"Auffällig",count:72},{id:"geprueft",label:"Geprüft",count:42}]} />
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
        <Card title="Prognosegüte" subtitle="Test 2025" icon="trending-up" status="brand"
          actions={<Select size="sm" options={["RMSE","MAE","R²"]} />} footer="Random-Forest-Regressor">
          <div style={{font:'var(--text-metric-sm)',fontVariantNumeric:'tabular-nums'}}>R² 0,912</div>
        </Card>
        <Card title="Datenqualität" status="warn" icon="database"
          actions={<Badge status="warn" size="sm" icon="triangle-alert">3 Befunde</Badge>}>
          412 Werte als MWh-Text, 38 Duplikate, 11 negative Verbräuche.
        </Card>
      </div>
    </div>
  </div>);}
ReactDOM.createRoot(document.getElementById("root")).render(<Demo />);
