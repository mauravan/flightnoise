"""OpenSky-Network-Client (https://opensky-network.org).

- bbox_states: GET /states/all — anonymer Live-Zugriff, rate-limited.
- flights_in_window: GET /flights/all — History, kostenloses Forschungskonto nötig.
"""

from __future__ import annotations

import requests

BASE = "https://opensky-network.org/api"


class OpenSkyClient:
    def __init__(self, username: str | None = None, password: str | None = None):
        self.auth = (username, password) if username and password else None

    def bbox_states(
        self, lamin: float, lomin: float, lamax: float, lomax: float
    ) -> list[dict]:
        """Live-Zustände in Bounding-Box (anonym möglich, rate-limited)."""
        resp = requests.get(
            f"{BASE}/states/all",
            params={"lamin": lamin, "lomin": lomin, "lamax": lamax, "lomax": lomax},
            auth=self.auth,
            timeout=30,
        )
        resp.raise_for_status()
        states = (resp.json().get("states") or [])
        keys = [
            "icao24", "callsign", "origin_country", "time_position", "last_contact",
            "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
            "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
            "spi", "position_source",
        ]
        return [dict(zip(keys, s)) for s in states]

    def flights_in_window(self, begin_ts: int, end_ts: int) -> list[dict]:
        """History-Flüge im Zeitfenster (Konto nötig)."""
        resp = requests.get(
            f"{BASE}/flights/all",
            params={"begin": begin_ts, "end": end_ts},
            auth=self.auth,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json() or []
