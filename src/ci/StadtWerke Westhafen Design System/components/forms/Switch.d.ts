import * as React from "react";

export interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: React.ReactNode;
  hint?: string;
}

/** Immediate-effect toggle (chart overlays, live settings). For form values that need saving, use Checkbox. */
export declare function Switch(props: SwitchProps): JSX.Element;
