import * as React from "react";

export type BadgeStatus = "ok" | "warn" | "critical" | "info" | "neutral" | "brand";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Maps to the status colour set. Default "neutral". */
  status?: BadgeStatus;
  size?: "sm" | "md";
  /** Lucide icon name rendered before the label. */
  icon?: string;
  /** Filled treatment — for navy surfaces and slide use. */
  solid?: boolean;
}

/** Status pill. Always carries a word; colour alone never conveys severity. */
export declare function Badge(props: BadgeProps): JSX.Element;
export declare const SEVERITY: Record<"geprueft" | "hinweis" | "auffaellig" | "kritisch", { status: BadgeStatus; icon: string; label: string }>;
