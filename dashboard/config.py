"""Zentrale Konfiguration: Riot-Routen, Queue-IDs, Pfade, LP-Modell.

Alles was man beim Erweitern anfassen will, liegt hier gebuendelt.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Account / Region -------------------------------------------------------
# Riot ID getrennt in Name + Tag (TURBOGURKE#TTV).
RIOT_ID_NAME = os.environ.get("RIOT_ID_NAME", "TURBOGURKE")
RIOT_ID_TAG = os.environ.get("RIOT_ID_TAG", "TTV")

# Platform-Route (Summoner/League) vs. Regional-Route (Account/Match).
PLATFORM = os.environ.get("RIOT_PLATFORM", "euw1")     # LEAGUE-V4, SUMMONER-V4
REGIONAL = os.environ.get("RIOT_REGIONAL", "europe")   # ACCOUNT-V1, MATCH-V5

# --- Queues -----------------------------------------------------------------
QUEUE_RANKED_SOLO = 420   # Ranked Solo/Duo -> darum geht es hier ausschliesslich

# --- Pfade ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("LOL_DB_PATH", BASE_DIR / "lol_stats.sqlite"))
OUTPUT_DIR = BASE_DIR / "output"
VENDOR_DIR = OUTPUT_DIR / "vendor"
DASHBOARD_HTML = OUTPUT_DIR / "dashboard.html"
TEMPLATE_DIR = BASE_DIR / "templates"

# --- Rate-Limits (Dev-Key) --------------------------------------------------
# 20 req/s und 100 req/2min. Wir bleiben bewusst leicht drunter.
RATE_LIMITS = [
    (20, 1.0),      # 20 Requests pro 1 Sekunde
    (100, 120.0),   # 100 Requests pro 120 Sekunden
]

# --- LP-Modell (Schaetzung!) ------------------------------------------------
# Nahe 50% Winrate liegt der Netto-Gewinn/Verlust bei ~20 LP pro Spiel.
# Diese Zahlen sind Naeherungen, im Dashboard klar als Schaetzung markiert.
AVG_LP_GAIN = 21
AVG_LP_LOSS = 19
LP_PER_NET_WIN = (AVG_LP_GAIN + AVG_LP_LOSS) / 2  # ~20 LP je Netto-Sieg

# --- Analyse-Parameter ------------------------------------------------------
TOP_CHAMP_COUNT = 5            # Long-Tail-Grenze: Top-N-Champs
SESSION_GAP_HOURS = 2.0       # Luecke > 2h -> neue Session
ROLLING_WINDOW = 20           # rollierende Winrate-Fenstergroesse
# Spielphasen fuer die Death-Analyse (Minuten).
GAME_PHASES = [
    ("Early (0-14)", 0, 14),
    ("Mid (14-25)", 14, 25),
    ("Late (25+)", 25, 9999),
]
