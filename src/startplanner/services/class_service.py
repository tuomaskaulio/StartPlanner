"""Race class and course assignment helpers."""

from __future__ import annotations

from datetime import time

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
        prev = rc.course_id
        rc.course_id = course_id
        if course_id:
            competition.class_course_map[rc.name] = course_id
            if prev != course_id:
                siblings = [
                    c
                    for c in competition.classes.values()
                    if c.course_id == course_id and c.id != class_id
                ]
                rc.course_order = (
                    max((c.course_order for c in siblings), default=-1) + 1
                )
        elif rc.name in competition.class_course_map:
            del competition.class_course_map[rc.name]

    def reorder_course_classes(
        self, competition: Competition, course_id: str, class_ids: list[str]
    ) -> None:
        if course_id not in competition.courses:
            raise StartPlannerError(f"Tuntematon rata: {course_id}")
        if len(class_ids) != len(set(class_ids)):
            raise StartPlannerError("Ratajärjestys sisältää duplikaatteja")
        expected = {
            rc.id
            for rc in competition.classes.values()
            if rc.course_id == course_id
        }
        if set(class_ids) != expected:
            raise StartPlannerError(
                "Järjestyksen on sisällettävä kaikki radan sarjat"
            )
        for index, class_id in enumerate(class_ids):
            competition.classes[class_id].course_order = index

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

    def set_location_first_start(
        self, competition: Competition, location_id: str, first_start: time | None
    ) -> None:
        loc = competition.start_locations.get(location_id)
        if loc is None:
            raise StartPlannerError(f"Tuntematon lähtö: {location_id}")
        loc.first_start = first_start

    def set_sort_order(
        self, competition: Competition, class_id: str, sort_order: int
    ) -> None:
        rc = competition.classes.get(class_id)
        if rc is None:
            raise StartPlannerError(f"Tuntematon sarja: {class_id}")
        if sort_order < 0:
            raise StartPlannerError("Järjestyksen on oltava vähintään 0")
        rc.sort_order = sort_order

    def reorder_classes(
        self, competition: Competition, class_ids: list[str]
    ) -> None:
        if len(class_ids) != len(set(class_ids)):
            raise StartPlannerError("Sarjajärjestys sisältää duplikaatteja")
        if set(class_ids) != set(competition.classes.keys()):
            raise StartPlannerError("Järjestyksen on sisällettävä kaikki sarjat")
        for index, class_id in enumerate(class_ids):
            competition.classes[class_id].sort_order = index

    def classes_missing_course(self, competition: Competition) -> list[str]:
        return sorted(
            rc.name
            for rc in competition.classes.values()
            if not rc.course_id or rc.course_id not in competition.courses
        )
