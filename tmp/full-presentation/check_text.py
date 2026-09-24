from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import re,json,sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2]
issues=[]
for filename in ['ML_Modellierung_Anomaliepruefung_SWW.pptx','Gesamtpraesentation_IHK_SWW.pptx']:
    p=root/'docs/presentation'/filename
    if not p.exists():continue
    with ZipFile(p) as z:
        for n in z.namelist():
            if n.endswith('.xml') and re.match(r'ppt/(slides/slide\d+|notesSlides/notesSlide\d+)\.xml$',n):
                xml=etree.fromstring(z.read(n))
                text=' '.join(xml.xpath('//a:t/text()',namespaces={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}))
                text=re.sub(r'https?://\S+','',text)
                bad=re.findall(r'\w+\?\w+|\ufffd|\\n|\bundefined\b',text)
                if bad:issues.append({'file':filename,'part':n,'suspicious_tokens':bad[:20]})
print(json.dumps({'issues':issues},ensure_ascii=False,indent=2))
if issues:raise SystemExit(1)
