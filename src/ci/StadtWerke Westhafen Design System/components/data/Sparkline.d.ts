import * as React from "react";

export interface SparklineProps extends React.SVGAttributes<SVGSVGElement> {
  /** Realised values (Ist) — drawn as a navy solid line. */
  values: number[];
  /** Optional predicted continuation — drawn cyan dashed 4 2, sharing the same y-scale. */
  forecast?: number[];
  width?: number;
  height?: number;
  /** Line colour; defaults to --data-actual. */
  color?: string;
  forecastColor?: string;
  /** Dot on the final realised value. Default true. */
  markLast?: boolean;
  /** Indices in `values` to mark with a red anomaly dot. */
  anomalyIndices?: number[];
}

/** 88×28 inline trend line for table rows and KPI tiles. Decorative-free: no axes, no grid, no fill. */
export declare function Sparkline(props: SparklineProps): JSX.Element;
