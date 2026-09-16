# Climb Journal — League Improvement Tool

Eigenständiges Tool (eine HTML-Datei, kein Build, kein Server) für strukturiertes Ranked-Improvement:

**Ziel → Routine → Spielen → Review → Anpassen**

## Nutzung
`index.html` im Browser öffnen — fertig. Alle Daten liegen im `localStorage` des Browsers; unter **Daten** gibt es Export/Import als JSON.

## Module
| Tab | Zweck |
|---|---|
| Heute | Rank/LP, Tagesfokus (aktives Lernziel), Routine-Checkliste, Streak, Kennzahlen, LP-Verlauf |
| Routine | Editierbare Pre-Session / Session-Regeln / Post-Session, 8-Wochen-Verlauf |
| Games | 60-Sekunden-Match-Log, Auswertung pro Champion, Matchup, Fehler-Muster |
| Champions | Pool (Main/Backup/Lernen), Notiz-Sektionen, Matchup-Pläne mit Winrate aus dem Log |
| Lernziele | Messbare Prozess-Ziele mit Fortschritt, Fokus-Markierung |
| Review | Geführter VOD-Review (Tode zuerst, 3 Fragen), Momente mit Timestamps, Takeaways → Lernziele |
| Wochen-Review | Wochenstatistik, häufigste Fehler, Reflexionsfragen |
| Wissen | Fundamentals: Waves, Trading, Tempo, Objectives, Vision, Macro, Mental, Pool, Drills |
| Notizen | Freie Notizen mit Tags und Suche |
| Daten | Export/Import, Beispieldaten entfernen, Reset |

Shortcut: `n` öffnet „Game loggen“.

Der Prompt, aus dem das Tool entstanden ist, liegt in [`PROMPT.md`](PROMPT.md).
