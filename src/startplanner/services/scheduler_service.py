"""Greedy deterministic start schedule builder."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from startplanner.domain import Competition, Competitor, RaceClass, Start, StartSchedule
from startplanner.domain.errors import ScheduleError


class SchedulerService:
    def build(self, competition: Competition) -> StartSchedule:
        self._validate_input(competition)
        classes = self._ordered_classes(competition)
        cursor = competition.competition_start_datetime()
        # first_control -> set of occupied minutes (as datetime minute)
        occupied: dict[str, set[datetime]] = {}
        # course_id -> end time of last placed class on that course
        course_end: dict[str, datetime] = {}
        starts: list[Start] = []
        start_number = 1
        gap = timedelta(minutes=competition.settings.class_gap_min)

        for rc in classes:
            competitors = self._ordered_competitors(competition, rc)
            if not competitors:
                continue
            course = competition.course_for_class(rc)
            assert course is not None
            first = course.first_control
            assert first is not None

            earliest = cursor
            if rc.course_id in course_end:
                earliest = max(earliest, course_end[rc.course_id] + gap)

            placement = self._find_placement(
                earliest=earliest,
                count=len(competitors),
                interval_min=rc.start_interval_min,
                first_control=first,
                occupied=occupied,
            )
            for i, competitor in enumerate(competitors):
                t = placement + timedelta(minutes=i * rc.start_interval_min)
                starts.append(
                    Start(
                        id=str(uuid4()),
                        competitor_id=competitor.id,
                        class_id=rc.id,
                        course_id=course.id,
                        start_time=t,
                        start_number=start_number,
                    )
                )
                start_number += 1
                occupied.setdefault(first, set()).add(t.replace(second=0, microsecond=0))

            last_time = placement + timedelta(
                minutes=(len(competitors) - 1) * rc.start_interval_min
            )
            course_end[course.id] = last_time
            cursor = last_time + gap

        return StartSchedule(starts=starts)

    def apply(self, competition: Competition) -> StartSchedule:
        schedule = self.build(competition)
        competition.schedule = schedule
        return schedule

    def _validate_input(self, competition: Competition) -> None:
        schedulable = [
            rc
            for rc in competition.classes.values()
            if rc.course_id
            and rc.course_id in competition.courses
            and competition.courses[rc.course_id].first_control
            and competition.competitors_in_class(rc.id)
        ]
        if not schedulable:
            raise ScheduleError("Ei sijoitettavia sarjoja (rata ja kilpailijat puuttuvat)")

    def _ordered_classes(self, competition: Competition) -> list[RaceClass]:
        classes = [
            rc
            for rc in competition.classes.values()
            if rc.course_id
            and rc.course_id in competition.courses
            and competition.courses[rc.course_id].first_control
            and competition.competitors_in_class(rc.id)
        ]

        def sort_key(rc: RaceClass) -> tuple:
            course = competition.course_for_class(rc)
            length = course.length_m if course else 0
            # Faster/longer first: higher estimated_speed, then longer course, then name
            return (-rc.estimated_speed, -length, rc.sort_order, rc.name)

        return sorted(classes, key=sort_key)

    def _ordered_competitors(
        self, competition: Competition, rc: RaceClass
    ) -> list[Competitor]:
        comps = competition.competitors_in_class(rc.id)
        return sorted(comps, key=lambda c: (c.last_name, c.first_name, c.id))

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
