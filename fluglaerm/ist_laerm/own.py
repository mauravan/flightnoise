"""Ist-Pegel aus eigenen Empfänger-States gegen die EASA-ANP-DB.

Kette: OpenSky-State → data/aircraft_registry.json → aircraft/engine
→ Doc-29 B-1/B-23 CNT → NPD-Interpolation → ΔI/Λ/ΔV.

Hex ohne Registry-Treffer: Tar1090-Typecode → EASA-Ersatztabelle
(substitutions in data/anp.sqlite) → ANP_PROXY + Δdep/Δapp dB, Proxy aus v9
oder ANP-Archiv v2.3 (data/anp_archive.sqlite).

Näherungen: ISA-Temperatur, Ground Speed ≡ TAS, kein Wind, SEL als
unendlicher Pfad ohne ΔF, keine atmosphärische Re-Normierung (Doc 29 App. D).

Registry-Format: {"<icao24 lowercase hex>": "<ANP acft_id>"},
z.B. {"3c6444": "A320-250N"}.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from fluglaerm.anp_db import AnpDatabase
from fluglaerm.common.geo import lateral_offset_m, slant_m
from fluglaerm.common.types import Receiver
from fluglaerm.engine import acoustic as ac
from fluglaerm.engine.anhang5 import grenzwert_status
from fluglaerm.engine.npd import (
    duration_correction,
    installation_correction,
    interp_npd,
    lateral_attenuation,
)
from fluglaerm.ist_laerm.track import Track

logger = logging.getLogger(__name__)

ARP_ALT_M = 432.0  # LSZH ARP-Höhe (AIP), m ü. M. — Bodenebene für AFE/Slant
CLIMB_VR_MS = 0.5  # Vertikalrate-Schwelle climb/descent (m/s)
LEVEL_SPLIT_FT = 6000.0  # Level-Flug ≤ 6000 ft AFE → Approach (idle), sonst MaxClimb
MAX_PROC_ALT_FT = 10000.0  # ANP-Prozeduren (dep/arr) enden bei 10 000 ft AFE; darüber D/MaxClimb-Schätzung (estimate=True)
FT_PER_M = 1.0 / 0.3048
KLEIN_MTOM_LB = 19000.0  # LSV Anhang 5: Kleinluftfahrzeug ≤ 8618 kg MTOM
TAG_S = 16 * 3600  # 57600 — Tag 06–22 (Grossflugzeuge)
KLEIN_TAG_S = 14 * 3600  # 50400 — Kleinflugzeuge nur 06–20
NACHT_S = 3600  # je Nachtstunde
OWN_LABEL = (
    "Ist-Beobachtung über das Abfragefenster, kein Jahresmittel; "
    "nicht rechtsgültig (massgebend: Berechnungsmodell BAZL/FLULA2 "
    "mit genehmigtem Datensatz)"
)


def lsv_weight_class(mtom_lb: float | None) -> str:
    """'klein' wenn MTOM ≤ 8618 kg (19 000 lb), sonst 'gross'; None → 'gross'."""
    return "klein" if (mtom_lb is not None and mtom_lb <= KLEIN_MTOM_LB) else "gross"


def local_hour(ts: int) -> int:
    """Stunde in Europe/Zurich (DST-fähig via zoneinfo)."""
    return datetime.fromtimestamp(ts, ZoneInfo("Europe/Zurich")).hour


def period_of(ts: int) -> str | None:
    """'tag' | 'nacht1' | 'nacht2' | None (ts ≤ 0 oder 00–06, ZRH geschlossen)."""
    if ts <= 0:
        return None
    h = local_hour(ts)
    if 6 <= h <= 21:
        return "tag"
    if h == 22:
        return "nacht1"
    if h == 23:
        return "nacht2"
    return None  # 00–06 inkl. letzte Nachtstunde 05–06 (LST_NIGHT_CLOSED)



def beurteilung_from_rows(
    rows: list[AircraftLevel], es: int
) -> tuple[float, float, float, dict[str, float], dict[str, str], int, int]:
    """-> (lrt, lrk, lrg, lrn, status, n_klein, n_gross). Fenster-Leq, kein Jahresmittel."""
    gross: dict[str, list[float]] = {"tag": [], "nacht1": [], "nacht2": []}
    klein: list[float] = []
    for r in rows:
        pid = period_of(r.ts)
        if pid is None:
            continue
        if r.weight_class == "klein":
            if pid == "tag" and 6 <= local_hour(r.ts) <= 19:  # Klein nur 06–20
                klein.append(r.sel_db)
        elif pid in gross:
            gross[pid].append(r.sel_db)
    lrg = ac.accumulate_leq(gross["tag"], TAG_S)
    lrk = (
        ac.klein_lrk(ac.accumulate_leq(klein, KLEIN_TAG_S), len(klein))
        if klein else float("-inf")
    )
    lrt = ac.gesamt_lrt(lrk, lrg) if klein else lrg
    lrn = {
        "nacht1": ac.accumulate_leq(gross["nacht1"], NACHT_S),
        "nacht2": ac.accumulate_leq(gross["nacht2"], NACHT_S),
    }
    status = {
        "tag": grenzwert_status(lrt, es, "tag", "lrt"),
        "nacht1": grenzwert_status(lrn["nacht1"], es, "nacht1", "lrn"),
        "nacht2": grenzwert_status(lrn["nacht2"], es, "nacht2", "lrn"),
    }
    return lrt, lrk, lrg, lrn, status, len(klein), sum(len(v) for v in gross.values())

@dataclass
class OwnDetail:
    acft_id: str
    rating: str
    ts: int
    east: float
    north: float
    alt_m: float
    speed_kn: float
    track_deg: float
    vertical_rate_ms: float
    on_ground: bool
    via: str
    sub_typecode: str
    description: str
    engines: int
    wing: str
    npd_id: str
    max_thrust_lbf: float
    cutback_ft: float | None
    alt_msl_ft: float
    alt_afe_ft: float
    op_mode: str
    estimate: bool
    coeff_low: dict
    coeff_hi: dict | None
    vc_kt: float
    temp_c: float
    cnt_lbf: float
    flat_rated: bool
    mount: str
    npd_source: str
    powers_lbf: list[float]
    ref_speed_kn: float
    slant_m: float
    elev_deg: float
    lateral_m: float
    base_lmax_db: float
    base_sel_db: float
    di_db: float
    lam_db: float
    dv_db: float
    delta_db: float
    lmax_db: float
    sel_db: float


@dataclass
class AircraftLevel:
    icao24: str
    callsign: str
    acft_id: str
    description: str
    engines: int
    wing: str
    phase: str  # "departure" | "approach"
    thrust_rating: str
    cnt_lbf: float
    slant_m: float
    lmax_db: float
    sel_db: float
    weight_class: str = "gross"  # "klein" | "gross"
    ts: int = 0  # Sample-Zeitpunkt des ausgewiesenen Werts (Unix, 0 = unbekannt)
    via: str = "registry"  # "registry" | "substitution" (EASA-Ersatztabelle)
    delta_db: float = 0.0  # EASA-Ersatzzuschlag Δ (dB) auf Lmax/SEL; 0 = keiner
    estimate: bool = False  # True: Sample über Prozedur-Abdeckung (10 000 ft AFE), D/MaxClimb-Schätzung
    di_db: float = 0.0        # ΔI Installationskorrektur (installation_correction)
    lam_db: float = 0.0       # Λ laterale Dämpfung (lateral_attenuation)
    dv_db: float = 0.0        # ΔV Dauerkorrektur (duration_correction)
    flat_rated: bool = False  # True wenn HiTemp-Flat-Rating zieht (hi is not None)
    sub_typecode: str = ""    # Original-Typecode bei Ersatz, sonst ""
    detail: OwnDetail | None = None

    @property
    def bemerkungen(self) -> str:
        parts: list[str] = []
        if self.via == "substitution":
            parts.append(f"Ersatz {self.sub_typecode} → {self.acft_id}, Δ {self.delta_db:+.1f} dB")
        if self.flat_rated:
            parts.append("HiTemp")
        if self.estimate:
            parts.append("Schätzung (>10 000 ft AFE)")
        parts.append(f"ΔI {self.di_db:+.1f}, Λ {self.lam_db:.1f}, ΔV {self.dv_db:+.1f}")
        return "; ".join(parts)


def format_own_header() -> str:
    return (f"{'Rufzeichen':>8}  {'ICAO24':<6}  {'Flugzeug':<10}  {'Phase':<9}  "
            f"{'Rating':<13}  {'Schub':>9}  {'Distanz':>8}  {'Lmax':>6}  {'SEL':>6}  "
            f"{'Zeit':<9}  Bemerkungen")


def format_own_row(r: AircraftLevel) -> str:
    stamp = time.strftime("%H:%M:%S", time.gmtime(r.ts)) if r.ts else "--:--:--"
    return (f"{r.callsign or '-':>8}  {r.icao24:<6}  {r.acft_id:<10}  {r.phase:<9}  "
            f"{r.thrust_rating:<13}  {r.cnt_lbf:7.0f} lb  {r.slant_m:6.0f} m  "
            f"{r.lmax_db:5.1f}  {r.sel_db:5.1f}  {stamp}Z  {r.bemerkungen}")


@dataclass
class OwnResult:
    rows: list[AircraftLevel]  # sortiert nach lmax_db absteigend
    unknown: list[str]  # "callsign (icao24)" ohne Registry-Treffer
    substituted: list[str]  # "callsign (icao24): ICAO → Proxy (Δdep …, Δapp …)"
    skipped: list[str]  # "… — Grund"
    level_db: float  # 10·log10(Σ 10^(lmax/10)); -inf wenn leer
    lrt: float = float("-inf")
    lrk: float = float("-inf")
    lrg: float = float("-inf")
    lrn: dict[str, float] = field(default_factory=dict)
    status: dict[str, str] = field(default_factory=dict)
    n_klein: int = 0
    n_gross: int = 0
    label: str = OWN_LABEL


def isa_temp_c(alt_msl_ft: float) -> float:
    return 15.0 - 0.0019812 * alt_msl_ft


def calibrated_airspeed_kt(tas_kt: float, alt_m: float) -> float:
    p = 101325.0 * (1 - 2.25577e-5 * alt_m) ** 5.25588
    t = 288.15 - 0.0065 * alt_m
    sigma = (p / 101325.0) / (t / 288.15)
    return tas_kt * sigma


def corrected_net_thrust(
    low: dict, hi: dict | None, vc_kt: float, alt_msl_ft: float, temp_c: float
) -> float:
    def b1(row: dict) -> float:
        return (
            row["e"]
            + row["f"] * vc_kt
            + row["ga"] * alt_msl_ft
            + row["gb"] * alt_msl_ft**2
            + row["h"] * temp_c
        )

    return min(b1(low), b1(hi)) if hi is not None else b1(low)


def pick_phase(
    vertical_rate_ms: float, alt_afe_ft: float, cutback_ft: float
) -> tuple[str, str]:
    if vertical_rate_ms >= CLIMB_VR_MS:
        return ("D", "MaxTakeoff" if alt_afe_ft <= cutback_ft else "MaxClimb")
    if vertical_rate_ms <= -CLIMB_VR_MS:
        return ("A", "IdleApproach")
    if alt_afe_ft <= LEVEL_SPLIT_FT:
        return ("A", "IdleApproach")
    return ("D", "MaxClimb")


def substitute(
    icao24: str,
    db: AnpDatabase,
    aircraft_db: dict[str, dict[str, str]] | None,
) -> tuple[str, str, float, float] | None:
    """(acft_id, typecode, Δdep, Δapp) für einen Hex ohne Registry-Treffer;
    None wenn der Tar1090-Eintrag fehlt, der Typecode leer ist oder kein
    Ersatztyp in v9/Archiv existiert. Nie geraten."""
    entry = (aircraft_db or {}).get(icao24)
    if not entry:
        return None
    typecode = (entry.get("typecode") or "").strip().upper()
    if not typecode:
        return None
    cands = db.substitutions(typecode)
    if not cands:
        return None
    acft_id, ddep, dapp = min(cands, key=lambda c: (abs(c[1]) + abs(c[2]), c[0]))
    return acft_id, typecode, ddep, dapp


def evaluate_own(
    receiver: Receiver,
    tracks: list[Track],
    db: AnpDatabase,
    registry: dict[str, str],
    arp_alt_m: float = ARP_ALT_M,
    peak: bool = False,
    aircraft_db: dict[str, dict[str, str]] | None = None,
) -> OwnResult:
    rows: list[AircraftLevel] = []
    unknown: list[str] = []
    substituted: list[str] = []
    skipped: list[str] = []
    n_samples = 0
    energy = 0.0
    logger.debug(
        "evaluate_own: %d Tracks, Registry mit %d Einträgen, ARP-Boden %.1f m, "
        "Empfänger E=%.0f N=%.0f h=%.1f m",
        len(tracks), len(registry), arp_alt_m,
        receiver.east, receiver.north, receiver.height_m,
    )
    for track in tracks:
        tag = f"{track.callsign or '-'} ({track.icao24})"
        via: str = "registry"
        sub_typecode = ""
        ddep = dapp = 0.0
        acft_id = registry.get(track.icao24)
        if acft_id is None:
            sub = substitute(track.icao24, db, aircraft_db)
            if sub is None:
                logger.debug("%s: kein Registry-Treffer, kein ANP-Ersatz", tag)
                unknown.append(tag)
                continue
            acft_id, typecode, ddep, dapp = sub
            sub_typecode = typecode
            via = "substitution"
            logger.debug("%s: ANP-Ersatz %s → %s (Δdep %+.1f dB, Δapp %+.1f dB)",
                         tag, typecode, acft_id, ddep, dapp)
            substituted.append(
                f"{tag}: {typecode} → {acft_id} "
                f"(Δdep {ddep:+.1f} dB, Δapp {dapp:+.1f} dB)"
            )
        src = db.source_for(acft_id)
        ac = src.aircraft(acft_id) if src is not None else None
        if ac is None:
            logger.debug("%s: Registry verweist auf %s, nicht in ANP-DB", tag, acft_id)
            unknown.append(tag)
            continue
        if not track.positions:
            logger.debug("%s: Track ohne Positionen", tag)
            skipped.append(f"{tag} — keine Positionen")
            continue
        positions = track.positions if peak else track.positions[-1:]
        best: AircraftLevel | None = None
        last_reason = ""
        for pos in positions:
            logger.debug(
                "%s: %s Sample ts=%d E=%.0f N=%.0f alt=%.1f m v=%.1f kn "
                "trk=%.0f° vr=%+.2f m/s on_ground=%s",
                tag, acft_id, pos.ts, pos.east, pos.north, pos.alt_m, pos.speed_kn,
                pos.track_deg, pos.vertical_rate_ms, pos.on_ground,
            )
            if pos.on_ground:
                last_reason = f"{tag} — Bodenrollen"
                continue
            alt_msl_ft = pos.alt_m * FT_PER_M
            alt_afe_ft = alt_msl_ft - arp_alt_m * FT_PER_M
            if alt_afe_ft <= 0:
                last_reason = f"{tag} — unter Bodenebene"
                continue
            estimate = alt_afe_ft > MAX_PROC_ALT_FT
            cutback: float | None = None
            if estimate:
                op_mode, rating = "D", "MaxClimb"
                delta = ddep
                logger.debug(
                    "%s: alt_msl=%.0f ft alt_afe=%.0f ft über Prozedur-Abdeckung "
                    "-> Überflug-Schätzung op_mode=D rating=MaxClimb",
                    tag, alt_msl_ft, alt_afe_ft,
                )
            else:
                cutback = src.cutback_altitude_ft(acft_id)
                op_mode, rating = pick_phase(pos.vertical_rate_ms, alt_afe_ft, cutback)
                delta = ddep if op_mode == "D" else dapp
                logger.debug(
                    "%s: alt_msl=%.0f ft alt_afe=%.0f ft cutback=%.0f ft vr=%+.2f m/s "
                    "-> op_mode=%s rating=%s",
                    tag, alt_msl_ft, alt_afe_ft, cutback, pos.vertical_rate_ms,
                    op_mode, rating,
                )
            low, hi = src.engine_coefficients(acft_id, rating)
            if low is None:
                last_reason = (
                    f"{tag} — keine Triebwerkskoeffizienten "
                    "(ANP v9: nur 12 der 14 Flugzeuge modelliert)"
                )
                continue
            vc = calibrated_airspeed_kt(pos.speed_kn, pos.alt_m)
            temp = isa_temp_c(alt_msl_ft)
            cnt = corrected_net_thrust(low, hi, vc, alt_msl_ft, temp)
            logger.debug(
                "%s: B-1 low=%s hi=%s VC=%.1f kt (TAS %.1f kn, alt %.0f m) "
                "T_isa=%.1f °C -> CNT=%.0f lbf%s",
                tag, low, hi, vc, pos.speed_kn, pos.alt_m, temp, cnt,
                " (HiTemp-Flap-Rating zieht)" if hi is not None else "",
            )
            mount = "wing" if ac["wing"] == "Wing" else "fuselage"
            thrust = float(ac["max_sea_level_static_thrust_lb"])
            t_d = src.npd_table(ac["npd_id"], "SEL", op_mode, mount, thrust)
            t_l = src.npd_table(ac["npd_id"], "LAmax", op_mode, mount, thrust)
            if t_d is None or t_l is None:
                last_reason = f"{tag} — keine NPD-Kurven"
                continue
            logger.debug(
                "%s: NPD npd_id=%s op_mode=%s mount=%s max_thrust=%.0f lb "
                "SEL-Kurven=%d LAmax-Kurven=%d ref_speed=%.0f kn",
                tag, ac["npd_id"], op_mode, mount, thrust,
                len(t_d.powers_lbf), len(t_l.powers_lbf), t_d.ref_speed_kn,
            )
            slant = max(
                slant_m(
                    pos.east, pos.north, pos.alt_m - arp_alt_m,
                    receiver.east, receiver.north, receiver.height_m,
                ),
                1.0,
            )
            elev_deg = math.degrees(
                math.asin(
                    min(max((pos.alt_m - arp_alt_m) - receiver.height_m, 0.0) / slant, 1.0)
                )
            )
            lat = lateral_offset_m(
                pos.east, pos.north, receiver.east, receiver.north, pos.track_deg
            )
            _, base_lmax = interp_npd(t_l, cnt, slant)
            base_le, _ = interp_npd(t_d, cnt, slant)
            di = installation_correction(elev_deg, mount)
            lam = lateral_attenuation(elev_deg, lat)
            dv = duration_correction(max(pos.speed_kn, 50.0), t_d.ref_speed_kn)
            lmax = base_lmax + di - lam + delta
            sel = base_le + dv + di - lam + delta
            logger.debug(
                "%s: Geometrie slant=%.1f m elev=%+.1f° lat=%.0f m -> base_Lmax=%.2f "
                "base_SEL=%.2f dB | ΔI=%+.2f Λ=%.2f ΔV=%+.2f -> Lmax=%.2f "
                "SEL=%.2f dB",
                tag, slant, elev_deg, lat, base_lmax, base_le, di, lam, dv,
                lmax, sel,
            )
            detail = OwnDetail(
                acft_id=acft_id,
                rating=rating,
                ts=pos.ts,
                east=pos.east,
                north=pos.north,
                alt_m=pos.alt_m,
                speed_kn=pos.speed_kn,
                track_deg=pos.track_deg,
                vertical_rate_ms=pos.vertical_rate_ms,
                on_ground=pos.on_ground,
                via=via,
                sub_typecode=sub_typecode,
                description=ac["description"],
                engines=int(ac["number_of_engines"]),
                wing=ac["wing"],
                npd_id=ac["npd_id"],
                max_thrust_lbf=float(ac["max_sea_level_static_thrust_lb"]),
                cutback_ft=cutback,
                alt_msl_ft=alt_msl_ft,
                alt_afe_ft=alt_afe_ft,
                op_mode=op_mode,
                estimate=estimate,
                coeff_low=low,
                coeff_hi=hi,
                vc_kt=vc,
                temp_c=temp,
                cnt_lbf=cnt,
                flat_rated=(hi is not None),
                mount=mount,
                npd_source=t_l.source,
                powers_lbf=list(t_l.powers_lbf),
                ref_speed_kn=t_l.ref_speed_kn,
                slant_m=slant,
                elev_deg=elev_deg,
                lateral_m=lat,
                base_lmax_db=base_lmax,
                base_sel_db=base_le,
                di_db=di,
                lam_db=lam,
                dv_db=dv,
                delta_db=delta,
                lmax_db=lmax,
                sel_db=sel,
            )
            row = AircraftLevel(
                icao24=track.icao24,
                callsign=track.callsign,
                acft_id=acft_id,
                description=ac["description"],
                engines=int(ac["number_of_engines"]),
                wing=ac["wing"],
                phase="departure" if op_mode == "D" else "approach",
                thrust_rating=rating,
                cnt_lbf=cnt,
                slant_m=slant,
                lmax_db=lmax,
                sel_db=sel,
                weight_class=lsv_weight_class(ac.get("max_gross_takeoff_weight_lb")),
                ts=pos.ts,
                via=via,
                delta_db=delta,
                estimate=estimate,
                di_db=di,
                lam_db=lam,
                dv_db=dv,
                flat_rated=(hi is not None),
                sub_typecode=sub_typecode,
                detail=detail,
            )
            if best is None or lmax > best.lmax_db:
                best = row
            energy += 10 ** (lmax / 10.0)
            n_samples += 1
        if best is None:
            skipped.append(last_reason)
            continue
        rows.append(best)
    rows.sort(key=lambda r: r.lmax_db, reverse=True)
    level = (
        10 * math.log10(energy) if energy > 0.0 else float("-inf")
    )
    logger.debug("%d Samples ausgewertet", n_samples)
    logger.debug(
        "Ergebnis: %d bewertet, %d ersetzt, %d unbekannt, %d übersprungen, "
        "L_jetzt=%.1f dB",
        len(rows), len(substituted), len(unknown), len(skipped), level,
    )
    lrt, lrk, lrg, lrn, status, n_klein, n_gross = beurteilung_from_rows(rows, receiver.es)
    return OwnResult(
        rows=rows, unknown=unknown, substituted=substituted,
        skipped=skipped, level_db=level,
        lrt=lrt, lrk=lrk, lrg=lrg, lrn=lrn, status=status,
        n_klein=n_klein, n_gross=n_gross,
    )
