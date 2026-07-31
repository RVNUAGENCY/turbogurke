"""Synthetische Match-/Timeline-JSONs -> DB -> Analyse -> HTML.

Zweck: die Ingest-/Analyse-/Render-Logik ohne echten API-Key end-to-end
pruefen und ein Demo-Dashboard erzeugen. Kein Netzwerkzugriff (ausser dem
einmaligen Chart.js-Download beim Rendern).

    python -m dashboard.tests.generate_sample
"""

from __future__ import annotations

import random
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .. import config
from ..analysis import run_all
from ..ingest import ingest_match
from ..render import render_dashboard
from ..storage import Storage

PUUID = "SAMPLE-PUUID"
CHAMPS = ["Jinx", "Caitlyn", "Kai'Sa", "Ezreal", "Lucian",   # Main-Pool ADC
          "Aphelios", "Vayne", "Zeri", "Nilah", "Draven"]      # Off-Champs
POSITIONS = ["BOTTOM", "BOTTOM", "BOTTOM", "JUNGLE"]  # ADC-Main, Jungle-Neben


def _participant(pid: int, puuid: str, team: int, pos: str, champ: str,
                 win: bool, rng: random.Random) -> dict:
    k = rng.randint(2, 12)
    d = rng.randint(2, 9)
    a = rng.randint(3, 18)
    return {
        "participantId": pid, "puuid": puuid, "teamId": team,
        "championName": champ, "teamPosition": pos, "individualPosition": pos,
        "win": win, "kills": k, "deaths": d, "assists": a,
        "totalMinionsKilled": rng.randint(120, 240),
        "neutralMinionsKilled": rng.randint(0, 40),
        "goldEarned": rng.randint(9000, 16000),
        "totalDamageDealtToChampions": rng.randint(12000, 32000),
    }


def _build_match(mid: str, creation_ms: int, champ: str, pos: str,
                 win: bool, autofill: bool, rng: random.Random) -> tuple[dict, dict]:
    my_pos = pos
    played_pos = pos
    if autofill:
        # zugewiesen != gespielt
        played_pos = "UTILITY" if pos == "BOTTOM" else "MIDDLE"
    duration = rng.randint(18, 38) * 60
    parts = []
    # Team 100: mein Team. participant 1 = ich.
    parts.append(_participant(1, PUUID, 100, my_pos, champ, win, rng))
    parts[0]["individualPosition"] = played_pos
    filler = ["TOP", "JUNGLE", "MIDDLE", "UTILITY"]
    for i, fp in enumerate(filler, start=2):
        parts.append(_participant(i, f"ally{i}", 100, fp, "Ally", win, rng))
    # Team 200: Gegner. Lane-Gegner = gleiche teamPosition wie ich.
    opp_positions = [my_pos] + [p for p in filler]
    for i, fp in enumerate(opp_positions, start=6):
        parts.append(_participant(i, f"enemy{i}", 200, fp, "Enemy", not win, rng))

    match = {
        "metadata": {"matchId": mid, "participants": [p["puuid"] for p in parts]},
        "info": {
            "queueId": 420, "gameCreation": creation_ms,
            "gameDuration": duration, "gameVersion": "14.14.1",
            "participants": parts,
        },
    }

    # Timeline: Frames im 60s-Raster mit participantFrames + Death-Events.
    frames = []
    my_lead = rng.choice([-1, -1, 1])  # tendenziell leichtes Behind
    for minute in range(0, duration // 60 + 1):
        pframes = {}
        for p in parts:
            base_cs = int(minute * rng.uniform(6.0, 8.5))
            gold = 500 + minute * rng.randint(280, 360)
            xp = minute * rng.randint(380, 460)
            pframes[str(p["participantId"])] = {
                "minionsKilled": base_cs,
                "jungleMinionsKilled": rng.randint(0, minute),
                "totalGold": gold, "currentGold": gold // 2, "xp": xp,
            }
        # Mein CS/Gold leicht anpassen fuer realistische Diffs
        me = pframes["1"]
        me["totalGold"] += my_lead * rng.randint(0, 600)
        me["xp"] += my_lead * rng.randint(0, 400)
        events = []
        # ein paar Deaths ueber das Spiel verteilt (Early-lastig)
        if minute in (rng.randint(3, 12), rng.randint(4, 20)):
            events.append({"type": "CHAMPION_KILL", "victimId": 1,
                           "killerId": 6, "timestamp": minute * 60000})
        frames.append({"timestamp": minute * 60000,
                       "participantFrames": pframes, "events": events})

    timeline = {"metadata": {"matchId": mid},
                "info": {"frameInterval": 60000, "frames": frames}}
    return match, timeline


def build_sample_db(store: Storage, n: int = 120, seed: int = 7) -> None:
    rng = random.Random(seed)
    now_ms = 1_720_000_000_000
    # Sessions simulieren: Bloecke von Games dicht beieinander, dann grosse Luecke.
    t = now_ms
    for i in range(n):
        # innerhalb Session ~35min Abstand, zwischen Sessions > 2h
        if i > 0 and rng.random() < 0.28:
            t += int(4 * 3600 * 1000)     # neue Session
        else:
            t += int(rng.uniform(30, 45) * 60 * 1000)
        # Main-Champs oefter, hoehere Winrate; Off-Champs seltener, schlechter.
        if rng.random() < 0.68:
            champ = rng.choice(CHAMPS[:5])
            win = rng.random() < 0.56
        else:
            champ = rng.choice(CHAMPS[5:])
            win = rng.random() < 0.40
        pos = rng.choice(POSITIONS)
        autofill = rng.random() < 0.12
        if autofill:
            win = rng.random() < 0.42
        mid = f"EUW1_SAMPLE{i:04d}"
        match, timeline = _build_match(mid, t, champ, pos, win, autofill, rng)
        store.store_raw(mid, match, timeline)
        ingest_match(store, mid, match, timeline, PUUID)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="lol_sample_"))
    db = tmp / "sample.sqlite"
    store = Storage(db)
    store.set_meta("puuid", PUUID)
    build_sample_db(store, n=120)

    player_rows = store.player_matches()
    laning_rows = store.laning_rows()
    print(f"Sample-DB: {len(player_rows)} player_match, {len(laning_rows)} laning rows")

    results = run_all(player_rows, laning_rows)

    # --- Assertions: Logik prueft sich selbst -------------------------------
    o = results["overall"]
    assert o["games"] == 120, o
    assert o["wins"] + o["losses"] == 120
    assert results["champions"], "Champion-Breakdown leer"
    assert results["long_tail"]["top"]["games"] > 0
    assert results["laning"]["cs10"]["dist"]["count"] > 0, "Keine CS@10-Daten"
    assert results["laning"]["gold_diff_10"]["dist"]["count"] > 0
    assert results["deaths"]["timeline_deaths"] > 0, "Keine Timeline-Deaths"
    assert sum(results["deaths"]["phase_counts"]) == results["deaths"]["timeline_deaths"]
    assert len(results["trend"]["y"]) == max(0, 120 - results["trend"]["window"] + 1)
    assert isinstance(results["problems"], list)
    print("Assertions OK.")

    rank = {"tier_label": "Diamond IV", "lp": 47, "wins": 243, "losses": 243,
            "season_winrate": 50.0}
    meta = {"generated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
            "version": "1.0.0-sample", "verbose": True}
    path = render_dashboard(results, rank, meta)
    print(f"Demo-Dashboard: {path}")

    # Terminal-Summary anzeigen
    from ..main import print_summary
    print_summary(results, rank)
    store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
