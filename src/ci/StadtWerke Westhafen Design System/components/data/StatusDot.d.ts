import * as React from "react";

export type DotStatus = "ok" | "warn" | "critical" | "info" | "neutral" | "running";

export interface StatusDotProps extends React.HTMLAttributes<HTMLSpanElement> {
  status?: DotStatus;
  /** Word next to the dot. Omit only inside a table cell that has a header explaining it. */
  label?: React.ReactNode;
  size?: "md" | "lg";
  /** Slow opacity pulse — only for "running" (Modelllauf aktiv). */
  pulse?: boolean;
}

/** Compact inline state marker for table cells, meter lists and pipeline status. */
export declare function StatusDot(props: StatusDotProps): JSX.Element;
