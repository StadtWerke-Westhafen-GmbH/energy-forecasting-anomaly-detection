"""Remove empty chart title placeholders and align the editable Office theme."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import copy

root = Path(__file__).resolve().parent
target = root / 'candidate.pptx'
with ZipFile(target) as z:
    parts = {n: z.read(n) for n in z.namelist()}
ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
removed=0
for name,content in list(parts.items()):
    if name=='ppt/slides/slide10.xml':
        xml=E.fromstring(content)
        for node in xml.findall('.//a:t',ns):
            if node.text=='Anteil mit Prüfhinweis': node.text='Hinweisquote'
        parts[name]=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
    if '/charts/chart' in name and name.endswith('.xml'):
        xml=E.fromstring(content)
        for lang in xml.findall('c:lang',ns):
            lang.set('val','de-DE')
        for title in xml.findall('.//c:title',ns):
            if not ''.join(title.itertext()).strip():
                title.getparent().remove(title)
                removed+=1
        # The runtime exports horizontal chart x/y styles onto the opposite axis.
        # Repair the native OOXML axes without changing any category or value.
        chart_number=int(Path(name).stem.removeprefix('chart'))
        if chart_number in (1,2,3):
            vmax,step={1:(22000,5000),2:(17000,5000),3:(8500,2000)}[chart_number]
            va=xml.find('.//c:valAx',ns)
            ca=xml.find('.//c:catAx',ns)
            for old in list(ca.findall('c:title',ns)):
                ca.remove(old)
            scaling=va.find('c:scaling',ns)
            for tag,value in [('min',0),('max',vmax)]:
                old=scaling.find('c:'+tag,ns)
                if old is not None: scaling.remove(old)
                E.SubElement(scaling,'{'+ns['c']+'}'+tag,val=str(value))
            va.find('c:numFmt',ns).set('formatCode','0')
            va.find('c:numFmt',ns).set('sourceLinked','0')
            old=va.find('c:majorUnit',ns)
            if old is not None: va.remove(old)
            E.SubElement(va,'{'+ns['c']+'}majorUnit',val=str(step))
        if chart_number==4:
            ln=xml.findall('.//c:ser',ns)[2].find('c:spPr/a:ln',ns)
            dash=ln.find('a:prstDash',ns)
            if dash is None: dash=E.SubElement(ln,'{'+ns['a']+'}prstDash')
            dash.set('val','sysDot')
        parts[name]=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
    if name.startswith('ppt/theme/') and name.endswith('.xml'):
        xml=E.fromstring(content)
        for latin in xml.xpath('//a:majorFont/a:latin | //a:minorFont/a:latin',namespaces=ns):
            latin.set('typeface','IBM Plex Sans')
        parts[name]=E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(target,'w',ZIP_DEFLATED) as z:
    for name,content in parts.items():
        z.writestr(name,content)
print(f'Removed {removed} empty chart title placeholders. Theme fonts set to IBM Plex Sans.')
