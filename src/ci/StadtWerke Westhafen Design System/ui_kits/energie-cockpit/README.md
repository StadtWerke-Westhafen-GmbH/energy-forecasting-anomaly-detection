# UI Kit — SWW Energie-Cockpit

Internes Betriebs-Dashboard für das Verbrauchsprognose- und Frühwarn-Projekt. Fünf Screens,
klickbar über `index.html`. Alle Primitive kommen aus `components/` (kein Neubau im Kit),
alle Charts aus Plotly mit dem Template aus `assets/plotly/`.

> **Keine Vorlage, keine Nachbildung.** Es wurde kein bestehendes SWW-Interface, kein Figma-File
> und kein Code geliefert. Dieses Kit ist die *erste* Umsetzung der Guidelines auf den im
> IHK-Brief beschriebenen Anwendungsfall — nicht die Rekonstruktion eines bestehenden Produkts.
> Screens, Beschriftungen und Metriken sind entsprechend Vorschläge und gehören mit den
> Stakeholdern abgeglichen.

## Screens

| Screen | Datei | Für wen | Inhalt |
| --- | --- | --- | --- |
| Übersicht | `UebersichtScreen.jsx` | alle | 4 KPIs, Portfolio Prognose/Ist, Anomalien nach Kundentyp, Top-6-Abweichungen |
| Anomalien | `AnomalienScreen.jsx` | Anke Bürger, Netzmanagement | Filter-Toolbar, Severity-Tabs, volle Zählertabelle, Ticket-Dialog |
| Zähler-Detail | `ZaehlerDetailScreen.jsx` | Netzmanagement | 24-Monats-Zeitreihe mit Anomalie-Markern, Residuen-Balken mit Schwellwert, Stammdaten, Feature Importance |
| Beschaffung | `BeschaffungScreen.jsx` | Stefan Lechtenberg, Beschaffung | Prognose vs. beschaffte Menge, Spot-Exposure, rollierender 6-Monats-Plan |
| Datenqualität | `DatenqualitaetScreen.jsx` | Henrik Maaß, Analyse | Befunde je Spalte, Bereinigungspipeline, Train/Test-Split |

## Interaktion in `index.html`

- Sidebar wechselt den Screen; Monatswähler in der Topbar wirkt auf alle Screens.
- Zeilenklick in *Übersicht* oder das Öffnen-Icon in *Anomalien* springt in *Zähler-Detail*.
- Ticket-Icon und "Anomalie-Ticket anlegen" öffnen den Dialog mit Prüfgrund und Notiz.
- Severity-Tabs, Kundentyp-Filter, Suche und Sortierung filtern die Tabelle wirklich.
- "Konfidenzband" schaltet das Band im Portfolio-Chart.

## Dateien

```
index.html                 Klickbare Demo (Shell + Screens + Ticket-Dialog)
Shell.jsx                  Navy-Sidebar + Topbar + Scroll-Content
Chart.jsx                  Plotly-Wrapper mit SWW-Template, ROLE/KT-Farbrollen
data.js                    Mock-Daten in der Struktur des Datenwörterbuchs
<Screen>.jsx               je ein Screen
```

## Abhängigkeiten

React 18 + Babel (CDN, gepinnt), Plotly 2.35.2 (CDN), `../../_ds_bundle.js` (vom Compiler erzeugt),
`../../styles.css`. Logos werden über `logoSrc`/`markSrc` relativ zur Seite übergeben.
