"""Die sieben Auswertungen. Reine Funktionen ueber die abgeleiteten Tabellen.

Erwartet Listen von dict-artigen Zeilen (sqlite3.Row funktioniert direkt).
Keine DB-, Netz- oder Render-Abhaengigkeit -> gut testbar.
"""

from __future__ import annotations

import json
from statistics import mean, median
from typing import Any, Sequence

from . import config

# Rollen-Labels fuer die Anzeige.
POSITION_LABELS = {
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "MIDDLE": "Mid",
    "BOTTOM": "ADC",
    "UTILITY": "Support",
    "": "Unbekannt",
}


def _label_pos(pos: str | None) -> str:
    return POSITION_LABELS.get(pos or "", pos or "Unbekannt")


def _pct(wins: int, games: int) -> float:
    return round(100.0 * wins / games, 1) if games else 0.0


def _kda(k: int, d: int, a: int) -> float:
    return round((k + a) / d, 2) if d else float(k + a)


def _percentile(values: Sequence[float], q: float) -> float:
    """Lineare Interpolation (Typ wie numpy default). q in [0,1]."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return round(s[0], 1)
    idx = q * (len(s) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(s) - 1)
    frac = idx - lo
    return round(s[lo] + (s[hi] - s[lo]) * frac, 1)


def _distribution(values: Sequence[float]) -> dict:
    vals = [v for v in values if v is not None]
    if not vals:
        return {"count": 0}
    return {
        "count": len(vals),
        "mean": round(mean(vals), 1),
        "median": round(median(vals), 1),
        "p25": _percentile(vals, 0.25),
        "p75": _percentile(vals, 0.75),
        "min": round(min(vals), 1),
        "max": round(max(vals), 1),
    }


def _histogram(values: Sequence[float], bins: int = 12) -> dict:
    vals = [v for v in values if v is not None]
    if not vals:
        return {"labels": [], "counts": []}
    lo, hi = min(vals), max(vals)
    if lo == hi:
        return {"labels": [f"{lo:.0f}"], "counts": [len(vals)]}
    width = (hi - lo) / bins
    counts = [0] * bins
    for v in vals:
        i = min(int((v - lo) / width), bins - 1)
        counts[i] += 1
    labels = [f"{lo + i * width:.0f}" for i in range(bins)]
    return {"labels": labels, "counts": counts}


# --- 1. Champion-Breakdown --------------------------------------------------
def champion_breakdown(rows: list[Any]) -> list[dict]:
    agg: dict[str, dict] = {}
    for r in rows:
        c = r["champion"] or "?"
        a = agg.setdefault(c, dict(games=0, wins=0, k=0, d=0, a=0, dur=0))
        a["games"] += 1
        a["wins"] += r["win"]
        a["k"] += r["kills"]
        a["d"] += r["deaths"]
        a["a"] += r["assists"]
        a["dur"] += r["game_duration"] or 0
    out = []
    for champ, a in agg.items():
        out.append({
            "champion": champ,
            "games": a["games"],
            "wins": a["wins"],
            "losses": a["games"] - a["wins"],
            "winrate": _pct(a["wins"], a["games"]),
            "kda": _kda(a["k"], a["d"], a["a"]),
            "kills": round(a["k"] / a["games"], 1),
            "deaths": round(a["d"] / a["games"], 1),
            "assists": round(a["a"] / a["games"], 1),
            "avg_duration_min": round(a["dur"] / a["games"] / 60, 1) if a["games"] else 0,
        })
    out.sort(key=lambda x: (-x["games"], -x["winrate"]))
    return out


# --- 2. Long-Tail -----------------------------------------------------------
def long_tail(rows: list[Any], top_n: int = config.TOP_CHAMP_COUNT) -> dict:
    breakdown = champion_breakdown(rows)
    top = breakdown[:top_n]
    rest = breakdown[top_n:]

    def group(items):
        games = sum(i["games"] for i in items)
        wins = sum(i["wins"] for i in items)
        return {
            "games": games,
            "wins": wins,
            "losses": games - wins,
            "winrate": _pct(wins, games),
            "champs": [i["champion"] for i in items],
        }

    g_top = group(top)
    g_rest = group(rest)

    # LP-Schaetzung (klar als Naeherung markiert):
    lp = config.LP_PER_NET_WIN
    rest_net = g_rest["wins"] - g_rest["losses"]
    rest_net_lp = round(rest_net * lp)
    # Kontrafaktisch: dieselben Off-Champ-Games mit der Top-5-Winrate gespielt.
    top_wr = g_top["winrate"] / 100.0
    exp_wins = top_wr * g_rest["games"]
    exp_net = 2 * exp_wins - g_rest["games"]
    exp_net_lp = exp_net * lp
    lp_left_on_table = round(exp_net_lp - rest_net_lp)

    return {
        "top": g_top,
        "rest": g_rest,
        "rest_net_lp": rest_net_lp,               # tatsaechliche Netto-LP der Off-Champs
        "lp_left_on_table": lp_left_on_table,     # entgangene LP ggü. Top-5-Niveau
        "lp_per_net_win": lp,
    }


# --- 3. Rollen-Split --------------------------------------------------------
def role_split(rows: list[Any]) -> dict:
    non_af: dict[str, dict] = {}
    af_games = af_wins = 0
    for r in rows:
        if r["autofill"]:
            af_games += 1
            af_wins += r["win"]
            continue
        pos = r["team_position"] or ""
        a = non_af.setdefault(pos, dict(games=0, wins=0))
        a["games"] += 1
        a["wins"] += r["win"]
    roles = []
    for pos, a in non_af.items():
        roles.append({
            "position": _label_pos(pos),
            "games": a["games"],
            "wins": a["wins"],
            "losses": a["games"] - a["wins"],
            "winrate": _pct(a["wins"], a["games"]),
        })
    roles.sort(key=lambda x: -x["games"])
    return {
        "roles": roles,
        "autofill": {
            "games": af_games,
            "wins": af_wins,
            "losses": af_games - af_wins,
            "winrate": _pct(af_wins, af_games),
        },
    }


# --- 4. Laning --------------------------------------------------------------
def laning(laning_rows: list[Any]) -> dict:
    def col(name):
        return [r[name] for r in laning_rows if r[name] is not None]
    return {
        "cs10": {"dist": _distribution(col("cs10")), "hist": _histogram(col("cs10"))},
        "cs14": {"dist": _distribution(col("cs14")), "hist": _histogram(col("cs14"))},
        "gold_diff_10": {"dist": _distribution(col("gold_diff_10")),
                          "hist": _histogram(col("gold_diff_10"))},
        "xp_diff_10": {"dist": _distribution(col("xp_diff_10")),
                        "hist": _histogram(col("xp_diff_10"))},
    }


# --- 5. Tilt / Sessions -----------------------------------------------------
def sessions(rows: list[Any], gap_hours: float = config.SESSION_GAP_HOURS) -> dict:
    """Rows muessen chronologisch aufsteigend sein (game_creation)."""
    gap_ms = gap_hours * 3600 * 1000
    by_pos: dict[str, dict] = {}   # "1","2","3","4+"
    after_loss_games = after_loss_wins = 0

    last_creation = None
    pos_in_session = 0
    prev_win = None
    for r in rows:
        gc = r["game_creation"] or 0
        if last_creation is None or (gc - last_creation) > gap_ms:
            pos_in_session = 1
        else:
            pos_in_session += 1
        last_creation = gc

        key = str(pos_in_session) if pos_in_session < 4 else "4+"
        a = by_pos.setdefault(key, dict(games=0, wins=0))
        a["games"] += 1
        a["wins"] += r["win"]

        # Winrate direkt nach einer Niederlage (nur innerhalb derselben Session).
        if prev_win == 0 and pos_in_session > 1:
            after_loss_games += 1
            after_loss_wins += r["win"]
        prev_win = r["win"]

    order = ["1", "2", "3", "4+"]
    position_stats = []
    for k in order:
        if k in by_pos:
            a = by_pos[k]
            position_stats.append({
                "position": f"Game {k}",
                "games": a["games"],
                "wins": a["wins"],
                "winrate": _pct(a["wins"], a["games"]),
            })
    return {
        "by_position": position_stats,
        "after_loss": {
            "games": after_loss_games,
            "wins": after_loss_wins,
            "winrate": _pct(after_loss_wins, after_loss_games),
        },
    }


# --- 6. Death-Analyse -------------------------------------------------------
def deaths(rows: list[Any]) -> dict:
    total_deaths = 0
    total_minutes = 0.0
    phase_counts = {name: 0 for name, _, _ in config.GAME_PHASES}
    timeline_deaths = 0
    for r in rows:
        total_deaths += r["deaths"]
        total_minutes += (r["game_duration"] or 0) / 60.0
        times = json.loads(r["death_times_json"] or "[]")
        for t in times:
            minute = t / 60000.0
            timeline_deaths += 1
            for name, lo, hi in config.GAME_PHASES:
                if lo <= minute < hi:
                    phase_counts[name] += 1
                    break
    return {
        "deaths_per_min": round(total_deaths / total_minutes, 2) if total_minutes else 0,
        "avg_deaths": round(total_deaths / len(rows), 1) if rows else 0,
        "total_deaths": total_deaths,
        "phase_labels": list(phase_counts.keys()),
        "phase_counts": list(phase_counts.values()),
        "timeline_deaths": timeline_deaths,
    }


# --- 7. Trend ---------------------------------------------------------------
def rolling_winrate(rows: list[Any], window: int = config.ROLLING_WINDOW) -> dict:
    wins = [r["win"] for r in rows]
    points = []
    for i in range(len(wins)):
        if i + 1 < window:
            continue
        w = wins[i - window + 1:i + 1]
        points.append(round(100.0 * sum(w) / window, 1))
    x = list(range(window, window + len(points)))
    return {"window": window, "x": x, "y": points}


# --- Gesamt-Bilanz ----------------------------------------------------------
def overall(rows: list[Any]) -> dict:
    games = len(rows)
    wins = sum(r["win"] for r in rows)
    return {
        "games": games,
        "wins": wins,
        "losses": games - wins,
        "winrate": _pct(wins, games),
    }


def run_all(player_rows: list[Any], laning_rows: list[Any]) -> dict:
    results = {
        "overall": overall(player_rows),
        "champions": champion_breakdown(player_rows),
        "long_tail": long_tail(player_rows),
        "roles": role_split(player_rows),
        "laning": laning(laning_rows),
        "sessions": sessions(player_rows),
        "deaths": deaths(player_rows),
        "trend": rolling_winrate(player_rows),
    }
    results["problems"] = top_problems(results)
    return results


# --- Priorisierte Baustellen (LP-Impact-Schaetzung) -------------------------
def top_problems(results: dict, limit: int = 3) -> list[dict]:
    """Kandidaten-Baustellen mit geschaetztem LP-Impact, absteigend sortiert.

    Der LP-Impact ist eine grobe Naeherung (~20 LP je Netto-Sieg) und dient
    nur der Priorisierung, nicht als exakte Vorhersage.
    """
    lp = config.LP_PER_NET_WIN
    problems: list[dict] = []

    # 1) Off-Champ-Drag
    lt = results["long_tail"]
    if lt["rest"]["games"] >= 5 and lt["lp_left_on_table"] > 0:
        problems.append({
            "key": "offchamps",
            "title": "Off-Champs ziehen dich runter",
            "detail": (
                f"Top-5-Champs: {lt['top']['winrate']}% WR ueber {lt['top']['games']} Games, "
                f"Rest: {lt['rest']['winrate']}% ueber {lt['rest']['games']} Games."
            ),
            "advice": "Champ-Pool auf die Top-5 verengen; Off-Picks nur bei klarem Vorteil.",
            "lp_impact": lt["lp_left_on_table"],
        })

    # 2) Tilt / Verlustserien
    al = results["sessions"]["after_loss"]
    base_wr = results["overall"]["winrate"]
    if al["games"] >= 5:
        wr_gap = base_wr - al["winrate"]  # Prozentpunkte schlechter nach Loss
        if wr_gap > 0:
            lost_net = (wr_gap / 100.0) * al["games"] * 2  # entgangene Netto-Siege
            problems.append({
                "key": "tilt",
                "title": "Du gibst LP in Verlustserien zurueck",
                "detail": (
                    f"Nach einer Niederlage nur {al['winrate']}% WR "
                    f"({al['games']} Games) vs. {base_wr}% gesamt."
                ),
                "advice": "Nach 2 Losses in Folge Pause. Loss-Streaks kosten am meisten LP.",
                "lp_impact": round(lost_net * lp),
            })

    # 3) Schwaches Laning (Gold-Diff@10 negativ)
    gd = results["laning"]["gold_diff_10"]["dist"]
    if gd.get("count", 0) >= 5 and gd.get("mean", 0) < 0:
        # Grobe Kopplung: deutlicher Gold-Rueckstand @10 korreliert mit Loss.
        est_games = results["overall"]["games"]
        impact = round(abs(gd["mean"]) / 500.0 * est_games * 0.5 * lp)
        problems.append({
            "key": "laning",
            "title": "Laning-Phase: du liegst @10 hinten",
            "detail": (
                f"Gold-Diff@10 im Schnitt {gd['mean']:+.0f} "
                f"(Median {gd['median']:+.0f}), CS@10 "
                f"{results['laning']['cs10']['dist'].get('mean', 0)}."
            ),
            "advice": "Wave-Management & Trading-Pattern reviewen; sauberes CS@10-Ziel setzen.",
            "lp_impact": impact,
        })

    # 4) Autofill-Verlust
    af = results["roles"]["autofill"]
    if af["games"] >= 5 and af["winrate"] < base_wr:
        wr_gap = base_wr - af["winrate"]
        lost_net = (wr_gap / 100.0) * af["games"] * 2
        problems.append({
            "key": "autofill",
            "title": "Autofill-Games kosten LP",
            "detail": f"Autofill: {af['winrate']}% WR ueber {af['games']} Games vs. {base_wr}% gesamt.",
            "advice": "Autofill-Rolle gezielt als Zweit-Main lernen oder dodgen wenn moeglich.",
            "lp_impact": round(lost_net * lp),
        })

    # 5) Frueh sterben
    d = results["deaths"]
    games = results["overall"]["games"]
    if d.get("timeline_deaths", 0) >= 10 and games:
        early = d["phase_counts"][0]
        share = early / d["timeline_deaths"]
        # Anteil ueber "gesundem" Early-Niveau (~40%), game-normalisiert in
        # Netto-Sieg-Aequivalente umgerechnet -> vergleichbar mit den anderen.
        excess = max(0.0, share - 0.40)
        if excess > 0.05:
            problems.append({
                "key": "early_deaths",
                "title": "Zu viele fruehe Tode",
                "detail": f"{round(share * 100)}% deiner Tode fallen in die Early-Phase (0-14 min).",
                "advice": "Frueh weniger greedy positionieren; Deaths vor 14 min direkt LP-negativ.",
                "lp_impact": round(excess * games * 0.25 * lp),
            })

    problems.sort(key=lambda p: -p["lp_impact"])
    return problems[:limit]
