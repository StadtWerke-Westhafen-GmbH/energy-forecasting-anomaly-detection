import * as React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLElement> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  /** Lucide icon shown before the title. */
  icon?: string;
  /** Right-aligned header controls (IconButton, Select, Button). */
  actions?: React.ReactNode;
  footer?: React.ReactNode;
  /** Paints a 3px status rule along the top edge — the only way status enters a card. */
  status?: "ok" | "warn" | "critical" | "info" | "brand";
  /** "flat" drops the shadow; "sunken" uses the grey surface. */
  variant?: "default" | "flat" | "sunken";
  /** Hover elevation + focusable, for cards that navigate. */
  interactive?: boolean;
  /** Removes body padding — required when the body is a DataTable or a chart. */
  flush?: boolean;
}

/** The standard SWW container: white, 1px border, shadow-card, 10px radius. */
export declare function Card(props: CardProps): JSX.Element;
