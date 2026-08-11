"""Ruudukko-välilehden värit ja sarakeleveys (v0.9.3).

Kaksi asiaa korjattu/lisätty:
1. Viimeinen sarake ei enää veny muita leveämmäksi (setStretchLastSection
   poistettu) — kaikki ratasarakkeet ovat nyt samanlevyisiä.
2. Sarakkeen tausta on sama kaikilla saman 1. rastin radoilla (auttaa
   hahmottamaan lähtökonfliktit), ja jokaisella sarjalla on oma,
   koko ruudukon läpi identtinen, ei-liian-tumma soluväri.
"""

from __future__ import annotations

import os
from datetime import datetime

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from startplanner.domain import (  # noqa: E402
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
    StartLocation,
)
from startplanner.gui.main_window import MainWindow  # noqa: E402


def _qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


def _grid_competition() -> tuple[Competition, ClassStartPlan]:
    """Two courses sharing first control '31' (A, B) and one on '40' (C),
    timed so some minutes have an occupied cell in only one of A/B while the
    other is empty — needed to check empty-cell column tinting."""
    c = Competition(name="Ruudukkotesti")
    loc = StartLocation(id="start:default", name="Lähtö 1")
    c.add_start_location(loc)
    course_a = Course(id="course:a", name="Rata A", controls=["31", "32"])
    course_b = Course(id="course:b", name="Rata B", controls=["31", "33"])
    course_c = Course(id="course:c", name="Rata C", controls=["40"])
    for course in (course_a, course_b, course_c):
        c.add_course(course)

    rc_a = RaceClass(
        id="class:a", name="H21", course_id="course:a",
        start_location_id=loc.id, start_interval_min=1,
    )
    rc_b = RaceClass(
        id="class:b", name="H35", course_id="course:b",
        start_location_id=loc.id, start_interval_min=1,
    )
    rc_c = RaceClass(
        id="class:c", name="H45", course_id="course:c",
        start_location_id=loc.id, start_interval_min=1,
    )
    for rc in (rc_a, rc_b, rc_c):
        c.add_class(rc)

    c.add_competitor(Competitor(id="a1", first_name="A", last_name="1", class_id="class:a"))
    c.add_competitor(Competitor(id="a2", first_name="A", last_name="2", class_id="class:a"))
    c.add_competitor(Competitor(id="b1", first_name="B", last_name="1", class_id="class:b"))
    c.add_competitor(Competitor(id="c1", first_name="C", last_name="1", class_id="class:c"))

    t0 = datetime(2026, 8, 15, 12, 0)
    plan = ClassStartPlan(
        start_location_id=loc.id,
        entries=[
            ClassStart(id="s1", class_id="class:a", first_start_time=t0),  # 12:00, 12:01
            ClassStart(id="s2", class_id="class:b", first_start_time=t0.replace(minute=5)),  # 12:05
            ClassStart(id="s3", class_id="class:c", first_start_time=t0),  # 12:00
        ],
    )
    return c, plan


def test_column_group_palette_distinct_and_light():
    colors = MainWindow._column_group_palette(5)
    assert len(colors) == 5
    assert len({(col.red(), col.green(), col.blue()) for col in colors}) == 5
    assert all(col.lightness() >= 180 for col in colors)


def test_class_color_palette_distinct_and_light():
    colors = MainWindow._class_color_palette(6)
    assert len(colors) == 6
    assert len({(col.red(), col.green(), col.blue()) for col in colors}) == 6
    assert all(col.lightness() >= 180 for col in colors)


def test_palettes_empty_for_zero_or_negative():
    assert MainWindow._column_group_palette(0) == []
    assert MainWindow._class_color_palette(-1) == []


def test_grid_columns_are_equal_width():
    _qapp()
    window = MainWindow()
    competition, plan = _grid_competition()
    window._competition = competition
    window._active_location_id = "start:default"
    window._refresh_course_grid(plan)

    table = window._grid_table
    assert table.columnCount() == 5  # Aika, Yht, Rata A, Rata B, Rata C
    course_widths = {table.columnWidth(i) for i in range(2, 5)}
    assert len(course_widths) == 1, "ratasarakkeiden tulisi olla samanlevyisiä"


def test_grid_same_first_control_shares_column_color_on_empty_cells():
    _qapp()
    window = MainWindow()
    competition, plan = _grid_competition()
    window._competition = competition
    window._active_location_id = "start:default"
    window._refresh_course_grid(plan)

    table = window._grid_table
    # Row order: 12:00, 12:01, 12:02, 12:03, 12:04, 12:05
    empty_row = 2  # 12:02: Rata A/B/C all empty at this minute
    color_a = table.item(empty_row, 2).background().color()
    color_b = table.item(empty_row, 3).background().color()
    color_c = table.item(empty_row, 4).background().color()

    assert table.item(empty_row, 2).text() == ""
    assert table.item(empty_row, 3).text() == ""
    assert color_a == color_b, "Rata A ja B jakavat 1. rastin '31' -> sama pohjaväri"
    assert color_a != color_c, "Rata C:n 1. rasti '40' eroaa -> eri pohjaväri"


def test_grid_class_color_is_consistent_and_distinct():
    _qapp()
    window = MainWindow()
    competition, plan = _grid_competition()
    window._competition = competition
    window._active_location_id = "start:default"
    window._refresh_course_grid(plan)

    table = window._grid_table
    # Row 0 = 12:00 (H21 @ Rata A, H45 @ Rata C both start here).
    # Row 1 = 12:01 (H21's second competitor, same class as row 0).
    h21_row0 = table.item(0, 2)
    h21_row1 = table.item(1, 2)
    h45_row0 = table.item(0, 4)

    assert h21_row0.text() == "H21"
    assert h21_row1.text() == "H21"
    assert h45_row0.text() == "H45"

    assert h21_row0.background().color() == h21_row1.background().color(), (
        "saman sarjan väri pysyy samana joka esiintymässä"
    )
    assert h21_row0.background().color() != h45_row0.background().color(), (
        "eri sarjoilla pitää olla eri väri"
    )
