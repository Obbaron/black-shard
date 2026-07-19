"""
fcal.engine

Vocab
-----
ordinal
    An absolute integer day-count. ``ordinal 0`` is the first day of the calendar's
    ``epoch_year``. Every day the calendar has ever had or will have maps to exactly
    one ordinal, and vice-versa. All arithmetic (weekday, moon phase, conversion) is
    done in ordinals; dates are just a human-readable face on top.
segment
    One year is decomposed into an ordered list of *segments*. A segment is either a
    month or an intercalary period, already resolved for a specific year (leap
    adjustments applied). This is the single source of truth for that year's layout.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List, Optional

SCHEMA_VERSION = 1


@dataclass
class Month:
    name: str
    days: int
    id: Optional[str] = None
    out_of_week_tail: int = 0
    tail_name: Optional[str] = None
    tail_id: Optional[str] = None

    def key(self) -> str:
        return self.id or self.name

    def tail_key(self) -> str:
        return self.tail_id or self.tail_name or f"{self.key()}~tail"


@dataclass
class Intercalary:
    """A run of days that sits between months and belongs to no month.

    ``after_month`` is a 1-based month index; the period falls immediately after
    that month. ``after_month = 0`` places it before the first month of the year.

    ``in_week=False`` marks these days as living outside the weekday cycle: they get
    no weekday and they do not advance the week. That is how e.g. a festival can sit
    "outside" the week and let the weekday cycle resume cleanly afterwards.
    """

    name: str
    days: int
    after_month: int = 0
    in_week: bool = True
    id: Optional[str] = None

    def key(self) -> str:
        return self.id or self.name


@dataclass
class Week:
    length: int
    names: List[str] = field(default_factory=list)
    hard: bool = True

    def name_for(self, index: int) -> str:
        if self.names and 0 <= index < len(self.names):
            return self.names[index]
        return f"Day {index + 1}"


@dataclass
class Moon:
    name: str
    cycle: float
    shift: float = 0.0
    color: str = "#cbd5e1"

    def phase_fraction(self, ordinal: int) -> float:
        """Return phase in [0, 1): 0.0 = new moon, 0.5 = full moon."""
        return ((ordinal + self.shift) % self.cycle) / self.cycle


@dataclass
class Adjustment:
    target: str  # month.key() | intercalary.key()
    days: int  # +/- days applied in leap years


@dataclass
class LeapRule:
    """A Gregorian-style leap rule.

    A year matches when ``(year - anchor) % interval == 0``, *except* when it also
    matches the (optional) except-clause, *unless* it further matches the (optional)
    unless-clause. Gregorian is ``interval=4, except_interval=100, unless_interval=400``.

    When a year matches, every listed adjustment is applied to its target block.
    Multiple matching rules stack.
    """

    name: str
    interval: int
    anchor: int = 0
    except_interval: Optional[int] = None
    except_anchor: int = 0
    unless_interval: Optional[int] = None
    unless_anchor: int = 0
    adjustments: List[Adjustment] = field(default_factory=list)

    def matches(self, year: int) -> bool:
        if self.interval <= 0 or (year - self.anchor) % self.interval != 0:
            return False

        if (
            self.except_interval
            and (year - self.except_anchor) % self.except_interval == 0
        ):
            if (
                self.unless_interval
                and (year - self.unless_anchor) % self.unless_interval == 0
            ):
                return True

            return False

        return True


@dataclass
class Segment:
    kind: str  # "month" | "intercalary"
    name: str
    key: str
    days: int
    in_week: bool


@dataclass
class Date:
    """Human-facing date: year, block (month | intercalary); index 1."""

    year: int
    block: str  # month.key()
    day: int

    def __str__(self) -> str:
        return f"{self.day} {self.block}, {self.year}"


@dataclass
class Calendar:
    name: str
    months: List[Month] = field(default_factory=list)
    intercalary: List[Intercalary] = field(default_factory=list)
    week: Week = field(default_factory=lambda: Week(7))
    moons: List[Moon] = field(default_factory=list)
    leap_rules: List[LeapRule] = field(default_factory=list)

    epoch_year: int = 1  # year ordinal 0 begins
    start_weekday: int = 0  # weekday index of ordinal 0
    current_year: int = 1  # "what year it is" (default view)
    has_year_zero: bool = True  # whether year 0 in the numbering
    hard_year: bool = True  # year length may never change (no leap adjustments)

    # Placement on the shared world timeline. ``epoch_offset`` is the world-day
    # number of this calendar's ordinal 0 i.e. how many days its own day 1 sits
    # from world-day 0 (negative if it predates the anchor). ``None`` means the
    # calendar is NOT on the world timeline e.g. a real-world reference like the
    # Gregorian yardstick; such calendars can only be converted via an explicit
    # anchor (see Converter), never through the world axis.
    epoch_offset: Optional[int] = None

    phase_names: List[str] = field(
        default_factory=lambda: [
            "New",
            "Waxing crescent",
            "First quarter",
            "Waxing gibbous",
            "Full",
            "Waning gibbous",
            "Last quarter",
            "Waning crescent",
        ]
    )

    def validate(self) -> List[str]:
        problems: List[str] = []
        if not self.months:
            problems.append("Calendar has no months.")

        if self.week.length <= 0:
            problems.append("Week length must be positive.")

        if self.week.names and len(self.week.names) != self.week.length:
            problems.append(
                f"Week has {self.week.length} days but {len(self.week.names)} names."
            )

        for m in self.months:
            if m.days <= 0:
                problems.append(f"Month {m.name!r} must have a positive day count.")

        for ic in self.intercalary:
            if ic.days < 0:
                problems.append(f"Intercalary {ic.name!r} has negative days.")

            if not (0 <= ic.after_month <= len(self.months)):
                problems.append(
                    f"Intercalary {ic.name!r} has after_month={ic.after_month} "
                    f"outside 0..{len(self.months)}."
                )

            if self.week.hard and not ic.in_week and ic.days > 0:
                problems.append(
                    f"Week is 'hard' but intercalary {ic.name!r} is out-of-week."
                )

        for moon in self.moons:
            if moon.cycle <= 0:
                problems.append(f"Moon {moon.name!r} must have a positive cycle.")

        if self.hard_year and self.leap_rules:
            base = self.year_length(self.epoch_year)

            for probe in (
                self.epoch_year + 1,
                self.epoch_year + 3,
                self.epoch_year + 99,
            ):
                if self.year_length(probe) != base:
                    problems.append(
                        "Year is 'hard' but leap rules change the year length "
                        f"(year {probe} = {self.year_length(probe)} vs {base})."
                    )

                    break

        keys = [b.key() for b in list(self.months) + list(self.intercalary)]
        keys += [m.tail_key() for m in self.months if m.out_of_week_tail]
        dupes = _duplicates(keys)

        if dupes:
            problems.append(f"Duplicate block keys: {', '.join(sorted(dupes))}.")

        return problems

    # per-year layout
    def _leap_delta(self, year: int, key: str) -> int:
        delta = 0
        for rule in self.leap_rules:
            if rule.matches(year):
                for adj in rule.adjustments:
                    if adj.target == key:
                        delta += adj.days

        return delta

    def segments(self, year: int) -> List[Segment]:
        """Ordered segments for ``year`` (leap adjustments applied)."""
        segs: List[Segment] = []

        def add_intercalary(after: int) -> None:
            for ic in self.intercalary:
                if ic.after_month == after:
                    days = ic.days + self._leap_delta(year, ic.key())
                    if days > 0:
                        segs.append(
                            Segment("intercalary", ic.name, ic.key(), days, ic.in_week)
                        )

        add_intercalary(0)

        for idx, m in enumerate(self.months, start=1):
            days = m.days + self._leap_delta(year, m.key())
            tail = (
                min(m.out_of_week_tail, max(days - 1, 0)) if m.out_of_week_tail else 0
            )
            head = days - tail

            if head > 0:
                segs.append(Segment("month", m.name, m.key(), head, True))

            if tail > 0:
                segs.append(
                    Segment(
                        "festival",
                        m.tail_name or f"{m.name} festival",
                        m.tail_key(),
                        tail,
                        False,
                    )
                )

            add_intercalary(idx)

        return segs

    def year_length(self, year: int) -> int:
        return sum(s.days for s in self.segments(year))

    def in_week_days_in_year(self, year: int) -> int:
        return sum(s.days for s in self.segments(year) if s.in_week)

    # year stepping
    def _year_after(self, year: int) -> int:
        if not self.has_year_zero:
            if year == -1:
                return 1
            if year == 0:
                return 1
        return year + 1

    def _year_before(self, year: int) -> int:
        if not self.has_year_zero:
            if year == 1:
                return -1
            if year == 0:
                return -1
        return year - 1

    def _years_forward(self, start: int) -> Iterable[int]:
        y = start
        while True:
            yield y
            y = self._year_after(y)

    # Convert ordinal <-> date
    def _days_before_year(self, year: int) -> int:
        """Ordinal of the first day of ``year`` (may be negative)."""
        if year == self.epoch_year:
            return 0

        total = 0
        if _year_gt(year, self.epoch_year, self.has_year_zero):
            y = self.epoch_year
            while y != year:
                total += self.year_length(y)
                y = self._year_after(y)
            return total

        else:
            y = year
            while y != self.epoch_year:
                total -= self.year_length(y)
                y = self._year_after(y)
            return total

    def date_to_ordinal(self, date: Date) -> int:
        segs = self.segments(date.year)
        offset = 0

        for s in segs:
            if s.key == date.block:
                if not (1 <= date.day <= s.days):
                    raise ValueError(
                        f"{date}: day {date.day} out of range 1..{s.days}."
                    )

                return self._days_before_year(date.year) + offset + (date.day - 1)

            offset += s.days

        raise ValueError(f"{date}: no block {date.block!r} in year {date.year}.")

    def ordinal_to_date(self, ordinal: int) -> Date:
        if ordinal >= 0:
            year = self.epoch_year

            while True:
                length = self.year_length(year)

                if ordinal < length:
                    break

                ordinal -= length
                year = self._year_after(year)

        else:
            year = self.epoch_year

            while ordinal < 0:
                year = self._year_before(year)
                ordinal += self.year_length(year)

        for s in self.segments(year):
            if ordinal < s.days:
                return Date(year, s.key, ordinal + 1)

            ordinal -= s.days

        raise AssertionError("ordinal_to_date() fell through")

    def _in_week_before_in_year(self, year: int, day_of_year0: int) -> int:
        """In-week days within ``year`` strictly before 0-based day_of_year0"""
        count = 0
        seen = 0

        for s in self.segments(year):
            for _ in range(s.days):
                if seen >= day_of_year0:
                    return count
                if s.in_week:
                    count += 1

                seen += 1

        return count

    def _is_in_week(self, year: int, day_of_year0: int) -> bool:
        seen = 0

        for s in self.segments(year):
            if seen + s.days > day_of_year0:
                return s.in_week

            seen += s.days

        raise ValueError("day_of_year out of range")

    def _in_week_before_ordinal(self, ordinal: int) -> int:
        """Count of in-week days in [0, ordinal)."""
        date = self.ordinal_to_date(ordinal)
        year = date.year

        total = 0
        if _year_gt(year, self.epoch_year, self.has_year_zero):
            y = self.epoch_year

            while y != year:
                total += self.in_week_days_in_year(y)
                y = self._year_after(y)

        elif _year_gt(self.epoch_year, year, self.has_year_zero):
            y = year

            while y != self.epoch_year:
                total -= self.in_week_days_in_year(y)
                y = self._year_after(y)

        day_of_year0 = ordinal - self._days_before_year(year)
        total += self._in_week_before_in_year(year, day_of_year0)

        return total

    def weekday_of_ordinal(self, ordinal: int) -> Optional[int]:
        date = self.ordinal_to_date(ordinal)
        doy0 = ordinal - self._days_before_year(date.year)

        if not self._is_in_week(date.year, doy0):
            return None

        return (
            self.start_weekday + self._in_week_before_ordinal(ordinal)
        ) % self.week.length

    def weekday_name_of_ordinal(self, ordinal: int) -> Optional[str]:
        idx = self.weekday_of_ordinal(ordinal)
        return None if idx is None else self.week.name_for(idx)

    def moon_phase_index(self, moon: Moon, ordinal: int, buckets: int = 8) -> int:
        frac = moon.phase_fraction(ordinal)
        return int(round(frac * buckets)) % buckets

    def moon_phase_name(self, moon: Moon, ordinal: int) -> str:
        return self.phase_names[
            self.moon_phase_index(moon, ordinal, len(self.phase_names))
        ]

    def moon_phases(self, ordinal: int) -> Dict[str, str]:
        return {m.name: self.moon_phase_name(m, ordinal) for m in self.moons}

    def new_year_weekday(self, year: int) -> Optional[int]:
        return self.weekday_of_ordinal(self._days_before_year(year))

    @property
    def on_world_timeline(self) -> bool:
        """True if this calendar is placed on the shared world axis."""
        return self.epoch_offset is not None

    def to_world_day(self, date: "Date") -> int:
        """The shared world-day number of a date in this calendar.

        world_day = ordinal (days from this calendar's own day 1) + epoch_offset
        (where this calendar's day 1 sits on the world axis).
        """
        if self.epoch_offset is None:
            raise ValueError(
                f"{self.name!r} is not on the world timeline (epoch_offset is None); "
                f"convert it with an explicit anchor via Converter instead."
            )

        return self.date_to_ordinal(date) + self.epoch_offset

    def from_world_day(self, world_day: int) -> "Date":
        """The date in this calendar that falls on a given shared world-day."""
        if self.epoch_offset is None:
            raise ValueError(
                f"{self.name!r} is not on the world timeline (epoch_offset is None)."
            )

        return self.ordinal_to_date(world_day - self.epoch_offset)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["schema_version"] = SCHEMA_VERSION
        return d

    def to_json(self, **kw) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, **kw)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_json())

    @classmethod
    def from_dict(cls, d: dict) -> "Calendar":
        d = dict(d)
        d.pop("schema_version", None)

        months = [Month(**m) for m in d.pop("months", [])]
        intercalary = [Intercalary(**i) for i in d.pop("intercalary", [])]
        week = Week(**d.pop("week")) if "week" in d else Week(7)
        moons = [Moon(**m) for m in d.pop("moons", [])]
        rules = []

        for r in d.pop("leap_rules", []):
            r = dict(r)
            adjustments = [Adjustment(**a) for a in r.pop("adjustments", [])]
            rules.append(LeapRule(adjustments=adjustments, **r))

        return cls(
            months=months,
            intercalary=intercalary,
            week=week,
            moons=moons,
            leap_rules=rules,
            **d,
        )

    @classmethod
    def load(cls, path: str) -> "Calendar":
        with open(path, encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))


class Converter:
    """Convert dates between two calendars by anchoring one shared real day.

    ``anchor_a`` (a date in calendar ``a``) and ``anchor_b`` (a date in calendar
    ``b``) must name the *same real day*. From that single correspondence every
    other day lines up, because equal real-day counts from the anchor must match.
    """

    def __init__(self, a: Calendar, b: Calendar, anchor_a: Date, anchor_b: Date):
        self.a, self.b = a, b
        self._oa = a.date_to_ordinal(anchor_a)
        self._ob = b.date_to_ordinal(anchor_b)

    def a_to_b(self, date: Date) -> Date:
        real_days_from_anchor = self.a.date_to_ordinal(date) - self._oa
        return self.b.ordinal_to_date(self._ob + real_days_from_anchor)

    def b_to_a(self, date: Date) -> Date:
        real_days_from_anchor = self.b.date_to_ordinal(date) - self._ob
        return self.a.ordinal_to_date(self._oa + real_days_from_anchor)

    def days_between(self, date_a: Date, date_b: Date) -> int:
        """Real days from ``date_a`` (in a) to ``date_b`` (in b); signed."""
        ra = self.a.date_to_ordinal(date_a) - self._oa
        rb = self.b.date_to_ordinal(date_b) - self._ob
        return rb - ra


def convert(date: "Date", src: "Calendar", dst: "Calendar") -> "Date":
    """Convert a date from ``src`` to ``dst`` through the shared world axis.

    Requires both calendars to be on the world timeline (``epoch_offset`` set).
    This composes: any on-timeline calendar converts to any other with no
    per-pair anchor, because they all measure days from the same world-day 0.
    For a calendar that is *off* the timeline (e.g. the Gregorian reference),
    use :class:`Converter` with an explicit shared anchor instead.
    """
    if not src.on_world_timeline or not dst.on_world_timeline:
        off = src.name if not src.on_world_timeline else dst.name
        raise ValueError(
            f"{off!r} is not on the world timeline; use Converter with an explicit "
            f"anchor to convert it."
        )
    return dst.from_world_day(src.to_world_day(date))


def _duplicates(items: List[str]) -> set:
    seen, dupes = set(), set()
    for x in items:
        if x in seen:
            dupes.add(x)
        seen.add(x)
    return dupes


def _year_gt(a: int, b: int, has_year_zero: bool) -> bool:
    """Is year ``a`` later than year ``b``, honouring a possible missing year 0?"""
    return _year_to_line(a, has_year_zero) > _year_to_line(b, has_year_zero)


def _year_to_line(year: int, has_year_zero: bool) -> int:
    """Map a year number onto a gap-free integer line for ordering."""
    if has_year_zero or year > 0:
        return year
    return year + 1  # collapse the missing 0 so -1 sits just below +1
