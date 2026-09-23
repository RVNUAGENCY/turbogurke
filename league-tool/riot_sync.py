#!/usr/bin/env python3
"""Riot-Sync für die "Road to Challenger"-Seite.

Holt Rang, LP und die letzten Ranked-Games eines Riot-Accounts über die
Riot-API und schreibt drei JSON-Dateien, die 1:1 als Dokumente in die
Datenbank der Seite gehen (riot/profile, riot/lp, riot/matches).

    RIOT_API_KEY=RGAPI-… python3 riot_sync.py "Name#TAG" euw1 \
        --lp-in lp_alt.json --out ./out

Nur Standardbibliothek. Der Key kommt ausschließlich aus der Umgebung.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REGIONAL = {  # Plattform -> Routing-Region für account-v1 / match-v5
    "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe", "me1": "europe",
    "na1": "americas", "br1": "americas", "la1": "americas", "la2": "americas",
    "kr": "asia", "jp1": "asia",
    "oc1": "sea", "sg2": "sea", "tw2": "sea", "vn2": "sea",
}
TIERS = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
DIVS = {"IV": 0, "III": 1, "II": 2, "I": 3}
QUEUES = {420: "Solo/Duo", 440: "Flex"}


def api(url, key, tries=4):
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"X-Riot-Token": key, "User-Agent": "road-to-challenger-sync"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                time.sleep(int(e.headers.get("Retry-After", "2")) + 1)
                continue
            if e.code == 404:
                return None
            body = e.read().decode("utf-8", "replace")[:200]
            raise SystemExit(f"Riot-API {e.code} für {url.split('?')[0]}: {body}")
    raise SystemExit("Riot-API: zu viele Versuche")


def ladder_value(tier, rank, lp):
    """Fortlaufende Zahl für den LP-Chart: jede Division = 100, Master+ = 2800 + LP."""
    t = TIERS.index(tier) if tier in TIERS else 0
    if t >= 7:
        return 2800 + lp
    return t * 400 + DIVS.get(rank, 0) * 100 + lp


def entry(e):
    if not e:
        return None
    return {"tier": e["tier"].title(), "rank": e.get("rank", ""), "lp": e["leaguePoints"],
            "wins": e["wins"], "losses": e["losses"], "hotStreak": e.get("hotStreak", False)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("riot_id")
    ap.add_argument("platform", nargs="?", default="euw1")
    ap.add_argument("--lp-in", help="bisheriges riot/lp-Dokument (JSON), wird fortgeschrieben")
    ap.add_argument("--out", default=".")
    ap.add_argument("--count", type=int, default=20)
    a = ap.parse_args()

    key = os.environ.get("RIOT_API_KEY", "").strip()
    if not key:
        raise SystemExit("RIOT_API_KEY fehlt in der Umgebung")
    if "#" not in a.riot_id:
        raise SystemExit("Riot-ID bitte als Name#TAG")
    name, tag = [s.strip() for s in a.riot_id.split("#", 1)]
    plat = a.platform.lower()
    region = REGIONAL.get(plat, "europe")
    q = urllib.parse.quote

    acc = api(f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{q(name)}/{q(tag)}", key)
    if not acc:
        raise SystemExit(f"Riot-ID {a.riot_id} nicht gefunden")
    puuid = acc["puuid"]
    summ = api(f"https://{plat}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}", key) or {}
    leagues = api(f"https://{plat}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}", key) or []
    solo = entry(next((e for e in leagues if e["queueType"] == "RANKED_SOLO_5x5"), None))
    flex = entry(next((e for e in leagues if e["queueType"] == "RANKED_FLEX_SR"), None))
    now = int(time.time() * 1000)

    profile = {"gameName": acc.get("gameName", name), "tagLine": acc.get("tagLine", tag), "platform": plat,
               "level": summ.get("summonerLevel"), "iconId": summ.get("profileIconId"),
               "solo": solo, "flex": flex, "syncedAt": now}

    # LP-Verlauf fortschreiben (ein Punkt pro Sync, nur bei Änderung, max. 300)
    points = []
    if a.lp_in and os.path.exists(a.lp_in):
        try:
            old = json.load(open(a.lp_in))
            points = (old.get("data", old) or {}).get("points", []) or []
        except Exception:
            points = []
    if solo:
        v = ladder_value(solo["tier"].upper(), solo["rank"], solo["lp"])
        if not points or points[-1].get("v") != v:
            points.append({"t": now, "v": v, "tier": solo["tier"], "rank": solo["rank"], "lp": solo["lp"]})
    points = points[-300:]

    # Match-History (Solo/Duo + Flex)
    ids = api(f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&count={a.count}", key) or []
    items = []
    for mid in ids:
        m = api(f"https://{region}.api.riotgames.com/lol/match/v5/matches/{mid}", key)
        if not m:
            continue
        info = m["info"]
        me = next((p for p in info["participants"] if p["puuid"] == puuid), None)
        if not me:
            continue
        dur = info.get("gameDuration", 0)
        opp = next((p for p in info["participants"] if p["teamId"] != me["teamId"]
                    and p.get("teamPosition") and p.get("teamPosition") == me.get("teamPosition")), None)
        team_kills = sum(p["kills"] for p in info["participants"] if p["teamId"] == me["teamId"]) or 1
        items.append({
            "id": mid, "ts": info.get("gameEndTimestamp") or info.get("gameCreation"),
            "queue": QUEUES.get(info.get("queueId"), str(info.get("queueId"))),
            "champ": me["championName"], "enemy": opp["championName"] if opp else "",
            "role": me.get("teamPosition") or me.get("individualPosition") or "",
            "win": bool(me["win"]), "remake": bool(me.get("gameEndedInEarlySurrender")) and dur < 300,
            "k": me["kills"], "d": me["deaths"], "a": me["assists"],
            "cs": me["totalMinionsKilled"] + me["neutralMinionsKilled"], "dur": dur,
            "dmg": me["totalDamageDealtToChampions"], "vision": me["visionScore"],
            "kp": round((me["kills"] + me["assists"]) / team_kills * 100),
            "gold": me["goldEarned"],
        })
    items.sort(key=lambda x: x["ts"] or 0, reverse=True)

    os.makedirs(a.out, exist_ok=True)
    json.dump(profile, open(os.path.join(a.out, "profile.json"), "w"))
    json.dump({"points": points, "updatedAt": now}, open(os.path.join(a.out, "lp.json"), "w"))
    json.dump({"items": items, "updatedAt": now}, open(os.path.join(a.out, "matches.json"), "w"))
    rank = f"{solo['tier']} {solo['rank']} {solo['lp']} LP" if solo else "unranked"
    print(f"OK {profile['gameName']}#{profile['tagLine']} · {rank} · {len(items)} Games · {len(points)} LP-Punkte")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code and not isinstance(e.code, int):
            print("FEHLER:", e.code, file=sys.stderr)
            sys.exit(1)
        raise
