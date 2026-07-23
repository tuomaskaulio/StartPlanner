"""Tests for course-column grid builder."""

from datetime import datetime

from startplanner.domain import (
    DEFAULT_START_LOCATION_ID,
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
)
from startplanner.gui.course_grid import build_course_grid


def _mini_plan() -> tuple[Competition, ClassStartPlan]:
    c = Competition(name="T")
    c.ensure_default_start_location()
    c.add_course(Course(id="c1", name="HD21", controls=["58", "59"]))
    c.add_course(Course(id="c2", name="HD12", controls=["64", "65"]))
    c.add_class(
        RaceClass(
            id="h21",
            name="H21",
            course_id="c1",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=2,
        )
    )
    c.add_class(
        RaceClass(
            id="d12",
            name="D12",
            course_id="c2",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=2,
        )
    )
    c.add_competitor(Competitor(id="1", first_name="A", last_name="B", class_id="h21"))
    c.add_competitor(Competitor(id="2", first_name="C", last_name="D", class_id="h21"))
    c.add_competitor(Competitor(id="3", first_name="E", last_name="F", class_id="d12"))
    t = datetime(2026, 7, 23, 12, 0)
    plan = ClassStartPlan(
        start_location_id=DEFAULT_START_LOCATION_ID,
        entries=[
            ClassStart("1", "h21", t),
            ClassStart("2", "d12", t),
        ],
    )
    return c, plan


def test_build_course_grid_columns_and_cells():
    c, plan = _mini_plan()
    grid = build_course_grid(c, plan)
    assert len(grid.columns) == 2
    assert grid.columns[0].first_control == "58"
    assert grid.columns[1].first_control == "64"
    assert grid.total(datetime(2026, 7, 23, 12, 0)) == 2
    assert grid.cell(datetime(2026, 7, 23, 12, 0), "c1") == "H21"
    assert grid.cell(datetime(2026, 7, 23, 12, 2), "c1") == "H21"
    assert grid.cell(datetime(2026, 7, 23, 12, 0), "c2") == "D12"


def test_build_course_grid_empty_plan():
    c, _ = _mini_plan()
    grid = build_course_grid(c, None)
    assert grid.minutes == []
    assert grid.columns == []
