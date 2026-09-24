from pathlib import Path
import json, base64
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'tmp/presentation-redesign/audit'
nb=json.loads((ROOT/'notebooks/13_modellierung_von_grund_auf_verstehen.ipynb').read_text(encoding='utf-8'))
ids=['learn-time-split','learn-cv-comparison','learn-benchmark','learn-vls-vs-kwh','learn-feature-importance','learn-ranked-errors','learn-vls-boundary-plot','learn-threshold-workload','learn-case-timeseries','learn-factor-plot','learn-metrics-example']
def decode(o):
    if isinstance(o,dict):
        if 'bdata' in o and 'dtype' in o:
            a=np.frombuffer(base64.b64decode(o['bdata']),dtype=o['dtype'])
            if 'shape' in o: a=a.reshape(tuple(map(int,o['shape'].split(','))))
            return a.tolist()
        return {k:decode(v) for k,v in o.items()}
    if isinstance(o,list): return [decode(v) for v in o]
    return o
charts={}
for c in nb['cells']:
    if c.get('id') in ids:
        o=next((o for o in c.get('outputs',[]) if 'application/vnd.plotly.v1+json' in o.get('data',{})),None)
        if o: charts[c['id']]=decode(o['data']['application/vnd.plotly.v1+json'])
(OUT/'chart_data.json').write_text(json.dumps(charts,ensure_ascii=False,indent=2),encoding='utf-8')
raw=(ROOT/'brand/design-system/ui_kits/energie-cockpit/anomaly-data.js').read_text(encoding='utf-8')
anomaly=json.loads(raw.split('window.SWWAnomalyData = ',1)[1].rsplit(';',1)[0])
(OUT/'anomaly_data.json').write_text(json.dumps(anomaly,ensure_ascii=False,indent=2),encoding='utf-8')
summary={k:anomaly[k] for k in ['meta','summary','threshold_options','monthly','segments']}
summary['case_ZL00147']=anomaly['meters'].get('ZL-00147')
(OUT/'fact_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
for k,v in charts.items():
    print('\nCHART',k)
    for t in v['data']:
        row={a:t[a] for a in ['type','name','x','y','text','base','error_x'] if a in t}
        for a in ['x','y','text','base']:
            if isinstance(row.get(a),list) and len(row[a])>25: row[a]=str(row[a][:3])+f' ... {len(row[a])} values ... '+str(row[a][-3:])
        print(json.dumps(row,ensure_ascii=False))
print('\nFACTS',json.dumps(summary,ensure_ascii=False))
