from pathlib import Path
import re

base = Path(__file__).resolve().parent
source = base.parent / 'presentation-redesign' / 'build.mjs'
code = source.read_text(encoding='utf-8')
code = code.replace("const cockpit=await fs.readFile(path.join(dir,'cockpit.png'));", '')
code = code.replace("'SWW  /  IHK-Projekt'", "'SWW  /  ML-Modellierung'")
code = code.replace("'Notebook 13 · Projektergebnisse'", "'ML-Modellierung · Notebook 13'")
code = code.replace("'Vertiefung · Notebook 13'", "'ML-Vertiefung · Notebook 13'")
code = code.replace("'IHK-PROJEKT  /  MODELLIERUNG'", "'MACHINE LEARNING  /  SWW'")
code = code.replace("'Modeling, Kalibrierung und der Weg zur Fachprüfung'", "'Zielvariable, Modellwahl und kalibrierte Prüfhinweise'")
code = code.replace("source.slides[n-1].notes", "source.slides[(n>=5&&n<=12?n-1:n)-1].notes")
code = code.replace('replacement={6:', 'replacement={7:').replace(".',10:",".',11:")
blocks = re.split(r'(?=// \d{2} ·)', code)
header = blocks[0]
result = [header]
for block in blocks[1:]:
    number = int(block[3:5])
    if number == 12:
        continue
    if 4 <= number <= 11:
        block = re.sub(r'\bslide\('+str(number)+r',', 'slide('+str(number+1)+',', block)
        block = re.sub(r'\bnote\(s,'+str(number)+r',', 'note(s,'+str(number+1)+',', block)
    result.append(block)
    if number == 3:
        result.append('''// 04 · Feature availability before the forecast, without future observations.
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
'''.replace('Arbeits-/Feiertage,\nProduktionsplan','Arbeits-/Feiertage,\\nProduktionsplan'))
code = ''.join(result)
(base/'build.mjs').write_text(code, encoding='utf-8')

finalize=(base/'finalize.mjs').read_text(encoding='utf-8')
finalize=finalize.replace('Modellierung_Anomaliepruefung_IHK_SWW.pptx','ML_Modellierung_Anomaliepruefung_SWW.pptx')
finalize=finalize.replace('[5,16,17]','[6,16,17]').replace('[6,7,8,9,10,11,14,15,16,17]','[7,8,9,10,11,12,14,15,16,17]')
finalize=finalize.replace('final-v3.validation.json','ml-final.validation.json')
(base/'finalize.mjs').write_text(finalize,encoding='utf-8')
render=(base/'render_final.mjs').read_text(encoding='utf-8').replace('Modellierung_Anomaliepruefung_IHK_SWW.pptx','ML_Modellierung_Anomaliepruefung_SWW.pptx')
(base/'render_final.mjs').write_text(render,encoding='utf-8')
pdf=(base/'export_pdf.py').read_text(encoding='utf-8').replace('Modellierung_Anomaliepruefung_IHK_SWW.pdf','ML_Modellierung_Anomaliepruefung_SWW.pdf').replace('for page in (4, 7, 10, 18):','for page in (4, 8, 11, 18):')
pdf=pdf.replace('Modellierung und Anomalieprüfung | SWW | IHK-Projekt','Machine Learning: Modellierung und Anomalieprüfung | SWW')
(base/'export_pdf.py').write_text(pdf,encoding='utf-8')
prep=(base/'prepare_package.py').read_text(encoding='utf-8').replace("name=='ppt/slides/slide10.xml'", "name=='ppt/slides/slide11.xml'")
(base/'prepare_package.py').write_text(prep,encoding='utf-8')
print('Prepared independent ML18 builder with feature availability and without live demo.')
