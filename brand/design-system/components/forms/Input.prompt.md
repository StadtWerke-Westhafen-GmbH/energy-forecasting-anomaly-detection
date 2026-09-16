One-line: labelled text/numeric field; `numeric` + `suffix` is the standard treatment for every energy value.

```jsx
<Input label="Zähler-ID" icon="search" placeholder="ZW-04412" />
<Input label="Schwellwert" numeric suffix="%" defaultValue="18,0" hint="95. Perzentil der Residuen" />
<Input label="Vertragsleistung" numeric suffix="kW" error="Wert muss > 0 sein" />
```

- Units live in `suffix`, never inside the label or the value.
- Labels are nouns without a colon; hints are a full short sentence.
- Errors name cause and fix; they replace the hint, never stack with it.
