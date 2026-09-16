One-line: one headline figure — value, unit, signed delta and the period the delta compares against.

```jsx
<KpiTile label="Prognose 04/2025" value="14.820" unit="MWh" delta="+2,1 %"
         reference="vs. Ist 03/2025" icon="trending-up" spark={letzte12} />
<KpiTile variant="accent" label="Offene Anomalien" value="128" delta="+18" reference="vs. 02/2025"
         deltaTone="bad" icon="triangle-alert" />
```

- Values arrive **pre-formatted German** (`14.820`, `12,4 %`, real minus sign). The tile never formats.
- A `delta` without a `reference` is not allowed — every comparison names its baseline.
- Colour: up = red, down = green by default (consumption up is bad). Override with `deltaTone`.
- KPI rows are 4-up; use `variant="accent"` at most once per screen.
