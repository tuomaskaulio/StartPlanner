"""Domain unit tests."""

from datetime import datetime, time

from startplanner.domain import Competition, Competitor, Course, RaceClass, Start, StartSchedule


def test_empty_competition():
    c = Competition()
    assert len(c.classes) == 0
    assert len(c.competitors) == 0


def test_first_control_from_controls():
    course = Course(id="c1", name="A", controls=["59", "40", "M"])
    assert course.first_control == "59"


def test_first_control_empty():
    course = Course(id="c1", name="A", controls=[])
    assert course.first_control is None


def test_start_not_on_competitor():
    comp = Competitor(id="1", first_name="A", last_name="B", class_id="cl")
    assert not hasattr(comp, "start_time")
    start = Start(
        id="s1",
        competitor_id="1",
        class_id="cl",
        course_id="c1",
        start_time=datetime(2025, 1, 1, 12, 0),
        start_number=1,
    )
    schedule = StartSchedule(starts=[start])
    assert len(schedule) == 1


def test_competition_start_datetime_uses_settings():
    c = Competition(name="X")
    c.settings.competition_start = time(10, 30)
    dt = c.competition_start_datetime()
    assert dt.hour == 10 and dt.minute == 30


def test_get_class_by_name():
    c = Competition()
    c.add_class(RaceClass(id="1", name="H21", course_id="c"))
    assert c.get_class_by_name("H21") is not None
    assert c.get_class_by_name("D21") is None
