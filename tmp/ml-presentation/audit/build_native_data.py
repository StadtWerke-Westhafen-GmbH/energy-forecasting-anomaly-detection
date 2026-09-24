from pathlib import Path
import json, hashlib

R=Path(__file__).resolve().parents[3]
A=R/'tmp/presentation-redesign/audit'
C=json.loads((A/'chart_data.json').read_text(encoding='utf-8'))
F=json.loads((A/'fact_summary.json').read_text(encoding='utf-8'))
D=json.loads((A/'anomaly_data.json').read_text(encoding='utf-8'))
cv=C['learn-cv-comparison']['data']
out={
 'source':'notebooks/13_modellierung_von_grund_auf_verstehen.ipynb',
 'cv':[{'model':name,'mean_rmse_kwh':cv[0]['x'][i],'sd_population_kwh':cv[0]['error_x']['array'][i],'folds_rmse_kwh':[cv[j]['x'][i] for j in range(1,4)]} for i,name in enumerate(cv[0]['y'])],
 'benchmark':[{'model':name,'rmse_kwh':C['learn-benchmark']['data'][0]['x'][i],'n':8388 if name=='Vormonat' else 8398} for i,name in enumerate(C['learn-benchmark']['data'][0]['y'])],
 'importance':[{'group':name,'rmse_increase_kwh':C['learn-feature-importance']['data'][0]['x'][i]} for i,name in enumerate(C['learn-feature-importance']['data'][0]['y'])],
 'threshold_options':F['threshold_options'],
 'monthly':F['monthly'],
 'segments':F['segments'],
 'case':{'meter':'ZL-00147','capacity_kw':49,'months':[m['month_label'] for m in F['case_ZL00147']['series'] if m['phase']=='Benchmark'],'actual_kwh':C['learn-case-timeseries']['data'][0]['y'],'forecast_kwh':C['learn-case-timeseries']['data'][1]['y'],'signed_threshold_factor':C['learn-factor-plot']['data'][0]['y']},
 'target_comparison':[{'target':name,'rmse_kwh':C['learn-vls-vs-kwh']['data'][0]['y'][i]} for i,name in enumerate(C['learn-vls-vs-kwh']['data'][0]['x'])],
 'metrics_example':[{'name':'A: gleichmäßig','absolute_errors_kwh':[10,10,10,10],'mae_kwh':10,'rmse_kwh':10},{'name':'B: Einzelpeak','absolute_errors_kwh':[0,0,0,40],'mae_kwh':10,'rmse_kwh':20}],
 'normalization_example':[{'name':'kleiner Anschluss','kwh':10000,'kw':50,'vls_hours':200},{'name':'großer Anschluss','kwh':40000,'kw':200,'vls_hours':200}],
 'timeline':[{'label':'Fold 1','train_months':'Jan–Apr 2024','validation_months':'Mai–Jun 2024'},{'label':'Fold 2','train_months':'Jan–Jun 2024','validation_months':'Jul–Aug 2024'},{'label':'Fold 3','train_months':'Jan–Aug 2024','validation_months':'Sep–Okt 2024'}],
 'summary':F['summary'],
 'meta':F['meta'],
 'source_hash_verified':hashlib.sha256((R/F['meta']['source']).read_bytes()).hexdigest()==F['meta']['source_sha256'],
}
rank=C['learn-ranked-errors']['data']
all_points=sorted({(x,y) for t in rank[:2] for x,y in zip(t['x'],t['y'])})
out['calibration_curve']={'n':len(all_points),'threshold_vls_hours':144.3547048640247,'percentile':99,'points':[{'percentile_position':x,'absolute_error_vls_hours':y} for x,y in all_points]}
out['scatter_vls']=[{'forecast':r['forecast_vls'],'actual':r['actual_vls'],'is_alert':r['abs_residual_vls']>=F['meta']['threshold_vls'],'direction':r['direction_code']} for r in D['observations']]
(A/'native_chart_data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('native_chart_data.json created. Hash verified:',out['source_hash_verified'])
