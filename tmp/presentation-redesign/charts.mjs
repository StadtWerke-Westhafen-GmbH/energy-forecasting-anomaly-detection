import fs from 'node:fs';

// Chart workbook snapshots use six decimal places, well below the displayed precision.
// Full precision remains in the notebook and audit inputs; Excel stores at most 15 digits.
const source = JSON.parse(fs.readFileSync(new URL('./audit/chart_data.json', import.meta.url), 'utf8'),
  (key,value)=>typeof value==='number'?Number(value.toFixed(6)):value);
const facts = JSON.parse(fs.readFileSync(new URL('./audit/fact_summary.json', import.meta.url), 'utf8'));
const FONT = 'IBM Plex Sans';
const C = { navy:'#084878', cyan:'#0090C8', teal:'#0080A0', grey:'#8C98A6', amber:'#A86505', red:'#B3261E', ink:'#142A3A', muted:'#4E5A68', grid:'#E4E9EF' };
const months = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];
const noLine = { fill:'none', width:0 };
const fmt = (n, digits=0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits:digits, maximumFractionDigits:digits });
const font = (size=22, fill=C.muted, bold=false) => ({ typeface:FONT, fontSize:size, fill, bold });
const axisTitle = text => ({ text, textStyle:font(22) });
const labels = (size=23) => ({ showValue:true, showSeriesName:false, showCategoryName:false, position:'outEnd', textStyle:font(size,C.ink,true) });
const overrides = (values,digits=0) => values.map((v,idx) => ({ idx, text:fmt(v,digits), showValue:true, textStyle:font(23,C.ink,true) }));
const common = position => ({ position, hasLegend:false, chartFill:'#FFFFFF', plotAreaFill:'#FFFFFF', chartLine:noLine, plotAreaLine:noLine, titlePlacement:'none', titleTextStyle:font(22) });
const grid = { style:'solid', fill:C.grid, width:1 };
const axisLine = { style:'solid', fill:C.grid, width:1 };
const valueAxis = (title,max,majorUnit) => ({ visible:true, min:0, max, majorUnit, title:axisTitle(title), numberFormatCode:'0', textStyle:font(), line:noLine, majorGridlines:grid, minorGridlines:null });
const categoryAxis = () => ({ visible:true, textStyle:font(), line:axisLine, majorGridlines:null, minorGridlines:null });

function bars(slide,position,categories,values,{title='RMSE (kWh)',max,step,digits=0,colors,gap=68,horizontal=true}={}) {
  const data = { name:title, values, valuesFormatCode:digits?'#,##0.0':'#,##0', fill:C.grey, line:noLine,
    points:values.map((v,idx) => ({idx,fill:colors?.[idx] || C.grey,line:noLine})), dataLabelOverrides:overrides(values,digits) };
  return slide.charts.add('bar', {
    ...common(position), categories, series:[data], barOptions:{direction:horizontal?'bar':'column',grouping:'clustered',gapWidth:gap,varyColors:false},
    xAxis:horizontal?valueAxis(title,max,step):categoryAxis(),
    yAxis:horizontal?categoryAxis():valueAxis(title,max,step), dataLabels:labels(),
  });
}

// Returned arrays contain only native PowerPoint chart objects.
export function addChart(slide,key,position) {
  if (!position) throw new Error(`Chart ${key}: position is required`);
  if (key==='cv' || key==='benchmark') {
    const trace = source[key==='cv'?'learn-cv-comparison':'learn-benchmark'].data[0];
    return [bars(slide,position,['Vormonat','Mittel bis 3 Monate','Lineare Regression','Random Forest'],trace.x,
      {max:key==='cv'?22000:17000,step:key==='cv'?5000:5000,colors:[C.grey,C.grey,C.navy,C.teal],gap:65})];
  }
  if (key==='importance') {
    const trace = source['learn-feature-importance'].data[0];
    return [bars(slide,position,trace.y,trace.x,{title:'RMSE-Anstieg (kWh)',max:8500,step:2000,gap:48,colors:trace.x.map((v,i)=>i===6?C.teal:C.grey)})];
  }
  if (key==='rank') {
    const d = source['learn-ranked-errors'].data;
    const threshold = d[2].y[0];
    return [slide.charts.add('scatter', {
      ...common(position), scatterOptions:{style:'line',varyColors:false},
      series:[
        {name:'Kalibrierungsfehler',xValues:d[0].x,values:d[0].y,line:{fill:C.navy,width:3,style:'solid'},marker:{symbol:'none'}},
        {name:'Oberhalb der Schwelle',xValues:d[1].x,values:d[1].y,line:{fill:C.red,width:3,style:'solid'},marker:{symbol:'none'}},
        {name:'99-%-Schwelle',xValues:[0,100],values:[threshold,threshold],line:{fill:C.amber,width:2,style:'dotted'},marker:{symbol:'none'}},
      ],
      xAxis:{...valueAxis('Perzentil der Kalibrierungsfehler',100,20),numberFormatCode:'0" %"',majorGridlines:null,line:axisLine},
      yAxis:valueAxis('Absoluter Fehler (VLS-h)',500,100),
    })];
  }
  if (key==='monthly') {
    const values = facts.monthly.map(v=>v.alerts);
    return [bars(slide,position,months,values,{title:'Prüfhinweise',max:20,step:5,horizontal:false,gap:70,colors:values.map(v=>v===16?C.red:C.navy)})];
  }
  if (key==='case') {
    const d = source['learn-case-timeseries'].data;
    return [slide.charts.add('line',{
      ...common(position), categories:months, hasLegend:true,
      legend:{position:'bottom',overlay:false,textStyle:font(22)},
      lineOptions:{smooth:false,grouping:'standard'},
      series:[
        {name:'Ist',values:d[0].y,valuesFormatCode:'#,##0',line:{fill:C.navy,width:3,style:'solid'},fill:C.navy,marker:{symbol:'circle',size:6},points:[{idx:7,fill:C.red,line:{fill:C.red,width:2}}],
          dataLabelOverrides:[{idx:7,text:fmt(d[0].y[7]),showValue:true,textStyle:font(23,C.red,true),position:'outEnd'}]},
        {name:'Prognose',values:d[1].y,valuesFormatCode:'#,##0',line:{fill:C.cyan,width:3,style:'dashed'},fill:C.cyan,marker:{symbol:'none'}},
      ],
      xAxis:categoryAxis(),yAxis:valueAxis('Verbrauch (kWh)',25000,5000),
    })];
  }
  if (key==='metrics') {
    const d = source['learn-metrics-example'].data;
    return [slide.charts.add('bar',{
      ...common(position),categories:['A: gleichmäßige Fehler','B: ein großer Fehler'],hasLegend:true,
      legend:{position:'bottom',overlay:false,textStyle:font(22)},
      series:d.map((t,i)=>({name:i?'RMSE':'MAE',values:t.y,valuesFormatCode:'0',fill:i?C.teal:C.navy,line:noLine,dataLabelOverrides:overrides(t.y)})),
      barOptions:{direction:'column',grouping:'clustered',gapWidth:95},
      xAxis:categoryAxis(),yAxis:valueAxis('Kennzahlenwert (kWh)',25,5),dataLabels:labels(),
    })];
  }
  if (key==='target') {
    const trace = source['learn-vls-vs-kwh'].data[0];
    return [bars(slide,position,['Direkt in kWh','VLS, zurück in kWh'],trace.y,{max:12000,step:4000,colors:[C.grey,C.teal],gap:110,horizontal:false})];
  }
  if (key==='threshold') {
    const trace = source['learn-threshold-workload'].data[0];
    return [bars(slide,position,['95 %','97,5 %','99 %','99,5 %'],trace.y,{title:'Prüfhinweise je Monat',max:40,step:10,digits:1,horizontal:false,gap:88,colors:[C.grey,C.grey,C.amber,C.grey]})];
  }
  if (key==='folds') {
    const d = source['learn-cv-comparison'].data.slice(1);
    return [bars(slide,position,['Fold 1','Fold 2','Fold 3'],d.map(t=>t.x[3]),{max:22000,step:5000,horizontal:false,gap:100,colors:[C.teal,C.teal,C.teal]})];
  }
  throw new Error(`Unknown chart key: ${key}`);
}

export const chartFacts = Object.freeze({
  cvMeans:source['learn-cv-comparison'].data[0].x,
  cvFolds:source['learn-cv-comparison'].data.slice(1).map(t=>({name:t.name,modelNames:t.y,values:t.x})),
  benchmark:source['learn-benchmark'].data[0].x,
  rank:{observations:1397,threshold:source['learn-ranked-errors'].data[2].y[0],max:Math.max(...source['learn-ranked-errors'].data[1].y),aboveThreshold:14},
  monthlyTotal:facts.monthly.reduce((sum,m)=>sum+m.alerts,0),
  metricsExamples:{A:[10,10,10,10],B:[0,0,0,40],mae:[10,10],rmse:[10,20]},
  caveats:{retrospective:true,confirmedAnomalyLabels:false,thresholdCalibrationPeriod:'11/2024–12/2024',benchmarkPeriod:'01/2025–12/2025'},
});
