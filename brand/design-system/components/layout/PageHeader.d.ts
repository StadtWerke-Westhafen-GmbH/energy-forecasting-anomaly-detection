import * as React from "react";

export interface PageHeaderProps extends React.HTMLAttributes<HTMLElement> {
  /** Uppercase teal overline, e.g. "BESCHAFFUNG". Use sparingly. */
  eyebrow?: string;
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  /** Timestamp / record count / model version row under the subtitle. */
  meta?: React.ReactNode;
  /** Right-aligned primary + secondary actions. */
  actions?: React.ReactNode;
  /** Drops the bottom rule. */
  plain?: boolean;
}

/** Screen header: eyebrow, H1, subtitle, meta row and actions above a 1px rule. */
export declare function PageHeader(props: PageHeaderProps): JSX.Element;
