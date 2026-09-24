from pathlib import Path
p=Path(__file__).resolve().parent/'story.mjs'
s=p.read_text(encoding='utf-8')
s=s.replace('504 Temperatur- / 672 Planlücken','Temperatur: 504 · Plan: 672')
s=s.replace('Formate und Einheiten werden nachvollziehbar korrigiert','Formate und Einheiten nachvollziehbar korrigieren')
s=s.replace('Strukturelle Lücken, fehlender Kontext und offene Prüffälle brauchen eigene Regeln.','Bereinigte Basis vor Neuberechnung der ML-Historie · unterschiedliche Fehlgründe')
p.write_text(s,encoding='utf-8')
