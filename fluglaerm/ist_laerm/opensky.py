"""OpenSky-Network-Client (https://opensky-network.org).

- bbox_states: GET /states/all — anonymer Live-Zugriff, rate-limited.
- flights_in_window: GET /flights/all — History, kostenloses Forschungskonto nötig.
- own_states: GET /states/own — eigene Empfänger-States, Client-Credentials nötig.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

BASE = "https://opensky-network.org/api"
TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

_STATE_KEYS = [
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source",
]


def _parse_states(states: list) -> list[dict]:
    return [dict(zip(_STATE_KEYS, s)) for s in states]


def load_credentials(path: str) -> tuple[str, str]:
    """Liest {"clientId": …, "clientSecret": …} (oder client_id/client_secret)."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Credentials-Datei {path} nicht lesbar: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Credentials-Datei {path} ist kein valides JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Credentials-Datei {path} muss ein JSON-Objekt sein")
    client_id = data.get("clientId") or data.get("client_id")
    client_secret = data.get("clientSecret") or data.get("client_secret")
    if not client_id or not client_secret:
        raise ValueError(
            f"Credentials-Datei {path} braucht 'clientId' und 'clientSecret'"
        )
    logger.debug("credentials aus %s geladen (client_id=%s)", path, client_id)
    return client_id, client_secret


class TokenManager:
    def __init__(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = ""
        self._expires_at = 0.0

    def get_token(self) -> str:
        if time.time() >= self._expires_at - 30:
            logger.debug("hole neuen OAuth2-Token von %s", TOKEN_URL)
            resp = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data["access_token"]
            self._expires_at = time.time() + float(data.get("expires_in", 1800))
            logger.debug(
                "Token ok (expires_in=%s, gültig bis %+.0fs)",
                data.get("expires_in", 1800), self._expires_at - time.time(),
            )
        else:
            logger.debug("OAuth2-Token wiederverwendet (%.0fs Restgültigkeit)",
                         self._expires_at - time.time())
        return self._token

    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}


class OpenSkyClient:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None, username: str | None = None, password: str | None = None):
        self.auth = (username, password) if username and password else None
        client_id = client_id or os.environ.get("OPENSKY_CLIENT_ID")
        client_secret = client_secret or os.environ.get("OPENSKY_CLIENT_SECRET")
        self.tokens = TokenManager(client_id, client_secret) if client_id and client_secret else None

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
        return _parse_states(resp.json().get("states") or [])

    def own_states(self, serials: list[int] | None = None, time: int | None = None) -> list[dict]:
        """Eigene States (GET /states/own); Client-Credentials nötig."""
        params: dict = {}
        if serials:
            params["serials"] = serials
        if time is not None:
            params["time"] = time
        url = f"{BASE}/states/own"
        query = urlencode(params, doseq=True) if params else ""
        # Vor dem Credentials-Check loggen: mit --debug soll die Ziel-URL auch
        # dann sichtbar sein, wenn der Aufruf gleich an fehlenden Credentials scheitert.
        logger.debug("GET %s%s", url, f"?{query}" if query else "")
        if self.tokens is None:
            raise ValueError("OpenSky-Client-Credentials fehlen (OPENSKY_CLIENT_ID/OPENSKY_CLIENT_SECRET, --client-id/--client-secret oder --credentials)")
        resp = requests.get(
            url,
            params=params or None,
            headers=self.tokens.headers(),
            timeout=30,
        )
        resp.raise_for_status()
        out = _parse_states(resp.json().get("states") or [])
        logger.debug(
            "%s%s -> HTTP %s, %d eigene States (%d bytes)",
            url, f"?{query}" if query else "", resp.status_code, len(out), len(resp.content),
        )
        remaining = resp.headers.get("X-Rate-Limit-Remaining")
        if remaining:
            logger.debug("X-Rate-Limit-Remaining: %s", remaining)
        return out

    def own_history(self, start_ts: int, end_ts: int, step_s: int = 60,
                    serials: list[int] | None = None) -> list[dict]:
        """States von start_ts (inkl.) bis end_ts (exkl.) in step_s-Schritten."""
        if step_s < 1:
            raise ValueError("Intervall muss >= 1 s sein")
        if end_ts <= start_ts:
            raise ValueError("Fensterende muss nach dem Fensterstart liegen")
        logger.debug("Backfill t=%d..%d Schritt %ds", start_ts, end_ts, step_s)
        out: list[dict] = []
        seen: set[tuple[str, int]] = set()
        for t in range(start_ts, end_ts, step_s):
            try:
                states = self.own_states(serials, t)
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 400:
                    logger.debug(
                        "Backfill bei t=%d gestoppt: 400 (Zeit ausserhalb der Abdeckung)", t
                    )
                    break
                raise
            for s in states:
                key = (str(s.get("icao24")), int(s.get("last_contact") or 0))
                if key in seen:
                    continue
                seen.add(key)
                out.append(s)
        logger.debug("Backfill: %d Abfragen, %d unique States",
                     len(range(start_ts, end_ts, step_s)), len(out))
        return out

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
