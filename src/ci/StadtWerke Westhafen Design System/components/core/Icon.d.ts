import * as React from "react";

/** Lucide glyph name, e.g. "zap", "triangle-alert". */
export type IconName = string;

export interface IconProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Lucide icon name (kebab-case), loaded from the Lucide CDN as a CSS mask. */
  name: IconName;
  /** 14 | 16 | 20 | 24 only. Default 16. */
  size?: 14 | 16 | 20 | 24;
  /** Overrides currentColor. Prefer inheriting. */
  color?: string;
  /** Accessible label. Omit for decorative icons (renders aria-hidden). */
  title?: string;
}

/** Monochrome icon rendered from the Lucide CDN via CSS mask, inheriting currentColor. */
export declare function Icon(props: IconProps): JSX.Element;
export declare const ICON_BASE: string;
export declare const DOMAIN_ICONS: Record<string, string>;
