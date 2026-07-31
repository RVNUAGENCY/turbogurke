"""Roh-JSON -> abgeleitete Tabellen.

Reine Transformationslogik ueber Match- und Timeline-JSON. Bewusst getrennt
vom API-Client, damit man sie mit synthetischen JSONs testen kann und die
abgeleiteten Tabellen jederzeit aus dem Raw-Cache neu aufbauen kann.
"""

from __future__ import annotations

import json
from typing import Any

from .storage import Storage


def _find_me(match_json: dict, puuid: str) -> dict | None:
    for p in match_json.get("info", {}).get("participants", []):
        if p.get("puuid") == puuid:
            return p
    return None


def _find_lane_opponent(match_json: dict, me: dict) -> dict | None:
    """Direkter Lane-Gegner = gleiche teamPosition auf dem anderen Team."""
    pos = me.get("teamPosition") or me.get("individualPosition")
    my_team = me.get("teamId")
    if not pos:
        return None
    for p in match_json.get("info", {}).get("participants", []):
        if p.get("teamId") != my_team and (p.get("teamPosition") == pos):
            return p
    return None


def _frame_at(frames: list[dict], target_ms: int) -> dict | None:
    """Frame, dessen Timestamp dem Ziel am naechsten liegt (Frames ~60s-Raster)."""
    if not frames:
        return None
    best = min(frames, key=lambda f: abs(f.get("timestamp", 0) - target_ms))
    return best


def _pframe(frame: dict, pid: int) -> dict:
    return frame.get("participantFrames", {}).get(str(pid), {})


def _cs(pf: dict) -> int:
    return int(pf.get("minionsKilled", 0)) + int(pf.get("jungleMinionsKilled", 0))


def compute_player_match(match_id: str, match_json: dict, puuid: str) -> dict | None:
    me = _find_me(match_json, puuid)
    if me is None:
        return None
    info = match_json.get("info", {})
    team_pos = me.get("teamPosition") or ""
    ind_pos = me.get("individualPosition") or ""
    # Autofill-Heuristik: zugewiesene Rolle != tatsaechlich gespielte Rolle.
    autofill = 1 if (team_pos and ind_pos and team_pos != ind_pos) else 0
    cs = int(me.get("totalMinionsKilled", 0)) + int(me.get("neutralMinionsKilled", 0))
    return {
        "match_id": match_id,
        "game_creation": info.get("gameCreation"),
        "game_duration": info.get("gameDuration"),
        "champion": me.get("championName"),
        "team_position": team_pos,
        "individual_position": ind_pos,
        "autofill": autofill,
        "win": 1 if me.get("win") else 0,
        "kills": int(me.get("kills", 0)),
        "deaths": int(me.get("deaths", 0)),
        "assists": int(me.get("assists", 0)),
        "cs": cs,
        "gold": int(me.get("goldEarned", 0)),
        "dmg": int(me.get("totalDamageDealtToChampions", 0)),
        "death_times_json": json.dumps(_death_times(match_json, timeline=None, me=me)),
    }


def _death_times(match_json: dict, timeline: dict | None, me: dict) -> list[int]:
    """Death-Timestamps (ms) aus der Timeline. Ohne Timeline leere Liste
    (Deaths-Total steht separat im player_match-Zaehler)."""
    if not timeline:
        return []
    my_pid = me.get("participantId")
    times: list[int] = []
    for frame in timeline.get("info", {}).get("frames", []):
        for ev in frame.get("events", []):
            if ev.get("type") == "CHAMPION_KILL" and ev.get("victimId") == my_pid:
                times.append(int(ev.get("timestamp", 0)))
    return times


def compute_laning(match_id: str, match_json: dict, timeline: dict, puuid: str) -> dict | None:
    me = _find_me(match_json, puuid)
    if me is None:
        return None
    opp = _find_lane_opponent(match_json, me)
    frames = timeline.get("info", {}).get("frames", [])
    if not frames:
        return None
    my_pid = me.get("participantId")
    opp_pid = opp.get("participantId") if opp else None

    f10 = _frame_at(frames, 10 * 60 * 1000)
    f14 = _frame_at(frames, 14 * 60 * 1000)
    if f10 is None:
        return None

    my_pf10 = _pframe(f10, my_pid)
    my_pf14 = _pframe(f14, my_pid) if f14 else {}
    cs10 = _cs(my_pf10)
    cs14 = _cs(my_pf14) if my_pf14 else None

    gold_diff = xp_diff = None
    if opp_pid is not None:
        opp_pf10 = _pframe(f10, opp_pid)
        if opp_pf10:
            gold_diff = int(my_pf10.get("totalGold", 0)) - int(opp_pf10.get("totalGold", 0))
            xp_diff = int(my_pf10.get("xp", 0)) - int(opp_pf10.get("xp", 0))

    return {
        "match_id": match_id,
        "cs10": float(cs10),
        "cs14": float(cs14) if cs14 is not None else None,
        "gold_diff_10": float(gold_diff) if gold_diff is not None else None,
        "xp_diff_10": float(xp_diff) if xp_diff is not None else None,
    }


def ingest_match(store: Storage, match_id: str, match_json: dict,
                 timeline_json: dict, puuid: str) -> bool:
    """Berechnet und schreibt player_match + laning fuer ein Match.

    Nur Ranked Solo/Duo (Queue 420) wird uebernommen. Gibt True zurueck,
    wenn eine player_match-Zeile geschrieben wurde.
    """
    info = match_json.get("info", {})
    if info.get("queueId") != 420:
        return False
    me = _find_me(match_json, puuid)
    if me is None:
        return False

    pm = compute_player_match(match_id, match_json, puuid)
    if pm is None:
        return False
    # Death-Timestamps aus der Timeline nachziehen.
    pm["death_times_json"] = json.dumps(_death_times(match_json, timeline_json, me))
    store.upsert_player_match(pm)

    lane = compute_laning(match_id, match_json, timeline_json, puuid)
    if lane is not None:
        store.upsert_laning(lane)
    return True


def rebuild_all(store: Storage, puuid: str) -> int:
    """Alle abgeleiteten Tabellen aus dem Raw-Cache neu aufbauen."""
    n = 0
    for match_id, match_json, timeline_json in store.iter_raw_matches():
        if ingest_match(store, match_id, match_json, timeline_json, puuid):
            n += 1
    return n
