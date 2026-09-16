# StadtWerke Westhafen GmbH — Design System

Design system for **StadtWerke Westhafen GmbH (SWW)**, a municipal energy utility in the Hamburg
Westhafen port district. SWW supplies **700 commercial, industrial and municipal large customers**
through medium- and low-voltage connections; annual revenue is **approx. EUR 180 million**.

This system exists to serve one concrete programme: the **Verbrauchsprognose- und Frühwarn-Projekt**
(monthly consumption forecasting + anomaly early warning). It therefore covers four surfaces in one
consistent language:

1. **Energie-Cockpit** — the internal operations dashboard (`ui_kits/energie-cockpit/`)
2. **Notebooks & Plotly** — chart theming for Python analysis (`assets/plotly/`)
3. **Presentations** — 16:9 slide layouts for the IHK report defence and stakeholder reviews (`slides/`)
4. **Documents & report figures** — the same type, colour and chart rules applied to print

---

## Sources this system was built from

| Source | Path / link | What was taken from it |
| --- | --- | --- |
| SWW logo (raster) | `uploads/sww-logo.png` | Entire colour palette (sampled pixel-wise), brand mark, wordmark, tagline |
| IHK project brief, Group 6 | `uploads/IHK_Group6.pdf` | Business context, stakeholders, data dictionary, ML canvas, domain vocabulary, KPI set |
| Project dataset | `https://drive.google.com/file/d/1A4QDD-n3XQIGNyXNI8Kh2qnTACvPPOPO/view?usp=drive_link` (referenced in the brief; **not read** — no access) | Column names and semantics taken from the brief's data dictionary only |

**No codebase, Figma file or existing UI was provided.** There is no prior SWW interface to recreate,
so the component inventory here is an authored standard set sized to the dashboard/notebook/slide
needs above, not a recreation. Everything visual derives from the logo plus the brief's vocabulary.

### Domain vocabulary (use these words, in German, verbatim)

`Zähler` (meter, id `zaehler_id`) · `Kunde` (`kunde_id`) · `Kundentyp`: Gewerbe / Industrie / Kommunal ·
`Vertragsleistung` (kW) · `Verbrauch` (kWh, watch MWh/kWh unification) · `Prognose` · `Ist` ·
`Residuum` / `Abweichung` · `Anomalie` · `Schwellwert` (95th-percentile policy) · `Heiztage` ·
`Arbeitstage` · `Produktionsplan-Index` · `Wartung aktiv` · `Beschaffung` / `Spotmarkt` ·
`Netzmanagement` · `Datenqualität`.

### Stakeholders the UI is written for

- **Stefan Lechtenberg** — Bereichsleiter Energiebeschaffung (sponsor). Wants next-month accuracy and
  procurement volumes. Sees totals, confidence, and cost exposure first.
- **Anke Bürger** — Leiterin Netzmanagement. Wants per-meter anomaly hints for maintenance triage.
  Sees ranked, actionable lists.
- **Henrik Maaß** — Senior-Datenanalyst. Wants a reproducible pipeline and a defensible anomaly
  definition. Sees method, thresholds, and metrics (RMSE / MAE / R²) stated on screen.

---

## CONTENT FUNDAMENTALS

**Language.** German, throughout. Technical terms stay German (`Verbrauch`, `Prognose`, `Abweichung`);
established English ML terms are kept as-is and not translated (`Random Forest`, `RMSE`, `Feature
Importance`, `Drift-Monitoring`, `ML Canvas`). Do not half-translate ("Zufallswald" is wrong).

**Register.** *Sie*, always — this is a municipal utility talking to internal professionals and
external Großkunden. Never *du*. In dashboard UI, prefer impersonal labels over addressing the user
at all: "Anomalien prüfen", not "Prüfen Sie Ihre Anomalien". First person plural ("wir") appears only
in presentations and stakeholder-facing prose, never in UI chrome.

**Tone.** Sachlich, präzise, verbindlich. State the number, then the qualification. The brief's own
voice is the model: measured, cautious about model authority, explicit about trade-offs. Mirror its
key caveat wherever the product flags something:

> Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges.

**Casing.** German sentence case with correct noun capitalisation. Headlines and buttons are
sentence case ("Prognose erstellen"), never Title Case, never ALL CAPS except the overline/eyebrow
style (`--text-overline`, `--ls-caps`, used for section eyebrows and table group headers). Units keep
a non-breaking space and standard casing: `kWh`, `MWh`, `kW`, `°C`. Never `KWH`.

**Numbers.** German formatting: decimal comma, thin/dot thousands separator — `1.284.500 kWh`,
`12,4 %`, `−8,3 %`. Use the real minus sign (−) in data, not a hyphen. Signed deltas always carry
their sign. Percentages of deviation are always stated *against* something: "+14,2 % vs. Prognose".
Dates are `MM/JJJJ` for months (`03/2025`) and `TT.MM.JJJJ` for days. Money as `EUR 180 Mio.`.
All figures sit on tabular numerals (`--font-mono` or `.tnum`) so columns align.

**Precision rules.** kWh without decimals. Percentages to one decimal. Model metrics to the
precision you can defend: `R² 0,912`, `MAE 4.180 kWh`. Never show more digits than the data supports;
never show a forecast without its reference period.

**Copy length.** UI labels 1–3 words. Table headers 1–2 words, abbreviated with a tooltip if needed
(`Ø 3 Mon.`). Empty states: one sentence of fact + one action. Error messages name the cause and the
fix, no apology ("Zählerdaten für 03/2025 fehlen. Import wiederholen.").

**Anomaly copy.** Never assert a defect. Write findings as observations plus a suggested check:
"Abweichung +38 % über Schwellwert — Zählerauslesung prüfen." Severity words map to fixed statuses:
*Hinweis* (info), *Auffällig* (warn), *Kritisch* (critical), *Geprüft* (ok/resolved).

**No emoji.** Anywhere — UI, slides, documents, commit messages in handoff docs. Status is carried
by the colour + icon + word triad, never by a pictogram. No exclamation marks in UI copy. No
marketing superlatives ("revolutionär", "State-of-the-Art"). No metadiscourse ("Hier sehen Sie…").

**Worked examples.**

| Context | Write | Not |
| --- | --- | --- |
| KPI label | `Prognose 04/2025` | `Deine Prognose für den April!` |
| KPI value | `14.820 MWh` | `14820 mwh` |
| Delta | `−3,4 % vs. Ist 03/2025` | `-3.4% besser` |
| Anomaly row | `Auffällig · +38,2 % · Zähler ZW-04412` | `⚠️ Problem gefunden!` |
| Empty state | `Keine Anomalien über dem Schwellwert. Schwellwert: 95. Perzentil.` | `Alles super — nichts zu tun 🎉` |
| Model note | `Random-Forest-Regressor, zeitlicher Split (Training 2024 / Test 2025).` | `KI-gestützte Vorhersage` |
| Button | `Anomalie-Ticket anlegen` | `Jetzt Ticket Anlegen` |

---

## VISUAL FOUNDATIONS

The logo is the whole brief: a navy harbour silhouette (container crane, industry, storage tanks)
over a **blue wave**, inside a **navy-to-green arc** with a green sun/energy arc — port infrastructure
on the left, renewable green on the right. The system reads that as: **navy = infrastructure and
structure, teal/cyan = water and data flow, green = energy and "in Ordnung", nothing decorative**.

### Colour

- **Hafen-Navy `#084878`** (`--navy-700`) is the primary: sidebar, top bar, primary buttons, headline
  ink on light, slide backgrounds. Sampled from the wordmark "Stadt".
- **Elbe-Teal `#0080A0`** (`--teal-500`) is the single interactive accent: links, focus, selected
  state, active tab, primary chart accent. Sampled from "Werke".
- **Wasser-Cyan `#0090C8`** (`--cyan-500`) is reserved for **model output** — forecast lines,
  prediction bands. Never used as UI chrome, so a cyan stroke always means "this is predicted".
- **Energie-Grün `#58A858`** (`--green-500`) means positive/renewable/within tolerance.
- **Signal-Amber `#C77E11`** = auffällig, **Signal-Rot `#B3261E`** = kritisch. These two exist only for
  status. Never as a fill, background wash, or brand colour.
- **Kai-Grau** neutrals are cool (blue-shifted), never warm grey and never pure black. Body ink is
  `--grey-900 #141A21`.

Rules: at most **two brand colours in one composition** plus neutrals. No gradient backgrounds — the
only gradient in the brand lives inside the logo artwork itself, and it is never reproduced in UI.
Large flat fields of navy are the brand's signature move; teal is a 5 % accent, not a field.

### Typography

**IBM Plex Sans** for everything UI, display and **all chart text**; **Geist Mono** only for IDs, code
tokens and the large KPI figures in tiles and tables. Plex Sans is a technical-humanist grotesque: engineering-credible, full German diacritics, legible at
11–13px in dense tables. Geist Mono is a contemporary, low-contrast monospace with clean tabular figures —
it reads as data rather than typewriter, which is why it replaced IBM Plex Mono. Display text uses `--ls-tighter` (−0.02em); overlines use `--ls-caps` (0.08em).
The scale is a 1.22 ratio from 10px to 58px (`tokens/typography.css`).

> **Substitution flag:** no brand font files were supplied. The logo wordmark is set in a geometric
> grotesque (Montserrat/Poppins class) that is **not** reproduced anywhere in this system — the logo is
> used as artwork only. If SWW has a licensed corporate typeface, send the files and this is a
> one-file change (`tokens/fonts.css`).

### Layout

Fixed app shell: 236px navy sidebar (`--sidebar-width`), 56px top bar (`--topbar-height`), scrolling
content at `--content-max: 1440px` with 24px page gutters. Content is a 12-column grid, 16px gap.
KPI rows are 4-up (desktop) and never wrap to a single orphan. Dashboard density is **compact**:
40px table rows, 36px controls, 20px card padding. Tables are the primary layout, not cards-in-a-grid:
one meter is one row. Sidebar and top bar are position-fixed; nothing else is.

### Surfaces, borders, radii

Page is `--grey-50`, cards are white. Cards: **1px `--border-default` + `--shadow-card` + 10px radius**
(`--radius-card`). Both border and shadow — the border carries the edge at low contrast, the shadow only
hints separation. Controls 6px, badges/tags pill, chart tooltips 6px, modals 14px. Nothing is fully
square except table cells and chart plot areas; nothing is a blob. There are **no** left-border accent
cards and no coloured card backgrounds; status lives in a badge or a 3px top rule, never in the fill.

### Shadows and transparency

Three levels only: `--shadow-card` (resting), `--shadow-raised` (dropdown, popover, hover on
interactive cards), `--shadow-overlay` (modal). All shadows are tinted with navy `rgba(4,38,63,…)`,
never neutral black. Transparency is used sparingly and only in three places: the modal scrim
(`--scrim`, navy 48 %), chart confidence bands (`--data-band`, cyan 16 %), and sidebar hover
(white 8 % on navy). **Backdrop blur** appears only on the modal scrim (`--blur-scrim`, 2px) and the
sticky table header when content scrolls under it (`--blur-panel`). Never blur behind text you need
to read as data.

### States

- **Hover** — light surfaces darken one neutral step (`--surface-hover`); brand buttons darken one
  ramp step (navy-700 → navy-800); on navy, overlay white 8 %. Never opacity-fade an interactive
  element on hover; never lighten a filled button.
- **Press** — one further ramp step darker, no scale, no translate. Buttons may drop to
  `--shadow-xs`. Nothing shrinks or bounces.
- **Focus** — `--focus-ring` (3px teal at 35 %) outside the element, radius preserved. Always visible,
  never removed; on navy use `--focus-ring-inverse`.
- **Selected** — `--surface-accent-subtle` fill plus a 2px teal left rule on table rows, 2px teal
  underline on tabs.
- **Disabled** — `--text-disabled` ink on `--grey-50`, 1px `--border-subtle`, `cursor:not-allowed`.
  No opacity trick (it makes data unreadable).
- **Loading** — neutral skeleton blocks at `--grey-100`, 1.4s pulse. Never spinners over charts;
  charts keep their axes and grey the plot area.

### Motion

Functional only. 120ms for control feedback, 180ms for panels and drawers, 260ms max for a route
change, 420ms for a chart's initial draw (`--dur-chart`, once, never on re-render). Easing is
`--ease-standard` (cubic-bezier(.2,0,.2,1)) — no overshoot, **no bounce, no spring, no parallax**.
Enter = fade + 4px translate; exit = fade only. Numbers never count up or animate; a KPI that
animates reads as unstable. Respect `prefers-reduced-motion` by dropping all translate and chart draw.

### Imagery

Photography, when used (slide covers, report title pages), is **real port and grid infrastructure**:
cranes, substations, switchgear, Elbe water, overhead lines — shot cool, blue-grey, overcast, no
warm golden-hour grading, no people posing, no stock-photo handshake. Treatment: full-bleed with a
navy 55 % overlay when type sits on it, otherwise untreated. No grain, no duotone gimmick, no
illustration style, no 3D renders, no icon-people.

> **Gap:** no brand photography or illustration was supplied. `assets/` therefore contains the logo
> only, and slide covers ship as flat navy fields with the logo — see `assets/readme.md`.

### Data visualisation

Charts are the brand's main visual surface, so they carry brand rules strictly: **one typeface — IBM Plex
Sans with tabular figures — for every axis, label and hover; monospace never appears inside a plot.**
White plot area, 1px `--data-grid` horizontal gridlines only (no vertical, no border box), axis labels in
`--grey-500` 11px,
2px line width, 6px markers, bars with 4px rounded ends and 36 % gap, overlaid distributions at 62 %
opacity on a log axis where the data is skewed, direct labelling on the line's end instead of a legend when there are
≤3 series. **Ist = navy solid. Prognose = cyan, dashed 4 2. Konfidenzband = cyan 16 %. Schwellwert =
amber dashed 1px. Anomalie = red filled marker, 7px.** Kundentyp keeps a fixed colour mapping
(Gewerbe teal, Industrie navy, Kommunal green) across every notebook, dashboard and slide so a
reader learns it once. Sequential ramps are navy-based; residual/diverging ramps run teal (negative /
Unterverbrauch) → grey → red (positive / Überverbrauch). Full Plotly/Matplotlib implementation in
`assets/plotly/`.

---

## ICONOGRAPHY

**Icon set: [Lucide](https://lucide.dev), loaded from CDN.** No icon assets were supplied with the
brand, and Lucide is the closest match to the system's voice: a single 24px grid, uniform
**1.75px stroke**, round caps, no fills, geometric and technical rather than friendly.

> **Substitution flag:** Lucide is a substitution, not an SWW asset. If SWW has an icon library, drop
> the SVGs into `assets/icons/` and repoint the `Icon` component's `--icon-src` — nothing else changes.

**How icons are rendered.** The `Icon` component paints the CDN SVG as a **CSS mask** filled with
`currentColor`, so icons inherit text colour and never ship as coloured bitmaps:

```css
mask: url("https://unpkg.com/lucide-static/icons/zap.svg") center/contain no-repeat;
background-color: currentColor;
```

**Rules.**
- Sizes: 14 / 16 / 20 / 24px only. 16px is the default in UI; 20px in the sidebar; 24px in empty states.
- Stroke stays at Lucide's native 2 (rendered ≈1.75 optically at 16px). Never mix a second weight.
- Icons are **monochrome** and inherit `currentColor`. An icon is never the only carrier of meaning —
  status is always icon **+** colour **+** word.
- No icon backgrounds, no circles-with-icons, no coloured icon tiles, no duotone.
- **No emoji, ever.** No Unicode dingbats as icons. The only Unicode glyphs used as symbols are
  mathematical/typographic: − (minus), · (middle dot separator), Ø (average), → (flow in diagrams),
  ± (tolerance), % , ° .
- Fixed domain mapping (learn once, reuse everywhere):
  `zap` Strom/Verbrauch · `trending-up` Prognose · `activity` Residuum/Zeitreihe ·
  `triangle-alert` Anomalie · `gauge` Zähler · `factory` Industrie · `store` Gewerbe ·
  `landmark` Kommunal · `thermometer` Temperatur/Heiztage · `wrench` Wartung ·
  `shopping-cart` Beschaffung · `database` Datenqualität · `file-chart-column` Bericht ·
  `calendar` Monat/Zeitraum · `filter` Filter · `download` Export · `check` Geprüft.

---

## Index

**Root**
- `readme.md` — this file: context, content fundamentals, visual foundations, iconography, index
- `SKILL.md` — Agent-Skill entry point (portable to Claude Code)
- `styles.css` — global CSS entry point (`@import` list only; consumers link this)
- `thumbnail.html` — homepage tile for this design system

**Tokens** (`tokens/`, all reachable from `styles.css`)
`fonts.css` · `colors.css` · `typography.css` · `spacing.css` · `radius.css` · `elevation.css` ·
`motion.css` · `charts.css` · `base.css`

**Assets** (`assets/`)
- `logo-sww-full.png` — primary lock-up (emblem + wordmark + tagline)
- `logo-sww-emblem.png` — emblem with SWW monogram, for square/favicon use
- `logo-sww-wordmark.png` — horizontal wordmark for headers and slide footers
- `assets/readme.md` — logo usage, clear space, minimum sizes, what is missing
- `assets/plotly/` — `sww_eda.py` (15 EDA figures for notebooks), `sww_plotly.js` (same builders for the
  browser), `sww_theme.py`, `sww_plotly_template.json`, `sww_matplotlib.mplstyle`, `readme.md`

**Guidelines** (`guidelines/`) — foundation specimen cards (Design System tab) plus deep dives:
`charts.md` (chart construction rules), `slides.md` (deck + PowerPoint mapping),
`charts/` (15 rendered chart-type cards, group "Charts")

**Components** (`components/`) — 20 primitives in 5 groups
- `core/` — Button, IconButton, Icon, Badge, Tag
- `forms/` — Input, Select, Checkbox, Switch
- `layout/` — Card, PageHeader, Tabs, SidebarNav
- `data/` — KpiTile, DataTable, StatusDot, Sparkline
- `feedback/` — Alert, Dialog, EmptyState

**Intentional additions** (no source defined a component inventory, so the set was authored):
- `Icon` — wrapper for the substituted Lucide glyph set; gives one place to repoint if SWW ships icons.
- `KpiTile`, `Sparkline`, `StatusDot`, `DataTable` — the forecasting/anomaly product cannot be
  assembled without them; they encode the Ist/Prognose/Schwellwert colour roles.

**UI kits** (`ui_kits/`)
- `energie-cockpit/` — internal operations dashboard: Übersicht, Anomalien, Zähler-Detail,
  Beschaffung. `index.html` is the interactive click-through.

**Slides** (`slides/`) — 10 layouts at 1280×720: Titel, Agenda, Abschnitt, KPI, Chart, ML Canvas,
Vergleich, Zitat, Tabelle, Abschluss. `slides/readme.md` lists the rules; `guidelines/slides.md`
maps them to PowerPoint point sizes.

**Templates** (`templates/`) — starting folders a consuming project copies:
- `energie-dashboard/EnergieDashboard.dc.html` — dashboard screen (sidebar, topbar, KPI row,
  Plotly forecast chart, anomaly table) composed from this system's components
- `projekt-praesentation/ProjektPraesentation.dc.html` — eight-slide 16:9 deck, print-ready
- `eda-charts/EdaCharts.dc.html` — all 15 EDA chart types in one gallery, each labelled with its
  Python and JS function name

Each template loads the system through its sibling `ds-base.js` — one line to repoint.

## Using this folder from a GitHub repository

Commit the whole folder (e.g. as `design_system/`). It is self-describing:

- **Agents / LLMs**: point them at `SKILL.md` (Agent-Skills compatible) — it links to this readme,
  the tokens and the component contracts in `*.d.ts` / `*.prompt.md`.
- **Notebooks**: `sys.path.append("design_system/assets/plotly")`, then `import sww_eda; sww_eda.setup()`.
  Every figure the EDA needs comes out on-brand; `save_for_slide()` exports for the deck.
- **Web / dashboard code**: link `design_system/styles.css` for tokens; `_ds_bundle.js` is a build
  artefact of this tool — in a plain repo, import the `.jsx` sources under `components/` instead.
- **Slides**: `slides/*.html` are the layouts, `guidelines/slides.md` translates them to PowerPoint.

Generated files (`_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json`) may be committed
or ignored; nothing in the folder depends on them except the card previews.
