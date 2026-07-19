"""
fcal - fantasy-calendar engine

Usage:
    from fcal import Calendar, Date, Converter, render_year_html

    yav = Calendar.load("data/canon/yavanna.json")
    html = render_year_html(yav, 812)
"""

from . import paths
from .engine import (
    Adjustment,
    Calendar,
    Converter,
    Date,
    Intercalary,
    LeapRule,
    Month,
    Moon,
    Segment,
    Week,
    convert,
)
from .render import render_year_html, render_year_text
from .world import World

__all__ = [
    "Month",
    "Intercalary",
    "Week",
    "Moon",
    "Adjustment",
    "LeapRule",
    "Segment",
    "Date",
    "Calendar",
    "Converter",
    "convert",
    "render_year_html",
    "render_year_text",
    "World",
    "paths",
]

__version__ = "0.1.0"
