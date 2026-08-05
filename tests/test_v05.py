"""v0.5: class-course assignment and incremental plan update."""

from pathlib import Path

from startplanner.services.class_service import ClassService
from startplanner.services.import_service import ImportService
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MEDIUM = ROOT / "samples" / "sample-medium"


def _medium_competition():
    imports = ImportService()
    xmls = sorted(SAMPLE_MEDIUM.glob("*_coursedata.xml"))
    competition = imports.import_coursedata(xmls[0])
    imports.import_coursedata(xmls[1], competition)
    imports.import_entries(competition, SAMPLE_MEDIUM / "ilmoittautumiset.csv")
    return competition


def test_assign_course_clears_missing_course_error():
    competition = _medium_competition()
    missing = ClassService().classes_missing_course(competition)
    assert missing

    rc = competition.get_class_by_name(missing[0])
    assert rc is not None
    course_id = next(iter(competition.courses))
    ClassService().assign_course(competition, rc.id, course_id)

    report = ValidationService().validate(competition)
    class_errors = [
        i
        for i in report.errors
        if i.rule_id == "class.course" and rc.name in i.message
    ]
    assert class_errors == []


def test_update_preserves_existing_plan_times_with_late_entries():
    competition = _medium_competition()
    scheduler = SchedulerService()
    plan = scheduler.apply(competition)
    times_before = {e.class_id: e.first_start_time for e in plan.entries}
    assert times_before

    before_competitors = len(competition.competitors)
    ImportService().import_entries(
        competition, SAMPLE_MEDIUM / "jalki_ilmoittautumiset.csv"
    )
    assert len(competition.competitors) == before_competitors + 9

    plan2 = scheduler.update(competition)
    for class_id, t in times_before.items():
        entry = plan2.entry_for_class(class_id)
        assert entry is not None
        assert entry.first_start_time == t


def test_update_adds_newly_mappable_classes():
    competition = _medium_competition()
    scheduler = SchedulerService()
    plan_before = scheduler.apply(competition)
    n_before = len(plan_before)

    rc = competition.get_class_by_name("H21")
    assert rc is not None
    assert not rc.course_id
    ClassService().assign_course(competition, rc.id, next(iter(competition.courses)))

    plan_after = scheduler.update(competition)
    assert len(plan_after) >= n_before
    assert plan_after.entry_for_class(rc.id) is not None


def test_assign_start_location_and_interval():
    from startplanner.domain import StartLocation

    competition = _medium_competition()
    loc = StartLocation(id="start:north", name="Pohjoinen")
    competition.add_start_location(loc)
    rc = next(iter(competition.classes.values()))
    svc = ClassService()
    svc.assign_start_location(competition, rc.id, loc.id)
    svc.set_start_interval(competition, rc.id, 3)
    assert rc.start_location_id == loc.id
    assert rc.start_interval_min == 3


def test_spc_roundtrip_preserves_interval_and_course_gap(tmp_path: Path):
    from startplanner.services.competition_service import CompetitionService

    competition = _medium_competition()
    rc = next(iter(competition.classes.values()))
    course = next(iter(competition.courses.values()))
    ClassService().set_start_interval(competition, rc.id, 4)
    ClassService().set_course_class_gap(competition, course.id, 5)

    path = tmp_path / "gap.spc"
    svc = CompetitionService()
    svc.save(competition, path)
    loaded = svc.load(path)
    assert loaded.classes[rc.id].start_interval_min == 4
    assert loaded.courses[course.id].class_gap_min == 5
    assert loaded.class_gap_for_course(course.id) == 5


def test_scheduler_respects_empty_slots_before():
    from datetime import timedelta

    from startplanner.domain import (
        DEFAULT_START_LOCATION_ID,
        Competition,
        Competitor,
        Course,
        RaceClass,
    )
    from startplanner.services.scheduler_service import SchedulerService

    c = Competition(name="EmptySlots")
    c.ensure_default_start_location()
    c.settings.class_gap_min = 2
    c.add_course(
        Course(
            id="cA",
            name="A",
            length_m=3000,
            controls=["31"],
        )
    )
    c.add_class(
        RaceClass(
            id="h60",
            name="H60",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=1,
        )
    )
    c.add_class(
        RaceClass(
            id="h65",
            name="H65",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=1,
            empty_slots_before=1,
        )
    )
    c.add_competitor(Competitor(id="1", first_name="A", last_name="One", class_id="h60"))
    c.add_competitor(Competitor(id="2", first_name="B", last_name="Two", class_id="h65"))
    plan = SchedulerService().apply(c)
    ordered = sorted(plan.entries, key=lambda e: e.first_start_time)
    first_end = c.class_span_end(
        c.classes[ordered[0].class_id], ordered[0].first_start_time
    )
    # H65 is second on course; 1 empty slot * 1-min interval => +1 min after gap
    assert ordered[1].first_start_time >= first_end + timedelta(minutes=2 + 1)


def test_scheduler_first_class_empty_slots_shifts_start():
    from datetime import timedelta

    from startplanner.domain import (
        DEFAULT_START_LOCATION_ID,
        Competition,
        Competitor,
        Course,
        RaceClass,
    )
    from startplanner.services.scheduler_service import SchedulerService

    c = Competition(name="FirstEmpty")
    c.ensure_default_start_location()
    c.settings.class_gap_min = 2
    c.add_course(
        Course(
            id="cA",
            name="A",
            length_m=3000,
            controls=["31"],
        )
    )
    c.add_class(
        RaceClass(
            id="h21",
            name="H21",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=2,
            empty_slots_before=1,
        )
    )
    c.add_competitor(Competitor(id="1", first_name="A", last_name="One", class_id="h21"))
    start = c.competition_start_datetime()
    plan = SchedulerService().apply(c)
    entry = plan.entry_for_class("h21")
    assert entry is not None
    # First class: 1 empty slot * 2-min interval => 2 min after start
    assert entry.first_start_time == start + timedelta(minutes=2)


def test_empty_slots_before_spc_roundtrip(tmp_path: Path):
    from startplanner.services.competition_service import CompetitionService

    c = _medium_competition()
    rc = next(iter(c.classes.values()))
    ClassService().set_empty_slots_before(c, rc.id, 3)

    path = tmp_path / "empty.spc"
    svc = CompetitionService()
    svc.save(c, path)
    loaded = svc.load(path)
    assert loaded.classes[rc.id].empty_slots_before == 3


def test_empty_slots_before_default_is_zero():
    from startplanner.domain import RaceClass

    rc = RaceClass(id="x", name="X")
    assert rc.empty_slots_before == 0


def test_scheduler_respects_course_class_gap():
    from datetime import timedelta

    from startplanner.domain import (
        DEFAULT_START_LOCATION_ID,
        Competition,
        Competitor,
        Course,
        RaceClass,
    )
    from startplanner.services.scheduler_service import SchedulerService

    c = Competition(name="Gap")
    c.ensure_default_start_location()
    c.settings.class_gap_min = 2
    c.add_course(
        Course(
            id="cA",
            name="A",
            length_m=3000,
            controls=["31"],
            class_gap_min=7,
        )
    )
    c.add_class(
        RaceClass(
            id="h21",
            name="H21",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=1,
        )
    )
    c.add_class(
        RaceClass(
            id="h20",
            name="H20",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=1,
        )
    )
    c.add_competitor(Competitor(id="1", first_name="A", last_name="One", class_id="h21"))
    c.add_competitor(Competitor(id="2", first_name="B", last_name="Two", class_id="h20"))
    plan = SchedulerService().apply(c)
    ordered = sorted(plan.entries, key=lambda e: e.first_start_time)
    first_end = c.class_span_end(
        c.classes[ordered[0].class_id], ordered[0].first_start_time
    )
    assert ordered[1].first_start_time >= first_end + timedelta(minutes=7)


def test_spc_roundtrip_location_first_start(tmp_path: Path):
    from datetime import time

    from startplanner.domain import StartLocation
    from startplanner.services.competition_service import CompetitionService

    competition = _medium_competition()
    loc = StartLocation(id="start:north", name="Pohjoinen", first_start=time(8, 30))
    competition.add_start_location(loc)
    ClassService().set_sort_order(
        competition, next(iter(competition.classes.values())).id, 42
    )

    path = tmp_path / "loc.spc"
    svc = CompetitionService()
    svc.save(competition, path)
    loaded = svc.load(path)
    assert loaded.start_locations[loc.id].first_start == time(8, 30)
    assert loaded.start_datetime_for(loc.id).hour == 8
    rc_id = next(iter(competition.classes.values())).id
    assert loaded.classes[rc_id].sort_order == 42


def test_scheduler_uses_location_first_start():
    from datetime import time

    from startplanner.domain import (
        DEFAULT_START_LOCATION_ID,
        Competition,
        Competitor,
        Course,
        RaceClass,
    )
    from startplanner.services.scheduler_service import SchedulerService

    c = Competition(name="LocStart")
    c.settings.competition_start = time(12, 0)
    c.ensure_default_start_location()
    c.start_locations[DEFAULT_START_LOCATION_ID].first_start = time(10, 0)
    c.add_course(Course(id="cA", name="A", length_m=3000, controls=["31"]))
    c.add_class(
        RaceClass(
            id="h21",
            name="H21",
            course_id="cA",
            start_location_id=DEFAULT_START_LOCATION_ID,
            start_interval_min=1,
        )
    )
    c.add_competitor(Competitor(id="1", first_name="A", last_name="One", class_id="h21"))
    plan = SchedulerService().apply(c)
    entry = plan.entry_for_class("h21")
    assert entry is not None
    assert entry.first_start_time.hour == 10
    assert entry.first_start_time.minute == 0


def test_set_sort_order():
    competition = _medium_competition()
    rc = next(iter(competition.classes.values()))
    ClassService().set_sort_order(competition, rc.id, 5)
    assert rc.sort_order == 5


def test_reorder_classes_renumbers_sort_order():
    competition = _medium_competition()
    ordered = sorted(
        competition.classes.values(), key=lambda c: (c.sort_order, c.name)
    )
    reversed_ids = [rc.id for rc in reversed(ordered)]
    ClassService().reorder_classes(competition, reversed_ids)
    for index, class_id in enumerate(reversed_ids):
        assert competition.classes[class_id].sort_order == index
