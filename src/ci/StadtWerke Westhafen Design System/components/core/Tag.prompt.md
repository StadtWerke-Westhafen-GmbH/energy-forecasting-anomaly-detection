One-line: neutral metadata / filter chip — categories and attributes, never severity (that is `Badge`).

```jsx
<Tag dotColor={KUNDENTYP_COLOR.Industrie}>Industrie</Tag>
<Tag icon="wrench">Wartung aktiv</Tag>
<Tag selected onClick={toggle} onRemove={clear}>Heiztage &gt; 200</Tag>
```

- Always pass `KUNDENTYP_COLOR` for Gewerbe / Industrie / Kommunal so tags match every chart.
- `onClick` makes it a filter chip (renders a `<button>`); `selected` marks the active one.
