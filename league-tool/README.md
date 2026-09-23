# Climb Journal — League Improvement Tool

Strukturiertes Ranked-Improvement in einer Datei: **Ziel → Routine → Spielen → Review → Anpassen**.
Rank, LP und Ranked-Games kommen automatisch aus der **Riot Games API** — du ergänzt pro Game nur einen Fehler und ein Learning.

## Schnellstart (Live-Sync mit deinem Account)

Die Riot-API darf nicht direkt aus dem Browser aufgerufen werden und braucht einen eigenen Key. Deshalb liegt ein winziger Server dabei (Node, keine Abhängigkeiten), der den Key hält.

1. **Node.js ≥ 18** installieren: https://nodejs.org
2. **Riot-API-Key** holen: https://developer.riotgames.com → mit Riot-Account einloggen → *Development API Key* kopieren.
   Der Development-Key läuft nach **24 h** ab (dann dort neu generieren). Für dauerhaft: dort *Register Product → Personal API Key* beantragen (kostenlos, für private Tools gedacht).
3. Im Ordner `league-tool/` die Datei `.env.example` nach `.env` kopieren und den Key eintragen:
   ```
   RIOT_API_KEY=RGAPI-…
   ```
4. Server starten:
   ```
   cd league-tool
   node server.js
   ```
5. http://localhost:3000 öffnen → **„Riot-Account verbinden“** → Riot-ID im Format `Name#TAG` + Region.

Ab dann lädt das Tool beim Öffnen automatisch Rank, LP und die letzten 20 Ranked-Solo-Games (max. alle 5 Minuten; „↻ Sync“ erzwingt es). Match-Details werden in `cache/` abgelegt, damit das Rate-Limit geschont wird.

Ohne Server (z. B. `index.html` direkt öffnen oder das claude.ai-Artifact) läuft alles manuell — Games trägst du dann selbst ein.

## Was aus der API kommt
Pro Game: Champion, Rolle, Lane-Gegner, Ergebnis, KDA, CS gesamt, **CS @ 10:00**, Gold-Differenz @ 10:00 zum Lane-Gegner, Vision Score, Schaden, Dauer. Rank/Division/LP aus Ranked Solo/Duo.
Nicht aus der API: LP-Änderung pro Game (Riot liefert das nicht — das Tool ordnet sie zu, wenn seit dem letzten Sync genau ein Game dazukam), Tilt, Fehler-Kategorie, Learning — das ist dein Teil.

## Module
| Tab | Zweck |
|---|---|
| Heute | Rank/LP, Tagesfokus (aktives Lernziel), Routine-Checkliste, Streak, Kennzahlen, LP-Verlauf, offene Learnings |
| Routine | Editierbare Pre-Session / Session-Regeln / Post-Session, 8-Wochen-Verlauf |
| Games | Match-Log (API + manuell), Auswertung pro Champion, Matchup, Fehler-Muster |
| Champions | Pool (Main/Backup/Lernen), Notiz-Sektionen, Matchup-Pläne mit Winrate aus dem Log |
| Lernziele | Messbare Prozess-Ziele mit Fortschritt, Fokus-Markierung |
| Review | Geführter VOD-Review (Tode zuerst, 3 Fragen), Momente mit Timestamps, Takeaways → Lernziele |
| Wochen-Review | Wochenstatistik, häufigste Fehler, Reflexionsfragen |
| Wissen | Fundamentals: Waves, Trading, Tempo, Objectives, Vision, Macro, Mental, Pool, Drills |
| Notizen | Freie Notizen mit Tags und Suche |
| Daten | Riot-Verbindung, Export/Import, Beispieldaten entfernen, Reset |

Shortcut: `n` öffnet „Game loggen“.

## Dateien
- `index.html` — das komplette Tool (Vanilla HTML/CSS/JS, Daten im `localStorage`)
- `server.js` — Static-Server + Riot-API-Proxy (`/api/health`, `/api/summoner`, `/api/matches`)
- `.env.example` — Vorlage für den Key (`.env` und `cache/` sind in `.gitignore`)
- `PROMPT.md` — der Prompt, aus dem das Tool entstanden ist

Der Server läuft unverändert auch gehostet (Railway, Render, Fly …): Repo verbinden, `RIOT_API_KEY` als Umgebungsvariable setzen, Start-Befehl `node server.js`.
