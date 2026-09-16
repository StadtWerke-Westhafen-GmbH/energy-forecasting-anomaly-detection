import * as React from "react";

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: React.ReactNode;
  /** Secondary line under the label. */
  hint?: string;
  /** Mixed state — used by the "alle Zähler" table header checkbox. */
  indeterminate?: boolean;
}

/** Checkbox with optional label and hint; supports the indeterminate table-header state. */
export declare function Checkbox(props: CheckboxProps): JSX.Element;
