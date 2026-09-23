# Modellierungsbasis mit verfügbarer Historie

`modellierung_basis_bis_3_monate.csv` ist eine reproduzierbare Ableitung von
`modellierung_basis.csv`. Patricks Schnittstellendatei bleibt dabei unverändert.

Geändert werden ausschließlich die drei Historienfelder. Sie werden je Zähler und
chronologisch neu aus gültigen Vollaststunden berechnet:

- `vormonat_vls`: letzter gültiger Vormonat;
- `letzte_3_monate_vls`: Mittel aus **bis zu drei** verfügbaren gültigen Vormonaten;
- `vorjahr_vls`: derselbe Monat des Vorjahres, sofern dieser gültig ist.

Damit gilt am Anfang jedes Zählers: Januar 2024 bleibt leer, Februar verwendet Januar,
März verwendet Januar und Februar, ab April stehen bis zu drei Vormonate bereit. Als
`unmoeglich` markierte Zielwerte fließen nicht in spätere Historienmerkmale ein. Es werden
keine Zukunftswerte ergänzt, keine Zeilen gelöscht und keine allgemeinen Fehlwerte
vorimputiert.

Die Entscheidung setzt den im Dozentengespräch genannten pragmatischen Ansatz um. Eine
Rückwärtsschätzung per Polynom oder Sinus wird bewusst nicht als Modellmerkmal verwendet:
Sie würde spätere Zielwerte desselben Jahres in frühere Validierungszeitpunkte tragen und
die zeitliche Auswertung schwerer nachvollziehbar machen.

Erzeugung und Prüfung:

```powershell
python scripts/build_modeling_basis_available_history.py
python scripts/build_modeling_basis_available_history.py --check
```

Die gleichnamige `.provenance.json` hält Regel, Hashwerte und Zeilenzahlen maschinenlesbar
fest.
