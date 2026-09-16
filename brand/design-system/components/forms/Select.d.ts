import * as React from "react";

export interface SelectOption { value: string; label: string }

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  hint?: string;
  error?: string;
  /** Strings or {value,label} pairs. Ignored if children are provided. */
  options?: Array<string | SelectOption>;
  size?: "sm" | "md";
}

/** Native select with SWW chrome — used for Monat, Kundentyp, Modellversion pickers. */
export declare function Select(props: SelectProps): JSX.Element;
