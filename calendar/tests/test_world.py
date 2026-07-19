"""World-timeline tests. Two on-axis calendars convert to each other with no
per-pair anchor (composition through world-day 0); off-axis calendars are refused;
and the world index loads and validates.

Runnable directly (``python tests/test_world.py``) or under pytest.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fcal.engine import Calendar, Month, Week, Date, convert  # noqa: E402
from fcal.world import World  # noqa: E402


def _anchor_cal(offset):
    """A trivial calendar (ten 10-day months, 5-day week) placed on the axis."""
    return Calendar(
        name=f"cal@{offset}",
        months=[Month(f"M{i}", 10, f"m{i:02d}") for i in range(1, 11)],
        week=Week(5, ["a", "b", "c", "d", "e"]),
        epoch_year=1, start_weekday=0, current_year=1,
        epoch_offset=offset,
    )


def test_on_timeline_flag():
    assert _anchor_cal(0).on_world_timeline is True
    off = _anchor_cal(0)
    off.epoch_offset = None
    assert off.on_world_timeline is False


def test_world_day_composition():
    a = _anchor_cal(0)       # its day 1 is world-day 0
    b = _anchor_cal(500)     # its day 1 is world-day 500

    # a's day 1 (world-day 0) is 500 days before b's day 1, so in b it is year -?
    d_a = Date(1, "m01", 1)
    assert a.to_world_day(d_a) == 0
    # Convert a->b->a and check round-trip for a spread of dates.
    for (blk, day, yr) in [("m01", 1, 1), ("m05", 7, 3), ("m10", 10, 50)]:
        d = Date(yr, blk, day)
        wd = a.to_world_day(d)
        in_b = convert(d, a, b)
        assert b.to_world_day(in_b) == wd            # same real day on the axis
        back = convert(in_b, b, a)
        assert (back.year, back.block, back.day) == (d.year, d.block, d.day)


def test_offaxis_is_refused():
    on = _anchor_cal(0)
    off = _anchor_cal(0)
    off.epoch_offset = None
    for args in ((Date(1, "m01", 1), on, off), (Date(1, "m01", 1), off, on)):
        try:
            convert(*args)
            assert False, "expected ValueError for off-timeline calendar"
        except ValueError:
            pass


def test_world_index_loads_and_validates():
    with tempfile.TemporaryDirectory() as dtmp:
        base = Path(dtmp)
        (base / "canon").mkdir()
        _anchor_cal(0).save(str(base / "canon" / "alpha.json"))
        _anchor_cal(-732).save(str(base / "canon" / "beta.json"))
        index = {
            "schema_version": 1,
            "anchor": {"calendar": "alpha", "world_day": 0, "description": "test"},
            "calendars": [
                {"name": "alpha", "file": "canon/alpha.json", "status": "canon", "note": ""},
                {"name": "beta", "file": "canon/beta.json", "status": "historical", "note": ""},
            ],
        }
        (base / "world.json").write_text(json.dumps(index), encoding="utf-8")

        w = World.load(base / "world.json")
        assert w.problems() == []
        assert set(w.calendars) == {"alpha", "beta"}
        # beta's day 1 sits 732 days before alpha's day 1.
        assert w.to_world_day(Date(1, "m01", 1), "beta") == -732
        # any-to-any via the registry
        d = Date(3, "m04", 5)
        assert w.to_world_day(w.convert(d, "alpha", "beta"), "beta") == \
               w.to_world_day(d, "alpha")


def test_world_index_rejects_bad_anchor():
    with tempfile.TemporaryDirectory() as dtmp:
        base = Path(dtmp)
        (base / "canon").mkdir()
        _anchor_cal(99).save(str(base / "canon" / "alpha.json"))   # offset != 0
        index = {
            "schema_version": 1,
            "anchor": {"calendar": "alpha", "world_day": 0},
            "calendars": [{"name": "alpha", "file": "canon/alpha.json", "status": "canon"}],
        }
        (base / "world.json").write_text(json.dumps(index), encoding="utf-8")
        try:
            World.load(base / "world.json")
            assert False, "expected ValueError for mismatched anchor offset"
        except ValueError:
            pass


if __name__ == "__main__":
    test_on_timeline_flag()
    test_world_day_composition()
    test_offaxis_is_refused()
    test_world_index_loads_and_validates()
    test_world_index_rejects_bad_anchor()
    print("WORLD TIMELINE TESTS PASSED")
