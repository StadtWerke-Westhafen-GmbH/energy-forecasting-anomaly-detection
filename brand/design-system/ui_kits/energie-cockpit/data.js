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
      const s = 1 + amp * Math.cos(((i % 12) / 12) * 2 * Math.PI);
      return Math.round(base * s * (1 + (rnd() - 0.5) * noise));
    });
  }

  const portfolioIst = serie(14500, 0.14, 0.05);
  const portfolioPrognose = portfolioIst.map((v, i) => Math.round(v * (1 + (rnd() - 0.5) * 0.045)));
  const portfolioBandLo = portfolioPrognose.map((v) => Math.round(v * 0.955));
  const portfolioBandHi = portfolioPrognose.map((v) => Math.round(v * 1.045));

  const TYPEN = ["Gewerbe", "Industrie", "Kommunal"];
  const SEV = [
    { status: "critical", label: "Kritisch" },
    { status: "warn", label: "Auffällig" },
    { status: "info", label: "Hinweis" },
    { status: "ok", label: "In Toleranz" },
  ];

  const zaehler = [];
  const ids = ["ZW-04412","ZW-01187","ZW-06021","ZW-00932","ZW-05540","ZW-02218","ZW-03771","ZW-06904","ZW-00145","ZW-04087","ZW-02993","ZW-05316","ZW-01620","ZW-06455","ZW-03208","ZW-04761","ZW-00578","ZW-02044"];
  const kunden = ["Hafenterminal Nord","Kühlhaus Elbkai","Bezirksamt Westhafen","Werft Süd","Containerlager 7","Stadtbad Westhafen","Metallbau Deichtor","Schulzentrum Kai","Logistikpark A","Pumpwerk Ost","Bäckerei Hansen","Klinikum Westhafen","Sägewerk Elbe","Wasserwerk Nord","Druckerei Kaiser","Umspannwerk 4","Kfz-Zentrum Hafen","Rechenzentrum Kai"];
  const abw = [38.2, -13.0, -1.6, 1.4, 31.7, -24.8, 19.4, -3.2, 22.1, -28.4, 2.8, 41.6, -19.7, 0.9, 16.3, -2.1, 26.9, -35.2];

  ids.forEach((id, i) => {
    const typ = TYPEN[i % 3];
    const base = typ === "Industrie" ? 780000 : typ === "Gewerbe" ? 210000 : 92000;
    const hist = serie(base / 1000, 0.18, 0.06).map((v) => v * 1000);
    const prognose = Math.round(base * (1 + (rnd() - 0.5) * 0.1));
    const ist = Math.round(prognose * (1 + abw[i] / 100));
    const a = Math.abs(abw[i]);
    const sev = a > 30 ? SEV[0] : a > 15 ? SEV[1] : a > 5 ? SEV[2] : SEV[3];
    hist[23] = ist;
    zaehler.push({
      zaehler_id: id, kunde_id: "K-" + (1200 + i * 37), kunde: kunden[i], kundentyp: typ,
      vertragsleistung_kw: [250, 1600, 400, 120, 900, 180, 630, 95, 1250, 210, 75, 1800, 540, 320, 260, 2200, 150, 3200][i],
      prognose_kwh: prognose, ist_kwh: ist, abweichung_pct: abw[i],
      residuum_kwh: ist - prognose, status: sev.status, statusLabel: sev.label,
      wartung_aktiv: i % 7 === 0 ? 1 : 0, arbeitstage: 21, feiertage: 1,
      mittlere_temperatur_c: TEMP[2], heiztage: HEIZTAGE[2],
      produktionsplan_index: +(0.85 + rnd() * 0.4).toFixed(2),
      historie: hist,
      anomalieIdx: a > 15 ? [23] : [],
      geprueft: i % 5 === 0,
    });
  });

  const anomalienNachTyp = { Gewerbe: 47, Industrie: 58, Kommunal: 23 };
  const anomalienVerlauf = [64, 71, 58, 66, 74, 69, 81, 77, 88, 95, 112, 128];

  const featureImportance = [
    { feature: "letzte_3_monate_durchschnitt_kwh", wert: 0.312 },
    { feature: "vorjahr_monat_verbrauch_kwh", wert: 0.208 },
    { feature: "vertragsleistung_kw", wert: 0.147 },
    { feature: "heiztage", wert: 0.121 },
    { feature: "produktionsplan_index", wert: 0.094 },
    { feature: "arbeitstage", wert: 0.058 },
    { feature: "mittlere_temperatur_c", wert: 0.041 },
    { feature: "wartung_aktiv", wert: 0.019 },
  ];

  const datenqualitaet = [
    { spalte: "verbrauch_kwh", typ: "Gemischt", befund: "412 Werte als MWh-Text", anteil: "2,5 %", status: "critical", massnahme: "Einheit vereinheitlicht auf kWh" },
    { spalte: "monat", typ: "Text", befund: "3 Datumsformate", anteil: "100 %", status: "warn", massnahme: "Parsing auf MM/JJJJ" },
    { spalte: "kundentyp", typ: "Text", befund: "9 Schreibvarianten", anteil: "1,1 %", status: "warn", massnahme: "Mapping auf 3 Klassen" },
    { spalte: "vormonat_verbrauch_kwh", typ: "Zahl", befund: "700 NaN (erster Monat)", anteil: "4,2 %", status: "info", massnahme: "Erwartet, Zeile behalten" },
    { spalte: "vorjahr_monat_verbrauch_kwh", typ: "Zahl", befund: "8.400 NaN (2024)", anteil: "50,0 %", status: "info", massnahme: "Erwartet, Feature nur 2025" },
    { spalte: "verbrauch_kwh", typ: "Zahl", befund: "11 negative Verbräuche", anteil: "0,07 %", status: "critical", massnahme: "Entfernt, Ticket an Netzmanagement" },
    { spalte: "zaehler_id", typ: "Text", befund: "38 Duplikate", anteil: "0,23 %", status: "warn", massnahme: "Dedupliziert nach zaehler_id + monat" },
    { spalte: "mittlere_temperatur_c", typ: "Zahl", befund: "keine Auffälligkeiten", anteil: "0 %", status: "ok", massnahme: "—" },
  ];

  const beschaffung = [
    { monat: "04/2025", prognose_mwh: 14820, band: "± 640", beschafft_mwh: 14500, spot_mwh: 320, kosten_eur: "1.482.000", status: "warn" },
    { monat: "05/2025", prognose_mwh: 13940, band: "± 610", beschafft_mwh: 13900, spot_mwh: 40, kosten_eur: "1.394.000", status: "ok" },
    { monat: "06/2025", prognose_mwh: 13210, band: "± 590", beschafft_mwh: 13200, spot_mwh: 10, kosten_eur: "1.321.000", status: "ok" },
    { monat: "07/2025", prognose_mwh: 13060, band: "± 620", beschafft_mwh: 12800, spot_mwh: 260, kosten_eur: "1.306.000", status: "warn" },
    { monat: "08/2025", prognose_mwh: 13180, band: "± 615", beschafft_mwh: 13100, spot_mwh: 80, kosten_eur: "1.318.000", status: "ok" },
    { monat: "09/2025", prognose_mwh: 13890, band: "± 650", beschafft_mwh: 13600, spot_mwh: 290, kosten_eur: "1.389.000", status: "warn" },
  ];

  const metrik = { r2: "0,912", mae: "4.180", rmse: "7.940", schwelle: "18,0", modell: "Random-Forest-Regressor", version: "v2.3", stand: "01.04.2025, 06:00" };

  window.SWWData = {
    MONATE, TEMP, HEIZTAGE, portfolioIst, portfolioPrognose, portfolioBandLo, portfolioBandHi,
    zaehler, anomalienNachTyp, anomalienVerlauf, featureImportance, datenqualitaet, beschaffung, metrik,
    fmt: (n) => new Intl.NumberFormat("de-DE").format(Math.round(n)),
    fmtPct: (n) => (n > 0 ? "+" : n < 0 ? "−" : "") + new Intl.NumberFormat("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(Math.abs(n)) + " %",
  };
})();
