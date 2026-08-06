"""CLI-Einstiegspunkt: pull -> ingest -> analyse -> render -> Terminal-Summary.

    python -m dashboard.main [--max N] [--no-fetch] [--rebuild] [--open]
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from datetime import datetime, timezone

from . import config
from .analysis import run_all
from .ingest import ingest_match, rebuild_all
from .render import render_dashboard
from .riot_client import MissingApiKey, RiotApiError, RiotClient
from .storage import Storage

TIER_ORDER = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD",
              "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]


def _fmt_tier(entry: dict | None) -> dict:
    if not entry:
        return {"tier_label": "Unranked", "lp": 0, "wins": 0, "losses": 0,
                "season_winrate": None}
    tier = (entry.get("tier") or "").title()
    rank = entry.get("rank", "")
    # Master+ hat keine Division.
    div = "" if entry.get("tier") in ("MASTER", "GRANDMASTER", "CHALLENGER") else f" {rank}"
    wins = entry.get("wins", 0)
    losses = entry.get("losses", 0)
    total = wins + losses
    return {
        "tier_label": f"{tier}{div}".strip(),
        "lp": entry.get("leaguePoints", 0),
        "wins": wins,
        "losses": losses,
        "season_winrate": round(100 * wins / total, 1) if total else None,
    }


def resolve_puuid(client: RiotClient, store: Storage) -> str:
    puuid = store.get_meta("puuid")
    if puuid:
        return puuid
    print(f"Loese PUUID fuer {config.RIOT_ID_NAME}#{config.RIOT_ID_TAG} auf ...", flush=True)
    acc = client.get_account_by_riot_id(config.RIOT_ID_NAME, config.RIOT_ID_TAG)
    puuid = acc["puuid"]
    store.set_meta("puuid", puuid)
    store.set_meta("riot_id", f"{acc.get('gameName')}#{acc.get('tagLine')}")
    return puuid


def fetch_incremental(client: RiotClient, store: Storage, puuid: str, max_new: int) -> int:
    """Zieht nur neue Ranked-Solo/Duo-Matches. Stoppt bei erster bekannter ID."""
    known = store.known_match_ids()
    new_ids: list[str] = []
    start = 0
    page = 100
    print("Suche neue Match-IDs ...", flush=True)
    while len(new_ids) < max_new:
        ids = client.get_match_ids(puuid, start=start, count=page,
                                   queue=config.QUEUE_RANKED_SOLO)
        if not ids:
            break
        hit_known = False
        for mid in ids:
            if mid in known:
                hit_known = True
                break
            new_ids.append(mid)
            if len(new_ids) >= max_new:
                break
        if hit_known or len(ids) < page:
            break
        start += page

    new_ids = new_ids[:max_new]
    if not new_ids:
        print("Keine neuen Matches — DB ist aktuell.", flush=True)
        return 0

    print(f"{len(new_ids)} neue Matches werden geholt (Match + Timeline) ...", flush=True)
    done = 0
    for i, mid in enumerate(new_ids, 1):
        try:
            match = client.get_match(mid)
            timeline = client.get_timeline(mid)
        except RiotApiError as exc:
            print(f"  [{i}/{len(new_ids)}] {mid} uebersprungen: {exc}", flush=True)
            continue
        store.store_raw(mid, match, timeline)
        ingest_match(store, mid, match, timeline, puuid)
        done += 1
        if i % 10 == 0 or i == len(new_ids):
            print(f"  [{i}/{len(new_ids)}] geholt ...", flush=True)
    return done


def print_summary(results: dict, rank: dict, window_note: str | None = None) -> None:
    line = "=" * 62
    print(f"\n{line}")
    print("  TURBOGURKE — CLIMB TRACKER · Top-Baustellen (LP-Impact)")
    print(line)
    scope = window_note if window_note else "DB gesamt"
    print(f"  Rank: {rank['tier_label']} {rank['lp']} LP   |   "
          f"Winrate ({scope}): {results['overall']['winrate']}% "
          f"({results['overall']['wins']}W/{results['overall']['losses']}L, "
          f"{results['overall']['games']} Games)")
    print(line)
    if not results["problems"]:
        print("  Zu wenig Daten fuer belastbare Priorisierung. Zieh mehr Games.")
    for i, p in enumerate(results["problems"], 1):
        print(f"\n  [{i}]  {p['title']}   (~{p['lp_impact']} LP)")
        print(f"       {p['detail']}")
        print(f"       -> {p['advice']}")
    print(f"\n{line}")
    print("  LP-Werte sind Schaetzungen (~20 LP/Netto-Sieg), nur zur Priorisierung.")
    print(line + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lokales LoL-Performance-Dashboard")
    parser.add_argument("--max", type=int, default=300,
                        help="Max. neue Matches pro Lauf (Erst-Backfill-Cap). Default 300.")
    parser.add_argument("--last", type=int, default=None,
                        help="Nur die juengsten N Games auswerten (z. B. --last 50 fuer die aktuelle Form).")
    parser.add_argument("--no-fetch", action="store_true",
                        help="Nicht von der API ziehen, nur aus der DB rendern.")
    parser.add_argument("--rebuild", action="store_true",
                        help="Abgeleitete Tabellen aus dem Raw-Cache neu berechnen.")
    parser.add_argument("--open", action="store_true",
                        help="Dashboard nach dem Rendern im Browser oeffnen.")
    args = parser.parse_args(argv)

    store = Storage(config.DB_PATH)
    rank = _fmt_tier(None)

    try:
        if not args.no_fetch:
            try:
                client = RiotClient()
            except MissingApiKey as exc:
                print(f"\nFEHLER: {exc}\n", file=sys.stderr)
                print("Tipp: mit --no-fetch kannst du ohne Key aus vorhandener DB rendern.",
                      file=sys.stderr)
                return 2

            puuid = resolve_puuid(client, store)

            # Rank/LP
            try:
                entries = client.get_league_entries_by_puuid(puuid)
                solo = next((e for e in entries if e.get("queueType") == "RANKED_SOLO_5x5"), None)
                rank = _fmt_tier(solo)
                store.set_meta("rank_json", json.dumps(rank))
            except RiotApiError as exc:
                print(f"  Rank konnte nicht geladen werden: {exc}", flush=True)

            fetch_incremental(client, store, puuid, args.max)
        else:
            puuid = store.get_meta("puuid")
            if not puuid:
                print("Keine PUUID in der DB — erster Lauf braucht einen API-Key (ohne --no-fetch).",
                      file=sys.stderr)
                return 2
            # Rank aus dem letzten Online-Lauf wiederverwenden (Offline-Render).
            cached = store.get_meta("rank_json")
            if cached:
                try:
                    rank = json.loads(cached)
                except (ValueError, TypeError):
                    try:  # Fallback: aeltere Laeufe speicherten Python-repr
                        import ast
                        rank = ast.literal_eval(cached)
                    except (ValueError, SyntaxError):
                        pass

        if args.rebuild:
            print("Baue abgeleitete Tabellen aus dem Raw-Cache neu ...", flush=True)
            n = rebuild_all(store, puuid)
            print(f"  {n} Matches neu verarbeitet.", flush=True)

        # Analyse
        player_rows = store.player_matches()   # chronologisch aufsteigend
        laning_rows = store.laning_rows()
        # --last N: nur die juengsten N Games auswerten (Naeherung fuer
        # "aktuelle Form / ab aktuellem Rank"; Riot liefert kein Tier-pro-Game).
        window_note = None
        if args.last and args.last < len(player_rows):
            player_rows = player_rows[-args.last:]
            keep = {r["match_id"] for r in player_rows}
            laning_rows = [r for r in laning_rows if r["match_id"] in keep]
            window_note = f"letzte {len(player_rows)} Games"
            print(f"Filter: nur {window_note} (von {store.match_count()} in DB).", flush=True)
        results = run_all(player_rows, laning_rows)

        # Render
        meta = {
            "generated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
            "version": "1.0.0",
            "verbose": True,
            "window_note": window_note,
        }
        path = render_dashboard(results, rank, meta)
        print(f"\nDashboard geschrieben: {path}", flush=True)

        # Terminal-Summary
        print_summary(results, rank, window_note)

        if args.open:
            webbrowser.open(f"file://{path.resolve()}")
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
