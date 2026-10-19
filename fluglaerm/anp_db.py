"""SQLite-Zugriff auf data/anp.sqlite (EASA-ANP v9, via data/import_anp.py)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fluglaerm.engine.npd import NpdTable

_NPD_DIST_FT = (200, 400, 630, 1000, 2000, 4000, 6300, 10000, 16000, 25000)
_NPD_LEVEL_COLS = ", ".join(f"l_{d}ft" for d in _NPD_DIST_FT)

HI_TEMP = {
    "MaxTakeoff": "MaxTkoffHiTemp",
    "MaxClimb": "MaxClimbHiTemp",
    "IdleApproach": "IdleApproachHiTemp",
}


class AnpDatabase:
    def __init__(self, path: str = "data/anp.sqlite"):
        if not Path(path).exists():
            raise FileNotFoundError(
                f"ANP-Datenbank {path} nicht gefunden; data/import_anp.py ausführen"
            )
        self._path = path
        self._archive: AnpDatabase | None = None

    @classmethod
    def with_archive(
        cls, path: str = "data/anp.sqlite",
        archive_path: str = "data/anp_archive.sqlite",
    ) -> "AnpDatabase":
        """ANP-DB mit optionalem v2.3-Archiv (Proxies für die Ersatztabelle)."""
        self = cls(path)
        if Path(archive_path).exists():
            self._archive = cls(archive_path)
        return self

    def source_for(self, acft_id: str) -> "AnpDatabase | None":
        """Primär-DB (v9) oder Archiv — None wenn beides den Typ nicht führt."""
        if self.aircraft(acft_id) is not None:
            return self
        if self._archive is not None and self._archive.aircraft(acft_id) is not None:
            return self._archive
        return None

    def substitutions(self, icao_code: str) -> list[tuple[str, float, float]]:
        """Ersatztypen für einen ICAO-Typecode: (acft_id, Δdep dB, Δapp dB),
        nur Proxies, die in v9 oder im Archiv existieren; ohne Tabelle []."""
        try:
            with self._connect() as con:
                rows = con.execute(
                    "SELECT acft_id, delta_dep_db, delta_app_db FROM substitutions"
                    " WHERE icao_code = ? ORDER BY acft_id",
                    (icao_code,),
                ).fetchall()
        except sqlite3.OperationalError:
            return []
        return [
            (r[0], float(r[1] or 0.0), float(r[2] or 0.0))
            for r in rows
            if self.source_for(r[0]) is not None
        ]

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(f"file:{self._path}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        return con

    def aircraft(self, acft_id: str) -> dict | None:
        with self._connect() as con:
            row = con.execute(
                "SELECT * FROM aircraft WHERE acft_id = ?", (acft_id,)
            ).fetchone()
        return dict(row) if row is not None else None

    def engine_coefficients(
        self, acft_id: str, rating: str
    ) -> tuple[dict | None, dict | None]:
        """(low_row, hi_row); nur B-1/B-23 (k1..k4 sind in ANP v9 überall NULL)."""
        with self._connect() as con:
            low = con.execute(
                "SELECT e, f, ga, gb, h FROM jet_engine_coefficients"
                " WHERE acft_id = ? AND thrust_rating = ?",
                (acft_id, rating),
            ).fetchone()
            hi = None
            if rating in HI_TEMP:
                hi = con.execute(
                    "SELECT e, f, ga, gb, h FROM jet_engine_coefficients"
                    " WHERE acft_id = ? AND thrust_rating = ?",
                    (acft_id, HI_TEMP[rating]),
                ).fetchone()
        return (
            dict(low) if low is not None else None,
            dict(hi) if hi is not None else None,
        )

    def cutback_altitude_ft(self, acft_id: str) -> float:
        with self._connect() as con:
            row = con.execute(
                "SELECT MAX(end_point_altitude_ft) FROM default_departure_procedural_steps"
                " WHERE acft_id = ? AND thrust_rating = 'MaxTakeoff' AND step_type = 'Climb'",
                (acft_id,),
            ).fetchone()
        return float(row[0]) if row is not None and row[0] is not None else 1500.0

    def npd_table(
        self,
        npd_id: str,
        metric: str,
        op_mode: str,
        engine_mount: str,
        max_thrust_lbf: float,
    ) -> NpdTable | None:
        with self._connect() as con:
            rows = con.execute(
                f"SELECT power_setting, {_NPD_LEVEL_COLS} FROM npd_data"
                " WHERE npd_id = ? AND noise_metric = ? AND op_mode = ?"
                " ORDER BY power_setting",
                (npd_id, metric, op_mode),
            ).fetchall()
        if not rows:
            return None
        grid = [[float(v) for v in r[1:]] for r in rows]
        empty = [[0.0] * len(_NPD_DIST_FT) for _ in rows]
        le, lmax = (grid, empty) if metric == "SEL" else (empty, grid)
        return NpdTable(
            aircraft=npd_id,
            source="EASA-ANP v9 (data/anp.sqlite)",
            engine_mount=engine_mount,
            max_thrust_lbf=max_thrust_lbf,
            ref_speed_kn=160.0,
            powers_lbf=[float(r[0]) for r in rows],
            distances_m=[d * 0.3048 for d in _NPD_DIST_FT],
            le=le,
            lmax=lmax,
        )
