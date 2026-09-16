import React from "react";
import { ICONS } from "../../dist/js/icons.js";

const css = `.sww-icon{display:inline-block;flex:none;background-color:currentColor;-webkit-mask-position:center;mask-position:center;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-size:contain;mask-size:contain;vertical-align:-0.15em}`;
if (typeof document !== "undefined" && !document.getElementById("sww-icon-css")) {
  const s = document.createElement("style"); s.id = "sww-icon-css"; s.textContent = css; document.head.appendChild(s);
}

export const ICON_BASE = ""; // Icons are bundled SVG data URLs, with no network request.

/** Fixed domain mapping — see readme.md > ICONOGRAPHY. */
export const DOMAIN_ICONS = {
  verbrauch: "zap", prognose: "trending-up", residuum: "activity", anomalie: "triangle-alert",
  zaehler: "gauge", industrie: "factory", gewerbe: "store", kommunal: "landmark",
  temperatur: "thermometer", wartung: "wrench", beschaffung: "shopping-cart",
  datenqualitaet: "database", bericht: "file-chart-column", monat: "calendar",
  filter: "filter", export: "download", geprueft: "check",
};

export function Icon({ name, size = 16, color, title, style, className = "", ...rest }) {
  const src = `url("${ICONS[name] || ICONS['circle-help']}")`;
  return (
    <span
      className={`sww-icon ${className}`}
      role={title ? "img" : "presentation"}
      aria-label={title || undefined}
      aria-hidden={title ? undefined : "true"}
      style={{ width: size, height: size, color, WebkitMaskImage: src, maskImage: src, ...style }}
      {...rest}
    />
  );
}
