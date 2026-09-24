from pathlib import Path
import json

R=Path(__file__).resolve().parents[3]
A=R/'tmp/full-presentation/audit'
M=R/'tmp/presentation-redesign/audit'
native=json.loads((M/'native_chart_data.json').read_text(encoding='utf-8'))
report=json.loads((A/'report_extracted.json').read_text(encoding='utf-8'))
facts={
 'scope':'Sachliche Grundlage für vollständige SWW-IHK-Projektpräsentation und separate ML-Präsentation. Kein aktualisierter Bericht, keine neuen fachlichen Ergebnisse.',
 'sources':{
  'report':{'path':'docs/IHK_Bericht_Gruppe_6_final.docx','locator':'Kapitel und Tabellen; report_extracted.json body index ist ein interner Prüflocator, keine Seitenzahl'},
  'brief':{'path':'docs/IHK_Group6-1.pdf','locator':'Nummerierte Abschnitte 1–11'},
  'template':{'path':'docs/Copy of Praesentationsvorlage_IHK.pptx','locator':'Folien 1–18'},
  'nb13':{'path':'notebooks/13_modellierung_von_grund_auf_verstehen.ipynb','purpose':'Aktuelle gemeinsame ML-Zahlenquelle beider Decks'},
  'nb12':{'path':'notebooks/12_modeling_ihk_lernstory.ipynb','purpose':'Quelle der abweichenden Importance-Zahlen im Bericht'},
  'data':{'path':'data/processed/modellierung_basis_bis_3_monate.csv','source_hash_verified':native['source_hash_verified']},
  'dashboard':{'path':'brand/design-system/ui_kits/energie-cockpit/anomaly-data.js'},
  'presentation_guideline':{'path':'docs/Learning Journey/Die Präsentation strukturieren — 30 Minuten Konzept, 15 Minuten Demo.md'},
  'assessment_guideline':{'path':'docs/Learning Journey/IHK-Bewertungsrubriken — Transparenz-Dokument.md'},
  'canvas_guideline':{'path':'docs/Learning Journey/Der Machine Learning Canvas.md'},
  'roles_guideline':{'path':'docs/Learning Journey/Gruppenarbeit aufteilen — individuelle Sichtbarkeit als IHK-Pflicht.md'},
  'planning_guideline':{'path':'docs/Learning Journey/Projektplanung und SCRUM-Dokumentation.md'},
 },
 'identity':{
  'group':6,
  'project_title':'Prognose des monatlichen Energieverbrauchs und Prüfung ungewöhnlicher Abweichungen',
  'original_project_title':'Prognose des monatlichen Energieverbrauchs und Erkennung von Anomalien',
  'organization':'StadtWerke Westhafen GmbH',
  'organization_context':'Fallunternehmen aus bereitgestelltem Projektauftrag, kein recherchierter Realbetrieb',
  'tutor':'Anuar Santoyo',
  'team':[
   {'name':'Iana Kraievska','role':'Datenmanagement und Datenqualität','contribution':'Bereinigung, Datentypen, Einheiten, Fehlwerte und Plausibilitätsregeln','lesson':'Plausible Lastspitzen und technisch unmögliche Werte trennen. Strukturell fehlende Historie nicht automatisch imputieren.'},
   {'name':'Patrick Olmo Hederer','role':'Explorative Datenanalyse und Visualisierung','contribution':'EDA, Treiberanalyse, Diagramme und visuelle Aufbereitung','lesson':'Korrelationen nach Produktionsniveau prüfen. Visualisierung als Analysewerkzeug nutzen.'},
   {'name':'Kiko Ramon Lukas','role':'Machine Learning und Evaluation','contribution':'ML Canvas, Zielgröße, Modellwahl, zeitliche Validierung, Kalibrierung und Anomalieprüfung','lesson':'Zeitliche Validierung, Baselines und Leakage-Vermeidung sind wichtiger als zusätzliche Modellkomplexität.'},
  ],
  'date_status':{'confirmed_presentation_date':None,'report_project_phase':'07.09.2024–30.09.2024','report_submission':'24.09.2024','template_presentation_date':'01.10.2024','conflict':'Daten enthalten 2025, Literaturabruf September2026. Die 2024-Projekt-/Prüfungsdaten sind widersprüchlich. Keine automatische Ersetzung durch erfundenes 2026-Datum.','recommendation':'Prüfungstermin auf Titelfolien weglassen. Ein tatsächlicher Bearbeitungsstand kann als solcher bezeichnet werden.'},
  'sources':['report Titel/Tabelle1/§3.6','template Folie1']
 },
 'business_context':{
  'location':'Hamburger Hafengebiet','industry':'Städtischer Energieversorger','customers':700,'customer_types':['Gewerbe','Industrie','Kommunal'],'annual_revenue_eur_approx':180000000,
  'connection_types':['Mittelspannung','Niederspannung'],
  'current_process':'Beschaffung nutzt manuelle Fortschreibungen. Monatliche Analyse ist rückblickend; kein einheitliches Prognosemodell und keine vorab festgelegte Fehlerschwelle. Ungewöhnliche Verbräuche fallen häufig erst beim Quartalsabschluss auf.',
  'problems':[
   {'problem':'Ungenaue Folgemonatsprognosen','consequence':'Kurzfristige Käufe oder Verkäufe am Spotmarkt können Beschaffungskosten erhöhen.'},
   {'problem':'Verzögerte Prüfung ungewöhnlicher Verbräuche','consequence':'Mögliche Mess-, Abrechnungs- oder technische Probleme bleiben länger ungeklärt.'}
  ],
  'goal':'Reproduzierbare Folgemonatsprognose je Zähler und priorisierte menschliche Prüfung großer Residuen nach Monatsabschluss.',
  'measured_benefit':'15,9 % geringerer RMSE gegenüber der besten einfachen Baseline im retrospektiven Benchmark. 114 Hinweise bzw. durchschnittlich 9,5 pro Monat beim q99-Szenario.',
  'expected_benefit':'Planbarere Beschaffung und monatliche statt erst quartalsweiser Prüfung. Wirkung im Betrieb noch zu messen.',
  'out_of_scope':['Produktive Systemanbindung','Automatische Abrechnungs- oder Wartungsentscheidungen','Nachgewiesene Euro-Einsparungen','Validierte Defektwahrscheinlichkeit'],
  'sources':['brief §1–2','report §1.1–1.4']
 },
 'stakeholders':[
  {'name':'Stefan Lechtenberg','role':'Bereichsleiter Energiebeschaffung, Sponsor','need':'Vor Monatsbeginn eine belastbare Folgemonatsprognose für Beschaffungsplanung.','sources':['brief §3','report §3.4']},
  {'name':'Anke Bürger','role':'Leiterin Netzmanagement','need':'Nach Monatsabschluss priorisierte Hinweise je Zähler für gezielte Ursachenprüfung.','sources':['brief §3','report §3.4']},
  {'name':'Henrik Maaß','role':'Senior-Datenanalyst','need':'Reproduzierbare Pipeline und nachvollziehbare Anomaliedefinition.','sources':['brief §3','report §3.4']}
 ],
 'data':{
  'source_file':'data/raw/verbrauch.csv','raw_rows':16830,'raw_columns':16,'clean_panel_rows':16800,'clean_source_columns':16,'modeling_columns':20,
  'meters':700,'months':24,'period':'01/2024–12/2025','grain':'Eine Zeile je Zähler und Monat','unique_key':['zaehler_id','monat'],
  'provided_sources':['Zählerverbrauch','Vertragsstammdaten','Kundentyp','Kalender','Wetter','Produktionsplanung','Wartung'],
  'source_caveat':'Projekt arbeitet mit bereitgestelltem CSV-Export. Smart-Meter-, Wetterdienst- oder ERP-Anbindung sind fachliche Herkunft aus dem Brief, keine implementierten Direktverbindungen.',
  'cleaning':[
   {'issue':'Doppelte Zähler-Monat-Kombinationen','n':30,'action':'Entfernt','sources':['report §3.3.1/§4.1','template Folie6/15']},
   {'issue':'MWh-Text statt kWh','n':672,'action':'Einheit in kWh vereinheitlicht','sources':['report §3.3.1','template Folie15']},
   {'issue':'Inkonsistente Datumsformate','n':11316,'action':'Monat vereinheitlicht','status':'Zahl aus Gesamtvorlage; EDA-Agent prüft CSV','sources':['template Folie6/15']},
   {'issue':'Inkonsistente Kundentypen','n':505,'action':'Kategorien vereinheitlicht','status':'Zahl aus Gesamtvorlage; EDA-Agent prüft CSV','sources':['template Folie6/15']},
   {'issue':'Fehlende/Platzhalter-Zielwerte','n':3,'action':'Über Folgemonatsinformation rekonstruiert und markiert, aus der strikten ML-Hauptbewertung ausgeschlossen','sources':['report §3.3.1','nb13 Datenaufbereitung']},
   {'issue':'Physikalisch unmögliche Verbrauchswerte','n':20,'action':'Kennzeichnen und prüfen; 10 aus2024 vom Training ausschließen, 10 aus2025 für Plausibilitätstest im Benchmark behalten','sources':['report §3.3.1','nb13 Datenaufbereitung']},
   {'issue':'Fehlender Vorjahresverbrauch2024','n':8400,'action':'Strukturell; kein Vorjahresmerkmal im Hauptmodell','sources':['template Folie6/15','report §3.3.2']},
   {'issue':'Fehlender Vormonatsverbrauch am Panelstart','n':700,'action':'Strukturelle fehlende Historie; kein pauschales Auffüllen im Quelldatensatz','sources':['template Folie6/15']},
   {'issue':'Fehlender Produktionsplan','n':672,'action':'Für EDA erhalten; fold-interne Medianbehandlung im ML','sources':['template Folie15','report §4.2']},
   {'issue':'Fehlende Temperatur','n':504,'action':'Für EDA erhalten; Temperatur nicht im finalen ML-Set','sources':['template Folie15']},
  ],
  'important_distinction':'16.800 Panelzeilen bleiben erhalten. ML-Filter sind keine physische Löschung aller Auffälligkeiten.',
  'samples':{'original_train_split':8390,'original_test_split':8400,'training_after_reconstructed_target_filter':8389,'benchmark_after_reconstructed_target_filter':8398,'calibration':1397,'previous_month_baseline_n':8388},
  'sources':['brief §4','report §3.3.1/§4.1/§4.2/AnhangB','nb13']
 },
 'eda':{
  'findings':[
   {'claim':'92 % der Streuung des Rohverbrauchs liegen zwischen Zählern.','value':92,'unit':'Prozent','implication':'Anschlussgröße dominiert rohe kWh.','sources':['report §3.3.2'],'status':'Im Bericht belegt; unabhängiger EDA-Agent prüft genaue Rechnung'},
   {'claim':'Nach VLS-Normierung liegen die Kundentyp-Mediane zwischen160 und173 Stunden.','range':[160,173],'unit':'VLS-h','implication':'Kundentypen werden im Verbrauchsniveau vergleichbarer.','sources':['report §3.3.2/AbbildungC2'],'status':'Im Bericht belegt; genaue Segmentdaten vom EDA-Agent'},
   {'claim':'Vertragsleistung dominiert Rohverbrauch. Nach Normierung treten operative Einflüsse deutlicher hervor.','sources':['report §3.3.2/AbbildungC1/C4']},
   {'claim':'Produktionsplan und geplante Wartung sind fachlich relevante Informationen. Wartungsmonate zeigen niedrigeres Verbrauchsniveau.','sources':['report §3.3.2/AbbildungC5/C6'],'caveat':'Deskriptiver Zusammenhang, kein kausaler Nachweis.'},
   {'claim':'Saisonale Produktion überlagert Wetter- und Feiertagskorrelationen.','sources':['report §3.3.2'],'implication':'Zusammenhänge innerhalb vergleichbarer Produktionsniveaus prüfen.'},
   {'claim':'Heizgradtage ersetzen nahezu redundante Temperaturvariable.','sources':['report §3.3.2']},
  ],
  'decisions':['VLS als interne Zielgröße','Plausible Spitzen behalten, nur technisch unmögliche Werte im Training ausschließen','Historie je Zähler aus Vergangenheit neu berechnen','Kein Vorjahresmerkmal ohne Trainingshistorie aus2023'],
  'appendix_figures':['C1 Roh-/VLS-Verteilung','C2 Kundentypen roh/normiert','C3 Physikalische Monatsgrenze','C4 Korrelationen','C5 Produktionsplan','C6 Wartung']
 },
 'canvas':[
  {'nr':1,'field':'Mehrwert','content':'Genauere Folgemonatsplanung und monatliche Prüfung ungewöhnlicher Zählerwerte.'},
  {'nr':2,'field':'Datenquellen','content':'Zählerverbrauch, Verträge, Kundenmerkmale, Kalender, Wetter, Produktionsplan, Wartung.'},
  {'nr':3,'field':'Vorhersage','content':'VLS je Zähler-Monat. Rückrechnung in kWh. Nach Ist-Eingang Residuenprüfung.'},
  {'nr':4,'field':'Merkmale','content':'Historie, Saison, Kalender, Wetterprognose, Produktion, Wartung und Kundentyp; rechtzeitige Verfügbarkeit nötig.'},
  {'nr':5,'field':'Lernansatz','content':'Überwachte Regression. Lineare Regression als Referenz, Random Forest als nichtlinearer Vergleich.'},
  {'nr':6,'field':'Evaluation','content':'RMSE in kWh als Hauptmetrik, MAE/R² ergänzend. Zeitlicher Vergleich mit Vormonat und Historienmittel.'},
  {'nr':7,'field':'Entscheidung','content':'Prognose unterstützt Beschaffung. Prüfhinweis führt zur menschlichen Fachprüfung.'},
  {'nr':8,'field':'Auswirkung','content':'Pilot-KPIs: Prognosefehler, Hinweisvolumen, Prüfzeit und Bestätigungsquote. Euro-Wirkung offen.'},
  {'nr':9,'field':'Zeitpunkt','content':'Prognose vor Monatsbeginn. Prüfung nach Eingang des tatsächlichen Monatsverbrauchs.'},
  {'nr':10,'field':'Monitoring','content':'Monatliche Fehler-, Drift- und Hinweiskontrolle. Retraining erst bei belegtem Bedarf.'},
 ],
 'canvas_sources':['report Kapitel2/TabelleA1'],
 'project_work':{
  'approach':'Layerorientierte Verantwortung über drei einwöchige Sprints, anschließend Finalisierung.','sprints':[
   {'sprint':1,'topic':'Verlässliche Datenbasis','result':'16.800 konsistente Zähler-Monate','decision':'Einheitliche Datenbasis und gemeinsame physikalische Plausibilitätsregel','challenge':'Plausible Spitzen von Messfehlern unterscheiden'},
   {'sprint':2,'topic':'EDA und Canvas','result':'Größeneffekt verstanden, VLS und verfügbare Merkmale festgelegt','decision':'Normierung, Heizgradtage statt Temperatur, Vorjahresmerkmal ausgeschlossen','challenge':'Saisonale Überlagerungen nicht als kausale Wirkung ausgeben'},
   {'sprint':3,'topic':'Modell und Prüfregel','result':'RF gewählt, q99 getrennt kalibriert','decision':'Lag-Merkmale strikt aus Vergangenheit neu berechnen','challenge':'Modellwahl, Kalibrierung und2025 trennen'},
   {'sprint':'Finalisierung','topic':'Bericht, Präsentation, Demo','result':'Kennzahlen, Begriffe und Rückfragen vereinheitlicht','decision':'Prüfhinweis statt bestätigter Defekt kommunizieren','challenge':'Gemeinsame nachvollziehbare Darstellung'},
  ],'sources':['report Kapitel3/Tabelle1/Tabelle2']
 },
 'workflow':['CSV-Quelle','Import und Schema-/Eindeutigkeitsprüfung','Bereinigung und Kennzeichnung','VLS und zeitlich korrekte Historie','EDA und Merkmalentscheidung','Zeitliche Modellwahl','Rollierende Schwellenkalibrierung','Finaler Fit auf gültigem2024','Retrospektiver One-Step-Ahead-Benchmark2025','Geprüfter JSON-Export','Lokale Demo und menschliche Fachprüfung'],
 'ml':{
  'task':'Überwachte Regression mit nachgelagerter Residuenregel; keine aktuelle Klassifikation.',
  'target':'vollaststunden = verbrauch_kwh / vertragsleistung_kw',
  'backtransform':'prognose_kwh = prognose_vls × vertragsleistung_kw',
  'feature_groups':{'Historie':['vormonat_vls','letzte_3_monate_vls'],'Kalender':['monat_idx','arbeitstage','feiertage_im_monat'],'Wetter':['heizgradtage'],'Planung':['produktionsplan_index','wartung_aktiv'],'Kundengruppe':['kundentyp']},
  'feature_count':9,'capacity_is_predictor':False,
  'preprocessing':'Numerische Medianbehandlung mit Fehlwertindikatoren innerhalb des jeweiligen Trainingsfolds; One-Hot-Kodierung für Kundentyp; lineare Referenz zusätzlich standardisiert.',
  'availability':'Brief erklärt alle Eingangsmerkmale zum Monatsbeginn als bekannt. Im echten Betrieb braucht Wetter vorab verfügbare Prognosen sowie geplante Produktion/Wartung. Keine unabhängige Forecast-Vintage-Prüfung vorliegend.',
  'historical_averaging':'Je Zähler shift(1).rolling(3,min_periods=1), unmögliche Historienwerte maskiert.',
  'timeline':native['timeline'],'calibration_period':'11–12/2024','benchmark_period':'01–12/2025',
  'final_training':'Gewählter RF auf allen gültigen Entwicklungsfällen2024 trainiert. Modellparameter und Schwelle bleiben2025 fest, bereits beobachtete Vormonatswerte aktualisieren sich monatlich.',
  'model_search':{'max_depth':[8,None],'min_samples_leaf':[5,20],'max_features':[0.7,1.0],'combinations':8,'folds':3,'fits':24},
  'chosen_model':{'name':'Random Forest','n_estimators':300,'max_depth':8,'min_samples_leaf':5,'max_features':0.7,'random_state':42},
  'cv':native['cv'],'benchmark':native['benchmark'],'meta':native['meta'],'target_comparison':native['target_comparison'],
  'importance':native['importance'],'importance_repeats':3,
  'importance_source_decision':'Beide neuen Präsentationen verwenden konsistent Notebook13 mit drei Wiederholungen. Der Bericht verwendet Notebook12 mit fünf Wiederholungen; Rangfolge identisch. Quellenunterschied in betreffenden Chart-Notizen offenlegen.',
  'report_importance_5_repeats':[
   {'group':'Verbrauchshistorie','rmse_increase_kwh':7256.366398984057},{'group':'Produktionsplan','rmse_increase_kwh':797.5003188992748},{'group':'Wartung','rmse_increase_kwh':591.0569388422907},{'group':'Kalender','rmse_increase_kwh':276.16351629978453},{'group':'Wetter','rmse_increase_kwh':154.05756358766376},{'group':'Jahreszeit','rmse_increase_kwh':121.22177363282208},{'group':'Kundentyp','rmse_increase_kwh':2.8578627682050866}],
  'permutation_caveat':'Modellnutzen statt Kausalität; korrelierte Gruppen können Bedeutung teilen.',
  'threshold_rule':'abs(ist_vls − prognose_vls) >=144.3547048640247',
  'threshold_factor':'abs(residuum_vls)/schwelle; vorzeichenbehaftete Fallgrafik verwendet residuum_vls/schwelle',
  'quantile_details':{'calibration_n':1397,'q':0.99,'threshold_vls_hours':144.3547048640247,'at_or_below_threshold':1383,'above_threshold':14,'zero_based_position':1382.04},
  'threshold_options':native['threshold_options'],'alerts':native['summary'],'monthly_alerts':native['monthly'],'case':native['case'],
  'sources':['report Kapitel4/AnhangB/AnhangD','nb13','dashboard']
 },
 'risks_ethics_privacy':{
  'observed_limits':['Nur24 Monate','Retrospektiver Benchmark, kein unberührter Blindtest','Kalibrierung nur2 Wintermonate','Keine vollständigen bestätigten Anomalielabel','Verfügbarkeit der Eingangsmerkmale im Produktivprozess noch sicherzustellen','Kein Nachweis von Euro-Nutzen oder realer Fehlerentdeckungsrate'],
  'false_positive_risk':'Unnötiger Aufwand durch Hinweis auf normalen Monat. Ausmaß mangels Labels nicht messbar.',
  'false_negative_risk':'Relevante Fälle können unbemerkt bleiben. Auch Nicht-Hinweise stichprobenartig prüfen.',
  'human_control':'Keine automatische Abrechnungsentscheidung oder technische Maßnahme. Ursache und Relevanz fachlich dokumentieren.',
  'fairness':'Es liegen Kundentypen und Anschlussgrößen vor, aber keine validierte Fairnessbewertung. Segmentweise Fehler und Hinweisquoten als Pilotkontrolle vorschlagen, nicht als bereits erfüllte Garantie.',
  'privacy_source_statement':'Brief§8 beschreibt keine Personendaten im engeren Sinn. Daraus folgt keine pauschale Datenschutzfreigabe eines späteren Produktivsystems.',
  'privacy_unknowns':['Konkretes Berechtigungs- und Rollenkonzept','Aufbewahrungs-/Löschfristen','Verantwortlichkeit und produktive technische/organisatorische Maßnahmen'],
  'privacy_recommendations':['Zugriff auf Zähler-/Kundendaten nach Aufgaben begrenzen','Für Präsentation/Export nur erforderliche Kennungen und Daten nutzen','Berechtigung und Aufbewahrung vor Produktivanbindung festlegen'],
  'sources':['brief §8','report §1.4/§4.4/AnhangE','template Folie17']
 },
 'economics':{
  'confirmed_cost_or_roi_estimates':False,'revenue_is_cost_savings_base':False,
  'fact':'180Mio.EUR ist Kontextumsatz des Fallunternehmens, keine Basis für nachgewiesene Einsparung.',
  'no_supported_claims':['Euro-Einsparung','ROI-Prozentsatz','Amortisationszeit','Gesparte Prüfminuten','Anzahl verhinderter Defekte'],
  'pilot_measurements_needed':['Beschaffungsabweichung und zugehörige tatsächlich vermiedene Kosten','Prüfzeit je Fall','Bestätigungsquote und fachlicher Nutzen','Integrations- und laufende Betriebskosten'],
  'sensitivity_evidence':'Belegt ist bisher nur Prüfvolumen je Schwelle: q95 33,3 bis q99,5 5,8 Fälle/Monat.',
  'optional_workload_formula':'Jährlicher Prüfaufwand in Stunden = Hinweise/Jahr × gemessene Minuten je Hinweis ÷60. Bei q99 Hinweise/Jahr=114, Minuten noch unbekannt.',
  'recommended_slide_title':'Wie der Pilot den betrieblichen Nutzen misst',
  'sources':['report §1.4/CanvasFeld8/§3.7/§4.4.3','template Folie18 enthält nur Platzhalter']
 },
 'recommendation':{
  'decision':'Prospektiven Schattenbetrieb mit ausgewählten Zählern beginnen.',
  'steps':['Prognosen parallel zum bisherigen Prozess erzeugen','Hinweise fachlich prüfen und auch Nicht-Hinweise stichprobenartig bewerten','RMSE, MAE, Drift, Hinweisvolumen, Prüfzeit und Bestätigungsquote monatlich messen','Bei stabiler Wirkung kontrolliert integrieren und erweitern'],
  'maintenance':'Retraining oder Schwellenanpassung erst nach dokumentierter Verschlechterung und erneuter getrennter Validierung; Briefvorschlag quartalsweise wurde im Projekt nicht als automatische Regel übernommen.',
  'future_classification':'Mit ausreichend bestätigten Ja/Nein-Labels kann eine zweite überwachte Lernaufgabe Priorisierung ergänzen. Eine Prozentwahrscheinlichkeit braucht eigene Validierung und Kalibrierung.',
  'sources':['report §3.7/§4.4.3/§4.5']
 },
 'demo':{
  'status':'Lokaler Prototyp mit retrospektivem2025-Export. Keine Live-Datenanbindung.',
  'full_15_minute_plan':[
   {'minute':0,'duration_min':2,'step':'Rohdaten und Qualitätsprobleme zeigen','suggested_owner':'Iana'},
   {'minute':2,'duration_min':3,'step':'Bereinigung und geprüften Output zeigen','suggested_owner':'Iana'},
   {'minute':5,'duration_min':3,'step':'Zwei EDA-Befunde zeigen und Entscheidungen erläutern','suggested_owner':'Patrick'},
   {'minute':8,'duration_min':4,'step':'Zeitaufteilung, Modell und Evaluation zeigen','suggested_owner':'Kiko'},
   {'minute':12,'duration_min':2,'step':'Dashboard: q99, Fallprüfung, Feedback','suggested_owner':'Kiko/Übergabe nach Teamentscheidung'},
   {'minute':14,'duration_min':1,'step':'Puffer und Übergang ins Fachgespräch','suggested_owner':'Team'}],
  'cockpit_flow':['Schwelle/Umfang zeigen','Prüfliste priorisieren','Zählerfall öffnen','Datenqualität, Produktion und Wartung prüfen','Entscheidung begründen und speichern','Feedback als spätere Labels erklären'],
  'contingency':'Gecachte Notebook-Ergebnisse und Screenshots bereithalten. Der komplette Hyperparametersuchlauf muss nicht live abgewartet werden.',
  'sources':['presentation_guideline','template Folie11/12','report AnhangE']
 },
 'presentation_guidance':{
  'concept_minutes':30,'demo_minutes':15,'individual_discussion_minutes_each':15,
  'assessment_dimensions':{'Inhalt und Struktur':16,'Sprache':8,'Präsenz':6},
  'individual_visibility':'Jedes Teammitglied präsentiert eigenständig seinen verantworteten Fachbereich.',
  'main_canvas_fields':['Mehrwert','Vorhersage','Merkmale','Lernansatz','Evaluation/Entscheidung'],
  'density':'Eine zentrale Aussage pro Folie. Detailtabellen und vollständige Canvas-/Cleaninglisten ins Backup.',
  'slide_count_caveat':'Learning Journey empfiehlt6–8 Konzeptfolien und warnt vor mehr als12 in30 Minuten. Die vollständige Datei kann umfangreiche Backups enthalten; Hauptteil zeitlich markieren.',
  'sources':['presentation_guideline','assessment_guideline','roles_guideline']
 },
 'unresolved_or_source_disagreements':[
  'Projekt-/Prüfungsdaten2024 widersprechen Datensatz2025 und Literatur2026. Nicht als aktuelle Termine übernehmen.',
  'Permutation Importance Bericht/Notebook12=5 Wiederholungen, Notebook13=3. Beide Decks laut Root einheitlich Notebook13. Unterschied in Notizen kennzeichnen.',
  'Reportbenchmarktext nennt n8398 allgemein, aber Vormonatbaseline hat n8388. In Chartfußnote differenzieren.',
  'Vorlage umfasst16 Eingangsspalten. Modellierungsbasis hat20 Spalten; es sind verschiedene Datenstufen.',
  'Vorlagen-DQ-Zahlen werden parallel durch EDA-Agent kontrolliert. Nach dessen Fakten Vorrang bei Detailzählungen.',
  'Datenschutz- und Kostenseiten der Vorlage sind Platzhalter. Nur als offene Pilot-/Einführungsfragen ausarbeiten, keine gemessenen Ergebnisse erfinden.',
  'Brief schlägt GradientBoosting/quartalsweisesRetraining/mehr Features vor. Tatsächlich verwendet sind linear+RF, neun Features, bedarfsabhängige Wartung.'
 ],
 'report_coverage':{'chapter1':'business_context und stakeholders','chapter2':'canvas','chapter3':'identity.team, project_work, recommendation','chapter4':'workflow, data, eda, ml, risks, demo','appendixA':'canvas Vollständigkeit','appendixB':'data schema/ml Formeln und Konfiguration','appendixC':'eda und paralleles Chartdaten-Audit','appendixD':'ml Charts und Metriken','appendixE':'demo'}
}
(A/'project_facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wrote project_facts.json with',len(facts),'top-level sections')
