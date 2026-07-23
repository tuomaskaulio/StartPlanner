"""Domain unit tests."""

from datetime import datetime, time

from startplanner.domain import (
    DEFAULT_START_LOCATION_ID,
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
)


def test_empty_competition():
    c = Competition()
    assert len(c.classes) == 0
    assert len(c.competitors) == 0


def test_default_start_location_on_add_class():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    assert DEFAULT_START_LOCATION_ID in c.start_locations
    assert c.classes["1"].start_location_id == DEFAULT_START_LOCATION_ID


def test_first_control_from_controls():
    course = Course(id="c1", name="A", controls=["59", "40", "M"])
    assert course.first_control == "59"


def test_class_start_plan():
    plan = ClassStartPlan(
        start_location_id="start:default",
        entries=[
            ClassStart(
                id="e1",
                class_id="h21",
                first_start_time=datetime(2025, 1, 1, 12, 0),
            )
        ],
    )
    assert len(plan) == 1
    assert plan.entry_for_class("h21") is not None


def test_competition_start_datetime_uses_settings():
    c = Competition(name="X")
    c.settings.competition_start = time(10, 30)
    dt = c.competition_start_datetime()
    assert dt.hour == 10 and dt.minute == 30


def test_competitor_count():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    c.add_competitor(Competitor(id="a", first_name="A", last_name="B", class_id="1"))
    assert c.competitor_count("1") == 1
