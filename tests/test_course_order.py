"""Course-order (within-course start sequence) tests."""

from datetime import timedelta
from pathlib import Path

from startplanner.domain import (
    DEFAULT_START_LOCATION_ID,
    Competition,
    Competitor,
    Course,
    RaceClass,
)
from startplanner.services.class_service import ClassService
from startplanner.services.competition_service import CompetitionService
from startplanner.services.scheduler_service import SchedulerService

ROOT = Path(__file__).resolve().parents[1]


def _same_course_competition() -> Competition:
    c = Competition(name="CourseOrder")
    c.ensure_default_start_location()
    c.settings.class_gap_min = 2
    c.add_course(Course(id="cA", name="A", length_m=5000, controls=["31"]))
    c.add_class(
        RaceClass(
            id="long",
            name="H21",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=1,
            course_order=1,
        )
    )
    c.add_class(
        RaceClass(
            id="short",
            name="H12",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=1,
            course_order=0,
        )
    )
    for i in range(5):
        c.add_competitor(
            Competitor(
                id=f"l{i}",
                first_name="L",
                last_name=str(i),
                class_id="long",
            )
        )
    c.add_competitor(
        Competitor(id="s0", first_name="S", last_name="0", class_id="short")
    )
    return c


def test_scheduler_places_same_course_by_course_order():
    c = _same_course_competition()
    plan = SchedulerService().apply(c)
    short = plan.entry_for_class("short")
    long = plan.entry_for_class("long")
    assert short is not None and long is not None
    # Short has course_order 0 → starts before long despite shorter stream.
    assert short.first_start_time < long.first_start_time
    gap = c.settings.class_gap_min
    short_end = c.class_span_end(c.classes["short"], short.first_start_time)
    assert long.first_start_time >= short_end + timedelta(minutes=gap)


def test_reorder_course_classes_and_spc_roundtrip(tmp_path: Path):
    c = _same_course_competition()
    ClassService().reorder_course_classes(c, "cA", ["long", "short"])
    assert c.classes["long"].course_order == 0
    assert c.classes["short"].course_order == 1

    path = tmp_path / "co.spc"
    CompetitionService().save(c, path)
    loaded = CompetitionService().load(path)
    assert loaded.classes["long"].course_order == 0
    assert loaded.classes["short"].course_order == 1

    plan = SchedulerService().apply(loaded)
    long = plan.entry_for_class("long")
    short = plan.entry_for_class("short")
    assert long is not None and short is not None
    assert long.first_start_time < short.first_start_time
