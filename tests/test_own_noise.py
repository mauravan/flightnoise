"""Eigene States gegen ANP-DB: B-1-Math, Phasen, Filter, Pegel (hermetisch)."""

from __future__ import annotations

import math

import requests

from fluglaerm.common.types import Receiver
from fluglaerm.engine.npd import NpdTable
from fluglaerm.ist_laerm.opensky import OpenSkyClient
from fluglaerm.ist_laerm.own import (
    ARP_ALT_M,
    calibrated_airspeed_kt,
    corrected_net_thrust,
    evaluate_own,
    pick_phase,
)
from fluglaerm.ist_laerm.track import Position, Track

IDLE = {"e": 2280, "f": -10.46, "ga": 0.08631, "gb": -7.327e-6, "h": 0}
CLIMB = {"e": 24570, "f": -34.93, "ga": 0.4774, "gb": -6.964e-6, "h": 0}

REC = Receiver(east=2684000.0, north=1256000.0, es=2, nutzung="wohnen", height_m=0.0)


class FakeDb:
    def aircraft(self, acft_id):
        return {
            "acft_id": "A320-250N",
            "description": "Airbus A320-250N",
            "number_of_engines": 2,
            "wing": "Wing",
            "npd_id": "X",
            "max_sea_level_static_thrust_lb": 27120.0,
        }

    def source_for(self, acft_id):
        return self

    def substitutions(self, icao_code):
        return []

    def cutback_altitude_ft(self, acft_id):
        return 1500.0

    def engine_coefficients(self, acft_id, rating):
        if rating == "IdleApproach":
            return IDLE, dict(IDLE, e=1780)
        return CLIMB, None

    def npd_table(self, npd_id, metric, op_mode, mount, thrust):
        kw = dict(
            aircraft="X", source="t", engine_mount="wing",
            max_thrust_lbf=27120, ref_speed_kn=160.0,
            powers_lbf=[10000.0, 20000.0], distances_m=[304.8, 1000.0, 3000.0],
        )
        if metric == "SEL":
            return NpdTable(le=[[90.0, 80.0, 70.0], [95.0, 85.0, 75.0]],
                            lmax=[[0.0] * 3, [0.0] * 3], **kw)
        return NpdTable(le=[[0.0] * 3, [0.0] * 3],
                        lmax=[[85.0, 75.0, 65.0], [90.0, 80.0, 70.0]], **kw)


def _track(icao24="abc", callsign="S1", east=2684000.0, north=1256000.0,
           afe_ft=2000.0, speed_kn=180.0, vr=5.0, ground=False):
    return Track(
        icao24=icao24, callsign=callsign, aircraft_type="X",
        positions=[Position(ts=1, east=east, north=north,
                            alt_m=ARP_ALT_M + afe_ft * 0.3048,
                            speed_kn=speed_kn, track_deg=0.0,
                            vertical_rate_ms=vr, on_ground=ground)],
    )
def test_b1_matches_hand_calculation():
    assert abs(corrected_net_thrust(IDLE, None, 140.0, 3000.0, 15.0) - 1008.6) < 0.05


def test_flat_rating_min():
    assert corrected_net_thrust(IDLE, dict(IDLE, e=1780), 140.0, 3000.0, 15.0) < 1008.6


def test_cas_from_tas():
    assert abs(calibrated_airspeed_kt(250.0, 914.4) - 228.8) < 0.1


def test_pick_phase_transitions():
    assert pick_phase(0.5, 1000.0, 1500.0) == ("D", "MaxTakeoff")
    assert pick_phase(0.5, 2000.0, 1500.0) == ("D", "MaxClimb")
    assert pick_phase(-0.5, 2000.0, 1500.0) == ("A", "IdleApproach")
    assert pick_phase(0.0, 6000.0, 1500.0) == ("A", "IdleApproach")
    assert pick_phase(0.0, 6001.0, 1500.0) == ("D", "MaxClimb")


def test_unknown_aircraft_excluded():
    res = evaluate_own(REC, [_track()], FakeDb(), {})
    assert res.rows == [] and res.level_db == float("-inf")
    assert res.unknown == ["S1 (abc)"]


class _SubDb(FakeDb):
    """Zwei Ersatztypen für A320: kleiner |Δ| gewinnt (A320-211)."""

    def substitutions(self, icao_code):
        return [("A320-232", 2.3, 2.2), ("A320-211", 0.2, 0.0)]


def test_substitution_used_when_registry_missing():
    db = _SubDb()
    adb = {"abc": {"typecode": "A320", "registration": "HB-JJM",
                   "description": "AIRBUS A-320"}}
    res = evaluate_own(REC, [_track()], db, {}, aircraft_db=adb)
    assert res.rows[0].acft_id == "A320-211"
    assert res.rows[0].via == "substitution"
    assert res.rows[0].delta_db == 0.2
    assert res.unknown == []
    assert res.substituted == [
        "S1 (abc): A320 → A320-211 (Δdep +0.2 dB, Δapp +0.0 dB)"
    ]
    assert "Ersatz" in res.rows[0].bemerkungen
    assert "A320-211" in res.rows[0].bemerkungen


def test_registry_wins_over_substitution():
    db = _SubDb()
    adb = {"abc": {"typecode": "A320", "registration": "HB-JJM",
                   "description": "AIRBUS A-320"}}
    res = evaluate_own(REC, [_track()], db, {"abc": "A320-250N"},
                       aircraft_db=adb)
    assert len(res.rows) == 1
    assert res.rows[0].via == "registry"
    assert res.rows[0].delta_db == 0.0
    assert res.substituted == []
    base = evaluate_own(REC, [_track()], db, {"abc": "A320-250N"})
    assert abs(res.rows[0].lmax_db - base.rows[0].lmax_db) < 1e-9


def test_no_proxy_stays_unknown():
    adb = {"abc": {"typecode": "GLF6"}}
    res = evaluate_own(REC, [_track()], FakeDb(), {}, aircraft_db=adb)
    assert res.rows == []
    assert res.unknown == ["S1 (abc)"]


def test_ground_and_below_ground_skips():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    r1 = evaluate_own(REC, [_track(ground=True)], db, reg)
    assert any("Bodenrollen" in s for s in r1.skipped)
    r2 = evaluate_own(REC, [_track(afe_ft=0.0)], db, reg)
    assert any("unter Bodenebene" in s for s in r2.skipped)


def test_overflight_estimated_not_skipped():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    res = evaluate_own(REC, [_track(afe_ft=10001.0)], db, reg)
    assert res.skipped == [] and len(res.rows) == 1
    row = res.rows[0]
    assert row.estimate is True
    assert row.phase == "departure" and row.thrust_rating == "MaxClimb"
    assert not math.isinf(res.level_db)
    assert "Schätzung" in row.bemerkungen
    assert "ΔI" in row.bemerkungen
    assert "Λ" in row.bemerkungen
    assert "ΔV" in row.bemerkungen


def test_overflight_peak_mixes_covered_and_estimate():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    lo = Position(ts=1, east=2684000.0, north=1256000.0,
                  alt_m=ARP_ALT_M + 2000.0 * 0.3048,
                  speed_kn=180.0, track_deg=0.0, vertical_rate_ms=5.0,
                  on_ground=False)
    hi = Position(ts=2, east=2684000.0, north=1256000.0,
                  alt_m=ARP_ALT_M + 12000.0 * 0.3048,
                  speed_kn=180.0, track_deg=0.0, vertical_rate_ms=0.0,
                  on_ground=False)
    track = Track(icao24="abc", callsign="S1", aircraft_type="X",
                  positions=[lo, hi])
    res = evaluate_own(REC, [track], db, reg, peak=True)
    assert len(res.rows) == 1 and res.skipped == []
    assert res.rows[0].estimate is False  # lauteste Probe ist die tiefe


def test_corrections_direction():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    base = evaluate_own(REC, [_track(east=2684000.0)], db, reg).rows[0].lmax_db
    lat = evaluate_own(REC, [_track(east=2684000.0 + 800)], db, reg).rows[0].lmax_db
    assert lat < base
    high = Receiver(east=2684000.0, north=1256000.0, es=2, nutzung="wohnen", height_m=100.0)
    up = evaluate_own(high, [_track(east=2684000.0)], db, reg).rows[0].lmax_db
    assert up > base


def test_clamping_at_grid_edges():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    res = evaluate_own(REC, [_track(afe_ft=500.0, vr=-5.0, speed_kn=140.0)], db, reg)
    row = res.rows[0]
    assert row.thrust_rating == "IdleApproach"
    assert row.cnt_lbf < 10000.0
    assert abs(row.lmax_db - 85.0) < 0.5


def test_aggregate_energy_sum():
    db, reg = FakeDb(), {"a1": "A320-250N", "a2": "A320-250N"}
    tracks = [_track(icao24="a1", callsign="A", east=2684000.0),
              _track(icao24="a2", callsign="B", east=2684000.0 + 500)]
    res = evaluate_own(REC, tracks, db, reg)
    a, b = (r.lmax_db for r in res.rows)
    assert abs(res.level_db - 10 * math.log10(10 ** (a / 10) + 10 ** (b / 10))) < 1e-9


def test_full_row_pinned():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    res = evaluate_own(REC, [_track(east=2684000.0 + 1000)], db, reg)
    row = res.rows[0]
    assert row.thrust_rating == "MaxClimb"
    assert abs(row.cnt_lbf - 20437.8) < 1.0
    assert abs(row.slant_m - 1171.2) < 0.5
    assert abs(row.lmax_db - 77.24) < 0.1


def test_anp_db_bridge_real_db():
    """Brückenmethoden gegen data/anp.sqlite (nur wenn die DB vorliegt)."""
    from pathlib import Path

    import pytest

    if not Path("data/anp.sqlite").exists():
        pytest.skip("data/anp.sqlite nicht vorhanden")
    from fluglaerm.anp_db import AnpDatabase

    db = AnpDatabase("data/anp.sqlite")
    ac = db.aircraft("A320-250N")
    assert ac is not None and ac["wing"] == "Wing"
    low, hi = db.engine_coefficients("A320-250N", "IdleApproach")
    assert set(low) == {"e", "f", "ga", "gb", "h"} and hi is not None
    assert db.cutback_altitude_ft("A320-250N") == 1500.0

    t_sel = db.npd_table("A320-250N", "SEL", "D", "wing", 27120.0)
    t_lmax = db.npd_table("A320-250N", "LAmax", "D", "wing", 27120.0)
    assert t_sel is not None and t_lmax is not None
    assert len(t_sel.distances_m) == 10 and t_sel.distances_m == sorted(t_sel.distances_m)
    assert t_sel.powers_lbf == sorted(t_sel.powers_lbf)
    assert any(t_sel.le[i][j] for i in range(len(t_sel.powers_lbf))
               for j in range(10))
    assert not any(t_sel.lmax[i][j] for i in range(len(t_sel.powers_lbf))
                   for j in range(10))
    assert any(t_lmax.lmax[i][j] for i in range(len(t_lmax.powers_lbf))
               for j in range(10))
    assert db.npd_table("NOPE-0000", "SEL", "D", "wing", 27120.0) is None
    if not Path("data/anp_archive.sqlite").exists():
        pytest.skip("data/anp_archive.sqlite nicht vorhanden")
    db = AnpDatabase.with_archive("data/anp.sqlite")
    subs = db.substitutions("A320")
    assert ("A320-211", 0.2, 0.0) in subs
    assert db.source_for("A320-211") is not None
    assert db.source_for("A320-211") is not db  # kommt aus dem Archiv
    assert db.source_for("7773ER") is db        # v9 hat es selbst


def test_load_credentials(tmp_path):
    from fluglaerm.ist_laerm.opensky import load_credentials

    camel = tmp_path / "credentials.json"
    camel.write_text('{"clientId": "abc", "clientSecret": "xyz"}', encoding="utf-8")
    assert load_credentials(str(camel)) == ("abc", "xyz")

    snake = tmp_path / "snake.json"
    snake.write_text('{"client_id": "abc", "client_secret": "xyz"}', encoding="utf-8")
    assert load_credentials(str(snake)) == ("abc", "xyz")

    partial = tmp_path / "partial.json"
    partial.write_text('{"clientId": "abc"}', encoding="utf-8")
    for bad in (str(partial), str(tmp_path / "missing.json")):
        try:
            load_credentials(bad)
            raise AssertionError(f"erwartete ValueError für {bad}")
        except ValueError:
            pass

    notjson = tmp_path / "notjson.json"
    notjson.write_text("nope", encoding="utf-8")
    try:
        load_credentials(str(notjson))
        raise AssertionError("erwartete ValueError für ungültiges JSON")
    except ValueError:
        pass


class _HistoryStub(OpenSkyClient):
    """Zeichnet own_states-Aufrufe auf; liefert synthetische States oder HTTP-Fehler."""

    def __init__(self, rows_by_t, raise_status=None, raise_from_t=None):
        super().__init__(client_id="id", client_secret="secret")
        self.calls = []
        self._rows = rows_by_t
        self._raise_status = raise_status
        self._raise_from_t = raise_from_t

    def own_states(self, serials, time):
        self.calls.append((serials, time))
        if self._raise_status is not None and time >= self._raise_from_t:
            resp = requests.Response()
            resp.status_code = self._raise_status
            raise requests.HTTPError(response=resp)
        return self._rows.get(time, [])


def test_own_history_backfills_and_dedupes():
    rows = {
        1000: [{"icao24": "abc", "last_contact": 1000},
               {"icao24": "def", "last_contact": 999}],
        1060: [{"icao24": "abc", "last_contact": 1000},
               {"icao24": "ghi", "last_contact": 1060}],
        1120: [{"icao24": "abc", "last_contact": 1100}],
    }
    client = _HistoryStub(rows)
    out = client.own_history(1000, 1180, 60, [7])
    # end-exklusiv: 1000, 1060, 1120 – genau 3 Aufrufe, serials forwarded
    assert client.calls == [([7], 1000), ([7], 1060), ([7], 1120)]
    # abc@1000 wiederholt sich in Schritt 2; dedupe auf (icao24, last_contact)
    assert [(s["icao24"], s["last_contact"]) for s in out] == [
        ("abc", 1000), ("def", 999), ("ghi", 1060), ("abc", 1100)]


def test_own_history_stops_on_400():
    rows = {1000: [{"icao24": "abc", "last_contact": 1000}]}
    client = _HistoryStub(rows, raise_status=400, raise_from_t=1060)
    out = client.own_history(1000, 1180, 60)
    assert [s["icao24"] for s in out] == ["abc"]
    assert client.calls == [(None, 1000), (None, 1060)]

    client500 = _HistoryStub(rows, raise_status=500, raise_from_t=1060)
    try:
        client500.own_history(1000, 1180, 60)
        raise AssertionError("erwartete HTTPError 500")
    except requests.HTTPError as exc:
        assert exc.response.status_code == 500


def test_own_history_rejects_bad_params():
    client = _HistoryStub({})
    for args in ((1000, 1000, 60), (2000, 1000, 60), (1000, 1180, 0)):
        try:
            client.own_history(*args)
            raise AssertionError(f"erwartete ValueError für {args}")
        except ValueError:
            pass
    assert client.calls == []


def _single_lmax(pos, db, reg):
    track = Track(icao24="abc", callsign="S1", aircraft_type="X", positions=[pos])
    res = evaluate_own(REC, [track], db, reg)
    assert len(res.rows) == 1
    return res.rows[0].lmax_db


def test_peak_over_window():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    older = Position(ts=100, east=2684000.0, north=1256000.0,
                     alt_m=ARP_ALT_M + 2000.0 * 0.3048, speed_kn=180.0,
                     track_deg=0.0, vertical_rate_ms=5.0)
    newer = Position(ts=200, east=2684000.0 + 3000.0, north=1256000.0,
                     alt_m=ARP_ALT_M + 1500.0 * 0.3048, speed_kn=200.0,
                     track_deg=0.0, vertical_rate_ms=5.0)
    a = _single_lmax(older, db, reg)
    b = _single_lmax(newer, db, reg)
    assert a > b  # der ältere Sample ist lauter (näher, steilerer elev)
    track = Track(icao24="abc", callsign="S1", aircraft_type="X",
                  positions=[older, newer])
    res = evaluate_own(REC, [track], db, reg, peak=True)
    assert len(res.rows) == 1 and res.skipped == []
    assert abs(res.rows[0].lmax_db - a) < 1e-9
    assert res.rows[0].ts == older.ts
    # L_jetzt = energetische Summe über ALLE ausgewerteten Samples des Fensters
    assert abs(res.level_db - 10 * math.log10(10 ** (a / 10) + 10 ** (b / 10))) < 1e-9


def test_current_mode_unchanged():
    db, reg = FakeDb(), {"abc": "A320-250N"}
    newest = Position(ts=200, east=2684000.0 + 1000.0, north=1256000.0,
                      alt_m=ARP_ALT_M + 2000.0 * 0.3048, speed_kn=180.0,
                      track_deg=0.0, vertical_rate_ms=5.0)
    older = Position(ts=100, east=2684000.0, north=1256000.0,
                     alt_m=ARP_ALT_M + 2000.0 * 0.3048, speed_kn=180.0,
                     track_deg=0.0, vertical_rate_ms=5.0)
    track = Track(icao24="abc", callsign="S1", aircraft_type="X",
                  positions=[older, newest])
    res = evaluate_own(REC, [track], db, reg)  # Default peak=False
    single = evaluate_own(
        REC, [Track(icao24="abc", callsign="S1", aircraft_type="X",
                    positions=[newest])], db, reg)
    assert len(res.rows) == 1 and res.skipped == []
    assert res.rows[0].ts == newest.ts  # nur der neueste Sample zählt
    assert abs(res.rows[0].lmax_db - single.rows[0].lmax_db) < 1e-9
    assert abs(res.level_db - single.level_db) < 1e-9


def test_own_table_strings():
    from fluglaerm.ist_laerm.own import AircraftLevel, format_own_header, format_own_row
    r = AircraftLevel(
        icao24="abc", callsign="S1", acft_id="A320-211",
        description="AIRBUS A-320", engines=2, wing="Wing",
        phase="departure", thrust_rating="MaxClimb",
        cnt_lbf=20000.0, slant_m=3000.0, lmax_db=80.0, sel_db=90.0,
        ts=1730000000, via="substitution", delta_db=0.2,
        estimate=True, di_db=1.5, lam_db=2.0, dv_db=-0.5,
        flat_rated=False, sub_typecode="GLF6",
    )
    assert "Bemerkungen" in format_own_header()
    assert "Ersatz GLF6 → A320-211" in format_own_row(r)


def test_own_detail_populated():
    from fluglaerm.ist_laerm.own import evaluate_own
    res = evaluate_own(REC, [_track()], FakeDb(), {"abc": "A320-250N"})
    assert res.rows
    d = res.rows[0].detail
    assert d is not None
    assert d.npd_id == "X"
    assert d.cnt_lbf > 0
    assert d.base_lmax_db > 0
    assert abs(d.lmax_db - res.rows[0].lmax_db) < 1e-9
    assert d.op_mode in ("D", "A")


def test_render_own_report():
    from fluglaerm.ist_laerm.own import evaluate_own
    from fluglaerm.ist_laerm.report import render_own_report
    res = evaluate_own(REC, [_track()], FakeDb(), {"abc": "A320-250N"})
    md = render_own_report(res, REC, db_path="data/anp.sqlite",
                           registry_path="data/aircraft_registry.json",
                           radius=15000.0, window=0)
    assert "Rufzeichen" in md
    assert "S1 (abc)" in md
    assert "jet_engine_coefficients" in md
    assert "npd_data" in md
    assert "data/anp.sqlite" in md
    assert "L_jetzt" in md
    assert "Methodik" in md
