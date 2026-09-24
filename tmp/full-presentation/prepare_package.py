from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import json

d=Path(__file__).resolve().parent
target=d/'candidate.pptx'
manifest=json.loads((d/'manifest.json').read_text())
keys=[]
for item in manifest['charts']:
    keys.extend([item['key']]*item['count'])
with ZipFile(target) as z: parts={n:z.read(n) for n in z.namelist()}
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
for name,content in list(parts.items()):
    if '/charts/chart' in name and name.endswith('.xml'):
        xml=E.fromstring(content)
        for lang in xml.findall('c:lang',ns): lang.set('val','de-DE')
        for title in xml.findall('.//c:title',ns):
            if not ''.join(title.itertext()).strip(): title.getparent().remove(title)
        key=keys[int(Path(name).stem.removeprefix('chart'))-1]
        if key in ('cv','benchmark','importance'):
            vmax,step={'cv':(22000,5000),'benchmark':(17000,5000),'importance':(8500,2000)}[key]
            va=xml.find('.//c:valAx',ns);ca=xml.find('.//c:catAx',ns)
            for node in ca.findall('c:title',ns): ca.remove(node)
            scaling=va.find('c:scaling',ns)
            for tag,value in [('min',0),('max',vmax)]:
                old=scaling.find('c:'+tag,ns)
                if old is not None: scaling.remove(old)
                E.SubElement(scaling,'{'+ns['c']+'}'+tag,val=str(value))
            va.find('c:numFmt',ns).set('formatCode','0')
            va.find('c:numFmt',ns).set('sourceLinked','0')
            old=va.find('c:majorUnit',ns)
            if old is not None:va.remove(old)
            E.SubElement(va,'{'+ns['c']+'}majorUnit',val=str(step))
        if key=='rank':
            ln=xml.findall('.//c:ser',ns)[2].find('c:spPr/a:ln',ns)
            dash=ln.find('a:prstDash',ns)
            if dash is None:dash=E.SubElement(ln,'{'+ns['a']+'}prstDash')
            dash.set('val','sysDot')
        parts[name]=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
    if name.startswith('ppt/theme/') and name.endswith('.xml'):
        xml=E.fromstring(content)
        for latin in xml.xpath('//a:majorFont/a:latin | //a:minorFont/a:latin',namespaces=ns):latin.set('typeface','IBM Plex Sans')
        parts[name]=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(target,'w',ZIP_DEFLATED) as z:
    for name,content in parts.items():z.writestr(name,content)
print('Native chart axes, chart title placeholders and theme fonts normalized:',len(keys),'charts')
