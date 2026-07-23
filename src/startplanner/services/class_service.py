"""Race class assignment helpers."""

from __future__ import annotations

from startplanner.domain import Competition
from startplanner.domain.errors import StartPlannerError


class ClassService:
    def assign_course(
        self, competition: Competition, class_id: str, course_id: str | None
    ) -> None:
        rc = competition.classes.get(class_id)
        if rc is None:
            raise StartPlannerError(f"Tuntematon sarja: {class_id}")
        if course_id is not None and course_id not in competition.courses:
            raise StartPlannerError(f"Tuntematon rata: {course_id}")
        rc.course_id = course_id
        if course_id:
            competition.class_course_map[rc.name] = course_id
        elif rc.name in competition.class_course_map:
            del competition.class_course_map[rc.name]

    def classes_missing_course(self, competition: Competition) -> list[str]:
        return sorted(
            rc.name
            for rc in competition.classes.values()
            if not rc.course_id or rc.course_id not in competition.courses
        )
