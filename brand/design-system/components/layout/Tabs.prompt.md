One-line: in-page section switch (`underline`) or compact segmented control (`pills`).

```jsx
<Tabs value={tab} onChange={setTab} items={[
  {id:"alle",label:"Alle",count:128},
  {id:"kritisch",label:"Kritisch",icon:"octagon-alert",count:14},
  {id:"geprueft",label:"Geprüft",count:42}]} />
<Tabs variant="pills" value={unit} onChange={setUnit} items={[{id:"kwh",label:"kWh"},{id:"mwh",label:"MWh"}]} />
```

- Tabs switch views of the *same* subject; they are not navigation between screens (that is `SidebarNav`).
- `count` uses tabular mono; keep counts live, never stale.
