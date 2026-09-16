---
name: stadtwerke-westhafen-design
description: Use this skill to generate well-branded interfaces and assets for StadtWerke Westhafen GmbH (SWW), either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for protoyping.
user-invocable: true
---

Read the readme.md file and guidelines/brand-guide.md within this skill, and explore the other available files.
If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.
If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## Orientation

- `readme.md` — context, CONTENT FUNDAMENTALS, VISUAL FOUNDATIONS, ICONOGRAPHY, index
- `tokens/design-tokens.json` is canonical; `styles.css` loads generated local CSS and fonts.
- `components/<group>/<Name>.jsx` + `.d.ts` + `.prompt.md` — 20 React primitives
- `ui_kits/energie-cockpit/` — five-screen operations dashboard, the reference application
- `slides/` — ten 16:9 slide layouts; `guidelines/slides.md` maps them to PowerPoint
- `templates/` — three ready starting folders: Energie-Dashboard, Projekt-Präsentation, EDA-Chart-Galerie
- `src/energy_analytics/visualization/` at repository root: 15 Python charts; `assets/plotly/sww_plotly.js` is the browser counterpart. Both consume generated values.
- `guidelines/charts.md` — chart construction rules (fixed colour roles)
- `assets/` — logo crops; `assets/readme.md` lists what is missing

## Non-negotiables

1. German, *Sie*, sentence case, no emoji. Numbers with decimal comma and dot thousands.
2. Navy = structure/Ist, teal = interaction/Residuum, cyan = **model output only**. Amber/red = thresholds/status. Customer colours have fixed named roles, including green for Kommunal.
3. Ist navy solid · Prognose cyan dashed · Band cyan 16 % · Schwellwert amber dotted · Anomalie red marker.
4. Cards: white, 1 px border, `--shadow-card`, 10 px radius. No coloured left borders, no gradient backgrounds.
5. Every figure carries its unit and its reference period. Every screen carries its as-of timestamp.
6. For any chart, use `energy_analytics.visualization.eda` / `sww_plotly.js` builders before writing raw Plotly — they encode rules 2–3.
   Charts use one typeface (IBM Plex Sans, tabular figures); Geist Mono never appears inside a plot.
7. The model caveat, verbatim where relevant: "Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges."
