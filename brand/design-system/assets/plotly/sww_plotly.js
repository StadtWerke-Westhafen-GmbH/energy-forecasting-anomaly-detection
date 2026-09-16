/* SWW Plotly helpers — JavaScript twin of assets/plotly/sww_eda.py.
   Every builder returns { data, layout }. Render with SWW.render(el, spec).
   Colour roles are identical to tokens/charts.css. */
(function (global) {
  if (!global.SWWTokens) throw new Error('Load dist/js/tokens.js before sww_plotly.js');
  const T = global.SWWTokens;
  const C = Object.fromEntries(Object.entries({navy:'navy-700',navy900:'navy-900',teal:'teal-500',cyan:'cyan-500',green:'chart-kommunal',amber:'data-threshold',red:'data-anomaly',ink:'text-primary',grey600:'grey-600',grey500:'text-muted',grey400:'grey-400',grey300:'grey-300',grey100:'grey-100',grey50:'grey-50'}).map(([k,v])=>[k,T.tokens[v]]));
  const QUALITATIVE = T.palette;
  const KT = T.customers;
  const ROLE = T.roles;
  const SEQ = T.sequential;
  const DIV = T.diverging;
  const scale = (arr) => arr.map((c, i) => [i / (arr.length - 1), c]);
  const FONT = T.tokens['font-chart'];
  const LABEL = FONT; // one family for every axis, label and hover — never monospace in charts

  const merge = (a, b) => {
    const o = { ...a };
    Object.keys(b || {}).forEach((k) => {
      o[k] = b[k] && typeof b[k] === "object" && !Array.isArray(b[k]) && o[k] && typeof o[k] === "object" && !Array.isArray(o[k]) ? merge(o[k], b[k]) : b[k];
    });
    return o;
  };

  const axis = () => ({
    showgrid: false, zeroline: false, showline: true, linecolor: C.grey100, ticks: "outside", ticklen: 4,
    tickcolor: C.grey100, tickfont: { family: LABEL, size: 11, color: C.grey500 }, title: { font: { family: FONT, size: 12, color: C.grey500 }, standoff: 10 },
  });

  function layout(over) {
    const base = merge(T.plotly.layout, {margin:{l:76,r:18,t:30,b:40}});
    return merge(base, over || {});
  }

  function render(el, spec, config) {
    if (!global.Plotly) return;
    const cfg = { displayModeBar: false, responsive: false, ...(config || {}) };
    const draw = () => {
      const w = el.clientWidth || (el.parentElement && el.parentElement.clientWidth) || 600;
      const h = el.clientHeight || parseInt(getComputedStyle(el).height, 10) || 280;
      return global.Plotly.react(el, spec.data, layout(merge(spec.layout || {}, { width: w, height: h, autosize: false })), cfg);
    };
    if (!el.__swwResize && typeof ResizeObserver !== "undefined") {
      let raf = 0;
      el.__swwResize = new ResizeObserver(() => { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); });
      el.__swwResize.observe(el);
    }
    return draw();
  }

  const num = (n) => new Intl.NumberFormat("de-DE").format(Math.round(n));
  const ols = (x, y) => {
    const n = x.length, mx = x.reduce((a, b) => a + b, 0) / n, my = y.reduce((a, b) => a + b, 0) / n;
    let sxy = 0, sxx = 0;
    for (let i = 0; i < n; i++) { sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) ** 2; }
    const b = sxy / (sxx || 1), a = my - b * mx;
    return { a, b };
  };

  /* ---------------- builders ---------------- */

  // 01 Zeitreihe: Ist vs Prognose mit Konfidenzband und Anomalie-Markern
  function timeseriesForecast({ x, ist, prognose, lo, hi, anomalien, yTitle = "Verbrauch (kWh)" }) {
    const data = [];
    if (lo && hi) data.push({ x: x.concat(x.slice().reverse()), y: hi.concat(lo.slice().reverse()), fill: "toself", fillcolor: ROLE.band, line: { width: 0 }, hoverinfo: "skip", name: "Konfidenzband", type: "scatter" });
    data.push({ x, y: ist, name: "Ist", mode: "lines+markers", type: "scatter", line: { color: ROLE.ist, width: 2 }, marker: { size: 5, color: ROLE.ist } });
    if (prognose) data.push({ x, y: prognose, name: "Prognose", mode: "lines", type: "scatter", line: { color: ROLE.prognose, width: 2, dash: "4,2" } });
    if (anomalien) data.push({ x: anomalien.x, y: anomalien.y, name: "Anomalie", mode: "markers", type: "scatter", marker: { size: 9, color: ROLE.anomalie, line: { width: 1.5, color: "#fff" } } });
    return { data, layout: { yaxis: { title: { text: yTitle } }, xaxis: { nticks: 6, tickangle: 0 }, margin: { t: 30 } } };
  }

  // 02 Saisonalität: Monatsmittel je Kundentyp
  function seasonality({ monate, series, yTitle = "Ø Verbrauch (kWh)" }) {
    const data = Object.keys(series).map((k) => ({ x: monate, y: series[k], name: k, mode: "lines+markers", type: "scatter", line: { color: KT[k] || undefined, width: 2 }, marker: { size: 5 } }));
    return { data, layout: { yaxis: { title: { text: yTitle } }, margin: { t: 30 } } };
  }

  // 03 Verteilung: überlagerte Histogramme je Kundentyp
  // logX: log-Skala für schiefe Verteilungen (Verbrauch über drei Größenordnungen)
  function histogram({ groups, xTitle = "Verbrauch (kWh)", nbins = 40, logX = false }) {
    const data = Object.keys(groups).map((k) => ({ x: logX ? groups[k].map((v) => Math.log10(Math.max(v, 1))) : groups[k], name: k, type: "histogram", nbinsx: nbins, opacity: 0.62, marker: { color: KT[k] || undefined } }));
    const xaxis = logX
      ? { title: { text: xTitle }, tickvals: [3, 3.5, 4, 4.5, 5, 5.5, 6], ticktext: ["1.000", "3.000", "10.000", "30.000", "100.000", "300.000", "1 Mio."] }
      : { title: { text: xTitle }, tickformat: ",d" };
    return { data, layout: { barmode: "overlay", bargap: 0.3, xaxis, yaxis: { title: { text: "Anzahl Zähler" } }, hovermode: "closest", margin: { t: 30 } } };
  }

  // 04 Boxplot je Kundentyp
  function boxplot({ groups, yTitle = "Verbrauch (kWh)" }) {
    const data = Object.keys(groups).map((k) => ({ y: groups[k], name: k, type: "box", marker: { color: KT[k] || undefined, size: 3 }, line: { width: 1.5 }, boxpoints: "outliers", fillcolor: "rgba(255,255,255,0)" }));
    return { data, layout: { showlegend: false, yaxis: { title: { text: yTitle } }, hovermode: "closest", xaxis: { showline: false } } };
  }

  // 05 Scatter mit Trendlinie je Gruppe (z. B. Temperatur vs Verbrauch)
  function scatterTrend({ groups, xTitle = "Mitteltemperatur (°C)", yTitle = "Verbrauch (kWh)" }) {
    const data = [];
    Object.keys(groups).forEach((k) => {
      const g = groups[k];
      data.push({ x: g.x, y: g.y, name: k, mode: "markers", type: "scatter", marker: { size: 6, color: KT[k] || undefined, opacity: 0.75 } });
      const { a, b } = ols(g.x, g.y);
      const xs = [Math.min(...g.x), Math.max(...g.x)];
      data.push({ x: xs, y: xs.map((v) => a + b * v), mode: "lines", type: "scatter", showlegend: false, hoverinfo: "skip", line: { color: KT[k] || C.grey400, width: 1.5, dash: "3,3" } });
    });
    return { data, layout: { hovermode: "closest", xaxis: { title: { text: xTitle }, showgrid: true, gridcolor: C.grey100 }, yaxis: { title: { text: yTitle } }, margin: { t: 30 } } };
  }

  // 06 Heatmap (sequentiell): z. B. Monat × Kundentyp
  function heatmap({ x, y, z, zTitle = "kWh" }) {
    return {
      data: [{ x, y, z, type: "heatmap", colorscale: scale(SEQ), colorbar: { title: { text: zTitle, font: { size: 11, color: C.grey500 } }, thickness: 10, len: 0.8, outlinewidth: 0, tickfont: { family: LABEL, size: 10, color: C.grey500 }, tickformat: ",d" }, hovertemplate: "%{y} · %{x}<br>%{z:,d} " + zTitle + "<extra></extra>", xgap: 2, ygap: 2 }],
      layout: { hovermode: "closest", xaxis: { showline: false, ticks: "" }, yaxis: { showgrid: false, ticks: "", tickformat: "", automargin: true }, margin: { l: 20, r: 10 } },
    };
  }

  // 07 Korrelationsmatrix (divergent, Mitte 0)
  function correlation({ labels, z, showText = false }) {
    const text = z.map((r) => r.map((v) => (v == null ? "" : v.toFixed(2).replace(".", ","))));
    return {
      data: [{ x: labels, y: labels, z, type: "heatmap", colorscale: scale(DIV), zmin: -1, zmax: 1, zmid: 0, text, texttemplate: showText ? "%{text}" : undefined, textfont: { family: LABEL, size: 10 }, colorbar: { thickness: 10, len: 0.8, outlinewidth: 0, tickfont: { family: LABEL, size: 10, color: C.grey500 } }, hovertemplate: "%{y} × %{x}<br>r = %{z:.2f}<extra></extra>", xgap: 2, ygap: 2 }],
      layout: { hovermode: "closest", xaxis: { showline: false, ticks: "", tickangle: -35, automargin: true, tickfont: { size: 10 } }, yaxis: { showgrid: false, ticks: "", tickformat: "", autorange: "reversed", automargin: true, tickfont: { size: 10 } }, margin: { l: 20, b: 20, r: 10 } },
    };
  }

  // 08 Residuen-Verteilung mit symmetrischem Schwellwert
  function residualHist({ residuen, schwelle, xTitle = "Residuum (kWh)" }) {
    return {
      data: [{ x: residuen, type: "histogram", nbinsx: 40, marker: { color: ROLE.residuum }, name: "Residuen" }],
      layout: {
        showlegend: false, hovermode: "closest", xaxis: { title: { text: xTitle }, tickformat: ",d", zeroline: true, zerolinecolor: C.grey300 }, yaxis: { title: { text: "Anzahl" } },
        shapes: [-1, 1].map((s) => ({ type: "line", x0: s * schwelle, x1: s * schwelle, y0: 0, y1: 1, yref: "paper", line: { color: ROLE.schwellwert, width: 1, dash: "3,3" } })),
        annotations: [{ x: schwelle, y: 1, yref: "paper", text: "Schwellwert ±" + num(schwelle), showarrow: false, xanchor: "left", yanchor: "top", font: { size: 11, color: ROLE.schwellwert } }],
      },
    };
  }

  // 09 Residuen über Zeit, Überschreitungen rot
  function residualBars({ x, residuen, schwelle, yTitle = "Residuum (kWh)" }) {
    return {
      data: [{ type: "bar", x, y: residuen, name: "Residuum", marker: { color: residuen.map((r) => (Math.abs(r) > schwelle ? ROLE.anomalie : ROLE.residuum)) } }],
      layout: {
        showlegend: false, yaxis: { title: { text: yTitle }, zeroline: true, zerolinecolor: C.grey300 }, xaxis: { nticks: 6, tickangle: 0 },
        shapes: [-1, 1].map((s) => ({ type: "line", xref: "paper", x0: 0, x1: 1, y0: s * schwelle, y1: s * schwelle, line: { color: ROLE.schwellwert, width: 1, dash: "3,3" } })),
      },
    };
  }

  // long snake_case labels: break once at the underscore nearest the middle
  const wrapLabel = (s, max = 24) => {
    if (s.length <= max) return s;
    const mid = Math.floor(s.length / 2);
    let best = -1;
    for (let i = 0; i < s.length; i++) if (s[i] === "_" && (best < 0 || Math.abs(i - mid) < Math.abs(best - mid))) best = i;
    return best > 0 ? s.slice(0, best + 1) + "<br>" + s.slice(best + 1) : s;
  };

  // 10 Feature Importance (horizontal, sortiert)
  function featureImportance({ features, values, xTitle = "Anteil" }) {
    const idx = values.map((_, i) => i).sort((a, b) => values[a] - values[b]);
    return {
      data: [{ type: "bar", orientation: "h", y: idx.map((i) => wrapLabel(features[i])), x: idx.map((i) => values[i]), marker: { color: ROLE.ist }, text: idx.map((i) => values[i].toFixed(3).replace(".", ",")), textposition: "outside", textfont: { family: LABEL, size: 11, color: C.grey600 }, cliponaxis: false }],
      layout: { showlegend: false, hovermode: "closest", xaxis: { title: { text: xTitle }, showgrid: true, gridcolor: C.grey100, showline: false, tickformat: ",.2f" }, yaxis: { showgrid: false, tickformat: "", automargin: true, tickfont: { family: LABEL, size: 11, color: C.grey600 } }, margin: { l: 20, r: 50 } },
    };
  }

  // 11 Datenqualität: fehlende / fehlerhafte Werte je Spalte (%)
  function missingValues({ columns, pct, title = "Anteil fehlerhaft/fehlend (%)" }) {
    return {
      data: [{ type: "bar", orientation: "h", y: columns.slice().reverse().map((c) => wrapLabel(c)), x: pct.slice().reverse(), marker: { color: pct.slice().reverse().map((p) => (p >= 5 ? ROLE.anomalie : p >= 1 ? ROLE.schwellwert : C.grey300)) }, text: pct.slice().reverse().map((p) => p.toFixed(1).replace(".", ",") + " %"), textposition: "outside", textfont: { family: LABEL, size: 11, color: C.grey600 }, cliponaxis: false }],
      layout: { showlegend: false, hovermode: "closest", xaxis: { title: { text: title }, showgrid: true, gridcolor: C.grey100, showline: false, tickformat: ",.0f", ticksuffix: " %" }, yaxis: { showgrid: false, tickformat: "", automargin: true, tickfont: { family: LABEL, size: 11, color: C.grey600 } }, margin: { l: 20, r: 60 } },
    };
  }

  // 12 Parity-Plot: Prognose vs Ist mit 45°-Linie
  function parity({ ist, prognose, anomalie, xTitle = "Prognose (kWh)", yTitle = "Ist (kWh)" }) {
    const mn = Math.min(...ist, ...prognose), mx = Math.max(...ist, ...prognose);
    const colors = (anomalie || ist.map(() => false)).map((a) => (a ? ROLE.anomalie : ROLE.ist));
    return {
      data: [
        { x: [mn, mx], y: [mn, mx], mode: "lines", type: "scatter", name: "Ist = Prognose", hoverinfo: "skip", line: { color: C.grey300, width: 1, dash: "4,4" } },
        { x: prognose, y: ist, mode: "markers", type: "scatter", name: "Zähler", marker: { size: 6, color: colors, opacity: 0.8 } },
      ],
      layout: { hovermode: "closest", xaxis: { title: { text: xTitle }, tickformat: ",d", showgrid: true, gridcolor: C.grey100 }, yaxis: { title: { text: yTitle } }, showlegend: false },
    };
  }

  // 13 Anomalien je Monat, gestapelt nach Kundentyp
  function anomalyStack({ x, series }) {
    return {
      data: Object.keys(series).map((k) => ({ type: "bar", name: k, x, y: series[k], marker: { color: KT[k] || undefined } })),
      layout: { barmode: "stack", yaxis: { title: { text: "Anomalien" } }, xaxis: { nticks: 6, tickangle: 0 }, margin: { t: 30 } },
    };
  }

  // 14 Top-N Rangliste (z. B. Zähler nach Verbrauch)
  function topN({ labels, values, xTitle = "Verbrauch (kWh)" }) {
    const idx = values.map((_, i) => i).sort((a, b) => values[a] - values[b]);
    return {
      data: [{ type: "bar", orientation: "h", y: idx.map((i) => labels[i]), x: idx.map((i) => values[i]), marker: { color: ROLE.ist }, text: idx.map((i) => num(values[i])), textposition: "outside", textfont: { family: LABEL, size: 11, color: C.grey600 }, cliponaxis: false }],
      layout: { showlegend: false, hovermode: "closest", xaxis: { title: { text: xTitle }, showgrid: true, gridcolor: C.grey100, showline: false, tickformat: ",d" }, yaxis: { showgrid: false, tickformat: "", automargin: true, tickfont: { family: LABEL, size: 11, color: C.grey600 } }, margin: { l: 20, r: 70 } },
    };
  }

  // 15 Anteile über Zeit (gestapelte Fläche, 100 %)
  function shareArea({ x, series, yTitle = "Anteil" }) {
    return {
      data: Object.keys(series).map((k) => ({ x, y: series[k], name: k, type: "scatter", mode: "lines", stackgroup: "one", groupnorm: "percent", line: { width: 0.5, color: KT[k] || undefined }, fillcolor: KT[k] || undefined })),
      layout: { yaxis: { title: { text: yTitle }, ticksuffix: " %", tickformat: ",.0f" }, xaxis: { nticks: 6, tickangle: 0 }, margin: { t: 30 } },
    };
  }

  /* ---------------- demo data (synthetic, mirrors the data dictionary) ---------------- */
  function demo() {
    let seed = 2024;
    const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const gauss = () => { let u = 0, v = 0; while (u === 0) u = rnd(); while (v === 0) v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
    const monate = []; for (let y = 2024; y <= 2025; y++) for (let m = 1; m <= 12; m++) monate.push(String(m).padStart(2, "0") + "/" + y);
    const M12 = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"];
    const TEMP = [2.1, 3.4, 6.2, 10.8, 14.9, 18.2, 19.8, 19.1, 15.4, 11.2, 6.1, 3.2];
    const base = { Gewerbe: 210000, Industrie: 780000, Kommunal: 92000 };
    const amp = { Gewerbe: 0.12, Industrie: 0.06, Kommunal: 0.22 };
    const season = (k, i) => 1 + amp[k] * Math.cos(((i % 12) / 12) * 2 * Math.PI);

    const portfolioIst = monate.map((_, i) => Math.round(14500 * (1 + 0.14 * Math.cos(((i % 12) / 12) * 2 * Math.PI)) * (1 + gauss() * 0.02)));
    const portfolioPrognose = portfolioIst.map((v) => Math.round(v * (1 + gauss() * 0.02)));
    const lo = portfolioPrognose.map((v) => Math.round(v * 0.955)), hi = portfolioPrognose.map((v) => Math.round(v * 1.045));

    const groups = {}, scatter = {}, seasonSeries = {};
    Object.keys(base).forEach((k) => {
      groups[k] = []; scatter[k] = { x: [], y: [] };
      for (let z = 0; z < 120; z++) for (let i = 0; i < 12; i++) {
        const v = Math.round(base[k] * season(k, i) * Math.exp(gauss() * 0.28));
        groups[k].push(v);
        if (z < 30) { scatter[k].x.push(+(TEMP[i] + gauss() * 1.4).toFixed(1)); scatter[k].y.push(v); }
      }
      seasonSeries[k] = M12.map((_, i) => Math.round(base[k] * season(k, i)));
    });

    const heat = Object.keys(base).map((k) => M12.map((_, i) => Math.round(base[k] * season(k, i) / 1000)));

    const labels = ["verbrauch_kwh", "vertragsleistung_kw", "vormonat_verbrauch_kwh", "letzte_3_monate_kwh", "vorjahr_monat_kwh", "heiztage", "mittlere_temperatur_c", "arbeitstage", "produktionsplan_index"];
    const corr = [
      [1, 0.81, 0.93, 0.95, 0.9, 0.31, -0.29, 0.12, 0.44],
      [0.81, 1, 0.8, 0.82, 0.79, 0.05, -0.04, 0.02, 0.21],
      [0.93, 0.8, 1, 0.96, 0.88, 0.28, -0.26, 0.1, 0.4],
      [0.95, 0.82, 0.96, 1, 0.9, 0.3, -0.28, 0.11, 0.42],
      [0.9, 0.79, 0.88, 0.9, 1, 0.34, -0.32, 0.09, 0.38],
      [0.31, 0.05, 0.28, 0.3, 0.34, 1, -0.97, -0.08, 0.02],
      [-0.29, -0.04, -0.26, -0.28, -0.32, -0.97, 1, 0.07, -0.01],
      [0.12, 0.02, 0.1, 0.11, 0.09, -0.08, 0.07, 1, 0.15],
      [0.44, 0.21, 0.4, 0.42, 0.38, 0.02, -0.01, 0.15, 1],
    ];

    const residuen = Array.from({ length: 700 }, () => Math.round(gauss() * 9000 + (rnd() < 0.06 ? (rnd() < 0.5 ? -1 : 1) * (25000 + rnd() * 30000) : 0)));
    const schwelle = 18000;
    const zaehlerIst = Array.from({ length: 220 }, () => Math.round(Math.exp(11 + gauss() * 1.1)));
    const zaehlerPrognose = zaehlerIst.map((v) => Math.round(v * (1 + gauss() * 0.08)));
    const anomalie = zaehlerIst.map((v, i) => Math.abs(v - zaehlerPrognose[i]) / zaehlerPrognose[i] > 0.18);

    const residSerie = monate.map((_, i) => Math.round(gauss() * 6000 + (i === 9 || i === 20 ? 24000 : 0)));
    const anomalienMonat = { Gewerbe: monate.map(() => 18 + Math.round(rnd() * 22)), Industrie: monate.map(() => 22 + Math.round(rnd() * 30)), Kommunal: monate.map(() => 6 + Math.round(rnd() * 14)) };

    return {
      monate, M12, TEMP, portfolioIst, portfolioPrognose, lo, hi,
      anomalien: { x: [monate[9], monate[20]], y: [portfolioIst[9], portfolioIst[20]] },
      groups, scatter, seasonSeries, heat, labels, corr, residuen, schwelle, residSerie,
      zaehlerIst, zaehlerPrognose, anomalie, anomalienMonat,
      features: ["letzte_3_monate_durchschnitt_kwh", "vorjahr_monat_verbrauch_kwh", "vertragsleistung_kw", "heiztage", "produktionsplan_index", "arbeitstage", "mittlere_temperatur_c", "wartung_aktiv"],
      importance: [0.312, 0.208, 0.147, 0.121, 0.094, 0.058, 0.041, 0.019],
      qcols: ["verbrauch_kwh (MWh-Text)", "vorjahr_monat_verbrauch_kwh", "vormonat_verbrauch_kwh", "kundentyp (Schreibvarianten)", "zaehler_id (Duplikate)", "verbrauch_kwh (negativ)", "monat (Format)"],
      qpct: [2.5, 50.0, 4.2, 1.1, 0.23, 0.07, 100],
      topLabels: ["ZW-02044", "ZW-05316", "ZW-04412", "ZW-06021", "ZW-03771", "ZW-05540", "ZW-01187", "ZW-00145"],
      topValues: [3120400, 2418700, 1284500, 742900, 631200, 268800, 212340, 198400],
      shareSeries: { Gewerbe: monate.map((_, i) => 210 * 120 * season("Gewerbe", i)), Industrie: monate.map((_, i) => 780 * 120 * season("Industrie", i)), Kommunal: monate.map((_, i) => 92 * 120 * season("Kommunal", i)) },
    };
  }

  /* Gallery manifest — id, German title, one-line "when", builder fed with demo data */
  const GALLERY = [
    { id: "zeitreihe", title: "Zeitreihe Prognose vs. Ist", when: "Portfolio oder ein Zähler über die Zeit; Band = Konfidenz, rote Marker = Anomalien", build: (d) => timeseriesForecast({ x: d.monate, ist: d.portfolioIst, prognose: d.portfolioPrognose, lo: d.lo, hi: d.hi, anomalien: d.anomalien, yTitle: "Verbrauch (MWh)" }) },
    { id: "saisonalitaet", title: "Saisonalität je Kundentyp", when: "Monatsmittel Jan–Dez; zeigt Heiz- und Produktionsabhängigkeit", build: (d) => seasonality({ monate: d.M12, series: d.seasonSeries }) },
    { id: "histogramm", title: "Verteilung des Verbrauchs", when: "Überlagerte, halbtransparente Histogramme je Kundentyp; log-Achse für schiefe Verteilungen", build: (d) => histogram({ groups: d.groups, logX: true }) },
    { id: "boxplot", title: "Boxplot je Kundentyp", when: "Streuung und Ausreißer kompakt vergleichen", build: (d) => boxplot({ groups: d.groups }) },
    { id: "scatter", title: "Temperatur vs. Verbrauch", when: "Wetterabhängigkeit je Kundentyp mit OLS-Trendlinie", build: (d) => scatterTrend({ groups: d.scatter }) },
    { id: "heatmap", title: "Heatmap Monat × Kundentyp", when: "Sequentielle Navy-Skala; Verbrauch in MWh", build: (d) => heatmap({ x: d.M12, y: Object.keys(d.seasonSeries), z: d.heat, zTitle: "MWh" }) },
    { id: "korrelation", title: "Korrelationsmatrix", when: "Divergente Skala, Mitte 0; Werte im Hover, showText:true ab ~700 px Breite", build: (d) => correlation({ labels: d.labels, z: d.corr }) },
    { id: "residuen-verteilung", title: "Residuen-Verteilung", when: "Histogramm der Residuen mit ±Schwellwert (95. Perzentil)", build: (d) => residualHist({ residuen: d.residuen, schwelle: d.schwelle }) },
    { id: "residuen-zeit", title: "Residuen über Zeit", when: "Balken je Monat, Überschreitungen rot", build: (d) => residualBars({ x: d.monate, residuen: d.residSerie, schwelle: 18000 }) },
    { id: "parity", title: "Parity-Plot Prognose vs. Ist", when: "Ein Punkt pro Zähler; Abstand zur Diagonale = Fehler, rot = Anomalie", build: (d) => parity({ ist: d.zaehlerIst, prognose: d.zaehlerPrognose, anomalie: d.anomalie }) },
    { id: "feature-importance", title: "Feature Importance", when: "Sortierte horizontale Balken mit Wert-Labels", build: (d) => featureImportance({ features: d.features, values: d.importance }) },
    { id: "anomalien-monat", title: "Anomalien je Monat", when: "Gestapelt nach Kundentyp; operative Plausibilität prüfen", build: (d) => anomalyStack({ x: d.monate, series: d.anomalienMonat }) },
    { id: "datenqualitaet", title: "Datenqualität je Spalte", when: "Anteil fehlerhafter Werte; ≥ 5 % rot, ≥ 1 % amber", build: (d) => missingValues({ columns: d.qcols, pct: d.qpct }) },
    { id: "top-n", title: "Top-Zähler nach Verbrauch", when: "Rangliste; Wert als Label außen", build: (d) => topN({ labels: d.topLabels, values: d.topValues }) },
    { id: "anteile", title: "Anteil Kundentyp über Zeit", when: "100 %-gestapelte Fläche; Strukturverschiebung im Portfolio", build: (d) => shareArea({ x: d.monate, series: d.shareSeries }) },
  ];

  global.SWW = { C, QUALITATIVE, KT, ROLE, SEQ, DIV, FONT, LABEL, layout, render, demo, GALLERY,
    timeseriesForecast, seasonality, histogram, boxplot, scatterTrend, heatmap, correlation, residualHist, residualBars, featureImportance, missingValues, parity, anomalyStack, topN, shareArea };
})(window);
