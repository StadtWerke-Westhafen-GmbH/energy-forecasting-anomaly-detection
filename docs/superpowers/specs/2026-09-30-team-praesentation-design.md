# Team-Präsentation Gruppe 6 im SWW-Design – Spezifikation

Stand 30.09.2026, Präsentation am 01.10.2026. Freigegeben im Chat („ja klingt gut“).

## Ziel

Eine gemeinsame, einheitliche Präsentation für Gruppe 6 nach der Team-Vorlage
(`docs/presentation/Copy of Praesentationsvorlage_IHK(1).pptx`), gestaltet in der Designsprache
von Kikos Teil (Leitfrage + Icon-Scheibe, Titel = Antwort, Zählwerk, Merksatz-Band, Split
links Navy / rechts Weiß, dunkle Akzentfolien). Dahinter Folienmuster, mit denen Iana und
Patrick ihre Folien selbst fertigstellen. Weiterbearbeitung in **Google Slides**.

## Rahmen

- 30 Minuten Konzept, keine Live-Demo, kein Fachgespräch am Termin.
- Reihenfolge nach Agenda-Folie 2 der Vorlage: Ausgangssituation → Daten → ML Canvas →
  Methodik → Ergebnisse → Empfehlungen. Sprecherfolge Iana → Kiko → Patrick.
- Namen und Rollen laut Bericht 3.1: Iana Kraievska (Datenmanagement und Datenqualität),
  Patrick Olmo Hederer (EDA und Visualisierung), Kiko Ramon Lukas (Machine Learning und
  Evaluation). Datum 01.10.2026.
- Zahlen wie Bericht / Notebook 13; Ianas Zahlen wie ihre Folien in der Vorlage.
- Synthetische Designvorlagen (`.build/screenshots/dashboard.png`) werden nicht verwendet.

## Aufbau

| Bereich | Folien | Quelle |
|---|---|---|
| Titel, Agenda | 2 | neu; Agenda mit Kapitel, Minuten, Person |
| Iana | Ausgangssituation, Datenstruktur, Datenqualität | Vorlage-Folien 4–6 + Bericht 1.1–1.4, 3.6 |
| Kiko | 11 Hauptfolien | `build_kiko_pptx.py`, inhaltlich unverändert |
| Patrick (Entwurf) | Ergebnisse für SWW, Verbrauchs-Cockpit, Empfehlungen, Fazit aller drei, Schluss | Bericht 3.6, 3.7, 4.3–4.5; Screenshot `verbrauchs-cockpit-prueffall.png` |
| Backup | Trenner, Ianas DQ-Detailtabelle, Kikos B1–B6, Ethik | Vorlage-Folie 15, Kiko-Backups, Bericht |
| Folienmuster | Regeln, 3 Karten, Text+Bild, Tabelle, Kennzahlen, Prozess, Split, Merksatz dunkel, Screenshot+Hinweise, Baukasten | neu |

Jede Hauptfolie trägt oben rechts eine Kapitelleiste (6 Agenda-Kapitel als Icon-Scheiben),
das aktive Kapitel mit Namen der sprechenden Person (IHK: individuelle Sichtbarkeit).
Entwurfsfolien für Iana und Patrick tragen in den Notizen „Entwurf aus Bericht … – bitte prüfen“
samt Sprechtext-Vorschlag.

## Google-Slides-Tauglichkeit

- Diagramme als PNG (Element-Screenshots aus Kikos HTML-Deck, 3-fach), Texte nativ.
- Keine nativen PowerPoint-Diagramme, keine SVG-Bilder.
- Transparenzen als feste Mischfarbe auf dem Folienhintergrund.
- Textfelder ohne Umbruch bekommen etwa 10 % Breitenreserve.
- Nur IBM Plex Sans und Geist Mono (beide in Google Fonts).

## Lieferung

- `scripts/build_team_pptx.py` → `docs/presentation/team/Gruppe6_Praesentation_SWW.pptx`
- Vorschau als PNG je Folie und PDF, README für das Team.
- Tests `tests/test_team_pptx.py`; Validator der pptx-Skill; Sichtprüfung aller Renderings.
- Nicht prüfbar hier: der echte Import in Google Slides (einmal manuell hochladen).

## Umkehrbarkeit

Kikos Einzel-Deck (HTML und PPTX) bleibt unverändert. Die Team-Datei ist neu. Nach der Übergabe
ist die Google-Slides-Datei das Original; ein Neuerzeugen überschreibt dortige Änderungen.
