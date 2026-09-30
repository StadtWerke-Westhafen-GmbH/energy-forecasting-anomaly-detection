# Endversion der Präsentation Gruppe 6

`Gruppe6_Praesentation_final.pptx` ist die Endversion für den 01.10.2026 (27 Hauptfolien, Backup-Trenner,
Backups B1–B8). `Gruppe6_Praesentation_final_Vorschau.pdf` zeigt alle Folien zum Durchsehen.

Quelle ist die im Drive zusammengeschnittene Datei `docs/Copy of Praesentationsvorlage_IHK(3).pptx`;
sie bleibt unverändert.

## Was geändert wurde

- **Übernommen:** Kikos und Patricks Folien behalten ihren Inhalt. Angepasst sind nur das Label
  (Schema „KAPITEL n · THEMA · NAME“), die Seitenzahl („n / 27“, Backups B1–B8), die Fußzeile
  („Verbrauchsprognose & Frühwarnung · Name“) und Backup-Verweise in den Notizen.
- **Neu gesetzt mit denselben Texten:** Titel, Agenda, Ausgangssituation, Datenstruktur,
  Datenqualität, Persönliches Fazit, Vielen Dank, Backup-Trenner, Datenqualität im Detail.
  Entfallen ist der Vorlagen-Hinweis „Tipp: Eine Folie reicht…“. Korrigiert wurden das Datum
  (01.10.2026) und die Spaltennamen `kundentyp` und `vorjahr_monat_verbrauch_kwh`.
- **Ianas Diagramme (Folien 6–8):** aus `data/raw/verbrauch_bereinigt.csv` mit den Plotly-Bausteinen
  des Designsystems neu berechnet (gleiche Kennzahlen wie in `ipynb/Presentation.ipynb`: Median und
  Maximum je Zähler und Jahr, relative Spitze = Maximum ÷ Median). Kundentyp-Farben nach Designsystem;
  Kommunal ist jetzt grün statt grau.
- **Kikos Folien 17 und 18:** zu einer Folie „Vom Prüfhinweis zum Klassifikationsmodell“
  zusammengeführt (heute im Cockpit, nächster Schritt, Übergabe an Patrick).

## Vor dem Termin prüfen

- In Google Slides hochladen und einmal durchklicken. Den echten Import konnten wir vorab nicht testen.
- Die Notizen der neu gesetzten Folien 1–5, 27 und 28 sind die Hinweise aus der IHK-Vorlage
  (z. B. „Begrüßen Sie die Prüfungskommission…“), unverändert übernommen; bei Bedarf durch eigene
  Sprechtexte ersetzen.
- Wer Folien einfügt oder löscht, muss Seitenzahlen und Verweise wie „Backup B5“ anpassen.

## Neu erzeugen

```bash
.venv/Scripts/python.exe scripts/build_final_praesentation.py
.venv/Scripts/python.exe -m pytest tests/test_final_praesentation.py
```

Neu erzeugen überschreibt Änderungen, die danach in Google Slides gemacht wurden.
