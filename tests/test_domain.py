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


def test_start_datetime_for_location_override():
    c = Competition(name="X")
    c.settings.competition_start = time(12, 0)
    c.ensure_default_start_location()
    loc = c.start_locations[DEFAULT_START_LOCATION_ID]
    assert c.start_datetime_for(loc.id).hour == 12
    loc.first_start = time(9, 15)
    assert c.start_datetime_for(loc.id).hour == 9
    assert c.start_datetime_for(loc.id).minute == 15


def test_sorted_entries_by_class_order():
    plan = ClassStartPlan(
        start_location_id="start:default",
        entries=[
            ClassStart(
                id="e1",
                class_id="b",
                first_start_time=datetime(2025, 1, 1, 12, 0),
            ),
            ClassStart(
                id="e2",
                class_id="a",
                first_start_time=datetime(2025, 1, 1, 12, 10),
            ),
        ],
    )
    orders = {"a": 1, "b": 2}
    names = {"a": "A", "b": "B"}
    by_class = plan.sorted_entries(
        by="class", class_sort_order=orders, class_names=names
    )
    assert [e.class_id for e in by_class] == ["a", "b"]
    by_time = plan.sorted_entries(
        by="time", class_sort_order=orders, class_names=names
    )
    assert [e.class_id for e in by_time] == ["b", "a"]


def test_competitor_count():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    c.add_competitor(Competitor(id="a", first_name="A", last_name="B", class_id="1"))
    assert c.competitor_count("1") == 1
