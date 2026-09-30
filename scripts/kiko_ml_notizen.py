"""Sprechernotizen für Kikos ML-Folien (build_kiko_ml_folien.py).

Je Hauptfolie: Stichworte zum freien Sprechen, ein Sprechtext zum Ablesen (rund eine Minute,
[Pause] = eine Sekunde Stille), ein Abschnitt „So verstehst du es“ mit dem Hintergrund in
einfachen Worten und fertige Antworten auf naheliegende Rückfragen. Zahlen wie im Bericht und
in Notebook 13; Ergebnisse des Testjahrs 2025 nennt Patrick.
"""

NOTES = {
    "f1": {
        "stichworte": ["Danke an Iana", "drei Fragen = drei Farben", "am Ende: mein nächster Schritt"],
        "sprechtext": [
            "Danke, Iana. Ich zeige jetzt den Machine-Learning-Teil. Drei Fragen führen durch: Was sagt unser "
            "Modell vorher, und womit? Woran messen wir, ob es gut ist? Und ab wann wird aus einer Abweichung ein "
            "Prüfhinweis? Am Ende sage ich, was ich als Nächstes vorhabe.",
        ],
        "verstehen": [
            "Die Folie ist die Landkarte für deine neun Minuten. Die drei Farben kommen wieder: Navy steht für die "
            "Vorhersage (Folie 2–4), Teal für das Messen (Folie 5–6), Amber für den Prüfhinweis (Folie 7–8).",
        ],
    },
    "f2": {
        "stichworte": ["Canvas = Steckbrief mit zehn Feldern", "Iana: Mehrwert, Daten · Patrick: Impact, Monitoring",
                       "sechs Karten als Kette lesen: was, womit, wie, woran, was dann, wann"],
        "sprechtext": [
            "Der Machine Learning Canvas ist ein Steckbrief für ein ML-Projekt: zehn Felder, die zusammenpassen "
            "müssen. Mehrwert und Datenquellen hat Iana gezeigt, Impact und Monitoring kommen bei Patrick. Sechs "
            "Felder gehören zum Modell, die gehe ich kurz durch.",
            "Vorhersage: Wir sagen den Stromverbrauch jedes Zählers für den nächsten Monat vorher. Merkmale: Dafür "
            "nutzen wir nur, was vor Monatsbeginn feststeht, also den bisherigen Verbrauch, Kalender, Wetter, "
            "Produktionsplan, Wartung und Kundentyp. Lernansatz: Das Modell lernt aus Beispielen, bei denen das "
            "Ergebnis bekannt ist. Wir haben einen Random Forest gegen einfachere Verfahren antreten lassen.",
            "Evaluation: Wir messen mit dem RMSE in Kilowattstunden, und zwar nur auf Monaten, die das Modell beim "
            "Lernen nicht kannte. Entscheidung und Zeitpunkt: Vor Monatsbeginn geht die Prognose an die "
            "Beschaffung. Nach Monatsende prüfen wir, ob die Abweichung ungewöhnlich groß ist.",
        ],
        "verstehen": [
            "Lies die Karten von links oben nach rechts unten wie eine Kette: Was sagen wir vorher, womit, wie lernt "
            "das Modell, woran messen wir, was passiert mit dem Ergebnis, wann läuft es.",
            "Regression heißt: Das Modell sagt eine Zahl vorher (kWh), keine Kategorie wie „Anomalie ja/nein“.",
            "Überwachtes Lernen heißt: Beim Lernen kennt das Modell den richtigen Wert, hier den echten Verbrauch "
            "der Vergangenheit.",
            "Random Forest: viele Entscheidungsbäume, jeder lernt auf einer etwas anderen Stichprobe; der "
            "Durchschnitt aller Bäume ist die Prognose. Das macht ihn robust gegen einzelne Ausreißer.",
        ],
        "fragen": [
            ("Warum keine Klassifikation?", "Es gibt keine bestätigten Anomalie-Labels. Die Spalte „anomalie“ ist "
                                            "nur ein geliefertes Kennzeichen, kein geprüftes Ergebnis. Deshalb "
                                            "sagen wir den Verbrauch vorher und werten die Abweichung aus."),
            ("Welche Merkmale sind bewusst weggelassen?", "Der Vorjahreswert (für 2024 fehlt die Historie aus "
                                                          "2023), die Temperatur (fast dasselbe wie die "
                                                          "Heizgradtage), die Spalte „anomalie“ und die "
                                                          "Vertragsleistung als Merkmal; sie dient nur der "
                                                          "Umrechnung."),
        ],
    },
    "f3": {
        "stichworte": ["nie aus der Zukunft lernen", "drei Folds 2024: Modellwahl",
                       "Schwelle Nov–Dez 2024, dann eingefroren", "3-Monats-Mittel neu berechnet (Leakage)"],
        "sprechtext": [
            "Das Wichtigste bei Zeitreihen: Ein Modell darf nie aus der Zukunft lernen. Deshalb teilen wir die "
            "Daten nicht zufällig auf, sondern nach der Zeit.",
            "In drei Durchgängen, den Folds, lernt das Modell auf den frühen Monaten 2024 und wird auf den zwei "
            "Monaten danach bewertet. Zum Beispiel: lernen Januar bis April, bewerten Mai und Juni. Damit "
            "entscheiden wir, welches Modell das beste ist.",
            "Die Schwelle für Prüfhinweise legen wir mit November und Dezember 2024 fest und frieren sie ein. Erst "
            "dann rechnet das finale Modell, gelernt auf ganz 2024, das Jahr 2025 durch. [Pause]",
            "Eine Falle haben wir dabei gefunden: Das gelieferte Drei-Monats-Mittel enthielt spätere Werte. Wir "
            "haben es für jeden Zähler nur aus abgeschlossenen Monaten neu berechnet.",
        ],
        "verstehen": [
            "Leakage heißt: Das Modell sieht beim Lernen Informationen, die es in der Wirklichkeit noch nicht hätte. "
            "Dann sieht der Fehler im Test besser aus, als er im Betrieb wäre.",
            "Fold = ein Durchgang aus Lernen und Bewerten. Drei Folds zeigen, ob ein Modell nicht nur zufällig in "
            "einem Zeitraum gut ist.",
            "Die Zeitleiste von oben nach unten: drei Folds für die Modellwahl, dann die Schwelle, dann das finale "
            "Modell. Die gestrichelte Linie ist der Jahreswechsel: Alles rechts davon wird nur noch angewendet.",
        ],
        "fragen": [
            ("Warum kein zufälliger Split?", "Er würde zum Beispiel Juli lernen und Mai testen. Das Modell kennt "
                                             "dann die Zukunft, und die Fehler wären zu optimistisch."),
        ],
    },
    "f4": {
        "stichworte": ["Zähler sehr unterschiedlich groß (92 % Streuung zwischen Zählern)",
                       "VLS = Verbrauch ÷ Leistung", "A und B: beide 200 VLS-h", "zurück in kWh für die Planung"],
        "sprechtext": [
            "Unsere Zähler sind sehr unterschiedlich groß. 92 Prozent der Streuung im Verbrauch liegen zwischen "
            "den Zählern, das hat Patricks Analyse gezeigt. Ein großer Industriekunde verbraucht einfach viel mehr "
            "als ein kleiner Betrieb.",
            "Deshalb lernt das Modell nicht direkt Kilowattstunden, sondern Vollaststunden: Verbrauch geteilt durch "
            "die vertraglich vereinbarte Leistung. Rechts sieht man es: Zähler A mit 10.000 Kilowattstunden bei 50 "
            "Kilowatt und Zähler B mit 40.000 bei 200 Kilowatt haben beide 200 Vollaststunden. Sie sind also "
            "gleich ausgelastet. [Pause]",
            "Für die Beschaffung rechnen wir die Prognose wieder in Kilowattstunden zurück, und in "
            "Kilowattstunden messen wir auch den Fehler.",
        ],
        "verstehen": [
            "Vollaststunden beantworten die Frage: Wie viele Stunden hätte der Anschluss mit voller Leistung laufen "
            "müssen, um diesen Verbrauch zu erreichen? Ein Monat hat rund 730 Stunden.",
            "Der Vorteil: Das Modell lernt ein Muster für alle Zähler (Auslastung) statt 700 verschiedene "
            "Größenordnungen.",
        ],
        "fragen": [
            ("Bringt VLS messbar etwas?", "Ja, im Test liegt der Fehler niedriger als bei einer direkten "
                                          "kWh-Prognose; die Ergebnisse 2025 zeigt Patrick."),
        ],
    },
    "f5": {
        "stichworte": ["gleiche Fehlersumme, gleicher MAE (10)", "RMSE quadriert: 10 gegen 20 kWh",
                       "große Fehler teuer am Spotmarkt", "Einheit kWh = Planungseinheit"],
        "sprechtext": [
            "Woran messen wir, ob die Prognose gut ist? Unsere Hauptmetrik ist der RMSE, die Wurzel aus dem "
            "mittleren quadrierten Fehler.",
            "Das Beispiel links zeigt, warum. Beide Male liegen vier Prognosen zusammen 40 Kilowattstunden daneben. "
            "In A ist jeder Fehler 10, in B sind drei Fehler null und einer 40. Der durchschnittliche Fehler, der "
            "MAE, ist in beiden Fällen 10. Der RMSE quadriert die Fehler aber vor dem Mitteln. Deshalb zählt der "
            "eine große Fehler stärker, und der RMSE steigt in B auf 20. [Pause]",
            "Genau das wollen wir: Große Abweichungen muss die Beschaffung kurzfristig am Spotmarkt ausgleichen, und "
            "das ist teuer. Außerdem misst der RMSE in Kilowattstunden, also in der Einheit, in der geplant wird. "
            "MAE und R² schauen wir ergänzend an, entschieden wird mit dem RMSE.",
        ],
        "verstehen": [
            "Rechenweg für B: Fehler quadrieren (40² = 1.600, die Nullen bleiben 0), Mittelwert bilden "
            "(1.600 ÷ 4 = 400), Wurzel ziehen (√400 = 20). Die Wurzel bringt die Einheit zurück auf kWh.",
            "MAE = Durchschnitt der Fehlerbeträge, also der typische Fehler. R² = Anteil der Streuung, den das "
            "Modell erklärt, zwischen 0 und 1, ohne Einheit.",
            "Das Beispiel ist aus Notebook 13 und zeigt das Prinzip; es sind keine Projektwerte.",
        ],
        "fragen": [
            ("Warum nicht MAPE, also Prozentfehler?", "Bei kleinen Verbräuchen werden Prozentfehler riesig und "
                                                      "gewichten kleine Zähler zu stark. Geplant wird in kWh."),
            ("Warum nicht R² als Hauptmetrik?", "R² hat keine Einheit und sagt nicht, wie viele kWh wir "
                                                "danebenliegen. Für die Beschaffung zählt die Menge."),
        ],
    },
    "f6": {
        "stichworte": ["vier Kandidaten, drei Folds", "Random Forest 13.272 vor linearer Regression 13.643",
                       "einfache Regeln klar dahinter", "Fold 1 am schwersten", "2025 zeigt Patrick"],
        "sprechtext": [
            "Mit dieser Metrik haben wir vier Kandidaten verglichen: einen Random Forest, eine lineare Regression "
            "und zwei einfache Regeln, nämlich „wie im Vormonat“ und „Mittel der letzten drei Monate“. Alle wurden "
            "in denselben drei Folds von 2024 bewertet. Die Rauten zeigen die einzelnen Folds.",
            "Der Random Forest liegt im Mittel bei 13.272 Kilowattstunden, knapp vor der linearen Regression mit "
            "13.643. Die einfachen Regeln liegen klar dahinter. Auffällig ist Fold 1, Mai und Juni: Der ist für "
            "alle Modelle am schwersten und zieht jeden Mittelwert hoch. [Pause]",
            "Entschieden haben wir nur mit 2024. Wie gut das Modell dann im Testjahr 2025 war, zeigt gleich Patrick.",
        ],
        "verstehen": [
            "Einfache Regeln (Baselines) sind der Maßstab: Ein Modell lohnt sich nur, wenn es besser ist als "
            "„nimm einfach den Vormonat“.",
            "Der Balken ist der Durchschnitt über die drei Folds, die Rauten sind die einzelnen Folds, der Strich "
            "zeigt die Streuung (±1 Standardabweichung).",
            "Die lineare Regression ist fast gleich gut und bleibt deshalb die Rückfallebene im Pilot.",
        ],
        "fragen": [
            ("Warum nicht die lineare Regression, wenn es so knapp ist?", "Der Random Forest war im Mittel besser "
                                                                          "und erfasst nichtlineare Effekte; die "
                                                                          "lineare Regression bleibt die "
                                                                          "Rückfallebene."),
            ("Welche Hyperparameter?", "Acht Kombinationen, nur in 2024 verglichen: Backup B1."),
        ],
    },
    "f7": {
        "stichworte": ["kleine Abweichungen sind normal", "1. messen · 2. normale Fehler sammeln · 3. Grenze ziehen",
                       "99 von 100 darunter = 144,4 VLS-h, eingefroren", "Faktor ≥ 1 → Prüfhinweis",
                       "99 % = Startwert, Kapazität zeigt Patrick"],
        "sprechtext": [
            "Jetzt die dritte Frage: Ab wann ist eine Abweichung ungewöhnlich? Kein Modell trifft genau, kleine "
            "Abweichungen sind also normal. Wir brauchen eine Grenze.",
            "Die haben wir in drei Schritten gezogen. Erstens messen wir nach Monatsende die Abweichung zwischen "
            "Ist und Prognose. Zweitens haben wir gesammelt, wie groß die normalen Fehler des Modells sind: 1.397 "
            "echte Vorhersagen für November und Dezember 2024. Rechts sind sie der Größe nach sortiert. Drittens "
            "ziehen wir die Grenze dort, wo 99 von 100 Fehlern darunter bleiben. Das sind 144,4 Vollaststunden, und "
            "diese Grenze frieren wir vor 2025 ein. [Pause]",
            "Wie weit ein Monat darüber liegt, sagt der Faktor: Abweichung geteilt durch die Grenze. Ab 1 gibt es "
            "einen Prüfhinweis.",
            "99 Prozent ist unser Startwert für den Pilot. Wie viele Hinweise das Team im Monat schafft und wie "
            "sich die Schwelle dafür verschieben lässt, zeigt Patrick im Dashboard.",
        ],
        "verstehen": [
            "Das Diagramm rechts: Jeder Punkt der Kurve ist ein Fehler, von klein (links) nach groß (rechts) "
            "sortiert. Fast alle Fehler sind klein; ganz rechts schießen 14 Fehler nach oben. Die gestrichelte "
            "Linie bei 144,4 trennt die 99 % normalen von dem 1 % auffälligen.",
            "Perzentil = Rangplatz in der sortierten Liste. Das 99. Perzentil ist der Wert, unter dem 99 % der "
            "Fehler liegen.",
            "Die Abwägung dahinter: Falsch-positiv heißt, ein normaler Monat wird gemeldet und umsonst geprüft. "
            "Falsch-negativ heißt, ein echtes Problem wird nicht gemeldet und fällt wie heute erst im Quartal auf. "
            "Eine niedrigere Grenze (etwa 95 %) meldet mehr Fälle, also mehr Arbeit und mehr Fehlalarme. Eine "
            "höhere Grenze meldet weniger, dafür rutscht eher etwas durch.",
            "Warum 99 %: Die Prüfkapazität ist begrenzt, jede Meldung soll wirklich auffällig sein. Deshalb ein "
            "strenger Startwert, den der Fachbereich im Pilot anpassen kann.",
            "Warum eingefroren: Würden wir die Grenze mit 2025 einstellen, wäre der Test geschönt (Leakage).",
            "Faktor-Beispiel: ZL-00147 hat 331,8 VLS-h Abweichung. 331,8 ÷ 144,4 = 2,3. Das Vorzeichen sagt die "
            "Richtung: plus = mehr verbraucht als erwartet, minus = weniger.",
        ],
        "fragen": [
            ("Warum 99 und nicht 95 Prozent?", "Bei 95 % läge jeder 20. normale Fehler über der Grenze, das wären "
                                               "viele Fehlalarme. 99 % ist ein strenger Startwert; welche Grenze "
                                               "zur Prüfkapazität passt, entscheidet der Fachbereich im Pilot."),
            ("Warum gerade November und Dezember 2024?", "Das sind die jüngsten Monate vor dem Test, und sie wurden "
                                                         "nicht für die Modellwahl gebraucht; die Folds enden im "
                                                         "Oktober. Später ginge nur mit 2025 selbst. Backup B3."),
            ("Ist die Schwelle 2025 eine andere?", "Nachträglich aus 2025 berechnet läge sie bei rund 175 VLS-h. "
                                                   "Das zu nutzen wäre Leakage. Der typische Fehler ist 2025 gleich "
                                                   "groß, nur die Extreme sind größer."),
        ],
    },
    "f8": {
        "stichworte": ["ZL-00147, 49 kW, August 2025", "erwartet gut 7.300, gemessen über 23.500 kWh",
                       "331,8 ÷ 144,4 = Faktor 2,3", "Hinweis ≠ Anomalie", "Bewertung wird Label"],
        "sprechtext": [
            "So sieht ein Prüfhinweis konkret aus. Zähler ZL-00147, ein Anschluss mit 49 Kilowatt. Für August 2025 "
            "hat das Modell gut 7.300 Kilowattstunden erwartet, gemessen wurden über 23.500. In Vollaststunden ist "
            "die Abweichung 331,8, die Grenze liegt bei 144,4. Der Faktor ist also 2,3: Die Abweichung ist 2,3-mal "
            "so groß wie erlaubt, deshalb der Hinweis. [Pause]",
            "Ein Hinweis ist aber noch keine bestätigte Anomalie. Deshalb wird jeder Fall im Cockpit geprüft und "
            "bewertet: Ist der Messwert gültig? Ist die Abweichung erklärt? Was war die Ursache? Diese Antworten "
            "speichern wir, und genau sie sind die Grundlage für meinen nächsten Schritt.",
        ],
        "verstehen": [
            "Der Faktor macht Zähler vergleichbar: 2,3 heißt mehr als doppelt so weit draußen wie erlaubt, egal wie "
            "groß der Anschluss ist.",
            "Im Diagramm: die durchgezogene Linie ist der gemessene Verbrauch, die gestrichelte die Prognose, die "
            "blaue Fläche der erlaubte Bereich. Nur der August liegt deutlich draußen.",
            "Im September ist die Prognose erhöht, weil der hohe August als Vormonat in die Prognose einfließt; der "
            "Faktor liegt dort bei −0,68, also innerhalb der Grenze.",
        ],
        "fragen": [
            ("Ist das eine bestätigte Anomalie?", "Nein. Ein Prüfhinweis sagt nur: ungewöhnlich groß. Erst die "
                                                  "Bewertung bestätigt oder verwirft den Verdacht."),
        ],
    },
    "f9": {
        "stichworte": ["Bewertung = Label", "zweites Modell: Klassifikation mit Wahrscheinlichkeit in %",
                       "automatisiert vorsortieren, Mensch entscheidet", "Übergabe an Patrick"],
        "sprechtext": [
            "Mein nächster Schritt baut auf diesen Bewertungen auf. Jede Bewertung ist ein Label: Hat sich der "
            "Hinweis bestätigt, ja oder nein, und warum.",
            "Sobald genug bestätigte Fälle vorliegen, trainiere ich darauf ein zweites Modell, ein "
            "Klassifikationsmodell. Die Regression sagt weiter den erwarteten Verbrauch vorher. Das "
            "Klassifikationsmodell schätzt dann für jeden Prüfhinweis, wie wahrscheinlich er sich bestätigt, zum "
            "Beispiel 80 Prozent. [Pause]",
            "Damit lassen sich die Hinweise automatisiert vorsortieren, die wahrscheinlichsten zuerst. Das spart "
            "Prüfzeit und erhöht die Treffsicherheit. Entscheiden bleibt beim Menschen: Das Modell ersetzt keine "
            "Abrechnungsentscheidung, es flaggt nur, was eine Prüfung wert ist.",
            "Wie das Modell 2025 abgeschnitten hat und wie bestätigte echte Zählerwerte das Retraining der Prognose "
            "verbessern können, zeigt jetzt Patrick.",
        ],
        "verstehen": [
            "Regression sagt eine Zahl vorher (kWh). Klassifikation sagt eine Klasse vorher (bestätigt ja/nein) "
            "und kann dazu eine Wahrscheinlichkeit angeben.",
            "Heute fehlen dafür die Labels, deshalb erst sammeln, dann trainieren. Belastbar wird die Prozentzahl "
            "erst, wenn man sie auf neuen Fällen geprüft und kalibriert hat.",
            "Arbeitsteilung mit Patrick: Du sprichst über das zweite Modell für die Hinweise, Patrick über das "
            "bessere Retraining der Verbrauchsprognose.",
        ],
        "fragen": [
            ("Wie viele Labels braucht man?", "Das legt der Pilot fest; wichtig sind genug bestätigte und verworfene "
                                              "Fälle, auch aus einer Stichprobe unauffälliger Monate."),
            ("Was ist Precision@K?", "Der Anteil bestätigter Fälle unter den K obersten Hinweisen der Prüfliste, "
                                     "also wie treffsicher die Liste ist."),
        ],
    },
}
