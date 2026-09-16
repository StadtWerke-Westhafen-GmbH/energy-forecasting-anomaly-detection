import * as React from "react";

export type ButtonVariant = "primary" | "accent" | "secondary" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** primary = navy (page's single main action); accent = teal; secondary = bordered white; ghost = text; danger = destructive. Default "primary". */
  variant?: ButtonVariant;
  /** sm 28px · md 36px · lg 44px. Default "md". */
  size?: ButtonSize;
  /** Leading Lucide icon name. */
  icon?: string;
  /** Trailing Lucide icon name (chevrons, external-link, download). */
  iconAfter?: string;
  /** Shows a spinner and disables the button. */
  loading?: boolean;
  fullWidth?: boolean;
  /** Inverted treatment for use on the navy sidebar / top bar / slide covers. */
  onNavy?: boolean;
  /** Renders an <a> instead of a <button>. */
  href?: string;
}

/** SWW action button. One primary per view; German sentence-case labels. */
export declare function Button(props: ButtonProps): JSX.Element;
