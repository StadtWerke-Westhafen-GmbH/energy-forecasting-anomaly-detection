# Energie-Cockpit · Designreferenz

Fünf Ansichten: Übersicht, Anomalien, Zähler-Detail, Beschaffung und Datenqualität.
Start über den lokalen Vorschau-Server: `node scripts/preview.mjs` vom Repository-Stamm.
Dann `http://127.0.0.1:4173/design-system/ui_kits/energie-cockpit/index.html` öffnen.

Alle Werte und fachlichen Aussagen in der Vorschau sind **synthetische Beispiele**.
Es gibt keine angebundene Prognose, Speicherung, Ticketübermittlung oder E-Mail-Funktion.
Die Monatsauswahl ist auf den Beispielmonat begrenzt, damit keine unveränderten Daten mit
einem anderen Datum etikettiert werden. Noch nicht angebundene Aktionen sind deaktiviert.

Navigation, Tabellenfilter, Sortierung, Detailansicht, Intervallanzeige und Dialogvorschau
funktionieren lokal. Die Dialoge unterstützen Escape, Fokusbegrenzung und Fokusrückgabe.

- `*.jsx`: gepflegte React-Quellen.
- `index.preview.jsx`: Einstiegspunkt der Anwendung.
- `Chart.jsx`: Plotly-Wrapper auf Basis der generierten Tokens.
- `data.js`: explizite Demodaten.
- `responsive.css`: Anpassung für kleinere Ansichten.
- `index.html`: lokale Laufzeitdateien aus `../../dist/`, keine CDN-Abhängigkeiten.

React, Plotly, Lucide und Fonts werden per `npm ci` installiert; `npm run build`
erzeugt die Browserdateien. Versionen stehen in `package-lock.json`.
Die Referenz benötigt keinen Browser-Compiler.
