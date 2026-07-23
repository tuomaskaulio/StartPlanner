"""Greedy deterministic ClassStartPlan builder (per StartLocation)."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from startplanner.domain import (
    ClassStart,
    ClassStartPlan,
    Competition,
    RaceClass,
)
from startplanner.domain.errors import ScheduleError


class SchedulerService:
    def build(
        self, competition: Competition, start_location_id: str | None = None
    ) -> ClassStartPlan:
        location_id = self._resolve_location(competition, start_location_id)
        classes = self._ordered_classes(competition, location_id)
        if not classes:
            raise ScheduleError(
                "Ei sijoitettavia sarjoja tässä lähdössä (rata ja kilpailijat puuttuvat)"
            )

        cursor = competition.competition_start_datetime()
        occupied: dict[str, set[datetime]] = {}
        course_end: dict[str, datetime] = {}
        entries: list[ClassStart] = []
        gap = timedelta(minutes=competition.settings.class_gap_min)

        existing = competition.plan_for(location_id)
        locked_times: dict[str, datetime] = {}
        if existing:
            for entry in existing.entries:
                rc = competition.classes.get(entry.class_id)
                if rc and (rc.locked or entry.locked):
                    locked_times[entry.class_id] = entry.first_start_time

        for rc in classes:
            n = max(competition.competitor_count(rc.id), 1)
            course = competition.course_for_class(rc)
            assert course is not None and course.first_control
            first_control = course.first_control

            if rc.id in locked_times:
                placement = locked_times[rc.id]
            else:
                earliest = cursor
                if rc.course_id in course_end:
                    earliest = max(earliest, course_end[rc.course_id] + gap)
                placement = self._find_placement(
                    earliest=earliest,
                    count=n,
                    interval_min=rc.start_interval_min,
                    first_control=first_control,
                    occupied=occupied,
                )

            entries.append(
                ClassStart(
                    id=str(uuid4()),
                    class_id=rc.id,
                    first_start_time=placement,
                    locked=rc.locked or rc.id in locked_times,
                )
            )
            for i in range(n):
                slot = (placement + timedelta(minutes=i * rc.start_interval_min)).replace(
                    second=0, microsecond=0
                )
                occupied.setdefault(first_control, set()).add(slot)

            last_time = competition.class_span_end(rc, placement)
            if rc.course_id:
                course_end[rc.course_id] = last_time
            if rc.id not in locked_times:
                cursor = last_time + gap

        return ClassStartPlan(start_location_id=location_id, entries=entries)

    def apply(
        self, competition: Competition, start_location_id: str | None = None
    ) -> ClassStartPlan:
        plan = self.build(competition, start_location_id)
        competition.set_plan(plan)
        return plan

    def _resolve_location(
        self, competition: Competition, start_location_id: str | None
    ) -> str:
        competition.ensure_default_start_location()
        if start_location_id:
            if start_location_id not in competition.start_locations:
                raise ScheduleError(f"Tuntematon lähtö: {start_location_id}")
            return start_location_id
        return next(iter(competition.start_locations))

    def _ordered_classes(
        self, competition: Competition, start_location_id: str
    ) -> list[RaceClass]:
        classes = [
            rc
            for rc in competition.classes_at_location(start_location_id)
            if rc.course_id
            and rc.course_id in competition.courses
            and competition.courses[rc.course_id].first_control
            and competition.competitor_count(rc.id) > 0
        ]

        def sort_key(rc: RaceClass) -> tuple:
            course = competition.course_for_class(rc)
            length = course.length_m if course else 0
            return (-rc.estimated_speed, -length, rc.sort_order, rc.name)

        return sorted(classes, key=sort_key)

    def _find_placement(
        self,
        *,
        earliest: datetime,
        count: int,
        interval_min: int,
        first_control: str,
        occupied: dict[str, set[datetime]],
    ) -> datetime:
        t = earliest.replace(second=0, microsecond=0)
        busy = occupied.get(first_control, set())
        while True:
            conflict = False
            for i in range(count):
                slot = (t + timedelta(minutes=i * interval_min)).replace(
                    second=0, microsecond=0
                )
                if slot in busy:
                    conflict = True
                    break
            if not conflict:
                return t
            t += timedelta(minutes=1)
