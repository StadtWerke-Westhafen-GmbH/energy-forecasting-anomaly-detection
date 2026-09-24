import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';
import {GlobalFonts} from '@napi-rs/canvas';
import {addChart as originalChart} from '../presentation-redesign/charts.mjs';
import {addEdaChart,edaFacts} from './eda_charts.mjs';

const dir=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1'));
const root=path.resolve(dir,'../..');
const out=path.join(root,'docs/presentation');
const ds=path.join(root,'brand/design-system');
for(const weight of [400,500,600,700]) GlobalFonts.registerFromPath(path.join(ds,`dist/fonts/ibm-plex-sans-${weight}.ttf`),'IBM Plex Sans');
for(const weight of [400,500,600]) GlobalFonts.registerFromPath(path.join(ds,`dist/fonts/geist-mono-${weight}.ttf`),'Geist Mono');
const {FontLibrary}=await import(pathToFileURL(path.join(dir,'node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.js')).href);
FontLibrary.use('IBM Plex Sans',[400,500,600,700].map(w=>path.join(ds,`dist/fonts/ibm-plex-sans-${w}.ttf`)));
FontLibrary.use('Geist Mono',[400,500,600].map(w=>path.join(ds,`dist/fonts/geist-mono-${w}.ttf`)));
const source=JSON.parse(await fs.readFile(path.join(dir,'../presentation-redesign/source_content.json'),'utf8'));
const data=JSON.parse(await fs.readFile(path.join(dir,'../presentation-redesign/audit/native_chart_data.json'),'utf8'));
const logo=await fs.readFile(path.join(ds,'assets/logo-sww-wordmark.png'));
const full=await fs.readFile(path.join(ds,'assets/logo-sww-full.png'));
const cockpit=await fs.readFile(path.join(dir,'../presentation-redesign/cockpit.png'));
const C={navy:'#063659',ink:'#141A21',muted:'#4E5A68',teal:'#0080A0',cyan:'#0090C8',pale:'#E6F3F6',line:'#D6DFE7',gray:'#F1F4F7',amber:'#A86505',red:'#B3261E',light:'#99D7E5'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
p.theme.colorScheme={name:'StadtWerke Westhafen',themeColors:{accent1:'#084878',accent2:'#0090C8',accent3:'#0080A0',accent4:'#A86505',accent5:'#B3261E',accent6:'#8C98A6',bg1:'#FFFFFF',bg2:'#F1F4F7',tx1:'#141A21',tx2:'#4E5A68',dk1:'#141A21',dk2:'#063659',lt1:'#FFFFFF',lt2:'#F1F4F7',hlink:'#0080A0',folHlink:'#084878'}};
const NN=[]; const footerNumbers=[]; const chartMeta=[];
let seq=0;
function box(s,x,y,w,h,fill,stroke='none',radius=0){return s.shapes.add({name:`block-${++seq}`,geometry:radius?'roundRect':'rect',borderRadius:radius,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:stroke==='none'?0:1}})}
function txt(s,t,x,y,w,h,size=28,color=C.ink,bold=false,extra={}){const a=box(s,x,y,w,h,'none');a.text=t;a.text.style={typeface:'IBM Plex Sans',fontSize:size,color,bold,autoFit:'none',wrap:'square',verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0},...extra};return a;}
function mono(s,t,x,y,w,h,size=62,color=C.teal){return txt(s,t,x,y,w,h,size,color,true,{typeface:'Geist Mono'});}
function rule(s,x,y,w,color=C.line,h=1){box(s,x,y,w,h,color);}
function image(s,blob,x,y,w,h,alt){s.images.add({blob,contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function note(s,n,extra=''){const replacement={6:'Das Diagramm zeigt den mittleren RMSE je Modell über drei Zeit-Folds. Random Forest gewinnt im Mittel mit 13.272 kWh. Gegenüber der linearen Regression beträgt der Vorteil rund 2,7 %. Die vollständigen Fold-Werte stehen unten in diesen Notizen, die RF-Einzelfolds im Anhang. Im dritten Fold ist die lineare Regression besser.',10:'Die Monatsbalken zeigen die Verteilung der 114 q99-Prüfhinweise über das Jahr 2025. Das entspricht durchschnittlich 9,5 Hinweisen pro Monat und 1,36 % der bewertbaren Zähler-Monate. Die 2024 kalibrierte Grenze bleibt unverändert. Die Abweichungen sind Arbeitsaufträge zur Prüfung, keine bestätigten Diagnosen.',17:'Die Balken zeigen die drei RF-Fold-Ergebnisse. Fold 2 erzielt den kleinsten RMSE. Die Zeiträume unterscheiden sich, daher lässt sich der Unterschied nicht allein auf die Trainingsmenge zurückführen. Die Tabelle dokumentiert die gewählten Hyperparameter.'};s.speakerNotes.textFrame.setText((replacement[n]||(source.slides[n-1]?.notes||[]).filter(Boolean).join('\n\n'))+'\n\n'+extra+'\n\nQuelle: notebooks/13_modellierung_von_grund_auf_verstehen.ipynb. Datenabgleich: brand/design-system/ui_kits/energie-cockpit/anomaly-data.js. Benchmark: 01–12/2025, Kalibrierung: 11–12/2024.');}
function foot(s,n,dark=false){const col=dark?'#A5C8DF':C.muted;rule(s,64,650,1152,dark?'#31607C':C.line);if(!dark)image(s,logo,64,668,106,36,'StadtWerke Westhafen');txt(s,dark?'SWW / IHK-Projekt':'Gruppe 6 · Projektdaten 2024–2025',dark?64:195,673,900,23,16,col);footerNumbers.push(txt(s,String(n).padStart(2,'0'),1130,673,86,25,16,col,false,{alignment:'right'}));}
const kickers={13:'05 / Zielvariable',15:'05 / Zeitliche Validierung',16:'05 / Modellvergleich',17:'05 / Benchmark 2025',18:'05 / Erklärbarkeit',19:'06 / Kalibrierung',20:'06 / Prüfvolumen',21:'06 / Fallbeispiel 2025',32:'Anhang D / Fehlermetriken',33:'Anhang E / Zielvariable',34:'Anhang F / Sensitivität',35:'Anhang G / Modellkonfiguration',36:'Anhang H / Modellwahl',37:'Anhang I / Begriffe'};
function slide(n,kicker,title,sub='',dark=false){const s=p.slides.add();s.background.fill=dark?C.navy:'#FFFFFF';NN.push(s);kicker=kickers[NN.length]||kicker;if(n)note(s,n);if(kicker)txt(s,kicker.toUpperCase(),64,42,1110,24,17,dark?C.light:C.teal,true);if(title)txt(s,title,64,80,1152,106,43,dark?'#FFFFFF':C.navy,true);if(sub)txt(s,sub,64,183,1152,58,25,dark?'#BED6E8':C.muted);foot(s,NN.length,dark);return s;}
function page(kicker,title,sub='',notes='',dark=false){const s=slide(0,kicker,title,sub,dark);s.speakerNotes.textFrame.setText(notes+'\n\nGrundlagen: docs/IHK_Bericht_Gruppe_6_final.docx; docs/IHK_Group6-1.pdf; Datenstand 260916_verbrauch_bereinigt.csv; notebooks/13_modellierung_von_grund_auf_verstehen.ipynb. Details siehe Quellenfolie.');return s;}
function addChart(s,key,pos){const c=originalChart(s,key,pos);chartMeta.push({slide:NN.indexOf(s)+1,key,count:1});return c;}
function eda(s,key,pos){const c=addEdaChart(s,key,pos);chartMeta.push({slide:NN.indexOf(s)+1,key:'eda_'+key,count:c.length});return c;}
function takeaway(s,t,y=590,dark=false){rule(s,64,y,56,dark?C.light:C.teal,4);txt(s,t,142,y-7,1074,53,25,dark?'#FFFFFF':C.navy,true);}
function kpi(s,val,label,x,y,w=330,dark=false,unit=''){mono(s,val,x,y,w,80,64,dark?C.light:C.teal);txt(s,label,x,y+82,w,65,25,dark?'#FFFFFF':C.muted);if(unit)txt(s,unit,x,y+146,w,36,20,C.muted);}
function table(s,values,x,y,w,h,widths,size=25){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths});t.borders.assign({fill:C.line,width:1});for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){const cell=t.getCell(r,c);cell.fill=r===0?C.navy:r%2?C.gray:'#FFFFFF';cell.text.style={typeface:'IBM Plex Sans',fontSize:size,color:r===0?'#FFFFFF':C.ink,bold:r===0,verticalAlignment:'middle',insets:{top:9,bottom:9,left:14,right:10}};}return t;}


function ML(n){switch(n){
case 1: {
 const s=slide(1,'','','',true);image(s,full,1000,64,176,198,'Original SWW-Logo');
 txt(s,'IHK-PROJEKT  /  MODELLIERUNG',64,91,890,32,20,C.light,true);
 txt(s,'Energieverbräuche\nprognostizieren.\nAbweichungen prüfen.',64,190,1070,240,64,'#FFFFFF',true);
 txt(s,'Modeling, Kalibrierung und der Weg zur Fachprüfung',68,470,1110,54,28,'#BED6E8');
 rule(s,68,561,64,C.light,4);txt(s,'Das Modell priorisiert. Die Fachprüfung entscheidet.',156,548,1040,64,30,'#FFFFFF',true);
}
break;
case 2: {
 const s=slide(2,'01  /  Aufgabe','Vom Prognosewert zum Prüfauftrag','Prognose und Prüfung greifen zu unterschiedlichen Zeitpunkten.');
 const steps=[['01','Prognose','Vor Monatsbeginn\nVerbrauch schätzen.'],['02','Istwert','Nach Monatsende\nMesswert übernehmen.'],['03','Residuum','Ist minus Prognose\nRichtung und Stärke.'],['04','Fachprüfung','Ursache und Relevanz\nmenschlich klären.']];
 steps.forEach(([num,title,body],i)=>{const x=64+i*291;mono(s,num,x,285,240,74,56,i===3?C.amber:C.teal);rule(s,x,370,258,i===3?C.amber:C.teal,4);txt(s,title,x,391,267,45,31,C.navy,true);txt(s,body,x,451,267,98,26,C.muted);});
 takeaway(s,'Schwelle überschritten = Prüfhinweis. Die Diagnose bleibt offen.');
}
break;
case 3: {
 const s=slide(3,'01  /  Zielvariable','Volllaststunden machen Anschlüsse vergleichbar','VLS normalisieren auf die Vertragsleistung. Sie sind keine gemessene Laufzeit.');
 box(s,64,266,1152,79,C.navy);txt(s,'VLS-h = Verbrauch (kWh) ÷ Vertragsleistung (kW)',89,282,1102,52,34,'#FFFFFF',true);
 txt(s,'KLEINER ANSCHLUSS',64,385,500,30,18,C.teal,true);txt(s,'GROSSER ANSCHLUSS',675,385,510,30,18,C.teal,true);
 txt(s,'10.000 kWh ÷ 50 kW',64,427,520,48,34,C.navy);txt(s,'40.000 kWh ÷ 200 kW',675,427,537,48,34,C.navy);
 mono(s,'200 h',64,482,530,78,65);mono(s,'200 h',675,482,530,78,65);
 takeaway(s,'Zurück zur Verbrauchsprognose: Prognose-VLS × Vertragsleistung = kWh');
}
break;
case 4: {
 const s=slide(4,'02  /  Validierung','Die Zeitachse trennt Lernen und Bewerten','Modellwahl 2024. Schwellenkalibrierung Ende 2024. Benchmark 2025.');
 const x0=235,cw=64,y0=290; const months=['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];
 months.forEach((m,i)=>txt(s,m,x0+i*cw,y0-32,cw,28,20,C.muted,false,{alignment:'center'}));
 const rows=[['Fold 1',4,4,2],['Fold 2',6,6,2],['Fold 3',8,8,2]];
 rows.forEach(([l,len,start,vl],i)=>{const y=y0+i*64;txt(s,l,64,y+9,155,38,27,C.navy,true);box(s,x0,y,cw*len-4,46,C.navy);box(s,x0+cw*start,y,cw*vl-4,46,C.teal);txt(s,'Training',x0+12,y+9,cw*len-25,29,22,'#FFFFFF');txt(s,'Bewertung',x0+cw*start+8,y+9,cw*vl-17,30,22,'#FFFFFF');});
 txt(s,'Kalibrierung',64,491,172,38,25,C.amber,true);box(s,x0+10*cw,482,2*cw-4,46,'#FFF0D4');txt(s,'Nov–Dez',x0+10*cw+10,491,128,30,23,C.amber,true);
 txt(s,'2025',1065,258,151,30,23,C.navy,true,{alignment:'center'});box(s,1065,290,151,238,C.gray);txt(s,'Testjahr',1079,375,125,40,27,C.navy,true,{alignment:'center'});note(s,4,'Zeitleiste: Vollständige Monate Jan–Apr/Mai–Jun, Jan–Jun/Jul–Aug und Jan–Aug/Sep–Okt 2024. Kalibrierung Nov–Dez: n=1.397. Entwicklung: n=8.389. Benchmark: n=8.398. Keine zufällige Aufteilung.');
 takeaway(s,'Jeder Bewertungszeitraum liegt vollständig nach seinem Trainingszeitraum.');
}
break;
case 5: {
 const s=slide(5,'02  /  Modellwahl','24 Fits für eine kontrollierte Modellwahl','Acht Einstellungen, drei Zeit-Folds. Auswahl nach dem mittleren CV-RMSE.');
 txt(s,'Lineare Regression',64,268,490,48,32,C.navy,true);txt(s,'Die nachvollziehbare Referenz\nfür zusätzliche Modellkomplexität.',64,323,500,90,27,C.muted);
 txt(s,'Random Forest',64,449,490,48,32,C.teal,true);txt(s,'Nichtlineare Muster und\nWechselwirkungen im Vergleich.',64,504,500,80,27,C.muted);
 table(s,[['Parameter','Suchraum'],['Baumtiefe','8 / unbegrenzt'],['Min. Fälle je Blatt','5 / 20'],['Merkmalsanteil','0,7 / 1,0']],620,270,596,242,[305,291],25);
 txt(s,'Gewählt: Tiefe 8, Blattgröße 5, Anteil 0,7',620,536,596,67,26,C.teal,true);note(s,5,'Suchraum: max_depth [8,None], min_samples_leaf [5,20], max_features [0.7,1.0], also 8 Konfigurationen × 3 Zeit-Folds = 24 Fits. n_estimators=300, random_state=42. 2025 beeinflusst keine Hyperparameterauswahl.');
}
break;
case 6: {
 const s=slide(6,'03  /  Validierungsergebnis','Random Forest gewinnt im Mittel','RMSE über drei Zeit-Folds 2024. Ein kleinerer Fehler ist besser.');
 addChart(s,'cv',{left:54,top:246,width:855,height:323});
 kpi(s,'−2,7 %','gegenüber der\nlinearen Regression',950,275,270);
 txt(s,'13.272 kWh\nmittlerer CV-RMSE',950,472,266,84,26,C.navy,true);
 takeaway(s,'Der Vorsprung gilt im Mittel. Im dritten Fold liegt die lineare Regression vorn.');
 note(s,6,'Korrektur der ursprünglichen Formulierung: RF gewinnt nicht jeden Fold. RMSE-Foldwerte und Standardabweichungen: '+JSON.stringify(data.cv)+'. Die Standardabweichung zwischen Folds beschreibt keine Unsicherheit einer einzelnen Prognose.');
}
break;
case 7: {
 const s=slide(7,'03  /  Benchmark 2025','15,9 % geringerer RMSE als die beste Baseline','Retrospektiv: einen Monat vorhersagen und anschließend mit dem Istwert vergleichen.');
 addChart(s,'benchmark',{left:54,top:246,width:855,height:323});
 kpi(s,'9.188','RMSE in kWh',950,275,270);mono(s,'3.725',950,446,265,69,51,C.navy);txt(s,'MAE in kWh',950,519,265,34,25,C.muted);
 txt(s,'RF, linear, 3-Monats-Mittel: n = 8.398. Vormonat: n = 8.388, zehn Vergleichswerte fehlen.',64,590,1152,47,22,C.muted);
 note(s,7,'Beste einfache Baseline: Bis-zu-3-Monats-Mittel. Relativer Vorteil berechnet als 1 − 9188.397030722987 / 10922.440645880763. Vergleichswerte: '+JSON.stringify(data.benchmark)+'. Verfügbarkeit der Eingangsmerkmale muss vor Monatsbeginn sichergestellt werden.');
}
break;
case 8: {
 const s=slide(8,'03  /  Erklärbarkeit','Die Verbrauchshistorie trägt am stärksten','Zusätzlicher RMSE in kWh, wenn eine Informationsgruppe zufällig vertauscht wird.');
 addChart(s,'importance',{left:52,top:239,width:1164,height:341});
 takeaway(s,'Permutation Importance beschreibt Modellnutzen. Sie belegt keine Ursache.');
 note(s,8,'Gruppierte Permutation Importance auf Benchmark 2025. Vertragsleistung bleibt als fester Umrechnungsfaktor VLS → kWh unverändert. Wetterprognose steht für Heizgradtage, die im Betrieb nur als vorab verfügbarer Prognosewert verwendet werden dürfen. Produktionsplan und Wartung müssen vor Monatsbeginn bekannt sein.');
}
break;
case 9: {
 const s=slide(9,'04  /  Kalibrierung','q99 setzt die Grenze für einen Prüfhinweis','1.397 absolute Out-of-Fold-Fehler aus November und Dezember 2024.');
 addChart(s,'rank',{left:54,top:249,width:836,height:319});
 kpi(s,'144,4','VLS-h\n99. Perzentil',940,278,276);
 txt(s,'14 von 1.397\nFehlern darüber',940,478,276,92,28,C.amber,true);
 takeaway(s,'q99 ist eine konservative Pilotgrenze. Sie liefert keine Defektwahrscheinlichkeit.');
 note(s,9,'Exakte Schwelle 144,3547 VLS-h. (1397−1) × 0,99 = 1382,04. Interpolation zwischen Rang 1.383 und 1.384. 1.383 Fehler liegen bis zur Grenze, 14 darüber.');
}
break;
case 10: {
 const s=slide(10,'04  /  Prüfvolumen','114 Hinweise im Benchmarkjahr 2025','Die Ende 2024 kalibrierte q99-Grenze bleibt unverändert.');
 kpi(s,'114','von 8.398 Zähler-Monaten',64,249,350);kpi(s,'1,36 %','Hinweisquote',479,249,350);kpi(s,'9,5','Hinweise pro Monat',894,249,322);
 addChart(s,'monthly',{left:60,top:424,width:1156,height:167});
 txt(s,'107 Zähler betroffen. 68 ungewöhnlich hohe und 46 ungewöhnlich niedrige Verbräuche.',64,606,1152,36,22,C.muted);
 note(s,10,'Die Monate 2025 sind anders verteilt als die Kalibrierung, daher beträgt die Hinweisquote 1,36 % und nicht exakt 1 %. Ein fehlender Hinweis ist ebenfalls keine bestätigte Unauffälligkeit. Monatliche Daten: '+JSON.stringify(data.monthly));
}
break;
case 11: {
 const s=slide(11,'05  /  Fallbeispiel 2025','ZL-00147: August löst eine Prüfung aus','49 kW Vertragsleistung. Die q99-Grenze entspricht ±7.073,4 kWh.');
 addChart(s,'case',{left:50,top:260,width:817,height:318});
 rule(s,915,264,301,C.red,4);txt(s,'AUGUST 2025',915,282,301,28,19,C.red,true);mono(s,'+2,30',915,319,301,73,57,C.red);txt(s,'Schwellenfaktor\n+16.259,6 kWh Residuum',915,399,301,77,25,C.ink);
 rule(s,915,494,301,C.teal,3);txt(s,'SEPTEMBER: −0,68',915,509,301,35,25,C.teal,true);txt(s,'Innerhalb der Grenze',915,552,301,33,24,C.muted);
 txt(s,'Faktor = VLS-Residuum ÷ 144,3547. Ein Betrag ≥ 1 erzeugt einen Prüfhinweis.',64,605,1152,37,22,C.navy);
 note(s,11,'August: Ist 23.563,5 kWh, Prognose 7.303,9 kWh, Residuum +16.259,6 kWh = +331,8 VLS-h, Faktor +2,30. September: Ist 5.915,0 kWh, Prognose 10.739,7 kWh, Residuum −4.824,7 kWh = −98,5 VLS-h, Faktor −0,68.');
}
break;
case 12: {
 const s=slide(12,'05  /  Live-Demo','In zwei Minuten zum dokumentierten Prüffall','Lokale Demo mit retrospektiven Projektdaten. Keine Live-Anbindung.');
 image(s,cockpit,64,264,735,355,'Anomalieprüfung 2025 im lokalen SWW Energie-Cockpit');
 const steps=[['00:00','Schwelle und Umfang'],['00:20','2 hohe + 2 niedrige Fälle'],['00:40','Fall öffnen'],['01:10','Kontext prüfen'],['01:35','Entscheidung festhalten'],['01:55','Label als Lernsignal']];
 steps.forEach(([time,label],i)=>{const y=265+i*48;txt(s,time,838,y,90,37,23,C.teal,true,{typeface:'Geist Mono'});txt(s,label,949,y,267,42,24,C.navy);});
 const link=txt(s,'Live-Demo im Browser öffnen',838,579,378,47,25,C.teal,true);link.text.get('Live-Demo im Browser öffnen').link={uri:'http://127.0.0.1:4173/design-system/ui_kits/energie-cockpit/index.html?screen=anomalien',isExternal:true};
}
break;
case 13: {
 const s=slide(13,'06  /  Fazit','Die Prognose liefert eine prüfbare Priorisierung','',true);
 kpi(s,'−15,9 %','RMSE gegenüber der\nbesten einfachen Baseline',64,269,345,true);kpi(s,'9,5','Prüfhinweise pro Monat\nim q99-Pilot',478,269,332,true);
 txt(s,'Labels\nfehlen',907,270,309,147,52,'#FFFFFF',true);txt(s,'Precision und Recall\nsind noch offen.',907,425,309,75,26,'#BED6E8');
 rule(s,64,540,1152,'#31607C');txt(s,'Nächster Schritt',64,563,300,42,28,C.light,true);txt(s,'Fälle fachlich prüfen und Labels sammeln.\nSpäter kann eine Klassifikation die Priorisierung ergänzen.',395,558,821,80,28,'#FFFFFF');
}
break;
case 14: {
 const s=slide(14,'Anhang A  /  Fehlermetriken','RMSE gewichtet große Fehler stärker','Beispiel: Fehlerbeträge A = [10, 10, 10, 10] kWh, B = [0, 0, 0, 40] kWh.');
 addChart(s,'metrics',{left:52,top:250,width:816,height:324});
 txt(s,'MAE',920,270,296,45,32,C.navy,true);txt(s,'10 kWh\nin beiden Beispielen',920,319,296,79,28,C.muted);
 txt(s,'RMSE',920,440,296,45,32,C.teal,true);txt(s,'10 versus 20 kWh\nEinzelpeak zählt stärker.',920,489,296,82,27,C.muted);
 takeaway(s,'Deshalb dient RMSE als Hauptmetrik. MAE ergänzt die mittlere Fehlergröße.');
}
break;
case 15: {
 const s=slide(15,'Anhang B  /  Zielvariable','VLS verbessert diesen Modellvergleich','Gleicher Modelltyp: Random Forest. Bewertung in kWh auf dem Benchmark 2025.');
 addChart(s,'target',{left:52,top:256,width:822,height:316});
 kpi(s,'−6,2 %','RMSE durch die\nZielvariable VLS',935,295,281);
 takeaway(s,'Das Ergebnis gilt für diesen Datensatz. Es ist keine allgemeine Überlegenheit.');
}
break;
case 16: {
 const s=slide(16,'Anhang C  /  Sensitivität','Das Perzentil bestimmt den Prüfaufwand','Gleiche Prognosen, andere Grenze. Dafür wird das Modell nicht neu trainiert.');
 addChart(s,'threshold',{left:52,top:263,width:673,height:307});
 table(s,[['Grenze','VLS-h','Hinweise / Monat'],['q95','68,0','33,3'],['q97,5','82,4','21,3'],['q99','144,4','9,5'],['q99,5','196,3','5,8']],769,270,447,288,[99,107,241],23);
 takeaway(s,'Die passende Grenze braucht bekannte Prüfkapazität und bestätigte Labels.');
 note(s,16,'q99 ist eine dokumentierte Pilotannahme. q99,5 ergibt exakt 69/12 = 5,75 Hinweise pro Monat, gerundet 5,8. Weitere Werte: '+JSON.stringify(data.threshold_options));
}
break;
case 17: {
 const s=slide(17,'Anhang D  /  Modellkonfiguration','Die Fold-Ergebnisse schwanken deutlich','Random-Forest-RMSE in kWh. Jeder Fold bewertet einen anderen Zeitraum.');
 addChart(s,'folds',{left:49,top:280,width:560,height:263});
 txt(s,'Mittel 13.272 kWh  ·  Standardabw. 3.843 kWh',64,559,550,40,22,C.muted);
 table(s,[['Parameter','Wert'],['max_depth','8'],['min_samples_leaf','5'],['max_features','0,7'],['n_estimators','300'],['random_state','42']],665,261,551,311,[364,187],24);
 txt(s,'Fold 2 erzielt den kleinsten Fehler. Mehr Training allein erklärt den Unterschied nicht.',64,608,1152,34,23,C.navy);
 note(s,17,'Korrigierte Rundung Fold 2: 8.223 kWh, exakter Wert 8223.484122161364. Konfiguration: Baumtiefe 8 begrenzt spezielle Regeln; mindestens 5 Fälle pro Blatt; Merkmalsanteil 0,7 fördert Unterschiede zwischen Bäumen; 300 Bäume stabilisieren das Ensemble; Seed 42 gewährleistet Reproduzierbarkeit.');
}
break;
case 18: {
 const s=slide(18,'Anhang E  /  Begriffe','Prüfhinweise sind noch keine bestätigten Anomalien','Vier Begriffe beschreiben vier unterschiedliche Aussagen.');
 const rows=[['01','Statistischer Ausreißer','Ungewöhnlich in einer Vergleichsverteilung.'],['02','Modellabweichung','Ist und Prognose unterscheiden sich deutlich.'],['03','Prüfhinweis','Die q99-Grenze ist erreicht. Eine Prüfung folgt.'],['04','Bestätigte Anomalie','Die Fachprüfung liefert ein begründetes Label.']];
 rows.forEach(([n,t,b],i)=>{const y=267+i*69;txt(s,n,64,y,67,43,29,i===3?C.amber:C.teal,true,{typeface:'Geist Mono'});txt(s,t,153,y,405,45,28,C.navy,true);txt(s,b,566,y,650,45,27,C.muted);rule(s,153,y+54,1063,C.line);});
 txt(s,'Für Precision und Recall fehlen Labels. Stichproben ohne Hinweis helfen,\nübersehene Fälle zu erfassen.',64,568,1152,71,27,C.navy,true);
}

break;
default:throw new Error("ML block "+n);}}
// Main presentation: 30 minutes; demo: 15 minutes. Further slides are backup.
{
 const s=page('','','','Wir zeigen, wie wir den Folgemonatsverbrauch je Zähler prognostizieren und anschließend große Abweichungen zur menschlichen Prüfung vorlegen. Die Präsentation verbindet die bereinigte Datenbasis, die Modellentscheidung und den geplanten betrieblichen Ablauf. Unsere Ergebnisse stammen aus dem bereitgestellten Fallprojekt und einem retrospektiven Benchmark; sie belegen noch keinen produktiven Einsatz.\nUnsere Gruppe besteht aus Iana Kraievska, Patrick Olmo Hederer und Kiko Ramon Lukas.\nQuellen: Projektauftrag IHK_Group6-1.pdf und Abschlussbericht, Kapitel 1 und 3.',true);
 image(s,full,1000,64,176,198,'Original SWW-Logo');txt(s,'STADTWERKE WESTHAFEN / GRUPPE 6',64,92,900,32,20,C.light,true);
 txt(s,'Energie besser planen.\nAbweichungen\ngezielt prüfen.',64,191,1080,246,64,'#FFFFFF',true);
 txt(s,'Von verlässlichen Daten zur prüfbaren Entscheidung',68,474,1135,46,30,'#BED6E8');
 rule(s,68,562,64,C.light,4);txt(s,'Iana Kraievska · Patrick Olmo Hederer · Kiko Ramon Lukas',156,550,1060,70,25,'#FFFFFF');
}
{
 const s=page('Orientierung','Der Weg vom Geschäftsproblem zur Entscheidung','30 Minuten Projektvortrag · 15 Minuten Live-Demo · anschließend Fachgespräch','Wir beginnen mit dem Geschäftsproblem und der Datenbasis. Danach erklären wir die Analyse, die Modellwahl und die Prüfregel. Zum Schluss zeigen wir, wie ein Pilot den betrieblichen Nutzen messen könnte. Anschließend führen wir gemeinsam durch die Live-Demo.\nIana erläutert Datenmanagement und Datenqualität. Patrick übernimmt die explorative Analyse und Visualisierung. Kiko verantwortet den ML Canvas, Modellierung und Evaluation. Die Übergaben orientieren sich an diesen Fachgebieten. Detailformeln und zusätzliche Vergleiche stehen im Anhang und werden nur bei Bedarf gezeigt.\nFür die Generalprobe sind 30 Minuten Projektvortrag und 15 Minuten Demo vorgesehen. Grundlage ist die bereitgestellte IHK-Präsentationsvorlage beziehungsweise die Learning Journey zur Prüfungspräsentation.');
 const rows=[['01','Auftrag & Daten','Ausgangslage, Qualität und Muster','8 Min.'],['02','Modell & Prüfung','Validierung, Ergebnis und Prüfhinweise','14 Min.'],['03','Pilot & Nutzen','Grenzen, Umsetzung und Fazit','8 Min.'],['04','Live-Demo','Datenweg und dokumentierter Prüffall','15 Min.']];
 rows.forEach(([n,t,b,time],i)=>{const y=265+i*76;mono(s,n,64,y,77,45,31);txt(s,t,169,y,370,43,30,C.navy,true);txt(s,b,550,y+2,490,53,25,C.muted);txt(s,time,1080,y+2,136,38,25,C.teal,true,{alignment:'right'});rule(s,169,y+61,1047);});
}
{
 const s=page('01 / Ausgangslage','Zwei Entscheidungen brauchen bessere Daten','SWW versorgt 700 gewerbliche, industrielle und kommunale Anschlüsse.','Der Projektauftrag beschreibt StadtWerke Westhafen als Energieversorger im Hamburger Hafengebiet. Die Organisation versorgt 700 gewerbliche, industrielle und kommunale Großkunden. Für die Beschaffung muss sie den Bedarf im kommenden Monat abschätzen. Bisher stützt sich diese Planung stark auf manuelle Fortschreibungen. Ungünstige Abweichungen können kurzfristige Käufe oder Verkäufe am Spotmarkt erforderlich machen.\nDaneben werden ungewöhnliche Verbräuche häufig erst beim Quartalsabschluss bemerkt. Unser Ansatz soll solche Fälle nach jedem Monatsabschluss zur Prüfung vorlegen. Stefan Lechtenberg vertritt die Energiebeschaffung, Anke Bürger das Netzmanagement und Henrik Maaß die Datenanalyse. Eine tatsächliche Kostensenkung haben wir im Projekt noch nicht gemessen.\nQuellen: Projektauftrag, Abschnitte 1 bis 3; Abschlussbericht, Kapitel 1 und Abschnitt 3.4.');
 txt(s,'BESCHAFFUNG',64,276,520,30,19,C.teal,true);txt(s,'Was wird nächsten\nMonat benötigt?',64,324,530,100,38,C.navy,true);txt(s,'Manuelle Fortschreibung erschwert\neine konsistente Planung.',64,462,533,95,28,C.muted);
 rule(s,626,268,1,C.line,294);txt(s,'NETZ & ABRECHNUNG',680,276,536,30,19,C.teal,true);txt(s,'Welche Abweichung\nmuss geprüft werden?',680,324,536,100,38,C.navy,true);txt(s,'Auffälligkeiten werden teilweise\nerst quartalsweise sichtbar.',680,462,536,95,28,C.muted);
 takeaway(s,'Ziel: monatlich prognostizieren und ungewöhnliche Fälle gezielt prüfen.');
}
{
 const s=page('01 / Projektziel','Der Erfolg muss überprüfbar sein','Der Prototyp verbindet eine Prognose mit einem dokumentierten Prüfprozess.','Wir beurteilen den Prototyp auf drei Ebenen. Erstens muss die Datenbasis reproduzierbar sein: Einheiten, Schlüssel und Historie müssen stimmen. Zweitens muss die Prognose auf zeitlich späteren Monaten besser abschneiden als eine einfache Vergleichsregel. Drittens muss verständlich sein, warum ein Zähler-Monat einen Prüfhinweis erhält.\nAls Hauptmetrik verwenden wir den RMSE in kWh. Der MAE ergänzt die mittlere Fehlergröße; R² dient bei Bedarf als weitere Einordnung. Bisher messen wir Prognosefehler und Hinweisvolumen. Prüfzeiten, bestätigte Ursachen und finanzielle Wirkung müssen wir erst in einem Pilotbetrieb erfassen. Der Prototyp besitzt keine produktive Anbindung und entscheidet nicht über Abrechnungen.\nQuelle: Abschlussbericht, Abschnitte 1.4, 3.2 und 4.3 bis 4.4.');
 const cols=[['01','Verlässliche Basis','Einheiten, Schlüssel und\nHistorie reproduzierbar\naufbereiten.'],['02','Messbare Prognose','Gegen einfache Baselines\nauf zeitlich späteren\nMonaten bewerten.'],['03','Prüfbarer Hinweis','Abweichung und Grenze\nsichtbar machen;\nEntscheidung festhalten.']];
 cols.forEach(([n,t,b],i)=>{let x=64+i*394;mono(s,n,x,269,330,73,58);rule(s,x,361,345,C.teal,4);txt(s,t,x,388,350,47,30,C.navy,true);txt(s,b,x,449,350,119,28,C.muted);});
 takeaway(s,'Gemessen: Prognosefehler und Hinweisvolumen. Betriebsnutzen folgt im Pilot.');
}
{
 const s=page('01 / Zusammenarbeit','Drei Schwerpunkte – ein gemeinsamer Datenweg','Die Beiträge bleiben sichtbar; Übergaben werden über gemeinsame Ergebnisse geprüft.','Unsere Verantwortungen verliefen über alle Arbeitsphasen hinweg. Iana war für Datenmanagement und Datenqualität zuständig, Patrick für explorative Analyse und Visualisierung und Kiko für den ML Canvas, Machine Learning und Evaluation. Übergaben und fachliche Entscheidungen haben wir gemeinsam abgestimmt.\nIm ersten Sprint entstand die gemeinsame Datenbasis. Im zweiten Sprint begründeten EDA und Canvas die Zielgröße und die verfügbaren Merkmale. Im dritten Sprint folgten Modellwahl und Kalibrierung. Eine wichtige Anpassung war, die gelieferte Verbrauchshistorie je Zähler neu aus der Vergangenheit aufzubauen.\nUnsere persönlichen Lernpunkte unterscheiden sich: Iana betont die fachliche Bedeutung von Bereinigungsregeln, Patrick die Trennung von Korrelation und Ursache, Kiko die zeitliche Validierung und die Vermeidung von Data Leakage.\nQuelle: Abschlussbericht, Abschnitte 3.1, 3.3, 3.5 und 3.6.');
 const a=[['Iana Kraievska','Datenqualität','1 / Grundlage','Typen, Einheiten,\nLücken und Regeln'],['Patrick Olmo Hederer','Analyse & Visualisierung','2 / Verständnis','Muster, Vergleiche\nund Visualisierung'],['Kiko Ramon Lukas','Modell & Evaluation','3 / Umsetzung','Zeit-Folds, Benchmark\nund Prüfgrenze']];
 a.forEach(([name,role,sprint,body],i)=>{const x=64+i*394;txt(s,sprint.toUpperCase(),x,275,351,31,19,C.teal,true);rule(s,x,322,345,C.teal,4);txt(s,name,x,354,352,80,31,C.navy,true);txt(s,role,x,432,350,64,25,C.teal,true);txt(s,body,x,505,350,78,27,C.muted);});
 takeaway(s,'Gemeinsam: gleiche Kennzahlen, gleiche Begriffe und nachvollziehbare Quellen.');
}
{
 const s=page('02 / Datenbasis','700 Zähler über 24 vollständige Monate','Januar 2024 bis Dezember 2025 · eine Beobachtung pro Zähler und Monat','Die Rohdatei enthält 16.830 Zeilen und 16 Spalten. Darunter liegen 30 vollständig identische Dubletten. Nach ihrer Entfernung bleiben 16.800 eindeutige Zähler-Monate: 700 Zähler mit jeweils 24 Monaten von Januar 2024 bis Dezember 2025. Der gemeinsame Schlüssel besteht aus Zählerkennung und Monat.\nNeben Verbrauch und Vertragsleistung enthält die Datei Kunden-, Kalender-, Wetter-, Produktions- und Wartungsinformationen. Wir arbeiten mit diesem bereitgestellten Export, nicht mit einer bereits angeschlossenen produktiven Datenquelle. Drei rückblickend rekonstruierte Zielwerte gehören zur explorativen Gesamtsicht, werden aber aus der strikten ML-Bewertung ausgeschlossen.\nQuellen: data/raw/verbrauch.csv, data/raw/260916_verbrauch_bereinigt.csv; überprüfte Zählungen in audit/eda_data.json.');
 kpi(s,'700','Zähler',64,261,300);kpi(s,'24','Monate',477,261,300);kpi(s,'16.800','bereinigte Zeilen',890,261,326);
 rule(s,64,447,1152);txt(s,'Messung & Vertrag',64,481,345,43,30,C.navy,true);txt(s,'Verbrauch, Leistung, Typ',64,536,345,49,24,C.muted);
 txt(s,'Kalender & Wetter',477,481,345,43,30,C.navy,true);txt(s,'Arbeitstage, Feiertage,\nHeizgradtage',477,536,345,71,24,C.muted);
 txt(s,'Betrieblicher Kontext',890,481,326,43,29,C.navy,true);txt(s,'Produktionsplan, Wartung,\nVerbrauchshistorie',890,536,326,71,24,C.muted);
}
{
 const s=page('02 / Datenqualität','Bereinigung heißt auch: die Bedeutung erhalten','Zahlen beziehen sich auf 16.800 Zeilen nach Entfernung der 30 Dubletten.','Die Zahlen auf dieser Folie beziehen sich auf die 16.800 Zeilen nach Entfernung der Dubletten. 672 Verbrauchswerte stehen als MWh-Text in der Datei. Wir rechnen sie mit dem Faktor 1.000 in kWh um. Dreizehn Schreibweisen des Kundentyps werden auf die drei vorgesehenen Kategorien vereinheitlicht.\n504 fehlende Temperaturwerte und 672 fehlende Produktionsplanwerte sind unterschiedliche Befunde. Sie werden im Cleaning nicht pauschal ersetzt. Drei auffällige Zielwerte konnten wir rückblickend aus der dokumentierten Vormonatsinformation der Folgezeile rekonstruieren. Damit diese spätere Information die Modellbewertung nicht verbessert, schließen wir die drei Fälle dort aus.\nZusätzlich markieren wir 20 Fälle oberhalb von Vertragsleistung mal Monatsstunden. Diese Überschreitungen brauchen eine fachliche Prüfung. Die Vertragsleistung ist ohne Domänenbestätigung keine zwingende physikalische Obergrenze und ein solcher Fall daher kein bewiesener Messfehler.\nQuelle: audit/eda_data.json; Datenbereinigungsnotebook.');
 const rows=[['Einheiten','672 MWh-Texte → kWh','Einheit vereinheitlichen.'],['Kategorien','13 Schreibweisen → 3 Typen','Identität erhalten.'],['Fehlwerte','Temperatur: 504 · Plan: 672','Fehlgrund berücksichtigen.'],['Zielwerte','3 Rekonstruktionen','Für ML ausschließen.']];
 rows.forEach(([t,v,b],i)=>{const y=265+i*71;txt(s,t,64,y,212,43,29,C.navy,true);txt(s,v,305,y,514,43,29,C.teal,true);txt(s,b,861,y+2,355,50,25,C.muted);rule(s,305,y+56,911);});
 takeaway(s,'Plausibilitätsfälle markieren und fachlich klären – nicht pauschal löschen.');
}
{
 const s=page('02 / Reproduzierbarkeit','Ein Datenweg mit klar getrennten Auswertungen','Die explorative Sicht beschreibt das Portfolio. Der ML-Lauf schützt die Zeitlogik.','Der Datenweg beginnt mit dem CSV-Import und den Prüfungen von Schlüsseln, Datentypen und Einheiten. Auf der gemeinsamen bereinigten Basis trennen wir die explorative Gesamtsicht von den zeitlich zulässigen Daten für die Modellierung. Die Ergebnisse gelangen über einen geprüften JSON-Datenvertrag in das lokale Cockpit.\nFür die EDA bleiben alle 16.800 Monatswerte einschließlich markierter Fälle sichtbar. Für das ML-Training aus 2024 verwenden wir 8.389 Fälle: Von 8.400 Monatswerten entfallen zehn Plausibilitätsflags und ein rekonstruierter Zielwert. Der Benchmark 2025 enthält 8.398 Fälle, weil zwei rekonstruierte Ziele entfallen. Die zehn Plausibilitätsflags aus 2025 bleiben bewusst enthalten. Die Kalibrierung nutzt 1.397 Fälle aus November und Dezember 2024.\nDie gelieferte Drei-Monats-Statistik war für frühere Prognosezeitpunkte ungeeignet. Wir erzeugen die Historienmerkmale deshalb je Zähler ausschließlich aus vorangegangenen Monaten.\nQuellen: Notebook 13; audit/eda_data.json.');
 const steps=[['Rohdaten','16.830 Zeilen'],['Bereinigung','16.800 Zeilen'],['EDA','Portfolio verstehen'],['Modellierung','Historie neu bilden']];
 steps.forEach(([t,b],i)=>{let x=64+i*292;box(s,x,272,264,99,i===3?C.navy:C.gray);txt(s,t,x+15,286,234,36,29,i===3?'#FFFFFF':C.navy,true);txt(s,b,x+15,332,237,33,22,i===3?'#BED6E8':C.muted);if(i<3)txt(s,'→',x+267,302,29,41,27,C.teal,true);});
 txt(s,'EDA: alle 16.800 Monatswerte',64,416,542,43,31,C.navy,true);txt(s,'Markierungen bleiben als Kontext\nfür die fachliche Interpretation erhalten.',64,472,540,83,27,C.muted);
 txt(s,'ML: zeitlich zulässige Teilmengen',662,416,554,43,30,C.teal,true);txt(s,'8.389 Entwicklungsfälle in 2024\n8.398 Benchmarkfälle in 2025',662,472,554,83,28,C.muted);
 takeaway(s,'Was erst später bekannt wird, darf keine frühere Prognose verbessern.');
}
{
 const s=page('03 / Explorative Analyse','Das Monatsprofil wiederholt sich deutlich','Monatssummen in MWh · vollständige bereinigte Basis mit 700 Zählern','Die Linien zeigen die monatlichen Gesamtverbräuche des Portfolios in MWh. In beiden Jahren liegen Sommer und früher Herbst niedriger; der Jahresgang ähnelt sich deutlich. Der Gesamtverbrauch beträgt rund 211.568 MWh im Jahr 2024 und 208.691 MWh im Jahr 2025. Das entspricht einem Rückgang um etwa 1,4 Prozent.\nDie Korrelation der zwölf aggregierten Monatswerte beider Jahre beträgt 0,946. Sie beschreibt die Ähnlichkeit des Portfolioverlaufs, beweist aber keine Ursache. Die Grafik enthält alle 16.800 bereinigten Werte einschließlich der Plausibilitätsflags. Die historische EDA darf beide Jahre beschreiben; die spätere Hyperparameterauswahl verwendet ausschließlich 2024.\nAus diesem Verlauf nehmen wir die saisonale Lage und die bereits bekannte Verbrauchshistorie als plausible Modellinformationen mit.\nQuelle: audit/eda_data.json, charts.monthly.');
 eda(s,'monthly',{left:54,top:248,width:880,height:329});kpi(s,'−1,4 %','Jahresverbrauch\n2025 vs. 2024',963,285,253);
 takeaway(s,'Saison und Historie sind plausible Merkmale für die Folgemonatsprognose.');
}
{
 const s=page('03 / Portfolio','Industrie prägt den Verbrauch stärker als die Anzahl','Anteile nach Kundentyp · Zählerzahl und Verbrauch 2024–2025 im Vergleich','Von den 700 Zählern gehören 376 zum Gewerbe, 226 zur Industrie und 98 zum kommunalen Bereich. Die Industrie stellt damit rund 32,3 Prozent der Zähler, aber 68,5 Prozent des Verbrauchs über beide Jahre. Die beiden Balkenarten haben unterschiedliche Bezugsgrößen: Zählerzahl einerseits und gesamte Energiemenge andererseits.\nDie Anschlussgröße ist deshalb bei einem Vergleich der absoluten kWh wichtig. Wir normieren später über die Vertragsleistung. Dass eine Kundengruppe viel Energie verbraucht, macht den Kundentyp noch nicht automatisch zu einem starken zusätzlichen Modellmerkmal. Diesen Beitrag prüfen wir getrennt mit Permutation Importance.\nQuelle: audit/eda_data.json, charts.portfolio. Grundlage sind alle 16.800 bereinigten Monatswerte.');
 eda(s,'portfolio',{left:54,top:248,width:858,height:327});kpi(s,'68,5 %','des Verbrauchs\nentfallen auf Industrie',953,282,263);
 takeaway(s,'Absolute kWh unterscheiden sich stark. Die Anschlussgröße muss berücksichtigt werden.');
}
{
 const s=page('04 / ML Canvas · 1 von 2','Der Anwendungsfall beginnt bei der Entscheidung','Fünf Felder verbinden fachlichen Nutzen, Daten und erwartete Wirkung.','Der Canvas beginnt bei der späteren Entscheidung. Die Beschaffung braucht eine Folgemonatsprognose; das Netzmanagement braucht nach Eingang des Istwerts eine begründete Priorisierung auffälliger Fälle. Dafür verbinden wir Verbrauchsdaten mit Vertrags-, Kalender-, Wetter- und Planinformationen.\nUnsere Vorhersage ist eine kontinuierliche Größe: Vollaststunden je Zähler und Monat. Für die Anwender rechnen wir sie wieder in kWh zurück. Die anschließende Prüfregel gehört zum selben Prozess, ist aber keine zweite bereits trainierte Klassifikation.\nDie Wirkung möchten wir an Prognosefehlern, Prüfzeit und bestätigten Ursachen messen. Der bereits gemessene Prognosevorteil ist noch keine nachgewiesene finanzielle Einsparung.\nQuelle: Abschlussbericht, Kapitel 2 und Tabelle A1; Projektauftrag.');
 const rows=[['Mehrwert','Planbarere Beschaffung und monatliche Prüfung.'],['Datenquellen','Verbrauch, Vertrag, Kalender, Wetter und Betriebspläne.'],['Vorhersage','VLS je Zähler und Folgemonat; Rückrechnung in kWh.'],['Entscheidung','Beschaffung informieren und Fachprüfung priorisieren.'],['Auswirkung','Fehler, Prüfzeit und bestätigte Ursachen im Pilot messen.']];
 rows.forEach(([a,b],i)=>{let y=262+i*66;txt(s,a,64,y,305,44,28,C.teal,true);txt(s,b,390,y+1,826,52,27,C.navy);rule(s,390,y+53,826);});
}
{
 const s=page('04 / ML Canvas · 2 von 2','Der Betrieb legt die Modellregeln fest','Fünf weitere Felder machen Zeitpunkt, Bewertung und Pflege konkret.','Die zweite Hälfte des Canvas legt die methodischen und betrieblichen Regeln fest. Die Merkmale müssen zum Prognosezeitpunkt bekannt sein. Wir vergleichen eine lineare Regression und einen Random Forest mit einfachen Baselines. Die Bewertung folgt der Zeitachse.\nVor Monatsbeginn entsteht die Prognose. Erst nach Eingang des tatsächlichen Monatsverbrauchs können wir ein Residuum berechnen und einen Prüfhinweis erzeugen. Wetterdaten müssen dafür als vorher verfügbare Prognose und Produktions- beziehungsweise Wartungsinformationen als Plan vorliegen. Die tatsächliche Verfügbarkeitskette einer produktiven Anwendung ist noch nicht nachgewiesen.\nFür einen Pilot empfehlen wir monatliche Kontrolle von Fehlern, Datenlücken, Merkmalsverteilungen und Hinweisvolumen. Ein neues Training sollte auf einen belegten Bedarf und eine erneute Prüfung folgen.\nQuelle: Abschlussbericht, Kapitel 2, Abschnitt 4.2 und Abschnitt 4.4.3.');
 const rows=[['Merkmale','Vergangenheit und vorab verfügbare Kontextdaten.'],['Lernansatz','Regression: lineares Modell und Random Forest.'],['Überprüfung','Zeit-Folds, späterer Benchmark und einfache Baselines.'],['Zeitpunkt','Prognose vorher; Abweichungsprüfung nach dem Istwert.'],['Wartung','Fehler, Datenlücken, Drift und Hinweisvolumen verfolgen.']];
 rows.forEach(([a,b],i)=>{let y=262+i*66;txt(s,a,64,y,305,44,28,C.teal,true);txt(s,b,390,y+1,826,52,27,C.navy);rule(s,390,y+53,826);});
}
ML(3);
{
 const s=page('05 / Merkmale','Nur verfügbare Information darf ins Modell','Neun Eingangsmerkmale · acht numerische Felder und ein kategoriales Feld','Das Modell verwendet neun Prädiktoren: vormonat_vls, letzte_3_monate_vls, monat_idx, arbeitstage, feiertage_im_monat, heizgradtage, produktionsplan_index, wartung_aktiv und kundentyp. Die Vertragsleistung dient ausschließlich zur Normierung und Rückrechnung.\nDie beiden Historienmerkmale stammen aus früheren Monaten desselben Zählers. Kalenderinformationen sind vorab bekannt. Heizgradtage dürfen nur als Wetterprognose verwendet werden; Produktion und Wartung müssen geplante Werte sein. Im Pilot müssen diese vorab verfügbaren Versionen nachvollziehbar gespeichert werden. Historische Prognoseversionen sind im Projekt nicht gesondert nachgewiesen.\nFehlende numerische Merkmale behandelt die Pipeline mit einem Median und Fehlwertindikatoren, die sie nur aus dem jeweiligen Trainingsfold lernt. Den Kundentyp ergänzt sie bei Bedarf mit dem häufigsten Trainingswert und kodiert ihn anschließend mit One-Hot-Encoding. Das lineare Modell standardisiert zusätzlich numerische Werte. IDs, aktuelle Zielwerte, die redundante Roh-Temperatur und der für 2024 nicht verfügbare Vorjahreswert gehören nicht zum finalen Merkmalset.\nQuelle: Notebook 13, Zelle learn-feature-table und Modellpipeline.');
 txt(s,'AUS DER VERGANGENHEIT',64,269,529,31,19,C.teal,true);txt(s,'Vormonats-VLS\nBis-zu-3-Monats-Mittel',64,320,529,99,31,C.navy,true);txt(s,'Mit jedem Monat nur bereits\nbekannte Werte fortschreiben.',64,457,529,82,28,C.muted);
 rule(s,622,266,1,C.line,300);txt(s,'VOR MONATSBEGINN BENÖTIGT',678,269,538,31,19,C.teal,true);txt(s,'Monat, Arbeitstage, Feiertage\nWetterprognose, Produktionsplan\nWartung, Kundentyp',678,320,538,135,29,C.navy,true);txt(s,'Plan- und Prognoseversionen\nmüssen gespeichert werden.',678,484,538,82,27,C.muted);
 takeaway(s,'IDs und aktuelle Verbrauchswerte bleiben außerhalb der Eingangsmerkmale.');
}
ML(4);ML(6);ML(7);ML(8);ML(9);ML(10);ML(11);
{
 const s=page('06 / Fachlicher Prozess','Ein Hinweis wird erst durch Prüfung nützlich','Das Modell liefert Richtung, Größenordnung und Kontext für die nächste Handlung.','Ein Hinweis ist zunächst eine Aufforderung zur Prüfung. Wir beginnen bei der Messung: Stimmen Einheit, Zählerzuordnung und Datenübertragung? Danach prüfen wir den betrieblichen Kontext, insbesondere Produktion, geplante Wartung und besondere Ereignisse. Erst anschließend entscheidet der Fachbereich, ob und welche Maßnahme nötig ist.\nDie fachliche Einordnung sollte eine Begründung enthalten. Mögliche Ergebnisse sind eine bestätigte technische Auffälligkeit, ein Mess- oder Datenfehler, eine plausible Betriebsänderung oder ein zunächst unklarer Fall. Das sind vorgeschlagene Prüfkategorien, keine heute vorhandene Ground Truth.\nDamit wir später auch übersehene Fälle untersuchen können, sollten zusätzlich zufällig ausgewählte Monate ohne Hinweis geprüft werden. Dieser Ablauf ist ein Prozessvorschlag und noch kein gemessener Produktivprozess.\nQuellen: Abschlussbericht, Abschnitt 4.5 und Anhang E; Projektauftrag, Abschnitt 8.');
 const rows=[['01','Messung prüfen','Einheit, Zuordnung, Lücke und Übertragungsfehler.'],['02','Kontext verstehen','Produktion, Wartung und besondere Ereignisse.'],['03','Ursache klären','Fachbereich entscheidet über weitere Maßnahmen.'],['04','Ergebnis festhalten','Begründung und Label als Lernsignal speichern.']];
 rows.forEach(([n,t,b],i)=>{let y=269+i*73;mono(s,n,64,y,75,43,29);txt(s,t,159,y,359,44,29,C.navy,true);txt(s,b,549,y+2,667,53,26,C.muted);rule(s,159,y+58,1057);});
 takeaway(s,'Auch eine plausible Abweichung ist ein wertvolles dokumentiertes Ergebnis.');
}
{
 const s=page('06 / Grenzen & Verantwortung','Drei Grenzen bestimmen den nächsten Schritt','Modellqualität, Datenverfügbarkeit und menschliche Entscheidung gehören zusammen.','Drei Grenzen sind für die nächste Entscheidung wesentlich. Erstens fehlen bestätigte Anomalielabel. Precision und Recall können wir deshalb nicht belastbar ausweisen. Auch Fälle ohne Hinweis müssen stichprobenartig bewertet werden, damit wir mögliche übersehene Fälle sehen. Die Schwelle basiert außerdem nur auf November und Dezember 2024; ihre Übertragbarkeit auf andere Jahreszeiten ist noch zu prüfen.\nZweitens müssen Wetter-, Produktions- und Wartungsinformationen zum richtigen Zeitpunkt verfügbar sein. Die bereitgestellte Aufgabe setzt diese Verfügbarkeit voraus, ein produktiver Nachweis fehlt bislang.\nDrittens bleibt die Verantwortung beim Fachbereich. Für eine spätere Anbindung empfehlen wir begrenzte Zugriffsrechte, dokumentierte Entscheidungen und festgelegte Aufbewahrung. Zähler-IDs machen Daten nicht automatisch anonym. Fehler und Hinweisquoten sollten zusätzlich nach Kundentyp und Anschlussgröße geprüft werden. Eine validierte Fairnessbewertung oder eine Datenschutzfreigabe behaupten wir damit nicht.\nQuellen: Projektauftrag, Abschnitt 8; Abschlussbericht, Abschnitte 1.4 und 4.4.');
 const c=[['Qualität','Labels fehlen.\nWinterkalibrierung ist\neine Pilotannahme.'],['Verfügbarkeit','Plan- und Wetterwerte\nmüssen zum Prognose-\nzeitpunkt vorliegen.'],['Verantwortung','Zugriff begrenzen,\nEntscheidungen begründen,\nFachprüfung beibehalten.']];
 c.forEach(([t,b],i)=>{let x=64+i*394;rule(s,x,279,345,i===0?C.amber:C.teal,4);txt(s,t,x,321,350,47,33,C.navy,true);txt(s,b,x,399,350,142,28,C.muted);});
 takeaway(s,'Fehler und Hinweisquoten zusätzlich nach Kundentyp und Anschlussgröße prüfen.');
}
{
 const s=page('07 / Handlungsempfehlung','Ein Schattenpilot macht den Nutzen messbar','Ausgewählte Zähler laufen zunächst parallel zum bisherigen Prozess.','Wir empfehlen einen begrenzten Schattenpilot mit ausgewählten Zählern. Die neuen Prognosen und Hinweise laufen zunächst parallel zum bisherigen Prozess und lösen keine automatische Entscheidung aus. Vor dem Start müssen Datenversionen, Verantwortlichkeiten und verfügbare Prüfkapazität feststehen.\nIm Pilot vergleichen wir Modell und Baselines und erfassen Hinweisvolumen, Bearbeitungszeit sowie bestätigte Ursachen. Gemeinsam mit den Fachbereichen legen wir vorab fest, welche Qualität, welcher Aufwand und welche Datenabdeckung für eine Fortführung erforderlich sind.\nBei Drift, Datenänderungen oder Qualitätsverlust prüfen wir zuerst die Ursache. Ein neues Training oder eine veränderte Schwelle braucht anschließend eine erneute getrennte Validierung. Erst mit belegten Preis-, Zeit- und Ergebnisdaten lässt sich die wirtschaftliche Wirkung bewerten.\nQuelle: Abschlussbericht, Abschnitte 3.7 und 4.4.3.');
 const rows=[['Start vorbereiten','Datenversionen, Rollen und Prüfkapazität festlegen.'],['Parallel messen','Fehler, Prüfaufwand und Ursachen erfassen.'],['Gemeinsam bewerten','Qualität und Aufwand gegen vereinbarte Ziele prüfen.'],['Gezielt weiterführen','Erst bei belegtem Nutzen anbinden und erweitern.']];
 rows.forEach(([a,b],i)=>{let y=268+i*74;txt(s,String(i+1).padStart(2,'0'),64,y,68,43,30,C.teal,true,{typeface:'Geist Mono'});txt(s,a,165,y,368,45,30,C.navy,true);txt(s,b,561,y+1,655,55,27,C.muted);rule(s,165,y+59,1051);});
 takeaway(s,'Monatlich überwachen. Bei Veränderungen Ursachen prüfen und Modelle anpassen.');
}
{
 const s=page('07 / Fazit','Die Grundlage steht. Der Betriebsnachweis folgt.','','Drei Ergebnisse können wir belegen: eine reproduzierbare Grundlage mit 16.800 Zähler-Monaten, einen um 15,9 Prozent geringeren RMSE gegenüber der besten einfachen Baseline im Benchmark 2025 und durchschnittlich 9,5 Hinweise pro Monat beim q99-Szenario.\nDie Erkennungsqualität bestätigter Defekte sowie Zeit- und Euro-Einsparungen sind noch offen. Deshalb empfehlen wir einen menschlich begleiteten Pilotbetrieb und eine strukturierte Erfassung fachlicher Rückmeldungen. Mit genügend belastbaren Labels könnte später eine eigene Klassifikationsaufgabe die Priorisierung ergänzen. Sie müsste separat validiert werden.\nDie Prognose priorisiert die Prüfung; sie stellt keine Diagnose.\nQuellen: Abschlussbericht, Abschnitte 3.7 und 4.3 bis 4.4; Notebook 13 und Dashboard-Export.',true);
 kpi(s,'16.800','bereinigte\nZähler-Monate',64,265,346,true);kpi(s,'−15,9 %','RMSE gegenüber der\nbesten einfachen Baseline',476,265,347,true);kpi(s,'9,5','Prüfhinweise pro Monat\nim Benchmark 2025',893,265,323,true);
 rule(s,64,521,1152,'#31607C');txt(s,'Nächster Schritt',64,562,300,43,29,C.light,true);txt(s,'Parallelbetrieb starten, Fälle fachlich prüfen\nund Nutzen anhand echter Ergebnisse bewerten.',395,552,821,84,29,'#FFFFFF');
}
{
 const s=page('08 / Live-Demo','15 Minuten entlang des gesamten Datenwegs','Jeder Schritt zeigt ein Ergebnis und die Entscheidung dahinter.','In der Demo gehen wir den Datenweg gemeinsam durch: zwei Minuten Rohdaten, drei Minuten Bereinigung, drei Minuten EDA, vier Minuten Modellierung, zwei Minuten Cockpit und eine Minute Puffer für Rückfragen. Jede Person zeigt ihren eigenen Verantwortungsbereich und erklärt die wesentliche Entscheidung hinter dem Ergebnis.\nVor dem Termin öffnen wir Notebooks, Daten und das lokale Cockpit. Gespeicherte Notebook-Ergebnisse erlauben uns, den Ablauf ohne lange Wartezeit auf einen vollständigen Trainingslauf zu erklären. Falls eine Live-Ausführung nicht funktioniert, stehen diese Ergebnisse sowie die Diagramme und der folgende Screenshot als Fallback bereit. Bereits gespeicherte Ergebnisse kennzeichnen wir dabei klar.\nQuelle: bereitgestellte Präsentationsvorlage und Learning Journey zur 30-Minuten-Präsentation und 15-Minuten-Demo.');
 const rows=[['02 Min.','Rohdaten','Struktur und Qualitätsprobleme'],['03 Min.','Bereinigung','Einheit, Schlüssel und Fehlwertlogik'],['03 Min.','EDA','Saison, Kundentyp und Normalisierung'],['04 Min.','Modellierung','Zeit-Folds, Benchmark und q99'],['02 Min.','Cockpit','Fall prüfen und Ergebnis festhalten'],['01 Min.','Rückfragen','Offene Punkte gezielt aufnehmen']];
 rows.forEach(([time,t,b],i)=>{let y=261+i*57;txt(s,time,64,y,144,40,25,C.teal,true,{typeface:'Geist Mono'});txt(s,t,257,y,332,43,28,C.navy,true);txt(s,b,606,y+1,610,46,25,C.muted);});
}
{
 const s=page('08 / Cockpit','Vom Gesamtbild in den konkreten Prüffall','Lokale Demo mit retrospektiven Projektdaten · keine produktive Systemanbindung','Wir öffnen die lokale Anomalieansicht und prüfen zunächst den Zeitraum 2025 und die aktive q99-Schwelle. Danach zeigen wir die priorisierte Liste und wählen einen hohen sowie einen niedrigen Fall aus.\nBei ZL-00147 im August erklären wir Istwert, Prognose, Richtung und Schwellenfaktor. Anschließend prüfen wir den Kontext und zeigen, wie eine begründete fachliche Einordnung dokumentiert werden kann. Diese Rückmeldung wäre später die Grundlage für bestätigte Labels.\nDie Oberfläche verwendet den retrospektiven Projektexport und besitzt keine produktive Systemanbindung. Der Screenshot dient als Rückfallebene; für eine Interaktion öffnen wir das Cockpit im lokalen Browser.\nQuelle: brand/design-system/ui_kits/energie-cockpit und Abschlussbericht, Anhang E.');
 image(s,cockpit,64,265,763,354,'SWW Energie-Cockpit: Anomalieprüfung 2025');
 const steps=[['01','Umfang kontrollieren'],['02','Fall auswählen'],['03','Abweichung erklären'],['04','Kontext prüfen'],['05','Einordnung festhalten']];steps.forEach(([n,t],i)=>{let y=282+i*58;txt(s,n,875,y,54,37,23,C.teal,true,{typeface:'Geist Mono'});txt(s,t,946,y,270,50,25,C.navy);});
 const link=txt(s,'Lokales Cockpit öffnen →',875,579,341,43,24,C.teal,true);link.text.get('Lokales Cockpit öffnen →').link={uri:'http://127.0.0.1:4173/design-system/ui_kits/energie-cockpit/index.html?screen=anomalien',isExternal:true};
}
{
 const s=page('Fachgespräch','Vielen Dank.','','Vielen Dank. Wir freuen uns auf Ihre Fragen zu den Daten, der Modellentscheidung und der möglichen Umsetzung.\nFür das Fachgespräch können wir insbesondere erklären, warum wir zeitliche Folds statt eines Zufallssplits verwenden, weshalb VLS die Zielgröße bilden und wie wir zukünftige Information aus den Eingaben heraushalten. Weitere Fragen betreffen die Aussagekraft ohne bestätigte Labels und die Erfolgsmessung im Pilot.\nDie folgenden Folien enthalten Vertiefungen. Sie sind nicht Bestandteil des regulären 30-Minuten-Hauptvortrags.',true);
 txt(s,'Das Modell priorisiert.\nDie Fachprüfung entscheidet.',64,258,1152,151,54,'#FFFFFF',true);rule(s,64,464,96,C.light,4);txt(s,'Fragen zu Daten, Modell und Umsetzung',64,512,1152,61,33,'#BED6E8');
}
// Backup section: use selectively in the discussion.
{
 const s=page('Anhang A / Bereinigungsprotokoll','Formate und Einheiten nachvollziehbar korrigieren','Bezugsbasis: 16.800 Zeilen nach Deduplizierung, außer bei den Dubletten.','Die Detailtabelle verwendet eine einheitliche Bezugsbasis: 16.800 Zeilen nach Entfernung der Dubletten. Nur die Anzahl der 30 Dubletten bezieht sich auf die ursprünglichen 16.830 Rohzeilen.\nDadurch unterscheiden sich zwei Zählungen von der alten Vorlage. Dort stehen 505 abweichende Kundentyp-Schreibweisen und 11.316 nicht im ISO-Format angegebene Monate. Nach der Deduplizierung sind es 504 beziehungsweise 11.298. Auch die MWh-Texte werden auf der deduplizierten Basis gezählt; hier sind es 672. Die Befunde können sich in einer Zeile überschneiden und dürfen nicht zu einer Gesamtfehlerquote addiert werden.\nDie drei Zielwerte 0, −50 und −1.000 rekonstruieren wir rückblickend aus der dokumentierten Information der Folgezeile. Für die strikte ML-Bewertung schließen wir diese Fälle aus.\nQuellen: unveränderte Rohdatei, Datenbereinigungsnotebook und audit/eda_data.json, quality_findings.');
 table(s,[['Befund','Anzahl','Behandlung'],['Identische Dubletten','30 / 16.830','Entfernen; Schlüssel prüfen'],['Nicht-ISO-Monat','11.298','Ein Datum pro Monat'],['Kundentyp-Schreibweise','504','13 Varianten → 3 Typen'],['Verbrauch als MWh-Text','672','× 1.000 → kWh'],['Zielwerte 0 / −50 / −1.000','3','Rekonstruieren; aus ML ausschließen']],64,265,1152,312,[431,205,516],25);
 takeaway(s,'Jede Regel bleibt dokumentiert und reproduzierbar.');
}
{
 const s=page('Anhang B / Fehlwerte & Plausibilität','Fehlende Historie ist nicht automatisch ein Datenfehler','Bereinigte Basis vor Neuberechnung der ML-Historie · unterschiedliche Fehlgründe','Die Tabelle beschreibt die bereinigte Datenbasis vor der ML-Neuberechnung. Dort fehlen 700 Vormonatswerte am Beginn der Zeitreihen und 8.400 Vorjahreswerte für 2024, weil 2023 nicht zum Datensatz gehört. Nach dem Ausblenden der Plausibilitätsfälle und der Neuberechnung der Historie enthält die ML-Datei 719 fehlende Vormonatswerte und 8.410 fehlende Vorjahreswerte. Die Zahlen gehören also zu unterschiedlichen Verarbeitungsschritten.\nBesonders auffällig war das gelieferte Drei-Monats-Mittel: Schon im Januar 2024 waren 699 von 700 Werten gefüllt, obwohl die notwendige Vorhistorie im Projekt nicht prüfbar vorlag. Wir übernehmen diese Statistik nicht, sondern berechnen das Mittel je Zähler aus bis zu drei bekannten Vormonaten neu. Im Januar bleiben deshalb alle 700 Werte leer. In späteren Monaten verwenden wir nur die jeweils verfügbare gültige Historie. Die 504 Temperaturlücken werden nicht pauschal ergänzt; das finale Merkmalset verwendet Heizgradtage. Fehlende Produktionsplanwerte behandelt die Pipeline mit einem ausschließlich im Trainingsfold gelernten Median und einem Fehlwertindikator.\nDie 20 Fälle über Vertragsleistung mal Monatsstunden verteilen sich mit jeweils zehn auf die beiden Jahre. Ohne fachliche Bestätigung sind das Plausibilitätsflags, keine bewiesenen Messfehler. Die zehn Fälle aus 2024 bleiben außerhalb des Trainings, die zehn Fälle aus 2025 bewusst im Benchmark. Diese Markierung ist von den drei rekonstruierten Zielwerten zu unterscheiden.\nQuellen: audit/eda_data.json und Notebook 13.');
 table(s,[['Befund','Anzahl','Folgerung'],['Temperatur fehlt','504','Heizgradtage als Modellmerkmal'],['Produktionsplan fehlt','672','Im Trainingsfold imputieren'],['Vormonat fehlt','700','Start der Zeitreihe beachten'],['Vorjahr fehlt','8.400','2023 fehlt → Merkmal weglassen'],['Vertragsleistung überschritten','20','Markieren und fachlich prüfen']],64,265,1152,312,[480,161,511],25);
 takeaway(s,'Rekonstruierte Zielwerte und offene Plausibilitätsflags sind getrennte Kategorien.');
}
{
 const s=page('Anhang C / Anschlussgröße','Normalisierung reduziert den Größenunterschied','Links: Median in kWh · rechts: Median in VLS-h · unterschiedliche Skalen','Links sehen wir den Median der monatlichen kWh je Kundentyp. Rechts sehen wir den Median nach Division durch die jeweilige Vertragsleistung, also in VLS-Stunden. Die beiden Diagramme haben unterschiedliche Einheiten und Skalen.\nAuf Basis aller 16.800 bereinigten Werte beträgt das Verhältnis Industrie zu Gewerbe beim kWh-Median etwa 5,22. Bei den VLS-Medianen sinkt es auf etwa 1,085. Die normierten Mediane liegen bei rund 159,7 Stunden für Gewerbe, 173,2 für Industrie und 169,9 für Kommunal. Das zeigt den verringerten Größeneffekt, beweist aber für sich noch keinen Modellvorteil.\nDiese beschreibende Auswertung enthält auch die 20 Plausibilitätsflags. ältere EDA-Darstellungen verwenden teilweise eine um diese Fälle reduzierte Basis und können geringfügig andere Werte ergeben. VLS sind eine rechnerische Normierung und keine gemessene Betriebsdauer.\nQuelle: audit/eda_data.json, charts.normalization.');
 eda(s,'normalization',{left:54,top:252,width:1162,height:318});takeaway(s,'VLS helfen beim Vergleich. Unterschiede im Nutzungsverhalten bleiben relevant.');
}
ML(14);ML(15);ML(16);ML(17);ML(5);ML(18);
{
 const s=page('Anhang J / Aufwand & Nutzen','Ein Pilot braucht einen Messplan vor einer ROI-Zahl','Der Datensatz enthält weder Prozesskosten noch bestätigte finanzielle Einsparungen.','Für einen belastbaren ROI fehlen im Datensatz die Prozesskosten und bestätigte finanzielle Wirkungen. Die Tabelle ist deshalb ausschließlich ein transparentes Aufwandsszenario. Die durchschnittlichen 9,5 Hinweise pro Monat stammen aus dem Benchmark 2025. Zehn, zwanzig oder dreißig Minuten je Hinweis sind ausdrücklich angenommene Bearbeitungszeiten, keine Messwerte.\nDie reine Rechnung ergibt rund 1,6, 3,2 oder 4,8 Stunden pro Monat. Nicht enthalten sind Stichproben ohne Hinweis, Nachverfolgung, Infrastruktur, Integration, Modelltraining oder Wartung. Aus diesen Werten folgt keine Einsparung.\nIm Pilot müssen wir tatsächliche Bearbeitungszeiten und Folgeschritte erfassen, Ursachen bestätigen und Betriebs-, Integrations- sowie Pflegekosten bestimmen. Für die Beschaffungswirkung brauchen wir zusätzlich Mengenprognosen und reale Preise.\nQuellen: Hinweisvolumen aus Notebook 13 und Dashboard-Export; Zeitansätze als ausdrücklich gekennzeichnete Szenarioannahmen.');
 table(s,[['Annahme je Hinweis','Reine Prüfzeit / Monat'],['10 Minuten','rund 1,6 Stunden'],['20 Minuten','rund 3,2 Stunden'],['30 Minuten','rund 4,8 Stunden']],64,275,603,257,[321,282],26);
 txt(s,'9,5 Hinweise × angenommene Dauer',64,552,603,67,24,C.muted);txt(s,'Im Pilot erfassen',730,276,486,47,32,C.navy,true);txt(s,'Bearbeitungszeit und Folgeschritte\nBestätigte Ursachen und Maßnahmen\nBetriebs-, Integrations- und Pflegekosten\nWirkung auf reale Beschaffung',730,350,486,214,27,C.muted);
}
{
 const s=page('Anhang K / Quellen & Leselogik','Die Aussagen bleiben bis zur Quelle nachvollziehbar','Lokale Projektquellen · Quellenhinweise und Erläuterungen in den Foliennotizen','Unsere Aussagen bleiben den jeweiligen Projektquellen zugeordnet. Auftrag und Teamkontext stammen aus dem Fallbrief und Abschlussbericht. Die hier gezeigte EDA verwendet alle 16.800 bereinigten Zeilen; abweichende ältere EDA-Stände können auf einer gefilterten Basis mit 16.780 Zeilen beruhen.\nDie ML-Diagramme der beiden neuen Präsentationen verwenden einheitlich Notebook 13. Bei der gruppierten Permutation Importance nutzt dieses Notebook drei Wiederholungen. Der Bericht verwendet Notebook 12 mit fünf Wiederholungen und leicht anderen Zahlen; die Rangfolge der Informationsgruppen bleibt gleich. Die betreffenden Diagrammnotizen nennen diesen Unterschied ausdrücklich.\nDer Cockpit-Export dient zum Abgleich von Prognosen, Schwellen und Hinweiszahlen. Die Datumsangaben in Bericht und Vorlage sind widersprüchlich; ein aktueller Prüfungstermin ist deshalb nicht angegeben.\nQuellen und genaue Auswertungsdefinitionen sind in den Foliennotizen sowie in audit/project_facts.json und audit/eda_data.json dokumentiert.');
 const rows=[['Auftrag & Team','IHK_Group6-1.pdf · IHK_Bericht_Gruppe_6_final.docx'],['Daten & EDA','verbrauch.csv · 260916_verbrauch_bereinigt.csv'],['ML-Ergebnisse','13_modellierung_von_grund_auf_verstehen.ipynb'],['Cockpit-Abgleich','ui_kits/energie-cockpit/anomaly-data.js'],['Gestaltung','SWW Design System · Projekt-Präsentationstemplate']];
 rows.forEach(([a,b],i)=>{let y=266+i*66;txt(s,a,64,y,278,44,27,C.teal,true);txt(s,b,367,y+1,849,51,25,C.navy);rule(s,367,y+52,849);});
}

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
