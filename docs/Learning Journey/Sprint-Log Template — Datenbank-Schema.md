# Sprint-Log Template — Datenbank-Schema

Empfohlene Spalten (Property-Namen und -Typen). Die Bezeichnungen können Sie an Ihre Spracheinstellung anpassen; entscheidend sind die Typen.

| Spalte | Typ | Beschreibung |
| --- | --- | --- |
| `Sprint` | Auswahl (Select) | `Sprint 1`, `Sprint 2`, `Sprint 3`, `Finalisierung` |
| `User Story` | Text (oder Relation zu einer User-Story-DB) | Die zugehörige User Story, z. B. „Als Vertriebsleiterin möchte ich…" |
| `Aufgabe` | Titel (Title) | Kurze, handlungsorientierte Aufgabenbeschreibung |
| `Verantwortlich` | Person | Eine Person pro Aufgabe |
| `Status` | Auswahl | `Zu erledigen`, `In Bearbeitung`, `Erledigt`, `Blockiert`, `Verschoben` |
| `Definition of Done` | Text | Was bedeutet „erledigt" für genau diese Aufgabe — üblicherweise ein Satz |
| `Blocker` | Text | Wird nur gefüllt, wenn Status = Blockiert |
| `Entscheidung` | Text | Während der Aufgabe getroffene Entscheidungen (eine Zeile) |
| `Anpassungen` | Text | Planänderungen während des Sprints |
| `Sprint-Tag` | Datum | Tag, an dem die Aufgabe in den Sprint kam |
| `Erledigt-Tag` | Datum | Tag, an dem die Aufgabe abgeschlossen wurde |
| `Notizen` | Text | Freie Notizen |

| Name der Ansicht | Filter | Sortierung | Zweck |
| --- | --- | --- | --- |
| Heute | `Status = In Bearbeitung` und `Verantwortlich = ich` | nach `Aufgabe` | Tagesfokus |
| Sprint-Board | nach `Sprint` | gruppiert nach `Status` | Sprint-Planung und Standup |
| Erledigt | `Status = Erledigt` | nach `Erledigt-Tag` absteigend | Sprint-Review und Rohmaterial für Kapitel 3 |
| Blocker | `Status = Blockiert` | nach `Sprint-Tag` absteigend | Was muss entblockt werden |
| Retro | nach `Sprint` | nach gefülltem `Anpassungen` | Sprint-Retrospektive |

Wenn Sie eine separate Datenbank für User Stories anlegen möchten:

| Spalte | Typ |
| --- | --- |
| `Story` | Titel — „Als <Rolle> möchte ich <Ziel>, damit <Nutzen>" |
| `Stakeholder` | Auswahl |
| `Priorität` | Auswahl — Hoch / Mittel / Niedrig |
| `Sprint` | Relation zum Sprint-Log |
| `Status` | Auswahl — Backlog / Aktiv / Abgeschlossen |

Für die meisten Gruppen reicht eine einzelne Sprint-Log-Datenbank. User Stories können im Textfeld `User Story` direkt an der jeweiligen Aufgabe stehen.

**Schlechte** `Aufgabe`**:**`Daten anschauen` (zu vage — wer macht konkret was?)

**Schlechte** `Definition of Done`**:**`Daten sind sauber` (Erfolgskriterium ist nicht messbar)

**Schlechte** `Entscheidung`**:**`Median ist besser` (keine Begründung — Kapitel 3 braucht das _Warum_)

---
*Source: https://app.masterschool.com/campus/lesson/Sprint-Log-Template---Datenbank-Schema-be3d/3b53*  
*All content belongs to its respective owners and creators.*