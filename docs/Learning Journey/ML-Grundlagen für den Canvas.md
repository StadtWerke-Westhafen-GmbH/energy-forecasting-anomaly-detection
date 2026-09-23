# ML-Grundlagen für den Canvas

Im Fachgespräch fragt die Prüfungskommission: _„Warum eine Klassifikation und nicht eine Regression? Warum diese Hauptmetrik?"_ Wer das Modell trainiert hat, aber den Unterschied zwischen den Begriffen nie in eigenen Worten formuliert hat, wirkt unsicher — und verliert Punkte, obwohl das Modell selbst gut sein mag.

Diese Lektion gibt Ihnen die ML-Grundbegriffe, die Sie für die Canvas-Felder 3, 5 und 6 souverän erklären müssen — und im Fachgespräch in einem Satz verteidigen können sollten.

Nach dieser Lektion können Sie:

-   den Unterschied zwischen überwachtem und unüberwachtem Lernen sowie zwischen Klassifikation und Regression in eigenen Worten erklären,

-   für eine gegebene Aufgabe (binäre Klassifikation / kontinuierliche Vorhersage / Anomalie-Erkennung) die passende Evaluation-Metrik begründen und im Fachgespräch verteidigen.

Der wichtigste Unterschied:

| Typ | Hat einen Zielwert (Label)? | Was lernt das Modell |
| --- | --- | --- |
| Überwachtes Lernen (Supervised Learning) | Ja — jeder Datenpunkt hat eine bekannte Zielvariable | Den Zusammenhang zwischen Merkmalen und Zielwert |
| Unüberwachtes Lernen (Unsupervised Learning) | Nein — nur Merkmale, kein Zielwert | Strukturen in den Daten (Cluster, Anomalien, Dimensionsreduktion) |

In Ihrem Projekt arbeiten Sie mit **überwachtem Lernen** — Sie haben in den Trainingsdaten eine Zielvariable (z. B. eine Kündigungsmarkierung, einen Umsatzwert oder einen Verbrauchswert).

Unüberwachtes Lernen kann Ihnen am Rand begegnen: Anomalien lassen sich z. B. über Residuen eines überwachten Regressionsmodells bewerten — **echte** Anomalie-Detektion (etwa mit Isolation Forest) ist hingegen unüberwacht.

Innerhalb des überwachten Lernens unterscheiden sich zwei Hauptaufgaben:

| Aufgabe | Zielvariable ist… | Typische Beispiel-Frage |
| --- | --- | --- |
| Klassifikation | kategorial (oft binär 0/1) | Kündigt der Kunde? Wird die Lieferung verspätet? Fällt der Kredit aus? |
| Regression | numerisch / kontinuierlich | Wie hoch ist der Umsatz im nächsten Monat? Wie hoch ist der Energieverbrauch? |
| Anomalie-Erkennung | meist ohne expliziten Label (oder über Residuen) | Welche Beobachtungen weichen so stark ab, dass sie eine Prüfung verdienen? |

Welcher dieser Typen für Ihr Projekt gilt, leiten Sie aus Ihrer Zielvariable im Datensatz ab. Im Sprint 1 ist dies eine der ersten Entscheidungen, die Sie treffen — und im ML Canvas dokumentieren.

Für die IHK-Prüfung reichen einfache, robuste Modelle. Im Fachgespräch ist **Erklärbarkeit wichtiger als Genauigkeit**.

| Modell | So funktioniert es (einsatzlang) | Stärke | Schwäche |
| --- | --- | --- | --- |
| Logistische Regression | Lernt Gewichte pro Merkmal, gibt eine Wahrscheinlichkeit zurück | Sehr erklärbar (Sie können pro Merkmal sagen, wie es das Ergebnis verschiebt) | Modelliert nur lineare Zusammenhänge |
| Decision Tree | Reihe von Ja/Nein-Fragen, die zu einer Klasse führen | Sehr anschaulich, ein Baum lässt sich zeichnen | Neigt zu Overfitting, einzelne Bäume sind instabil |
| Random Forest | Viele Decision Trees, Mehrheitsentscheid | Robust, gute Standard-Wahl | Black-Box-Charakter; Feature Importance verzerrt zugunsten kontinuierlicher Merkmale |

| Modell | So funktioniert es | Stärke | Schwäche |
| --- | --- | --- | --- |
| Lineare Regression | Lineare Gleichung über die Merkmale | Sehr erklärbar | Nur lineare Zusammenhänge |
| Random Forest Regressor | Bäume, Mittelwert der Vorhersagen | Robust, nicht-linear | Black-Box |
| Gradient Boosting (z. B. XGBoost) | Bäume, die nacheinander Fehler korrigieren | Oft beste Genauigkeit | Schwerer zu erklären, mehr Hyperparameter |

**Empfehlung für das IHK-Projekt:** Beginnen Sie mit einem **logistischen / linearen** Modell. Vergleichen Sie es mit einem **Random Forest**. Wenn beide ähnlich gut sind, ist die logistische / lineare Variante die bessere Wahl für die Verteidigung im Fachgespräch.

![Welche Metrik passt zu welcher Aufgabe?](https://www.notion.so/image/attachment%3Ac5506f77-4acf-42d3-bba7-84287efb5603%3AL06_evaluationsmetriken_entscheidungsbaum.svg?table=block&id=a0334195-9979-417d-b56f-3fb823e6674c&cache=v2)

Welche Metrik passt zu welcher Aufgabe?

Die **falsche Metrik** ist die häufigste vermeidbare Fehlerquelle im IHK-Fachgespräch. Diese Übersicht zeigt, was zu welcher Aufgabe passt.

| Metrik | Was sie misst | Wann sinnvoll |
| --- | --- | --- |
| Accuracy | Anteil korrekter Vorhersagen | Klassen sind etwa gleich groß (z. B. 50/50) |

| Metrik | Was sie misst | Wann sinnvoll |
| --- | --- | --- |
| Recall (Sensitivität) | Anteil der echten Positiven, die gefunden wurden | Sie wollen so viele wie möglich der positiven Klasse erwischen (z. B. alle gefährdeten Kund:innen) |
| Precision | Anteil der vorhergesagten Positiven, die wirklich positiv sind | Sie wollen wenige Fehlalarme |
| F1 | Harmonisches Mittel aus Precision und Recall | Sie wollen beides ausbalancieren |
| ROC-AUC | Wie gut das Modell die Klassen rangiert (0,5 = Zufall, 1,0 = perfekt) | Sie vergleichen Modelle unabhängig vom Schwellwert |

> 📌 **NordWind-Beispiel — Churn-Klassifikation**
> 
> Bei der NordWind Shop GmbH ist die Marketing-Leiterin Lara Hoffmann an einer Liste der Kund:innen interessiert, die in den nächsten 30 Tagen wahrscheinlich kündigen. Historisch kündigen rund 8 % der aktiven Kund:innen in einem Monat — die Klassen sind also unausgeglichen.
> 
> Was passiert, wenn die Gruppe **Accuracy** als Hauptmetrik wählt? Ein Modell, das **nie** Churn vorhersagt, erreicht bereits 92 % Accuracy — und ist im Geschäft völlig nutzlos: Lara erhält eine leere Liste. **Recall** auf der Churn-Klasse misst stattdessen, _welcher Anteil der tatsächlich gefährdeten Kund:innen_ gefunden wird. Ergänzend dazu **ROC-AUC** für ein schwellwert-unabhängiges Ranking.
> 
> Im Bericht und im Fachgespräch verteidigen Sie die Wahl wie folgt: _„Wir berichten Recall als Hauptmetrik, weil das Geschäftsziel darin besteht, möglichst viele der gefährdeten Kund:innen frühzeitig zu erkennen. Accuracy wäre hier irreführend, weil die Klassen unbalanciert sind."_

| Metrik | Was sie misst | Wann sinnvoll |
| --- | --- | --- |
| RMSE (Root Mean Squared Error) | Durchschnittlicher Fehler, große Fehler werden stärker bestraft | Standard-Wahl; berichten Sie in der Einheit der Zielvariable |
| MAE (Mean Absolute Error) | Durchschnittlicher absoluter Fehler | Robust gegen Ausreißer |
| R² (Bestimmtheitsmaß) | Anteil der erklärten Varianz (0–1) | Vergleich gegen einen naiven Baseline |

> 📌 **NordWind-Beispiel — Umsatzprognose**
> 
> Angenommen, die NordWind Shop GmbH möchte zusätzlich zur Churn-Liste eine **wöchentliche Umsatzprognose** pro Produktkategorie, damit das Einkaufsteam die Bestellmengen passend dimensionieren kann. Das ist eine **Regressionsaufgabe**: die Zielvariable ist der Umsatz pro Kategorie und Woche, in EUR.
> 
> Die Hauptmetrik ist **RMSE in EUR** — derselbe Einheitenkontext, in dem das Einkaufsteam denkt. Wenn das Modell im Schnitt um 1 800 € pro Woche und Kategorie daneben liegt, ist das eine konkrete, geschäftliche Aussage. **R²** ergänzt um eine Einordnung: wie viel besser ist das Modell als ein einfacher Mittelwert? Ein R² von 0,7 heißt, das Modell erklärt 70 % der Varianz — deutlich besser als die Baseline.
> 
> Im Fachgespräch verteidigen Sie die Wahl: _„Wir berichten RMSE in EUR, weil das Einkaufsteam in Euro plant. R² ergänzt um die Einordnung gegen eine konstante Baseline."_

In vielen realen Klassifikationsaufgaben ist die positive Klasse unterrepräsentiert — zum Beispiel sind kündigende Kund:innen, ausfallende Kredite oder verspätete Lieferungen typischerweise eine Minderheit. Wenn Ihre Aufgabe darunter fällt:

-   **Accuracy ist irreführend.** Eine „immer-negativ"-Vorhersage erreicht hohe Accuracy, ist aber geschäftlich nutzlos.

-   `class_weight='balanced'` im Random Forest / der logistischen Regression hilft, weil das Modell die seltene Klasse stärker gewichtet.

-   Berichten Sie **Recall** und **ROC-AUC** als Hauptmetriken.

-   Vergleichen Sie immer gegen eine **Baseline**: „Mehrheitsklasse-Vorhersage" oder „letzter beobachteter Wert".

Bevor Sie ein Modell evaluieren, müssen Sie Trainings- und Testdaten trennen:

-   **Stratifizierter Zufalls-Split** (für unabhängige Beobachtungen): typisch 75 % / 25 %, mit `stratify=y` bei imbalanced classes.

-   **Zeitlicher Split** (wenn Ihre Zielvariable über die Zeit gemessen wird — z. B. Umsatzprognosen oder Verbrauchsdaten): Training auf älteren Zeiträumen, Test auf neueren. Ein zufälliger Split bei Zeitreihen ist **Datenleckage** — das Modell sieht im Training Werte aus der Zukunft des Testzeitraums.

Diese Wahl müssen Sie im Fachgespräch begründen können.

Nach dem Training fragen Sie: welche Merkmale tragen das Modell?

-   **Impurity-basierte Importance** (Standard bei Random Forest) bevorzugt **kontinuierliche Merkmale** mit vielen einzigartigen Werten — auch wenn diese Merkmale kein echtes Signal haben.

-   **Permutationsbasierte Importance** ist robuster: sie mischt die Werte einer Spalte zufällig und beobachtet den Performance-Verlust. `sklearn.inspection.permutation_importance`.

-   **Logistische Regressions-Koeffizienten** sind direkt interpretierbar (Vorzeichen + Größe).

Für den Bericht: berichten Sie Feature Importance — aber **caveat** en Sie sie. Beispiel: „Salary erscheint mit Random-Forest-Importance hoch, korreliert aber stark mit Position. Eine permutationsbasierte Auswertung zeigt, dass Position das eigentliche Signal trägt."

-   Was ist der Unterschied zwischen Klassifikation und Regression?

-   Warum nicht Accuracy als Hauptmetrik bei unbalanced classes?

-   Was ist Ihr Train/Test-Split — und warum dieser?

-   Welche Merkmale tragen Ihr Modell, und sind diese geschäftlich plausibel?

ML-Grundlagen für die IHK reichen knapp: überwacht vs. unüberwacht, Klassifikation vs. Regression, ein einfaches Modell, die richtige Metrik, einen begründeten Train/Test-Split. **Wichtiger als das beste Modell ist das Modell, das Sie verteidigen können.** Beginnen Sie mit logistischer / linearer Regression, vergleichen Sie mit einem Random Forest.

Wählen Sie die Metrik nach Klassen-Balance, nicht nach Gewohnheit. Caveat-en Sie Feature Importance bei Random Forest. In der nächsten Lektion fügen wir diese Grundlagen in das Geschäftsbild ein — den Machine Learning Canvas, Kapitel 2 Ihres Berichts.

---
*Source: https://app.masterschool.com/campus/lesson/ML-Grundlagen-f-r-den-Canvas-c51b/60e0*  
*All content belongs to its respective owners and creators.*