"""Gemeinsame Typen: Empfänger, Perioden, Routen, Bewegungsdatensatz."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Receiver:
    east: float  # LV95 E, EPSG:2056
    north: float  # LV95 N
    es: int  # 1..4
    nutzung: Literal["wohnen", "betrieb"]
    height_m: float = 0.0  # Empfängerhöhe über Flughafen-Grund (Referenz der Segment-alt_m)


@dataclass
class Period:
    id: str  # "tag" | "nacht1" | "nacht2" | "letzte_nacht"
    start_hour: int
    end_hour: int


@dataclass
class Segment:
    east: float
    north: float
    alt_m: float
    thrust: float | None  # None => Standardprofil je Phase


@dataclass
class Route:
    id: str
    kind: Literal["departure", "arrival"]
    runway: str  # "14" | "16" | "28" | "34"
    segments: list[Segment]  # Ground-Track mit Höhen-/Thrust-Verlauf
    share: float  # 0..1, Anteil der Bewegungen auf dieser Route


@dataclass
class Movement:
    route_id: str
    aircraft_anp: str  # ANP-Identifier (Bsp. "A320-214")
    period: str  # Period.id
    count: int
    weight_class: Literal["gross", "klein"]  # >8'618 kg / <=8'618 kg


@dataclass
class MovementDataset:
    airport_icao: str
    airport_east: float
    airport_north: float
    periods: list[Period] = field(default_factory=list)
    routes: list[Route] = field(default_factory=list)
    movements: list[Movement] = field(default_factory=list)
