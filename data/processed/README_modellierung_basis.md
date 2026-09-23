# Schnittstellenvereinbarung — `modellierung_basis.csv`

**Von:** EDA (Patrick) · **An:** Modellierung · **Stand:** 23.09.2026 (Fassung 3 — Spalte `split` kam dazu, `vertragsleistung_kw` ist kein Merkmal)
**Erzeugt von:** `eda_4.ipynb`, Abschnitt 7. Die Datei wird bei jedem Notebook-Lauf neu
geschrieben; sie ist ein Ergebnis, keine Quelle.
**Quelle:** `data/processed/verbrauch_bereinigt.csv` (unverändert, read-only).

---

## 1. Was die Datei ist

16.800 Zeilen × 19 Spalten, **eine Zeile je Zähler und Monat** (700 Zähler × 24 Monate,
2024–2025), sortiert nach `zaehler_id, monat`. Vollständiges Panel, keine Lücke in der
Zeitachse, Zielgröße ohne Fehlwert.

**Es ist keine Zeile gelöscht.** Welche Zeilen ins Training dürfen, entscheidet die
Modellierung über die beiden Kennzeichen-Spalten (Abschnitt 4). Das ist Absicht: Die
Prüfliste der Ausreißer bleibt so erhalten und die EDA nachvollziehbar.

**Format:** CSV, UTF-8, Komma als Trennzeichen, Punkt als Dezimalzeichen, kein Index.
`monat` als ISO-Datum auf dem Monatsersten (`2024-01-01`), Wahrheitswerte als
`True`/`False`, Fehlwerte als leeres Feld.

```python
d = pd.read_csv("data/processed/modellierung_basis.csv", parse_dates=["monat"])
d["kundentyp"] = pd.Categorical(d["kundentyp"], ["Gewerbe", "Industrie", "Kommunal"])
```

---

## 2. Die 19 Spalten in vier Rollen

### Schlüssel
| Spalte | Bedeutung |
|---|---|
| `zaehler_id` | 700 Zähler, Gruppierungsschlüssel |
| `monat` | Zeitachse, trennt Training von Test |
| `jahr` | 2024 oder 2025 |
| `split` | **`train` (8.390) · `test` (8.400) · `ausschluss` (10)** — fertig zum Filtern, siehe Abschnitt 4 |

### Zielgröße
| Spalte | Bedeutung |
|---|---|
| `vollaststunden` | **Trainingsziel.** `verbrauch_kwh / vertragsleistung_kw` — Verbrauch je kW Anschlussleistung |
| `verbrauch_kwh` | **Bewertungsskala.** Nur zum Zurückrechnen und Bewerten, nie als Merkmal |
| `vertragsleistung_kw` | **Rücktransformation, kein Merkmal.** 20 bis 1.067 kW |

Begründung der Normierung: Gegen den rohen Verbrauch korreliert praktisch nur die
Anschlussgröße (Spearman 0,90), alle Betriebs- und Wettergrößen liegen unter 0,15. Normiert
fällt die Vertragsleistung auf 0,07 und jeder echte Treiber verdoppelt bis verdreifacht
sich. Die Niveauspanne zwischen kleinstem und größtem Zähler sinkt von Faktor 21,8 auf 2,7,
die Schiefe von 3,44 auf 1,18. Beleg: Abbildungen **A1** und **A2**.

**Rücktransformation:** `prognose_kwh = prognose_vollaststunden × vertragsleistung_kw`.
Exakt, kein Smearing-Korrekturfaktor nötig — das war ein Argument gegen eine zusätzliche
Log-Transformation.

### Die 9 Merkmale
| Spalte | Typ | Bemerkung |
|---|---|---|
| `kundentyp` | kategorial, 3 Stufen | Gewerbe 9.024 / Industrie 5.424 / Kommunal 2.352 Zeilen |
| `monat_idx` | ganzzahlig 1–12 | Monat des Jahres, trägt den Jahresgang |
| `arbeitstage` | ganzzahlig | Kalender, je Monat konstant |
| `feiertage_im_monat` | ganzzahlig | Kalender, je Monat konstant |
| `heizgradtage` | ganzzahlig | Wetter, **zählerspezifisch** (im Januar 2024 allein 74 verschiedene Werte) |
| `produktionsplan_index` | Gleitkomma | stärkster Betriebs-Treiber (Spearman 0,33 normiert) |
| `wartung_aktiv` | Wahrheitswert | 5,8 % der Monate |
| `vormonat_vls` | Gleitkomma | Lag 1, **normiert** |
| `letzte_3_monate_vls` | Gleitkomma | Mittel der Lags 1–3, **normiert** |

Die Lag-Spalten sind bewusst normiert (`/ vertragsleistung_kw`). Roh übergeben würden sie
die Anschlussgröße durch die Hintertür wieder ins Modell tragen — genau das, was die
Normierung der Zielgröße entfernt hat.

Alle neun sind **zum Monatsbeginn bekannt**, wie der Brief es verlangt.

**Warum `vertragsleistung_kw` kein Merkmal ist.** Sie steckt bereits im Nenner der
Zielgröße. Die Prüfung, ob sie daneben noch eigene Information trägt — ob große Anschlüsse
systematisch anders ausgelastet sind als kleine — fällt negativ aus: Über zehn Größendezile
schwanken die Mediane zwischen 150 und 184 Vollaststunden (Faktor 1,23, nicht monoton),
Spearman 0,089; je Kundentyp getrennt +0,03 / −0,03 / +0,06. Der kleine Resteffekt ist
Typ-Mix, und `kundentyp` ist Merkmal. Dazu ein Risiko: 271 verschiedene kW-Werte auf 700
Zähler, **130 Zähler sind darüber eindeutig identifizierbar** — als Merkmal wirkt die Spalte
teilweise wie eine Zähler-ID, über die ein Baummodell Zählerniveaus aus 2024 auswendig
lernen kann. Das Zählerniveau liegt ohnehin zeitveränderlich in `vormonat_vls` und
`letzte_3_monate_vls`.

**Leakage ist es dabei nicht:** Die Vertragsleistung steht im Vertrag, ist Monate im
Voraus bekannt und wird nicht aus dem Verbrauch berechnet. Sie entfällt, weil sie nichts
beiträgt — nicht, weil sie etwas verrät. Beleg: Abbildung **A2** und die Dezil-Tabelle
darunter.

### Baseline und Kennzeichen
| Spalte | Bedeutung |
|---|---|
| `vorjahr_vls` | **Kein Merkmal.** Vergleichsmaßstab „Verbrauch wie im Vorjahresmonat". In 2024 vollständig leer, in 2025 vollständig gefüllt |
| `anomalie` | 1.400 Zeilen über dem p95 des eigenen Zählers — **Referenzmenge, keine Ground Truth** |
| `unmoeglich` | 20 Zeilen, negativ oder über 100 % Auslastung — belegte Messfehler |

---

## 3. Was schon erledigt ist

1. **Drei Sentinel-Werte rekonstruiert.** Die Platzhalter 0 / −50 / −1000 standen im Export
   als Fehlwert; der echte Messwert stand in `vormonat_verbrauch_kwh` der Folgezeile.
   Befund an das Cleaning, in der Quelldatei nicht verändert.
2. **Lag-Bereinigung.** Jeder Monatswert steht im Panel zweimal — als Zielwert seiner
   eigenen Zeile und als Lag der folgenden (in 16.091 von 16.100 prüfbaren Fällen exakt
   weitergetragen). Die 20 unmöglichen Werte tauchten deshalb in **19** Folgezeilen als
   `vormonat_vls` und in **57** als `letzte_3_monate_vls` wieder auf. Diese Einträge stehen
   jetzt auf `NaN`: Ein Wert, den das Training als Messfehler ausschließt, darf nicht über
   die Lag-Spalte zurückkommen.
3. **Leakage-Prüfung.** `faktor`, `median_vls`, `auslastung_prozent` und
   `stunden_im_monat` enthalten den Zielwert desselben Monats. Sie bleiben in der EDA und
   sind hier nicht enthalten; eine `assert`-Zeile im Notebook prüft das bei jedem Lauf.
4. **Gestrichene Spalten:** `mittlere_temperatur_c` (Spearman −1,00 zu `heizgradtage`, 503
   Lücken mehr), `vorjahr_monat_verbrauch_kwh` als Merkmal (im Trainingsjahr durchgehend
   leer → wurde Baseline), `kunde_id` (1:1 zur `zaehler_id`).

---

## 4. Train-Test-Split

**Zeitlich, wie im Brief vorgegeben — kein Zufallssplit.**

**Der Split liegt als Spalte `split` bei** — die Regel muss nicht nachgebaut werden, und
sie ist damit in beiden Notebooks garantiert dieselbe.

| `split` | Bedeutung | Zeilen |
|---|---|---|
| `train` | 2024 ohne die dort liegenden unmöglichen Zeilen | **8.390** |
| `test` | 2025 vollständig | **8.400** |
| `ausschluss` | die 10 unmöglichen Zeilen aus 2024 | **10** |

Zweitauswertung auf dem Test: `split == "test"` **und nicht** `anomalie` → **7.729** Zeilen.

Die 10 unmöglichen Zeilen aus **2025** stehen bewusst auf `test`, nicht auf `ausschluss` —
der Test soll die Wirklichkeit abbilden. Zwei `assert`-Zeilen im Notebook sichern das ab.

Der Test bleibt absichtlich vollständig — er soll die Wirklichkeit abbilden, inklusive der
671 dort markierten Zeilen. Die zweite Auswertung ohne sie zeigt, wie stark die Ausreißer
den Fehler treiben.

**Warum kein Zufallssplit:** `vormonat_vls` einer Zeile ist der Zielwert der Vorzeile. Bei
zufälliger Aufteilung stünde der Zielwert einer Testzeile als Merkmal in einer
Trainingszeile — das Modell sähe die Antwort. Wird eine Validierung gebraucht, die letzten
Monate aus 2024 abtrennen (z. B. Oktober–Dezember), nie über beide Jahre mischen.

---

## 5. Was die Modellierung tut

```python
MERKMALE = ["kundentyp", "monat_idx", "arbeitstage", "feiertage_im_monat",
            "heizgradtage", "produktionsplan_index", "wartung_aktiv",
            "vormonat_vls", "letzte_3_monate_vls"]

train = d[d["split"] == "train"]     # 8.390
test  = d[d["split"] == "test"]      # 8.400

X_train, y_train = train[MERKMALE], train["vollaststunden"]
X_test,  y_test  = test[MERKMALE],  test["vollaststunden"]

modell = HistGradientBoostingRegressor(categorical_features=["kundentyp"],
                                       random_state=42).fit(X_train, y_train)

prognose_kwh = modell.predict(X_test) * test["vertragsleistung_kw"]   # Bewertung in kWh
```

Form im Training: `X_train` 8.390 × 9 · `X_test` 8.400 × 9 · `y` jeweils
`vollaststunden`.

**Bewertet wird in kWh** mit **RMSE, MAE, R²** (Vorgabe des Briefs) plus MAPE, je einmal
auf allen 8.400 und einmal auf den 7.729 unmarkierten Testzeilen. RMSE und MAE nebeneinander
ausweisen, weil die Zielgröße ohne Logarithmus leicht rechtsschief bleibt (Schiefe 1,18).
Zusätzlich sinnvoll: der Fehler auf der **Monatssumme** über alle Zähler — das ist die
Beschaffungssicht.

**Baselines** auf denselben Testzeilen, ebenfalls in kWh: `vorjahr_vls` (Vorjahresmonat)
und `vormonat_vls` (Vormonat).

### Was je Modellklasse anzupassen ist

Mehr als das ist nicht nötig — die Datei ist ansonsten für alle drei Varianten dieselbe:

| | Anpassung |
|---|---|
| **Baummodell** (`HistGradientBoostingRegressor`) | `categorical_features=["kundentyp"]`. Fehlwerte werden nativ verarbeitet. Sonst nichts |
| **Lineares Modell** (interpretierbare Referenz) | `pd.get_dummies(d["kundentyp"], drop_first=True)`; Fehlwerte müssen imputiert werden (**Imputer nur auf `train` fitten**); Skalierung optional, ebenfalls nur auf `train` fitten. `vormonat_vls` und `letzte_3_monate_vls` korrelieren mit 0,87 — die Koeffizienten werden dadurch instabil, das gehört in den Kommentar |
| **Baselines** | keine Merkmale nötig: `vorjahr_vls × vertragsleistung_kw` bzw. `vormonat_vls × vertragsleistung_kw`, auf denselben Testzeilen |

**Nichts vorskalieren und nichts vorimputieren** liegt deshalb bewusst bei der Modellierung:
Ein Skalierer oder Imputer, der auf dem gesamten Datensatz gefittet wird, trägt Statistiken
aus dem Testjahr ins Training — das wäre Leakage, und zwar eine der Formen, die in der
Prüfung gern gefragt wird.

### Was ausdrücklich nicht zu tun ist

- **Nicht imputieren.** Verbleibende Lücken bleiben `NaN`;
  `HistGradientBoostingRegressor` verarbeitet sie nativ und lernt selbst, wohin eine Lücke
  zeigt. Jede Imputation erfindet hier eine Information.

  | Spalte | Lücken Training | Lücken Test | Grund |
  |---|---:|---:|---|
  | `produktionsplan_index` | 356 | 316 | zufällig, über beide Jahre und alle Kundentypen |
  | `vormonat_vls` | 709 | 10 | erster Monat je Zähler (strukturell) + Lag-Bereinigung |
  | `letzte_3_monate_vls` | 25 | 33 | Lag-Bereinigung |

- **Keine weiteren Ausreißer entfernen.** Nur die 20 unmöglichen fliegen aus dem Training.
  Nähme man alle 1.400 markierten heraus, verlöre das Training 39 % der 506 Monate mit
  Produktionsplan über 1,2, die Streuung des Faktors fiele von 0,275 auf 0,186 und die
  Saisonamplitude 2024 von 35 auf 30 Prozentpunkte — das Modell würde ausgerechnet die
  Winterspitzen unterschätzen. Beleg: Abbildung **A6**.
- **`vorjahr_vls` nicht in `MERKMALE` aufnehmen.** Im Trainingsjahr durchgehend leer.
- **`vertragsleistung_kw` nicht in `MERKMALE` aufnehmen.** Sie wird nur zum Zurückrechnen
  gebraucht (Begründung in Abschnitt 2).
- **Nicht auf `verbrauch_kwh` trainieren.**
- **Keine Spalte umbenennen oder umrechnen**, ohne es hier zu vermerken.

---

## 6. Anomalie-Erkennung über die Residuen

Die Spalte `anomalie` ist die **Referenzmenge**, gegen die sich die Residuenschwelle
kalibrieren lässt — nicht die Wahrheit. Nur die 20 in `unmoeglich` sind Gewissheit; findet
der Detektor die nicht, ist er kaputt.

Drei Punkte, die aus der EDA folgen:

1. **Residuum relativ rechnen** (Ist/Prognose bzw. prozentuale Abweichung), nicht in rohen
   kWh — auf der kWh-Skala würde eine Schwelle nur Großzähler markieren, derselbe Fehler,
   den die Normierung der Zielgröße behebt.
2. **Beidseitig schwellen.** Die EDA-Regel markiert nur nach oben. 176 Monatswerte unter
   40 % des Zählermedians (kleinster 0,04×) meldet sie nicht — die muss der Detektor
   finden. Er kann das, weil er `wartung_aktiv` kennt und den geplanten Einbruch
   wegerklärt.
3. **Die Regel ist eine Quotenregel:** zwei Monate je Zähler, alle 700 betroffen, 78 % der
   Treffer zwischen Dezember und April — überwiegend Jahresgang. Das Modell kennt
   Produktionsplan, Heizgradtage und Wartung und soll genau diese Fälle wegerklären. Die
   Auswertung gehört in drei Gruppen: von beiden gefunden · nur von der Regel (Modell hat
   es erklärt, also richtig so) · **nur vom Modell** (kontextuelle Anomalien — der
   eigentliche Mehrwert).

---

## 7. Änderungen an dieser Schnittstelle

Änderungswünsche an Spalten, Split oder Kennzeichen bitte an die EDA zurückspielen, nicht
lokal im Modellierungs-Notebook patchen — sonst laufen die Zahlen im Bericht auseinander.
Die Datei entsteht ausschließlich aus `eda_4.ipynb`.
