import React from "react";
import { Icon } from "../core/Icon.jsx";

const css = `
.sww-tblwrap{width:100%;overflow:auto}
.sww-tbl{width:100%;border-collapse:separate;border-spacing:0;font:var(--text-body)}
.sww-tbl th{position:sticky;top:0;z-index:1;background:var(--surface-sunken);backdrop-filter:var(--blur-panel);font:var(--text-overline);letter-spacing:var(--ls-caps);text-transform:uppercase;color:var(--text-secondary);text-align:left;padding:0 var(--space-4);height:var(--row-height-compact);white-space:nowrap;border-bottom:1px solid var(--border-default)}
.sww-tbl th.num,.sww-tbl td.num{text-align:right;font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.sww-tbl th.num{font-family:var(--font-sans)}
.sww-tbl td{padding:0 var(--space-4);height:var(--row-height);border-bottom:1px solid var(--border-subtle);color:var(--text-primary);vertical-align:middle;white-space:nowrap}
.sww-tbl--compact td{height:var(--row-height-compact);font-size:var(--fs-sm)}
.sww-tbl tbody tr{transition:background-color var(--dur-fast) var(--ease-standard)}
.sww-tbl tbody tr:hover{background:var(--surface-hover)}
.sww-tbl tbody tr.is-clickable{cursor:pointer}
.sww-tbl tbody tr.is-selected{background:var(--surface-accent-subtle);box-shadow:inset 2px 0 0 var(--teal-500)}
.sww-tbl tbody tr:focus-visible{outline:none;box-shadow:inset 0 0 0 2px var(--teal-500)}
.sww-tbl__sort{display:inline-flex;align-items:center;gap:4px;border:0;background:transparent;padding:0;font:inherit;letter-spacing:inherit;text-transform:inherit;color:inherit;cursor:pointer}
.sww-tbl__sort:hover{color:var(--text-primary)}
.sww-tbl__sort[data-active="true"]{color:var(--text-accent)}
.sww-tbl__mono{font-family:var(--font-mono);font-size:var(--fs-sm)}
.sww-tbl__empty{padding:var(--space-10) var(--space-4);text-align:center;color:var(--text-muted);font:var(--text-body)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-table-css")) {
  const s = document.createElement("style"); s.id = "sww-table-css"; s.textContent = css; document.head.appendChild(s);
}

export function DataTable({
  columns = [], rows = [], rowKey = "id", compact = false, selectedKey,
  onRowClick, sort, onSortChange, empty = "Keine Daten für den gewählten Zeitraum.", className = "", ...rest
}) {
  return (
    <div className="sww-tblwrap" {...rest}>
      <table className={["sww-tbl", compact && "sww-tbl--compact", className].filter(Boolean).join(" ")}>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} className={c.numeric ? "num" : undefined} style={{ width: c.width }}>
                {c.sortable && onSortChange ? (
                  <button className="sww-tbl__sort" type="button" data-active={sort && sort.key === c.key}
                    onClick={() => onSortChange({ key: c.key, dir: sort && sort.key === c.key && sort.dir === "desc" ? "asc" : "desc" })}>
                    {c.label}
                    <Icon name={sort && sort.key === c.key && sort.dir === "asc" ? "arrow-up" : "arrow-down"} size={12} />
                  </button>
                ) : c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td className="sww-tbl__empty" colSpan={columns.length}>{empty}</td></tr>
          ) : rows.map((r) => {
            const key = r[rowKey];
            return (
              <tr key={key} tabIndex={onRowClick ? 0 : undefined}
                className={[onRowClick && "is-clickable", selectedKey === key && "is-selected"].filter(Boolean).join(" ")}
                onClick={onRowClick ? () => onRowClick(r) : undefined}
                onKeyDown={onRowClick ? (e) => { if (e.key === "Enter") onRowClick(r); } : undefined}>
                {columns.map((c) => (
                  <td key={c.key} className={c.numeric ? "num" : c.mono ? "sww-tbl__mono" : undefined}>
                    {c.render ? c.render(r) : r[c.key]}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
