One-line: inline 24-month trend for a single meter inside a table row or KPI tile — no axes, no fill, no legend.

```jsx
<Sparkline values={monatsVerbrauch} anomalyIndices={[14, 21]} />
<Sparkline values={ist} forecast={[prognose]} width={120} height={32} />
```

- Colour roles are fixed: navy = Ist, cyan dashed = Prognose, red dot = Anomalie.
- It is `aria-hidden`; the row must also carry the numeric value in text.
- For anything with axes or a threshold, use a real Plotly chart (`assets/plotly/`), not a sparkline.
