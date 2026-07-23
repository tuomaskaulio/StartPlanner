"""Light iterative optimizer for ClassStartPlan."""

from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from startplanner.domain import ClassStart, ClassStartPlan, Competition
from startplanner.services.quality_service import QualityService
from startplanner.services.validation_service import ValidationService


class OptimizerService:
    """Shift unlocked classes by small minute offsets to improve quality score."""

    def __init__(self) -> None:
        self._quality = QualityService()
        self._validator = ValidationService()

    def optimize(
        self,
        competition: Competition,
        start_location_id: str,
        *,
        max_shift_min: int = 15,
        max_passes: int = 3,
    ) -> ClassStartPlan:
        plan = competition.plan_for(start_location_id)
        if not plan or not plan.entries:
            raise ValueError("Ei lähtökaaviota optimoitavaksi")

        best = deepcopy(plan)
        competition.set_plan(best)
        best_score = self._quality.score(competition, start_location_id).total

        for _ in range(max_passes):
            improved = False
            for entry in list(best.sorted_entries()):
                rc = competition.classes.get(entry.class_id)
                if not rc or rc.locked or entry.locked:
                    continue
                for delta in self._shift_order(max_shift_min):
                    if delta == 0:
                        continue
                    candidate = self._with_shift(best, entry.class_id, delta)
                    competition.set_plan(candidate)
                    report = self._validator.validate(
                        competition,
                        start_location_id=start_location_id,
                        require_plan=True,
                    )
                    if any(i.rule_id.startswith("plan.") for i in report.errors):
                        competition.set_plan(best)
                        continue
                    score = self._quality.score(competition, start_location_id).total
                    if score > best_score:
                        best = candidate
                        best_score = score
                        improved = True
                        break
                    competition.set_plan(best)
            if not improved:
                break

        competition.set_plan(best)
        return best

    def _with_shift(
        self, plan: ClassStartPlan, class_id: str, delta_min: int
    ) -> ClassStartPlan:
        entries: list[ClassStart] = []
        for e in plan.entries:
            if e.class_id == class_id:
                entries.append(
                    ClassStart(
                        id=str(uuid4()),
                        class_id=e.class_id,
                        first_start_time=e.first_start_time + timedelta(minutes=delta_min),
                        locked=e.locked,
                    )
                )
            else:
                entries.append(
                    ClassStart(
                        id=e.id,
                        class_id=e.class_id,
                        first_start_time=e.first_start_time,
                        locked=e.locked,
                    )
                )
        return ClassStartPlan(start_location_id=plan.start_location_id, entries=entries)

    @staticmethod
    def _shift_order(max_shift: int) -> list[int]:
        # Prefer small adjustments; alternate +/−
        order = [0]
        for m in range(1, max_shift + 1):
            order.append(m)
            order.append(-m)
        return order
