"""Scheduler and import/export E2E tests for ClassStartPlan."""

from pathlib import Path

from startplanner.domain import StartLocation
from startplanner.importers.condes_coursedata import class_tokens_from_course_name
from startplanner.services.competition_service import CompetitionService
from startplanner.services.import_service import ExportService, ImportService
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_SMALL = ROOT / "samples" / "sample-small"
SAMPLE_MEDIUM = ROOT / "samples" / "sample-medium"


def _small_xml() -> Path:
    return next(SAMPLE_SMALL.glob("*_coursedata.xml"))


def _medium_xmls() -> list[Path]:
    return sorted(SAMPLE_MEDIUM.glob("*_coursedata.xml"))


def test_class_tokens_from_course_name():
    assert class_tokens_from_course_name("6 H75/D60/D65") == ["H75", "D60", "D65"]
    assert class_tokens_from_course_name("D21 H35 H40") == ["D21", "H35", "H40"]
    assert class_tokens_from_course_name("H21A") == ["H21A"]


def test_sample_small_import_schedule_validate_export(tmp_path: Path):
    imports = ImportService()
    competition = imports.import_coursedata(_small_xml())
    n = imports.import_entries(competition, SAMPLE_SMALL / "ilmoittautumiset.csv")
    assert n == 38
    assert competition.classes
    assert competition.start_locations
    assert all(rc.course_id for rc in competition.classes.values())
    assert all(rc.start_location_id for rc in competition.classes.values())

    plan = SchedulerService().apply(competition)
    assert len(plan) >= 1
    assert all(e.first_start_time for e in plan.entries)

    plan2 = SchedulerService().build(competition)
    times1 = [(e.class_id, e.first_start_time) for e in plan.sorted_entries()]
    times2 = [(e.class_id, e.first_start_time) for e in plan2.sorted_entries()]
    assert times1 == times2

    report = ValidationService().validate(competition, require_plan=True)
    schedule_errors = [
        i
        for i in report.errors
        if i.rule_id.startswith("plan.") or i.rule_id in {"class.course", "class.start_location"}
    ]
    assert schedule_errors == [], [i.message for i in schedule_errors]

    xlsx = tmp_path / "out.xlsx"
    csv_path = tmp_path / "out.csv"
    ExportService().export_excel(competition, xlsx)
    ExportService().export_csv(competition, csv_path)
    assert xlsx.exists() and xlsx.stat().st_size > 0
    text = csv_path.read_text(encoding="utf-8")
    assert "1. lähtöaika" in text
    assert "Sarja" in text


def test_sample_medium_merge_partial_schedule():
    imports = ImportService()
    xmls = _medium_xmls()
    assert len(xmls) == 2
    competition = imports.import_coursedata(xmls[0])
    imports.import_coursedata(xmls[1], competition)
    imports.import_entries(competition, SAMPLE_MEDIUM / "ilmoittautumiset.csv")

    report_before = ValidationService().validate(competition)
    missing_course = [i for i in report_before.errors if i.rule_id == "class.course"]
    assert missing_course, "medium sample should have some classes without course"

    plan = SchedulerService().apply(competition)
    assert len(plan) > 0

    report = ValidationService().validate(competition, require_plan=True)
    assert any(i.rule_id == "class.course" for i in report.errors)
    schedule_hard = [
        i
        for i in report.errors
        if i.rule_id in {"plan.first_control", "plan.course_interleave"}
    ]
    assert schedule_hard == [], [i.message for i in schedule_hard]


def test_two_locations_scheduled_independently():
    imports = ImportService()
    competition = imports.import_coursedata(_small_xml())
    imports.import_entries(competition, SAMPLE_SMALL / "ilmoittautumiset.csv")
    loc2 = StartLocation(id="start:2", name="Lähtö 2")
    competition.add_start_location(loc2)
    # Move half the classes to location 2
    for i, rc in enumerate(sorted(competition.classes.values(), key=lambda x: x.name)):
        if i % 2 == 1:
            rc.start_location_id = loc2.id

    plan1 = SchedulerService().apply(competition, "start:default")
    plan2 = SchedulerService().apply(competition, loc2.id)
    assert len(plan1) > 0 and len(plan2) > 0
    assert plan1.start_location_id != plan2.start_location_id
    report = ValidationService().validate(competition, require_plan=True)
    assert not any(i.rule_id == "plan.first_control" for i in report.errors)


def test_spc_roundtrip(tmp_path: Path):
    imports = ImportService()
    competition = imports.import_coursedata(_small_xml())
    imports.import_entries(competition, SAMPLE_SMALL / "ilmoittautumiset.csv")
    SchedulerService().apply(competition)

    path = tmp_path / "test.spc"
    svc = CompetitionService()
    svc.save(competition, path)
    loaded = svc.load(path)
    assert loaded.name == competition.name
    assert len(loaded.competitors) == len(competition.competitors)
    assert loaded.start_locations
    assert loaded.plans
    loc_id = next(iter(competition.plans))
    assert loaded.plan_for(loc_id) is not None
    assert loaded.plan_for(loc_id).sorted_entries()[0].first_start_time == (
        competition.plan_for(loc_id).sorted_entries()[0].first_start_time
    )
