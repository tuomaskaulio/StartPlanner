"""Even flow distribution tests."""

from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from startplanner.domain import (
    DEFAULT_START_LOCATION_ID,
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
)
from startplanner.services.class_service import ClassService
from startplanner.services.import_service import ImportService
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MEDIUM = ROOT / "samples" / "sample-medium"


def test_target_load_uses_inclusive_window_minutes():
    start = datetime(2026, 7, 23, 12, 0)
    end = datetime(2026, 7, 23, 12, 9)
    assert SchedulerService._target_load(25, start, end) == 2.5


def test_candidate_times_group_two_minute_phases():
    start = datetime(2026, 7, 23, 12, 0)
    end = datetime(2026, 7, 23, 12, 5)
    candidates = SchedulerService._candidate_times(
        start, end, interval_min=2, phased=True
    )
    assert [t.minute for t in candidates] == [0, 2, 4, 1, 3, 5]


def test_load_score_prefers_underloaded_two_minute_phase():
    start = datetime(2026, 7, 23, 12, 0)
    end = datetime(2026, 7, 23, 12, 3)
    minute_load = {
        start: 3,
        start + timedelta(minutes=1): 1,
        start + timedelta(minutes=2): 3,
        start + timedelta(minutes=3): 1,
    }
    even = SchedulerService._placement_flow_score(
        start,
        count=2,
        interval_min=2,
        minute_load=minute_load,
        target_load=2.0,
        window_start=start,
        window_end=end,
    )
    odd = SchedulerService._placement_flow_score(
        start + timedelta(minutes=1),
        count=2,
        interval_min=2,
        minute_load=minute_load,
        target_load=2.0,
        window_start=start,
        window_end=end,
    )
    assert odd < even


def test_load_score_compares_improvement_from_current_load():
    start = datetime(2026, 7, 23, 12, 0)
    end = start + timedelta(minutes=1)
    minute_load = {start + timedelta(minutes=1): 1}
    empty_minute = SchedulerService._placement_flow_score(
        start,
        count=1,
        interval_min=1,
        minute_load=minute_load,
        target_load=2.5,
        window_start=start,
        window_end=end,
    )
    partly_loaded = SchedulerService._placement_flow_score(
        start + timedelta(minutes=1),
        count=1,
        interval_min=1,
        minute_load=minute_load,
        target_load=2.5,
        window_start=start,
        window_end=end,
    )
    assert empty_minute < partly_loaded


def _medium_competition():
    imp = ImportService()
    xmls = sorted(SAMPLE_MEDIUM.glob("*_coursedata.xml"))
    c = imp.import_coursedata(xmls[0])
    imp.import_coursedata(xmls[1], c)
    imp.import_entries(c, SAMPLE_MEDIUM / "ilmoittautumiset.csv")
    for rc in c.classes.values():
        if not rc.course_id:
            ClassService().assign_course(c, rc.id, next(iter(c.courses)))
    return c


def _medium_scheduled():
    c = _medium_competition()
    plan = SchedulerService().apply(c)
    return c, plan


def _minute_load(competition, plan):
    per_min: dict = defaultdict(int)
    for entry in plan.entries:
        rc = competition.classes[entry.class_id]
        n = max(competition.competitor_count(rc.id), 1)
        for i in range(n):
            m = (
                entry.first_start_time
                + timedelta(minutes=i * rc.start_interval_min)
            ).replace(second=0, microsecond=0)
            per_min[m] += 1
    return per_min


def _all_start_minutes(competition, plan):
    times = []
    for entry in plan.entries:
        rc = competition.classes[entry.class_id]
        n = max(competition.competitor_count(rc.id), 1)
        for i in range(n):
            times.append(
                (
                    entry.first_start_time
                    + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
            )
    return times


def test_bottleneck_course_identified():
    c = _medium_competition()
    loc = next(iter(c.start_locations))
    sched = SchedulerService()
    classes = sched._ordered_classes(c, loc)
    durations = sched._course_durations(c, classes)
    bottleneck_id = sched._bottleneck_course_id(c, durations)
    assert bottleneck_id is not None
    assert c.courses[bottleneck_id].name == "D35 D40 D45 H60 H65 H16"


def test_medium_overall_span_near_bottleneck():
    c, plan = _medium_scheduled()
    loc = next(iter(c.start_locations))
    sched = SchedulerService()
    classes = sched._ordered_classes(c, loc)
    durations = sched._course_durations(c, classes)
    start = c.competition_start_datetime()
    window_end = sched._schedule_window_end(start, durations)
    times = _all_start_minutes(c, plan)
    overall_span = int((max(times) - min(times)).total_seconds() // 60) + 1
    bottleneck_span = int((window_end - start).total_seconds() // 60) + 1
    assert overall_span <= bottleneck_span + 2


def test_no_starts_long_after_bottleneck():
    c, plan = _medium_scheduled()
    loc = next(iter(c.start_locations))
    sched = SchedulerService()
    classes = sched._ordered_classes(c, loc)
    durations = sched._course_durations(c, classes)
    start = c.competition_start_datetime()
    window_end = sched._schedule_window_end(start, durations)
    times = _all_start_minutes(c, plan)
    late = [t for t in times if t > window_end + timedelta(minutes=2)]
    assert late == []
    report = ValidationService().validate(c, require_plan=True)
    assert not any(i.rule_id.startswith("plan.") for i in report.errors)


def test_medium_sample_load_is_balanced():
    c, plan = _medium_scheduled()
    loads = list(_minute_load(c, plan).values())
    assert max(loads) <= 6
    avg = sum(loads) / len(loads)
    variance = sum((x - avg) ** 2 for x in loads) / len(loads)
    assert variance < 3.0


def test_extended_window_is_filled_evenly():
    """When schedule reaches the fill window, late minutes should not be empty-only."""
    c, plan = _medium_scheduled()
    per_min = _minute_load(c, plan)
    t0 = min(per_min)
    t1 = max(per_min)
    empty = 0
    t = t0
    while t <= t1:
        if t not in per_min:
            empty += 1
        t += timedelta(minutes=1)
    # Allow a couple of gaps from 2-min intervals, but not a sparse tail.
    assert empty <= 3
    late_half_start = t0 + (t1 - t0) / 2
    late_loads = [per_min[m] for m in per_min if m >= late_half_start]
    assert late_loads
    assert max(late_loads) <= 6
    assert sum(late_loads) / len(late_loads) >= 1.0


def test_overflow_window_rebalances_deterministically():
    c = Competition(name="Overflow")
    c.ensure_default_start_location()
    for course_id in ("a", "b", "c"):
        c.add_course(
            Course(
                id=course_id,
                name=course_id.upper(),
                controls=["31", f"{course_id}2"],
            )
        )
        rc = RaceClass(
            id=f"class:{course_id}",
            name=course_id.upper(),
            course_id=course_id,
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=2,
        )
        c.add_class(rc)
        for i in range(3):
            c.add_competitor(
                Competitor(
                    id=f"{course_id}:{i}",
                    first_name="Test",
                    last_name=f"{course_id}{i}",
                    class_id=rc.id,
                )
            )

    scheduler = SchedulerService()
    classes = scheduler._ordered_classes(c, DEFAULT_START_LOCATION_ID)
    estimated_end = scheduler._schedule_window_end(
        c.competition_start_datetime(),
        scheduler._course_durations(c, classes),
    )
    first = scheduler.build(c)
    second = scheduler.build(c)

    first_times = [
        (entry.class_id, entry.first_start_time) for entry in first.sorted_entries()
    ]
    second_times = [
        (entry.class_id, entry.first_start_time) for entry in second.sorted_entries()
    ]
    assert first_times == second_times

    actual_times = _all_start_minutes(c, first)
    assert max(actual_times) > estimated_end
    load = _minute_load(c, first)
    t = min(load)
    empty = 0
    while t <= max(load):
        empty += int(t not in load)
        t += timedelta(minutes=1)
    assert empty <= 2


def test_clearing_competitors_drops_stale_lock_and_avoids_next_day():
    """A class locked at a late, now-stale anchor time (e.g. it used to be a
    small filler class squeezed in late in the day) must not balloon into
    the next day once its roster is wiped and re-imported with far more
    entries. Clearing competitors must drop the stale lock so the class is
    freshly (and sensibly) placed again."""
    c = Competition(name="StaleLock", event_date=date(2026, 8, 6))
    c.ensure_default_start_location()
    c.add_course(Course(id="crs", name="Rata", controls=["31", "32"]))

    class_a = RaceClass(
        id="class:a",
        name="A",
        course_id="crs",
        start_location_id=DEFAULT_START_LOCATION_ID,
        start_interval_min=2,
        course_order=0,
    )
    class_b = RaceClass(
        id="class:b",
        name="B",
        course_id="crs",
        start_location_id=DEFAULT_START_LOCATION_ID,
        start_interval_min=2,
        course_order=1,
    )
    c.add_class(class_a)
    c.add_class(class_b)
    c.add_competitor(Competitor(id="a:0", first_name="T", last_name="a0", class_id="class:a"))
    c.add_competitor(Competitor(id="b:0", first_name="T", last_name="b0", class_id="class:b"))

    # Manually seed a plan where class A is locked at a late, stale anchor —
    # as if it was locked long ago while it was still a tiny filler class.
    stale_anchor = datetime(2026, 8, 6, 20, 0)
    c.set_plan(
        ClassStartPlan(
            start_location_id=DEFAULT_START_LOCATION_ID,
            entries=[
                ClassStart(
                    id="s1", class_id="class:a", first_start_time=stale_anchor, locked=True
                )
            ],
        )
    )

    removed = c.clear_competitors()
    assert removed == 2
    stale_entry = c.plan_for(DEFAULT_START_LOCATION_ID).entry_for_class("class:a")
    assert stale_entry.locked is False

    # Re-import: class A turns out to have a much larger real roster.
    for i in range(300):
        c.add_competitor(
            Competitor(id=f"a2:{i}", first_name="T", last_name=f"a2-{i}", class_id="class:a")
        )
    c.add_competitor(Competitor(id="b2:0", first_name="T", last_name="b2-0", class_id="class:b"))

    new_plan = SchedulerService().apply(c)
    assert all(e.first_start_time.date() == c.event_date for e in new_plan.entries)
    entry_a = new_plan.entry_for_class("class:a")
    assert entry_a.locked is False
    assert entry_a.first_start_time == c.competition_start_datetime()
