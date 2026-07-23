"""Scheduler and import/export E2E tests."""

from pathlib import Path

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
    assert all(rc.course_id for rc in competition.classes.values())

    schedule = SchedulerService().apply(competition)
    assert len(schedule) == 38

    schedule2 = SchedulerService().build(competition)
    times1 = [(s.competitor_id, s.start_time) for s in schedule.sorted_starts()]
    times2 = [(s.competitor_id, s.start_time) for s in schedule2.sorted_starts()]
    assert times1 == times2

    report = ValidationService().validate(competition, require_schedule=True)
    schedule_errors = [
        i
        for i in report.errors
        if i.rule_id.startswith("schedule.") or i.rule_id == "class.course"
    ]
    assert schedule_errors == [], [i.message for i in schedule_errors]

    xlsx = tmp_path / "out.xlsx"
    csv_path = tmp_path / "out.csv"
    ExportService().export_excel(competition, xlsx)
    ExportService().export_csv(competition, csv_path)
    assert xlsx.exists() and xlsx.stat().st_size > 0
    assert csv_path.exists()
    text = csv_path.read_text(encoding="utf-8")
    assert "Aika" in text
    assert text.count("\n") >= 38


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

    schedule = SchedulerService().apply(competition)
    assert len(schedule) > 0
    assert len(schedule) < len(competition.competitors)

    report = ValidationService().validate(competition, require_schedule=True)
    assert any(i.rule_id == "class.course" for i in report.errors)
    schedule_hard = [
        i
        for i in report.errors
        if i.rule_id
        in {"schedule.first_control", "schedule.interval", "schedule.course_interleave"}
    ]
    assert schedule_hard == [], [i.message for i in schedule_hard]


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
    assert len(loaded.schedule) == len(competition.schedule)
    assert loaded.schedule.sorted_starts()[0].start_time == competition.schedule.sorted_starts()[
        0
    ].start_time
