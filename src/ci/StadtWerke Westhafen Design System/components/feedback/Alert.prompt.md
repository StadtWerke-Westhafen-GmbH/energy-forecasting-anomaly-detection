One-line: in-flow message for data-quality notes and model caveats — SWW has no floating toasts.

```jsx
<Alert status="warn" title="Einheiten gemischt">
  412 Werte in verbrauch_kwh liegen als MWh-Text vor und wurden umgerechnet.
</Alert>
<Alert status="neutral" icon="info">
  Das Modell ersetzt keine Abrechnungsentscheidung — es flaggt nur Untersuchungswürdiges.
</Alert>
```

- Place it directly above the content it qualifies (chart, table, KPI row). It never overlays.
- The neutral variant is the standard holder for the model caveat; keep that sentence verbatim.
