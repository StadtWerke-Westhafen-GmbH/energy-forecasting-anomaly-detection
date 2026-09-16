import React from "react";

const css = `
.sww-dot{display:inline-flex;align-items:center;gap:6px;font:var(--text-caption);color:var(--text-secondary);white-space:nowrap}
.sww-dot__d{width:8px;height:8px;border-radius:50%;flex:none;box-shadow:0 0 0 2px var(--surface-card)}
.sww-dot--lg .sww-dot__d{width:10px;height:10px}
.sww-dot--pulse .sww-dot__d{animation:sww-dot-pulse 2s var(--ease-standard) infinite}
@keyframes sww-dot-pulse{0%,100%{opacity:1}50%{opacity:.45}}
@media (prefers-reduced-motion:reduce){.sww-dot--pulse .sww-dot__d{animation:none}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-statusdot-css")) {
  const s = document.createElement("style"); s.id = "sww-statusdot-css"; s.textContent = css; document.head.appendChild(s);
}

const COLOR = {
  ok: "var(--status-ok)", warn: "var(--status-warn)", critical: "var(--status-critical)",
  info: "var(--status-info)", neutral: "var(--grey-300)", running: "var(--teal-500)",
};

export function StatusDot({ status = "neutral", label, size = "md", pulse = false, className = "", ...rest }) {
  const cls = ["sww-dot", size === "lg" && "sww-dot--lg", pulse && "sww-dot--pulse", className].filter(Boolean).join(" ");
  return (
    <span className={cls} {...rest}>
      <span className="sww-dot__d" style={{ background: COLOR[status] }} />
      {label}
    </span>
  );
}
