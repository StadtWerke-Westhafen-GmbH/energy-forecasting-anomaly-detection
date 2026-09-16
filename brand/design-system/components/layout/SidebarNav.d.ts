import * as React from "react";

export interface SidebarItem {
  id: string;
  label: string;
  /** Lucide icon name — required; the collapsed rail shows icons only. */
  icon: string;
  /** Optional group heading; consecutive items sharing a group render under one heading. */
  group?: string;
  count?: number;
  /** Renders the count pill in signal red (open critical anomalies). */
  alert?: boolean;
}

export interface SidebarNavProps extends React.HTMLAttributes<HTMLElement> {
  items: SidebarItem[];
  value: string;
  onChange?: (id: string) => void;
  /** 60px icon rail instead of the 236px panel. */
  collapsed?: boolean;
  footer?: React.ReactNode;
  /** Path to the wordmark raster, relative to the mounting page. Default "assets/logo-sww-wordmark.png". */
  logoSrc?: string;
  /** Path to the emblem raster, used when collapsed. */
  markSrc?: string;
}

/** The navy app-shell navigation: 236px panel, white logo holder, teal active item. */
export declare function SidebarNav(props: SidebarNavProps): JSX.Element;
