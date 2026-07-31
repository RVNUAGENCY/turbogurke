"""Riot-API-Client mit Rate-Limiter und Backoff.

Nutzt ausschliesslich offizielle Riot-Endpoints. Der API-Key kommt aus der
Umgebungsvariable RIOT_API_KEY und wird niemals geloggt oder gespeichert.
"""

from __future__ import annotations

import os
import time
from collections import deque
from typing import Any

import requests

from . import config


class RiotApiError(RuntimeError):
    """Fehler beim Riot-API-Zugriff (z. B. ungueltiger Key, 5xx nach Retries)."""


class MissingApiKey(RuntimeError):
    """RIOT_API_KEY ist nicht gesetzt."""


class RateLimiter:
    """Gleitende-Fenster-Limiter fuer mehrere (count, seconds)-Limits gleichzeitig.

    Vor jedem Request wird geprueft, ob eines der Fenster voll ist; falls ja,
    wird proaktiv geschlafen, bis wieder Platz ist. So reissen wir das
    Dev-Key-Limit gar nicht erst und vermeiden 429er weitgehend.
    """

    def __init__(self, limits: list[tuple[int, float]]):
        self._limits = limits
        self._hits: list[deque[float]] = [deque() for _ in limits]

    def acquire(self) -> None:
        while True:
            now = time.monotonic()
            wait = 0.0
            for (count, window), hits in zip(self._limits, self._hits):
                while hits and now - hits[0] >= window:
                    hits.popleft()
                if len(hits) >= count:
                    # aeltester Hit muss aus dem Fenster laufen
                    wait = max(wait, window - (now - hits[0]) + 0.01)
            if wait <= 0:
                break
            time.sleep(wait)
        stamp = time.monotonic()
        for hits in self._hits:
            hits.append(stamp)


class RiotClient:
    """Duenner Wrapper um die genutzten Riot-Endpoints."""

    MAX_RETRIES = 5

    def __init__(self, api_key: str | None = None,
                 platform: str = config.PLATFORM,
                 regional: str = config.REGIONAL,
                 verbose: bool = True):
        self.api_key = api_key or os.environ.get("RIOT_API_KEY")
        if not self.api_key:
            raise MissingApiKey(
                "RIOT_API_KEY ist nicht gesetzt. Hol dir einen Key auf "
                "https://developer.riotgames.com und setze:\n"
                "    export RIOT_API_KEY=RGAPI-...."
            )
        self.platform = platform
        self.regional = regional
        self.verbose = verbose
        self._limiter = RateLimiter(config.RATE_LIMITS)
        self._session = requests.Session()
        self._session.headers.update({"X-Riot-Token": self.api_key})

    # -- interner Kern -------------------------------------------------------
    def _get(self, host: str, path: str, params: dict | None = None,
             allow_404: bool = False) -> Any:
        url = f"https://{host}{path}"
        attempt = 0
        while True:
            self._limiter.acquire()
            try:
                resp = self._session.get(url, params=params, timeout=15)
            except requests.RequestException as exc:
                attempt += 1
                if attempt > self.MAX_RETRIES:
                    raise RiotApiError(f"Netzwerkfehler bei {path}: {exc}") from exc
                self._sleep_backoff(attempt, reason=f"Netzwerkfehler ({exc})")
                continue

            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 404 and allow_404:
                return None
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", "2"))
                if self.verbose:
                    print(f"  429 rate-limited -> warte {retry_after:.0f}s", flush=True)
                time.sleep(retry_after + 0.5)
                continue
            if resp.status_code in (500, 502, 503, 504):
                attempt += 1
                if attempt > self.MAX_RETRIES:
                    raise RiotApiError(f"{resp.status_code} bei {path} nach {self.MAX_RETRIES} Versuchen")
                self._sleep_backoff(attempt, reason=f"Server {resp.status_code}")
                continue
            if resp.status_code in (401, 403):
                raise RiotApiError(
                    f"{resp.status_code} - API-Key ungueltig oder abgelaufen. "
                    "Dev-Keys sind nur 24h gueltig; neu generieren auf developer.riotgames.com."
                )
            raise RiotApiError(f"Unerwarteter Status {resp.status_code} bei {path}: {resp.text[:200]}")

    def _sleep_backoff(self, attempt: int, reason: str) -> None:
        delay = min(2 ** attempt, 16)
        if self.verbose:
            print(f"  {reason} -> Backoff {delay}s (Versuch {attempt})", flush=True)
        time.sleep(delay)

    # -- ACCOUNT-V1 ----------------------------------------------------------
    def get_account_by_riot_id(self, name: str, tag: str) -> dict:
        host = f"{self.regional}.api.riotgames.com"
        path = f"/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
        return self._get(host, path)

    # -- SUMMONER-V4 ---------------------------------------------------------
    def get_summoner_by_puuid(self, puuid: str) -> dict | None:
        host = f"{self.platform}.api.riotgames.com"
        path = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return self._get(host, path, allow_404=True)

    # -- LEAGUE-V4 -----------------------------------------------------------
    def get_league_entries_by_puuid(self, puuid: str) -> list[dict]:
        """Aktueller Rank/LP. Zuerst der moderne by-puuid-Endpoint,
        Fallback ueber SummonerId (by-summoner) fuer aeltere Key-Scopes."""
        host = f"{self.platform}.api.riotgames.com"
        data = self._get(host, f"/lol/league/v4/entries/by-puuid/{puuid}", allow_404=True)
        if data:
            return data
        summoner = self.get_summoner_by_puuid(puuid)
        if summoner and summoner.get("id"):
            return self._get(host, f"/lol/league/v4/entries/by-summoner/{summoner['id']}",
                             allow_404=True) or []
        return []

    # -- MATCH-V5 ------------------------------------------------------------
    def get_match_ids(self, puuid: str, start: int = 0, count: int = 100,
                      queue: int | None = config.QUEUE_RANKED_SOLO) -> list[str]:
        host = f"{self.regional}.api.riotgames.com"
        params: dict[str, Any] = {"start": start, "count": count}
        if queue is not None:
            params["queue"] = queue
        return self._get(host, f"/lol/match/v5/matches/by-puuid/{puuid}/ids", params=params)

    def get_match(self, match_id: str) -> dict:
        host = f"{self.regional}.api.riotgames.com"
        return self._get(host, f"/lol/match/v5/matches/{match_id}")

    def get_timeline(self, match_id: str) -> dict:
        host = f"{self.regional}.api.riotgames.com"
        return self._get(host, f"/lol/match/v5/matches/{match_id}/timeline")
