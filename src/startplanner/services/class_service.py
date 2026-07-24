"""Race class and course assignment helpers."""

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

    def assign_start_location(
        self, competition: Competition, class_id: str, start_location_id: str
    ) -> None:
        rc = competition.classes.get(class_id)
        if rc is None:
            raise StartPlannerError(f"Tuntematon sarja: {class_id}")
        if start_location_id not in competition.start_locations:
            raise StartPlannerError(f"Tuntematon lähtö: {start_location_id}")
        rc.start_location_id = start_location_id

    def set_start_interval(
        self, competition: Competition, class_id: str, interval_min: int
    ) -> None:
        rc = competition.classes.get(class_id)
        if rc is None:
            raise StartPlannerError(f"Tuntematon sarja: {class_id}")
        if interval_min < 1:
            raise StartPlannerError("Lähtövälin on oltava vähintään 1 minuutti")
        rc.start_interval_min = interval_min

    def set_course_class_gap(
        self, competition: Competition, course_id: str, gap_min: int | None
    ) -> None:
        course = competition.courses.get(course_id)
        if course is None:
            raise StartPlannerError(f"Tuntematon rata: {course_id}")
        if gap_min is not None and gap_min < 0:
            raise StartPlannerError("Sarjaväli ei voi olla negatiivinen")
        course.class_gap_min = gap_min

    def rename_start_location(
        self, competition: Competition, location_id: str, name: str
    ) -> None:
        loc = competition.start_locations.get(location_id)
        if loc is None:
            raise StartPlannerError(f"Tuntematon lähtö: {location_id}")
        cleaned = name.strip()
        if not cleaned:
            raise StartPlannerError("Lähdön nimi ei voi olla tyhjä")
        loc.name = cleaned

    def classes_missing_course(self, competition: Competition) -> list[str]:
        return sorted(
            rc.name
            for rc in competition.classes.values()
            if not rc.course_id or rc.course_id not in competition.courses
        )
