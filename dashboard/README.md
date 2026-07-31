# TURBOGURKE — LoL Performance Dashboard 🥒

Lokales Performance-Dashboard für den Climb **Diamond 4 → Master**
(Account: `TURBOGURKE#TTV`, EUW). Zieht deine Ranked-Solo/Duo-Historie über die
**offizielle Riot Games API** in eine lokale SQLite-DB (inkrementell) und
generiert daraus ein statisches Dark-Mode-HTML-Dashboard + eine priorisierte
Terminal-Zusammenfassung deiner größten Baustellen.

Kein Scraping, kein Server, keine fremde Datenquelle — nur die Riot API und
deine eigene, über Wochen wachsende Historie.

## Features

- **Inkrementeller Pull** mit Rate-Limiter (20 req/s · 100 req/2min) + Backoff — bricht nicht ab.
- **Raw-JSON-Cache** in SQLite: Analysen jederzeit ohne Re-Fetch neu berechenbar (`--rebuild`).
- **7 Auswertungen**: Champion-Breakdown · Long-Tail (Top-5 vs. Rest inkl. LP-Kosten) ·
  Rollen-Split (Autofill separat) · Laning (CS@10/@14, Gold-/XP-Diff@10 **mit Verteilung**) ·
  Tilt-Erkennung (Sessions, Winrate nach Spielposition & nach Niederlage) ·
  Death-Analyse (Deaths/min, Phasen 0–14 / 14–25 / 25+) · rollierende 20-Game-Winrate.
- **Offline-Dashboard**: Chart.js wird einmalig lokal vendored — HTML funktioniert ohne Internet.
- **Terminal-Summary**: Top-3-Baustellen priorisiert nach geschätztem LP-Impact.

## Setup

```bash
cd dashboard
python3 -m venv .venv && source .venv/bin/activate     # optional
pip install -r requirements.txt
```

### API-Key

Hol dir einen Key auf <https://developer.riotgames.com> (Dev-Keys gelten nur 24h)
und setze ihn als Umgebungsvariable — **niemals hardcoden**:

```bash
export RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Account/Region sind auf `TURBOGURKE#TTV` / EUW voreingestellt. Anpassbar über
Umgebungsvariablen: `RIOT_ID_NAME`, `RIOT_ID_TAG`, `RIOT_PLATFORM` (`euw1`),
`RIOT_REGIONAL` (`europe`).

## Nutzung

```bash
# Aus dem Repo-Root (Ordner über dashboard/):
python -m dashboard.main               # pull + analyse + render + summary
python -m dashboard.main --max 500     # erster Backfill weiter zurück (Default 300)
python -m dashboard.main --no-fetch    # nur aus vorhandener DB rendern (kein Key nötig)
python -m dashboard.main --rebuild     # abgeleitete Tabellen aus Raw-Cache neu berechnen
python -m dashboard.main --open        # Dashboard danach im Browser öffnen
```

Der **erste Lauf** backfillt bis `--max` Games (Rate-Limiter greift, dauert
entsprechend). **Jeder weitere Lauf** zieht nur neue Matches und stoppt bei der
ersten bereits bekannten Match-ID → so wächst deine Historie über Wochen.

Ergebnis: `dashboard/output/dashboard.html` — im Browser öffnen.

## Demo ohne API-Key

```bash
python -m dashboard.tests.generate_sample
```

Erzeugt synthetische Matches, prüft die komplette Ingest-/Analyse-/Render-Pipeline
(mit Assertions) und rendert ein Demo-Dashboard.

## Projektstruktur

```
dashboard/
├── config.py         # Routen, Queue-IDs, Pfade, LP-Konstanten
├── riot_client.py    # Riot-API-Client + Rate-Limiter + Backoff
├── storage.py        # SQLite-Schema + Raw-JSON-Cache + Upserts
├── ingest.py         # Roh-JSON -> player_match / laning (rein, testbar)
├── analysis.py       # die 7 Auswertungen + Baustellen-Priorisierung
├── render.py         # Jinja2 -> HTML, vendored Chart.js
├── main.py           # CLI-Orchestrierung
├── templates/dashboard.html.j2
└── tests/generate_sample.py
```

Sauber getrennte Module — zum Erweitern: neue Analyse in `analysis.py` ergänzen,
im Template rendern. Da alle Roh-JSONs in der DB liegen, brauchst du dafür
**keinen** neuen API-Pull, nur `--rebuild`.

## Genutzte Riot-Endpoints

| Zweck | Endpoint |
|---|---|
| PUUID | ACCOUNT-V1 `/riot/account/v1/accounts/by-riot-id/{name}/{tag}` |
| Rank/LP | LEAGUE-V4 `/lol/league/v4/entries/by-puuid/{puuid}` (Fallback via SUMMONER-V4) |
| Match-IDs | MATCH-V5 `/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420` |
| Match + Timeline | MATCH-V5 `/lol/match/v5/matches/{id}` und `/{id}/timeline` |

## Hinweise

- **Nur Ranked Solo/Duo** (Queue 420) wird ausgewertet.
- **Autofill-Heuristik**: `teamPosition` ≠ `individualPosition`.
- **LP-Zahlen sind Schätzungen** (~20 LP je Netto-Sieg) — sie dienen der
  Priorisierung, nicht als exakte Vorhersage. Riot liefert keine echten LP-Deltas pro Game.
- `output/` und `*.sqlite` sind gitignored (lokale Daten bleiben lokal).
