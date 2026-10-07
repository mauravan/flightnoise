"""Geodäsie-Primitive: LV95<->WGS84, Slant-Distanz, EGRID-Auflösung."""

import math
import sqlite3

import requests
from pyproj import Transformer

_LV95_TO_WGS84 = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
_WGS84_TO_LV95 = Transformer.from_crs("EPSG:4326", "EPSG:2056", always_xy=True)

MADD_DB_PATH = "data/ch.sqlite"
HEIGHT_URL = "https://api3.geo.admin.ch/rest/services/height"


def lv95_to_wgs84(east: float, north: float) -> tuple[float, float]:
    """LV95 E/N -> (lon, lat) WGS84."""
    return _LV95_TO_WGS84.transform(east, north)


def wgs84_to_lv95(lon: float, lat: float) -> tuple[float, float]:
    """(lon, lat) WGS84 -> LV95 (E, N)."""
    return _WGS84_TO_LV95.transform(lon, lat)


def slant_m(
    seg_east: float,
    seg_north: float,
    seg_alt_m: float,
    rec_east: float,
    rec_north: float,
    ground_alt_m: float = 0.0,
) -> float:
    """Schrägdistanz Segmentvertex -> Empfänger (Bodenhöhe = ground_alt_m)."""
    horiz = math.hypot(seg_east - rec_east, seg_north - rec_north)
    vert = max(seg_alt_m - ground_alt_m, 0.0)
    return math.hypot(horiz, vert)


def lateral_offset_m(
    seg_east: float,
    seg_north: float,
    rec_east: float,
    rec_north: float,
    track_azimuth_deg: float,
) -> float:
    """Seitlicher Versatz des Empfängers zur Track-Achse (für Lateral-Dämpfung)."""
    az = math.radians(track_azimuth_deg)
    dx = rec_east - seg_east
    dy = rec_north - seg_north
    # Track-Richtung: (sin az, cos az); Lateral = Kreuzprodukt
    return abs(dx * math.cos(az) - dy * math.sin(az))


def resolve_egrid(egrid: str) -> tuple[float, float]:
    """EGRID -> LV95 (E, N) über das lokale GWR-SQLite data/ch.sqlite.

    EGRID wird normalisiert (Leerzeichen entfernt, gross; fehlendes CH-Präfix
    ergänzt). Liefert die Gebäudekoordinate (GKODE=Ost, GKODN=Nord) des ersten
    Gebäudes (kleinste EGID) auf der Parzelle.
    """
    key = egrid.replace(" ", "").upper()
    if not key.startswith("CH"):
        key = "CH" + key
    try:
        con = sqlite3.connect(f"file:{MADD_DB_PATH}?mode=ro", uri=True)
        row = con.execute(
            "SELECT GKODE, GKODN FROM building "
            "WHERE EGRID = ? AND GKODE IS NOT NULL AND GKODN IS NOT NULL "
            "AND GKODE <> 0 AND GKODN <> 0 ORDER BY EGID LIMIT 1",
            (key,),
        ).fetchone()
        con.close()
    except sqlite3.OperationalError as exc:
        raise ValueError(
            f"GWR-Datenbank fehlt oder ist nicht lesbar ({exc}); lade sie: "
            "curl -C - -o data/ch.sqlite https://public.madd.bfs.admin.ch/data_ch.sqlite"
        ) from exc
    if row is None:
        raise ValueError(
            f"Keine Koordinate für EGRID '{egrid}' in data/ch.sqlite gefunden."
        )
    return float(row[0]), float(row[1])


def resolve_height(east: float, north: float) -> float:
    """Geländehöhe (m ü. M., LHN95) an LV95-Koordinate via geo.admin.ch height service."""
    try:
        resp = requests.get(
            HEIGHT_URL,
            params={"easting": east, "northing": north, "sr": 2056},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return float(data["height"])
    except Exception as exc:
        raise ValueError(
            f"Geländehöhe nicht abrufbar ({exc}); --height direkt angeben."
        ) from exc
