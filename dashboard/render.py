"""Jinja2 -> statisches HTML-Dashboard.

Chart.js wird einmalig lokal nach output/vendor/ gelegt, damit das Dashboard
komplett offline funktioniert (kein Server, kein CDN noetig).
"""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import config

CHARTJS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"
CHARTJS_FILE = "chart.umd.min.js"


def ensure_chartjs(verbose: bool = True) -> bool:
    """Laedt Chart.js einmalig in output/vendor/. Gibt True bei Erfolg/vorhanden."""
    config.VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    target = config.VENDOR_DIR / CHARTJS_FILE
    if target.exists() and target.stat().st_size > 10000:
        return True
    try:
        import requests
        if verbose:
            print("  Lade Chart.js (einmalig) nach output/vendor/ ...", flush=True)
        resp = requests.get(CHARTJS_URL, timeout=30)
        resp.raise_for_status()
        target.write_bytes(resp.content)
        return True
    except Exception as exc:  # noqa: BLE001
        if verbose:
            print(f"  WARN: Chart.js konnte nicht geladen werden ({exc}). "
                  "Charts werden erst nach erneutem Online-Lauf angezeigt.", flush=True)
        return False


def render_dashboard(results: dict, rank: dict, meta: dict) -> Path:
    ensure_chartjs(verbose=meta.get("verbose", True))

    env = Environment(
        loader=FileSystemLoader(str(config.TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["tojson"] = lambda v: json.dumps(v)
    template = env.get_template("dashboard.html.j2")

    html = template.render(
        results=results,
        rank=rank,
        meta=meta,
        chartjs_path=f"vendor/{CHARTJS_FILE}",
    )
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.DASHBOARD_HTML.write_text(html, encoding="utf-8")
    return config.DASHBOARD_HTML
