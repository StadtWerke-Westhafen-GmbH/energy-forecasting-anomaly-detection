import * as React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  /** Helper text below the field. Hidden while `error` is set. */
  hint?: string;
  /** Error message — also paints the invalid border. */
  error?: string;
  required?: boolean;
  /** sm 28px · md 36px. Default "md". */
  size?: "sm" | "md";
  /** Leading Lucide icon name. */
  icon?: string;
  /** Trailing unit or affix, e.g. "kWh", "kW", "%". Rendered in mono. */
  suffix?: React.ReactNode;
  /** Right-aligned tabular-mono figures — use for every kWh / kW / °C field. */
  numeric?: boolean;
}

/** Labelled text or numeric field with hint, error and unit suffix. */
export declare function Input(props: InputProps): JSX.Element;
