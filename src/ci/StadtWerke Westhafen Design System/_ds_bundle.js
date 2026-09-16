/* @ds-bundle: {"format":4,"namespace":"StadtWerkeWesthafenDesignSystem_acd94c","components":[{"name":"SEVERITY","sourcePath":"components/core/Badge.jsx"},{"name":"Badge","sourcePath":"components/core/Badge.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"ICON_BASE","sourcePath":"components/core/Icon.jsx"},{"name":"DOMAIN_ICONS","sourcePath":"components/core/Icon.jsx"},{"name":"Icon","sourcePath":"components/core/Icon.jsx"},{"name":"IconButton","sourcePath":"components/core/IconButton.jsx"},{"name":"KUNDENTYP_COLOR","sourcePath":"components/core/Tag.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"},{"name":"DataTable","sourcePath":"components/data/DataTable.jsx"},{"name":"KpiTile","sourcePath":"components/data/KpiTile.jsx"},{"name":"Sparkline","sourcePath":"components/data/Sparkline.jsx"},{"name":"StatusDot","sourcePath":"components/data/StatusDot.jsx"},{"name":"Alert","sourcePath":"components/feedback/Alert.jsx"},{"name":"Dialog","sourcePath":"components/feedback/Dialog.jsx"},{"name":"EmptyState","sourcePath":"components/feedback/EmptyState.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"},{"name":"Card","sourcePath":"components/layout/Card.jsx"},{"name":"PageHeader","sourcePath":"components/layout/PageHeader.jsx"},{"name":"SidebarNav","sourcePath":"components/layout/SidebarNav.jsx"},{"name":"Tabs","sourcePath":"components/layout/Tabs.jsx"}],"sourceHashes":{"assets/plotly/sww_plotly.js":"cdf30a0d7bf8","components/core/Badge.jsx":"4c2de7eeda99","components/core/Button.jsx":"68a7f850fcd6","components/core/Icon.jsx":"1291cdb6fd7b","components/core/IconButton.jsx":"6b0c8794f9d3","components/core/Tag.jsx":"be7966a5f48c","components/data/DataTable.jsx":"21a391e86348","components/data/KpiTile.jsx":"2c6241cf13b9","components/data/Sparkline.jsx":"a6887d9546f5","components/data/StatusDot.jsx":"27b4609ea30a","components/feedback/Alert.jsx":"dc48987bd1ff","components/feedback/Dialog.jsx":"08600be23afb","components/feedback/EmptyState.jsx":"68abfa5b43df","components/forms/Checkbox.jsx":"0f18b097ac47","components/forms/Input.jsx":"9ccca758c144","components/forms/Select.jsx":"3eaf8a2ff9ef","components/forms/Switch.jsx":"87abbe688c5e","components/layout/Card.jsx":"b463efb7062a","components/layout/PageHeader.jsx":"97b143cdb20c","components/layout/SidebarNav.jsx":"781acf23e9d9","components/layout/Tabs.jsx":"0a9ec428773f","ui_kits/energie-cockpit/AnomalienScreen.jsx":"6b6b12a3708d","ui_kits/energie-cockpit/BeschaffungScreen.jsx":"8f43d46d7cb4","ui_kits/energie-cockpit/Chart.jsx":"6561771b746d","ui_kits/energie-cockpit/DatenqualitaetScreen.jsx":"8b1454f74349","ui_kits/energie-cockpit/Shell.jsx":"a1888cb81ba5","ui_kits/energie-cockpit/UebersichtScreen.jsx":"f45237fbff63","ui_kits/energie-cockpit/ZaehlerDetailScreen.jsx":"fb49b77c71c6","ui_kits/energie-cockpit/data.js":"8845fd275adc"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.StadtWerkeWesthafenDesignSystem_acd94c = window.StadtWerkeWesthafenDesignSystem_acd94c || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// assets/plotly/sww_plotly.js
try { (() => {
/* SWW Plotly helpers — JavaScript twin of assets/plotly/sww_eda.py.
   Every builder returns { data, layout }. Render with SWW.render(el, spec).
   Colour roles are identical to tokens/charts.css. */
(function (global) {
  const C = {
    navy: "#084878",
    navy900: "#04263F",
    teal: "#0080A0",
    cyan: "#0090C8",
    green: "#58A858",
    amber: "#C77E11",
    red: "#B3261E",
    ink: "#141A21",
    grey600: "#4E5A68",
    grey500: "#6B7887",
    grey400: "#8C99A7",
    grey300: "#B4BFCB",
    grey100: "#E4E9EF",
    grey50: "#F1F4F7"
  };
  const QUALITATIVE = [C.navy, C.teal, C.green, C.cyan, C.amber, "#6CC0D2", C.grey600, C.red];
  const KT = {
    Gewerbe: C.teal,
    Industrie: C.navy,
    Kommunal: C.green
  };
  const ROLE = {
    ist: C.navy,
    prognose: C.cyan,
    band: "rgba(0,144,200,0.16)",
    residuum: C.teal,
    schwellwert: C.amber,
    anomalie: C.red
  };
  const SEQ = ["#E4EFF7", "#BBD7EA", "#7FB4D8", "#3E90C4", "#0F6FAE", "#084878", "#04263F"];
  const DIV = ["#005E77", "#1C9BB8", "#B2DEE7", "#F1F4F7", "#F3C6C1", "#D2564B", "#951C15"];
  const scale = arr => arr.map((c, i) => [i / (arr.length - 1), c]);
  const FONT = "IBM Plex Sans, Segoe UI, sans-serif";
  const LABEL = FONT; // one family for every axis, label and hover — never monospace in charts

  const merge = (a, b) => {
    const o = {
      ...a
    };
    Object.keys(b || {}).forEach(k => {
      o[k] = b[k] && typeof b[k] === "object" && !Array.isArray(b[k]) && o[k] && typeof o[k] === "object" && !Array.isArray(o[k]) ? merge(o[k], b[k]) : b[k];
    });
    return o;
  };
  const axis = () => ({
    showgrid: false,
    zeroline: false,
    showline: true,
    linecolor: C.grey100,
    ticks: "outside",
    ticklen: 4,
    tickcolor: C.grey100,
    tickfont: {
      family: LABEL,
      size: 11,
      color: C.grey500
    },
    title: {
      font: {
        family: FONT,
        size: 12,
        color: C.grey500
      },
      standoff: 10
    }
  });
  function layout(over) {
    const base = {
      font: {
        family: FONT,
        size: 12,
        color: C.ink
      },
      paper_bgcolor: "#fff",
      plot_bgcolor: "#fff",
      separators: ",.",
      colorway: QUALITATIVE,
      margin: {
        l: 76,
        r: 18,
        t: 14,
        b: 40
      },
      hovermode: "x unified",
      bargap: 0.36,
      barcornerradius: 4,
      hoverlabel: {
        bgcolor: "#fff",
        bordercolor: C.grey100,
        font: {
          family: LABEL,
          size: 12,
          color: C.ink
        },
        align: "left"
      },
      legend: {
        orientation: "h",
        yanchor: "bottom",
        y: 1.02,
        xanchor: "left",
        x: 0,
        font: {
          size: 12,
          color: C.grey500
        },
        bgcolor: "rgba(0,0,0,0)"
      },
      xaxis: axis(),
      yaxis: merge(axis(), {
        showgrid: true,
        gridcolor: C.grey100,
        showline: false,
        tickformat: ",d",
        separatethousands: true
      })
    };
    return merge(base, over || {});
  }
  function render(el, spec, config) {
    if (!global.Plotly) return;
    const cfg = {
      displayModeBar: false,
      responsive: false,
      ...(config || {})
    };
    const draw = () => {
      const w = el.clientWidth || el.parentElement && el.parentElement.clientWidth || 600;
      const h = el.clientHeight || parseInt(getComputedStyle(el).height, 10) || 280;
      return global.Plotly.react(el, spec.data, layout(merge(spec.layout || {}, {
        width: w,
        height: h,
        autosize: false
      })), cfg);
    };
    if (!el.__swwResize && typeof ResizeObserver !== "undefined") {
      let raf = 0;
      el.__swwResize = new ResizeObserver(() => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(draw);
      });
      el.__swwResize.observe(el);
    }
    return draw();
  }
  const num = n => new Intl.NumberFormat("de-DE").format(Math.round(n));
  const ols = (x, y) => {
    const n = x.length,
      mx = x.reduce((a, b) => a + b, 0) / n,
      my = y.reduce((a, b) => a + b, 0) / n;
    let sxy = 0,
      sxx = 0;
    for (let i = 0; i < n; i++) {
      sxy += (x[i] - mx) * (y[i] - my);
      sxx += (x[i] - mx) ** 2;
    }
    const b = sxy / (sxx || 1),
      a = my - b * mx;
    return {
      a,
      b
    };
  };

  /* ---------------- builders ---------------- */

  // 01 Zeitreihe: Ist vs Prognose mit Konfidenzband und Anomalie-Markern
  function timeseriesForecast({
    x,
    ist,
    prognose,
    lo,
    hi,
    anomalien,
    yTitle = "Verbrauch (kWh)"
  }) {
    const data = [];
    if (lo && hi) data.push({
      x: x.concat(x.slice().reverse()),
      y: hi.concat(lo.slice().reverse()),
      fill: "toself",
      fillcolor: ROLE.band,
      line: {
        width: 0
      },
      hoverinfo: "skip",
      name: "Konfidenzband",
      type: "scatter"
    });
    data.push({
      x,
      y: ist,
      name: "Ist",
      mode: "lines+markers",
      type: "scatter",
      line: {
        color: ROLE.ist,
        width: 2
      },
      marker: {
        size: 5,
        color: ROLE.ist
      }
    });
    if (prognose) data.push({
      x,
      y: prognose,
      name: "Prognose",
      mode: "lines",
      type: "scatter",
      line: {
        color: ROLE.prognose,
        width: 2,
        dash: "4,2"
      }
    });
    if (anomalien) data.push({
      x: anomalien.x,
      y: anomalien.y,
      name: "Anomalie",
      mode: "markers",
      type: "scatter",
      marker: {
        size: 9,
        color: ROLE.anomalie,
        line: {
          width: 1.5,
          color: "#fff"
        }
      }
    });
    return {
      data,
      layout: {
        yaxis: {
          title: {
            text: yTitle
          }
        },
        xaxis: {
          nticks: 6,
          tickangle: 0
        },
        margin: {
          t: 30
        }
      }
    };
  }

  // 02 Saisonalität: Monatsmittel je Kundentyp
  function seasonality({
    monate,
    series,
    yTitle = "Ø Verbrauch (kWh)"
  }) {
    const data = Object.keys(series).map(k => ({
      x: monate,
      y: series[k],
      name: k,
      mode: "lines+markers",
      type: "scatter",
      line: {
        color: KT[k] || undefined,
        width: 2
      },
      marker: {
        size: 5
      }
    }));
    return {
      data,
      layout: {
        yaxis: {
          title: {
            text: yTitle
          }
        },
        margin: {
          t: 30
        }
      }
    };
  }

  // 03 Verteilung: überlagerte Histogramme je Kundentyp
  // logX: log-Skala für schiefe Verteilungen (Verbrauch über drei Größenordnungen)
  function histogram({
    groups,
    xTitle = "Verbrauch (kWh)",
    nbins = 40,
    logX = false
  }) {
    const data = Object.keys(groups).map(k => ({
      x: logX ? groups[k].map(v => Math.log10(Math.max(v, 1))) : groups[k],
      name: k,
      type: "histogram",
      nbinsx: nbins,
      opacity: 0.62,
      marker: {
        color: KT[k] || undefined
      }
    }));
    const xaxis = logX ? {
      title: {
        text: xTitle
      },
      tickvals: [3, 3.5, 4, 4.5, 5, 5.5, 6],
      ticktext: ["1.000", "3.000", "10.000", "30.000", "100.000", "300.000", "1 Mio."]
    } : {
      title: {
        text: xTitle
      },
      tickformat: ",d"
    };
    return {
      data,
      layout: {
        barmode: "overlay",
        bargap: 0.3,
        xaxis,
        yaxis: {
          title: {
            text: "Anzahl Zähler"
          }
        },
        hovermode: "closest",
        margin: {
          t: 30
        }
      }
    };
  }

  // 04 Boxplot je Kundentyp
  function boxplot({
    groups,
    yTitle = "Verbrauch (kWh)"
  }) {
    const data = Object.keys(groups).map(k => ({
      y: groups[k],
      name: k,
      type: "box",
      marker: {
        color: KT[k] || undefined,
        size: 3
      },
      line: {
        width: 1.5
      },
      boxpoints: "outliers",
      fillcolor: "rgba(255,255,255,0)"
    }));
    return {
      data,
      layout: {
        showlegend: false,
        yaxis: {
          title: {
            text: yTitle
          }
        },
        hovermode: "closest",
        xaxis: {
          showline: false
        }
      }
    };
  }

  // 05 Scatter mit Trendlinie je Gruppe (z. B. Temperatur vs Verbrauch)
  function scatterTrend({
    groups,
    xTitle = "Mitteltemperatur (°C)",
    yTitle = "Verbrauch (kWh)"
  }) {
    const data = [];
    Object.keys(groups).forEach(k => {
      const g = groups[k];
      data.push({
        x: g.x,
        y: g.y,
        name: k,
        mode: "markers",
        type: "scatter",
        marker: {
          size: 6,
          color: KT[k] || undefined,
          opacity: 0.75
        }
      });
      const {
        a,
        b
      } = ols(g.x, g.y);
      const xs = [Math.min(...g.x), Math.max(...g.x)];
      data.push({
        x: xs,
        y: xs.map(v => a + b * v),
        mode: "lines",
        type: "scatter",
        showlegend: false,
        hoverinfo: "skip",
        line: {
          color: KT[k] || C.grey400,
          width: 1.5,
          dash: "3,3"
        }
      });
    });
    return {
      data,
      layout: {
        hovermode: "closest",
        xaxis: {
          title: {
            text: xTitle
          },
          showgrid: true,
          gridcolor: C.grey100
        },
        yaxis: {
          title: {
            text: yTitle
          }
        },
        margin: {
          t: 30
        }
      }
    };
  }

  // 06 Heatmap (sequentiell): z. B. Monat × Kundentyp
  function heatmap({
    x,
    y,
    z,
    zTitle = "kWh"
  }) {
    return {
      data: [{
        x,
        y,
        z,
        type: "heatmap",
        colorscale: scale(SEQ),
        colorbar: {
          title: {
            text: zTitle,
            font: {
              size: 11,
              color: C.grey500
            }
          },
          thickness: 10,
          len: 0.8,
          outlinewidth: 0,
          tickfont: {
            family: LABEL,
            size: 10,
            color: C.grey500
          },
          tickformat: ",d"
        },
        hovertemplate: "%{y} · %{x}<br>%{z:,d} " + zTitle + "<extra></extra>",
        xgap: 2,
        ygap: 2
      }],
      layout: {
        hovermode: "closest",
        xaxis: {
          showline: false,
          ticks: ""
        },
        yaxis: {
          showgrid: false,
          ticks: "",
          tickformat: "",
          automargin: true
        },
        margin: {
          l: 20,
          r: 10
        }
      }
    };
  }

  // 07 Korrelationsmatrix (divergent, Mitte 0)
  function correlation({
    labels,
    z,
    showText = false
  }) {
    const text = z.map(r => r.map(v => v == null ? "" : v.toFixed(2).replace(".", ",")));
    return {
      data: [{
        x: labels,
        y: labels,
        z,
        type: "heatmap",
        colorscale: scale(DIV),
        zmin: -1,
        zmax: 1,
        zmid: 0,
        text,
        texttemplate: showText ? "%{text}" : undefined,
        textfont: {
          family: LABEL,
          size: 10
        },
        colorbar: {
          thickness: 10,
          len: 0.8,
          outlinewidth: 0,
          tickfont: {
            family: LABEL,
            size: 10,
            color: C.grey500
          }
        },
        hovertemplate: "%{y} × %{x}<br>r = %{z:.2f}<extra></extra>",
        xgap: 2,
        ygap: 2
      }],
      layout: {
        hovermode: "closest",
        xaxis: {
          showline: false,
          ticks: "",
          tickangle: -35,
          automargin: true,
          tickfont: {
            size: 10
          }
        },
        yaxis: {
          showgrid: false,
          ticks: "",
          tickformat: "",
          autorange: "reversed",
          automargin: true,
          tickfont: {
            size: 10
          }
        },
        margin: {
          l: 20,
          b: 20,
          r: 10
        }
      }
    };
  }

  // 08 Residuen-Verteilung mit symmetrischem Schwellwert
  function residualHist({
    residuen,
    schwelle,
    xTitle = "Residuum (kWh)"
  }) {
    return {
      data: [{
        x: residuen,
        type: "histogram",
        nbinsx: 40,
        marker: {
          color: ROLE.residuum
        },
        name: "Residuen"
      }],
      layout: {
        showlegend: false,
        hovermode: "closest",
        xaxis: {
          title: {
            text: xTitle
          },
          tickformat: ",d",
          zeroline: true,
          zerolinecolor: C.grey300
        },
        yaxis: {
          title: {
            text: "Anzahl"
          }
        },
        shapes: [-1, 1].map(s => ({
          type: "line",
          x0: s * schwelle,
          x1: s * schwelle,
          y0: 0,
          y1: 1,
          yref: "paper",
          line: {
            color: ROLE.schwellwert,
            width: 1,
            dash: "3,3"
          }
        })),
        annotations: [{
          x: schwelle,
          y: 1,
          yref: "paper",
          text: "Schwellwert ±" + num(schwelle),
          showarrow: false,
          xanchor: "left",
          yanchor: "top",
          font: {
            size: 11,
            color: ROLE.schwellwert
          }
        }]
      }
    };
  }

  // 09 Residuen über Zeit, Überschreitungen rot
  function residualBars({
    x,
    residuen,
    schwelle,
    yTitle = "Residuum (kWh)"
  }) {
    return {
      data: [{
        type: "bar",
        x,
        y: residuen,
        name: "Residuum",
        marker: {
          color: residuen.map(r => Math.abs(r) > schwelle ? ROLE.anomalie : ROLE.residuum)
        }
      }],
      layout: {
        showlegend: false,
        yaxis: {
          title: {
            text: yTitle
          },
          zeroline: true,
          zerolinecolor: C.grey300
        },
        xaxis: {
          nticks: 6,
          tickangle: 0
        },
        shapes: [-1, 1].map(s => ({
          type: "line",
          xref: "paper",
          x0: 0,
          x1: 1,
          y0: s * schwelle,
          y1: s * schwelle,
          line: {
            color: ROLE.schwellwert,
            width: 1,
            dash: "3,3"
          }
        }))
      }
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
  function featureImportance({
    features,
    values,
    xTitle = "Anteil"
  }) {
    const idx = values.map((_, i) => i).sort((a, b) => values[a] - values[b]);
    return {
      data: [{
        type: "bar",
        orientation: "h",
        y: idx.map(i => wrapLabel(features[i])),
        x: idx.map(i => values[i]),
        marker: {
          color: ROLE.ist
        },
        text: idx.map(i => values[i].toFixed(3).replace(".", ",")),
        textposition: "outside",
        textfont: {
          family: LABEL,
          size: 11,
          color: C.grey600
        },
        cliponaxis: false
      }],
      layout: {
        showlegend: false,
        hovermode: "closest",
        xaxis: {
          title: {
            text: xTitle
          },
          showgrid: true,
          gridcolor: C.grey100,
          showline: false,
          tickformat: ",.2f"
        },
        yaxis: {
          showgrid: false,
          tickformat: "",
          automargin: true,
          tickfont: {
            family: LABEL,
            size: 11,
            color: C.grey600
          }
        },
        margin: {
          l: 20,
          r: 50
        }
      }
    };
  }

  // 11 Datenqualität: fehlende / fehlerhafte Werte je Spalte (%)
  function missingValues({
    columns,
    pct,
    title = "Anteil fehlerhaft/fehlend (%)"
  }) {
    return {
      data: [{
        type: "bar",
        orientation: "h",
        y: columns.slice().reverse().map(c => wrapLabel(c)),
        x: pct.slice().reverse(),
        marker: {
          color: pct.slice().reverse().map(p => p >= 5 ? ROLE.anomalie : p >= 1 ? ROLE.schwellwert : C.grey300)
        },
        text: pct.slice().reverse().map(p => p.toFixed(1).replace(".", ",") + " %"),
        textposition: "outside",
        textfont: {
          family: LABEL,
          size: 11,
          color: C.grey600
        },
        cliponaxis: false
      }],
      layout: {
        showlegend: false,
        hovermode: "closest",
        xaxis: {
          title: {
            text: title
          },
          showgrid: true,
          gridcolor: C.grey100,
          showline: false,
          tickformat: ",.0f",
          ticksuffix: " %"
        },
        yaxis: {
          showgrid: false,
          tickformat: "",
          automargin: true,
          tickfont: {
            family: LABEL,
            size: 11,
            color: C.grey600
          }
        },
        margin: {
          l: 20,
          r: 60
        }
      }
    };
  }

  // 12 Parity-Plot: Prognose vs Ist mit 45°-Linie
  function parity({
    ist,
    prognose,
    anomalie,
    xTitle = "Prognose (kWh)",
    yTitle = "Ist (kWh)"
  }) {
    const mn = Math.min(...ist, ...prognose),
      mx = Math.max(...ist, ...prognose);
    const colors = (anomalie || ist.map(() => false)).map(a => a ? ROLE.anomalie : ROLE.ist);
    return {
      data: [{
        x: [mn, mx],
        y: [mn, mx],
        mode: "lines",
        type: "scatter",
        name: "Ist = Prognose",
        hoverinfo: "skip",
        line: {
          color: C.grey300,
          width: 1,
          dash: "4,4"
        }
      }, {
        x: prognose,
        y: ist,
        mode: "markers",
        type: "scatter",
        name: "Zähler",
        marker: {
          size: 6,
          color: colors,
          opacity: 0.8
        }
      }],
      layout: {
        hovermode: "closest",
        xaxis: {
          title: {
            text: xTitle
          },
          tickformat: ",d",
          showgrid: true,
          gridcolor: C.grey100
        },
        yaxis: {
          title: {
            text: yTitle
          }
        },
        showlegend: false
      }
    };
  }

  // 13 Anomalien je Monat, gestapelt nach Kundentyp
  function anomalyStack({
    x,
    series
  }) {
    return {
      data: Object.keys(series).map(k => ({
        type: "bar",
        name: k,
        x,
        y: series[k],
        marker: {
          color: KT[k] || undefined
        }
      })),
      layout: {
        barmode: "stack",
        yaxis: {
          title: {
            text: "Anomalien"
          }
        },
        xaxis: {
          nticks: 6,
          tickangle: 0
        },
        margin: {
          t: 30
        }
      }
    };
  }

  // 14 Top-N Rangliste (z. B. Zähler nach Verbrauch)
  function topN({
    labels,
    values,
    xTitle = "Verbrauch (kWh)"
  }) {
    const idx = values.map((_, i) => i).sort((a, b) => values[a] - values[b]);
    return {
      data: [{
        type: "bar",
        orientation: "h",
        y: idx.map(i => labels[i]),
        x: idx.map(i => values[i]),
        marker: {
          color: ROLE.ist
        },
        text: idx.map(i => num(values[i])),
        textposition: "outside",
        textfont: {
          family: LABEL,
          size: 11,
          color: C.grey600
        },
        cliponaxis: false
      }],
      layout: {
        showlegend: false,
        hovermode: "closest",
        xaxis: {
          title: {
            text: xTitle
          },
          showgrid: true,
          gridcolor: C.grey100,
          showline: false,
          tickformat: ",d"
        },
        yaxis: {
          showgrid: false,
          tickformat: "",
          automargin: true,
          tickfont: {
            family: LABEL,
            size: 11,
            color: C.grey600
          }
        },
        margin: {
          l: 20,
          r: 70
        }
      }
    };
  }

  // 15 Anteile über Zeit (gestapelte Fläche, 100 %)
  function shareArea({
    x,
    series,
    yTitle = "Anteil"
  }) {
    return {
      data: Object.keys(series).map(k => ({
        x,
        y: series[k],
        name: k,
        type: "scatter",
        mode: "lines",
        stackgroup: "one",
        groupnorm: "percent",
        line: {
          width: 0.5,
          color: KT[k] || undefined
        },
        fillcolor: KT[k] || undefined
      })),
      layout: {
        yaxis: {
          title: {
            text: yTitle
          },
          ticksuffix: " %",
          tickformat: ",.0f"
        },
        xaxis: {
          nticks: 6,
          tickangle: 0
        },
        margin: {
          t: 30
        }
      }
    };
  }

  /* ---------------- demo data (synthetic, mirrors the data dictionary) ---------------- */
  function demo() {
    let seed = 2024;
    const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const gauss = () => {
      let u = 0,
        v = 0;
      while (u === 0) u = rnd();
      while (v === 0) v = rnd();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    };
    const monate = [];
    for (let y = 2024; y <= 2025; y++) for (let m = 1; m <= 12; m++) monate.push(String(m).padStart(2, "0") + "/" + y);
    const M12 = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"];
    const TEMP = [2.1, 3.4, 6.2, 10.8, 14.9, 18.2, 19.8, 19.1, 15.4, 11.2, 6.1, 3.2];
    const base = {
      Gewerbe: 210000,
      Industrie: 780000,
      Kommunal: 92000
    };
    const amp = {
      Gewerbe: 0.12,
      Industrie: 0.06,
      Kommunal: 0.22
    };
    const season = (k, i) => 1 + amp[k] * Math.cos(i % 12 / 12 * 2 * Math.PI);
    const portfolioIst = monate.map((_, i) => Math.round(14500 * (1 + 0.14 * Math.cos(i % 12 / 12 * 2 * Math.PI)) * (1 + gauss() * 0.02)));
    const portfolioPrognose = portfolioIst.map(v => Math.round(v * (1 + gauss() * 0.02)));
    const lo = portfolioPrognose.map(v => Math.round(v * 0.955)),
      hi = portfolioPrognose.map(v => Math.round(v * 1.045));
    const groups = {},
      scatter = {},
      seasonSeries = {};
    Object.keys(base).forEach(k => {
      groups[k] = [];
      scatter[k] = {
        x: [],
        y: []
      };
      for (let z = 0; z < 120; z++) for (let i = 0; i < 12; i++) {
        const v = Math.round(base[k] * season(k, i) * Math.exp(gauss() * 0.28));
        groups[k].push(v);
        if (z < 30) {
          scatter[k].x.push(+(TEMP[i] + gauss() * 1.4).toFixed(1));
          scatter[k].y.push(v);
        }
      }
      seasonSeries[k] = M12.map((_, i) => Math.round(base[k] * season(k, i)));
    });
    const heat = Object.keys(base).map(k => M12.map((_, i) => Math.round(base[k] * season(k, i) / 1000)));
    const labels = ["verbrauch_kwh", "vertragsleistung_kw", "vormonat_verbrauch_kwh", "letzte_3_monate_kwh", "vorjahr_monat_kwh", "heiztage", "mittlere_temperatur_c", "arbeitstage", "produktionsplan_index"];
    const corr = [[1, 0.81, 0.93, 0.95, 0.9, 0.31, -0.29, 0.12, 0.44], [0.81, 1, 0.8, 0.82, 0.79, 0.05, -0.04, 0.02, 0.21], [0.93, 0.8, 1, 0.96, 0.88, 0.28, -0.26, 0.1, 0.4], [0.95, 0.82, 0.96, 1, 0.9, 0.3, -0.28, 0.11, 0.42], [0.9, 0.79, 0.88, 0.9, 1, 0.34, -0.32, 0.09, 0.38], [0.31, 0.05, 0.28, 0.3, 0.34, 1, -0.97, -0.08, 0.02], [-0.29, -0.04, -0.26, -0.28, -0.32, -0.97, 1, 0.07, -0.01], [0.12, 0.02, 0.1, 0.11, 0.09, -0.08, 0.07, 1, 0.15], [0.44, 0.21, 0.4, 0.42, 0.38, 0.02, -0.01, 0.15, 1]];
    const residuen = Array.from({
      length: 700
    }, () => Math.round(gauss() * 9000 + (rnd() < 0.06 ? (rnd() < 0.5 ? -1 : 1) * (25000 + rnd() * 30000) : 0)));
    const schwelle = 18000;
    const zaehlerIst = Array.from({
      length: 220
    }, () => Math.round(Math.exp(11 + gauss() * 1.1)));
    const zaehlerPrognose = zaehlerIst.map(v => Math.round(v * (1 + gauss() * 0.08)));
    const anomalie = zaehlerIst.map((v, i) => Math.abs(v - zaehlerPrognose[i]) / zaehlerPrognose[i] > 0.18);
    const residSerie = monate.map((_, i) => Math.round(gauss() * 6000 + (i === 9 || i === 20 ? 24000 : 0)));
    const anomalienMonat = {
      Gewerbe: monate.map(() => 18 + Math.round(rnd() * 22)),
      Industrie: monate.map(() => 22 + Math.round(rnd() * 30)),
      Kommunal: monate.map(() => 6 + Math.round(rnd() * 14))
    };
    return {
      monate,
      M12,
      TEMP,
      portfolioIst,
      portfolioPrognose,
      lo,
      hi,
      anomalien: {
        x: [monate[9], monate[20]],
        y: [portfolioIst[9], portfolioIst[20]]
      },
      groups,
      scatter,
      seasonSeries,
      heat,
      labels,
      corr,
      residuen,
      schwelle,
      residSerie,
      zaehlerIst,
      zaehlerPrognose,
      anomalie,
      anomalienMonat,
      features: ["letzte_3_monate_durchschnitt_kwh", "vorjahr_monat_verbrauch_kwh", "vertragsleistung_kw", "heiztage", "produktionsplan_index", "arbeitstage", "mittlere_temperatur_c", "wartung_aktiv"],
      importance: [0.312, 0.208, 0.147, 0.121, 0.094, 0.058, 0.041, 0.019],
      qcols: ["verbrauch_kwh (MWh-Text)", "vorjahr_monat_verbrauch_kwh", "vormonat_verbrauch_kwh", "kundentyp (Schreibvarianten)", "zaehler_id (Duplikate)", "verbrauch_kwh (negativ)", "monat (Format)"],
      qpct: [2.5, 50.0, 4.2, 1.1, 0.23, 0.07, 100],
      topLabels: ["ZW-02044", "ZW-05316", "ZW-04412", "ZW-06021", "ZW-03771", "ZW-05540", "ZW-01187", "ZW-00145"],
      topValues: [3120400, 2418700, 1284500, 742900, 631200, 268800, 212340, 198400],
      shareSeries: {
        Gewerbe: monate.map((_, i) => 210 * 120 * season("Gewerbe", i)),
        Industrie: monate.map((_, i) => 780 * 120 * season("Industrie", i)),
        Kommunal: monate.map((_, i) => 92 * 120 * season("Kommunal", i))
      }
    };
  }

  /* Gallery manifest — id, German title, one-line "when", builder fed with demo data */
  const GALLERY = [{
    id: "zeitreihe",
    title: "Zeitreihe Prognose vs. Ist",
    when: "Portfolio oder ein Zähler über die Zeit; Band = Konfidenz, rote Marker = Anomalien",
    build: d => timeseriesForecast({
      x: d.monate,
      ist: d.portfolioIst,
      prognose: d.portfolioPrognose,
      lo: d.lo,
      hi: d.hi,
      anomalien: d.anomalien,
      yTitle: "Verbrauch (MWh)"
    })
  }, {
    id: "saisonalitaet",
    title: "Saisonalität je Kundentyp",
    when: "Monatsmittel Jan–Dez; zeigt Heiz- und Produktionsabhängigkeit",
    build: d => seasonality({
      monate: d.M12,
      series: d.seasonSeries
    })
  }, {
    id: "histogramm",
    title: "Verteilung des Verbrauchs",
    when: "Überlagerte, halbtransparente Histogramme je Kundentyp; log-Achse für schiefe Verteilungen",
    build: d => histogram({
      groups: d.groups,
      logX: true
    })
  }, {
    id: "boxplot",
    title: "Boxplot je Kundentyp",
    when: "Streuung und Ausreißer kompakt vergleichen",
    build: d => boxplot({
      groups: d.groups
    })
  }, {
    id: "scatter",
    title: "Temperatur vs. Verbrauch",
    when: "Wetterabhängigkeit je Kundentyp mit OLS-Trendlinie",
    build: d => scatterTrend({
      groups: d.scatter
    })
  }, {
    id: "heatmap",
    title: "Heatmap Monat × Kundentyp",
    when: "Sequentielle Navy-Skala; Verbrauch in MWh",
    build: d => heatmap({
      x: d.M12,
      y: Object.keys(d.seasonSeries),
      z: d.heat,
      zTitle: "MWh"
    })
  }, {
    id: "korrelation",
    title: "Korrelationsmatrix",
    when: "Divergente Skala, Mitte 0; Werte im Hover, showText:true ab ~700 px Breite",
    build: d => correlation({
      labels: d.labels,
      z: d.corr
    })
  }, {
    id: "residuen-verteilung",
    title: "Residuen-Verteilung",
    when: "Histogramm der Residuen mit ±Schwellwert (95. Perzentil)",
    build: d => residualHist({
      residuen: d.residuen,
      schwelle: d.schwelle
    })
  }, {
    id: "residuen-zeit",
    title: "Residuen über Zeit",
    when: "Balken je Monat, Überschreitungen rot",
    build: d => residualBars({
      x: d.monate,
      residuen: d.residSerie,
      schwelle: 18000
    })
  }, {
    id: "parity",
    title: "Parity-Plot Prognose vs. Ist",
    when: "Ein Punkt pro Zähler; Abstand zur Diagonale = Fehler, rot = Anomalie",
    build: d => parity({
      ist: d.zaehlerIst,
      prognose: d.zaehlerPrognose,
      anomalie: d.anomalie
    })
  }, {
    id: "feature-importance",
    title: "Feature Importance",
    when: "Sortierte horizontale Balken mit Wert-Labels",
    build: d => featureImportance({
      features: d.features,
      values: d.importance
    })
  }, {
    id: "anomalien-monat",
    title: "Anomalien je Monat",
    when: "Gestapelt nach Kundentyp; operative Plausibilität prüfen",
    build: d => anomalyStack({
      x: d.monate,
      series: d.anomalienMonat
    })
  }, {
    id: "datenqualitaet",
    title: "Datenqualität je Spalte",
    when: "Anteil fehlerhafter Werte; ≥ 5 % rot, ≥ 1 % amber",
    build: d => missingValues({
      columns: d.qcols,
      pct: d.qpct
    })
  }, {
    id: "top-n",
    title: "Top-Zähler nach Verbrauch",
    when: "Rangliste; Wert als Label außen",
    build: d => topN({
      labels: d.topLabels,
      values: d.topValues
    })
  }, {
    id: "anteile",
    title: "Anteil Kundentyp über Zeit",
    when: "100 %-gestapelte Fläche; Strukturverschiebung im Portfolio",
    build: d => shareArea({
      x: d.monate,
      series: d.shareSeries
    })
  }];
  global.SWW = {
    C,
    QUALITATIVE,
    KT,
    ROLE,
    SEQ,
    DIV,
    FONT,
    LABEL,
    layout,
    render,
    demo,
    GALLERY,
    timeseriesForecast,
    seasonality,
    histogram,
    boxplot,
    scatterTrend,
    heatmap,
    correlation,
    residualHist,
    residualBars,
    featureImportance,
    missingValues,
    parity,
    anomalyStack,
    topN,
    shareArea
  };
})(window);
})(); } catch (e) { __ds_ns.__errors.push({ path: "assets/plotly/sww_plotly.js", error: String((e && e.message) || e) }); }

// components/core/Icon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `.sww-icon{display:inline-block;flex:none;background-color:currentColor;-webkit-mask-position:center;mask-position:center;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-size:contain;mask-size:contain;vertical-align:-0.15em}`;
if (typeof document !== "undefined" && !document.getElementById("sww-icon-css")) {
  const s = document.createElement("style");
  s.id = "sww-icon-css";
  s.textContent = css;
  document.head.appendChild(s);
}
const ICON_BASE = "https://unpkg.com/lucide-static/icons/";

/** Fixed domain mapping — see readme.md > ICONOGRAPHY. */
const DOMAIN_ICONS = {
  verbrauch: "zap",
  prognose: "trending-up",
  residuum: "activity",
  anomalie: "triangle-alert",
  zaehler: "gauge",
  industrie: "factory",
  gewerbe: "store",
  kommunal: "landmark",
  temperatur: "thermometer",
  wartung: "wrench",
  beschaffung: "shopping-cart",
  datenqualitaet: "database",
  bericht: "file-chart-column",
  monat: "calendar",
  filter: "filter",
  export: "download",
  geprueft: "check"
};
function Icon({
  name,
  size = 16,
  color,
  title,
  style,
  className = "",
  ...rest
}) {
  const src = `url("${ICON_BASE}${name}.svg")`;
  return /*#__PURE__*/React.createElement("span", _extends({
    className: `sww-icon ${className}`,
    role: title ? "img" : "presentation",
    "aria-label": title || undefined,
    "aria-hidden": title ? undefined : "true",
    style: {
      width: size,
      height: size,
      color,
      WebkitMaskImage: src,
      maskImage: src,
      ...style
    }
  }, rest));
}
Object.assign(__ds_scope, { ICON_BASE, DOMAIN_ICONS, Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Icon.jsx", error: String((e && e.message) || e) }); }

// components/core/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-badge{display:inline-flex;align-items:center;gap:var(--space-1);border-radius:var(--radius-pill);border:1px solid;font-family:var(--font-sans);font-weight:var(--fw-medium);font-size:var(--fs-xs);line-height:1;padding:4px 8px 4px 7px;white-space:nowrap}
.sww-badge--sm{font-size:var(--fs-2xs);padding:3px 7px 3px 6px}
.sww-badge--ok{background:var(--status-ok-bg);border-color:var(--status-ok-border);color:var(--green-700)}
.sww-badge--warn{background:var(--status-warn-bg);border-color:var(--status-warn-border);color:var(--amber-700)}
.sww-badge--critical{background:var(--status-critical-bg);border-color:var(--status-critical-border);color:var(--red-600)}
.sww-badge--info{background:var(--status-info-bg);border-color:var(--status-info-border);color:var(--teal-700)}
.sww-badge--neutral{background:var(--status-neutral-bg);border-color:var(--status-neutral-border);color:var(--grey-600)}
.sww-badge--brand{background:var(--surface-brand-subtle);border-color:var(--navy-200);color:var(--navy-800)}
.sww-badge--solid{border-color:transparent;color:#fff}
.sww-badge--solid.sww-badge--ok{background:var(--green-600)}
.sww-badge--solid.sww-badge--warn{background:var(--amber-600)}
.sww-badge--solid.sww-badge--critical{background:var(--red-500)}
.sww-badge--solid.sww-badge--info{background:var(--teal-600)}
.sww-badge--solid.sww-badge--neutral{background:var(--grey-500)}
.sww-badge--solid.sww-badge--brand{background:var(--navy-700)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-badge-css")) {
  const s = document.createElement("style");
  s.id = "sww-badge-css";
  s.textContent = css;
  document.head.appendChild(s);
}

/** Anomaly severity vocabulary — see readme.md > CONTENT FUNDAMENTALS. */
const SEVERITY = {
  geprueft: {
    status: "ok",
    icon: "check",
    label: "Geprüft"
  },
  hinweis: {
    status: "info",
    icon: "info",
    label: "Hinweis"
  },
  auffaellig: {
    status: "warn",
    icon: "triangle-alert",
    label: "Auffällig"
  },
  kritisch: {
    status: "critical",
    icon: "octagon-alert",
    label: "Kritisch"
  }
};
function Badge({
  status = "neutral",
  size = "md",
  icon,
  solid = false,
  children,
  className = "",
  ...rest
}) {
  const cls = ["sww-badge", `sww-badge--${status}`, `sww-badge--${size}`, solid && "sww-badge--solid", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("span", _extends({
    className: cls
  }, rest), icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 14
  }) : null, children);
}
Object.assign(__ds_scope, { SEVERITY, Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Badge.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-btn{display:inline-flex;align-items:center;justify-content:center;gap:var(--space-2);font-family:var(--font-sans);font-weight:var(--fw-medium);letter-spacing:var(--ls-tight);border-radius:var(--radius-control);border:1px solid transparent;cursor:pointer;white-space:nowrap;text-decoration:none;transition:var(--transition-control)}
.sww-btn:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-btn--sm{height:var(--control-height-sm);padding:0 var(--space-3);font-size:var(--fs-sm)}
.sww-btn--md{height:var(--control-height);padding:0 var(--space-4);font-size:var(--fs-base)}
.sww-btn--lg{height:var(--control-height-lg);padding:0 var(--space-5);font-size:var(--fs-md)}
.sww-btn--block{width:100%}
.sww-btn--primary{background:var(--navy-700);color:#fff;box-shadow:var(--shadow-xs)}
.sww-btn--primary:hover:not(:disabled){background:var(--navy-800)}
.sww-btn--primary:active:not(:disabled){background:var(--navy-900);box-shadow:none}
.sww-btn--accent{background:var(--teal-500);color:#fff;box-shadow:var(--shadow-xs)}
.sww-btn--accent:hover:not(:disabled){background:var(--teal-600)}
.sww-btn--accent:active:not(:disabled){background:var(--teal-700);box-shadow:none}
.sww-btn--secondary{background:var(--surface-card);color:var(--text-primary);border-color:var(--border-default);box-shadow:var(--shadow-xs)}
.sww-btn--secondary:hover:not(:disabled){background:var(--surface-hover);border-color:var(--border-strong)}
.sww-btn--secondary:active:not(:disabled){background:var(--surface-active);box-shadow:none}
.sww-btn--ghost{background:transparent;color:var(--text-accent)}
.sww-btn--ghost:hover:not(:disabled){background:var(--teal-100)}
.sww-btn--ghost:active:not(:disabled){background:var(--teal-200)}
.sww-btn--danger{background:var(--red-500);color:#fff}
.sww-btn--danger:hover:not(:disabled){background:var(--red-600)}
.sww-btn--danger:active:not(:disabled){background:var(--red-700)}
.sww-btn:disabled{cursor:not-allowed;background:var(--grey-50);color:var(--text-disabled);border-color:var(--border-subtle);box-shadow:none}
.sww-btn--onNavy.sww-btn--secondary{background:rgba(255,255,255,.1);color:#fff;border-color:var(--border-inverse);box-shadow:none}
.sww-btn--onNavy.sww-btn--secondary:hover:not(:disabled){background:rgba(255,255,255,.18);border-color:rgba(255,255,255,.3)}
.sww-btn--onNavy:focus-visible{box-shadow:var(--focus-ring-inverse)}
.sww-btn__spin{width:1em;height:1em;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:sww-btn-spin .7s linear infinite}
@keyframes sww-btn-spin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.sww-btn__spin{animation-duration:2s}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-button-css")) {
  const s = document.createElement("style");
  s.id = "sww-button-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function Button({
  variant = "primary",
  size = "md",
  icon,
  iconAfter,
  loading = false,
  fullWidth = false,
  onNavy = false,
  disabled = false,
  type = "button",
  href,
  children,
  className = "",
  ...rest
}) {
  const cls = ["sww-btn", `sww-btn--${variant}`, `sww-btn--${size}`, fullWidth && "sww-btn--block", onNavy && "sww-btn--onNavy", className].filter(Boolean).join(" ");
  const iconSize = size === "lg" ? 20 : 16;
  const inner = /*#__PURE__*/React.createElement(React.Fragment, null, loading ? /*#__PURE__*/React.createElement("span", {
    className: "sww-btn__spin"
  }) : icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: iconSize
  }) : null, children, iconAfter && !loading ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconAfter,
    size: iconSize
  }) : null);
  if (href && !disabled) return /*#__PURE__*/React.createElement("a", _extends({
    className: cls,
    href: href
  }, rest), inner);
  return /*#__PURE__*/React.createElement("button", _extends({
    className: cls,
    type: type,
    disabled: disabled || loading
  }, rest), inner);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-iconbtn{display:inline-flex;align-items:center;justify-content:center;border-radius:var(--radius-control);border:1px solid transparent;background:transparent;color:var(--text-secondary);cursor:pointer;transition:var(--transition-control)}
.sww-iconbtn:hover:not(:disabled){background:var(--surface-hover);color:var(--text-primary)}
.sww-iconbtn:active:not(:disabled){background:var(--surface-active)}
.sww-iconbtn:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-iconbtn:disabled{cursor:not-allowed;color:var(--text-disabled);background:transparent}
.sww-iconbtn--sm{width:var(--control-height-sm);height:var(--control-height-sm)}
.sww-iconbtn--md{width:var(--control-height);height:var(--control-height)}
.sww-iconbtn--bordered{border-color:var(--border-default);background:var(--surface-card);box-shadow:var(--shadow-xs)}
.sww-iconbtn--bordered:hover:not(:disabled){border-color:var(--border-strong)}
.sww-iconbtn--onNavy{color:var(--navy-200)}
.sww-iconbtn--onNavy:hover:not(:disabled){background:rgba(255,255,255,.1);color:#fff}
.sww-iconbtn--onNavy:focus-visible{box-shadow:var(--focus-ring-inverse)}
.sww-iconbtn[aria-pressed="true"]{background:var(--surface-accent-subtle);color:var(--teal-700)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-iconbutton-css")) {
  const s = document.createElement("style");
  s.id = "sww-iconbutton-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function IconButton({
  icon,
  label,
  size = "md",
  bordered = false,
  onNavy = false,
  pressed,
  className = "",
  ...rest
}) {
  const cls = ["sww-iconbtn", `sww-iconbtn--${size}`, bordered && "sww-iconbtn--bordered", onNavy && "sww-iconbtn--onNavy", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("button", _extends({
    className: cls,
    type: "button",
    title: label,
    "aria-label": label,
    "aria-pressed": pressed
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: size === "sm" ? 14 : 16
  }));
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-tag{display:inline-flex;align-items:center;gap:6px;border-radius:var(--radius-pill);border:1px solid var(--border-default);background:var(--surface-card);color:var(--text-secondary);font-family:var(--font-sans);font-size:var(--fs-xs);font-weight:var(--fw-medium);line-height:1;padding:5px 9px;transition:var(--transition-control)}
.sww-tag--clickable{cursor:pointer}
.sww-tag--clickable:hover{background:var(--surface-hover);border-color:var(--border-strong);color:var(--text-primary)}
.sww-tag--selected{background:var(--surface-accent-subtle);border-color:var(--teal-300);color:var(--teal-700)}
.sww-tag:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-tag__dot{width:7px;height:7px;border-radius:50%;flex:none}
.sww-tag__x{display:inline-flex;margin:-2px -3px -2px 1px;padding:2px;border:0;background:transparent;color:inherit;border-radius:var(--radius-pill);cursor:pointer;opacity:.7}
.sww-tag__x:hover{opacity:1;background:rgba(4,38,63,.08)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-tag-css")) {
  const s = document.createElement("style");
  s.id = "sww-tag-css";
  s.textContent = css;
  document.head.appendChild(s);
}

/** Fixed Kundentyp colours — identical to tokens/charts.css and sww_theme.py. */
const KUNDENTYP_COLOR = {
  Gewerbe: "var(--chart-gewerbe)",
  Industrie: "var(--chart-industrie)",
  Kommunal: "var(--chart-kommunal)"
};
function Tag({
  children,
  dotColor,
  icon,
  selected = false,
  onRemove,
  onClick,
  className = "",
  ...rest
}) {
  const clickable = Boolean(onClick);
  const cls = ["sww-tag", clickable && "sww-tag--clickable", selected && "sww-tag--selected", className].filter(Boolean).join(" ");
  const Node = clickable ? "button" : "span";
  return /*#__PURE__*/React.createElement(Node, _extends({
    className: cls,
    onClick: onClick,
    type: clickable ? "button" : undefined
  }, rest), dotColor ? /*#__PURE__*/React.createElement("span", {
    className: "sww-tag__dot",
    style: {
      background: dotColor
    }
  }) : null, icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 14
  }) : null, children, onRemove ? /*#__PURE__*/React.createElement("button", {
    className: "sww-tag__x",
    type: "button",
    "aria-label": "Entfernen",
    onClick: e => {
      e.stopPropagation();
      onRemove(e);
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "x",
    size: 12
  })) : null);
}
Object.assign(__ds_scope, { KUNDENTYP_COLOR, Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

// components/data/DataTable.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-tblwrap{width:100%;overflow:auto}
.sww-tbl{width:100%;border-collapse:separate;border-spacing:0;font:var(--text-body)}
.sww-tbl th{position:sticky;top:0;z-index:1;background:var(--surface-sunken);backdrop-filter:var(--blur-panel);font:var(--text-overline);letter-spacing:var(--ls-caps);text-transform:uppercase;color:var(--text-secondary);text-align:left;padding:0 var(--space-4);height:var(--row-height-compact);white-space:nowrap;border-bottom:1px solid var(--border-default)}
.sww-tbl th.num,.sww-tbl td.num{text-align:right;font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.sww-tbl th.num{font-family:var(--font-sans)}
.sww-tbl td{padding:0 var(--space-4);height:var(--row-height);border-bottom:1px solid var(--border-subtle);color:var(--text-primary);vertical-align:middle;white-space:nowrap}
.sww-tbl--compact td{height:var(--row-height-compact);font-size:var(--fs-sm)}
.sww-tbl tbody tr{transition:background-color var(--dur-fast) var(--ease-standard)}
.sww-tbl tbody tr:hover{background:var(--surface-hover)}
.sww-tbl tbody tr.is-clickable{cursor:pointer}
.sww-tbl tbody tr.is-selected{background:var(--surface-accent-subtle);box-shadow:inset 2px 0 0 var(--teal-500)}
.sww-tbl tbody tr:focus-visible{outline:none;box-shadow:inset 0 0 0 2px var(--teal-500)}
.sww-tbl__sort{display:inline-flex;align-items:center;gap:4px;border:0;background:transparent;padding:0;font:inherit;letter-spacing:inherit;text-transform:inherit;color:inherit;cursor:pointer}
.sww-tbl__sort:hover{color:var(--text-primary)}
.sww-tbl__sort[data-active="true"]{color:var(--text-accent)}
.sww-tbl__mono{font-family:var(--font-mono);font-size:var(--fs-sm)}
.sww-tbl__empty{padding:var(--space-10) var(--space-4);text-align:center;color:var(--text-muted);font:var(--text-body)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-table-css")) {
  const s = document.createElement("style");
  s.id = "sww-table-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function DataTable({
  columns = [],
  rows = [],
  rowKey = "id",
  compact = false,
  selectedKey,
  onRowClick,
  sort,
  onSortChange,
  empty = "Keine Daten für den gewählten Zeitraum.",
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: "sww-tblwrap"
  }, rest), /*#__PURE__*/React.createElement("table", {
    className: ["sww-tbl", compact && "sww-tbl--compact", className].filter(Boolean).join(" ")
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, columns.map(c => /*#__PURE__*/React.createElement("th", {
    key: c.key,
    className: c.numeric ? "num" : undefined,
    style: {
      width: c.width
    }
  }, c.sortable && onSortChange ? /*#__PURE__*/React.createElement("button", {
    className: "sww-tbl__sort",
    type: "button",
    "data-active": sort && sort.key === c.key,
    onClick: () => onSortChange({
      key: c.key,
      dir: sort && sort.key === c.key && sort.dir === "desc" ? "asc" : "desc"
    })
  }, c.label, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: sort && sort.key === c.key && sort.dir === "asc" ? "arrow-up" : "arrow-down",
    size: 12
  })) : c.label)))), /*#__PURE__*/React.createElement("tbody", null, rows.length === 0 ? /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("td", {
    className: "sww-tbl__empty",
    colSpan: columns.length
  }, empty)) : rows.map(r => {
    const key = r[rowKey];
    return /*#__PURE__*/React.createElement("tr", {
      key: key,
      tabIndex: onRowClick ? 0 : undefined,
      className: [onRowClick && "is-clickable", selectedKey === key && "is-selected"].filter(Boolean).join(" "),
      onClick: onRowClick ? () => onRowClick(r) : undefined,
      onKeyDown: onRowClick ? e => {
        if (e.key === "Enter") onRowClick(r);
      } : undefined
    }, columns.map(c => /*#__PURE__*/React.createElement("td", {
      key: c.key,
      className: c.numeric ? "num" : c.mono ? "sww-tbl__mono" : undefined
    }, c.render ? c.render(r) : r[c.key])));
  }))));
}
Object.assign(__ds_scope, { DataTable });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/DataTable.jsx", error: String((e && e.message) || e) }); }

// components/data/Sparkline.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-spark{display:block;overflow:visible}
.sww-spark__wrap{display:inline-flex;align-items:center;gap:var(--space-2)}
.sww-spark__val{font:var(--text-data);color:var(--text-secondary);font-variant-numeric:tabular-nums}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-sparkline-css")) {
  const s = document.createElement("style");
  s.id = "sww-sparkline-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function path(values, w, h, pad) {
  const min = Math.min(...values),
    max = Math.max(...values);
  const span = max - min || 1;
  const step = values.length > 1 ? (w - pad * 2) / (values.length - 1) : 0;
  return values.map((v, i) => {
    const x = pad + i * step;
    const y = pad + (h - pad * 2) * (1 - (v - min) / span);
    return `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(" ");
}
function Sparkline({
  values = [],
  forecast,
  width = 88,
  height = 28,
  color = "var(--data-actual)",
  forecastColor = "var(--data-forecast)",
  markLast = true,
  anomalyIndices = [],
  className = "",
  ...rest
}) {
  if (!values.length) return null;
  const pad = 3;
  const all = forecast ? values.concat(forecast) : values;
  const min = Math.min(...all),
    max = Math.max(...all),
    span = max - min || 1;
  const step = all.length > 1 ? (width - pad * 2) / (all.length - 1) : 0;
  const pt = (v, i) => [pad + i * step, pad + (height - pad * 2) * (1 - (v - min) / span)];
  const d = values.map((v, i) => {
    const [x, y] = pt(v, i);
    return `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(" ");
  const fd = forecast ? forecast.map((v, i) => {
    const [x, y] = pt(v, values.length - 1 + i + (i === 0 ? 0 : 0));
    return `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(" ") : null;
  const [lx, ly] = pt(values[values.length - 1], values.length - 1);
  return /*#__PURE__*/React.createElement("svg", _extends({
    className: `sww-spark ${className}`,
    width: width,
    height: height,
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-hidden": "true"
  }, rest), /*#__PURE__*/React.createElement("path", {
    d: d,
    fill: "none",
    stroke: color,
    strokeWidth: "1.75",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }), fd ? /*#__PURE__*/React.createElement("path", {
    d: fd,
    fill: "none",
    stroke: forecastColor,
    strokeWidth: "1.75",
    strokeDasharray: "4 2",
    strokeLinecap: "round"
  }) : null, anomalyIndices.map(i => {
    const [x, y] = pt(values[i], i);
    return /*#__PURE__*/React.createElement("circle", {
      key: i,
      cx: x,
      cy: y,
      r: "2.75",
      fill: "var(--data-anomaly)",
      stroke: "#fff",
      strokeWidth: "1"
    });
  }), markLast ? /*#__PURE__*/React.createElement("circle", {
    cx: lx,
    cy: ly,
    r: "2.25",
    fill: color
  }) : null);
}
Sparkline.pathFor = path;
Object.assign(__ds_scope, { Sparkline });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/Sparkline.jsx", error: String((e && e.message) || e) }); }

// components/data/KpiTile.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-kpi{container-type:inline-size;display:flex;flex-direction:column;gap:var(--space-2);min-width:0;overflow:hidden;background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-card);box-shadow:var(--shadow-card);padding:var(--space-4) var(--gutter-card)}
.sww-kpi__top{display:flex;align-items:center;gap:var(--space-2);color:var(--text-muted)}
.sww-kpi__lbl{font:var(--text-label);color:var(--text-secondary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sww-kpi__val{display:flex;align-items:baseline;gap:6px;white-space:nowrap;font:var(--text-metric);letter-spacing:var(--ls-tighter);color:var(--text-primary);font-variant-numeric:tabular-nums}
.sww-kpi__unit{font:var(--text-label);font-size:var(--fs-base);color:var(--text-muted);font-family:var(--font-mono)}
.sww-kpi__row{display:flex;align-items:center;gap:var(--space-3);margin-top:2px;min-width:0;overflow:hidden}
.sww-kpi__delta{display:inline-flex;align-items:center;gap:3px;flex:none;white-space:nowrap;font:var(--text-data);font-weight:var(--fw-medium);font-variant-numeric:tabular-nums}
.sww-kpi__delta--up{color:var(--red-600)}
.sww-kpi__delta--down{color:var(--green-700)}
.sww-kpi__delta--flat{color:var(--text-muted)}
.sww-kpi__delta--good{color:var(--green-700)}
.sww-kpi__delta--bad{color:var(--red-600)}
.sww-kpi__ref{font:var(--text-caption);color:var(--text-muted);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sww-kpi__spark{margin-left:auto;flex:0 1 88px;min-width:0;overflow:hidden;line-height:0}
.sww-kpi__spark svg{display:block;width:100%;height:auto;max-width:88px}
@container (max-width:120px){.sww-kpi__spark{display:none}}
.sww-kpi--accent{background:var(--navy-800);border-color:var(--navy-900);box-shadow:none}
.sww-kpi--accent .sww-kpi__lbl,.sww-kpi--accent .sww-kpi__top{color:var(--navy-200)}
.sww-kpi--accent .sww-kpi__val{color:#fff}
.sww-kpi--accent .sww-kpi__unit,.sww-kpi--accent .sww-kpi__ref{color:var(--navy-300)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-kpi-css")) {
  const s = document.createElement("style");
  s.id = "sww-kpi-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function KpiTile({
  label,
  value,
  unit,
  delta,
  deltaDirection,
  deltaTone,
  reference,
  icon,
  spark,
  sparkForecast,
  variant = "default",
  className = "",
  ...rest
}) {
  const dir = deltaDirection || (delta == null ? null : String(delta).trim().startsWith("−") || String(delta).trim().startsWith("-") ? "down" : "up");
  const toneCls = deltaTone ? `sww-kpi__delta--${deltaTone}` : `sww-kpi__delta--${dir || "flat"}`;
  return /*#__PURE__*/React.createElement("div", _extends({
    className: ["sww-kpi", variant === "accent" && "sww-kpi--accent", className].filter(Boolean).join(" ")
  }, rest), /*#__PURE__*/React.createElement("div", {
    className: "sww-kpi__top"
  }, icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 16
  }) : null, /*#__PURE__*/React.createElement("span", {
    className: "sww-kpi__lbl"
  }, label)), /*#__PURE__*/React.createElement("div", {
    className: "sww-kpi__val"
  }, value, unit ? /*#__PURE__*/React.createElement("span", {
    className: "sww-kpi__unit"
  }, unit) : null), /*#__PURE__*/React.createElement("div", {
    className: "sww-kpi__row"
  }, delta != null ? /*#__PURE__*/React.createElement("span", {
    className: `sww-kpi__delta ${toneCls}`
  }, dir === "up" ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "arrow-up-right",
    size: 13
  }) : dir === "down" ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "arrow-down-right",
    size: 13
  }) : null, delta) : null, reference ? /*#__PURE__*/React.createElement("span", {
    className: "sww-kpi__ref"
  }, reference) : null, spark ? /*#__PURE__*/React.createElement("span", {
    className: "sww-kpi__spark"
  }, /*#__PURE__*/React.createElement(__ds_scope.Sparkline, {
    values: spark,
    forecast: sparkForecast,
    color: variant === "accent" ? "var(--teal-300)" : "var(--data-actual)"
  })) : null));
}
Object.assign(__ds_scope, { KpiTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/KpiTile.jsx", error: String((e && e.message) || e) }); }

// components/data/StatusDot.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-dot{display:inline-flex;align-items:center;gap:6px;font:var(--text-caption);color:var(--text-secondary);white-space:nowrap}
.sww-dot__d{width:8px;height:8px;border-radius:50%;flex:none;box-shadow:0 0 0 2px var(--surface-card)}
.sww-dot--lg .sww-dot__d{width:10px;height:10px}
.sww-dot--pulse .sww-dot__d{animation:sww-dot-pulse 2s var(--ease-standard) infinite}
@keyframes sww-dot-pulse{0%,100%{opacity:1}50%{opacity:.45}}
@media (prefers-reduced-motion:reduce){.sww-dot--pulse .sww-dot__d{animation:none}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-statusdot-css")) {
  const s = document.createElement("style");
  s.id = "sww-statusdot-css";
  s.textContent = css;
  document.head.appendChild(s);
}
const COLOR = {
  ok: "var(--status-ok)",
  warn: "var(--status-warn)",
  critical: "var(--status-critical)",
  info: "var(--status-info)",
  neutral: "var(--grey-300)",
  running: "var(--teal-500)"
};
function StatusDot({
  status = "neutral",
  label,
  size = "md",
  pulse = false,
  className = "",
  ...rest
}) {
  const cls = ["sww-dot", size === "lg" && "sww-dot--lg", pulse && "sww-dot--pulse", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("span", _extends({
    className: cls
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "sww-dot__d",
    style: {
      background: COLOR[status]
    }
  }), label);
}
Object.assign(__ds_scope, { StatusDot });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/StatusDot.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Alert.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-alert{display:flex;gap:var(--space-3);padding:var(--space-3) var(--space-4);border:1px solid;border-radius:var(--radius-control);font:var(--text-body)}
.sww-alert__ico{flex:none;margin-top:1px}
.sww-alert__bd{min-width:0;flex:1}
.sww-alert__ttl{font:var(--text-h4);font-size:var(--fs-base);margin:0 0 2px}
.sww-alert__txt{margin:0;color:var(--text-secondary);text-wrap:pretty}
.sww-alert__act{margin-top:var(--space-3);display:flex;gap:var(--space-2)}
.sww-alert__x{flex:none;align-self:flex-start;border:0;background:transparent;color:inherit;opacity:.6;cursor:pointer;padding:2px;border-radius:var(--radius-sm)}
.sww-alert__x:hover{opacity:1;background:rgba(4,38,63,.07)}
.sww-alert--info{background:var(--status-info-bg);border-color:var(--status-info-border);color:var(--teal-700)}
.sww-alert--ok{background:var(--status-ok-bg);border-color:var(--status-ok-border);color:var(--green-700)}
.sww-alert--warn{background:var(--status-warn-bg);border-color:var(--status-warn-border);color:var(--amber-700)}
.sww-alert--critical{background:var(--status-critical-bg);border-color:var(--status-critical-border);color:var(--red-600)}
.sww-alert--neutral{background:var(--surface-sunken);border-color:var(--border-default);color:var(--text-primary)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-alert-css")) {
  const s = document.createElement("style");
  s.id = "sww-alert-css";
  s.textContent = css;
  document.head.appendChild(s);
}
const DEFAULT_ICON = {
  info: "info",
  ok: "circle-check",
  warn: "triangle-alert",
  critical: "octagon-alert",
  neutral: "info"
};
function Alert({
  status = "info",
  title,
  icon,
  actions,
  onDismiss,
  children,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: ["sww-alert", `sww-alert--${status}`, className].filter(Boolean).join(" "),
    role: status === "critical" ? "alert" : "status"
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    className: "sww-alert__ico",
    name: icon || DEFAULT_ICON[status],
    size: 16
  }), /*#__PURE__*/React.createElement("div", {
    className: "sww-alert__bd"
  }, title ? /*#__PURE__*/React.createElement("p", {
    className: "sww-alert__ttl"
  }, title) : null, children ? /*#__PURE__*/React.createElement("p", {
    className: "sww-alert__txt"
  }, children) : null, actions ? /*#__PURE__*/React.createElement("div", {
    className: "sww-alert__act"
  }, actions) : null), onDismiss ? /*#__PURE__*/React.createElement("button", {
    className: "sww-alert__x",
    type: "button",
    "aria-label": "Schlie\xDFen",
    onClick: onDismiss
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "x",
    size: 14
  })) : null);
}
Object.assign(__ds_scope, { Alert });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Alert.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Dialog.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-dlg__scrim{position:fixed;inset:0;background:var(--scrim);backdrop-filter:var(--blur-scrim);display:grid;place-items:center;padding:var(--space-6);z-index:60;animation:sww-dlg-fade var(--dur-base) var(--ease-out)}
.sww-dlg{width:100%;background:var(--surface-card);border-radius:var(--radius-xl);box-shadow:var(--shadow-overlay);display:flex;flex-direction:column;max-height:86vh;animation:sww-dlg-in var(--dur-base) var(--ease-out)}
.sww-dlg--sm{max-width:420px}.sww-dlg--md{max-width:560px}.sww-dlg--lg{max-width:820px}
.sww-dlg__hd{display:flex;align-items:flex-start;gap:var(--space-3);padding:var(--space-5) var(--space-6) var(--space-4)}
.sww-dlg__ttl{font:var(--text-h3);margin:0;color:var(--text-primary)}
.sww-dlg__sub{font:var(--text-caption);color:var(--text-muted);margin:4px 0 0}
.sww-dlg__x{margin-left:auto;border:0;background:transparent;color:var(--text-muted);cursor:pointer;padding:4px;border-radius:var(--radius-sm)}
.sww-dlg__x:hover{background:var(--surface-hover);color:var(--text-primary)}
.sww-dlg__bd{padding:0 var(--space-6) var(--space-5);overflow:auto;font:var(--text-body);color:var(--text-secondary)}
.sww-dlg__ft{display:flex;align-items:center;gap:var(--space-2);justify-content:flex-end;padding:var(--space-4) var(--space-6);border-top:1px solid var(--border-subtle);background:var(--surface-sunken);border-radius:0 0 var(--radius-xl) var(--radius-xl)}
@keyframes sww-dlg-fade{from{opacity:0}to{opacity:1}}
@keyframes sww-dlg-in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.sww-dlg,.sww-dlg__scrim{animation:none}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-dialog-css")) {
  const s = document.createElement("style");
  s.id = "sww-dialog-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function Dialog({
  open = false,
  title,
  subtitle,
  size = "md",
  footer,
  onClose,
  children,
  className = "",
  ...rest
}) {
  React.useEffect(() => {
    if (!open || !onClose) return;
    const h = e => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", h);
    return () => document.removeEventListener("keydown", h);
  }, [open, onClose]);
  if (!open) return null;
  return /*#__PURE__*/React.createElement("div", {
    className: "sww-dlg__scrim",
    onClick: onClose ? e => {
      if (e.target === e.currentTarget) onClose();
    } : undefined
  }, /*#__PURE__*/React.createElement("div", _extends({
    className: ["sww-dlg", `sww-dlg--${size}`, className].filter(Boolean).join(" "),
    role: "dialog",
    "aria-modal": "true",
    "aria-label": typeof title === "string" ? title : undefined
  }, rest), /*#__PURE__*/React.createElement("header", {
    className: "sww-dlg__hd"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("h2", {
    className: "sww-dlg__ttl"
  }, title), subtitle ? /*#__PURE__*/React.createElement("p", {
    className: "sww-dlg__sub"
  }, subtitle) : null), onClose ? /*#__PURE__*/React.createElement("button", {
    className: "sww-dlg__x",
    type: "button",
    "aria-label": "Schlie\xDFen",
    onClick: onClose
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "x",
    size: 18
  })) : null), /*#__PURE__*/React.createElement("div", {
    className: "sww-dlg__bd"
  }, children), footer ? /*#__PURE__*/React.createElement("footer", {
    className: "sww-dlg__ft"
  }, footer) : null));
}
Object.assign(__ds_scope, { Dialog });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Dialog.jsx", error: String((e && e.message) || e) }); }

// components/feedback/EmptyState.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-empty{display:flex;flex-direction:column;align-items:center;text-align:center;gap:var(--space-2);padding:var(--space-12) var(--space-6);color:var(--text-secondary)}
.sww-empty--sm{padding:var(--space-8) var(--space-4)}
.sww-empty__ico{display:grid;place-items:center;width:44px;height:44px;border-radius:var(--radius-pill);background:var(--surface-sunken);border:1px solid var(--border-subtle);color:var(--text-muted);margin-bottom:var(--space-2)}
.sww-empty__ttl{font:var(--text-h4);color:var(--text-primary);margin:0}
.sww-empty__txt{font:var(--text-body);color:var(--text-muted);margin:0;max-width:52ch;text-wrap:pretty}
.sww-empty__act{margin-top:var(--space-4);display:flex;gap:var(--space-2)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-empty-css")) {
  const s = document.createElement("style");
  s.id = "sww-empty-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function EmptyState({
  icon = "inbox",
  title,
  children,
  actions,
  size = "md",
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: ["sww-empty", size === "sm" && "sww-empty--sm", className].filter(Boolean).join(" ")
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "sww-empty__ico"
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 24
  })), /*#__PURE__*/React.createElement("p", {
    className: "sww-empty__ttl"
  }, title), children ? /*#__PURE__*/React.createElement("p", {
    className: "sww-empty__txt"
  }, children) : null, actions ? /*#__PURE__*/React.createElement("div", {
    className: "sww-empty__act"
  }, actions) : null);
}
Object.assign(__ds_scope, { EmptyState });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/EmptyState.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-check{display:inline-flex;align-items:flex-start;gap:var(--space-2);cursor:pointer;font:var(--text-body);color:var(--text-primary)}
.sww-check--disabled{cursor:not-allowed;color:var(--text-disabled)}
.sww-check__box{position:relative;flex:none;width:16px;height:16px;margin-top:2px;border:1px solid var(--border-strong);border-radius:var(--radius-xs);background:var(--surface-card);display:grid;place-items:center;color:#fff;transition:var(--transition-control)}
.sww-check:hover .sww-check__box{border-color:var(--teal-500)}
.sww-check__in{position:absolute;inset:0;opacity:0;margin:0;cursor:inherit}
.sww-check__in:checked+.sww-check__box,.sww-check__in:indeterminate+.sww-check__box{background:var(--teal-500);border-color:var(--teal-500)}
.sww-check__in:focus-visible+.sww-check__box{box-shadow:var(--focus-ring)}
.sww-check__in:disabled+.sww-check__box{background:var(--grey-50);border-color:var(--border-default);color:var(--text-disabled)}
.sww-check__in:disabled:checked+.sww-check__box{background:var(--grey-300);border-color:var(--grey-300)}
.sww-check__wrap{position:relative;display:flex;align-items:flex-start}
.sww-check__txt{display:flex;flex-direction:column;gap:2px}
.sww-check__hint{font:var(--text-caption);color:var(--text-muted)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-checkbox-css")) {
  const s = document.createElement("style");
  s.id = "sww-checkbox-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function Checkbox({
  label,
  hint,
  indeterminate = false,
  disabled = false,
  className = "",
  style,
  ...rest
}) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (ref.current) ref.current.indeterminate = indeterminate;
  }, [indeterminate]);
  return /*#__PURE__*/React.createElement("label", {
    className: ["sww-check", disabled && "sww-check--disabled", className].filter(Boolean).join(" "),
    style: style
  }, /*#__PURE__*/React.createElement("span", {
    className: "sww-check__wrap"
  }, /*#__PURE__*/React.createElement("input", _extends({
    ref: ref,
    className: "sww-check__in",
    type: "checkbox",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "sww-check__box"
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: indeterminate ? "minus" : "check",
    size: 12
  }))), label ? /*#__PURE__*/React.createElement("span", {
    className: "sww-check__txt"
  }, label, hint ? /*#__PURE__*/React.createElement("span", {
    className: "sww-check__hint"
  }, hint) : null) : null);
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-field{display:flex;flex-direction:column;gap:6px;min-width:0}
.sww-field__label{font:var(--text-label);color:var(--text-secondary)}
.sww-field__req{color:var(--red-500);margin-left:2px}
.sww-field__hint{font:var(--text-caption);color:var(--text-muted)}
.sww-field__err{font:var(--text-caption);color:var(--red-600);display:flex;align-items:center;gap:4px}
.sww-input{display:flex;align-items:center;gap:var(--space-2);height:var(--control-height);padding:0 var(--space-3);background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-control);color:var(--text-primary);transition:var(--transition-control)}
.sww-input:hover{border-color:var(--border-strong)}
.sww-input:focus-within{border-color:var(--border-accent);box-shadow:var(--focus-ring)}
.sww-input--sm{height:var(--control-height-sm);padding:0 var(--space-2);font-size:var(--fs-sm)}
.sww-input--invalid{border-color:var(--red-500)}
.sww-input--invalid:focus-within{box-shadow:0 0 0 3px rgba(179,38,30,.25)}
.sww-input--disabled{background:var(--grey-50);border-color:var(--border-subtle);color:var(--text-disabled);cursor:not-allowed}
.sww-input__el{flex:1;min-width:0;border:0;background:transparent;outline:none;font:var(--text-body);color:inherit}
.sww-input__el::placeholder{color:var(--text-disabled)}
.sww-input__el:disabled{cursor:not-allowed}
.sww-input--numeric .sww-input__el{font-family:var(--font-mono);font-variant-numeric:tabular-nums;text-align:right}
.sww-input__affix{font:var(--text-data);color:var(--text-muted);flex:none}
.sww-input__ico{color:var(--text-muted);flex:none}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-input-css")) {
  const s = document.createElement("style");
  s.id = "sww-input-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function Input({
  label,
  hint,
  error,
  required = false,
  size = "md",
  icon,
  suffix,
  numeric = false,
  disabled = false,
  id,
  className = "",
  style,
  ...rest
}) {
  const uid = React.useMemo(() => id || `sww-in-${Math.random().toString(36).slice(2, 8)}`, [id]);
  const cls = ["sww-input", `sww-input--${size}`, numeric && "sww-input--numeric", error && "sww-input--invalid", disabled && "sww-input--disabled", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", {
    className: "sww-field",
    style: style
  }, label ? /*#__PURE__*/React.createElement("label", {
    className: "sww-field__label",
    htmlFor: uid
  }, label, required ? /*#__PURE__*/React.createElement("span", {
    className: "sww-field__req"
  }, "*") : null) : null, /*#__PURE__*/React.createElement("div", {
    className: cls
  }, icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    className: "sww-input__ico",
    name: icon,
    size: 16
  }) : null, /*#__PURE__*/React.createElement("input", _extends({
    className: "sww-input__el",
    id: uid,
    disabled: disabled,
    "aria-invalid": error ? true : undefined
  }, rest)), suffix ? /*#__PURE__*/React.createElement("span", {
    className: "sww-input__affix"
  }, suffix) : null), error ? /*#__PURE__*/React.createElement("span", {
    className: "sww-field__err"
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "triangle-alert",
    size: 12
  }), error) : hint ? /*#__PURE__*/React.createElement("span", {
    className: "sww-field__hint"
  }, hint) : null);
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-select{position:relative;display:flex;align-items:center;height:var(--control-height);background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-control);transition:var(--transition-control)}
.sww-select:hover{border-color:var(--border-strong)}
.sww-select:focus-within{border-color:var(--border-accent);box-shadow:var(--focus-ring)}
.sww-select--sm{height:var(--control-height-sm)}
.sww-select--disabled{background:var(--grey-50);border-color:var(--border-subtle);cursor:not-allowed}
.sww-select__el{appearance:none;-webkit-appearance:none;flex:1;min-width:0;height:100%;border:0;outline:none;background:transparent;font:var(--text-body);color:var(--text-primary);padding:0 32px 0 var(--space-3);cursor:pointer}
.sww-select--sm .sww-select__el{font-size:var(--fs-sm);padding:0 28px 0 var(--space-2)}
.sww-select__el:disabled{color:var(--text-disabled);cursor:not-allowed}
.sww-select__chev{position:absolute;right:10px;color:var(--text-muted);pointer-events:none}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-select-css")) {
  const s = document.createElement("style");
  s.id = "sww-select-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function Select({
  label,
  hint,
  error,
  options = [],
  size = "md",
  disabled = false,
  id,
  className = "",
  style,
  children,
  ...rest
}) {
  const uid = React.useMemo(() => id || `sww-sel-${Math.random().toString(36).slice(2, 8)}`, [id]);
  const cls = ["sww-select", `sww-select--${size}`, disabled && "sww-select--disabled", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", {
    className: "sww-field",
    style: style
  }, label ? /*#__PURE__*/React.createElement("label", {
    className: "sww-field__label",
    htmlFor: uid
  }, label) : null, /*#__PURE__*/React.createElement("div", {
    className: cls
  }, /*#__PURE__*/React.createElement("select", _extends({
    className: "sww-select__el",
    id: uid,
    disabled: disabled
  }, rest), children || options.map(o => {
    const opt = typeof o === "string" ? {
      value: o,
      label: o
    } : o;
    return /*#__PURE__*/React.createElement("option", {
      key: opt.value,
      value: opt.value
    }, opt.label);
  })), /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    className: "sww-select__chev",
    name: "chevron-down",
    size: 16
  })), error ? /*#__PURE__*/React.createElement("span", {
    className: "sww-field__err"
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "triangle-alert",
    size: 12
  }), error) : hint ? /*#__PURE__*/React.createElement("span", {
    className: "sww-field__hint"
  }, hint) : null);
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-switch{display:inline-flex;align-items:center;gap:var(--space-3);cursor:pointer;font:var(--text-body);color:var(--text-primary)}
.sww-switch--disabled{cursor:not-allowed;color:var(--text-disabled)}
.sww-switch__wrap{position:relative;flex:none;width:34px;height:20px}
.sww-switch__in{position:absolute;inset:0;opacity:0;margin:0;cursor:inherit}
.sww-switch__track{position:absolute;inset:0;background:var(--grey-300);border-radius:var(--radius-pill);transition:background-color var(--dur-fast) var(--ease-standard)}
.sww-switch__knob{position:absolute;top:2px;left:2px;width:16px;height:16px;background:#fff;border-radius:50%;box-shadow:var(--shadow-sm);transition:transform var(--dur-fast) var(--ease-standard)}
.sww-switch__in:checked~.sww-switch__track{background:var(--teal-500)}
.sww-switch__in:checked~.sww-switch__knob{transform:translateX(14px)}
.sww-switch__in:focus-visible~.sww-switch__track{box-shadow:var(--focus-ring)}
.sww-switch__in:disabled~.sww-switch__track{background:var(--grey-200)}
.sww-switch__txt{display:flex;flex-direction:column;gap:2px}
.sww-switch__hint{font:var(--text-caption);color:var(--text-muted)}
@media (prefers-reduced-motion:reduce){.sww-switch__knob{transition:none}}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-switch-css")) {
  const s = document.createElement("style");
  s.id = "sww-switch-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function Switch({
  label,
  hint,
  disabled = false,
  className = "",
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: ["sww-switch", disabled && "sww-switch--disabled", className].filter(Boolean).join(" "),
    style: style
  }, /*#__PURE__*/React.createElement("span", {
    className: "sww-switch__wrap"
  }, /*#__PURE__*/React.createElement("input", _extends({
    className: "sww-switch__in",
    type: "checkbox",
    role: "switch",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "sww-switch__track"
  }), /*#__PURE__*/React.createElement("span", {
    className: "sww-switch__knob"
  })), label ? /*#__PURE__*/React.createElement("span", {
    className: "sww-switch__txt"
  }, label, hint ? /*#__PURE__*/React.createElement("span", {
    className: "sww-switch__hint"
  }, hint) : null) : null);
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// components/layout/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-card{display:flex;flex-direction:column;min-width:0;background:var(--surface-card);border:1px solid var(--border-default);border-radius:var(--radius-card);box-shadow:var(--shadow-card)}
.sww-card--flat{box-shadow:none}
.sww-card--sunken{background:var(--surface-sunken)}
.sww-card--interactive{cursor:pointer;transition:box-shadow var(--dur-fast) var(--ease-standard),border-color var(--dur-fast) var(--ease-standard)}
.sww-card--interactive:hover{box-shadow:var(--shadow-raised);border-color:var(--border-strong)}
.sww-card--interactive:focus-visible{outline:none;box-shadow:var(--focus-ring)}
.sww-card__rule{height:3px;border-radius:var(--radius-card) var(--radius-card) 0 0;margin:-1px -1px 0}
.sww-card__hd{display:flex;align-items:center;gap:var(--space-3);padding:var(--space-4) var(--gutter-card);border-bottom:1px solid var(--border-subtle)}
.sww-card__ttl{font:var(--text-h4);color:var(--text-primary);margin:0}
.sww-card__sub{font:var(--text-caption);color:var(--text-muted);margin:2px 0 0}
.sww-card__act{margin-left:auto;display:flex;align-items:center;gap:var(--space-2)}
.sww-card__bd{padding:var(--gutter-card);flex:1;min-width:0}
.sww-card__bd--flush{padding:0}
.sww-card__ft{padding:var(--space-3) var(--gutter-card);border-top:1px solid var(--border-subtle);font:var(--text-caption);color:var(--text-muted);display:flex;align-items:center;gap:var(--space-3)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-card-css")) {
  const s = document.createElement("style");
  s.id = "sww-card-css";
  s.textContent = css;
  document.head.appendChild(s);
}
const RULE = {
  ok: "var(--status-ok)",
  warn: "var(--status-warn)",
  critical: "var(--status-critical)",
  info: "var(--status-info)",
  brand: "var(--navy-700)"
};
function Card({
  title,
  subtitle,
  icon,
  actions,
  footer,
  status,
  variant = "default",
  interactive = false,
  flush = false,
  children,
  className = "",
  ...rest
}) {
  const cls = ["sww-card", variant !== "default" && `sww-card--${variant}`, interactive && "sww-card--interactive", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("section", _extends({
    className: cls,
    tabIndex: interactive ? 0 : undefined
  }, rest), status ? /*#__PURE__*/React.createElement("div", {
    className: "sww-card__rule",
    style: {
      background: RULE[status]
    }
  }) : null, title ? /*#__PURE__*/React.createElement("header", {
    className: "sww-card__hd"
  }, icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 16,
    style: {
      color: "var(--text-muted)"
    }
  }) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("h3", {
    className: "sww-card__ttl"
  }, title), subtitle ? /*#__PURE__*/React.createElement("p", {
    className: "sww-card__sub"
  }, subtitle) : null), actions ? /*#__PURE__*/React.createElement("div", {
    className: "sww-card__act"
  }, actions) : null) : null, /*#__PURE__*/React.createElement("div", {
    className: `sww-card__bd${flush ? " sww-card__bd--flush" : ""}`
  }, children), footer ? /*#__PURE__*/React.createElement("footer", {
    className: "sww-card__ft"
  }, footer) : null);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Card.jsx", error: String((e && e.message) || e) }); }

// components/layout/PageHeader.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-ph{display:flex;align-items:flex-end;gap:var(--space-4);flex-wrap:wrap;padding-bottom:var(--space-5);border-bottom:1px solid var(--border-default);margin-bottom:var(--space-6)}
.sww-ph--plain{border-bottom:0;padding-bottom:0;margin-bottom:var(--space-5)}
.sww-ph__eyebrow{font:var(--text-overline);letter-spacing:var(--ls-caps);text-transform:uppercase;color:var(--text-accent);margin:0 0 6px}
.sww-ph__ttl{font:var(--text-h1);letter-spacing:var(--ls-tighter);color:var(--text-primary);margin:0}
.sww-ph__sub{font:var(--text-body);color:var(--text-secondary);margin:6px 0 0;max-width:72ch;text-wrap:pretty}
.sww-ph__meta{display:flex;align-items:center;gap:var(--space-3);margin-top:var(--space-3);font:var(--text-caption);color:var(--text-muted);flex-wrap:wrap}
.sww-ph__act{margin-left:auto;display:flex;align-items:center;gap:var(--space-2);flex-wrap:wrap}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-pageheader-css")) {
  const s = document.createElement("style");
  s.id = "sww-pageheader-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function PageHeader({
  eyebrow,
  title,
  subtitle,
  meta,
  actions,
  plain = false,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("header", _extends({
    className: ["sww-ph", plain && "sww-ph--plain", className].filter(Boolean).join(" ")
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, eyebrow ? /*#__PURE__*/React.createElement("p", {
    className: "sww-ph__eyebrow"
  }, eyebrow) : null, /*#__PURE__*/React.createElement("h1", {
    className: "sww-ph__ttl"
  }, title), subtitle ? /*#__PURE__*/React.createElement("p", {
    className: "sww-ph__sub"
  }, subtitle) : null, meta ? /*#__PURE__*/React.createElement("div", {
    className: "sww-ph__meta"
  }, meta) : null), actions ? /*#__PURE__*/React.createElement("div", {
    className: "sww-ph__act"
  }, actions) : null);
}
Object.assign(__ds_scope, { PageHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/PageHeader.jsx", error: String((e && e.message) || e) }); }

// components/layout/SidebarNav.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-sb{display:flex;flex-direction:column;width:var(--sidebar-width);flex:none;background:var(--navy-800);color:#fff;height:100%;overflow:hidden}
.sww-sb--collapsed{width:var(--sidebar-width-collapsed)}
.sww-sb__brand{display:flex;align-items:center;gap:var(--space-3);padding:var(--space-4);border-bottom:1px solid var(--border-inverse);min-height:var(--topbar-height);box-sizing:border-box}
.sww-sb__logo{background:#fff;border-radius:var(--radius-sm);padding:5px 7px;display:block}
.sww-sb__logo img{display:block;height:24px;width:auto}
.sww-sb__mark{background:#fff;border-radius:var(--radius-sm);padding:3px;display:grid;place-items:center}
.sww-sb__mark img{display:block;height:26px;width:auto}
.sww-sb__grp{font:var(--text-overline);letter-spacing:var(--ls-caps);text-transform:uppercase;color:var(--navy-300);padding:var(--space-5) var(--space-4) var(--space-2)}
.sww-sb__list{list-style:none;margin:0;padding:var(--space-2) var(--space-2) 0;display:flex;flex-direction:column;gap:2px;overflow-y:auto}
.sww-sb__i{display:flex;align-items:center;gap:var(--space-3);width:100%;padding:0 var(--space-3);height:var(--control-height);border:0;background:transparent;color:var(--navy-100);font:var(--text-label);font-size:var(--fs-base);text-align:left;border-radius:var(--radius-control);cursor:pointer;transition:var(--transition-control)}
.sww-sb__i:hover{background:rgba(255,255,255,.08);color:#fff}
.sww-sb__i:focus-visible{outline:none;box-shadow:var(--focus-ring-inverse)}
.sww-sb__i[aria-current="page"]{background:var(--teal-600);color:#fff;font-weight:var(--fw-semibold)}
.sww-sb__n{margin-left:auto;font:var(--text-data);font-size:var(--fs-2xs);background:rgba(255,255,255,.14);border-radius:var(--radius-pill);padding:2px 6px}
.sww-sb__i[aria-current="page"] .sww-sb__n{background:rgba(255,255,255,.22)}
.sww-sb__n--alert{background:var(--red-500)}
.sww-sb__ft{margin-top:auto;padding:var(--space-4);border-top:1px solid var(--border-inverse);font:var(--text-caption);color:var(--navy-300)}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-sidebar-css")) {
  const s = document.createElement("style");
  s.id = "sww-sidebar-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function SidebarNav({
  items = [],
  value,
  onChange,
  collapsed = false,
  footer,
  logoSrc = "assets/logo-sww-wordmark.png",
  markSrc = "assets/logo-sww-emblem.png",
  className = "",
  ...rest
}) {
  const groups = [];
  items.forEach(it => {
    const g = it.group || "";
    const last = groups[groups.length - 1];
    if (last && last.name === g) last.items.push(it);else groups.push({
      name: g,
      items: [it]
    });
  });
  return /*#__PURE__*/React.createElement("nav", _extends({
    className: ["sww-sb", collapsed && "sww-sb--collapsed", className].filter(Boolean).join(" ")
  }, rest), /*#__PURE__*/React.createElement("div", {
    className: "sww-sb__brand"
  }, collapsed ? /*#__PURE__*/React.createElement("span", {
    className: "sww-sb__mark"
  }, /*#__PURE__*/React.createElement("img", {
    src: markSrc,
    alt: "SWW"
  })) : /*#__PURE__*/React.createElement("span", {
    className: "sww-sb__logo"
  }, /*#__PURE__*/React.createElement("img", {
    src: logoSrc,
    alt: "StadtWerke Westhafen GmbH"
  }))), groups.map((g, gi) => /*#__PURE__*/React.createElement(React.Fragment, {
    key: g.name || gi
  }, g.name && !collapsed ? /*#__PURE__*/React.createElement("div", {
    className: "sww-sb__grp"
  }, g.name) : null, /*#__PURE__*/React.createElement("ul", {
    className: "sww-sb__list"
  }, g.items.map(it => /*#__PURE__*/React.createElement("li", {
    key: it.id
  }, /*#__PURE__*/React.createElement("button", {
    className: "sww-sb__i",
    type: "button",
    title: it.label,
    "aria-current": it.id === value ? "page" : undefined,
    onClick: () => onChange && onChange(it.id)
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: it.icon,
    size: 20
  }), collapsed ? null : it.label, !collapsed && it.count != null ? /*#__PURE__*/React.createElement("span", {
    className: `sww-sb__n${it.alert ? " sww-sb__n--alert" : ""}`
  }, it.count) : null)))))), footer && !collapsed ? /*#__PURE__*/React.createElement("div", {
    className: "sww-sb__ft"
  }, footer) : null);
}
Object.assign(__ds_scope, { SidebarNav });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/SidebarNav.jsx", error: String((e && e.message) || e) }); }

// components/layout/Tabs.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const css = `
.sww-tabs{display:flex;align-items:stretch;gap:var(--space-5);border-bottom:1px solid var(--border-default)}
.sww-tabs__t{position:relative;display:inline-flex;align-items:center;gap:var(--space-2);padding:0 2px var(--space-3);border:0;background:transparent;font:var(--text-label);font-size:var(--fs-base);color:var(--text-secondary);cursor:pointer;transition:var(--transition-control)}
.sww-tabs__t:hover{color:var(--text-primary)}
.sww-tabs__t:focus-visible{outline:none;box-shadow:var(--focus-ring);border-radius:var(--radius-xs)}
.sww-tabs__t[aria-selected="true"]{color:var(--text-brand);font-weight:var(--fw-semibold)}
.sww-tabs__t[aria-selected="true"]::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:var(--teal-500);border-radius:2px 2px 0 0}
.sww-tabs__t:disabled{color:var(--text-disabled);cursor:not-allowed}
.sww-tabs__n{font:var(--text-data);font-size:var(--fs-2xs);background:var(--grey-100);color:var(--text-secondary);border-radius:var(--radius-pill);padding:2px 6px}
.sww-tabs__t[aria-selected="true"] .sww-tabs__n{background:var(--surface-accent-subtle);color:var(--teal-700)}
.sww-tabs--pills{border-bottom:0;gap:var(--space-1);background:var(--grey-100);padding:3px;border-radius:var(--radius-control);display:inline-flex}
.sww-tabs--pills .sww-tabs__t{padding:6px var(--space-3);border-radius:var(--radius-sm)}
.sww-tabs--pills .sww-tabs__t[aria-selected="true"]{background:var(--surface-card);box-shadow:var(--shadow-xs)}
.sww-tabs--pills .sww-tabs__t[aria-selected="true"]::after{display:none}
`;
if (typeof document !== "undefined" && !document.getElementById("sww-tabs-css")) {
  const s = document.createElement("style");
  s.id = "sww-tabs-css";
  s.textContent = css;
  document.head.appendChild(s);
}
function Tabs({
  items = [],
  value,
  onChange,
  variant = "underline",
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: ["sww-tabs", variant === "pills" && "sww-tabs--pills", className].filter(Boolean).join(" "),
    role: "tablist"
  }, rest), items.map(it => /*#__PURE__*/React.createElement("button", {
    key: it.id,
    className: "sww-tabs__t",
    role: "tab",
    type: "button",
    "aria-selected": it.id === value,
    disabled: it.disabled,
    onClick: () => onChange && onChange(it.id)
  }, it.icon ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: it.icon,
    size: 16
  }) : null, it.label, it.count != null ? /*#__PURE__*/React.createElement("span", {
    className: "sww-tabs__n"
  }, it.count) : null)));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Tabs.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/AnomalienScreen.jsx
try { (() => {
const {
  PageHeader,
  Card,
  DataTable,
  Tabs,
  Tag,
  StatusDot,
  Badge,
  Button,
  IconButton,
  Select,
  Input,
  Checkbox,
  Dialog,
  EmptyState,
  Alert,
  KUNDENTYP_COLOR,
  Sparkline
} = window.StadtWerkeWesthafenDesignSystem_acd94c;
function AnomalienScreen({
  monat,
  onOpenZaehler
}) {
  const D = window.SWWData;
  const [tab, setTab] = React.useState("alle");
  const [typ, setTyp] = React.useState("all");
  const [q, setQ] = React.useState("");
  const [sort, setSort] = React.useState({
    key: "abweichung_pct",
    dir: "desc"
  });
  const [sel, setSel] = React.useState(null);
  const [ticket, setTicket] = React.useState(null);
  let rows = D.zaehler.filter(z => {
    if (tab === "kritisch" && z.status !== "critical") return false;
    if (tab === "auffaellig" && z.status !== "warn") return false;
    if (tab === "geprueft" && !z.geprueft) return false;
    if (typ !== "all" && z.kundentyp !== typ) return false;
    if (q && !(z.zaehler_id + " " + z.kunde).toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });
  rows = rows.slice().sort((a, b) => {
    const k = sort.key,
      m = sort.dir === "desc" ? -1 : 1;
    const av = k === "abweichung_pct" ? Math.abs(a[k]) : a[k],
      bv = k === "abweichung_pct" ? Math.abs(b[k]) : b[k];
    return av > bv ? m : av < bv ? -m : 0;
  });
  const counts = {
    alle: D.zaehler.length,
    kritisch: D.zaehler.filter(z => z.status === "critical").length,
    auffaellig: D.zaehler.filter(z => z.status === "warn").length,
    geprueft: D.zaehler.filter(z => z.geprueft).length
  };
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(PageHeader, {
    eyebrow: "Fr\xFChwarnung",
    title: "Anomalien " + monat,
    subtitle: "Zähler mit absoluter prozentualer Abweichung über dem Schwellwert von " + D.metrik.schwelle + " % (95. Perzentil der Residuen).",
    meta: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", null, rows.length, " von 700 Z\xE4hlern"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, "Stand ", D.metrik.stand)),
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      icon: "download"
    }, "Export CSV"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      icon: "file-chart-column"
    }, "Bericht erzeugen"))
  }), /*#__PURE__*/React.createElement(Alert, {
    status: "warn",
    title: "Einheiten gemischt",
    style: {
      marginBottom: "var(--space-4)"
    },
    actions: /*#__PURE__*/React.createElement(Button, {
      size: "sm",
      variant: "secondary",
      icon: "database"
    }, "Zur Datenqualit\xE4t")
  }, "412 Werte in verbrauch_kwh lagen als MWh-Text vor und wurden auf kWh umgerechnet."), /*#__PURE__*/React.createElement(Card, {
    flush: true
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-3)",
      padding: "var(--space-3) var(--gutter-card)",
      borderBottom: "1px solid var(--border-subtle)",
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement(Tabs, {
    value: tab,
    onChange: setTab,
    variant: "pills",
    items: [{
      id: "alle",
      label: "Alle",
      count: counts.alle
    }, {
      id: "kritisch",
      label: "Kritisch",
      count: counts.kritisch
    }, {
      id: "auffaellig",
      label: "Auffällig",
      count: counts.auffaellig
    }, {
      id: "geprueft",
      label: "Geprüft",
      count: counts.geprueft
    }]
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginLeft: "auto",
      display: "flex",
      alignItems: "center",
      gap: "var(--space-3)"
    }
  }, /*#__PURE__*/React.createElement(Input, {
    size: "sm",
    icon: "search",
    placeholder: "Z\xE4hler oder Kunde",
    value: q,
    onChange: e => setQ(e.target.value),
    style: {
      width: 210
    }
  }), /*#__PURE__*/React.createElement(Select, {
    size: "sm",
    value: typ,
    onChange: e => setTyp(e.target.value),
    style: {
      width: 170
    },
    options: [{
      value: "all",
      label: "Alle Kundentypen"
    }, {
      value: "Gewerbe",
      label: "Gewerbe"
    }, {
      value: "Industrie",
      label: "Industrie"
    }, {
      value: "Kommunal",
      label: "Kommunal"
    }]
  }), /*#__PURE__*/React.createElement(IconButton, {
    icon: "filter",
    label: "Weitere Filter",
    bordered: true
  }))), rows.length === 0 ? /*#__PURE__*/React.createElement(EmptyState, {
    icon: "triangle-alert",
    title: "Keine Anomalien \xFCber dem Schwellwert",
    actions: /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      size: "sm",
      onClick: () => {
        setQ("");
        setTyp("all");
        setTab("alle");
      }
    }, "Filter zur\xFCcksetzen")
  }, "Schwellwert: 95. Perzentil der absoluten prozentualen Abweichung (" + D.metrik.schwelle + " %).") : /*#__PURE__*/React.createElement(DataTable, {
    rowKey: "zaehler_id",
    sort: sort,
    onSortChange: setSort,
    selectedKey: sel,
    onRowClick: r => setSel(r.zaehler_id),
    columns: [{
      key: "check",
      label: /*#__PURE__*/React.createElement(Checkbox, {
        indeterminate: true,
        "aria-label": "Alle ausw\xE4hlen"
      }),
      width: 44,
      render: () => /*#__PURE__*/React.createElement(Checkbox, {
        "aria-label": "Zeile ausw\xE4hlen"
      })
    }, {
      key: "zaehler_id",
      label: "Zähler",
      mono: true,
      width: 108,
      sortable: true
    }, {
      key: "kunde",
      label: "Kunde"
    }, {
      key: "kundentyp",
      label: "Kundentyp",
      width: 148,
      render: r => /*#__PURE__*/React.createElement(Tag, {
        dotColor: KUNDENTYP_COLOR[r.kundentyp]
      }, r.kundentyp)
    }, {
      key: "vertragsleistung_kw",
      label: "Leistung (kW)",
      numeric: true,
      sortable: true,
      render: r => D.fmt(r.vertragsleistung_kw)
    }, {
      key: "prognose_kwh",
      label: "Prognose (kWh)",
      numeric: true,
      render: r => D.fmt(r.prognose_kwh)
    }, {
      key: "ist_kwh",
      label: "Ist (kWh)",
      numeric: true,
      sortable: true,
      render: r => D.fmt(r.ist_kwh)
    }, {
      key: "residuum_kwh",
      label: "Residuum (kWh)",
      numeric: true,
      render: r => (r.residuum_kwh > 0 ? "+" : "−") + D.fmt(Math.abs(r.residuum_kwh))
    }, {
      key: "abweichung_pct",
      label: "Abweichung",
      numeric: true,
      sortable: true,
      render: r => /*#__PURE__*/React.createElement("span", {
        style: {
          fontWeight: 600,
          color: Math.abs(r.abweichung_pct) > 30 ? "var(--red-600)" : Math.abs(r.abweichung_pct) > 15 ? "var(--amber-700)" : "var(--text-secondary)"
        }
      }, D.fmtPct(r.abweichung_pct))
    }, {
      key: "trend",
      label: "24 Monate",
      width: 104,
      render: r => /*#__PURE__*/React.createElement(Sparkline, {
        values: r.historie.map(v => v / 1000),
        anomalyIndices: r.anomalieIdx
      })
    }, {
      key: "status",
      label: "Status",
      width: 136,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        status: r.status,
        label: r.statusLabel
      })
    }, {
      key: "akt",
      label: "",
      width: 96,
      render: r => /*#__PURE__*/React.createElement("span", {
        style: {
          display: "flex",
          gap: 4
        }
      }, /*#__PURE__*/React.createElement(IconButton, {
        size: "sm",
        icon: "external-link",
        label: "Z\xE4hler \xF6ffnen",
        onClick: e => {
          e.stopPropagation();
          onOpenZaehler(r.zaehler_id);
        }
      }), /*#__PURE__*/React.createElement(IconButton, {
        size: "sm",
        icon: "ticket",
        label: "Ticket anlegen",
        onClick: e => {
          e.stopPropagation();
          setTicket(r);
        }
      }))
    }],
    rows: rows
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-3)",
      padding: "var(--space-3) var(--gutter-card)",
      borderTop: "1px solid var(--border-subtle)",
      font: "var(--text-caption)",
      color: "var(--text-muted)"
    }
  }, /*#__PURE__*/React.createElement("span", null, rows.length, " Zeilen \xB7 sortiert nach ", sort.key), /*#__PURE__*/React.createElement("span", {
    style: {
      marginLeft: "auto",
      display: "flex",
      gap: "var(--space-2)"
    }
  }, /*#__PURE__*/React.createElement(IconButton, {
    size: "sm",
    icon: "chevron-left",
    label: "Vorherige Seite",
    bordered: true
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--text-data)",
      alignSelf: "center"
    }
  }, "1 / 8"), /*#__PURE__*/React.createElement(IconButton, {
    size: "sm",
    icon: "chevron-right",
    label: "N\xE4chste Seite",
    bordered: true
  })))), /*#__PURE__*/React.createElement(Dialog, {
    open: Boolean(ticket),
    onClose: () => setTicket(null),
    title: "Anomalie-Ticket anlegen",
    subtitle: ticket ? ticket.zaehler_id + " · " + ticket.kunde + " · " + monat : "",
    footer: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      onClick: () => setTicket(null)
    }, "Abbrechen"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      icon: "check",
      onClick: () => setTicket(null)
    }, "Ticket anlegen"))
  }, ticket ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0
    }
  }, "Abweichung ", D.fmtPct(ticket.abweichung_pct), " gegen\xFCber der Prognose (", D.fmt(ticket.prognose_kwh), " kWh). Das Ticket geht an Netzmanagement (Anke B\xFCrger)."), /*#__PURE__*/React.createElement(Select, {
    label: "Pr\xFCfgrund",
    options: ["Zählerauslesung prüfen", "Leitungsverlust vermuten", "Abrechnungsfehler prüfen", "Produktionsplan abweichend"]
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Notiz",
    placeholder: "Kurzbeschreibung f\xFCr Netzmanagement"
  }), /*#__PURE__*/React.createElement(Checkbox, {
    label: "Netzmanagement per E-Mail informieren",
    defaultChecked: true
  })) : null));
}
Object.assign(window, {
  AnomalienScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/AnomalienScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/BeschaffungScreen.jsx
try { (() => {
const {
  PageHeader,
  Card,
  KpiTile,
  DataTable,
  Badge,
  Button,
  Select,
  Alert,
  StatusDot,
  Tabs
} = window.StadtWerkeWesthafenDesignSystem_acd94c;
function BeschaffungScreen({
  monat
}) {
  const D = window.SWWData;
  const [view, setView] = React.useState("menge");
  const typen = ["Gewerbe", "Industrie", "Kommunal"];
  const anteil = {
    Gewerbe: 0.27,
    Industrie: 0.58,
    Kommunal: 0.15
  };
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(PageHeader, {
    eyebrow: "Planung",
    title: "Beschaffungsplanung 04/2025",
    subtitle: "Prognostizierte Abnahmemenge je Monat als Grundlage der Terminbeschaffung; Restmenge geht in den Spotmarkt.",
    meta: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", null, "Sponsor: Stefan Lechtenberg, Energiebeschaffung"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, "Stand ", D.metrik.stand)),
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      icon: "download"
    }, "Plan exportieren"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      icon: "check"
    }, "Beschaffung freigeben"))
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4,1fr)",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(KpiTile, {
    variant: "accent",
    label: "Prognose 04/2025",
    value: "14.820",
    unit: "MWh",
    reference: "Konfidenzband \xB1 640 MWh",
    icon: "trending-up"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Bereits beschafft",
    value: "14.500",
    unit: "MWh",
    reference: "97,8 % der Prognose",
    icon: "shopping-cart"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Offene Spotmenge",
    value: "320",
    unit: "MWh",
    delta: "+120",
    deltaTone: "bad",
    reference: "vs. Plan 03/2025",
    icon: "activity"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Spot-Kostenrisiko",
    value: "38.400",
    unit: "EUR",
    reference: "bei 120 EUR/MWh Spread",
    icon: "triangle-alert"
  })), /*#__PURE__*/React.createElement(Alert, {
    status: "info",
    title: "Prognosefehler wirkt direkt auf die Spotmenge",
    style: {
      marginBottom: "var(--space-4)"
    }
  }, "MAE ", D.metrik.mae, " kWh pro Z\xE4hler entspricht rund 290 MWh Portfolio-Unsicherheit je Monat. Terminbeschaffung deckt daher 97\u201398 %, nicht 100 %."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1.5fr 1fr",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Prognostizierte Abnahme nach Kundentyp",
    subtitle: "N\xE4chste 6 Monate, MWh",
    icon: "chart-column",
    actions: /*#__PURE__*/React.createElement(Tabs, {
      variant: "pills",
      value: view,
      onChange: setView,
      items: [{
        id: "menge",
        label: "Menge"
      }, {
        id: "anteil",
        label: "Anteil"
      }]
    }),
    footer: "Terminbeschaffung monatlich zum Monatsbeginn"
  }, /*#__PURE__*/React.createElement(Chart, {
    height: 270,
    layout: {
      barmode: view === "anteil" ? "stack" : "group",
      margin: {
        l: 62,
        r: 16,
        t: 30,
        b: 40
      },
      yaxis: {
        title: {
          text: view === "anteil" ? "Anteil (MWh)" : "MWh"
        }
      }
    },
    data: typen.map(t => ({
      type: "bar",
      name: t,
      x: D.beschaffung.map(b => b.monat),
      y: D.beschaffung.map(b => Math.round(b.prognose_mwh * anteil[t])),
      marker: {
        color: KT[t]
      }
    }))
  })), /*#__PURE__*/React.createElement(Card, {
    title: "Prognose vs. beschaffte Menge",
    subtitle: "Differenz = Spotmarkt-Exposure",
    icon: "shopping-cart",
    footer: "Positiv = Zukauf, negativ = Verkauf"
  }, /*#__PURE__*/React.createElement(Chart, {
    height: 270,
    layout: {
      margin: {
        l: 58,
        r: 16,
        t: 30,
        b: 40
      },
      yaxis: {
        title: {
          text: "MWh"
        }
      }
    },
    data: [{
      type: "bar",
      name: "Beschafft",
      x: D.beschaffung.map(b => b.monat),
      y: D.beschaffung.map(b => b.beschafft_mwh),
      marker: {
        color: ROLE.ist
      }
    }, {
      type: "scatter",
      mode: "lines+markers",
      name: "Prognose",
      x: D.beschaffung.map(b => b.monat),
      y: D.beschaffung.map(b => b.prognose_mwh),
      line: {
        color: ROLE.prognose,
        width: 2,
        dash: "4,2"
      },
      marker: {
        size: 6,
        color: ROLE.prognose
      }
    }]
  }))), /*#__PURE__*/React.createElement(Card, {
    title: "Beschaffungsplan",
    subtitle: "Rollierend 6 Monate",
    icon: "calendar",
    flush: true,
    actions: /*#__PURE__*/React.createElement(Select, {
      size: "sm",
      options: ["6 Monate", "12 Monate"],
      style: {
        width: 130
      }
    })
  }, /*#__PURE__*/React.createElement(DataTable, {
    rowKey: "monat",
    columns: [{
      key: "monat",
      label: "Monat",
      mono: true,
      width: 100
    }, {
      key: "prognose_mwh",
      label: "Prognose (MWh)",
      numeric: true,
      render: r => D.fmt(r.prognose_mwh)
    }, {
      key: "band",
      label: "Konfidenzband",
      numeric: true
    }, {
      key: "beschafft_mwh",
      label: "Beschafft (MWh)",
      numeric: true,
      render: r => D.fmt(r.beschafft_mwh)
    }, {
      key: "spot_mwh",
      label: "Spot offen (MWh)",
      numeric: true,
      render: r => D.fmt(r.spot_mwh)
    }, {
      key: "deckung",
      label: "Deckung",
      numeric: true,
      render: r => new Intl.NumberFormat("de-DE", {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
      }).format(r.beschafft_mwh / r.prognose_mwh * 100) + " %"
    }, {
      key: "kosten_eur",
      label: "Termin­kosten (EUR)",
      numeric: true
    }, {
      key: "status",
      label: "Status",
      width: 150,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        status: r.status,
        label: r.status === "ok" ? "Gedeckt" : "Spot nötig"
      })
    }],
    rows: D.beschaffung
  })));
}
Object.assign(window, {
  BeschaffungScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/BeschaffungScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/Chart.jsx
try { (() => {
/* Plotly wrapper that applies the SWW template from assets/plotly/. */
const SWW_PLOT = {
  font: {
    family: "IBM Plex Sans, Segoe UI, sans-serif",
    size: 12,
    color: "#141A21"
  },
  paper_bgcolor: "#FFFFFF",
  plot_bgcolor: "#FFFFFF",
  colorway: ["#084878", "#0080A0", "#58A858", "#0090C8", "#C77E11", "#6CC0D2", "#4E5A68", "#B3261E"],
  separators: ",.",
  margin: {
    l: 58,
    r: 18,
    t: 14,
    b: 36
  },
  hovermode: "x unified",
  hoverlabel: {
    bgcolor: "#FFFFFF",
    bordercolor: "#E4E9EF",
    font: {
      family: "IBM Plex Sans, sans-serif",
      size: 12,
      color: "#141A21"
    }
  },
  legend: {
    orientation: "h",
    yanchor: "bottom",
    y: 1.02,
    xanchor: "left",
    x: 0,
    font: {
      size: 12,
      color: "#6B7887"
    }
  },
  xaxis: {
    showgrid: false,
    zeroline: false,
    showline: true,
    linecolor: "#E4E9EF",
    ticks: "outside",
    ticklen: 4,
    tickcolor: "#E4E9EF",
    tickfont: {
      family: "IBM Plex Sans, sans-serif",
      size: 11,
      color: "#6B7887"
    }
  },
  yaxis: {
    showgrid: true,
    gridcolor: "#E4E9EF",
    zeroline: false,
    showline: false,
    tickformat: ",d",
    separatethousands: true,
    tickfont: {
      family: "IBM Plex Sans, sans-serif",
      size: 11,
      color: "#6B7887"
    },
    title: {
      font: {
        size: 12,
        color: "#6B7887"
      }
    }
  },
  bargap: 0.36,
  barcornerradius: 4
};
function deepMerge(a, b) {
  const out = Array.isArray(a) ? a.slice() : {
    ...a
  };
  Object.keys(b || {}).forEach(k => {
    out[k] = b[k] && typeof b[k] === "object" && !Array.isArray(b[k]) && a && typeof a[k] === "object" ? deepMerge(a[k] || {}, b[k]) : b[k];
  });
  return out;
}
function Chart({
  data,
  layout = {},
  height = 260,
  config
}) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!ref.current || !window.Plotly) return;
    const el = ref.current;
    let raf = 0;
    const draw = () => {
      const w = el.clientWidth || el.parentElement && el.parentElement.clientWidth || 600;
      window.Plotly.react(el, data, deepMerge(deepMerge(SWW_PLOT, {
        height,
        width: w,
        autosize: false
      }), layout), {
        displayModeBar: false,
        responsive: false,
        ...config
      });
    };
    const ro = new ResizeObserver(() => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(draw);
    });
    ro.observe(el);
    draw();
    return () => {
      ro.disconnect();
      cancelAnimationFrame(raf);
      window.Plotly.purge(el);
    };
  }, [data, layout, height]);
  return /*#__PURE__*/React.createElement("div", {
    ref: ref,
    style: {
      width: "100%",
      height,
      minWidth: 0,
      overflow: "hidden"
    }
  });
}
const ROLE = {
  ist: "#084878",
  prognose: "#0090C8",
  band: "rgba(0,144,200,0.16)",
  residuum: "#0080A0",
  schwelle: "#C77E11",
  anomalie: "#B3261E"
};
const KT = {
  Gewerbe: "#0080A0",
  Industrie: "#084878",
  Kommunal: "#58A858"
};
Object.assign(window, {
  Chart,
  SWW_PLOT,
  ROLE,
  KT
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/Chart.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/DatenqualitaetScreen.jsx
try { (() => {
const {
  PageHeader,
  Card,
  KpiTile,
  DataTable,
  Badge,
  Button,
  Alert,
  StatusDot,
  Tag
} = window.StadtWerkeWesthafenDesignSystem_acd94c;
function DatenqualitaetScreen() {
  const D = window.SWWData;
  const stufen = [{
    schritt: "Rohdaten",
    zeilen: 16800
  }, {
    schritt: "Duplikate entfernt",
    zeilen: 16762
  }, {
    schritt: "Negative Verbräuche entfernt",
    zeilen: 16751
  }, {
    schritt: "Einheiten vereinheitlicht",
    zeilen: 16751
  }, {
    schritt: "Analytische Tabelle",
    zeilen: 16751
  }];
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(PageHeader, {
    eyebrow: "Planung",
    title: "Datenqualit\xE4t",
    subtitle: "Befunde der Qualit\xE4tspr\xFCfung auf data/verbrauch.csv (700 Z\xE4hler \xD7 24 Monate, UTF-8 mit BOM).",
    meta: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", null, "16.800 Beobachtungen"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, "Januar 2024 \u2013 Dezember 2025"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, "Pr\xFCfung ", D.metrik.stand)),
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      icon: "download"
    }, "Pr\xFCfprotokoll"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      icon: "refresh-cw"
    }, "Pr\xFCfung erneut ausf\xFChren"))
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4,1fr)",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(KpiTile, {
    label: "Beobachtungen",
    value: "16.800",
    reference: "700 Z\xE4hler \xD7 24 Monate",
    icon: "database"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Nach Bereinigung",
    value: "16.751",
    delta: "\u221249",
    deltaTone: "flat",
    reference: "0,3 % entfernt",
    icon: "check"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Befunde offen",
    value: "3",
    delta: "\u22125",
    deltaTone: "good",
    reference: "vs. Erstpr\xFCfung",
    icon: "triangle-alert"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Fehlende Zielwerte",
    value: "0",
    unit: "%",
    reference: "verbrauch_kwh vollst\xE4ndig",
    icon: "zap"
  })), /*#__PURE__*/React.createElement(Alert, {
    status: "critical",
    title: "11 negative Verbr\xE4uche entfernt",
    style: {
      marginBottom: "var(--space-4)"
    },
    actions: /*#__PURE__*/React.createElement(Button, {
      size: "sm",
      variant: "secondary",
      icon: "ticket"
    }, "Tickets ansehen")
  }, "Physikalisch unm\xF6gliche Werte in verbrauch_kwh. Zeilen aus dem Trainingssatz entfernt und als Z\xE4hlerdefekt an Netzmanagement gemeldet."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1.6fr 1fr",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Befunde je Spalte",
    icon: "database",
    flush: true,
    actions: /*#__PURE__*/React.createElement(Badge, {
      status: "warn",
      size: "sm",
      icon: "triangle-alert"
    }, "3 offen")
  }, /*#__PURE__*/React.createElement(DataTable, {
    compact: true,
    rowKey: "k",
    rows: D.datenqualitaet.map((d, i) => ({
      ...d,
      k: i
    })),
    columns: [{
      key: "spalte",
      label: "Spalte",
      mono: true,
      width: 210
    }, {
      key: "typ",
      label: "Typ",
      width: 90
    }, {
      key: "befund",
      label: "Befund"
    }, {
      key: "anteil",
      label: "Anteil",
      numeric: true,
      width: 80
    }, {
      key: "status",
      label: "Schwere",
      width: 130,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        status: r.status,
        label: r.status === "critical" ? "Kritisch" : r.status === "warn" ? "Auffällig" : r.status === "info" ? "Hinweis" : "In Ordnung"
      })
    }, {
      key: "massnahme",
      label: "Maßnahme"
    }]
  })), /*#__PURE__*/React.createElement(Card, {
    title: "Bereinigungspipeline",
    subtitle: "Zeilen je Schritt",
    icon: "activity",
    footer: "Reproduzierbar, versioniert in der Notebook-Pipeline"
  }, /*#__PURE__*/React.createElement(Chart, {
    height: 250,
    layout: {
      margin: {
        l: 210,
        r: 60,
        t: 10,
        b: 30
      },
      showlegend: false,
      xaxis: {
        range: [16700, 16830],
        title: {
          text: "Zeilen"
        },
        showgrid: true,
        gridcolor: "#E4E9EF",
        showline: false
      },
      yaxis: {
        showgrid: false,
        tickfont: {
          size: 11,
          color: "#4E5A68"
        }
      }
    },
    data: [{
      type: "bar",
      orientation: "h",
      y: stufen.map(s => s.schritt).reverse(),
      x: stufen.map(s => s.zeilen).reverse(),
      marker: {
        color: [ROLE.ist, ROLE.residuum, ROLE.residuum, ROLE.residuum, "#58A858"].reverse()
      },
      text: stufen.map(s => D.fmt(s.zeilen)).reverse(),
      textposition: "outside",
      textfont: {
        family: "IBM Plex Sans, sans-serif",
        size: 11,
        color: "#4E5A68"
      }
    }]
  }))), /*#__PURE__*/React.createElement(Card, {
    title: "Train/Test-Split",
    subtitle: "Zeitlicher Split \u2014 keine zuf\xE4llige Aufteilung",
    icon: "calendar"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: "var(--space-4)",
      alignItems: "stretch"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      background: "var(--navy-100)",
      border: "1px solid var(--navy-200)",
      borderRadius: "var(--radius-md)",
      padding: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      font: "var(--text-overline)",
      letterSpacing: "var(--ls-caps)",
      textTransform: "uppercase",
      color: "var(--navy-800)",
      margin: "0 0 6px"
    }
  }, "Training"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: "var(--text-metric-sm)",
      margin: "0 0 4px",
      color: "var(--navy-900)"
    }
  }, "01/2024 \u2013 12/2024"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: "var(--text-caption)",
      color: "var(--navy-800)",
      margin: 0
    }
  }, "8.376 Beobachtungen \xB7 700 Z\xE4hler")), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      background: "var(--teal-100)",
      border: "1px solid var(--teal-200)",
      borderRadius: "var(--radius-md)",
      padding: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      font: "var(--text-overline)",
      letterSpacing: "var(--ls-caps)",
      textTransform: "uppercase",
      color: "var(--teal-700)",
      margin: "0 0 6px"
    }
  }, "Test"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: "var(--text-metric-sm)",
      margin: "0 0 4px",
      color: "var(--teal-700)"
    }
  }, "01/2025 \u2013 12/2025"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: "var(--text-caption)",
      color: "var(--teal-700)",
      margin: 0
    }
  }, "8.375 Beobachtungen \xB7 R\xB2 ", D.metrik.r2, " \xB7 MAE ", D.metrik.mae, " kWh")), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1.2,
      display: "flex",
      flexDirection: "column",
      gap: 8,
      justifyContent: "center"
    }
  }, /*#__PURE__*/React.createElement(Tag, {
    icon: "info"
  }, "Vorjahresmerkmal erst ab 2025 verf\xFCgbar"), /*#__PURE__*/React.createElement(Tag, {
    icon: "info"
  }, "Anomalie-Definition: |Abweichung| > 95. Perzentil"), /*#__PURE__*/React.createElement(Tag, {
    icon: "info"
  }, "Retraining quartalsweise, Drift-Monitoring auf Temperatur")))));
}
Object.assign(window, {
  DatenqualitaetScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/DatenqualitaetScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/Shell.jsx
try { (() => {
const {
  SidebarNav,
  IconButton,
  Select,
  Badge,
  Icon
} = window.StadtWerkeWesthafenDesignSystem_acd94c;
const NAV = [{
  id: "uebersicht",
  label: "Übersicht",
  icon: "layout-dashboard",
  group: "Betrieb"
}, {
  id: "anomalien",
  label: "Anomalien",
  icon: "triangle-alert",
  group: "Betrieb",
  count: 128,
  alert: true
}, {
  id: "zaehler",
  label: "Zähler-Detail",
  icon: "gauge",
  group: "Betrieb"
}, {
  id: "beschaffung",
  label: "Beschaffung",
  icon: "shopping-cart",
  group: "Planung"
}, {
  id: "qualitaet",
  label: "Datenqualität",
  icon: "database",
  group: "Planung"
}];
function TopBar({
  title,
  onMonthChange,
  monat
}) {
  return /*#__PURE__*/React.createElement("header", {
    style: {
      height: "var(--topbar-height)",
      flex: "none",
      display: "flex",
      alignItems: "center",
      gap: "var(--space-4)",
      padding: "0 var(--gutter-page)",
      background: "var(--surface-card)",
      borderBottom: "1px solid var(--border-default)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--text-h4)",
      color: "var(--text-primary)"
    }
  }, title), /*#__PURE__*/React.createElement(Badge, {
    status: "neutral",
    size: "sm",
    icon: "calendar"
  }, monat), /*#__PURE__*/React.createElement("div", {
    style: {
      marginLeft: "auto",
      display: "flex",
      alignItems: "center",
      gap: "var(--space-3)"
    }
  }, /*#__PURE__*/React.createElement(Select, {
    size: "sm",
    value: monat,
    onChange: e => onMonthChange(e.target.value),
    options: ["01/2025", "02/2025", "03/2025"],
    style: {
      width: 130
    }
  }), /*#__PURE__*/React.createElement(IconButton, {
    icon: "search",
    label: "Z\xE4hler suchen"
  }), /*#__PURE__*/React.createElement(IconButton, {
    icon: "bell",
    label: "Benachrichtigungen"
  }), /*#__PURE__*/React.createElement(IconButton, {
    icon: "circle-help",
    label: "Hilfe"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      width: 1,
      height: 24,
      background: "var(--border-default)"
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 28,
      height: 28,
      borderRadius: "50%",
      background: "var(--navy-100)",
      color: "var(--navy-800)",
      display: "grid",
      placeItems: "center",
      font: "var(--text-label)",
      fontSize: "var(--fs-xs)"
    }
  }, "HM"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--text-caption)",
      color: "var(--text-secondary)"
    }
  }, "Henrik Maa\xDF"))));
}
function Shell({
  screen,
  onNavigate,
  title,
  monat,
  onMonthChange,
  children
}) {
  const {
    metrik
  } = window.SWWData;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      height: "100vh",
      overflow: "hidden",
      background: "var(--surface-page)"
    }
  }, /*#__PURE__*/React.createElement(SidebarNav, {
    items: NAV,
    value: screen,
    onChange: onNavigate,
    logoSrc: "../../assets/logo-sww-wordmark.png",
    markSrc: "../../assets/logo-sww-emblem.png",
    footer: /*#__PURE__*/React.createElement(React.Fragment, null, "Modell ", metrik.version, " \xB7 ", metrik.modell, /*#__PURE__*/React.createElement("br", null), "Stand ", metrik.stand)
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0,
      display: "flex",
      flexDirection: "column"
    }
  }, /*#__PURE__*/React.createElement(TopBar, {
    title: title,
    monat: monat,
    onMonthChange: onMonthChange
  }), /*#__PURE__*/React.createElement("main", {
    style: {
      flex: 1,
      overflow: "auto",
      padding: "var(--space-6) var(--gutter-page) var(--space-10)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: "var(--content-max)",
      margin: "0 auto"
    }
  }, children))));
}
Object.assign(window, {
  Shell,
  TopBar,
  NAV
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/Shell.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/UebersichtScreen.jsx
try { (() => {
const {
  PageHeader,
  Card,
  KpiTile,
  DataTable,
  Tag,
  StatusDot,
  Badge,
  Button,
  Alert,
  Switch,
  KUNDENTYP_COLOR,
  Sparkline
} = window.StadtWerkeWesthafenDesignSystem_acd94c;
function UebersichtScreen({
  monat,
  onOpenZaehler
}) {
  const D = window.SWWData;
  const [band, setBand] = React.useState(true);
  const top = D.zaehler.slice().sort((a, b) => Math.abs(b.abweichung_pct) - Math.abs(a.abweichung_pct)).slice(0, 6);
  const traces = [];
  if (band) traces.push({
    x: D.MONATE.concat(D.MONATE.slice().reverse()),
    y: D.portfolioBandHi.concat(D.portfolioBandLo.slice().reverse()),
    fill: "toself",
    fillcolor: ROLE.band,
    line: {
      width: 0
    },
    hoverinfo: "skip",
    name: "Konfidenzband",
    type: "scatter"
  });
  traces.push({
    x: D.MONATE,
    y: D.portfolioIst,
    name: "Ist",
    mode: "lines+markers",
    type: "scatter",
    line: {
      color: ROLE.ist,
      width: 2
    },
    marker: {
      size: 5,
      color: ROLE.ist
    }
  }, {
    x: D.MONATE,
    y: D.portfolioPrognose,
    name: "Prognose",
    mode: "lines",
    type: "scatter",
    line: {
      color: ROLE.prognose,
      width: 2,
      dash: "4,2"
    }
  });
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(PageHeader, {
    eyebrow: "Betrieb",
    title: "Portfolio-Übersicht " + monat,
    subtitle: "Monatsverbrauch von 700 Z\xE4hlern, Prognose zum Monatsbeginn gegen realisierten Verbrauch.",
    meta: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", null, "700 Z\xE4hler"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, "Mittel- und Niederspannung"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, "Stand ", D.metrik.stand)),
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      icon: "download"
    }, "Export"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      icon: "trending-up"
    }, "Prognose 04/2025"))
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4,1fr)",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(KpiTile, {
    label: "Prognose 04/2025",
    value: "14.820",
    unit: "MWh",
    delta: "+2,1 %",
    reference: "vs. Ist 03/2025",
    icon: "trending-up",
    spark: D.portfolioIst.slice(-12).map(v => v / 1000)
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Ist " + monat,
    value: "14.514",
    unit: "MWh",
    delta: "\u22121,3 %",
    reference: "vs. 02/2025",
    icon: "zap"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Prognoseg\xFCte Test 2025",
    value: "R² " + D.metrik.r2,
    reference: "MAE " + D.metrik.mae + " kWh · RMSE " + D.metrik.rmse + " kWh",
    icon: "activity"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    variant: "accent",
    label: "Offene Anomalien",
    value: "128",
    delta: "+18",
    deltaTone: "bad",
    reference: "vs. 02/2025",
    icon: "triangle-alert",
    spark: D.anomalienVerlauf
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1.9fr 1fr",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Prognose vs. Ist \u2014 Portfolio",
    subtitle: "24 Monate, Verbrauch in MWh",
    icon: "trending-up",
    actions: /*#__PURE__*/React.createElement(Switch, {
      label: "Konfidenzband",
      checked: band,
      onChange: e => setBand(e.target.checked)
    }),
    footer: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", null, "Training 2024 \xB7 Test 2025 (zeitlicher Split)"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, D.metrik.modell, " ", D.metrik.version))
  }, /*#__PURE__*/React.createElement(Chart, {
    data: traces,
    height: 272,
    layout: {
      yaxis: {
        title: {
          text: "Verbrauch (MWh)"
        }
      },
      margin: {
        l: 66,
        r: 18,
        t: 30,
        b: 42
      }
    }
  })), /*#__PURE__*/React.createElement(Card, {
    title: "Anomalien nach Kundentyp",
    subtitle: monat,
    icon: "chart-column",
    footer: "Schwellwert: 95. Perzentil der absoluten Abweichung"
  }, /*#__PURE__*/React.createElement(Chart, {
    height: 272,
    layout: {
      margin: {
        l: 44,
        r: 12,
        t: 12,
        b: 40
      },
      showlegend: false,
      yaxis: {
        title: {
          text: "Zähler"
        }
      }
    },
    data: [{
      type: "bar",
      x: Object.keys(D.anomalienNachTyp),
      y: Object.values(D.anomalienNachTyp),
      marker: {
        color: Object.keys(D.anomalienNachTyp).map(k => KT[k])
      },
      text: Object.values(D.anomalienNachTyp),
      textposition: "outside",
      textfont: {
        family: "IBM Plex Sans, sans-serif",
        size: 12,
        color: "#4E5A68"
      }
    }]
  }))), /*#__PURE__*/React.createElement(Alert, {
    status: "neutral",
    icon: "info",
    style: {
      marginBottom: "var(--space-4)"
    }
  }, "Das Modell ersetzt keine Abrechnungsentscheidung \u2014 es flaggt nur Untersuchungsw\xFCrdiges."), /*#__PURE__*/React.createElement(Card, {
    title: "Gr\xF6\xDFte Abweichungen",
    subtitle: "Top 6 nach absoluter prozentualer Abweichung, " + monat,
    icon: "triangle-alert",
    flush: true,
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Badge, {
      status: "critical",
      size: "sm"
    }, "14 kritisch"), /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      size: "sm",
      iconAfter: "arrow-right",
      onClick: () => onOpenZaehler(null)
    }, "Alle Anomalien"))
  }, /*#__PURE__*/React.createElement(DataTable, {
    rowKey: "zaehler_id",
    onRowClick: r => onOpenZaehler(r.zaehler_id),
    columns: [{
      key: "zaehler_id",
      label: "Zähler",
      mono: true,
      width: 110
    }, {
      key: "kunde",
      label: "Kunde"
    }, {
      key: "kundentyp",
      label: "Kundentyp",
      width: 150,
      render: r => /*#__PURE__*/React.createElement(Tag, {
        dotColor: KUNDENTYP_COLOR[r.kundentyp]
      }, r.kundentyp)
    }, {
      key: "prognose_kwh",
      label: "Prognose (kWh)",
      numeric: true,
      render: r => D.fmt(r.prognose_kwh)
    }, {
      key: "ist_kwh",
      label: "Ist (kWh)",
      numeric: true,
      render: r => D.fmt(r.ist_kwh)
    }, {
      key: "abweichung_pct",
      label: "Abweichung",
      numeric: true,
      render: r => /*#__PURE__*/React.createElement("span", {
        style: {
          color: Math.abs(r.abweichung_pct) > 30 ? "var(--red-600)" : Math.abs(r.abweichung_pct) > 15 ? "var(--amber-700)" : "var(--text-secondary)"
        }
      }, D.fmtPct(r.abweichung_pct))
    }, {
      key: "trend",
      label: "24 Monate",
      width: 110,
      render: r => /*#__PURE__*/React.createElement(Sparkline, {
        values: r.historie.map(v => v / 1000),
        anomalyIndices: r.anomalieIdx
      })
    }, {
      key: "status",
      label: "Status",
      width: 140,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        status: r.status,
        label: r.statusLabel
      })
    }],
    rows: top
  })));
}
Object.assign(window, {
  UebersichtScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/UebersichtScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/ZaehlerDetailScreen.jsx
try { (() => {
const {
  PageHeader,
  Card,
  KpiTile,
  Tag,
  Badge,
  Button,
  Select,
  Alert,
  DataTable,
  StatusDot,
  KUNDENTYP_COLOR
} = window.StadtWerkeWesthafenDesignSystem_acd94c;
function ZaehlerDetailScreen({
  zaehlerId,
  monat,
  onBack,
  onTicket
}) {
  const D = window.SWWData;
  const z = D.zaehler.find(x => x.zaehler_id === zaehlerId) || D.zaehler[0];
  const prognoseSerie = z.historie.map((v, i) => Math.round(v * (1 + (i * 37 % 11 - 5) / 130)));
  const residuen = z.historie.map((v, i) => v - prognoseSerie[i]);
  const schwelle = Math.round(Math.max(...residuen.map(Math.abs)) * 0.55);
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(PageHeader, {
    eyebrow: /*#__PURE__*/React.createElement("span", {
      style: {
        display: "inline-flex",
        alignItems: "center",
        gap: 6
      }
    }, "Z\xE4hler-Detail"),
    title: z.zaehler_id + " · " + z.kunde,
    subtitle: "Monatsverbrauch, Prognose und Residuen über 24 Monate. Anomalie-Schwellwert " + D.metrik.schwelle + " % (95. Perzentil).",
    meta: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Tag, {
      dotColor: KUNDENTYP_COLOR[z.kundentyp]
    }, z.kundentyp), /*#__PURE__*/React.createElement(Tag, {
      icon: "gauge"
    }, D.fmt(z.vertragsleistung_kw), " kW Vertragsleistung"), /*#__PURE__*/React.createElement(Tag, {
      icon: "hash"
    }, z.kunde_id), z.wartung_aktiv ? /*#__PURE__*/React.createElement(Tag, {
      icon: "wrench"
    }, "Wartung aktiv") : null, /*#__PURE__*/React.createElement(Badge, {
      status: z.status,
      size: "sm",
      icon: z.status === "critical" ? "octagon-alert" : z.status === "warn" ? "triangle-alert" : "check"
    }, z.statusLabel)),
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      icon: "arrow-left",
      onClick: onBack
    }, "Zur Liste"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      icon: "ticket",
      onClick: () => onTicket(z)
    }, "Anomalie-Ticket anlegen"))
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4,1fr)",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(KpiTile, {
    label: "Ist " + monat,
    value: D.fmt(z.ist_kwh),
    unit: "kWh",
    icon: "zap"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Prognose " + monat,
    value: D.fmt(z.prognose_kwh),
    unit: "kWh",
    icon: "trending-up"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "Residuum",
    value: (z.residuum_kwh > 0 ? "+" : "−") + D.fmt(Math.abs(z.residuum_kwh)),
    unit: "kWh",
    delta: D.fmtPct(z.abweichung_pct),
    deltaTone: Math.abs(z.abweichung_pct) > 15 ? "bad" : "flat",
    reference: "vs. Prognose",
    icon: "activity"
  }), /*#__PURE__*/React.createElement(KpiTile, {
    label: "\xD8 3 Monate",
    value: D.fmt(z.historie.slice(-3).reduce((a, b) => a + b, 0) / 3),
    unit: "kWh",
    icon: "calendar",
    reference: "Vorjahresmonat " + D.fmt(z.historie[11]) + " kWh"
  })), Math.abs(z.abweichung_pct) > 15 ? /*#__PURE__*/React.createElement(Alert, {
    status: z.status === "critical" ? "critical" : "warn",
    title: "Abweichung " + D.fmtPct(z.abweichung_pct) + " über Schwellwert",
    style: {
      marginBottom: "var(--space-4)"
    }
  }, "Z\xE4hlerauslesung und Produktionsplan pr\xFCfen. Produktionsplan-Index ", String(z.produktionsplan_index).replace(".", ","), ", ", z.wartung_aktiv ? "Wartung im Monat aktiv" : "keine Wartung gemeldet", ".") : null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1.9fr 1fr",
      gap: "var(--space-4)",
      marginBottom: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Prognose vs. Ist",
    subtitle: "24 Monate, Verbrauch in kWh",
    icon: "trending-up",
    actions: /*#__PURE__*/React.createElement(Select, {
      size: "sm",
      options: ["24 Monate", "12 Monate"],
      style: {
        width: 130
      }
    }),
    footer: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", null, "Ist navy \xB7 Prognose cyan gestrichelt \xB7 Anomalie rot"), /*#__PURE__*/React.createElement("span", null, "\xB7"), /*#__PURE__*/React.createElement("span", null, D.metrik.modell, " ", D.metrik.version))
  }, /*#__PURE__*/React.createElement(Chart, {
    height: 280,
    layout: {
      yaxis: {
        title: {
          text: "Verbrauch (kWh)"
        }
      },
      margin: {
        l: 74,
        r: 18,
        t: 30,
        b: 42
      }
    },
    data: [{
      x: D.MONATE,
      y: z.historie,
      name: "Ist",
      mode: "lines+markers",
      type: "scatter",
      line: {
        color: ROLE.ist,
        width: 2
      },
      marker: {
        size: 5,
        color: ROLE.ist
      }
    }, {
      x: D.MONATE,
      y: prognoseSerie,
      name: "Prognose",
      mode: "lines",
      type: "scatter",
      line: {
        color: ROLE.prognose,
        width: 2,
        dash: "4,2"
      }
    }, {
      x: z.anomalieIdx.map(i => D.MONATE[i]),
      y: z.anomalieIdx.map(i => z.historie[i]),
      name: "Anomalie",
      mode: "markers",
      type: "scatter",
      marker: {
        size: 10,
        color: ROLE.anomalie,
        line: {
          width: 1.5,
          color: "#fff"
        }
      }
    }]
  })), /*#__PURE__*/React.createElement(Card, {
    title: "Residuen",
    subtitle: "Ist \u2212 Prognose, kWh",
    icon: "activity",
    footer: "Schwellwert ± " + D.fmt(schwelle) + " kWh"
  }, /*#__PURE__*/React.createElement(Chart, {
    height: 280,
    layout: {
      margin: {
        l: 66,
        r: 14,
        t: 12,
        b: 42
      },
      showlegend: false,
      yaxis: {
        title: {
          text: "Residuum (kWh)"
        },
        zeroline: true,
        zerolinecolor: "#B4BFCB",
        zerolinewidth: 1
      },
      shapes: [{
        type: "line",
        xref: "paper",
        x0: 0,
        x1: 1,
        y0: schwelle,
        y1: schwelle,
        line: {
          color: ROLE.schwelle,
          width: 1,
          dash: "3,3"
        }
      }, {
        type: "line",
        xref: "paper",
        x0: 0,
        x1: 1,
        y0: -schwelle,
        y1: -schwelle,
        line: {
          color: ROLE.schwelle,
          width: 1,
          dash: "3,3"
        }
      }]
    },
    data: [{
      type: "bar",
      x: D.MONATE,
      y: residuen,
      marker: {
        color: residuen.map(r => Math.abs(r) > schwelle ? ROLE.anomalie : ROLE.residuum)
      }
    }]
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1.3fr",
      gap: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Stammdaten & Monatsmerkmale",
    subtitle: "Bekannt zum Monatsbeginn",
    icon: "database",
    flush: true
  }, /*#__PURE__*/React.createElement(DataTable, {
    compact: true,
    rowKey: "k",
    columns: [{
      key: "k",
      label: "Merkmal"
    }, {
      key: "v",
      label: "Wert",
      numeric: true
    }],
    rows: [{
      k: "zaehler_id",
      v: z.zaehler_id
    }, {
      k: "kunde_id",
      v: z.kunde_id
    }, {
      k: "kundentyp",
      v: z.kundentyp
    }, {
      k: "vertragsleistung_kw",
      v: D.fmt(z.vertragsleistung_kw)
    }, {
      k: "arbeitstage",
      v: z.arbeitstage
    }, {
      k: "feiertage_im_monat",
      v: z.feiertage
    }, {
      k: "mittlere_temperatur_c",
      v: String(z.mittlere_temperatur_c).replace(".", ",")
    }, {
      k: "heiztage",
      v: D.fmt(z.heiztage)
    }, {
      k: "produktionsplan_index",
      v: String(z.produktionsplan_index).replace(".", ",")
    }, {
      k: "wartung_aktiv",
      v: z.wartung_aktiv
    }]
  })), /*#__PURE__*/React.createElement(Card, {
    title: "Einflussfaktoren",
    subtitle: "Feature Importance, Random-Forest-Regressor",
    icon: "chart-column",
    footer: "Gini-Importance, Training 2024"
  }, /*#__PURE__*/React.createElement(Chart, {
    height: 250,
    layout: {
      margin: {
        l: 210,
        r: 26,
        t: 10,
        b: 30
      },
      showlegend: false,
      xaxis: {
        title: {
          text: "Anteil"
        },
        showgrid: true,
        gridcolor: "#E4E9EF",
        showline: false
      },
      yaxis: {
        showgrid: false,
        tickfont: {
          family: "IBM Plex Sans, sans-serif",
          size: 11,
          color: "#4E5A68"
        }
      }
    },
    data: [{
      type: "bar",
      orientation: "h",
      y: D.featureImportance.map(x => x.feature).reverse(),
      x: D.featureImportance.map(x => x.wert).reverse(),
      marker: {
        color: ROLE.ist
      },
      text: D.featureImportance.map(x => String(x.wert).replace(".", ",")).reverse(),
      textposition: "outside",
      textfont: {
        family: "IBM Plex Sans, sans-serif",
        size: 11,
        color: "#4E5A68"
      }
    }]
  }))));
}
Object.assign(window, {
  ZaehlerDetailScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/ZaehlerDetailScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/energie-cockpit/data.js
try { (() => {
/* Mock data for the Energie-Cockpit UI kit.
   Shapes follow the data dictionary in uploads/IHK_Group6.pdf (700 Zähler × 24 Monate).
   Values are synthetic; the dataset itself was not read. */
(function () {
  const MONATE = [];
  for (let y = 2024; y <= 2025; y++) for (let m = 1; m <= 12; m++) MONATE.push(String(m).padStart(2, "0") + "/" + y);

  // deterministic pseudo-random
  let seed = 42;
  const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  const TEMP = [2.1, 3.4, 6.2, 10.8, 14.9, 18.2, 19.8, 19.1, 15.4, 11.2, 6.1, 3.2];
  const HEIZTAGE = [498, 442, 366, 232, 118, 34, 12, 18, 96, 218, 372, 470];
  function serie(base, amp, noise) {
    return MONATE.map((_, i) => {
      const s = 1 + amp * Math.cos(i % 12 / 12 * 2 * Math.PI);
      return Math.round(base * s * (1 + (rnd() - 0.5) * noise));
    });
  }
  const portfolioIst = serie(14500, 0.14, 0.05);
  const portfolioPrognose = portfolioIst.map((v, i) => Math.round(v * (1 + (rnd() - 0.5) * 0.045)));
  const portfolioBandLo = portfolioPrognose.map(v => Math.round(v * 0.955));
  const portfolioBandHi = portfolioPrognose.map(v => Math.round(v * 1.045));
  const TYPEN = ["Gewerbe", "Industrie", "Kommunal"];
  const SEV = [{
    status: "critical",
    label: "Kritisch"
  }, {
    status: "warn",
    label: "Auffällig"
  }, {
    status: "info",
    label: "Hinweis"
  }, {
    status: "ok",
    label: "In Toleranz"
  }];
  const zaehler = [];
  const ids = ["ZW-04412", "ZW-01187", "ZW-06021", "ZW-00932", "ZW-05540", "ZW-02218", "ZW-03771", "ZW-06904", "ZW-00145", "ZW-04087", "ZW-02993", "ZW-05316", "ZW-01620", "ZW-06455", "ZW-03208", "ZW-04761", "ZW-00578", "ZW-02044"];
  const kunden = ["Hafenterminal Nord", "Kühlhaus Elbkai", "Bezirksamt Westhafen", "Werft Süd", "Containerlager 7", "Stadtbad Westhafen", "Metallbau Deichtor", "Schulzentrum Kai", "Logistikpark A", "Pumpwerk Ost", "Bäckerei Hansen", "Klinikum Westhafen", "Sägewerk Elbe", "Wasserwerk Nord", "Druckerei Kaiser", "Umspannwerk 4", "Kfz-Zentrum Hafen", "Rechenzentrum Kai"];
  const abw = [38.2, -13.0, -1.6, 1.4, 31.7, -24.8, 19.4, -3.2, 22.1, -28.4, 2.8, 41.6, -19.7, 0.9, 16.3, -2.1, 26.9, -35.2];
  ids.forEach((id, i) => {
    const typ = TYPEN[i % 3];
    const base = typ === "Industrie" ? 780000 : typ === "Gewerbe" ? 210000 : 92000;
    const hist = serie(base / 1000, 0.18, 0.06).map(v => v * 1000);
    const prognose = Math.round(base * (1 + (rnd() - 0.5) * 0.1));
    const ist = Math.round(prognose * (1 + abw[i] / 100));
    const a = Math.abs(abw[i]);
    const sev = a > 30 ? SEV[0] : a > 15 ? SEV[1] : a > 5 ? SEV[2] : SEV[3];
    hist[23] = ist;
    zaehler.push({
      zaehler_id: id,
      kunde_id: "K-" + (1200 + i * 37),
      kunde: kunden[i],
      kundentyp: typ,
      vertragsleistung_kw: [250, 1600, 400, 120, 900, 180, 630, 95, 1250, 210, 75, 1800, 540, 320, 260, 2200, 150, 3200][i],
      prognose_kwh: prognose,
      ist_kwh: ist,
      abweichung_pct: abw[i],
      residuum_kwh: ist - prognose,
      status: sev.status,
      statusLabel: sev.label,
      wartung_aktiv: i % 7 === 0 ? 1 : 0,
      arbeitstage: 21,
      feiertage: 1,
      mittlere_temperatur_c: TEMP[2],
      heiztage: HEIZTAGE[2],
      produktionsplan_index: +(0.85 + rnd() * 0.4).toFixed(2),
      historie: hist,
      anomalieIdx: a > 15 ? [23] : [],
      geprueft: i % 5 === 0
    });
  });
  const anomalienNachTyp = {
    Gewerbe: 47,
    Industrie: 58,
    Kommunal: 23
  };
  const anomalienVerlauf = [64, 71, 58, 66, 74, 69, 81, 77, 88, 95, 112, 128];
  const featureImportance = [{
    feature: "letzte_3_monate_durchschnitt_kwh",
    wert: 0.312
  }, {
    feature: "vorjahr_monat_verbrauch_kwh",
    wert: 0.208
  }, {
    feature: "vertragsleistung_kw",
    wert: 0.147
  }, {
    feature: "heiztage",
    wert: 0.121
  }, {
    feature: "produktionsplan_index",
    wert: 0.094
  }, {
    feature: "arbeitstage",
    wert: 0.058
  }, {
    feature: "mittlere_temperatur_c",
    wert: 0.041
  }, {
    feature: "wartung_aktiv",
    wert: 0.019
  }];
  const datenqualitaet = [{
    spalte: "verbrauch_kwh",
    typ: "Gemischt",
    befund: "412 Werte als MWh-Text",
    anteil: "2,5 %",
    status: "critical",
    massnahme: "Einheit vereinheitlicht auf kWh"
  }, {
    spalte: "monat",
    typ: "Text",
    befund: "3 Datumsformate",
    anteil: "100 %",
    status: "warn",
    massnahme: "Parsing auf MM/JJJJ"
  }, {
    spalte: "kundentyp",
    typ: "Text",
    befund: "9 Schreibvarianten",
    anteil: "1,1 %",
    status: "warn",
    massnahme: "Mapping auf 3 Klassen"
  }, {
    spalte: "vormonat_verbrauch_kwh",
    typ: "Zahl",
    befund: "700 NaN (erster Monat)",
    anteil: "4,2 %",
    status: "info",
    massnahme: "Erwartet, Zeile behalten"
  }, {
    spalte: "vorjahr_monat_verbrauch_kwh",
    typ: "Zahl",
    befund: "8.400 NaN (2024)",
    anteil: "50,0 %",
    status: "info",
    massnahme: "Erwartet, Feature nur 2025"
  }, {
    spalte: "verbrauch_kwh",
    typ: "Zahl",
    befund: "11 negative Verbräuche",
    anteil: "0,07 %",
    status: "critical",
    massnahme: "Entfernt, Ticket an Netzmanagement"
  }, {
    spalte: "zaehler_id",
    typ: "Text",
    befund: "38 Duplikate",
    anteil: "0,23 %",
    status: "warn",
    massnahme: "Dedupliziert nach zaehler_id + monat"
  }, {
    spalte: "mittlere_temperatur_c",
    typ: "Zahl",
    befund: "keine Auffälligkeiten",
    anteil: "0 %",
    status: "ok",
    massnahme: "—"
  }];
  const beschaffung = [{
    monat: "04/2025",
    prognose_mwh: 14820,
    band: "± 640",
    beschafft_mwh: 14500,
    spot_mwh: 320,
    kosten_eur: "1.482.000",
    status: "warn"
  }, {
    monat: "05/2025",
    prognose_mwh: 13940,
    band: "± 610",
    beschafft_mwh: 13900,
    spot_mwh: 40,
    kosten_eur: "1.394.000",
    status: "ok"
  }, {
    monat: "06/2025",
    prognose_mwh: 13210,
    band: "± 590",
    beschafft_mwh: 13200,
    spot_mwh: 10,
    kosten_eur: "1.321.000",
    status: "ok"
  }, {
    monat: "07/2025",
    prognose_mwh: 13060,
    band: "± 620",
    beschafft_mwh: 12800,
    spot_mwh: 260,
    kosten_eur: "1.306.000",
    status: "warn"
  }, {
    monat: "08/2025",
    prognose_mwh: 13180,
    band: "± 615",
    beschafft_mwh: 13100,
    spot_mwh: 80,
    kosten_eur: "1.318.000",
    status: "ok"
  }, {
    monat: "09/2025",
    prognose_mwh: 13890,
    band: "± 650",
    beschafft_mwh: 13600,
    spot_mwh: 290,
    kosten_eur: "1.389.000",
    status: "warn"
  }];
  const metrik = {
    r2: "0,912",
    mae: "4.180",
    rmse: "7.940",
    schwelle: "18,0",
    modell: "Random-Forest-Regressor",
    version: "v2.3",
    stand: "01.04.2025, 06:00"
  };
  window.SWWData = {
    MONATE,
    TEMP,
    HEIZTAGE,
    portfolioIst,
    portfolioPrognose,
    portfolioBandLo,
    portfolioBandHi,
    zaehler,
    anomalienNachTyp,
    anomalienVerlauf,
    featureImportance,
    datenqualitaet,
    beschaffung,
    metrik,
    fmt: n => new Intl.NumberFormat("de-DE").format(Math.round(n)),
    fmtPct: n => (n > 0 ? "+" : n < 0 ? "−" : "") + new Intl.NumberFormat("de-DE", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(Math.abs(n)) + " %"
  };
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/energie-cockpit/data.js", error: String((e && e.message) || e) }); }

__ds_ns.SEVERITY = __ds_scope.SEVERITY;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.ICON_BASE = __ds_scope.ICON_BASE;

__ds_ns.DOMAIN_ICONS = __ds_scope.DOMAIN_ICONS;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.KUNDENTYP_COLOR = __ds_scope.KUNDENTYP_COLOR;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.DataTable = __ds_scope.DataTable;

__ds_ns.KpiTile = __ds_scope.KpiTile;

__ds_ns.Sparkline = __ds_scope.Sparkline;

__ds_ns.StatusDot = __ds_scope.StatusDot;

__ds_ns.Alert = __ds_scope.Alert;

__ds_ns.Dialog = __ds_scope.Dialog;

__ds_ns.EmptyState = __ds_scope.EmptyState;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Switch = __ds_scope.Switch;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.PageHeader = __ds_scope.PageHeader;

__ds_ns.SidebarNav = __ds_scope.SidebarNav;

__ds_ns.Tabs = __ds_scope.Tabs;

})();
