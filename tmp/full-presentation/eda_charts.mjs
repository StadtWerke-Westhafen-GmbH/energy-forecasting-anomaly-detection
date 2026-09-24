import fs from 'node:fs';

export const edaFacts = JSON.parse(fs.readFileSync(new URL('./audit/eda_data.json', import.meta.url),'utf8'));
const FONT='IBM Plex Sans';
const C={navy:'#084878',teal:'#0080A0',green:'#2F7A33',grey:'#8C98A6',ink:'#142A3A',muted:'#4E5A68',grid:'#E4E9EF'};
const colors=[C.teal,C.navy,C.green];
const noLine={fill:'none',width:0};
const line={fill:C.grid,width:1,style:'solid'};
const style=(size=22,fill=C.muted,bold=false)=>({typeface:FONT,fontSize:size,fill,bold});
const rounded=values=>values.map(v=>Number(v.toFixed(6)));
const fmt=(value,digits=0)=>value.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits});
const base=position=>({position,chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:noLine,plotAreaLine:noLine,hasLegend:false,titlePlacement:'none',titleTextStyle:style(24)});
const category=()=>({visible:true,textStyle:style(),line,majorGridlines:null,minorGridlines:null});
const numeric=(title,max,majorUnit,format='0')=>({visible:true,title:{text:title,textStyle:style()},min:0,max,majorUnit,numberFormatCode:format,textStyle:style(),line:noLine,majorGridlines:line,minorGridlines:null});
const dataLabels={position:'outEnd',showValue:true,showSeriesName:false,showCategoryName:false,textStyle:style(23,C.ink,true)};
const direct=(values,digits=0,suffix='')=>values.map((v,idx)=>({idx,text:fmt(v,digits)+suffix,showValue:true,position:'outEnd',textStyle:style(23,C.ink,true)}));

function oneBarChart(slide,position,categories,values,{name,max,step,digits=0}) {
  return slide.charts.add('bar',{
    ...base(position),categories,
    series:[{name,values:rounded(values),valuesFormatCode:digits?'0.0':'0',fill:C.navy,line:noLine,
      points:values.map((v,idx)=>({idx,fill:colors[idx],line:noLine})),dataLabelOverrides:direct(values,digits)}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:95,varyColors:false},
    xAxis:category(),yAxis:numeric(name,max,step),dataLabels,
  });
}

// Three chart concepts, native PowerPoint objects only. 'normalization' returns two
// charts with separate units and scales; use a position at least 1050 px wide.
export function addEdaChart(slide,key,position) {
  if(!position) throw new Error(`EDA chart ${key}: missing position`);
  const data=edaFacts.charts[key];
  if(!data) throw new Error(`Unknown EDA chart key: ${key}`);
  if(key==='monthly') {
    return [slide.charts.add('line',{
      ...base(position),categories:data.categories,hasLegend:true,
      legend:{position:'bottom',overlay:false,textStyle:style(22)},lineOptions:{smooth:false,grouping:'standard'},
      series:data.series.map((s,i)=>({name:s.name,values:rounded(s.values),valuesFormatCode:'0',
        line:{fill:i?C.navy:C.grey,width:i?3.5:2.5,style:'solid'},fill:i?C.navy:C.grey,marker:{symbol:'circle',size:i?6:5}})),
      xAxis:category(),yAxis:numeric('Monatsverbrauch (MWh)',25000,5000),
    })];
  }
  if(key==='portfolio') {
    return [slide.charts.add('bar',{
      ...base(position),categories:data.categories,hasLegend:true,
      legend:{position:'bottom',overlay:false,textStyle:style(22)},
      series:data.series.map((s,i)=>({name:s.name,values:rounded(s.values),valuesFormatCode:'0.0" %"',
        fill:i?C.navy:C.grey,line:noLine,dataLabelOverrides:direct(s.values,1,' %')})),
      barOptions:{direction:'column',grouping:'clustered',gapWidth:95,overlap:0},
      xAxis:category(),yAxis:numeric('Anteil (%)',80,20,'0" %"'),dataLabels,
    })];
  }
  if(key==='normalization') {
    const gap=44;
    const width=(position.width-gap)/2;
    const left={...position,width};
    const right={...position,left:position.left+width+gap,width};
    return [
      oneBarChart(slide,left,data.categories,data.raw_values,{name:'Median Verbrauch (kWh)',max:60000,step:20000}),
      oneBarChart(slide,right,data.categories,data.normalized_values,{name:'Median Volllaststunden (h)',max:200,step:50,digits:1}),
    ];
  }
  throw new Error(`Unknown EDA chart key: ${key}`);
}
