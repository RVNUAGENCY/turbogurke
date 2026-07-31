"""SQLite-Persistenz mit Raw-JSON-Cache.

Design-Entscheidung: Wir speichern das komplette Match- und Timeline-JSON als
Blob. Damit lassen sich alle abgeleiteten Tabellen jederzeit neu berechnen,
ohne die Riot-API erneut zu belasten - wichtig, wenn die Analyse-Logik spaeter
erweitert wird. Die abgeleiteten Tabellen (player_match, laning) dienen der
schnellen Auswertung.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS matches (
    match_id      TEXT PRIMARY KEY,
    queue_id      INTEGER,
    game_creation INTEGER,   -- ms
    game_duration INTEGER,   -- s
    game_version  TEXT,
    match_json    TEXT,
    timeline_json TEXT,
    fetched_at    INTEGER
);

CREATE TABLE IF NOT EXISTS player_match (
    match_id            TEXT PRIMARY KEY,
    game_creation       INTEGER,
    game_duration       INTEGER,
    champion            TEXT,
    team_position       TEXT,
    individual_position TEXT,
    autofill            INTEGER,   -- 0/1
    win                 INTEGER,   -- 0/1
    kills               INTEGER,
    deaths              INTEGER,
    assists             INTEGER,
    cs                  INTEGER,
    gold                INTEGER,
    dmg                 INTEGER,
    death_times_json    TEXT,      -- Liste von Death-Timestamps (ms)
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

CREATE TABLE IF NOT EXISTS laning (
    match_id     TEXT PRIMARY KEY,
    cs10         REAL,
    cs14         REAL,
    gold_diff_10 REAL,
    xp_diff_10   REAL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

CREATE INDEX IF NOT EXISTS idx_pm_creation ON player_match(game_creation);
"""


class Storage:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # -- meta ----------------------------------------------------------------
    def get_meta(self, key: str) -> str | None:
        row = self.conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self.conn.commit()

    # -- matches -------------------------------------------------------------
    def known_match_ids(self) -> set[str]:
        rows = self.conn.execute("SELECT match_id FROM matches").fetchall()
        return {r["match_id"] for r in rows}

    def has_match(self, match_id: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM matches WHERE match_id = ?", (match_id,)
        ).fetchone() is not None

    def store_raw(self, match_id: str, match_json: dict, timeline_json: dict) -> None:
        info = match_json.get("info", {})
        self.conn.execute(
            "INSERT OR REPLACE INTO matches "
            "(match_id, queue_id, game_creation, game_duration, game_version, "
            " match_json, timeline_json, fetched_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                match_id,
                info.get("queueId"),
                info.get("gameCreation"),
                info.get("gameDuration"),
                info.get("gameVersion"),
                json.dumps(match_json, separators=(",", ":")),
                json.dumps(timeline_json, separators=(",", ":")),
                int(time.time()),
            ),
        )
        self.conn.commit()

    def iter_raw_matches(self) -> Iterable[tuple[str, dict, dict]]:
        cur = self.conn.execute(
            "SELECT match_id, match_json, timeline_json FROM matches"
        )
        for row in cur:
            yield (
                row["match_id"],
                json.loads(row["match_json"]),
                json.loads(row["timeline_json"]) if row["timeline_json"] else {},
            )

    # -- abgeleitete Tabellen ------------------------------------------------
    def upsert_player_match(self, rec: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO player_match "
            "(match_id, game_creation, game_duration, champion, team_position, "
            " individual_position, autofill, win, kills, deaths, assists, cs, "
            " gold, dmg, death_times_json) "
            "VALUES (:match_id,:game_creation,:game_duration,:champion,:team_position,"
            " :individual_position,:autofill,:win,:kills,:deaths,:assists,:cs,"
            " :gold,:dmg,:death_times_json)",
            rec,
        )
        self.conn.commit()

    def upsert_laning(self, rec: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO laning "
            "(match_id, cs10, cs14, gold_diff_10, xp_diff_10) "
            "VALUES (:match_id,:cs10,:cs14,:gold_diff_10,:xp_diff_10)",
            rec,
        )
        self.conn.commit()

    def player_matches(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM player_match ORDER BY game_creation ASC"
        ).fetchall()

    def laning_rows(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM laning").fetchall()

    def match_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) AS c FROM matches").fetchone()["c"]
