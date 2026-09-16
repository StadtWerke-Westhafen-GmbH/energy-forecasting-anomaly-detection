import * as React from "react";

export interface DialogProps extends React.HTMLAttributes<HTMLDivElement> {
  open: boolean;
  title: React.ReactNode;
  /** One short line of context under the title, often the Zähler-ID or period. */
  subtitle?: React.ReactNode;
  /** sm 420 · md 560 · lg 820 px. Default "md". */
  size?: "sm" | "md" | "lg";
  /** Right-aligned action row. Cancel is a secondary Button, confirm a primary. */
  footer?: React.ReactNode;
  /** Escape and scrim click call this. */
  onClose?: () => void;
}

/** Modal over a navy 48 % scrim: confirmations, Anomalie-Ticket, threshold policy editor. */
export declare function Dialog(props: DialogProps): JSX.Element;
