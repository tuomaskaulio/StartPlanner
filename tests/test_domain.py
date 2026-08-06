"""Domain unit tests."""

from datetime import datetime, time

from startplanner.domain import (
    DEFAULT_START_LOCATION_ID,
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
    format_start_time,
)


def test_empty_competition():
    c = Competition()
    assert len(c.classes) == 0
    assert len(c.competitors) == 0


def test_default_start_location_on_add_class():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    assert DEFAULT_START_LOCATION_ID in c.start_locations
    assert c.classes["1"].start_location_id == DEFAULT_START_LOCATION_ID


def test_first_control_from_controls():
    course = Course(id="c1", name="A", controls=["59", "40", "M"])
    assert course.first_control == "59"


def test_class_start_plan():
    plan = ClassStartPlan(
        start_location_id="start:default",
        entries=[
            ClassStart(
                id="e1",
                class_id="h21",
                first_start_time=datetime(2025, 1, 1, 12, 0),
            )
        ],
    )
    assert len(plan) == 1
    assert plan.entry_for_class("h21") is not None


def test_competition_start_datetime_uses_settings():
    c = Competition(name="X")
    c.settings.competition_start = time(10, 30)
    dt = c.competition_start_datetime()
    assert dt.hour == 10 and dt.minute == 30


def test_start_datetime_for_location_override():
    c = Competition(name="X")
    c.settings.competition_start = time(12, 0)
    c.ensure_default_start_location()
    loc = c.start_locations[DEFAULT_START_LOCATION_ID]
    assert c.start_datetime_for(loc.id).hour == 12
    loc.first_start = time(9, 15)
    assert c.start_datetime_for(loc.id).hour == 9
    assert c.start_datetime_for(loc.id).minute == 15


def test_sorted_entries_by_class_order():
    plan = ClassStartPlan(
        start_location_id="start:default",
        entries=[
            ClassStart(
                id="e1",
                class_id="b",
                first_start_time=datetime(2025, 1, 1, 12, 0),
            ),
            ClassStart(
                id="e2",
                class_id="a",
                first_start_time=datetime(2025, 1, 1, 12, 10),
            ),
        ],
    )
    orders = {"a": 1, "b": 2}
    names = {"a": "A", "b": "B"}
    by_class = plan.sorted_entries(
        by="class", class_sort_order=orders, class_names=names
    )
    assert [e.class_id for e in by_class] == ["a", "b"]
    by_time = plan.sorted_entries(
        by="time", class_sort_order=orders, class_names=names
    )
    assert [e.class_id for e in by_time] == ["b", "a"]


def test_competitor_count():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    c.add_competitor(Competitor(id="a", first_name="A", last_name="B", class_id="1"))
    assert c.competitor_count("1") == 1


def test_clear_competitors():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    c.add_competitor(Competitor(id="a", first_name="A", last_name="B", class_id="1"))
    c.add_competitor(Competitor(id="b", first_name="C", last_name="D", class_id="1"))
    removed = c.clear_competitors()
    assert removed == 2
    assert len(c.competitors) == 0
    assert c.competitor_count("1") == 0


def test_format_start_time_same_day():
    from datetime import date

    value = datetime(2026, 8, 6, 13, 45)
    assert format_start_time(value, date(2026, 8, 6)) == "13:45"


def test_format_start_time_next_day():
    from datetime import date

    value = datetime(2026, 8, 7, 0, 15)
    assert format_start_time(value, date(2026, 8, 6)) == "00:15 (+1 pv)"


def test_format_start_time_no_event_date():
    value = datetime(2026, 8, 7, 0, 15)
    assert format_start_time(value, None) == "00:15"


def test_clear_competitors_empty():
    c = Competition()
    assert c.clear_competitors() == 0
    assert len(c.competitors) == 0


def test_remove_competitor():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    c.add_competitor(Competitor(id="a", first_name="A", last_name="B", class_id="1"))
    assert c.remove_competitor("a") is True
    assert len(c.competitors) == 0
    assert c.remove_competitor("a") is False


def test_competition_service_clear_competitors():
    from startplanner.services.competition_service import CompetitionService

    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    c.add_competitor(Competitor(id="a", first_name="A", last_name="B", class_id="1"))
    c.add_competitor(Competitor(id="b", first_name="C", last_name="D", class_id="1"))
    removed = CompetitionService().clear_competitors(c)
    assert removed == 2
    assert len(c.competitors) == 0


def test_new_competition_with_settings():
    """CompetitionService.new_competition accepts name, event_date, and settings."""
    from datetime import date

    from startplanner.domain import Settings
    from startplanner.services.competition_service import CompetitionService

    service = CompetitionService()
    competition = service.new_competition(
        name="Testikilpailu",
        event_date=date(2026, 6, 15),
        settings=Settings(
            default_start_interval_min=3,
            class_gap_min=5,
            competition_start=time(10, 30),
        ),
    )
    assert competition.name == "Testikilpailu"
    assert competition.event_date == date(2026, 6, 15)
    assert competition.settings.default_start_interval_min == 3
    assert competition.settings.class_gap_min == 5
    assert competition.settings.competition_start == time(10, 30)
    assert DEFAULT_START_LOCATION_ID in competition.start_locations
