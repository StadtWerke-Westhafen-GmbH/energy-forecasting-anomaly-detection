import * as React from "react";

export interface TabItem {
  id: string;
  label: string;
  /** Lucide icon name. */
  icon?: string;
  /** Count pill, e.g. number of anomalies in that severity. */
  count?: number;
  disabled?: boolean;
}

export interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  items: TabItem[];
  /** Currently selected tab id. */
  value: string;
  onChange?: (id: string) => void;
  /** "underline" for in-page sections, "pills" for compact segmented switches. */
  variant?: "underline" | "pills";
}

/** Tab strip — teal 2px underline for sections, grey pill group for compact switches. */
export declare function Tabs(props: TabsProps): JSX.Element;
