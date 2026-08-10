"""Poisto-ominaisuudet: yksittäinen kilpailija, sarja, rata (v0.8.7).

Aiemmin kilpailijat sai poistaa vain kaikki kerralla, eikä rataa tai sarjaa
voinut poistaa lainkaan. Nämä testit kattavat sekä domain/service-tason
kaskadilogiikan että sen GUI-kytkennän.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from startplanner.domain import (  # noqa: E402
    ClassStart,
    ClassStartPlan,
    Competition,
    Competitor,
    Course,
    RaceClass,
    StartLocation,
)
from startplanner.domain.errors import StartPlannerError  # noqa: E402
from startplanner.gui.main_window import MainWindow  # noqa: E402
from startplanner.services.class_service import ClassService  # noqa: E402
from startplanner.services.competition_service import CompetitionService  # noqa: E402


def _qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


def _basic_competition() -> Competition:
    c = Competition(name="Testi")
    loc = StartLocation(id="start:default", name="Lähtö 1")
    c.add_start_location(loc)
    course = Course(id="course:1", name="Rata 1", controls=["31"])
    c.add_course(course)
    rc = RaceClass(id="class:1", name="H21", course_id=course.id, start_location_id=loc.id)
    c.add_class(rc)
    c.add_competitor(
        Competitor(id="comp:1", first_name="Matti", last_name="Ahola", class_id=rc.id)
    )
    return c


# --- Yksittäisen kilpailijan poisto -----------------------------------------


def test_competition_remove_competitor_removes_only_target():
    c = _basic_competition()
    c.add_competitor(
        Competitor(id="comp:2", first_name="Liisa", last_name="Ojala", class_id="class:1")
    )
    assert c.remove_competitor("comp:1") is True
    assert "comp:1" not in c.competitors
    assert "comp:2" in c.competitors


def test_competition_remove_competitor_unknown_id_returns_false():
    c = _basic_competition()
    assert c.remove_competitor("no-such-id") is False


def test_competition_service_remove_competitor_raises_on_unknown_id():
    c = _basic_competition()
    with pytest.raises(StartPlannerError):
        CompetitionService().remove_competitor(c, "no-such-id")


def test_competition_service_remove_competitor_removes_known_id():
    c = _basic_competition()
    CompetitionService().remove_competitor(c, "comp:1")
    assert "comp:1" not in c.competitors


def test_gui_delete_selected_competitor(monkeypatch):
    _qapp()
    window = MainWindow()
    window._competition = _basic_competition()
    window._active_location_id = "start:default"
    window._refresh_all()

    assert window._competitors_table.rowCount() == 1
    item = window._competitors_table.item(0, 0)
    assert item.data(Qt.UserRole) == "comp:1"
    window._competitors_table.selectRow(0)

    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    window._delete_selected_competitor()

    assert "comp:1" not in window._competition.competitors
    assert window._competitors_table.rowCount() == 0


# --- Radan ja sarjan kaskadipoisto -------------------------------------------


def _competition_with_two_courses() -> Competition:
    c = _basic_competition()
    course2 = Course(id="course:2", name="Rata 2", controls=["41"])
    c.add_course(course2)
    rc2 = RaceClass(
        id="class:2", name="D21", course_id=course2.id, start_location_id="start:default"
    )
    c.add_class(rc2)
    c.add_competitor(
        Competitor(id="comp:2", first_name="Liisa", last_name="Ojala", class_id="class:2")
    )
    c.class_course_map["H21"] = "course:1"
    c.class_course_map["H21-import-only"] = "course:1"
    c.set_plan(
        ClassStartPlan(
            start_location_id="start:default",
            entries=[
                ClassStart(id="s1", class_id="class:1", first_start_time=c.competition_start_datetime()),
                ClassStart(id="s2", class_id="class:2", first_start_time=c.competition_start_datetime()),
            ],
        )
    )
    return c


def test_remove_class_cascades_competitors_and_plan_entries():
    c = _competition_with_two_courses()
    assert c.remove_class("class:1") is True
    assert "class:1" not in c.classes
    assert "comp:1" not in c.competitors
    assert "comp:2" in c.competitors  # untouched
    entry_ids = {e.class_id for e in c.plan_for("start:default").entries}
    assert "class:1" not in entry_ids
    assert "class:2" in entry_ids
    assert "H21" not in c.class_course_map


def test_remove_class_unknown_id_returns_false():
    c = _competition_with_two_courses()
    assert c.remove_class("no-such-id") is False


def test_remove_course_cascades_all_its_classes_and_import_only_map_entries():
    c = _competition_with_two_courses()
    assert c.remove_course("course:1") is True
    assert "course:1" not in c.courses
    assert "class:1" not in c.classes
    assert "comp:1" not in c.competitors
    # course:2 / class:2 untouched
    assert "course:2" in c.courses
    assert "class:2" in c.classes
    assert "comp:2" in c.competitors
    # import-only mapping (never became a RaceClass) also cleaned up
    assert "H21-import-only" not in c.class_course_map


def test_remove_course_unknown_id_returns_false():
    c = _competition_with_two_courses()
    assert c.remove_course("no-such-id") is False


def test_clear_courses_and_classes_wipes_everything_but_keeps_settings():
    c = _competition_with_two_courses()
    n_courses, n_classes = c.clear_courses_and_classes()
    assert (n_courses, n_classes) == (2, 2)
    assert c.courses == {}
    assert c.classes == {}
    assert c.competitors == {}
    assert c.class_course_map == {}
    assert c.name == "Testi"
    assert "start:default" in c.start_locations


def test_class_service_remove_class_raises_on_unknown_id():
    c = _competition_with_two_courses()
    with pytest.raises(StartPlannerError):
        ClassService().remove_class(c, "no-such-id")


def test_class_service_remove_course_raises_on_unknown_id():
    c = _competition_with_two_courses()
    with pytest.raises(StartPlannerError):
        ClassService().remove_course(c, "no-such-id")


def test_class_service_remove_class_and_course_delegate_to_domain():
    c = _competition_with_two_courses()
    ClassService().remove_class(c, "class:2")
    assert "class:2" not in c.classes
    ClassService().remove_course(c, "course:1")
    assert "course:1" not in c.courses
    assert "class:1" not in c.classes


def test_gui_delete_selected_class_and_course(monkeypatch):
    _qapp()
    window = MainWindow()
    window._competition = _competition_with_two_courses()
    window._active_location_id = "start:default"
    window._refresh_all()

    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))

    class_id = window._selected_classes_table_class_id()
    # No row selected yet -> None; select first row and retry.
    assert class_id is None
    window._classes_table.selectRow(0)
    class_id = window._selected_classes_table_class_id()
    assert class_id in window._competition.classes
    window._delete_selected_class()
    assert class_id not in window._competition.classes

    window._courses_table.selectRow(0)
    course_id = window._selected_course_id()
    assert course_id in window._competition.courses
    window._delete_selected_course()
    assert course_id not in window._competition.courses


def test_gui_clear_courses_and_classes(monkeypatch):
    _qapp()
    window = MainWindow()
    window._competition = _competition_with_two_courses()
    window._active_location_id = "start:default"
    window._refresh_all()

    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    window._clear_courses_and_classes()

    assert window._competition.courses == {}
    assert window._competition.classes == {}
    assert window._competition.competitors == {}
