import * as React from "react";

export interface DataTableColumn<R = any> {
  key: string;
  label: React.ReactNode;
  /** Right-aligned tabular mono — every kWh / kW / % / count column. */
  numeric?: boolean;
  /** Mono but left-aligned — IDs like ZW-04412. */
  mono?: boolean;
  sortable?: boolean;
  width?: number | string;
  render?: (row: R) => React.ReactNode;
}

export interface DataTableProps<R = any> extends React.HTMLAttributes<HTMLDivElement> {
  columns: DataTableColumn<R>[];
  rows: R[];
  /** Field used as the React key and for selection matching. Default "id". */
  rowKey?: string;
  /** 32px rows instead of 40px. */
  compact?: boolean;
  selectedKey?: string | number;
  onRowClick?: (row: R) => void;
  sort?: { key: string; dir: "asc" | "desc" };
  onSortChange?: (sort: { key: string; dir: "asc" | "desc" }) => void;
  /** Empty-state sentence. State the filter, not an apology. */
  empty?: React.ReactNode;
}

/** The primary SWW layout for meter-level data: sticky uppercase header, 40px rows, mono numerics. */
export declare function DataTable<R = any>(props: DataTableProps<R>): JSX.Element;
