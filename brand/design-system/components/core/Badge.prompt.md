One-line: status pill for anomaly severity, data-quality state and model state — colour plus word, never colour alone.

```jsx
<Badge status="warn" icon="triangle-alert">Auffällig</Badge>
<Badge status="ok" icon="check">Geprüft</Badge>
<Badge status="brand" solid size="sm">Prognose</Badge>
```

- Use the `SEVERITY` map so severity wording stays *Geprüft / Hinweis / Auffällig / Kritisch*.
- `solid` only on navy backgrounds or slides; in tables use the default subtle fill.
