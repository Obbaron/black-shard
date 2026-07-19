#!/usr/bin/env python3
"""
fcal.cli - command-line front end

Run as a module from package root:  ``python -m fcal.cli <command>``

Calendars may be named by their bundled short name (``yavanna``, ``gregorian``),
which resolves to ``data/canon`` or ``data/reference``, or by an explicit path to
any ``.json`` file.

Examples
--------
  # (re)build the bundled calendars + a rendered Yavanna year
  python -m fcal.cli examples

  # summarize a calendar
  python -m fcal.cli info yavanna

  # render a year to HTML
  python -m fcal.cli render yavanna --year 812 --out rendered/yavanna_812.html

  # print year to terminal
  python -m fcal.cli show yavanna --year 812

  # what weekday / moon phases does a date fall on?
  python -m fcal.cli date yavanna --year 812 --block m01 --day 1

  # convert a date between two calendars, given one shared anchor day
  python -m fcal.cli convert \
      --from yavanna --to gregorian \
      --anchor-from 812:m01:1 --anchor-to 2026:jul:19 \
      --date 812:plerosis:1
"""

import argparse
import runpy
import sys
from pathlib import Path

from . import paths
from .engine import Calendar, Converter, Date


def _resolve(name: str) -> str:
    """Turn a short name or path into a calendar JSON path."""
    p = Path(name)

    if p.exists():
        return str(p)

    stem = p.name[:-5] if p.name.endswith(".json") else p.name

    for base in (paths.CANON_DIR, paths.REFERENCE_DIR):
        cand = base / f"{stem}.json"
        if cand.exists():
            return str(cand)

    raise SystemExit(
        f"calendar '{name}' not found (looked for a path, and for "
        f"{stem}.json under data/canon and data/reference)"
    )


def _parse_date(spec: str) -> Date:
    y, block, day = spec.split(":")
    return Date(int(y), block, int(day))


def cmd_examples(_):
    builder = paths.ROOT / "examples" / "build_calendars.py"

    if not builder.exists():
        raise SystemExit(f"builder not found: {builder}")

    runpy.run_path(str(builder), run_name="__main__")


def cmd_info(a):
    cal = Calendar.load(_resolve(a.file))

    probs = cal.validate()

    print(f"{cal.name}")
    print(
        f"  year length : {cal.year_length(cal.current_year)} days "
        f"({'hard' if cal.hard_year else 'soft'})"
    )
    print(f"  months      : {len(cal.months)}")
    print(
        f"  week        : {cal.week.length} days "
        f"({'hard' if cal.week.hard else 'soft'}) "
        f"[{', '.join(cal.week.names)}]"
    )
    print(
        f"  moons       : {', '.join(f'{m.name} ({m.cycle}d)' for m in cal.moons) or '-'}"
    )
    print(
        f"  epoch       : year {cal.epoch_year} opens on "
        f"{cal.week.name_for(cal.start_weekday)}; current year {cal.current_year}"
    )

    wd = cal.new_year_weekday(cal.current_year)

    if wd is not None:
        print(f"  new year    : {cal.week.name_for(wd)}")

    if probs:
        print("  WARNINGS:")
        for p in probs:
            print(f"    - {p}")


def cmd_render(a):
    from .render import render_year_html

    src = _resolve(a.file)
    cal = Calendar.load(src)
    year = a.year if a.year is not None else cal.current_year
    stem = Path(src).stem
    out = a.out or str(paths.RENDERED_DIR / f"{stem}_{year}.html")

    paths.RENDERED_DIR.mkdir(parents=True, exist_ok=True)

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render_year_html(cal, year, title=a.title or cal.name))

    print(f"Wrote {out}")


def cmd_show(a):
    from .render import render_year_text

    cal = Calendar.load(_resolve(a.file))
    year = a.year if a.year is not None else cal.current_year

    print(render_year_text(cal, year))


def cmd_date(a):
    cal = Calendar.load(_resolve(a.file))
    date = Date(a.year, a.block, a.day)
    ord = cal.date_to_ordinal(date)
    wd = cal.weekday_name_of_ordinal(ord)

    print(f"{date}")
    print(f"  ordinal   : {ord}")

    if cal.on_world_timeline:
        print(f"  world-day : {cal.to_world_day(date)}")

    print(f"  weekday   : {wd if wd else '- (outside the week)'}")

    for name, phase in cal.moon_phases(ord).items():
        print(f"  {name:9s}: {phase}")


def cmd_convert(a):
    src = Calendar.load(_resolve(getattr(a, "from")))
    dst = Calendar.load(_resolve(a.to))
    date = _parse_date(a.date)

    if a.anchor_from and a.anchor_to:
        conv = Converter(src, dst, _parse_date(a.anchor_from), _parse_date(a.anchor_to))
        result = conv.a_to_b(date)
        how = "via anchor"

    elif src.on_world_timeline and dst.on_world_timeline:
        from .engine import convert

        result = convert(date, src, dst)
        how = "via world axis"

    else:
        off = src.name if not src.on_world_timeline else dst.name
        raise SystemExit(
            f"{off!r} is not on the world timeline, so an anchor is required: "
            f"pass --anchor-from and --anchor-to (a shared day in each calendar)."
        )

    wd = dst.weekday_name_of_ordinal(dst.date_to_ordinal(result))
    print(f"{a.date}  in {src.name}")
    print(f"  = {result}  in {dst.name}  ({wd if wd else 'outside the week'})  [{how}]")


def cmd_calendars(_):
    from .world import World

    try:
        world = World.load()

    except FileNotFoundError:
        raise SystemExit(f"no world index found at {paths.DATA_DIR / 'world.json'}")

    print(f"Anchor: {world.anchor_calendar} = world-day {world.anchor_world_day}")
    if world.anchor_description:
        print(f"  {world.anchor_description}")

    print()
    print(f"{'name':16s} {'status':11s} {'offset':>8s}  note")
    print("-" * 72)

    for e in world.entries:
        cal = world.calendars[e.name]
        off = "-" if cal.epoch_offset is None else str(cal.epoch_offset)
        print(f"{e.name:16s} {e.status:11s} {off:>8s}  {e.note}")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Fantasy calendar creator / viewer / converter"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("examples", help="write bundled example calendars").set_defaults(
        fn=cmd_examples
    )

    s = sub.add_parser("info", help="summarize a calendar")
    s.add_argument("file")
    s.set_defaults(fn=cmd_info)

    s = sub.add_parser("render", help="render a year to HTML")
    s.add_argument("file")
    s.add_argument("--year", type=int)
    s.add_argument("--out")
    s.add_argument("--title")
    s.set_defaults(fn=cmd_render)

    s = sub.add_parser("show", help="print a year as text")
    s.add_argument("file")
    s.add_argument("--year", type=int)
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("date", help="inspect one date")
    s.add_argument("file")
    s.add_argument("--year", type=int, required=True)
    s.add_argument("--block", required=True)
    s.add_argument("--day", type=int, required=True)
    s.set_defaults(fn=cmd_date)

    sub.add_parser(
        "calendars", help="list the world's calendars and their offsets"
    ).set_defaults(fn=cmd_calendars)

    s = sub.add_parser("convert", help="convert a date between calendars")
    s.add_argument("--from", required=True)
    s.add_argument("--to", required=True)
    s.add_argument(
        "--anchor-from",
        dest="anchor_from",
        help="a date in --from; only needed for off-timeline calendars",
    )
    s.add_argument(
        "--anchor-to",
        dest="anchor_to",
        help="the same real day in --to; only needed for off-timeline calendars",
    )
    s.add_argument("--date", required=True)
    s.set_defaults(fn=cmd_convert)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
