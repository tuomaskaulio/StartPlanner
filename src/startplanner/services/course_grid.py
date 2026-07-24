"""Course-column grid model for the schedule timeline view."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from startplanner.domain import ClassStartPlan, Competition


@dataclass(frozen=True)
class CourseGridColumn:
    course_id: str
    course_name: str
    first_control: str


@dataclass
class CourseGrid:
    minutes: list[datetime] = field(default_factory=list)
    columns: list[CourseGridColumn] = field(default_factory=list)
    total_by_minute: dict[datetime, int] = field(default_factory=dict)
    cells: dict[tuple[datetime, str], str] = field(default_factory=dict)

    def cell(self, minute: datetime, course_id: str) -> str:
        return self.cells.get((minute.replace(second=0, microsecond=0), course_id), "")

    def total(self, minute: datetime) -> int:
        return self.total_by_minute.get(minute.replace(second=0, microsecond=0), 0)


def build_course_grid(
    competition: Competition,
    plan: ClassStartPlan | None,
) -> CourseGrid:
    grid = CourseGrid()
    if not plan or not plan.entries:
        return grid

    course_ids: set[str] = set()
    minute_load: dict[datetime, int] = {}
    cells: dict[tuple[datetime, str], str] = {}

    for entry in plan.entries:
        rc = competition.classes.get(entry.class_id)
        if not rc or not rc.course_id:
            continue
        course = competition.courses.get(rc.course_id)
        if not course:
            continue
        course_ids.add(rc.course_id)
        n = max(competition.competitor_count(rc.id), 1)
        for i in range(n):
            minute = (
                entry.first_start_time + timedelta(minutes=i * rc.start_interval_min)
            ).replace(second=0, microsecond=0)
            minute_load[minute] = minute_load.get(minute, 0) + 1
            key = (minute, rc.course_id)
            if key in cells and cells[key] != rc.name:
                cells[key] = f"{cells[key]}, {rc.name}"
            else:
                cells[key] = rc.name

    if not minute_load:
        return grid

    t0 = min(minute_load)
    t1 = max(minute_load)
    minutes: list[datetime] = []
    t = t0
    while t <= t1:
        minutes.append(t)
        t += timedelta(minutes=1)

    columns: list[CourseGridColumn] = []
    for cid in sorted(
        course_ids,
        key=lambda c: (
            competition.courses[c].first_control or "",
            competition.courses[c].name,
        ),
    ):
        course = competition.courses[cid]
        columns.append(
            CourseGridColumn(
                course_id=cid,
                course_name=course.name,
                first_control=course.first_control or "",
            )
        )

    grid.minutes = minutes
    grid.columns = columns
    grid.total_by_minute = minute_load
    grid.cells = cells
    return grid
