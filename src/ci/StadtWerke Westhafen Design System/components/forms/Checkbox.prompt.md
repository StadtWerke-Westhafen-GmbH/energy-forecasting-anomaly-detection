One-line: checkbox for multi-select in tables and for option lists; supports `indeterminate` for the header row.

```jsx
<Checkbox label="Nur Anomalien über Schwellwert" defaultChecked />
<Checkbox indeterminate aria-label="Alle Zähler auswählen" />
```

- The teal fill marks a checked box; never use navy (navy is structure, teal is interaction).
- Use `hint` to state the consequence, not to repeat the label.
