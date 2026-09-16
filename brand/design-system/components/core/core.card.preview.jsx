
const { Button, IconButton, Badge, Tag, Icon, KUNDENTYP_COLOR } = window.StadtWerkeWesthafenDesignSystem_acd94c;
function Demo(){return (<div className="col" style={{gap:18}}>
  <div><p className="lbl">Button — Varianten</p><div className="row">
    <Button variant="primary" icon="trending-up">Prognose erstellen</Button>
    <Button variant="accent">Anomalie prüfen</Button>
    <Button variant="secondary" icon="download">Export</Button>
    <Button variant="ghost" iconAfter="arrow-right">Alle Anomalien</Button>
    <Button variant="danger" icon="trash-2">Verwerfen</Button>
    <Button disabled>Gesperrt</Button>
  </div></div>
  <div><p className="lbl">Größen · Loading · IconButton</p><div className="row">
    <Button size="sm" variant="secondary">sm 28</Button>
    <Button size="md" variant="secondary">md 36</Button>
    <Button size="lg" variant="secondary">lg 44</Button>
    <Button loading>Läuft</Button>
    <span style={{width:12}} />
    <IconButton icon="filter" label="Filter" bordered />
    <IconButton icon="refresh-cw" label="Aktualisieren" bordered />
    <IconButton icon="ellipsis-vertical" label="Mehr" />
    <IconButton icon="rows-3" label="Kompakt" pressed />
  </div></div>
  <div><p className="lbl">Badge — Anomalie-Schweregrade · Tag — Kundentyp</p><div className="row">
    <Badge status="ok" icon="check">Geprüft</Badge>
    <Badge status="info" icon="info">Hinweis</Badge>
    <Badge status="warn" icon="triangle-alert">Auffällig</Badge>
    <Badge status="critical" icon="octagon-alert">Kritisch</Badge>
    <Badge status="brand" solid size="sm">Prognose</Badge>
    <span style={{width:12}} />
    <Tag dotColor={KUNDENTYP_COLOR.Gewerbe}>Gewerbe</Tag>
    <Tag dotColor={KUNDENTYP_COLOR.Industrie}>Industrie</Tag>
    <Tag dotColor={KUNDENTYP_COLOR.Kommunal}>Kommunal</Tag>
    <Tag icon="wrench">Wartung aktiv</Tag>
    <Tag selected onClick={()=>{}} onRemove={()=>{}}>Abweichung &gt; 18 %</Tag>
  </div></div>
  <div><p className="lbl">Icon — Domänen-Mapping (Lucide, 20px)</p><div className="row" style={{gap:18,color:'var(--navy-700)'}}>
    {["zap","trending-up","activity","triangle-alert","gauge","factory","store","landmark","thermometer","wrench","shopping-cart","database","file-chart-column","calendar","filter","download"].map(n=><Icon key={n} name={n} size={20} title={n} />)}
  </div></div>
</div>);}
ReactDOM.createRoot(document.getElementById("root")).render(<Demo />);
