"""StartPlanner domain model."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from uuid import uuid4

DEFAULT_START_LOCATION_ID = "start:default"


def _new_id() -> str:
    return str(uuid4())


def format_start_time(value: datetime, event_date: date | None) -> str:
    """Format a start time as HH:MM, marking a day offset from event_date."""
    clock = value.strftime("%H:%M")
    if event_date is None:
        return clock
    offset = (value.date() - event_date).days
    if offset == 0:
        return clock
    return f"{clock} ({offset:+d} pv)"


@dataclass
class Settings:
    default_start_interval_min: int = 2
    class_gap_min: int = 2
    competition_start: time = time(12, 0)


@dataclass
class StartLocation:
    id: str
    name: str
    # None = use competition Settings.competition_start
    first_start: time | None = None


@dataclass
class Course:
    id: str
    name: str
    length_m: int = 0
    climb_m: int = 0
    controls: list[str] = field(default_factory=list)
    # None = use competition Settings.class_gap_min
    class_gap_min: int | None = None

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
    start_location_id: str | None = None
    start_interval_min: int = 2
    estimated_speed: float = 0.0
    sort_order: int = 0  # display order (Sarjajärjestys)
    # Order of classes sharing the same course (scheduler sequence)
    course_order: int = 0
    locked: bool = False
    # Number of empty start slots to leave before this class on its course
    empty_slots_before: int = 0


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
class ClassStart:
    """One row in a start scheme: class + first start time."""

    id: str
    class_id: str
    first_start_time: datetime
    locked: bool = False


@dataclass
class ClassStartPlan:
    """Start scheme for one StartLocation."""

    start_location_id: str
    entries: list[ClassStart] = field(default_factory=list)

    def sorted_entries(
        self,
        *,
        by: str = "time",
        class_sort_order: dict[str, int] | None = None,
        class_names: dict[str, str] | None = None,
    ) -> list[ClassStart]:
        """Sort plan rows. by='time' (default) or by='class' (sort_order)."""
        orders = class_sort_order or {}
        names = class_names or {}

        def _key(e: ClassStart) -> tuple:
            order = orders.get(e.class_id, 0)
            name = names.get(e.class_id, e.class_id)
            if by == "class":
                return (order, e.first_start_time, name)
            return (e.first_start_time, order, name)

        return sorted(self.entries, key=_key)

    def __iter__(self) -> Iterator[ClassStart]:
        return iter(self.sorted_entries())

    def __len__(self) -> int:
        return len(self.entries)

    def entry_for_class(self, class_id: str) -> ClassStart | None:
        for entry in self.entries:
            if entry.class_id == class_id:
                return entry
        return None


@dataclass
class Competition:
    id: str = field(default_factory=_new_id)
    name: str = ""
    event_date: date | None = None
    settings: Settings = field(default_factory=Settings)
    start_locations: dict[str, StartLocation] = field(default_factory=dict)
    courses: dict[str, Course] = field(default_factory=dict)
    classes: dict[str, RaceClass] = field(default_factory=dict)
    competitors: dict[str, Competitor] = field(default_factory=dict)
    plans: dict[str, ClassStartPlan] = field(default_factory=dict)
    # class_name -> course_id assignments from import
    class_course_map: dict[str, str] = field(default_factory=dict)

    def ensure_default_start_location(self) -> StartLocation:
        if DEFAULT_START_LOCATION_ID not in self.start_locations:
            self.start_locations[DEFAULT_START_LOCATION_ID] = StartLocation(
                id=DEFAULT_START_LOCATION_ID,
                name="Lähtö 1",
            )
        return self.start_locations[DEFAULT_START_LOCATION_ID]

    def add_start_location(self, location: StartLocation) -> None:
        self.start_locations[location.id] = location

    def add_course(self, course: Course) -> None:
        self.courses[course.id] = course

    def add_class(self, race_class: RaceClass) -> None:
        if not race_class.start_location_id:
            self.ensure_default_start_location()
            race_class.start_location_id = DEFAULT_START_LOCATION_ID
        self.classes[race_class.id] = race_class

    def add_competitor(self, competitor: Competitor) -> None:
        self.competitors[competitor.id] = competitor

    def remove_competitor(self, competitor_id: str) -> bool:
        """Remove a single competitor by id. Returns True if removed."""
        return self.competitors.pop(competitor_id, None) is not None

    def clear_competitors(self) -> int:
        """Remove all competitors from the competition.

        Locks on the start plan and on classes are left untouched — a
        re-imported roster that grows a locked class past its old anchor
        is rare, and is already surfaced via the `plan.next_day` warning
        and the "(+1 pv)" marker rather than silently unlocked here.

        Returns the number of competitors removed.
        """
        count = len(self.competitors)
        self.competitors.clear()
        return count

    def set_plan(self, plan: ClassStartPlan) -> None:
        self.plans[plan.start_location_id] = plan

    def plan_for(self, start_location_id: str) -> ClassStartPlan | None:
        return self.plans.get(start_location_id)

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

    def competitor_count(self, class_id: str) -> int:
        return len(self.competitors_in_class(class_id))

    def classes_at_location(self, start_location_id: str) -> list[RaceClass]:
        return [
            rc
            for rc in self.classes.values()
            if rc.start_location_id == start_location_id
        ]

    def course_for_class(self, race_class: RaceClass) -> Course | None:
        if not race_class.course_id:
            return None
        return self.courses.get(race_class.course_id)

    def first_control_for_class(self, race_class: RaceClass) -> str | None:
        course = self.course_for_class(race_class)
        return course.first_control if course else None

    def class_span_end(self, rc: RaceClass, first_start: datetime) -> datetime:
        n = max(self.competitor_count(rc.id), 1)
        if n <= 1:
            return first_start
        return first_start + timedelta(minutes=(n - 1) * rc.start_interval_min)

    def class_gap_for_course(self, course_id: str | None) -> int:
        if course_id:
            course = self.courses.get(course_id)
            if course is not None and course.class_gap_min is not None:
                return course.class_gap_min
        return self.settings.class_gap_min

    def competition_start_datetime(self) -> datetime:
        d = self.event_date or date.today()
        return datetime.combine(d, self.settings.competition_start)

    def start_datetime_for(self, start_location_id: str) -> datetime:
        d = self.event_date or date.today()
        loc = self.start_locations.get(start_location_id)
        if loc is not None and loc.first_start is not None:
            return datetime.combine(d, loc.first_start)
        return self.competition_start_datetime()
