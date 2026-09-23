# Die Präsentation strukturieren — 30 Minuten Konzept, 15 Minuten Demo

Am Prüfungstag stehen Sie als Dreier-Gruppe vor einer IHK-Vertreter:in und einer Masterschool-Dozent:in. Sie haben 45 Minuten: 30 Minuten Konzept-Präsentation, dann 15 Minuten Live-Demo. Danach kommt das individuelle Fachgespräch. Die Frage ist nicht: _„Wie viele Folien?"_ — sondern: _„Welche Geschichte erzählen wir, und welche Folien sind dafür unverzichtbar?"_

Nach dieser Lektion können Sie:

-   die 45-Minuten-Präsentation in einen 30-Minuten-Konzept-Block und einen 15-Minuten-Live-Demo-Block strukturieren — mit ca. 6–8 Konzept-Folien plus Backup,

-   die drei Bewertungsachsen (Inhalt und Struktur 16, Sprache 8, Präsenz 6) erkennen und für jede gezielt vorbereiten.

💭 **Verwandte Vorlage** — `Praesentationsvorlage_IHK.pptx` enthält 15 Folien (8 Konzept + 2 Live-Demo + 1 Schluss + 3 Backup + 1 Übergang) inklusive Sprechertexten in den Notizen. Kopieren Sie sie als Startpunkt.

| Kriterium | Punkte |
| --- | --- |
| Inhalt und Struktur | 16 |
| Sprache | 8 |
| Präsenz | 6 |
| Summe | 30 |

Sie werden also nicht nur am Inhalt gemessen, sondern auch an **wie** Sie ihn vortragen. Üben Sie laut. Mindestens dreimal komplett.

![Die 45+45-Minuten-Zeitschiene](https://www.notion.so/image/attachment%3A293cd2ef-fde7-45d4-a674-4b3d05720cea%3AL10_praesentation_zeitschiene.svg?table=block&id=6e9ed992-495d-400b-af8a-191a0988ba7c&cache=v2)

Die 45+45-Minuten-Zeitschiene

_Die 45+45-Minuten-Zeitschiene_

Sechs Folien-Themen reichen. Jedes Gruppenmitglied übernimmt **mindestens eine Sektion eigenständig** (IHK-Pflicht: individuelle Sichtbarkeit).

| # | Folie | Inhalt | Zeit |
| --- | --- | --- | --- |
| 1 | Titel + Gruppe | Projekttitel, Teilnehmende, Datum | ca. 30 sec |
| 2 | Agenda | Block 1 / 2 / 3 — Strukturhinweis für die Kommission | ca. 30 sec |
| 3 | Ausgangssituation | Organisation, Problem, Ziel — Kapitel 1 in einer Folie | 3 min |
| 4 | ML Canvas (Highlights) | Die 5 wichtigsten Felder, nicht alle 10 | 5 min |
| 5 | Daten und Datenqualität | Was Sie gefunden, was Sie bereinigt haben | 4 min |
| 6 | Methodik | Modelltyp, Train/Test-Split, Metrik-Wahl | 6 min |
| 7 | Ergebnisse | Hauptmetrik, Baseline, Feature Importance, eine Visualisierung | 6 min |
| 8 | Empfehlungen + Ausblick | Konkrete nächste Schritte, persönliches Fazit | 3 min |

Die T4-Präsentationsvorlage liefert genau diese Folien plus Backup-Slides.

**Wenig Text, eine zentrale Aussage.** Faustregel: eine Folie sollte in 6 Sekunden lesbar sein, danach sprechen Sie über sie — nicht umgekehrt.

| Funktioniert | Funktioniert nicht |
| --- | --- |
| Eine Überschrift, max. 5 Bullet-Points, max. 12 Wörter pro Bullet | Fließtext-Absätze auf der Folie |
| Eine zentrale Zahl groß: „ROC-AUC: 0,72" | Drei Tabellen nebeneinander, alles in 8 pt |
| Eine Visualisierung, deren Aussage in einem Satz unter dem Chart steht | Standard-Excel-Chart ohne Achsenbeschriftung |
| Markierungen / Hervorhebungen, wo die Kommission hinschauen soll | „Findet das selbst raus"-Charts |

-   **Ein gut beschrifteter Balken- oder Linien-Chart** mit der Hauptaussage als Untertitel.

-   **Confusion Matrix** als Tabelle (4 Zellen, beschriftet) — wenn Klassifikation.

-   **Residuen-Plot** — wenn Regression / Anomalie.

-   **Feature Importance** als Balken-Chart, **mit** Plausibilitäts-Kommentar.

Vermeiden Sie:

-   Pie Charts mit mehr als 3 Segmenten.

-   Punkt-Wolken ohne Trendlinie.

-   Charts, die aus dem Tool kopiert wurden ohne Achsen-Beschriftung.

-   Mehr als 4 Farben auf einer Folie.

Die häufigste Schwäche in der 30-Minuten-Präsentation ist **zu viel Inhalt**. Sie haben drei Wochen gearbeitet — der Versuch, alles zu zeigen, verteilt die Aufmerksamkeit. Lassen Sie weg:

-   Die vollständige Datenbereinigungs-Liste (3 Beispiele reichen — den Rest erwähnen Sie als „neben weiteren X Problemen").

-   Alle 10 Canvas-Felder einzeln (zeigen Sie 5, der Rest ist im Bericht).

-   Hyperparameter-Tabellen.

-   Code-Schnipsel — die kommen in der Live-Demo, nicht in der Konzept-Sektion.

-   Mehrere alternative Modelle, die Sie nicht ausgewählt haben.

In diesem Block zeigen Sie Ihren Workflow tatsächlich laufend. Empfohlener Ablauf:

| # | Schritt | Zeit |
| --- | --- | --- |
| 1 | Rohdaten öffnen, Qualitätsprobleme zeigen | 2 min |
| 2 | Bereinigungspipeline laufen lassen (Output sichtbar) | 3 min |
| 3 | EDA — die zwei wichtigsten Visualisierungen | 3 min |
| 4 | Modell trainieren und evaluieren | 4 min |
| 5 | Dashboard / Ergebnis-Übergabe | 2 min |
| 6 | Puffer und Rückfragen-Antizipation | 1 min |

**Üben Sie die Demo mindestens dreimal komplett mit Stoppuhr.** Live-Demos scheitern an Kleinigkeiten — Pfadfehler, Tool startet nicht, Datei wird nicht gefunden. Halten Sie immer ein **Backup-Notebook** mit gecachten Ergebnissen bereit, das die Demo in 5 Minuten durchgehen kann, wenn etwas live nicht funktioniert.

Drei Personen, sieben Konzept-Folien plus Demo. Vorschlag:

| Person | Folien | Logik |
| --- | --- | --- |
| Person A | 3 (Ausgangssituation), 8 (Empfehlungen) | Klammert das Projekt geschäftlich ein |
| Person B | 4 (ML Canvas), 5 (Daten und Qualität) | Verbindung von Geschäftsfrage und Daten |
| Person C | 6 (Methodik), 7 (Ergebnisse), Live-Demo-Lead | Technische Seite |

Die individuelle Sichtbarkeit ist **IHK-Pflicht**. Wenn drei Personen vor der Kommission stehen und nur eine spricht, kostet das Punkte.

Die Bewertung Sprache (8 Punkte) und Präsenz (6 Punkte) zielt auf:

| Kriterium | Was gut wirkt | Was nicht |
| --- | --- | --- |
| Deutlichkeit | Klare Aussprache, ruhiges Tempo | Genuscheltes, Fülltext-Geschwindigkeit |
| Variation in der Betonung | Wichtige Zahlen leicht betonen | Monotones Vortragen |
| Pausen-Technik | Nach einer wichtigen Zahl eine Sekunde Stille | Durchgängiges Sprechen ohne Atemzeichen |
| Blickkontakt | Wechselnd zur Kommission und zur Gruppe | Folie ablesen |
| Freies Sprechen | Speaker-Notes nur als Stützpunkte | Folien als Skript vorlesen |
| Sicheres Auftreten | Ruhige Körperhaltung, Hände locker | Hände in Hosentaschen, Wippen |

Tipp: nehmen Sie eine Generalprobe auf Video auf. Sie sehen sich selbst — das ist unbequem, aber zeigt sofort, was zu üben ist.

-   Detail-Metriken (Confusion Matrix, per-Segment-Performance)

-   Ethik-Diskussion (welche Features wurden ausgeschlossen und warum)

-   Kosten-Annahmen (Quellen, Sensitivität)

-   Alternativen, die Sie ausprobiert haben

-   **Zu viele Folien** (mehr als 12 für die 30-Minuten-Sektion). Sie werden in Zeitdruck kommen.

-   **Folien ablesen.** Sofort sichtbar, kostet bei „Präsenz" Punkte.

-   **Live-Demo, die nicht funktioniert**, und kein Backup bereit.

-   **Nur eine Person spricht.** Verletzt die Sichtbarkeits-Anforderung.

-   **Generischer Schluss.** „Vielen Dank für Ihre Aufmerksamkeit" ohne klare Übergabe ans Fachgespräch.

Die 45-Minuten-Präsentation ist 30 Punkte wert und besteht aus 30 Minuten Konzept + 15 Minuten Live-Demo. Konzeptlich reichen sieben Hauptfolien plus Backup. Halten Sie Folien knapp, eine Aussage pro Folie.

Üben Sie die Demo mit Stoppuhr und halten Sie ein Backup-Notebook bereit. Bewertet werden Inhalt, Struktur, Sprache und Präsenz — jede Person muss eigenständig sprechen. In der nächsten Lektion: wie Sie sich auf das individuelle Fachgespräch vorbereiten — die zweite Hälfte der mündlichen Prüfung.

---
*Source: https://app.masterschool.com/campus/lesson/Die-Pr-sentation-strukturieren---30-Minuten-Konzept--15-Minuten-Demo-90e9/50e5*  
*All content belongs to its respective owners and creators.*