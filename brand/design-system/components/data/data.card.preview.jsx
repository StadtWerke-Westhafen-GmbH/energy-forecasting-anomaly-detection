
const { KpiTile, DataTable, Sparkline, StatusDot, Card, Tag, Badge, KUNDENTYP_COLOR } = window.StadtWerkeWesthafenDesignSystem_acd94c;
const trend=[820,905,870,1010,1180,1120,980,940,1005,1090,1240,1310];
const rows=[
 {zaehler_id:"ZW-04412",kundentyp:"Industrie",ist:"1.284.500",prognose:"928.700",abw:"+38,2 %",status:"critical",sl:"Kritisch",t:[910,880,940,1010,1284],a:[4]},
 {zaehler_id:"ZW-01187",kundentyp:"Gewerbe",ist:"212.340",prognose:"244.100",abw:"−13,0 %",status:"warn",sl:"Auffällig",t:[250,246,240,244,212],a:[4]},
 {zaehler_id:"ZW-00932",kundentyp:"Kommunal",ist:"88.120",prognose:"86.940",abw:"+1,4 %",status:"ok",sl:"In Toleranz",t:[84,85,87,87,88],a:[]},
 {zaehler_id:"ZW-06021",kundentyp:"Industrie",ist:"742.900",prognose:"755.300",abw:"−1,6 %",status:"ok",sl:"In Toleranz",t:[740,748,752,755,743],a:[]}];
function Demo(){const [sort,setSort]=React.useState({key:"abw",dir:"desc"});const [sel,setSel]=React.useState("ZW-04412");
 return (<div className="col" style={{gap:16}}>
  <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:12}}>
    <KpiTile label="Prognose 04/2025" value="14.820" unit="MWh" delta="+2,1 %" reference="vs. Ist 03/2025" icon="trending-up" spark={trend} />
    <KpiTile label="Ist 03/2025" value="14.514" unit="MWh" delta="−1,3 %" reference="vs. 02/2025" icon="zap" />
    <KpiTile label="MAE Test 2025" value="4.180" unit="kWh" icon="activity" reference="R² 0,912 · RMSE 7.940" />
    <KpiTile variant="accent" label="Offene Anomalien" value="128" delta="+18" deltaTone="bad" reference="vs. 02/2025" icon="triangle-alert" />
  </div>
  <Card title="Anomalien 03/2025" icon="triangle-alert" flush actions={<Badge status="critical" size="sm">14 kritisch</Badge>}>
    <DataTable rowKey="zaehler_id" sort={sort} onSortChange={setSort} selectedKey={sel} onRowClick={(r)=>setSel(r.zaehler_id)}
      columns={[{key:"zaehler_id",label:"Zähler",mono:true,width:110},
        {key:"kundentyp",label:"Kundentyp",render:r=><Tag dotColor={KUNDENTYP_COLOR[r.kundentyp]}>{r.kundentyp}</Tag>},
        {key:"prognose",label:"Prognose (kWh)",numeric:true,sortable:true},
        {key:"ist",label:"Ist (kWh)",numeric:true,sortable:true},
        {key:"abw",label:"Abweichung",numeric:true,sortable:true},
        {key:"trend",label:"24 Monate",render:r=><Sparkline values={r.t} anomalyIndices={r.a} />},
        {key:"status",label:"Status",render:r=><StatusDot status={r.status} label={r.sl} />}]}
      rows={rows} />
  </Card>
</div>);}
ReactDOM.createRoot(document.getElementById("root")).render(<Demo />);
