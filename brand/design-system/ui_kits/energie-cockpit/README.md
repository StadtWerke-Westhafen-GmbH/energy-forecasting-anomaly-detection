# Energie-Cockpit · Designreferenz

Fünf Ansichten: Übersicht, Anomalien, Zähler-Detail, Beschaffung und Datenqualität.
Start über den lokalen Vorschau-Server: `node scripts/preview.mjs` vom Repository-Stamm.
Dann `http://127.0.0.1:4173/design-system/ui_kits/energie-cockpit/index.html` öffnen.

Die Ansichten Übersicht, Beschaffung und Datenqualität verwenden weiterhin **synthetische
Beispieldaten**. Die Ansichten **Anomalieprüfung** und **Prüffall** verwenden dagegen einen
reproduzierbaren statischen Export der RF-VLS-Auswertung aus dem retrospektiven Benchmarkjahr
2025: 105 Prüfhinweise bei einer am 99. Perzentil kalibrierten Score-Schwelle von rund 6,33.
Es gibt keine Live-Prognose, Backend-Speicherung, Ticketübermittlung oder E-Mail-Funktion.
Fachliche Bewertungen werden für die Demonstration ausschließlich im lokalen Browser gespeichert.
Die Monatsauswahl ist auf den Beispielmonat begrenzt, damit keine unveränderten Daten mit
einem anderen Datum etikettiert werden. Noch nicht angebundene Aktionen sind deaktiviert.

Navigation, Tabellenfilter, Sortierung, Detailansicht, Intervallanzeige und Dialogvorschau
funktionieren lokal. Die Dialoge unterstützen Escape, Fokusbegrenzung und Fokusrückgabe.

- `*.jsx`: gepflegte React-Quellen.
- `index.preview.jsx`: Einstiegspunkt der Anwendung.
- `Chart.jsx`: Plotly-Wrapper auf Basis der generierten Tokens.
- `data.js`: explizite Demodaten.
- `anomaly-data.js`: generierter, statischer Export der Anomalieauswertung; nicht manuell ändern.
- `responsive.css`: Anpassung für kleinere Ansichten.
- `index.html`: lokale Laufzeitdateien aus `../../dist/`, keine CDN-Abhängigkeiten.

React, Plotly, Lucide und Fonts werden per `npm ci` installiert; `npm run build`
erzeugt die Browserdateien. Versionen stehen in `package-lock.json`.
Die Referenz benötigt keinen Browser-Compiler.

Der Datenexport wird vom Repository-Stamm reproduziert und geprüft:

```sh
python scripts/build_anomaly_dashboard_data.py
python scripts/build_anomaly_dashboard_data.py --check
```

Direkte Präsentationsansicht:
`http://127.0.0.1:4173/design-system/ui_kits/energie-cockpit/index.html?screen=anomalien`.
