import * as React from "react";

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Lucide icon name, rendered at 24px in a neutral circle. Default "inbox". */
  icon?: string;
  /** One factual sentence fragment, e.g. "Keine Anomalien über dem Schwellwert". */
  title: React.ReactNode;
  /** One sentence of explanation — usually the active filter or threshold. */
  children?: React.ReactNode;
  actions?: React.ReactNode;
  size?: "sm" | "md";
}

/** Empty result state: fact + reason + at most one action. No illustrations, no apologies. */
export declare function EmptyState(props: EmptyStateProps): JSX.Element;
