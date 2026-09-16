import * as React from "react";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  status?: "info" | "ok" | "warn" | "critical" | "neutral";
  /** Short headline; the body then carries the detail. */
  title?: React.ReactNode;
  /** Override the status default Lucide icon. */
  icon?: string;
  /** Buttons row under the text — usually one ghost/secondary action. */
  actions?: React.ReactNode;
  onDismiss?: () => void;
}

/** Inline, in-flow message — data-quality notes, model caveats, threshold changes. Never floats. */
export declare function Alert(props: AlertProps): JSX.Element;
