# Sachliche Story für die vollständige SWW-Projektpräsentation

Die Arbeit beantwortet zwei betriebliche Fragen: Wie viel Energie erwartet die Beschaffung im kommenden Monat, und welche später beobachteten Abweichungen sollte das Netzmanagement prüfen? Die Gruppe verbindet eine bereinigte Datenbasis mit nachvollziehbarer Modellwahl und einer vorab kalibrierten Prüfgrenze. Gemessen sind eine bessere retrospektive Prognose und ein begrenztes Hinweisvolumen. Die Wirkung im realen Betrieb bleibt Aufgabe eines Piloten.

## Quellen und Zahlenpriorität

Der vollständige Bericht `docs/IHK_Bericht_Gruppe_6_final.docx` wurde einschließlich aller Textkapitel und Tabellen gelesen. Der Projektauftrag `docs/IHK_Group6-1.pdf`, alle 18 Folien von `docs/Copy of Praesentationsvorlage_IHK.pptx` und relevante Learning-Journey-Texte bilden den Kontext. `project_facts.json` enthält die strukturierte Quellenzuordnung und alle Zahlen. Rechenwerte der neuen Decks kommen einheitlich aus Notebook 13 und dem bestehenden Dashboard-Export, ohne Modellneuberechnung.

Der einzige relevante Ergebnisunterschied zum Bericht betrifft die gruppierte Permutation Importance: Der Bericht verwendet Notebook 12 mit fünf Wiederholungen, die neuen Decks Notebook 13 mit drei. Die Rangfolge bleibt gleich. In beiden neuen Diagrammnotizen muss stehen: „Notebook 13, drei Wiederholungen. Der Bericht verwendet Notebook 12 mit fünf Wiederholungen; dadurch unterscheiden sich die Zahlen geringfügig, die Rangfolge bleibt gleich.“ Werte nicht zwischen den Varianten mischen.

Namen sind belegt: **Iana Kraievska**, **Patrick Olmo Hederer**, **Kiko Ramon Lukas**. Tutor: Anuar Santoyo. Ein aktueller Prüfungstermin ist nicht verlässlich belegt: Bericht und Vorlage enthalten Termine aus September/Oktober 2024, obwohl Daten bis Ende 2025 und ein Literaturabruf 2026 vorliegen. Das Datum deshalb weglassen, bis es feststeht. Nicht eigenständig einen Oktobertermin 2026 daraus machen.

## Verdichteter Hauptteil für 30 Minuten

Die Learning Journey empfiehlt wenige Konzeptfolien und warnt ausdrücklich vor mehr als zwölf in 30 Minuten. Eine vollständige Datei kann ausführliche Backups enthalten. Die folgende Gliederung zeigt eine mögliche Verdichtung in zwölf Hauptfolien; sie ist ein Zeitvorschlag, keine neue Vorgabe des Nutzers.

| Nr. | Thema und Kernbotschaft | Sichtbare Evidenz | Vortrag / Zeit |
|---|---|---|---|
| 1 | Projekt und Gruppe | Titel, vollständige Namen, SWW | Gemeinsamer Einstieg, 0:30 |
| 2 | Ablauf und Verantwortung | Datenqualität: Iana; EDA: Patrick; ML: Kiko. 30 Minuten Konzept, 15 Minuten Demo | Übergaben, 1:00 |
| 3 | Ausgangslage und betriebliche Entscheidung | 700 Großkunden; manuelle Fortschreibung; Hinweise häufig erst beim Quartalsabschluss | Iana, 2:30 |
| 4 | Verlässliche Datenbasis | 16.830 Rohzeilen zu 16.800 eindeutigen Zähler-Monaten; drei markante Bereinigungsbeispiele | Iana, 3:30 |
| 5 | Workflow und Projektentscheidungen | Quelle, Bereinigung, EDA, Modell, Prüfung, Übergabe; drei Sprints und wichtigste Anpassungen | Teamübergabe, 2:00 |
| 6 | EDA: Anschlussgröße und Zielvariable | Rohverbrauch durch Zählergröße geprägt; Vergleich vor/nach VLS-Normierung | Patrick, 3:00 |
| 7 | EDA: Planung und Wartung | Deskriptive Befunde zu Produktion/Wartung; saisonale Überlagerung beachten | Patrick, 2:30 |
| 8 | Canvas als zusammenhängende Entscheidung | Mehrwert, Vorhersage, verfügbare Merkmale, Evaluation und Fachentscheidung | Kiko, 2:00 |
| 9 | Zeitlich saubere Modellwahl | Drei Vorwärts-Folds 2024; Linear/RF; RMSE; Kalibrierung getrennt | Kiko, 3:00 |
| 10 | Ergebnis mit Baseline | 9.188 kWh RMSE, 3.725 kWh MAE; 15,9 % geringerer RMSE; retrospektiv | Kiko, 3:00 |
| 11 | Prüfregel und konkreter Fall | q99 = 144,4 VLS-h; 114 Hinweise, 9,5/Monat; ZL-00147 | Kiko, 3:00 |
| 12 | Pilot, Grenzen und nächster Schritt | Schattenbetrieb, Bestätigungen erfassen, Wirkung messen; keine automatische Diagnose | Gemeinsamer Schluss, 3:00 |

Detail-EDA, ML-Erklärbarkeit, Sensitivität oder Canvas können bei gewünschter größerer Folienzahl eigene Folien erhalten. Dann den Hauptteil bewusst kürzen oder zusätzliche Folien als Vertiefung kennzeichnen. Die separate ML-Präsentation ist ein eigenständiger Lern-/Vortragsblock und muss nicht vollständig in den 30-Minuten-Gesamtteil hineinkopiert werden.

## Inhalt, den die neue Gesamtpräsentation abdecken sollte

### Ausgangslage und Nutzen

Der Fallauftrag beschreibt SWW als städtischen Energieversorger im Hamburger Hafengebiet mit 700 gewerblichen, industriellen und kommunalen Großkunden sowie rund 180 Mio. EUR Jahresumsatz. Die Zahl ist Unternehmenskontext, keine Rechengrundlage für eine behauptete Einsparung.

Die Beschaffung arbeitet mit manuellen Fortschreibungen; schlechte Prognosen können kurzfristige Spotmarktgeschäfte nötig machen. Ungewöhnliche Verbräuche werden häufig erst im Quartalsabschluss erkannt. Das Projekt soll die Folgemonatsplanung verbessern und Hinweise monatlich nach Eingang des Istwerts zur Fachprüfung vorlegen. Es verspricht keine Echtzeitentdeckung und keine Prüfung vor Entstehung des Monatswerts.

Stakeholder: Stefan Lechtenberg, Bereichsleiter Energiebeschaffung und Sponsor, braucht die Folgemonatsprognose. Anke Bürger, Leiterin Netzmanagement, braucht priorisierte Fälle. Henrik Maaß, Senior-Datenanalyst, verlangt Reproduzierbarkeit und eine nachvollziehbare Definition. Quellen: Auftrag §§1–3, Bericht §§1.1–1.4 und 3.4.

### Datenqualität und Datenmodell

Eine Zeile entspricht einem Zähler-Monat. 700 Zähler über 24 Monate ergeben 16.800 eindeutige Kombinationen von Januar 2024 bis Dezember 2025. Der Rohdatensatz enthält zusätzlich 30 Duplikate und damit 16.830 Zeilen. Der Eingangsexport hat 16 Spalten, die spätere Modellierungsbasis 20. Diese unterschiedlichen Stufen nicht in einer Kennzahl vermischen.

Auf Hauptfolien reichen drei starke Beispiele: 672 MWh-Werte nach kWh vereinheitlicht, 30 Duplikate entfernt, 20 technisch unmögliche Werte markiert. Letztere nicht als „alle gelöscht“ darstellen: Zehn Fälle aus 2024 dürfen nicht ins Training; zehn aus 2025 bleiben im Benchmark als Plausibilitätsfälle. Alle zehn erzeugen einen Hinweis. Das ist ein Sanity Check, keine validierte Defekterkennungsrate.

Weitere in der Vorlage dokumentierte Probleme gehören ins Backup: 11.316 Datumsinkonsistenzen, 505 inkonsistente Kundentypen, 672 fehlende Produktionsplanwerte, 504 fehlende Temperaturen sowie strukturell fehlende Vorjahres-/Vormonatshistorie. Der parallele EDA-Audit kontrolliert die Detailzählungen und Bezugsgrößen. Drei Zielwerte werden rekonstruierbar markiert, für die strikte ML-Bewertung aber ausgeschlossen. Deshalb 8.389 Entwicklungsfälle und 8.398 Benchmarkfälle, statt der ursprünglichen Splitgrößen 8.390 und 8.400.

Wichtig ist die Entscheidung statt der bloßen Fehlerliste: Fehlwerte nach Ursache behandeln; plausible Spitzen erhalten; physikalische Grenze über Vertragsleistung und Monatsstunden prüfen. Historische Merkmale je Zähler strikt aus Vergangenheit neu berechnen. Quellen: Bericht §§3.3.1, 4.1–4.2, Anhang B; Vorlage Folien 5, 6, 15; Notebook 13.

### EDA als Begründung der Modellentscheidungen

Der Bericht nennt 92 % der Rohverbrauchsstreuung zwischen Zählern. Die Vertragsleistung prägt damit die kWh-Größe. Nach Normierung liegen die Mediane der Kundentypen laut Bericht zwischen 160 und 173 VLS-Stunden. VLS sind Verbrauch geteilt durch Vertragsleistung, keine gemessene Laufzeit. Die Prognose rechnet exakt wieder in kWh zurück.

Produktion und geplante Wartung liefern fachlich nachvollziehbare Information. Wartungsmonate zeigen ein niedrigeres Verbrauchsniveau. Saisonale Produktion kann Wetter- und Feiertagskorrelationen überlagern; die Analyse kontrolliert vergleichbare Produktionsniveaus. Keine Kausalität aus Diagrammen ableiten. Heizgradtage ersetzen die weitgehend redundante Temperaturvariable. Der Vorjahreswert ist 2024 mangels 2023-Historie kein brauchbares Trainingsmerkmal.

Die EDA-Anhänge C1–C6 decken Verteilung, Kundentypen, physikalische Monatsgrenze, Korrelationen, Produktionsplan und Wartung ab. Hauptteil zeigt zwei entscheidungsrelevante Grafiken, der Rest bleibt Backup. Quelle: Bericht §3.3.2 und Anhang C. Exakte Chartdaten kommen aus dem parallelen EDA-Audit.

### Canvas und methodische Kohärenz

Die zentrale Kette: Daten liefern eine kontinuierliche Verbrauchsprognose; Regressionsmetriken bewerten sie; eine nachgelagerte Schwelle priorisiert Fachprüfungen. Das Projekt trainiert aktuell keinen Defektklassifikator.

Alle zehn Canvasfelder sind im Bericht und im JSON vollständig belegt. Im Hauptteil etwa fünf zusammenhängende Felder zeigen: Mehrwert, Vorhersage, Merkmale, Evaluation, Entscheidung. Im Backup die vollständige Übersicht. Planinformationen müssen vor Monatsbeginn verfügbar sein. Der Fallbrief setzt dies voraus; eine produktive Prüfung historischer Wetterprognoseversionen liegt nicht vor. Heizgradtage daher ausdrücklich als Wetterprognose, Produktion und Wartung als geplante Werte benennen.

Die neun Prädiktoren sind zwei Historienmerkmale, Monat/Arbeits-/Feiertage, Heizgradtage, Produktionsplan, Wartung und Kundentyp. Vertragsleistung normalisiert und rechnet zurück; sie ist kein gelerntes Merkmal des VLS-Modells. Numerische Medianbehandlung und One-Hot-Kodierung bleiben im jeweiligen Trainingsfold. Quelle: Bericht Kapitel 2, §4.2, Tabellen A1/B1/B2; Notebook 13, Zelle `learn-feature-table`.

### Modellwahl, Ergebnis und Erklärbarkeit

Trainiert werden lineare Regression und Random Forest. Vormonat und Mittel aus bis zu drei Vormonaten sind einfache, untrainierte Vergleichsregeln. Acht RF-Konfigurationen über drei Zeit-Folds ergeben 24 Fits. Die Entscheidung fällt ausschließlich nach mittlerem CV-RMSE aus 2024. Die Bewertung nutzt Mai/Juni, Juli/August und September/Oktober nach jeweils vorangehendem Lernblock.

CV-RMSE: RF 13.272, linear 13.643, Historienmittel 15.483, Vormonat 18.460 kWh. RF gewinnt im Mittel um 2,7 %, nicht in jedem Fold. Die Streuung ist Standardabweichung der drei Fold-Ergebnisse, kein Konfidenzintervall. Gewählt sind 300 Bäume, Tiefe 8, mindestens fünf Fälle je Blatt und 70 % Merkmale je Aufteilung, Zufallsstart 42.

Benchmark 2025: RF 9.188 kWh RMSE und 3.725 kWh MAE, R² = 0,901. Linear 9.414, Historienmittel 10.922 und Vormonat 12.386 kWh RMSE. 15,9 % Vorteil bedeutet geringeren RMSE, weder weniger Fälle noch Euro-Einsparung. RF/linear/Historienmittel verwenden n = 8.398, Vormonat n = 8.388. Für die Präsentation genügt RMSE mit MAE; R² bleibt bei Bedarf Backup.

Der gewählte RF trainiert abschließend auf gültigen Entwicklungsfällen des gesamten Jahres 2024. Danach bleiben Modell und Schwelle fest. Die bereits bekannten Lag-Merkmale aktualisieren sich 2025 monatlich. Es handelt sich um rückblickend geprüfte einzelne Folgemonatsprognosen, keine Jahresprognose am 1. Januar.

Für die Erklärbarkeit beide Decks konsistent auf Notebook 13: RMSE-Anstieg nach gruppiertem Mischen ist 7.349 kWh für Verbrauchshistorie, 717 für Produktion, 578 für Wartung, 232 für Kalender, 193 für Wetter, 115 für Jahreszeit und 5 für Kundentyp. Die Werte beschreiben Modellnutzen, keine Ursache. Die bereits erläuterte Abweichung zum Bericht in den Notizen offenlegen. Quellen: Bericht §§4.3.1–4.3.4 und Anhang D, Notebook 13.

### Prüfregel und betriebliche Arbeitslast

Die Schwelle entsteht nach der Modellwahl aus 1.397 rollierend erzeugten Fehlern für November/Dezember 2024. November lernt aus Januar–Oktober, Dezember aus Januar–November. Das 99. Perzentil beträgt ungerundet 144,354704864 VLS-Stunden. Ein Betrag mindestens so groß wie die Schwelle erzeugt einen Hinweis. Der Schwellenfaktor ist keine Wahrscheinlichkeit.

2025 ergeben sich 114 Hinweise für 107 Zähler, 1,36 % der 8.398 Fälle, im Mittel 9,5 pro Monat. 68 sind ungewöhnlich hoch, 46 ungewöhnlich niedrig. Ein 99. Perzentil aus 2024 garantiert keine Ein-Prozent-Quote in späteren Daten.

ZL-00147 mit 49 kW macht die Regel konkret: August 2025 hat 23.563,5 kWh Ist gegen 7.303,9 kWh Prognose. Residuum +16.259,6 kWh beziehungsweise +331,8 VLS-h, signierter Faktor +2,30. September liegt mit Faktor −0,68 innerhalb der Schwelle. In kWh ist die Grenze wegen der Vertragsleistung zählerspezifisch; hier 7.073,4 kWh.

Die Perzentile q95/q97,5/q99/q99,5 ergeben 400/256/114/69 Hinweise oder 33,3/21,3/9,5/5,8 Hinweise pro Monat. Der Regler ändert nur die Entscheidungsgrenze, trainiert das Modell nicht neu. Quellen: Bericht §§4.3.5–4.4, Anhang B/D und Dashboard-Export.

### Grenzen, Ethik, Datenschutz und Kosten

Die vorhandene Evidenz reicht für eine Priorisierungshilfe, nicht für eine automatische Diagnose. Falsch positive Hinweise verursachen Aufwand, falsch negative Hinweise können relevante Fälle übersehen. Ohne bestätigte Labels sind Precision und Recall offen. Auch Nicht-Hinweise müssen stichprobenartig geprüft werden, damit übersehene Fälle überhaupt beobachtbar werden.

Weitere Grenzen: nur zwei Jahre, retrospektiver Benchmark und winterlastige Kalibrierung aus zwei Monaten. Kein klarer Hinweis auf Überanpassung ist kein Beweis ihrer Abwesenheit. R² ist erklärte Streuung, keine Trefferquote. Die heutigen Kennzahlen belegen keinen produktiven Nutzen.

Der Fallbrief nennt keine Personendaten im engeren Sinn. Die Präsentation darf daraus keine pauschale Datenschutzfreigabe ableiten. Berechtigungen, Aufbewahrung und produktive Verantwortlichkeiten sind nicht belegt. Für eine Einführungsfolie als offene Aufgaben formulieren: Zugriff nach Rolle begrenzen, erforderliche Daten verwenden, Berechtigung und Speicherfristen vor Anbindung festlegen. Keine Rechtslage behaupten. Fairness zwischen Kundentypen ist nicht validiert; segmentweise Fehler-/Hinweisprüfung ist eine geplante Kontrolle.

ROI, Amortisation, vermiedene Defekte und gesparte Prüfminuten fehlen als belastbare Zahlen. Die Kostenfolie der Vorlage enthält nur Platzhalter. Eine vollständige Präsentation soll diese Lücke ehrlich als Messplan füllen: Beschaffungswirkung, Prüfminuten je Fall, Bestätigungsquote, Integration und laufende Betriebskosten im Pilot erheben. Bereits belegbar ist die Arbeitsmenge je Perzentil. Eine optionale Formel lautet `jährliche Prüfzeit = Hinweise pro Jahr × gemessene Minuten je Hinweis / 60`; keine Minutenwerte erfinden. Quellen: Auftrag §8, Bericht §§1.4, 3.7, 4.4, Vorlage Folien 17–18.

### Projektarbeit, Empfehlung und persönliche Lernpunkte

Der Bericht dokumentiert drei einwöchige Sprints und eine Finalisierung mit durchgängigen Verantwortungen. Die Story sollte die drei wesentlichen Entscheidungen zeigen: gemeinsame bereinigte Datenbasis und Plausibilitätsregel; VLS und verfügbare Merkmale aus der EDA; zeitlich saubere Modellwahl und neu berechnete Historie. Die Sprintdaten bleiben relativ, weil die konkreten Kalenderdaten widersprüchlich sind.

Die individuellen Lernpunkte sind belegte eigene Berichtsaussagen: Iana betont ursachenbezogene Bereinigung und physikalische Plausibilität. Patrick trennt Korrelation und Kausalität durch Produktionskontrolle. Kiko betont Baselines, zeitliche Validierung und Leakage-Vermeidung. Nicht auf einer überladenen Schlussfolie alle drei ausformulieren; kurze Notiz und klarer Sprecherübergang reichen.

Empfehlung: zunächst Schattenbetrieb auf ausgewählten Zählern parallel zur bestehenden Praxis. Fehler, Merkmalsverteilungen, Hinweisvolumen, Prüfzeit und Bestätigungsquote monatlich messen. Bei stabiler Wirkung kontrolliert integrieren und erweitern. Retraining erst bei dokumentiertem Bedarf mit erneuter getrennter Validierung. Der Brief nennt quartalsweises Retraining als Vorschlag, das Projekt hat bewusst eine bedarfsabhängige Regel.

Später können bestätigte Ja/Nein-Labels eine zweite Lernaufgabe ermöglichen: Klassifikation zur Priorisierung relevanter Fälle. Eine Prozentwahrscheinlichkeit braucht eigene Validierung und Kalibrierung. Heute kein bereits trainiertes zweites Modell behaupten. Quellen: Bericht Kapitel 3, §§4.4.3–4.5.

## Demo und Backup

Der 15-Minuten-Ablauf aus der Learning Journey passt zur Rollenverteilung: zwei Minuten Rohdaten, drei Minuten Bereinigung, drei Minuten EDA, vier Minuten Modell/Evaluation, zwei Minuten Dashboard, eine Minute Puffer. Jede Person zeigt ihren eigenen Beitrag. Ein gecachtes Notebook und Screenshots dienen als Fallback; den gesamten Hyperparametersuchlauf nicht unter Zeitdruck abwarten.

Die Dashboarddemo zeigt einen lokalen Prototyp mit dem retrospektiven Datenstand 2025. Ablauf: Schwelle zeigen, Prüfliste priorisieren, Fall öffnen, Datenqualität/Produktionsplan/Wartung prüfen, Entscheidung begründen, Feedback als spätere Labels erklären. Es ist keine Live-Anbindung und löst keine automatische Maßnahme aus.

Vollständigkeit im Backup sichern: alle zehn Canvasfelder; detaillierte Datenbereinigung; Datenmodell und neun Features; ergänzende EDA-Grafiken; CV-Folds/Parameter; MAE/RMSE-Didaktik; VLS-direkt-kWh-Vergleich; Perzentilsensitivität; Risiken/Datenschutz und Nutzenmessung. Damit werden alle Berichtskapitel und Anhänge abgedeckt, ohne den Hauptvortrag in eine Liste von Tabellen zu verwandeln.
