One-line: empty result — one factual line, one sentence naming the filter or threshold, at most one action.

```jsx
<EmptyState icon="triangle-alert" title="Keine Anomalien über dem Schwellwert"
  actions={<Button variant="secondary" size="sm">Filter zurücksetzen</Button>}>
  Schwellwert: 95. Perzentil der absoluten prozentualen Abweichung (18,0 %).
</EmptyState>
```

- Never celebratory ("Alles super"), never an apology, no emoji, no illustration.
- Always state the *why*: the active filter, the period, or the threshold that produced zero rows.
