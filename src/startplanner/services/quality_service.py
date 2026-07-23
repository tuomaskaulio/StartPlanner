"""Quality score for a ClassStartPlan (0–100)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from startplanner.domain import ClassStartPlan, Competition
from startplanner.services.validation_service import ValidationService


@dataclass(frozen=True)
class QualityScore:
    total: int
    rules: int
    first_controls: int
    flow: int
    order: int
    gaps: int

    def as_text(self) -> str:
        return f"{self.total} / 100"


class QualityService:
    """Spec weights: rules 50, first controls 20, flow 15, order 10, gaps 5."""

    def score(
        self, competition: Competition, start_location_id: str
    ) -> QualityScore:
        plan = competition.plan_for(start_location_id)
        if not plan or not plan.entries:
            return QualityScore(0, 0, 0, 0, 0, 0)

        report = ValidationService().validate(
            competition, start_location_id=start_location_id, require_plan=True
        )
        hard = [i for i in report.errors if i.rule_id.startswith("plan.")]
        rules = 50 if not hard else max(0, 50 - 10 * len(hard))

        first_controls = self._first_control_score(competition, plan)
        flow = self._flow_score(competition, plan)
        order = self._order_score(competition, plan)
        gaps = self._gap_score(competition, plan)
        total = rules + first_controls + flow + order + gaps
        return QualityScore(total, rules, first_controls, flow, order, gaps)

    def _first_control_score(
        self, competition: Competition, plan: ClassStartPlan
    ) -> int:
        load: dict[tuple[str, datetime], float] = defaultdict(float)
        for entry in plan.entries:
            rc = competition.classes.get(entry.class_id)
            if not rc:
                continue
            first = competition.first_control_for_class(rc)
            if not first:
                continue
            n = max(competition.competitor_count(rc.id), 1)
            for i in range(n):
                minute = (
                    entry.first_start_time
                    + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
                load[(first, minute)] += 1.0
        overload = sum(1 for v in load.values() if v > 1 + 1e-9)
        if overload == 0:
            return 20
        return max(0, 20 - 5 * overload)

    def _flow_score(self, competition: Competition, plan: ClassStartPlan) -> int:
        per_minute: dict[datetime, float] = defaultdict(float)
        for entry in plan.entries:
            rc = competition.classes.get(entry.class_id)
            if not rc:
                continue
            n = max(competition.competitor_count(rc.id), 1)
            for i in range(n):
                minute = (
                    entry.first_start_time
                    + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
                per_minute[minute] += 1.0
        if not per_minute:
            return 0
        values = list(per_minute.values())
        avg = sum(values) / len(values)
        if avg <= 0:
            return 15
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        # Lower variance → higher score
        if variance < 0.25:
            return 15
        if variance < 1.0:
            return 12
        if variance < 4.0:
            return 8
        if variance < 9.0:
            return 4
        return 0

    def _order_score(self, competition: Competition, plan: ClassStartPlan) -> int:
        entries = plan.sorted_entries()
        if len(entries) < 2:
            return 10
        inversions = 0
        pairs = 0
        for i, a in enumerate(entries):
            ra = competition.classes.get(a.class_id)
            ca = competition.course_for_class(ra) if ra else None
            la = ca.length_m if ca else 0
            for b in entries[i + 1 :]:
                rb = competition.classes.get(b.class_id)
                cb = competition.course_for_class(rb) if rb else None
                lb = cb.length_m if cb else 0
                pairs += 1
                # Prefer longer/faster earlier: if later class is longer, count inversion
                if lb > la + 500:
                    inversions += 1
        if pairs == 0:
            return 10
        ratio = inversions / pairs
        return max(0, int(10 * (1 - ratio)))

    def _gap_score(self, competition: Competition, plan: ClassStartPlan) -> int:
        entries = plan.sorted_entries()
        if len(entries) < 2:
            return 5
        desired = competition.settings.class_gap_min
        good = 0
        total = 0
        for prev, cur in zip(entries, entries[1:]):
            rc_prev = competition.classes.get(prev.class_id)
            if not rc_prev:
                continue
            end = competition.class_span_end(rc_prev, prev.first_start_time)
            gap = int((cur.first_start_time - end).total_seconds() // 60)
            total += 1
            if gap >= desired:
                good += 1
        if total == 0:
            return 5
        return int(5 * good / total)
