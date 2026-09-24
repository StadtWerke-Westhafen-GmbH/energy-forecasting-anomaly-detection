from pathlib import Path
import re

d=Path(__file__).resolve().parent
old=(d.parent/'presentation-redesign/build.mjs').read_text(encoding='utf-8')
head=old[:old.index('// 01')]
head=head.replace("import {addChart} from './charts.mjs';", "import {addChart as originalChart} from '../presentation-redesign/charts.mjs';\nimport {addEdaChart,edaFacts} from './eda_charts.mjs';")
head=head.replace("path.join(dir,'source_content.json')", "path.join(dir,'../presentation-redesign/source_content.json')")
head=head.replace("path.join(dir,'audit/native_chart_data.json')", "path.join(dir,'../presentation-redesign/audit/native_chart_data.json')")
head=head.replace("path.join(dir,'cockpit.png')", "path.join(dir,'../presentation-redesign/cockpit.png')")
head=head.replace("const NN=[];", "const NN=[]; const footerNumbers=[]; const chartMeta=[];")
head=head.replace("source.slides[n-1].notes", "source.slides[n-1]?.notes")
start=head.index('function foot(')
end=head.index('function takeaway(',start)
head=head[:start]+'''function foot(s,n,dark=false){const col=dark?'#A5C8DF':C.muted;rule(s,64,650,1152,dark?'#31607C':C.line);if(!dark)image(s,logo,64,668,106,36,'StadtWerke Westhafen');txt(s,dark?'SWW / IHK-Projekt':'Gruppe 6 · Projektdaten 2024–2025',dark?64:195,673,900,23,16,col);footerNumbers.push(txt(s,String(n).padStart(2,'0'),1130,673,86,25,16,col,false,{alignment:'right'}));}
const kickers={13:'05 / Zielvariable',15:'05 / Zeitliche Validierung',16:'05 / Modellvergleich',17:'05 / Benchmark 2025',18:'05 / Erklärbarkeit',19:'06 / Kalibrierung',20:'06 / Prüfvolumen',21:'06 / Fallbeispiel 2025',32:'Anhang D / Fehlermetriken',33:'Anhang E / Zielvariable',34:'Anhang F / Sensitivität',35:'Anhang G / Modellkonfiguration',36:'Anhang H / Modellwahl',37:'Anhang I / Begriffe'};
function slide(n,kicker,title,sub='',dark=false){const s=p.slides.add();s.background.fill=dark?C.navy:'#FFFFFF';NN.push(s);kicker=kickers[NN.length]||kicker;if(n)note(s,n);if(kicker)txt(s,kicker.toUpperCase(),64,42,1110,24,17,dark?C.light:C.teal,true);if(title)txt(s,title,64,80,1152,106,43,dark?'#FFFFFF':C.navy,true);if(sub)txt(s,sub,64,183,1152,58,25,dark?'#BED6E8':C.muted);foot(s,NN.length,dark);return s;}
function page(kicker,title,sub='',notes='',dark=false){const s=slide(0,kicker,title,sub,dark);s.speakerNotes.textFrame.setText(notes+'\\n\\nGrundlagen: docs/IHK_Bericht_Gruppe_6_final.docx; docs/IHK_Group6-1.pdf; Datenstand 260916_verbrauch_bereinigt.csv; notebooks/13_modellierung_von_grund_auf_verstehen.ipynb. Details siehe Quellenfolie.');return s;}
function addChart(s,key,pos){const c=originalChart(s,key,pos);chartMeta.push({slide:NN.indexOf(s)+1,key,count:1});return c;}
function eda(s,key,pos){const c=addEdaChart(s,key,pos);chartMeta.push({slide:NN.indexOf(s)+1,key:'eda_'+key,count:c.length});return c;}
''' +head[end:]
blocks=re.split(r'// (\d\d) ·[^\n]*\n',old[old.index('// 01'):])
func='\nfunction ML(n){switch(n){\n'
for i in range(1,len(blocks),2):
    num=int(blocks[i]); body=blocks[i+1]
    if num==18: body=body[:body.index("await fs.mkdir")]
    func+=f'case {num}: '+body+'break;\n'
func+='default:throw new Error("ML block "+n);}}\n'
end='''
note(NN[17],8,'Gruppierte Permutation Importance auf dem Benchmark 2025 mit drei Wiederholungen. Vertragsleistung bleibt als fester Umrechnungsfaktor VLS → kWh unverändert. Wetter, Produktionsplan und Wartung müssen vor Monatsbeginn verfügbar sein. Einheitlicher Zahlenstand: Notebook 13. Der Bericht verwendet hier teilweise Notebook 12 mit fünf Wiederholungen und deshalb leicht andere Werte bei gleicher Rangfolge.');
footerNumbers.forEach((f,i)=>{f.text=String(i+1).padStart(2,'0')+' / '+NN.length;});
await fs.mkdir(path.join(dir,'render'),{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(dir,'candidate.pptx'));
await fs.writeFile(path.join(dir,'manifest.json'),JSON.stringify({slides:NN.length,charts:chartMeta,chartOwners:NN.map((s,i)=>s.charts.items.length?i+1:null).filter(Boolean),tableOwners:NN.map((s,i)=>s.tables.items.length?i+1:null).filter(Boolean)},null,2));
for(let i=0;i<NN.length;i++){
 const png=await p.export({slide:NN[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(dir,'render',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 const layout=await NN[i].export({format:'layout'});await fs.writeFile(path.join(dir,'render',`slide-${i+1}.json`),await layout.text());
 console.log('Rendered '+(i+1)+'/'+NN.length);
}
'''
(d/'build.mjs').write_text(head+func+(d/'story.mjs').read_text(encoding='utf-8')+end,encoding='utf-8')
print('Assembled build.mjs')
