import math

from fluglaerm.common.types import Movement, MovementDataset, Period, Receiver, Route, Segment
from fluglaerm.engine.acoustic import accumulate_leq, gesamt_lrt, klein_lrk
from fluglaerm.engine.engine import evaluate


def _mini_dataset() -> MovementDataset:
    seg = lambda e, n, a: Segment(east=e, north=n, alt_m=a, thrust=None)
    routes = [
        Route(id="R1", kind="departure", runway="16", share=1.0,
              segments=[seg(2684000, 1254000, 0.0), seg(2684000, 1256000, 400.0),
                        seg(2684000, 1258000, 800.0)]),
    ]
    return MovementDataset(
        airport_icao="LSZH", airport_east=2684000.0, airport_north=1256000.0,
        periods=[Period(id="tag", start_hour=6, end_hour=22),
                 Period(id="nacht1", start_hour=22, end_hour=23),
                 Period(id="nacht2", start_hour=23, end_hour=24)],
        routes=routes,
        movements=[Movement(route_id="R1", aircraft_anp="A320-214", period="tag",
                            count=36500, weight_class="gross")],
    )


def test_engine_monotonic_distance():
    ds = _mini_dataset()
    near = evaluate(ds, Receiver(east=2684300, north=1256000, es=2, nutzung="wohnen"))
    mid = evaluate(ds, Receiver(east=2689000, north=1261000, es=2, nutzung="wohnen"))
    assert 50.0 < near.lrt < 80.0
    assert mid.lrt < near.lrt
    assert near.agl == "innerhalb"


def test_engine_status_keys():
    res = evaluate(_mini_dataset(),
                   Receiver(east=2684300, north=1256000, es=2, nutzung="wohnen"))
    assert set(res.status) == {"tag", "nacht1", "nacht2"}


def test_acoustic_identities():
    assert gesamt_lrt(55.0, 63.0) == 10 * math.log10(10**5.5 + 10**6.3)
    assert klein_lrk(50.0, 15000) == 50.0
    assert klein_lrk(50.0, 20000) == 50.0 + 10 * math.log10(20000 / 15000)
    assert accumulate_leq([], 3600.0) == float("-inf")
    assert accumulate_leq([80.0], 1.0) == 80.0

def test_engine_receiver_height_increases_level():
    ds = _mini_dataset()
    base = evaluate(ds, Receiver(east=2684000, north=1256000, es=2, nutzung="wohnen"))
    high = evaluate(ds, Receiver(east=2684000, north=1256000, es=2, nutzung="wohnen",
                                 height_m=50.0))
    assert high.lrt > base.lrt
