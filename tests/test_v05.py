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
    class_errors = [i for i in report.errors if i.rule_id == "class.course" and rc.name in i.message]
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
