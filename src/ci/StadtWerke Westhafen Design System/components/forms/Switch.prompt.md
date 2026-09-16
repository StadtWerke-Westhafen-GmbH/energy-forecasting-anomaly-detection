One-line: toggle for settings that take effect immediately — chart overlays, auto-refresh, band visibility.

```jsx
<Switch label="Konfidenzband anzeigen" defaultChecked />
<Switch label="Anomalie-Benachrichtigungen" hint="E-Mail an Netzmanagement bei Kritisch" />
```

- Immediate effect only. Anything requiring "Speichern" is a `Checkbox`.
- Knob slides 120ms, no bounce; honours `prefers-reduced-motion`.
