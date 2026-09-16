import * as React from "react";

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Lucide icon name. */
  icon: string;
  /** Required — used as both title and aria-label. */
  label: string;
  /** sm 28px · md 36px. Default "md". */
  size?: "sm" | "md";
  /** Adds the secondary-button border + white fill. */
  bordered?: boolean;
  /** Inverted treatment for the navy shell. */
  onNavy?: boolean;
  /** Toggle state — renders the teal selected treatment. */
  pressed?: boolean;
}

/** Square icon-only button for toolbars, table row actions and the app shell. */
export declare function IconButton(props: IconButtonProps): JSX.Element;
