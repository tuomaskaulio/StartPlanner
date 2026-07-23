"""Scheduler parallel-start and first-control tests."""

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
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService


def _parallel_competition() -> Competition:
    c = Competition(name="Parallel")
    c.ensure_default_start_location()
    c.add_course(Course(id="cA", name="A", length_m=5000, controls=["31", "32"]))
    c.add_course(Course(id="cB", name="B", length_m=4000, controls=["40", "41"]))
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
    c.add_competitor(Competitor(id="2", first_name="B", last_name="Two", class_id="d21"))
    return c


def test_different_first_controls_can_start_same_minute():
    c = _parallel_competition()
    plan = SchedulerService().apply(c)
    h = plan.entry_for_class("h21")
    d = plan.entry_for_class("d21")
    assert h is not None and d is not None
    report = ValidationService().validate(c, require_plan=True)
    assert not any(i.rule_id.startswith("plan.") for i in report.errors)


def test_balanced_flow_spreads_short_classes():
    c = _parallel_competition()
    plan = SchedulerService().apply(c)
    h = plan.entry_for_class("h21")
    d = plan.entry_for_class("d21")
    assert h is not None and d is not None
    # Different first controls may share a minute within the bottleneck window.
    assert h.first_start_time == c.competition_start_datetime()
    assert d.first_start_time >= c.competition_start_datetime()
    report = ValidationService().validate(c, require_plan=True)
    assert not any(i.rule_id.startswith("plan.") for i in report.errors)


def test_same_first_control_staggered_by_minute():
    c = _parallel_competition()
    c.courses["cB"] = Course(id="cB", name="B", length_m=4000, controls=["31", "41"])
    plan = SchedulerService().apply(c)
    h = plan.entry_for_class("h21")
    d = plan.entry_for_class("d21")
    assert h is not None and d is not None
    assert d.first_start_time == h.first_start_time + __import__("datetime").timedelta(
        minutes=1
    )
    report = ValidationService().validate(c, require_plan=True)
    assert not any(i.rule_id.startswith("plan.") for i in report.errors)


def test_same_course_classes_are_sequential():
    c = _parallel_competition()
    c.add_class(
        RaceClass(
            id="h20",
            name="H20",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=2,
        )
    )
    c.add_competitor(Competitor(id="3", first_name="C", last_name="Three", class_id="h20"))
    plan = SchedulerService().apply(c)
    on_a = [
        e
        for e in plan.entries
        if c.classes[e.class_id].course_id == "cA"
    ]
    assert len(on_a) == 2
    ordered = sorted(on_a, key=lambda e: e.first_start_time)
    first_end = c.class_span_end(c.classes[ordered[0].class_id], ordered[0].first_start_time)
    gap = c.settings.class_gap_min
    assert ordered[1].first_start_time >= first_end + __import__(
        "datetime"
    ).timedelta(minutes=gap)
    report = ValidationService().validate(c, require_plan=True)
    assert not any(i.rule_id == "plan.course_interleave" for i in report.errors)


def test_sample_small_even_flow():
    from pathlib import Path

    from startplanner.services.import_service import ImportService

    root = Path(__file__).resolve().parents[1] / "samples" / "sample-small"
    imp = ImportService()
    c = imp.import_coursedata(next(root.glob("*_coursedata.xml")))
    imp.import_entries(c, root / "ilmoittautumiset.csv")
    plan = SchedulerService().apply(c)
    times = [e.first_start_time for e in plan.sorted_entries()]
    minutes = {t.minute for t in times}
    assert any(m % 2 == 1 for m in minutes), "expected some odd-minute class starts"
    report = ValidationService().validate(c, require_plan=True)
    assert not any(i.rule_id.startswith("plan.") for i in report.errors)
