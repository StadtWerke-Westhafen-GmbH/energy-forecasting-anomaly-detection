const {
  PageHeader, Card, KpiTile, Tag, Badge, Button, Alert, DataTable,
  KUNDENTYP_COLOR,
} = window.StadtWerkeWesthafenDesignSystem_acd94c;

function formatNumber(value, digits = 0) {
  return Number(value).toLocaleString("de-DE", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function signedValue(value, digits = 0, unit = "") {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";
  return `${sign}${formatNumber(Math.abs(value), digits)}${unit}`;
}

function optionLabel(options, value) {
  return options.find((option) => option.value === value)?.label || value || "Unklar";
}

function ZaehlerDetailScreen({ alertId, decisions = {}, onBack, onReview }) {
  const D = window.SWWAnomalyData;
  const alert = D.alerts.find((item) => item.alert_id === alertId) || D.alerts[0];
  const meter = D.meters[alert.zaehler_id];
  const decision = decisions[alert.alert_id] || { workflow: "nicht_bewertet" };
  const scoreRows = meter.series.filter((item) => item.score != null);
  const anomalyRows = meter.series.filter((item) => item.is_alert);
  const ReviewBadge = window.ReviewBadge;

  const contextRows = [
    { key: "Kundentyp", value: alert.kundentyp },
    { key: "Kunden-ID", value: alert.kunde_id },
    { key: "Vertragsleistung", value: `${formatNumber(alert.vertragsleistung_kw)} kW` },
    { key: "Wartung gemeldet", value: alert.wartung_aktiv ? "ja" : "nein" },
    { key: "Produktionsplan-Index", value: formatNumber(alert.produktionsplan_index, 2) },
    { key: "Arbeitstage", value: String(alert.arbeitstage) },
    { key: "Feiertage", value: String(alert.feiertage) },
    { key: "Kapazitäts-Plausibilitätsflag", value: alert.dq_capacity ? "ja" : "nein" },
    { key: "Hinweise für diesen Zähler", value: String(alert.meter_alert_count) },
  ];

  return (
    <div data-testid="anomaly-case-file">
      <PageHeader eyebrow="Fallakte"
        title={`${alert.zaehler_id} · ${alert.month_label}`}
        subtitle={`${alert.kunde_id} · ${alert.direction}. Das Modell priorisiert den Fall; die Ursache wird fachlich geprüft.`}
        meta={<>
          <Tag dotColor={KUNDENTYP_COLOR[alert.kundentyp]}>{alert.kundentyp}</Tag>
          <Badge status="critical" icon="triangle-alert">Score {formatNumber(alert.score, 2)}</Badge>
          <ReviewBadge workflow={decision.workflow} />
          {alert.wartung_aktiv ? <Tag icon="wrench">Wartung gemeldet</Tag> : null}
          {alert.dq_capacity ? <Badge status="critical" icon="database">DQ-Flag</Badge> : null}
        </>}
        actions={<>
          <Button variant="secondary" icon="arrow-left" onClick={onBack}>Zur Prüfwarteschlange</Button>
          <Button variant="primary" icon="clipboard-check" onClick={() => onReview(alert)}>Bewertung dokumentieren</Button>
        </>} />

      <div className="anomaly-kpi-grid" style={{ marginBottom: "var(--space-4)" }}>
        <KpiTile label={`Ist ${alert.month_label}`} value={formatNumber(alert.actual_kwh, 0)} unit="kWh" icon="zap" />
        <KpiTile label={`Prognose ${alert.month_label}`} value={formatNumber(alert.forecast_kwh, 0)} unit="kWh" icon="trending-up"
          reference="Random Forest · Vollaststunden" />
        <KpiTile label="Abweichung" value={signedValue(alert.residual_kwh, 0)} unit="kWh" icon="activity"
          delta={signedValue(alert.deviation_pct, 1, " %")} deltaTone="bad" reference="gegenüber Prognose" />
        <KpiTile label="Anomalie-Score" value={formatNumber(alert.score, 2)} icon="triangle-alert"
          reference={`Schwelle ${formatNumber(D.meta.threshold_score, 2)}`} />
      </div>

      <Alert status="warn" title="Warum wurde dieser Fall markiert?" style={{ marginBottom: "var(--space-4)" }}>
        Der robust normierte Log-Residual-Score {formatNumber(alert.score, 2)} liegt über der aus November und Dezember 2024 kalibrierten Schwelle {formatNumber(D.meta.threshold_score, 2)}. Ist {formatNumber(alert.actual_kwh, 2)} kWh und Prognose {formatNumber(alert.forecast_kwh, 2)} kWh unterscheiden sich um {signedValue(alert.residual_kwh, 2, " kWh")} beziehungsweise {signedValue(alert.deviation_pct, 2, " %")}.
      </Alert>

      {alert.dq_capacity ? (
        <Alert status="critical" title="Zusätzliches Datenqualitätsflag" style={{ marginBottom: "var(--space-4)" }}>
          Der Monatsverbrauch überschreitet die aus Vertragsleistung und Monatsstunden abgeleitete Plausibilitätsgrenze. Prüfen Sie zuerst Messwert, Einheit und Stammdaten, bevor Sie den Verbrauch betrieblich interpretieren.
        </Alert>
      ) : null}
      {alert.wartung_aktiv ? (
        <Alert status="info" title="Wartung als Prüfkontext" style={{ marginBottom: "var(--space-4)" }}>
          Für diesen Monat ist Wartung gemeldet. Das ist eine plausible Prüfhypothese, aber kein vom Modell bewiesener Grund. Gleichen Sie Zeitraum und tatsächliche Auswirkung mit dem Fachbereich ab.
        </Alert>
      ) : null}

      <div className="anomaly-detail-grid" style={{ marginBottom: "var(--space-4)" }}>
        <Card title="Ist und Prognose" subtitle="Ist 01/2024–12/2025 · echte Out-of-time-Prognosen ab 11/2024" icon="trending-up"
          footer={<><span>Ist navy, durchgezogen</span><span>·</span><span>Prognose cyan, gestrichelt</span><span>·</span><span>Prüfhinweis rot</span></>}>
          <Chart height={310} layout={{
            margin: { l: 76, r: 20, t: 18, b: 52 },
            yaxis: { title: { text: "Verbrauch (kWh)" }, rangemode: "tozero" },
            xaxis: { title: { text: "Monat" }, tickangle: 0 },
          }} data={[
            { type: "scatter", mode: "lines+markers", name: "Ist", x: meter.series.map((item) => item.month_label), y: meter.series.map((item) => item.actual_kwh), line: { color: ROLE.ist, width: 2 }, marker: { size: 4, color: ROLE.ist } },
            { type: "scatter", mode: "lines", name: "Prognose", x: meter.series.map((item) => item.month_label), y: meter.series.map((item) => item.forecast_kwh), connectgaps: false, line: { color: ROLE.prognose, width: 2, dash: "4,2" } },
            { type: "scatter", mode: "markers", name: "Prüfhinweis", x: anomalyRows.map((item) => item.month_label), y: anomalyRows.map((item) => item.actual_kwh), marker: { size: 10, color: ROLE.anomalie, line: { width: 2, color: "#fff" } } },
          ]} />
        </Card>

        <Card title="Anomalie-Score" subtitle="Kalibrierung 11/2024–12/2024 · Benchmark 01/2025–12/2025" icon="activity"
          footer={`Score ist keine Wahrscheinlichkeit · feste Schwelle ${formatNumber(D.meta.threshold_score, 2)}`}>
          <Chart height={310} layout={{
            margin: { l: 58, r: 18, t: 18, b: 52 }, showlegend: false,
            yaxis: { title: { text: "Score" }, rangemode: "tozero" },
            xaxis: { title: { text: "Monat" } },
            shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: D.meta.threshold_score, y1: D.meta.threshold_score, line: { color: ROLE.schwelle, width: 2, dash: "3,3" } }],
            annotations: [{ xref: "paper", x: 1, xanchor: "right", y: D.meta.threshold_score, yanchor: "bottom", text: `Schwelle ${formatNumber(D.meta.threshold_score, 2)}`, showarrow: false, font: { color: ROLE.schwelle, size: 11 } }],
          }} data={[{
            type: "bar", x: scoreRows.map((item) => item.month_label), y: scoreRows.map((item) => item.score),
            marker: { color: scoreRows.map((item) => item.is_alert ? ROLE.anomalie : ROLE.residuum) },
            customdata: scoreRows.map((item) => item.phase),
            hovertemplate: "%{x}<br>Score %{y:.2f}<br>%{customdata}<extra></extra>",
          }]} />
        </Card>
      </div>

      <div className="anomaly-context-grid">
        <Card title="Kontext zum Prognosestichtag" subtitle="Kontext unterstützt die Prüfung, beweist aber keine Ursache" icon="database" flush>
          <DataTable compact rowKey="key" columns={[
            { key: "key", label: "Merkmal" },
            { key: "value", label: "Wert", numeric: true },
          ]} rows={contextRows} />
        </Card>

        <Card title="Menschliche Bewertung" subtitle="Lokaler Demonstrationsstatus · keine Ticketübermittlung" icon="clipboard-check"
          actions={<ReviewBadge workflow={decision.workflow} />}>
          {decision.workflow === "nicht_bewertet" ? (
            <p style={{ marginTop: 0, color: "var(--text-secondary)" }}>
              Dieser Hinweis wurde noch nicht bewertet. Prüfen Sie Messwert, betriebliche Zusammenhänge und möglichen Handlungsbedarf getrennt.
            </p>
          ) : (
            <dl className="anomaly-review-summary">
              <div><dt>Messwert gültig</dt><dd>{optionLabel(D.review_options.tri_state, decision.measurement)}</dd></div>
              <div><dt>Abweichung erklärt</dt><dd>{optionLabel(D.review_options.tri_state, decision.explained)}</dd></div>
              <div><dt>Ursache</dt><dd>{decision.cause || "Noch ungeklärt"}</dd></div>
              <div><dt>Handlungsbedarf</dt><dd>{decision.action || "Noch offen"}</dd></div>
              <div><dt>Verantwortlich</dt><dd>{decision.owner || "nicht zugewiesen"}</dd></div>
              {decision.note ? <div className="wide"><dt>Notiz</dt><dd>{decision.note}</dd></div> : null}
              {decision.updated_at ? <div className="wide"><dt>Lokaler Zeitstempel</dt><dd>{new Date(decision.updated_at).toLocaleString("de-DE")}</dd></div> : null}
            </dl>
          )}
          <Button variant="primary" icon="clipboard-check" onClick={() => onReview(alert)}>
            {decision.workflow === "nicht_bewertet" ? "Bewertung beginnen" : "Bewertung bearbeiten"}
          </Button>
        </Card>
      </div>

      <Alert status="neutral" title="Grenze der Aussage" style={{ marginTop: "var(--space-4)" }}>
        {D.meta.caveat} Ohne bestätigte Falllabels lassen sich Precision, Recall und die Zahl übersehener Störungen nicht seriös angeben.
      </Alert>
    </div>
  );
}

Object.assign(window, { ZaehlerDetailScreen });
