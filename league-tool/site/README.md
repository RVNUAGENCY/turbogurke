# Road to Challenger – Website

Statische Version der Seite für GitHub Pages: https://rvnuagency.github.io/turbogurke/

- `index.html` – die Seite (identisch mit `road-to-challenger.html`)
- `data/riot/*.json` – Rang, LP-Verlauf und letzte Games; werden vom Sync (`../riot_sync.py`) geschrieben

Auf GitHub Pages liest die Seite die Riot-Daten aus `data/riot/`. Fortschritt (Woche, Haken, Kennzahlen) wird dort nur im Browser gespeichert.
Account-Sync, der Sync-Knopf und der Coach-Chat funktionieren nur in der claude.ai-Version der Seite.
