import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';
import {GlobalFonts} from '@napi-rs/canvas';
import {addChart} from './charts.mjs';

const dir=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1'));
const root=path.resolve(dir,'../..');
const out=path.join(root,'docs/presentation');
const ds=path.join(root,'brand/design-system');
for(const weight of [400,500,600,700]) GlobalFonts.registerFromPath(path.join(ds,`dist/fonts/ibm-plex-sans-${weight}.ttf`),'IBM Plex Sans');
for(const weight of [400,500,600]) GlobalFonts.registerFromPath(path.join(ds,`dist/fonts/geist-mono-${weight}.ttf`),'Geist Mono');
const {FontLibrary}=await import(pathToFileURL(path.join(dir,'node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.js')).href);
FontLibrary.use('IBM Plex Sans',[400,500,600,700].map(w=>path.join(ds,`dist/fonts/ibm-plex-sans-${w}.ttf`)));
FontLibrary.use('Geist Mono',[400,500,600].map(w=>path.join(ds,`dist/fonts/geist-mono-${w}.ttf`)));
const source=JSON.parse(await fs.readFile(path.join(dir,'source_content.json'),'utf8'));
const data=JSON.parse(await fs.readFile(path.join(dir,'audit/native_chart_data.json'),'utf8'));
const logo=await fs.readFile(path.join(ds,'assets/logo-sww-wordmark.png'));
const full=await fs.readFile(path.join(ds,'assets/logo-sww-full.png'));

const C={navy:'#063659',ink:'#141A21',muted:'#4E5A68',teal:'#0080A0',cyan:'#0090C8',pale:'#E6F3F6',line:'#D6DFE7',gray:'#F1F4F7',amber:'#A86505',red:'#B3261E',light:'#99D7E5'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
p.theme.colorScheme={name:'StadtWerke Westhafen',themeColors:{accent1:'#084878',accent2:'#0090C8',accent3:'#0080A0',accent4:'#A86505',accent5:'#B3261E',accent6:'#8C98A6',bg1:'#FFFFFF',bg2:'#F1F4F7',tx1:'#141A21',tx2:'#4E5A68',dk1:'#141A21',dk2:'#063659',lt1:'#FFFFFF',lt2:'#F1F4F7',hlink:'#0080A0',folHlink:'#084878'}};
const NN=[];
let seq=0;
function box(s,x,y,w,h,fill,stroke='none',radius=0){return s.shapes.add({name:`block-${++seq}`,geometry:radius?'roundRect':'rect',borderRadius:radius,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:stroke==='none'?0:1}})}
function txt(s,t,x,y,w,h,size=28,color=C.ink,bold=false,extra={}){const a=box(s,x,y,w,h,'none');a.text=t;a.text.style={typeface:'IBM Plex Sans',fontSize:size,color,bold,autoFit:'none',wrap:'square',verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0},...extra};return a;}
function mono(s,t,x,y,w,h,size=62,color=C.teal){return txt(s,t,x,y,w,h,size,color,true,{typeface:'Geist Mono'});}
function rule(s,x,y,w,color=C.line,h=1){box(s,x,y,w,h,color);}
function image(s,blob,x,y,w,h,alt){s.images.add({blob,contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function note(s,n,extra=''){const replacement={7:'Das Diagramm zeigt den mittleren RMSE je Modell über drei Zeit-Folds. Random Forest gewinnt im Mittel mit 13.272 kWh. Gegenüber der linearen Regression beträgt der Vorteil rund 2,7 %. Die vollständigen Fold-Werte stehen unten in diesen Notizen, die RF-Einzelfolds im Anhang. Im dritten Fold ist die lineare Regression besser.',11:'Die Monatsbalken zeigen die Verteilung der 114 q99-Prüfhinweise über das Jahr 2025. Das entspricht durchschnittlich 9,5 Hinweisen pro Monat und 1,36 % der bewertbaren Zähler-Monate. Die 2024 kalibrierte Grenze bleibt unverändert. Die Abweichungen sind Arbeitsaufträge zur Prüfung, keine bestätigten Diagnosen.',17:'Die Balken zeigen die drei RF-Fold-Ergebnisse. Fold 2 erzielt den kleinsten RMSE. Die Zeiträume unterscheiden sich, daher lässt sich der Unterschied nicht allein auf die Trainingsmenge zurückführen. Die Tabelle dokumentiert die gewählten Hyperparameter.'};s.speakerNotes.textFrame.setText((replacement[n]||(source.slides[(n>=5&&n<=12?n-1:n)-1].notes||[]).filter(Boolean).join('\n\n'))+'\n\n'+extra+'\n\nQuelle: notebooks/13_modellierung_von_grund_auf_verstehen.ipynb. Datenabgleich: brand/design-system/ui_kits/energie-cockpit/anomaly-data.js. Benchmark: 01–12/2025, Kalibrierung: 11–12/2024.');}
function foot(s,n,dark=false,label='ML-Modellierung · Notebook 13'){const col=dark?'#A5C8DF':C.muted;rule(s,64,650,1152,dark?'#31607C':C.line);if(!dark) image(s,logo,64,668,106,36,'StadtWerke Westhafen');txt(s,dark?'SWW  /  ML-Modellierung':label,dark?64:195,673,dark?900:930,23,16,col);txt(s,String(n).padStart(2,'0')+' / 18',1130,673,86,25,16,col,false,{alignment:'right'});}
function slide(n,kicker,title,sub='',dark=false){const s=p.slides.add();s.background.fill=dark?C.navy:'#FFFFFF';NN.push(s);note(s,n);if(kicker)txt(s,kicker.toUpperCase(),64,42,1110,24,17,dark?C.light:C.teal,true);if(title)txt(s,title,64,80,1152,106,43,dark?'#FFFFFF':C.navy,true);if(sub)txt(s,sub,64,183,1152,58,25,dark?'#BED6E8':C.muted);foot(s,n,dark,n>13?'ML-Vertiefung · Notebook 13':'ML-Modellierung · Notebook 13');return s;}
function takeaway(s,t,y=590,dark=false){rule(s,64,y,56,dark?C.light:C.teal,4);txt(s,t,142,y-7,1074,53,25,dark?'#FFFFFF':C.navy,true);}
function kpi(s,val,label,x,y,w=330,dark=false,unit=''){mono(s,val,x,y,w,80,64,dark?C.light:C.teal);txt(s,label,x,y+82,w,65,25,dark?'#FFFFFF':C.muted);if(unit)txt(s,unit,x,y+146,w,36,20,C.muted);}
function table(s,values,x,y,w,h,widths,size=25){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths});t.borders.assign({fill:C.line,width:1});for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){const cell=t.getCell(r,c);cell.fill=r===0?C.navy:r%2?C.gray:'#FFFFFF';cell.text.style={typeface:'IBM Plex Sans',fontSize:size,color:r===0?'#FFFFFF':C.ink,bold:r===0,verticalAlignment:'middle',insets:{top:9,bottom:9,left:14,right:10}};}return t;}

// 01 · Cover: original brand logo, strong editorial typography.
{
 const s=slide(1,'','','',true);image(s,full,1000,64,176,198,'Original SWW-Logo');
 txt(s,'MACHINE LEARNING  /  SWW',64,91,890,32,20,C.light,true);
 txt(s,'Energieverbräuche\nprognostizieren.\nAbweichungen prüfen.',64,190,1070,240,64,'#FFFFFF',true);
 txt(s,'Zielvariable, Modellwahl und kalibrierte Prüfhinweise',68,470,1110,54,28,'#BED6E8');
 rule(s,68,561,64,C.light,4);txt(s,'Das Modell priorisiert. Die Fachprüfung entscheidet.',156,548,1040,64,30,'#FFFFFF',true);
}
// 02 · Editable process diagram.
{
 const s=slide(2,'01  /  Aufgabe','Vom Prognosewert zum Prüfauftrag','Prognose und Prüfung greifen zu unterschiedlichen Zeitpunkten.');
 const steps=[['01','Prognose','Vor Monatsbeginn\nVerbrauch schätzen.'],['02','Istwert','Nach Monatsende\nMesswert übernehmen.'],['03','Residuum','Ist minus Prognose\nRichtung und Stärke.'],['04','Fachprüfung','Ursache und Relevanz\nmenschlich klären.']];
 steps.forEach(([num,title,body],i)=>{const x=64+i*291;mono(s,num,x,285,240,74,56,i===3?C.amber:C.teal);rule(s,x,370,258,i===3?C.amber:C.teal,4);txt(s,title,x,391,267,45,31,C.navy,true);txt(s,body,x,451,267,98,26,C.muted);});
 takeaway(s,'Schwelle überschritten = Prüfhinweis. Die Diagnose bleibt offen.');
}
// 03 · Normalisation, clear equal result rather than tiny cards.
{
 const s=slide(3,'01  /  Zielvariable','Volllaststunden machen Anschlüsse vergleichbar','VLS normalisieren auf die Vertragsleistung. Sie sind keine gemessene Laufzeit.');
 box(s,64,266,1152,79,C.navy);txt(s,'VLS-h = Verbrauch (kWh) ÷ Vertragsleistung (kW)',89,282,1102,52,34,'#FFFFFF',true);
 txt(s,'KLEINER ANSCHLUSS',64,385,500,30,18,C.teal,true);txt(s,'GROSSER ANSCHLUSS',675,385,510,30,18,C.teal,true);
 txt(s,'10.000 kWh ÷ 50 kW',64,427,520,48,34,C.navy);txt(s,'40.000 kWh ÷ 200 kW',675,427,537,48,34,C.navy);
 mono(s,'200 h',64,482,530,78,65);mono(s,'200 h',675,482,530,78,65);
 takeaway(s,'Zurück zur Verbrauchsprognose: Prognose-VLS × Vertragsleistung = kWh');
}
// 04 · Feature availability before the forecast, without future observations.
{
 const s=slide(4,'01  /  Merkmale','Nur vorab verfügbare Merkmale dürfen ins Modell','Neun Prädiktoren. Die Vertragsleistung dient separat zur VLS-Umrechnung.');
 const rows=[
  ['01','Vergangenheit','Vormonat und 3-Monats-Mittel in VLS'],
  ['02','Planung & Kalender','Monat, Arbeits-/Feiertage,\nProduktionsplan und geplante Wartung'],
  ['03','Wetterprognose','Heizgradtage als Prognose vor Monatsbeginn'],
  ['04','Stammdaten','Kundentyp des Zählers']
 ];
 rows.forEach(([n,t,b],i)=>{const y=255+i*77;txt(s,n,64,y,62,45,29,C.teal,true,{typeface:'Geist Mono'});txt(s,t,145,y,369,45,28,C.navy,true);txt(s,b,537,y,679,65,25,C.muted);rule(s,145,y+68,1071,C.line);});
 takeaway(s,'Keine Istwerte des Prognosemonats. Die Verfügbarkeit muss betrieblich gesichert sein.');
 s.speakerNotes.textFrame.setText('Quelle: Notebook 13, Zelle learn-feature-table; scripts/build_modeling_verstehen_notebook.py, Feature-Tabelle. Neun gelernte Prädiktoren: vormonat_vls, letzte_3_monate_vls, monat_idx, arbeitstage, feiertage_im_monat, produktionsplan_index, wartung_aktiv, heizgradtage, kundentyp. Vertragsleistung ist kein gelerntes Merkmal, sondern der separate Normierungs- und Rückrechnungsfaktor. Historienmerkmale dürfen nur bekannte frühere Monate desselben Zählers verwenden. Produktionsplan und Wartung müssen vor Monatsbeginn bekannt sein. Heizgradtage sind nur als zu diesem Zeitpunkt verfügbarer Wetterprognosewert zulässig; eine historische Forecast-Vintage ist hier nicht nachgewiesen. Der Einsatz benötigt deshalb eine Prüfung der tatsächlichen Verfügbarkeit. Istverbrauch, Ziel-VLS und nachträglich realisierte Wetterdaten desselben Monats dürfen nicht als vorab bekannte Eingaben behandelt werden. Keine produktive Verfügbarkeit behaupten.');
}
// 04 · Training intervals align exactly with complete calendar months.
{
 const s=slide(5,'02  /  Validierung','Die Zeitachse trennt Lernen und Bewerten','Modellwahl 2024. Schwellenkalibrierung Ende 2024. Benchmark 2025.');
 const x0=235,cw=64,y0=290; const months=['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];
 months.forEach((m,i)=>txt(s,m,x0+i*cw,y0-32,cw,28,20,C.muted,false,{alignment:'center'}));
 const rows=[['Fold 1',4,4,2],['Fold 2',6,6,2],['Fold 3',8,8,2]];
 rows.forEach(([l,len,start,vl],i)=>{const y=y0+i*64;txt(s,l,64,y+9,155,38,27,C.navy,true);box(s,x0,y,cw*len-4,46,C.navy);box(s,x0+cw*start,y,cw*vl-4,46,C.teal);txt(s,'Training',x0+12,y+9,cw*len-25,29,22,'#FFFFFF');txt(s,'Bewertung',x0+cw*start+8,y+9,cw*vl-17,30,22,'#FFFFFF');});
 txt(s,'Kalibrierung',64,491,172,38,25,C.amber,true);box(s,x0+10*cw,482,2*cw-4,46,'#FFF0D4');txt(s,'Nov–Dez',x0+10*cw+10,491,128,30,23,C.amber,true);
 txt(s,'2025',1065,258,151,30,23,C.navy,true,{alignment:'center'});box(s,1065,290,151,238,C.gray);txt(s,'Testjahr',1079,375,125,40,27,C.navy,true,{alignment:'center'});note(s,5,'Zeitleiste: Vollständige Monate Jan–Apr/Mai–Jun, Jan–Jun/Jul–Aug und Jan–Aug/Sep–Okt 2024. Kalibrierung Nov–Dez: n=1.397. Entwicklung: n=8.389. Benchmark: n=8.398. Keine zufällige Aufteilung.');
 takeaway(s,'Jeder Bewertungszeitraum liegt vollständig nach seinem Trainingszeitraum.');
}
// 05 · Model choice and native hyperparameter table.
{
 const s=slide(6,'02  /  Modellwahl','24 Fits für eine kontrollierte Modellwahl','Acht Einstellungen, drei Zeit-Folds. Auswahl nach dem mittleren CV-RMSE.');
 txt(s,'Lineare Regression',64,268,490,48,32,C.navy,true);txt(s,'Die nachvollziehbare Referenz\nfür zusätzliche Modellkomplexität.',64,323,500,90,27,C.muted);
 txt(s,'Random Forest',64,449,490,48,32,C.teal,true);txt(s,'Nichtlineare Muster und\nWechselwirkungen im Vergleich.',64,504,500,80,27,C.muted);
 table(s,[['Parameter','Suchraum'],['Baumtiefe','8 / unbegrenzt'],['Min. Fälle je Blatt','5 / 20'],['Merkmalsanteil','0,7 / 1,0']],620,270,596,242,[305,291],25);
 txt(s,'Gewählt: Tiefe 8, Blattgröße 5, Anteil 0,7',620,536,596,67,26,C.teal,true);note(s,6,'Suchraum: max_depth [8,None], min_samples_leaf [5,20], max_features [0.7,1.0], also 8 Konfigurationen × 3 Zeit-Folds = 24 Fits. n_estimators=300, random_state=42. 2025 beeinflusst keine Hyperparameterauswahl.');
}
// 06 · CV result.
{
 const s=slide(7,'03  /  Validierungsergebnis','Random Forest gewinnt im Mittel','RMSE über drei Zeit-Folds 2024. Ein kleinerer Fehler ist besser.');
 addChart(s,'cv',{left:54,top:246,width:855,height:323});
 kpi(s,'−2,7 %','gegenüber der\nlinearen Regression',950,275,270);
 txt(s,'13.272 kWh\nmittlerer CV-RMSE',950,472,266,84,26,C.navy,true);
 takeaway(s,'Der Vorsprung gilt im Mittel. Im dritten Fold liegt die lineare Regression vorn.');
 note(s,7,'Korrektur der ursprünglichen Formulierung: RF gewinnt nicht jeden Fold. RMSE-Foldwerte und Standardabweichungen: '+JSON.stringify(data.cv)+'. Die Standardabweichung zwischen Folds beschreibt keine Unsicherheit einer einzelnen Prognose.');
}
// 07 · Benchmark.
{
 const s=slide(8,'03  /  Benchmark 2025','15,9 % geringerer RMSE als die beste Baseline','Retrospektiv: einen Monat vorhersagen und anschließend mit dem Istwert vergleichen.');
 addChart(s,'benchmark',{left:54,top:246,width:855,height:323});
 kpi(s,'9.188','RMSE in kWh',950,275,270);mono(s,'3.725',950,446,265,69,51,C.navy);txt(s,'MAE in kWh',950,519,265,34,25,C.muted);
 txt(s,'RF, linear, 3-Monats-Mittel: n = 8.398. Vormonat: n = 8.388, zehn Vergleichswerte fehlen.',64,590,1152,47,22,C.muted);
 note(s,8,'Beste einfache Baseline: Bis-zu-3-Monats-Mittel. Relativer Vorteil berechnet als 1 − 9188.397030722987 / 10922.440645880763. Vergleichswerte: '+JSON.stringify(data.benchmark)+'. Verfügbarkeit der Eingangsmerkmale muss vor Monatsbeginn sichergestellt werden.');
}
// 08 · Importance.
{
 const s=slide(9,'03  /  Erklärbarkeit','Die Verbrauchshistorie trägt am stärksten','Zusätzlicher RMSE in kWh, wenn eine Informationsgruppe zufällig vertauscht wird.');
 addChart(s,'importance',{left:52,top:239,width:1164,height:341});
 takeaway(s,'Permutation Importance beschreibt Modellnutzen. Sie belegt keine Ursache.');
 note(s,9,'Gruppierte Permutation Importance auf Benchmark 2025. Drei Permutationswiederholungen aus Notebook 13. Bericht und Notebook 12 verwenden fünf Wiederholungen, deshalb zeigen sie leicht andere Werte bei gleicher Rangfolge. Vertragsleistung bleibt als fester Umrechnungsfaktor VLS → kWh unverändert. Wetterprognose steht für Heizgradtage, die im Betrieb nur als vorab verfügbarer Prognosewert verwendet werden dürfen. Produktionsplan und Wartung müssen vor Monatsbeginn bekannt sein.');
}
// 09 · Quantile calibration.
{
 const s=slide(10,'04  /  Kalibrierung','q99 setzt die Grenze für einen Prüfhinweis','1.397 absolute Out-of-Fold-Fehler aus November und Dezember 2024.');
 addChart(s,'rank',{left:54,top:249,width:836,height:319});
 kpi(s,'144,4','VLS-h\n99. Perzentil',940,278,276);
 txt(s,'14 von 1.397\nFehlern darüber',940,478,276,92,28,C.amber,true);
 takeaway(s,'q99 ist eine konservative Pilotgrenze. Sie liefert keine Defektwahrscheinlichkeit.');
 note(s,10,'Exakte Schwelle 144,3547 VLS-h. (1397−1) × 0,99 = 1382,04. Interpolation zwischen Rang 1.383 und 1.384. 1.383 Fehler liegen bis zur Grenze, 14 darüber.');
}
// 10 · Workload, native monthly chart replaces unreadable dense scatter.
{
 const s=slide(11,'04  /  Prüfvolumen','114 Hinweise im Benchmarkjahr 2025','Die Ende 2024 kalibrierte q99-Grenze bleibt unverändert.');
 kpi(s,'114','von 8.398 Zähler-Monaten',64,249,350);kpi(s,'1,36 %','Hinweisquote',479,249,350);kpi(s,'9,5','Hinweise pro Monat',894,249,322);
 addChart(s,'monthly',{left:60,top:424,width:1156,height:167});
 txt(s,'107 Zähler betroffen. 68 ungewöhnlich hohe und 46 ungewöhnlich niedrige Verbräuche.',64,606,1152,36,22,C.muted);
 note(s,11,'Die Monate 2025 sind anders verteilt als die Kalibrierung, daher beträgt die Hinweisquote 1,36 % und nicht exakt 1 %. Ein fehlender Hinweis ist ebenfalls keine bestätigte Unauffälligkeit. Monatliche Daten: '+JSON.stringify(data.monthly));
}
// 11 · Single case, readable timeline and direct comparison.
{
 const s=slide(12,'05  /  Fallbeispiel 2025','ZL-00147: August löst eine Prüfung aus','49 kW Vertragsleistung. Die q99-Grenze entspricht ±7.073,4 kWh.');
 addChart(s,'case',{left:50,top:260,width:817,height:318});
 rule(s,915,264,301,C.red,4);txt(s,'AUGUST 2025',915,282,301,28,19,C.red,true);mono(s,'+2,30',915,319,301,73,57,C.red);txt(s,'Schwellenfaktor\n+16.259,6 kWh Residuum',915,399,301,77,25,C.ink);
 rule(s,915,494,301,C.teal,3);txt(s,'SEPTEMBER: −0,68',915,509,301,35,25,C.teal,true);txt(s,'Innerhalb der Grenze',915,552,301,33,24,C.muted);
 txt(s,'Faktor = VLS-Residuum ÷ 144,3547. Ein Betrag ≥ 1 erzeugt einen Prüfhinweis.',64,605,1152,37,22,C.navy);
 note(s,12,'August: Ist 23.563,5 kWh, Prognose 7.303,9 kWh, Residuum +16.259,6 kWh = +331,8 VLS-h, Faktor +2,30. September: Ist 5.915,0 kWh, Prognose 10.739,7 kWh, Residuum −4.824,7 kWh = −98,5 VLS-h, Faktor −0,68.');
}
// 13 · A clear closing statement in the reference's navy style.
{
 const s=slide(13,'06  /  Fazit','Die Prognose liefert eine prüfbare Priorisierung','',true);
 kpi(s,'−15,9 %','RMSE gegenüber der\nbesten einfachen Baseline',64,269,345,true);kpi(s,'9,5','Prüfhinweise pro Monat\nim q99-Pilot',478,269,332,true);
 txt(s,'Labels\nfehlen',907,270,309,147,52,'#FFFFFF',true);txt(s,'Precision und Recall\nsind noch offen.',907,425,309,75,26,'#BED6E8');
 rule(s,64,540,1152,'#31607C');txt(s,'Nächster Schritt',64,563,300,42,28,C.light,true);txt(s,'Fälle fachlich prüfen und Labels sammeln.\nSpäter kann eine Klassifikation die Priorisierung ergänzen.',395,558,821,80,28,'#FFFFFF');
}
// 14 · Transparent didactic metric example.
{
 const s=slide(14,'Anhang A  /  Fehlermetriken','RMSE gewichtet große Fehler stärker','Beispiel: Fehlerbeträge A = [10, 10, 10, 10] kWh, B = [0, 0, 0, 40] kWh.');
 addChart(s,'metrics',{left:52,top:250,width:816,height:324});
 txt(s,'MAE',920,270,296,45,32,C.navy,true);txt(s,'10 kWh\nin beiden Beispielen',920,319,296,79,28,C.muted);
 txt(s,'RMSE',920,440,296,45,32,C.teal,true);txt(s,'10 versus 20 kWh\nEinzelpeak zählt stärker.',920,489,296,82,27,C.muted);
 takeaway(s,'Deshalb dient RMSE als Hauptmetrik. MAE ergänzt die mittlere Fehlergröße.');
}
// 15 · Target comparison.
{
 const s=slide(15,'Anhang B  /  Zielvariable','VLS verbessert diesen Modellvergleich','Gleicher Modelltyp: Random Forest. Bewertung in kWh auf dem Benchmark 2025.');
 addChart(s,'target',{left:52,top:256,width:822,height:316});
 kpi(s,'−6,2 %','RMSE durch die\nZielvariable VLS',935,295,281);
 takeaway(s,'Das Ergebnis gilt für diesen Datensatz. Es ist keine allgemeine Überlegenheit.');
}
// 16 · Decision threshold native evidence.
{
 const s=slide(16,'Anhang C  /  Sensitivität','Das Perzentil bestimmt den Prüfaufwand','Gleiche Prognosen, andere Grenze. Dafür wird das Modell nicht neu trainiert.');
 addChart(s,'threshold',{left:52,top:263,width:673,height:307});
 table(s,[['Grenze','VLS-h','Hinweise / Monat'],['q95','68,0','33,3'],['q97,5','82,4','21,3'],['q99','144,4','9,5'],['q99,5','196,3','5,8']],769,270,447,288,[99,107,241],23);
 takeaway(s,'Die passende Grenze braucht bekannte Prüfkapazität und bestätigte Labels.');
 note(s,16,'q99 ist eine dokumentierte Pilotannahme. q99,5 ergibt exakt 69/12 = 5,75 Hinweise pro Monat, gerundet 5,8. Weitere Werte: '+JSON.stringify(data.threshold_options));
}
// 17 · Fold details and native settings table.
{
 const s=slide(17,'Anhang D  /  Modellkonfiguration','Die Fold-Ergebnisse schwanken deutlich','Random-Forest-RMSE in kWh. Jeder Fold bewertet einen anderen Zeitraum.');
 addChart(s,'folds',{left:49,top:280,width:560,height:263});
 txt(s,'Mittel 13.272 kWh  ·  Standardabw. 3.843 kWh',64,559,550,40,22,C.muted);
 table(s,[['Parameter','Wert'],['max_depth','8'],['min_samples_leaf','5'],['max_features','0,7'],['n_estimators','300'],['random_state','42']],665,261,551,311,[364,187],24);
 txt(s,'Fold 2 erzielt den kleinsten Fehler. Mehr Training allein erklärt den Unterschied nicht.',64,608,1152,34,23,C.navy);
 note(s,17,'Korrigierte Rundung Fold 2: 8.223 kWh, exakter Wert 8223.484122161364. Konfiguration: Baumtiefe 8 begrenzt spezielle Regeln; mindestens 5 Fälle pro Blatt; Merkmalsanteil 0,7 fördert Unterschiede zwischen Bäumen; 300 Bäume stabilisieren das Ensemble; Seed 42 gewährleistet Reproduzierbarkeit.');
}
// 18 · Distinctions with readable, flat typographic hierarchy.
{
 const s=slide(18,'Anhang E  /  Begriffe','Prüfhinweise sind noch keine bestätigten Anomalien','Vier Begriffe beschreiben vier unterschiedliche Aussagen.');
 const rows=[['01','Statistischer Ausreißer','Ungewöhnlich in einer Vergleichsverteilung.'],['02','Modellabweichung','Ist und Prognose unterscheiden sich deutlich.'],['03','Prüfhinweis','Die q99-Grenze ist erreicht. Eine Prüfung folgt.'],['04','Bestätigte Anomalie','Die Fachprüfung liefert ein begründetes Label.']];
 rows.forEach(([n,t,b],i)=>{const y=267+i*69;txt(s,n,64,y,67,43,29,i===3?C.amber:C.teal,true,{typeface:'Geist Mono'});txt(s,t,153,y,405,45,28,C.navy,true);txt(s,b,566,y,650,45,27,C.muted);rule(s,153,y+54,1063,C.line);});
 txt(s,'Für Precision und Recall fehlen Labels. Stichproben ohne Hinweis helfen,\nübersehene Fälle zu erfassen.',64,568,1152,71,27,C.navy,true);
}

await fs.mkdir(path.join(dir,'render'),{recursive:true});
const candidate=path.join(dir,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
console.log('EXPORTED '+candidate);
await fs.writeFile(path.join(dir,'chart-owners.json'),JSON.stringify(NN.map((s,i)=>s.charts.items.length?i+1:null).filter(Boolean)));
for(let i=0;i<NN.length;i++){
 const png=await p.export({slide:NN[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(dir,'render',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 const layout=await NN[i].export({format:'layout'});await fs.writeFile(path.join(dir,'render',`slide-${i+1}.json`),await layout.text());
 console.log('Rendered '+(i+1));
}
console.log('DONE');
