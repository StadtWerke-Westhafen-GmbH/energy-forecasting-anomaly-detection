import * as React from "react";

export interface TagProps extends React.HTMLAttributes<HTMLElement> {
  /** Leading colour dot — pass KUNDENTYP_COLOR[t] to keep the chart/UI mapping identical. */
  dotColor?: string;
  /** Lucide icon name (alternative to dotColor). */
  icon?: string;
  /** Teal selected treatment, for filter chips. */
  selected?: boolean;
  /** Renders a remove affordance. */
  onRemove?: (e: React.MouseEvent) => void;
}

/** Neutral metadata chip: Kundentyp, active filters, meter attributes. Not a status — use Badge for that. */
export declare function Tag(props: TagProps): JSX.Element;
export declare const KUNDENTYP_COLOR: Record<"Gewerbe" | "Industrie" | "Kommunal", string>;
