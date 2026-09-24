from pathlib import Path
import json, re, zipfile, xml.etree.ElementTree as ET, posixpath

ROOT = Path(__file__).resolve().parents[3]
PPTX = ROOT / 'docs/presentation/Modellierung_Anomaliepruefung_IHK.pptx'
OUT = ROOT / 'tmp/presentation-redesign/source_content.json'
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'p':'http://schemas.openxmlformats.org/presentationml/2006/main', 'c':'http://schemas.openxmlformats.org/drawingml/2006/chart', 'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def texts(el):
    return [''.join(t.text or '' for t in p.findall('.//a:t', NS)) for p in el.findall('.//a:p', NS)]
def rels(z, part):
    name = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part)+'.rels')
    if name not in z.namelist(): return []
    return [{'id':e.get('Id'), 'type':e.get('Type').split('/')[-1], 'target':posixpath.normpath(posixpath.join(posixpath.dirname(part), e.get('Target'))).lstrip('/'), 'external':e.get('TargetMode') == 'External'} for e in ET.fromstring(z.read(name))]
with zipfile.ZipFile(PPTX) as z:
    prs=ET.fromstring(z.read('ppt/presentation.xml'))
    size=prs.find('p:sldSz',NS)
    result={'source':str(PPTX.relative_to(ROOT)), 'size_emu':size.attrib, 'slides':[], 'charts':[], 'media':[]}
    for part in sorted((p for p in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$',p)),key=lambda p:int(re.search(r'(\d+)\.xml',p).group(1))):
        el=ET.fromstring(z.read(part)); rr=rels(z,part)
        note=[r['target'] for r in rr if r['type']=='notesSlide']
        row={'number':int(re.search(r'(\d+)\.xml',part).group(1)), 'part':part,'texts':texts(el), 'notes':texts(ET.fromstring(z.read(note[0]))) if note else [], 'relationships':rr, 'shapes':[]}
        for shape in el.findall('.//p:spTree/*',NS):
            row['shapes'].append({'kind':shape.tag.split('}')[-1], 'texts':texts(shape)})
        result['slides'].append(row)
    for part in sorted(p for p in z.namelist() if re.match(r'ppt/charts/chart\d+\.xml$',p)):
        el=ET.fromstring(z.read(part)); series=[]
        for s in el.findall('.//c:ser',NS):
            series.append({'texts':[t.text for t in s.findall('.//c:v',NS)],'xml':ET.tostring(s,encoding='unicode')})
        result['charts'].append({'part':part,'series':series,'relationships':rels(z,part)})
    for part in sorted(p for p in z.namelist() if p.startswith('ppt/media/')):
        result['media'].append({'part':part, 'bytes':z.getinfo(part).file_size, 'slides':[s['number'] for s in result['slides'] if part in [r['target'] for r in s['relationships']]]})
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for s in result['slides']:
    print('\nSLIDE',s['number'],'\n'+'\n'.join(s['texts'])+'\nNOTES\n'+'\n'.join(s['notes']))
print('\nCHARTS',len(result['charts']),'MEDIA',len(result['media']))
