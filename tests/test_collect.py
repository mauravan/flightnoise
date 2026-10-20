"""Collector: tar1090-Konvertierung, StateStore, collect_once (hermetisch)."""

from __future__ import annotations

import fluglaerm.ist_laerm.collect as collect_mod
from fluglaerm.ist_laerm.collect import StateStore, aircraft_to_state, collect_once, import_history

NOW = 1700000000


def _full() -> dict:
    return {
        "hex": "4B1698",
        "flight": "SWR4TD  ",
        "lat": 47.46,
        "lon": 8.55,
        "alt_baro": 38000,
        "alt_geom": 37500,
        "gs": 450.0,
        "track": 90.0,
        "baro_rate": -2100,
        "seen": 2.0,
    }


def test_aircraft_to_state_units():
    s = aircraft_to_state(_full(), NOW)
    assert s is not None
    assert s["baro_altitude"] == 38000 * 0.3048
    assert s["geo_altitude"] == 37500 * 0.3048
    assert s["velocity"] == 450 * 0.5144444
    assert s["vertical_rate"] == -2100 * 0.00508
    assert s["callsign"] == "SWR4TD"
    assert s["icao24"] == "4b1698"
    assert s["time_position"] == NOW
    assert s["last_contact"] == NOW - 2
    assert s["on_ground"] == 0


def test_aircraft_to_state_ground():
    ac = _full()
    ac["alt_baro"] = "ground"
    s = aircraft_to_state(ac, NOW)
    assert s is not None
    assert s["on_ground"] == 1
    assert s["baro_altitude"] is None


def test_aircraft_to_state_skips():
    ac = _full()
    del ac["lat"]
    assert aircraft_to_state(ac, NOW) is None
    ac = _full()
    ac["lon"] = None
    assert aircraft_to_state(ac, NOW) is None
    ac = _full()
    ac["hex"] = "~abc123"
    assert aircraft_to_state(ac, NOW) is None
    ac = _full()
    ac["hex"] = ""
    assert aircraft_to_state(ac, NOW) is None


def test_aircraft_to_state_rate_fallback():
    ac = _full()
    del ac["baro_rate"]
    ac["geom_rate"] = 1000
    s = aircraft_to_state(ac, NOW)
    assert s is not None
    assert s["vertical_rate"] == 1000 * 0.00508
    ac = _full()
    del ac["baro_rate"]
    s = aircraft_to_state(ac, NOW)
    assert s is not None
    assert s["vertical_rate"] is None


def _row(ts: int, icao24: str = "abc123") -> dict:
    return {
        "icao24": icao24, "callsign": "S1", "time_position": ts,
        "last_contact": ts, "longitude": 8.55, "latitude": 47.46,
        "baro_altitude": 3000.0, "geo_altitude": 3100.0, "velocity": 100.0,
        "true_track": 90.0, "vertical_rate": 0.0, "on_ground": 0,
    }


def test_store_insert_dedup(tmp_path):
    store = StateStore(str(tmp_path / "s.sqlite"))
    store.init_schema()
    assert store.insert_states([_row(1000)]) == 1
    assert store.insert_states([_row(1000)]) == 0
    assert len(store.states_between(0, 2000)) == 1


def test_store_states_between_window(tmp_path):
    store = StateStore(str(tmp_path / "s.sqlite"))
    store.init_schema()
    store.insert_states([_row(1000), _row(1010), _row(1020)])
    rows = store.states_between(1010, 1020)
    assert [r["time_position"] for r in rows] == [1010]


def test_collect_once_inserts(tmp_path, monkeypatch):
    store = StateStore(str(tmp_path / "s.sqlite"))
    store.init_schema()
    monkeypatch.setattr(
        collect_mod, "fetch_aircraft_json",
        lambda host, port=8080, timeout=10: {"now": NOW, "aircraft": [_full()]},
    )
    assert collect_once(store, "pi") == 1
    rows = store.states_between(NOW - 10, NOW + 10)
    assert len(rows) == 1
    assert rows[0]["icao24"] == "4b1698"

def test_import_history_backfills(tmp_path, monkeypatch):
    store = StateStore(str(tmp_path / "s.sqlite"))
    store.init_schema()
    t0 = NOW
    snaps = {
        0: {"now": t0, "aircraft": [_full()]},
        1: {"now": t0 - 30, "aircraft": [_full()]},
    }
    monkeypatch.setattr(collect_mod, "fetch_receiver_json", lambda host, port=8080, timeout=10: {"history": 2})
    monkeypatch.setattr(collect_mod, "fetch_history_json",
                        lambda host, port=8080, index=0, timeout=10: snaps[index])
    assert import_history(store, "pi") == (2, 2)
    rows = store.states_between(t0 - 30, t0 + 1)
    assert {r["time_position"] for r in rows} == {t0 - 30, t0}


def test_import_history_skips_missing(tmp_path, monkeypatch):
    store = StateStore(str(tmp_path / "s.sqlite"))
    store.init_schema()
    snaps = {0: {"now": NOW, "aircraft": [_full()]}, 1: {"now": NOW - 30, "aircraft": [_full()]}}
    monkeypatch.setattr(collect_mod, "fetch_receiver_json", lambda host, port=8080, timeout=10: {"history": 3})
    monkeypatch.setattr(collect_mod, "fetch_history_json",
                        lambda host, port=8080, index=0, timeout=10: snaps.get(index))
    loaded, _ = import_history(store, "pi")
    assert loaded == 2


def test_import_history_no_marker(tmp_path, monkeypatch):
    store = StateStore(str(tmp_path / "s.sqlite"))
    store.init_schema()
    calls = []
    monkeypatch.setattr(collect_mod, "fetch_receiver_json", lambda host, port=8080, timeout=10: {})
    monkeypatch.setattr(collect_mod, "fetch_history_json",
                        lambda host, port=8080, index=0, timeout=10: calls.append(index))
    assert import_history(store, "pi") == (0, 0)
    assert calls == []
    monkeypatch.setattr(collect_mod, "fetch_receiver_json", lambda host, port=8080, timeout=10: None)
    assert import_history(store, "pi") == (0, 0)


def test_import_history_idempotent(tmp_path, monkeypatch):
    store = StateStore(str(tmp_path / "s.sqlite"))
    store.init_schema()
    snaps = {0: {"now": NOW, "aircraft": [_full()]}, 1: {"now": NOW - 30, "aircraft": [_full()]}}
    monkeypatch.setattr(collect_mod, "fetch_receiver_json", lambda host, port=8080, timeout=10: {"history": 2})
    monkeypatch.setattr(collect_mod, "fetch_history_json",
                        lambda host, port=8080, index=0, timeout=10: snaps[index])
    assert import_history(store, "pi") == (2, 2)
    assert import_history(store, "pi") == (2, 0)
    assert len(store.states_between(NOW - 30, NOW + 1)) == 2
