"""Lokaler ADS-B-State-Collector: tar1090-Scrape + SQLite-Historie."""

import logging
import re
import sqlite3
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

FT_M = 0.3048
KN_MS = 0.5144444
FPM_MS = 0.00508

_STATE_COLS = [
    "icao24", "callsign", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "geo_altitude",
    "velocity", "true_track", "vertical_rate", "on_ground",
]

_HEX_RE = re.compile(r"^[0-9a-f]{6}$")


class StateStore:
    def __init__(self, path: str):
        self._path = path

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._path)
        con.row_factory = sqlite3.Row
        return con

    def init_schema(self) -> None:
        with self._connect() as con:
            con.execute(
                """CREATE TABLE IF NOT EXISTS states (
  icao24        TEXT NOT NULL,
  callsign      TEXT,
  time_position INTEGER NOT NULL,
  last_contact  INTEGER,
  longitude     REAL,
  latitude      REAL,
  baro_altitude REAL,
  geo_altitude  REAL,
  velocity      REAL,
  true_track    REAL,
  vertical_rate REAL,
  on_ground     INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (icao24, time_position)
) WITHOUT ROWID"""
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_states_time ON states(time_position)")

    def insert_states(self, rows: list[dict]) -> int:
        with self._connect() as con:
            before = con.total_changes
            con.executemany(
                "INSERT OR IGNORE INTO states "
                "(icao24, callsign, time_position, last_contact, longitude, latitude, "
                "baro_altitude, geo_altitude, velocity, true_track, vertical_rate, on_ground) "
                "VALUES (:icao24, :callsign, :time_position, :last_contact, :longitude, :latitude, "
                ":baro_altitude, :geo_altitude, :velocity, :true_track, :vertical_rate, :on_ground)",
                [
                    {
                        "icao24": r.get("icao24"),
                        "callsign": r.get("callsign"),
                        "time_position": r.get("time_position"),
                        "last_contact": r.get("last_contact"),
                        "longitude": r.get("longitude"),
                        "latitude": r.get("latitude"),
                        "baro_altitude": r.get("baro_altitude"),
                        "geo_altitude": r.get("geo_altitude"),
                        "velocity": r.get("velocity"),
                        "true_track": r.get("true_track"),
                        "vertical_rate": r.get("vertical_rate"),
                        "on_ground": r.get("on_ground") or 0,
                    }
                    for r in rows
                ],
            )
            return con.total_changes - before

    def states_between(self, start: int, end: int) -> list[dict]:
        if not Path(self._path).exists():
            return []
        with self._connect() as con:
            cur = con.execute(
                f"SELECT {', '.join(_STATE_COLS)} FROM states "
                "WHERE time_position >= ? AND time_position < ? "
                "ORDER BY time_position ASC",
                (start, end),
            )
            return [dict(r) for r in cur.fetchall()]


def fetch_aircraft_json(host: str, port: int = 8080, timeout: int = 10) -> dict:
    url = f"http://{host}:{port}/data/aircraft.json"
    logger.debug("GET %s", url)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    logger.debug("%s -> HTTP %d, %d aircraft, now=%s (%d bytes)",
                 url, resp.status_code, len(data.get("aircraft") or []),
                 data.get("now"), len(resp.content))
    return data

def _get_json(host: str, port: int, name: str, timeout: int = 10) -> dict | None:
    url = f"http://{host}:{port}/data/{name}"
    logger.debug("GET %s", url)
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        logger.debug("%s nicht ladbar: %s", url, exc)
        return None


def fetch_receiver_json(host: str, port: int = 8080, timeout: int = 10) -> dict | None:
    return _get_json(host, port, "receiver.json", timeout)


def fetch_history_json(host: str, port: int = 8080, index: int = 0, timeout: int = 10) -> dict | None:
    return _get_json(host, port, f"history_{index}.json", timeout)


def _num(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) else None


def aircraft_to_state(ac: dict, now: int) -> dict | None:
    icao24 = (ac.get("hex") or "").strip().lower()
    if not _HEX_RE.match(icao24):
        return None
    lat = ac.get("lat")
    lon = ac.get("lon")
    if lat is None or lon is None:
        return None
    callsign = (ac.get("flight") or "").strip() or None
    alt_baro = ac.get("alt_baro")
    if isinstance(alt_baro, str) and alt_baro == "ground":
        on_ground = 1
        baro_altitude = None
    elif isinstance(alt_baro, (int, float)):
        on_ground = 0
        baro_altitude = float(alt_baro) * FT_M
    else:
        on_ground = 0
        baro_altitude = None
    geo = _num(ac.get("alt_geom"))
    geo_altitude = geo * FT_M if geo is not None else None
    gs = _num(ac.get("gs"))
    velocity = gs * KN_MS if gs is not None else None
    trk = _num(ac.get("track"))
    true_track = float(trk) if trk is not None else None
    baro_rate = _num(ac.get("baro_rate"))
    geom_rate = _num(ac.get("geom_rate"))
    rate = baro_rate if baro_rate is not None else geom_rate
    vertical_rate = rate * FPM_MS if rate is not None else None
    seen = ac.get("seen")
    last_contact = now - int(seen) if isinstance(seen, (int, float)) else now
    return {
        "icao24": icao24,
        "callsign": callsign,
        "time_position": now,
        "last_contact": last_contact,
        "longitude": float(lon),
        "latitude": float(lat),
        "baro_altitude": baro_altitude,
        "geo_altitude": geo_altitude,
        "velocity": velocity,
        "true_track": true_track,
        "vertical_rate": vertical_rate,
        "on_ground": on_ground,
    }


def collect_once(store: StateStore, host: str, port: int = 8080) -> int:
    data = fetch_aircraft_json(host, port)
    now = int(data.get("now") or time.time())
    raw = data.get("aircraft") or []
    rows = [aircraft_to_state(a, now) for a in raw]
    kept = [r for r in rows if r is not None]
    n = store.insert_states(kept)
    logger.debug("snapshot now=%d: %d aircraft -> %d mit Position, %d neu gespeichert (%d Duplikate übersprungen)",
                 now, len(raw), len(kept), n, len(kept) - n)
    return n

def import_history(store: StateStore, host: str, port: int = 8080) -> tuple[int, int]:
    recv = fetch_receiver_json(host, port)
    count = int((recv or {}).get("history") or 0)
    if count <= 0:
        logger.debug("kein History-Marker (receiver.json 'history') → kein Backfill")
        return (0, 0)
    rows = []
    loaded = 0
    for index in range(count):
        data = fetch_history_json(host, port, index)
        if data is None:
            continue
        now = int(data.get("now") or 0)
        if now <= 0:
            continue
        loaded += 1
        for ac in data.get("aircraft") or []:
            s = aircraft_to_state(ac, now)
            if s is not None:
                rows.append(s)
    n = store.insert_states(rows)
    logger.debug("History-Backfill: %d/%d Snapshots geladen, %d States gespeichert", loaded, count, n)
    return (loaded, n)
