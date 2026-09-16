One-line: the top block of every screen — eyebrow, H1, one-sentence subtitle, meta row, actions.

```jsx
<PageHeader eyebrow="Frühwarnung" title="Anomalien 03/2025"
  subtitle="Zähler mit absoluter Abweichung über dem 95-Perzentil-Schwellwert."
  meta={<><span>128 von 700 Zählern</span><span>·</span><span>Stand 01.04.2025, 06:00</span></>}
  actions={<Button icon="download" variant="secondary">Export</Button>} />
```

- The subtitle states the definition in one sentence — this is where the anomaly rule gets declared.
- `meta` always carries the data's as-of timestamp. Never show a screen of numbers without it.
