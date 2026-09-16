One-line: the meter list — one `Zähler` per row, sticky uppercase header, right-aligned mono numerics, teal selected row.

```jsx
<DataTable rowKey="zaehler_id" selectedKey={sel} onRowClick={open}
  sort={sort} onSortChange={setSort}
  columns={[
    {key:"zaehler_id",label:"Zähler",mono:true,width:120},
    {key:"kundentyp",label:"Kundentyp",render:r=><Tag dotColor={KUNDENTYP_COLOR[r.kundentyp]}>{r.kundentyp}</Tag>},
    {key:"ist",label:"Ist (kWh)",numeric:true,sortable:true},
    {key:"abweichung",label:"Abweichung",numeric:true,sortable:true},
    {key:"status",label:"Status",render:r=><StatusDot status={r.status} label={r.statusLabel} />}]}
  rows={rows} />
```

- Put it inside `<Card flush>` — the card owns the border, the table owns its padding.
- Units go in the header (`Ist (kWh)`), never repeated in every cell.
- Numeric columns must set `numeric` so figures align; IDs use `mono`.
