# Folien-Layouts (1280 × 720)

Neun Layout-Typen. Jede Datei ist eine eigenständige HTML-Folie, gerendert im 16:9-Rahmen
(`slide.css`) mit den echten Tokens aus `styles.css`.

| Datei | Typ | Einsatz |
| --- | --- | --- |
| `TitleSlide.html` | Titel | Deckblatt, Vollsignet im weißen Halter auf Navy |
| `AgendaSlide.html` | Agenda | Kapitelübersicht, aktives Kapitel in Teal |
| `SectionSlide.html` | Abschnitt | Kapiteltrenner mit großer Nummer |
| `KpiSlide.html` | Kennzahlen | 4 KPIs + eine Kernaussage |
| `ChartSlide.html` | Chart | Ein Plotly-Chart, eine Aussage als Untertitel |
| `MlCanvasSlide.html` | Raster | ML Canvas, alle 10 Felder |
| `ComparisonSlide.html` | Vergleich | Trade-off, Vorher/Nachher |
| `QuoteSlide.html` | Zitat | Stakeholder-Erwartung |
| `TableSlide.html` | Tabelle | Datenwörterbuch, Qualitätsbefunde |
| `ClosingSlide.html` | Abschluss | Empfehlungen, Vorbehalt |

## Regeln

- **Schriftgrößen**: Titel 54 px, H2 40 px, Lead 24 px, Fließtext 19–22 px, Fußzeile 16 px.
  Nie unter 15 px — bei 1280 × 720 entspricht das etwa 24 pt auf einer 1920er Bühne.
- **Höchstens zwei Hintergründe pro Deck**: weiß und Navy. `--surface-page` als dritter Ton nur für
  KPI- und Rasterfolien.
- **Ein Chart pro Folie**, Aussage in der Überschrift, Methode in der Fußzeile.
- **Logo**: Vollsignet nur auf der Titelfolie, Wortmarke in der Fußzeile, immer im weißen Halter.
- **Keine Emoji, keine Icon-Dekoration, keine Verlaufshintergründe.**
- Für den PowerPoint-Export: Folien einzeln exportieren (1280 × 720 entspricht 33,87 × 19,05 cm).
  Charts als PNG mit `scale=2` aus `assets/plotly/` einsetzen, Text als echter Text.
