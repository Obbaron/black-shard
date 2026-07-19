"""
fcal.world - world's calendars and shared timeline

A single JSON index, ``data/world.json``, names the calendars belonging to the
world and records the anchor: which calendar's day 1 is world-day 0. Each calendar
carries its own ``epoch_offset`` (its day 1 as a world-day number), so once they are
all on the axis, any calendar converts to any other with no per-pair anchor.

    from fcal.world import World
    world = World.load()
    world.convert(Date(812, "m01", 1), "yavanna", "old_yavanna")   # once both exist

The index does not duplicate the offsets; those live authoritatively in each
calendar file. ``World.load`` validates the anchor calendar's offset matches the
declared world-day (0 by default).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from . import paths
from .engine import Calendar, Date
from .engine import convert as _convert

INDEX_NAME = "world.json"


@dataclass
class CalendarEntry:
    name: str
    file: str
    status: str = "canon"  # canon | historical | regional | reference | draft
    note: str = ""


@dataclass
class World:
    anchor_calendar: str
    anchor_world_day: int = 0
    anchor_description: str = ""
    entries: List[CalendarEntry] = field(default_factory=list)
    calendars: Dict[str, Calendar] = field(default_factory=dict)

    @classmethod
    def load(cls, index_path: Optional[Path] = None) -> "World":
        index_path = Path(index_path) if index_path else (paths.DATA_DIR / INDEX_NAME)

        with open(index_path, encoding="utf-8") as fh:
            d = json.load(fh)

        anchor = d.get("anchor", {})
        entries = [CalendarEntry(**e) for e in d.get("calendars", [])]

        base = index_path.parent
        calendars: Dict[str, Calendar] = {}
        for e in entries:
            calendars[e.name] = Calendar.load(str(base / e.file))

        world = cls(
            anchor_calendar=anchor.get("calendar", ""),
            anchor_world_day=anchor.get("world_day", 0),
            anchor_description=anchor.get("description", ""),
            entries=entries,
            calendars=calendars,
        )

        world._validate()

        return world

    def _validate(self) -> None:
        problems = self.problems()
        if problems:
            raise ValueError("world index invalid:\n  - " + "\n  - ".join(problems))

    def problems(self) -> List[str]:
        out: List[str] = []

        if self.anchor_calendar not in self.calendars:
            out.append(f"anchor calendar {self.anchor_calendar!r} is not in the index")
            return out

        anchor = self.calendars[self.anchor_calendar]
        if anchor.epoch_offset != self.anchor_world_day:
            out.append(
                f"anchor {self.anchor_calendar!r} has epoch_offset "
                f"{anchor.epoch_offset!r}, but the index says world-day "
                f"{self.anchor_world_day!r}; they must agree"
            )

        for name, cal in self.calendars.items():
            status = self.status(name)
            if status != "reference" and not cal.on_world_timeline:
                out.append(
                    f"{name!r} is status {status!r} but has no epoch_offset "
                    f"(it is not placed on the world timeline)"
                )

        return out

    def status(self, name: str) -> str:
        for e in self.entries:
            if e.name == name:
                return e.status

        return ""

    def convert(self, date: Date, src: str, dst: str) -> Date:
        """Convert a date between two registered calendars via the world axis."""
        return _convert(date, self.calendars[src], self.calendars[dst])

    def to_world_day(self, date: Date, calendar: str) -> int:
        return self.calendars[calendar].to_world_day(date)

    def from_world_day(self, world_day: int, calendar: str) -> Date:
        return self.calendars[calendar].from_world_day(world_day)
