from fluglaerm.common.types import Receiver
from fluglaerm.ist_laerm.ist import IST_LABEL, evaluate_ist
from fluglaerm.ist_laerm.track import Track, Position, build_tracks


def _states():
    base = {"icao24": "ab12cd", "callsign": "SWR1A", "velocity": 90.0,
            "true_track": 160.0, "time_position": 1700000000, "last_contact": 1700000000}
    pts = [(8.5524, 47.4494, 600.0), (8.5560, 47.4520, 650.0)]
    return [{**base, "longitude": lo, "latitude": la, "geo_altitude": a,
             "baro_altitude": a, "time_position": 1700000000 + i,
             "last_contact": 1700000000 + i} for i, (lo, la, a) in enumerate(pts)]


def test_build_tracks_groups_and_filters():
    tracks = build_tracks(_states(), 2684000, 1256000,
                          type_by_icao24={"ab12cd": "A320-214"})
    assert len(tracks) == 1
    assert tracks[0].aircraft_type == "A320-214"
    assert len(tracks[0].positions) == 2
    # weit entfernte Spur wird verworfen
    far = build_tracks(_states(), 2500000, 1100000)
    assert far == []


def test_ist_label_and_positive_leq():
    tracks = build_tracks(_states(), 2684000, 1256000)
    rec = Receiver(east=2684000, north=1256000, es=2, nutzung="wohnen")
    res = evaluate_ist(rec, tracks, 900.0)
    assert res.leq > 0
    assert res.n_flights == 1
    assert res.label == IST_LABEL
    assert "nicht rechtsgültig" in res.label

def test_ist_receiver_height_increases_leq():
    tracks = build_tracks(_states(), 2684000, 1256000)
    base = evaluate_ist(Receiver(east=2684000, north=1256000, es=2, nutzung="wohnen"),
                        tracks, 900.0)
    high = evaluate_ist(Receiver(east=2684000, north=1256000, es=2, nutzung="wohnen",
                                 height_m=100.0), tracks, 900.0)
    assert high.leq > base.leq
