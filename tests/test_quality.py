"""Quality, optimizer and history tests."""

from datetime import datetime, timedelta
from uuid import uuid4

from startplanner.domain import (
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
)
from startplanner.services.history_service import HistoryService
from startplanner.services.optimizer_service import OptimizerService
from startplanner.services.quality_service import QualityService
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService


def _mini_competition() -> Competition:
    competition = Competition(name="Test")
    competition.ensure_default_start_location()
    loc = next(iter(competition.start_locations))
    c1 = Course(id="c1", name="Rata A", length_m=5000, controls=["31", "32"])
    c2 = Course(id="c2", name="Rata B", length_m=3000, controls=["41", "42"])
    competition.add_course(c1)
    competition.add_course(c2)
    for name, course_id, n in (("H21", "c1", 3), ("D21", "c2", 2), ("H40", "c1", 2)):
        rc = RaceClass(
            id=name,
            name=name,
            course_id=course_id,
            start_location_id=loc,
            start_interval_min=2,
        )
        competition.add_class(rc)
        for i in range(n):
            competition.add_competitor(
                Competitor(
                    id=str(uuid4()),
                    first_name=f"F{i}",
                    last_name=name,
                    class_id=rc.id,
                )
            )
    return competition


def test_quality_score_after_schedule():
    competition = _mini_competition()
    SchedulerService().apply(competition)
    score = QualityService().score(competition, next(iter(competition.start_locations)))
    assert score.total >= 50
    assert score.rules == 50


def test_optimizer_keeps_valid_plan():
    competition = _mini_competition()
    loc = next(iter(competition.start_locations))
    SchedulerService().apply(competition, loc)
    before = QualityService().score(competition, loc).total
    OptimizerService().optimize(competition, loc, max_shift_min=5, max_passes=2)
    report = ValidationService().validate(competition, start_location_id=loc, require_plan=True)
    hard = [i for i in report.errors if i.rule_id.startswith("plan.")]
    assert hard == []
    after = QualityService().score(competition, loc).total
    assert after >= before


def test_history_undo_redo():
    history = HistoryService()
    loc = "start:default"
    t0 = datetime(2026, 7, 23, 12, 0)
    plan_a = ClassStartPlan(
        start_location_id=loc,
        entries=[ClassStart(id="1", class_id="H21", first_start_time=t0)],
    )
    plan_b = ClassStartPlan(
        start_location_id=loc,
        entries=[
            ClassStart(id="1", class_id="H21", first_start_time=t0 + timedelta(minutes=5))
        ],
    )
    history.push("A", plan_a)
    history.push("B", plan_b)
    assert history.can_undo()
    undone = history.undo()
    assert undone is not None
    assert undone.plan is not None
    assert undone.plan.entries[0].first_start_time == t0
    redone = history.redo()
    assert redone is not None
    assert redone.plan is not None
    assert redone.plan.entries[0].first_start_time == t0 + timedelta(minutes=5)
