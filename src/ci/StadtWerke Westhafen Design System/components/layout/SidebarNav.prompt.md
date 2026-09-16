One-line: the fixed navy left navigation of the Energie-Cockpit; teal fill marks the active screen.

```jsx
<SidebarNav value={screen} onChange={setScreen} footer="Modell v2.3 · Stand 01.04.2025" items={[
  {id:"uebersicht",label:"Übersicht",icon:"layout-dashboard",group:"Betrieb"},
  {id:"anomalien",label:"Anomalien",icon:"triangle-alert",group:"Betrieb",count:128,alert:true},
  {id:"beschaffung",label:"Beschaffung",icon:"shopping-cart",group:"Planung"}]} />
```

- The logo always sits in a white holder — the supplied raster has an opaque white background.
- Group headings are uppercase overlines in `--navy-300`; keep them to 1–2 words.
- `logoSrc` / `markSrc` default to `assets/…` relative to the **mounting page** — pass `../../assets/…` from a nested card.
