from pathlib import Path
import re
import json

path = Path(__file__).resolve().parents[1] / 'story.mjs'
original = path.read_text(encoding='utf-8')
field = r"'(?:[^'\\]|\\.)*'"
pattern = re.compile(r'const s=page\((' + field + r'),(' + field + r'),(' + field + r'),(' + field + r')')

# This source is written directly as UTF-8 by apply_patch, never through a shell pipe.
words = '''
Prüfung Präsentation Zähler anschließend große Übergaben übernimmt Anschließend
Datenqualität Geschäftsproblem Prüfregel Prüfungspräsentation Präsentationsvorlage
erklären erläutert führen könnte Für zusätzliche Bürger Fälle Großkunden Käufe Maaß
Ungünstige Verbräuche Verkäufe abschätzen häufig können stützt tatsächliche ungewöhnliche
über Fehlergröße Prüfhinweis Prüfzeiten R² Schlüssel bestätigte ergänzt erhält müssen
späteren verständlich Zielgröße begründeten für persönlichen verfügbaren zuständig
überprüfte Zählerkennung Zählungen enthält gehören rückblickend vollständig Überschreitungen
Domänenbestätigung auffällige Zusätzlich schließen spätere Plausibilitätsflags Prüfungen
Schlüsseln ausschließlich einschließlich frühere geprüften zulässigen ähnelt Ähnlichkeit
Gesamtverbräuche Rückgang beträgt früher zwölf Anschlussgröße Bezugsgrößen Zählern
Zählerzahl prüfen später zusätzlichen Dafür Größe Prüfzeit anschließende auffälliger
begründete bestätigten gehört möchten zurück Datenlücken Hälfte Verfügbarkeitskette
dafür tatsächlichen verfügbare Prädiktoren Rückrechnung Zählers dürfen früheren häufigsten
zusätzlich übersehene Auffälligkeit Begründung Betriebsänderung Datenübertragung Mögliche
Maßnahme Prüfkategorien Zählerzuordnung ausgewählte geprüft nötig zufällig zunächst
Übertragbarkeit Verfügbarkeit außerdem mögliche nächste verfügbar Datenänderungen
Fortführung Prüfkapazität Qualität Qualitätsverlust ausgewählten lösen lässt veränderte
Erkennungsqualität Rückmeldungen bestätigter ergänzen gegenüber genügend müsste öffnen
Ausführung Rückfragen erklärt vollständigen Oberfläche Rückfallebene Rückmeldung wählen
wäre Fachgespräch möglichen regulären zukünftige überschneiden gezählt unveränderte
ursprünglichen übernehmen Bestätigung Plausibilitätsfälle Temperaturlücken außerhalb
auffällig gültige gefüllt prüfbar ältere Größeneffekt Verhältnis geringfügig Zeitansätze
ausdrücklich bestätigen dreißig fünf Prüfungstermin Präsentationen Stände widersprüchlich
'''.split()

replacements = {re.sub(r'[^\x00-\x7f]', '?', word): word for word in words}
replacements.update({'?50': '−50', '?1.000': '−1.000'})
ordered = sorted(replacements.items(), key=lambda pair: len(pair[0]), reverse=True)
matches = list(pattern.finditer(original))
assert len(matches) == 25, len(matches)
updated = original
for match in reversed(matches):
    note = match.group(4)
    for broken, correct in ordered:
        note = note.replace(broken, correct)
    updated = updated[:match.start(4)] + note + updated[match.end(4):]

def masked(text):
    return pattern.sub(lambda match: match.group(0)[:match.start(4) - match.start()] + '<NOTE>', text)

assert masked(original) == masked(updated), 'Changed content outside note arguments'
remaining = []
for index, match in enumerate(pattern.finditer(updated), 1):
    note = match.group(4)
    if '?' in note:
        remaining.append({'note': index, 'contexts': [note[max(0,m.start()-45):m.end()+45] for m in re.finditer(r'\?', note)]})
path.write_text(updated, encoding='utf-8', newline='\n')
print(json.dumps({'updated_notes': 25, 'remaining_question_marks': remaining, 'outside_notes_unchanged': True}, ensure_ascii=True))
