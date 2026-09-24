"""Read project sources and prepare presentation evidence. Never modify sources."""
from pathlib import Path
import hashlib
import json
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'eda_data.json'
FILES = {
    'raw': 'data/raw/verbrauch.csv',
    'clean': 'data/raw/260916_verbrauch_bereinigt.csv',
    'older_clean': 'data/raw/verbrauch_bereinigt.csv',
    'model': 'data/processed/modellierung_basis_bis_3_monate.csv',
}
raw = pd.read_csv(BASE / FILES['raw'])
dedup = raw.drop_duplicates().copy()
clean = pd.read_csv(BASE / FILES['clean'], parse_dates=['monat'])
model = pd.read_csv(BASE / FILES['model'], parse_dates=['monat'])
clean['year'] = clean.monat.dt.year
clean['month_number'] = clean.monat.dt.month
clean['vls_h'] = clean.verbrauch_kwh / clean.vertragsleistung_kw
clean['capacity_ratio'] = clean.vls_h / (clean.monat.dt.days_in_month * 24)
TYPES = ['Gewerbe', 'Industrie', 'Kommunal']
MONTHS = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

def norm_month(value):
    if '-' in value: return value
    if '/' in value: month, year = value.split('/')
    else: month, year = value.split('.')
    return f'{year}-{month}'

dedup['normalized_month'] = dedup.monat.map(norm_month)
dedup['mwh_text'] = dedup.verbrauch_kwh.str.contains('mwh', case=False)
dedup['numeric_consumption_kwh'] = dedup.verbrauch_kwh.str.replace('MWh', '', case=False, regex=False).astype(float) * np.where(dedup.mwh_text, 1000, 1)
meter = clean.groupby('zaehler_id').agg(
    kundentyp=('kundentyp', 'first'), vertragsleistung_kw=('vertragsleistung_kw', 'first'),
    mean_consumption_kwh=('verbrauch_kwh', 'mean'), mean_vls_h=('vls_h', 'mean'))
assert len(raw) == 16830 and len(dedup) == len(clean) == 16800
assert clean.groupby('zaehler_id').size().eq(24).all()
assert clean.groupby('monat').size().eq(700).all()
assert not clean.duplicated(['zaehler_id', 'monat']).any()
assert clean.verbrauch_kwh.notna().all()
assert clean.groupby('zaehler_id').kundentyp.nunique().eq(1).all()
assert clean.groupby('zaehler_id').vertragsleistung_kw.nunique().eq(1).all()
assert clean.zaehler_id.nunique() == clean.kunde_id.nunique() == 700

monthly = clean.groupby(['year', 'month_number']).verbrauch_kwh.sum().div(1000).unstack(0)
annual = clean.groupby('year').verbrauch_kwh.sum().div(1000)
total = clean.verbrauch_kwh.sum()
grouped = clean.groupby('kundentyp').agg(
    observation_count=('verbrauch_kwh', 'size'), consumption_kwh=('verbrauch_kwh', 'sum'),
    mean_monthly_kwh=('verbrauch_kwh', 'mean'), median_monthly_kwh=('verbrauch_kwh', 'median'),
    median_monthly_vls_h=('vls_h', 'median'))
group_meter = meter.groupby('kundentyp').agg(
    meter_count=('vertragsleistung_kw', 'size'), median_capacity_kw=('vertragsleistung_kw', 'median'))
portfolio = []
for label in TYPES:
    a, b = grouped.loc[label], group_meter.loc[label]
    portfolio.append({'customer_type':label, 'meter_count':int(b.meter_count),
        'meter_share_pct':float(b.meter_count / len(meter) * 100),
        'consumption_share_pct':float(a.consumption_kwh / total * 100),
        'consumption_mwh':float(a.consumption_kwh / 1000),
        'observation_count':int(a.observation_count),
        'median_capacity_kw':float(b.median_capacity_kw),
        'median_monthly_consumption_kwh':float(a.median_monthly_kwh),
        'mean_monthly_consumption_kwh':float(a.mean_monthly_kwh),
        'median_monthly_vls_h':float(a.median_monthly_vls_h)})

raw_formats = dedup.monat.map(lambda x: 'YYYY-MM' if '-' in x else 'MM/YYYY' if '/' in x else 'MM.YYYY').value_counts().to_dict()
sentinels=[]
for _, row in dedup[dedup.numeric_consumption_kwh.le(0)].iterrows():
    month=pd.Timestamp(row.normalized_month)
    actual=clean.loc[clean.zaehler_id.eq(row.zaehler_id) & clean.monat.eq(month)].iloc[0]
    next_row=clean.loc[clean.zaehler_id.eq(row.zaehler_id) & clean.monat.eq(month+pd.DateOffset(months=1))].iloc[0]
    assert actual.verbrauch_kwh == next_row.vormonat_verbrauch_kwh
    sentinels.append({'meter_id':row.zaehler_id,'month':row.normalized_month,
        'raw_value_kwh':float(row.numeric_consumption_kwh),'reconstructed_value_kwh':float(actual.verbrauch_kwh),
        'basis':'vormonat_verbrauch_kwh der Folgezeile desselben Zählers'})

keyed_clean=clean.set_index(['zaehler_id','monat'])
keyed_model=model.set_index(['zaehler_id','monat'])
target_delta=(keyed_clean.verbrauch_kwh-keyed_model.verbrauch_kwh).abs()
assert target_delta.max()<1e-6
capacity_flags=clean.capacity_ratio.gt(1)
model_flags=model.unmoeglich.astype(str).str.lower().eq('true')
reconstructed_flags=model.ziel_rekonstruiert.astype(str).str.lower().eq('true')
assert int(capacity_flags.sum()) == int(model_flags.sum()) == 20
assert int(reconstructed_flags.sum()) == 3
assert abs(sum(p['consumption_share_pct'] for p in portfolio)-100)<1e-9
assert abs(sum(p['meter_share_pct'] for p in portfolio)-100)<1e-9

quality = [
 {'key':'duplicates','finding':'Vollständige Dubletten','count':30,'denominator':16830,'measure':'Zeilen','action':'30 identische Zeilen entfernt. Danach eine Zeile je Zähler und Monat.','source':'data/raw/verbrauch.csv: DataFrame.duplicated(); 260916_Datenbereinigung_PC.ipynb Zellen 11–16'},
 {'key':'unit_mix','finding':'MWh-Texte in Verbrauchsspalte','count':int(dedup.mwh_text.sum()),'denominator':16800,'measure':'Zeilen nach Deduplizierung','action':'MWh mit Faktor 1.000 in kWh umgerechnet, Zielgröße numerisch gespeichert.','source':'data/raw/verbrauch.csv: case-insensitive Textsuche MWh; 260916_Datenbereinigung_PC.ipynb Zellen 49–56'},
 {'key':'customer_labels','finding':'Abweichende Kundentyp-Schreibweisen','count':int((~dedup.kundentyp.isin(TYPES)).sum()),'denominator':16800,'measure':'Zeilen nach Deduplizierung','action':'13 Roh-Ausprägungen auf Gewerbe, Industrie und Kommunal vereinheitlicht.','source':'data/raw/verbrauch.csv; 260916_Datenbereinigung_PC.ipynb Zellen 5–6'},
 {'key':'month_formats','finding':'Nicht-ISO-Monatsangaben','count':int(raw_formats['MM/YYYY']+raw_formats['MM.YYYY']),'denominator':16800,'measure':'Zeilen nach Deduplizierung','action':'Drei Monatsformate in ISO-Datum auf dem Monatsersten überführt. Monatsnummer geprüft.','source':'data/raw/verbrauch.csv; 260916_Datenbereinigung_PC.ipynb Zellen 8–9'},
 {'key':'sentinels','finding':'Zielwerte 0, −50 und −1.000','count':len(sentinels),'denominator':16800,'measure':'Zeilen','action':'Rückblickend aus dem dokumentierten Vormonatswert der Folgezeile rekonstruiert. Im ML-Hauptlauf aus Training und Benchmark ausgeschlossen.','source':'260916_Datenbereinigung_PC.ipynb Zellen 57–77; scripts/build_modeling_ihk_lernstory_notebook.py Train-/Benchmark-Filter ~ziel_rekonstruiert'},
 {'key':'missing_temperature','finding':'Fehlende Temperaturwerte','count':int(clean.mittlere_temperatur_c.isna().sum()),'denominator':16800,'measure':'Zeilen','action':'Im Cleaning nicht pauschal ergänzt. Aktueller ML-Layer verwendet vollständige Heizgradtage.','source':'data/raw/260916_verbrauch_bereinigt.csv; Modellierungsbasis Spalte heizgradtage'},
 {'key':'missing_production','finding':'Fehlender Produktionsplan','count':int(clean.produktionsplan_index.isna().sum()),'denominator':16800,'measure':'Zeilen','action':'Lücken erhalten. Falls Imputation erforderlich, nur innerhalb der trainierten Modellpipeline.','source':'data/raw/260916_verbrauch_bereinigt.csv; 260916_Datenbereinigung_PC.ipynb Zellen 83–98'},
 {'key':'capacity_flags','finding':'Verbrauch über Vertragsleistung × Monatsstunden','count':int(capacity_flags.sum()),'denominator':16800,'measure':'Zähler-Monate','action':'Gesondert markiert und fachlich zu prüfen. Vertragsleistung ist ohne Domänenbestätigung keine harte physikalische Obergrenze.','source':'eigene Neuberechnung auf 260916-Verbrauch; scripts/build_modeling_notebook.py Dokumentation zu dq_vertragsleistung'},
]
for row in quality: row['share_pct']=row['count']/row['denominator']*100

result = {
 'schema_version':1,
 'sources':{k:{'path':v,'sha256':hashlib.sha256((BASE/v).read_bytes()).hexdigest()} for k,v in FILES.items()},
 'profile':{'raw_rows':len(raw),'clean_rows':len(clean),'raw_columns':len(raw.columns),
     'meters':len(meter),'customers':int(clean.kunde_id.nunique()),'months':24,'first_month':'2024-01','last_month':'2025-12',
     'rows_per_month':700,'rows_per_meter':24,'duplicate_keys_after_cleaning':0,
     'target_missing_after_cleaning':0,'customer_type_raw_variants':int(dedup.kundentyp.nunique()),
     'customer_type_clean_variants':3,'model_target_max_difference_kwh':float(target_delta.max())},
 'quality_findings':quality,'sentinel_reconstruction':sentinels,
 'quality_counting_caveat':'Befundklassen können dieselbe Zeile betreffen und dürfen nicht zu einer Gesamtzahl fehlerhafter Zeilen summiert werden. Die beiden Werte 672 bezeichnen einmal MWh-Texte und einmal fehlende Produktionsplanwerte.',
 'current_model_population':{
     'stored_split_counts':{str(k):int(v) for k,v in model.split.value_counts().items()},
     'main_training_rows_excluding_reconstructed':int((model.split.eq('train') & ~reconstructed_flags).sum()),
     'main_benchmark_rows_excluding_reconstructed':int((model.split.eq('test') & ~reconstructed_flags).sum()),
     'capacity_flagged_train_year':int((model_flags & model.jahr.eq(2024)).sum()),
     'capacity_flagged_test_year':int((model_flags & model.jahr.eq(2025)).sum()),
     'rule':'Schnittstelle schließt die zehn Vertragsleistungsflags 2024 über split=ausschluss aus dem Training aus. Die zehn Fälle 2025 bleiben im Test. Das Flag heißt unmoeglich, die fachliche Bewertung ist dennoch offen. Hauptlauf schließt außerdem die drei aus einer Folgezeile rekonstruierten Zielwerte aus.'},
 'raw_month_format_counts_after_deduplication':{k:int(v) for k,v in raw_formats.items()},
 'missing_values_after_cleaning':{k:int(v) for k,v in clean[list(raw.columns)].isna().sum().items() if v},
 'structural_missing_history':{
     'previous_month_january_2024':700,'previous_year_all_2024':8400,
     'raw_three_month_mean_filled_january_2024':int(clean.loc[clean.monat.eq(pd.Timestamp('2024-01-01')),'letzte_3_monate_durchschnitt_kwh'].notna().sum()),
     'model_three_month_mean_missing':int(model.letzte_3_monate_vls.isna().sum()),
     'model_rule':'Je Zähler Mittel aus bis zu drei vorherigen gültigen Monaten; Januar 2024 bleibt leer. Keine zukünftigen Werte.'},
 'charts':{
   'monthly':{
     'source':FILES['clean'],'population':'Alle 16.800 bereinigten Zähler-Monate, inklusive drei rekonstruierten Zielen und 20 Vertragsleistungsflags.',
     'definition':'SUM(verbrauch_kwh) / 1000 je Kalenderjahr und Kalendermonat. 700 Zähler in jedem Monat. MWh sind Energiemenge, keine Leistung.',
     'unit':'MWh','categories':MONTHS,'series':[{'name':str(y),'values':[float(x) for x in monthly[y]]} for y in [2024,2025]],
     'annual_total_mwh':{str(y):float(annual[y]) for y in [2024,2025]},
     'annual_change_pct':float((annual[2025]/annual[2024]-1)*100),
     'pearson_monthly_profiles':float(monthly[2024].corr(monthly[2025])),
     'takeaway':'Ein ähnlicher Jahresgang erscheint in beiden Jahren. Der Monatsverbrauch liegt im Sommer und frühen Herbst niedriger.',
     'caveat':'Deskriptive Gesamtverbräuche, keine Modellleistung und kein kausaler Nachweis eines Wetter- oder Produktionseffekts.'},
   'portfolio':{
     'source':FILES['clean'],'population':'700 unterschiedliche Zähler; Verbrauch aller 16.800 bereinigten Monatswerte 01/2024–12/2025.',
     'definition':'Zähleranteil = Anzahl eindeutiger Zähler des Kundentyps / 700. Verbrauchsanteil = Summe kWh des Kundentyps / Gesamtsumme kWh über beide Jahre.',
     'unit':'%','categories':TYPES,
     'series':[{'name':'Anteil Zähler','values':[p['meter_share_pct'] for p in portfolio]},{'name':'Anteil Verbrauch','values':[p['consumption_share_pct'] for p in portfolio]}],
     'detail':portfolio,
     'takeaway':f"Industrie stellt {portfolio[1]['meter_share_pct']:.1f} % der Zähler und {portfolio[1]['consumption_share_pct']:.1f} % des Verbrauchs.",
     'caveat':'Die Anteile beschreiben unterschiedliche Bezugsgrößen. Keine Aussage über Wirtschaftlichkeit, Kundenertrag oder Fehlerquote.'},
   'normalization':{
     'source':FILES['clean'],'population':'Alle 16.800 bereinigten Zähler-Monate 01/2024–12/2025, dieselben Zeilen für beide Kennzahlen.',
     'definition':'Median der monatlichen Verbrauchswerte je Kundentyp. Normiert: je Zeile verbrauch_kwh / vertragsleistung_kw, anschließend Median je Kundentyp. Vertragsleistung ist je Zähler konstant.',
     'categories':TYPES,'raw_unit':'kWh','normalized_unit':'VLS-h',
     'raw_values':[p['median_monthly_consumption_kwh'] for p in portfolio],
     'normalized_values':[p['median_monthly_vls_h'] for p in portfolio],
     'industry_vs_commercial_raw_ratio':float(portfolio[1]['median_monthly_consumption_kwh']/portfolio[0]['median_monthly_consumption_kwh']),
     'industry_vs_commercial_normalized_ratio':float(portfolio[1]['median_monthly_vls_h']/portfolio[0]['median_monthly_vls_h']),
     'takeaway':'Nach Division durch die Vertragsleistung liegen die Mediane der drei Kundentypen deutlich näher zusammen.',
     'caveat':'Getrennte Achsen und Einheiten nötig. Die Normierung erklärt Größenunterschiede und beweist allein keinen Modellvorteil.'}},
 'capacity_flags':{'count':int(capacity_flags.sum()),'by_year':{str(y):int(v) for y,v in clean[capacity_flags].groupby('year').size().items()},'max_ratio':float(clean.capacity_ratio.max()),'definition':'verbrauch_kwh > vertragsleistung_kw × tatsächliche Kalendermonatsstunden','is_confirmed_fault':False},
 'source_disagreements':[
     'ipynb/eda.ipynb und eda_ci.ipynb starten aus verbrauch_bereinigt.csv, rekonstruieren 3 Sentinels und filtern 20 Vertragsleistungsfälle. Ihre späteren EDA-Statistiken beruhen deshalb auf 16.780 Zeilen. Die hier neu berechneten Charts nutzen 16.800 Zeilen aus 260916_verbrauch_bereinigt.csv.',
     'Die ältere EDA bezeichnet Vertragsleistungsflags als physikalisch unmöglich. Neuere Modellierungsdokumentation hält die fachliche Grenze für unbestätigt. Daher hier Prüfhinweise statt bestätigter Fehler.',
     'Die README_modellierung_basis.md nennt 19 Spalten und eine ältere Lag-Regel; die aktuelle Datei hat 20 Spalten, die Ableitung bis_3_monate verwendet verfügbare Historie.',
     'Gespeicherte Notebook-Ausgaben können von aktuellen CSVs abweichen. Alle Zahlen dieses Audits wurden direkt aus den bezeichneten CSVs neu berechnet.'
 ]
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
print(str(OUT))
print(json.dumps({'profile':result['profile'],'industry':portfolio[1],'annual_total_mwh':result['charts']['monthly']['annual_total_mwh'],'profile_correlation':result['charts']['monthly']['pearson_monthly_profiles']},ensure_ascii=True))
