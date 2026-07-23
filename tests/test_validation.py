"""Validation tests."""

from datetime import datetime

from startplanner.domain import Competition, Competitor, Course, RaceClass, Start, StartSchedule
from startplanner.services.validation_service import ValidationService
from startplanner.validation.issues import Severity


def _base() -> Competition:
    c = Competition(name="Test")
    c.add_course(Course(id="cA", name="A", length_m=5000, controls=["31", "32"]))
    c.add_course(Course(id="cB", name="B", length_m=4000, controls=["31", "40"]))
    c.add_class(RaceClass(id="h21", name="H21", course_id="cA", start_interval_min=2))
    c.add_class(RaceClass(id="d21", name="D21", course_id="cB", start_interval_min=2))
    c.add_competitor(Competitor(id="1", first_name="A", last_name="One", class_id="h21"))
    c.add_competitor(Competitor(id="2", first_name="B", last_name="Two", class_id="h21"))
    c.add_competitor(Competitor(id="3", first_name="C", last_name="Three", class_id="d21"))
    return c


def test_missing_course_is_error():
    c = _base()
    c.classes["h21"].course_id = None
    report = ValidationService().validate(c)
    assert any(i.rule_id == "class.course" and i.severity is Severity.ERROR for i in report.issues)


def test_first_control_conflict():
    c = _base()
    t = datetime(2025, 1, 1, 12, 0)
    c.schedule = StartSchedule(
        starts=[
            Start("s1", "1", "h21", "cA", t, 1),
            Start("s2", "3", "d21", "cB", t, 2),
        ]
    )
    report = ValidationService().validate(c, require_schedule=True)
    assert any(i.rule_id == "schedule.first_control" for i in report.errors)


def test_interval_violation():
    c = _base()
    t0 = datetime(2025, 1, 1, 12, 0)
    t1 = datetime(2025, 1, 1, 12, 1)
    c.schedule = StartSchedule(
        starts=[
            Start("s1", "1", "h21", "cA", t0, 1),
            Start("s2", "2", "h21", "cA", t1, 2),
            Start("s3", "3", "d21", "cB", datetime(2025, 1, 1, 12, 2), 3),
        ]
    )
    report = ValidationService().validate(c, require_schedule=True)
    assert any(i.rule_id == "schedule.interval" for i in report.errors)


def test_course_interleave():
    c = _base()
    c.classes["d21"].course_id = "cA"
    c.schedule = StartSchedule(
        starts=[
            Start("s1", "1", "h21", "cA", datetime(2025, 1, 1, 12, 0), 1),
            Start("s2", "3", "d21", "cA", datetime(2025, 1, 1, 12, 1), 2),
            Start("s3", "2", "h21", "cA", datetime(2025, 1, 1, 12, 2), 3),
        ]
    )
    report = ValidationService().validate(c, require_schedule=True)
    assert any(i.rule_id == "schedule.course_interleave" for i in report.errors)
