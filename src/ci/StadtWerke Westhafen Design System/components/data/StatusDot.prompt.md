One-line: compact dot + word for row-level state — meter health, pipeline stage, data-quality per column.

```jsx
<StatusDot status="ok" label="In Toleranz" />
<StatusDot status="critical" label="Kritisch" />
<StatusDot status="running" pulse label="Modelllauf läuft" />
```

- Denser than `Badge`; use it inside table rows, use `Badge` in headers and detail panels.
- `pulse` is reserved for an actually-running process. Never decorative.
