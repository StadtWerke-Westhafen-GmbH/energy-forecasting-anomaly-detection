One-line: native `<select>` in SWW chrome — for Monat, Kundentyp, Modell and threshold-policy pickers.

```jsx
<Select label="Monat" options={["01/2025","02/2025","03/2025"]} defaultValue="03/2025" />
<Select label="Kundentyp" size="sm" options={[{value:"all",label:"Alle Kundentypen"},{value:"Industrie",label:"Industrie"}]} />
```

- Toolbar filters use `size="sm"` with no label; the label then lives in the option text ("Alle Kundentypen").
- Keep option order stable and German-collated; "Alle …" is always first.
