One-line: the standard container for every dashboard panel — white, 1px border, `--shadow-card`, 10px radius.

```jsx
<Card title="Prognose vs. Ist" subtitle="Portfolio, 12 Monate" icon="trending-up"
      actions={<Select size="sm" options={["12 Monate","24 Monate"]} />} flush>
  <ChartArea />
</Card>
<Card title="Datenqualität" status="warn" footer="Stand 01.04.2025, 06:00">…</Card>
```

- `flush` whenever the body is a table or chart — padding belongs to the content then.
- Status never fills the card; it is the 3px top rule plus a `Badge` in the header.
- Never add a coloured left border — that pattern is explicitly out of the brand.
