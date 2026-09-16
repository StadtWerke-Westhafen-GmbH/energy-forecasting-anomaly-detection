One-line: the SWW action button — use `primary` for the single main action of a view, `secondary` for everything beside it.

```jsx
<Button variant="primary" icon="trending-up">Prognose erstellen</Button>
<Button variant="secondary" size="sm" icon="download">Export</Button>
<Button variant="ghost" iconAfter="arrow-right">Alle Anomalien</Button>
```

- Labels are German sentence case, 1–3 words, verb-first. No Title Case, no exclamation marks.
- `accent` (teal) is for accent surfaces and inline table actions; never use it next to a `primary`.
- `danger` only for irreversible acts (Anomalie-Ticket verwerfen).
- `onNavy` swaps `secondary` to a translucent white treatment for the navy shell.
- Never lighten or fade on hover — the component darkens one ramp step; do not override.
