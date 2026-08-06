"""Validation tests for ClassStartPlan."""

from datetime import datetime

from startplanner.domain import (
    DEFAULT_START_LOCATION_ID,
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
    StartLocation,
)
from startplanner.services.validation_service import ValidationService
from startplanner.validation.issues import Severity


def _base() -> Competition:
    c = Competition(name="Test")
    c.ensure_default_start_location()
    c.add_course(Course(id="cA", name="A", length_m=5000, controls=["31", "32"]))
    c.add_course(Course(id="cB", name="B", length_m=4000, controls=["31", "40"]))
    c.add_class(
        RaceClass(
            id="h21",
            name="H21",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=2,
        )
    )
    c.add_class(
        RaceClass(
            id="d21",
            name="D21",
            course_id="cB",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=2,
        )
    )
    c.add_competitor(Competitor(id="1", first_name="A", last_name="One", class_id="h21"))
    c.add_competitor(Competitor(id="2", first_name="B", last_name="Two", class_id="h21"))
    c.add_competitor(Competitor(id="3", first_name="C", last_name="Three", class_id="d21"))
    return c


def test_missing_course_is_error():
    c = _base()
    c.classes["h21"].course_id = None
    report = ValidationService().validate(c)
    assert any(i.rule_id == "class.course" and i.severity is Severity.ERROR for i in report.issues)


def test_first_control_conflict_in_plan():
    c = _base()
    t = datetime(2025, 1, 1, 12, 0)
    c.set_plan(
        ClassStartPlan(
            start_location_id=DEFAULT_START_LOCATION_ID,
            entries=[
                ClassStart("s1", "h21", t),
                ClassStart("s2", "d21", t),
            ],
        )
    )
    report = ValidationService().validate(c, require_plan=True)
    assert any(i.rule_id == "plan.first_control" for i in report.errors)


def test_course_interleave_in_plan():
    c = _base()
    c.classes["d21"].course_id = "cA"
    c.set_plan(
        ClassStartPlan(
            start_location_id=DEFAULT_START_LOCATION_ID,
            entries=[
                ClassStart("s1", "h21", datetime(2025, 1, 1, 12, 0)),
                # H21 has 2 competitors @ 2 min → spans 12:00-12:02
                ClassStart("s2", "d21", datetime(2025, 1, 1, 12, 1)),
            ],
        )
    )
    report = ValidationService().validate(c, require_plan=True)
    assert any(i.rule_id == "plan.course_interleave" for i in report.errors)


def test_next_day_start_is_warning():
    from datetime import date

    c = _base()
    c.event_date = date(2025, 1, 1)
    c.set_plan(
        ClassStartPlan(
            start_location_id=DEFAULT_START_LOCATION_ID,
            entries=[
                ClassStart("s1", "h21", datetime(2025, 1, 1, 12, 0)),
                ClassStart("s2", "d21", datetime(2025, 1, 2, 0, 15)),
            ],
        )
    )
    report = ValidationService().validate(c, require_plan=True)
    assert any(i.rule_id == "plan.next_day" for i in report.warnings)
    assert not any(i.rule_id == "plan.next_day" for i in report.errors)


def test_separate_locations_allow_same_first_control_minute():
    c = _base()
    c.add_start_location(StartLocation(id="start:2", name="Lähtö 2"))
    c.classes["d21"].start_location_id = "start:2"
    t = datetime(2025, 1, 1, 12, 0)
    c.set_plan(
        ClassStartPlan(
            start_location_id=DEFAULT_START_LOCATION_ID,
            entries=[ClassStart("s1", "h21", t)],
        )
    )
    c.set_plan(
        ClassStartPlan(
            start_location_id="start:2",
            entries=[ClassStart("s2", "d21", t)],
        )
    )
    report = ValidationService().validate(c, require_plan=True)
    assert not any(i.rule_id == "plan.first_control" for i in report.errors)
