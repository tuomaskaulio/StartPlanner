"""StartPlanner domain model."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, datetime, time
from uuid import uuid4


def _new_id() -> str:
    return str(uuid4())


@dataclass
class Settings:
    default_start_interval_min: int = 2
    class_gap_min: int = 2
    competition_start: time = time(12, 0)


@dataclass
class Course:
    id: str
    name: str
    length_m: int = 0
    climb_m: int = 0
    controls: list[str] = field(default_factory=list)

    @property
    def first_control(self) -> str | None:
        return self.controls[0] if self.controls else None

    @property
    def length_km(self) -> float:
        return self.length_m / 1000.0


@dataclass
class RaceClass:
    id: str
    name: str
    course_id: str | None = None
    start_interval_min: int = 2
    estimated_speed: float = 0.0
    sort_order: int = 0
    locked: bool = False


@dataclass
class Competitor:
    id: str
    first_name: str
    last_name: str
    club: str = ""
    class_id: str = ""
    emit: str | None = None
    birth_year: int | None = None
    locked: bool = False

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name}".strip()


@dataclass
class Start:
    id: str
    competitor_id: str
    class_id: str
    course_id: str
    start_time: datetime
    start_number: int
    locked: bool = False


@dataclass
class StartSchedule:
    starts: list[Start] = field(default_factory=list)

    def sorted_starts(self) -> list[Start]:
        return sorted(self.starts, key=lambda s: (s.start_time, s.start_number))

    def __iter__(self) -> Iterator[Start]:
        return iter(self.sorted_starts())

    def __len__(self) -> int:
        return len(self.starts)


@dataclass
class Competition:
    id: str = field(default_factory=_new_id)
    name: str = ""
    event_date: date | None = None
    settings: Settings = field(default_factory=Settings)
    courses: dict[str, Course] = field(default_factory=dict)
    classes: dict[str, RaceClass] = field(default_factory=dict)
    competitors: dict[str, Competitor] = field(default_factory=dict)
    schedule: StartSchedule = field(default_factory=StartSchedule)
    # class_name -> course_id assignments from import
    class_course_map: dict[str, str] = field(default_factory=dict)

    def add_course(self, course: Course) -> None:
        self.courses[course.id] = course

    def add_class(self, race_class: RaceClass) -> None:
        self.classes[race_class.id] = race_class

    def add_competitor(self, competitor: Competitor) -> None:
        self.competitors[competitor.id] = competitor

    def get_class_by_name(self, name: str) -> RaceClass | None:
        for rc in self.classes.values():
            if rc.name == name:
                return rc
        return None

    def get_course_by_name(self, name: str) -> Course | None:
        for course in self.courses.values():
            if course.name == name:
                return course
        return None

    def competitors_in_class(self, class_id: str) -> list[Competitor]:
        return [c for c in self.competitors.values() if c.class_id == class_id]

    def course_for_class(self, race_class: RaceClass) -> Course | None:
        if not race_class.course_id:
            return None
        return self.courses.get(race_class.course_id)

    def first_control_for_class(self, race_class: RaceClass) -> str | None:
        course = self.course_for_class(race_class)
        return course.first_control if course else None

    def competition_start_datetime(self) -> datetime:
        d = self.event_date or date.today()
        return datetime.combine(d, self.settings.competition_start)
