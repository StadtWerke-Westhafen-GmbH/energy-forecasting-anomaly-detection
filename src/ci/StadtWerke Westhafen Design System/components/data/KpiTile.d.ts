import * as React from "react";

export interface KpiTileProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Short noun label, e.g. "Prognose 04/2025". */
  label: React.ReactNode;
  /** Pre-formatted German number string — the component never formats. */
  value: React.ReactNode;
  /** Unit rendered in mono after the value: "MWh", "kWh", "%", "EUR". */
  unit?: string;
  /** Signed, pre-formatted delta, e.g. "−3,4 %". Use the real minus sign. */
  delta?: React.ReactNode;
  /** Override arrow direction if it cannot be inferred from the sign. */
  deltaDirection?: "up" | "down" | "flat";
  /** Override colour semantics when up is good (or down is bad). */
  deltaTone?: "good" | "bad" | "flat";
  /** What the delta compares against, e.g. "vs. Ist 03/2025". Required whenever delta is set. */
  reference?: React.ReactNode;
  icon?: string;
  /** Trend values for the inline sparkline. */
  spark?: number[];
  sparkForecast?: number[];
  /** "accent" = navy tile, for the single headline KPI of a screen. */
  variant?: "default" | "accent";
}

/** Single headline figure with unit, signed delta, reference period and optional sparkline. */
export declare function KpiTile(props: KpiTileProps): JSX.Element;
