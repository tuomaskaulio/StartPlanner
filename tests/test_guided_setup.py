"""Ohjattu "Aloitus"-välilehti uuden kilpailun perustamiselle (v0.9.0 / v0.9.1).

Muut välilehdet piilotetaan kunnes sekä ratatiedot että ilmoittautumiset on
tuotu. Sääntö perustuu kilpailun tietoihin (ei siihen, onko projekti juuri
luotu vai avattu) ja arvioidaan uudelleen joka päivityksellä — jos data
myöhemmin tyhjenee, sovellus palaa Aloitukseen.

v0.9.1 lisää toisen, heikomman portin: ennen kuin käyttäjä on nimenomaisesti
luonut ("Uusi") tai avannut ("Avaa .spc…") kilpailun, Aloitus-sivun
tuontipainikkeet sekä "Kilpailu"- ja "Lähtökaavio"-valikot pysyvät
disabloituina, ja aktiivinen lähtö -yläpalkki piilossa kunnes data on valmis.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from startplanner.domain import (  # noqa: E402
    Competition,
    Competitor,
    Course,
    RaceClass,
    StartLocation,
)
from startplanner.gui.main_window import MainWindow  # noqa: E402


def _qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


def _visible_tab_labels(window: MainWindow) -> set[str]:
    return {
        window._tabs.tabText(i)
        for i in range(window._tabs.count())
        if window._tabs.isTabVisible(i)
    }


def test_fresh_window_shows_only_aloitus():
    _qapp()
    window = MainWindow()
    assert _visible_tab_labels(window) == {"Aloitus"}
    assert window._tabs.currentWidget() is window._start_page
    assert window._tree.topLevelItem(0).childCount() == 1


def test_courses_only_still_gated():
    _qapp()
    window = MainWindow()
    loc = next(iter(window._competition.start_locations.values()))
    course = Course(id="course:1", name="Rata 1", controls=["31"])
    window._competition.add_course(course)
    window._competition.add_class(
        RaceClass(id="class:1", name="H21", course_id=course.id, start_location_id=loc.id)
    )
    window._refresh_all()
    assert _visible_tab_labels(window) == {"Aloitus"}
    assert window._start_build_btn.isHidden()


def test_ready_once_courses_classes_and_competitors_present():
    _qapp()
    window = MainWindow()
    loc = next(iter(window._competition.start_locations.values()))
    course = Course(id="course:1", name="Rata 1", controls=["31"])
    window._competition.add_course(course)
    rc = RaceClass(id="class:1", name="H21", course_id=course.id, start_location_id=loc.id)
    window._competition.add_class(rc)
    window._competition.add_competitor(
        Competitor(id="c1", first_name="A", last_name="B", class_id=rc.id)
    )
    window._refresh_all()
    visible = _visible_tab_labels(window)
    assert "Aloitus" in visible
    assert "Sarjat" in visible
    assert "Lähtökaavio" in visible
    # isVisible() is always False in headless tests (top-level window is
    # never shown); isHidden() reflects the explicit setVisible() call.
    assert not window._start_build_btn.isHidden()


def test_opened_project_with_existing_data_skips_start_page():
    """Simulates opening a .spc that already has data: the gating rule is
    data-presence based, so it must not show an Aloitus-only interlude."""
    _qapp()
    c = Competition(name="Valmis kilpailu")
    loc = StartLocation(id="start:default", name="Lähtö 1")
    c.add_start_location(loc)
    course = Course(id="course:1", name="Rata 1", controls=["31"])
    c.add_course(course)
    rc = RaceClass(id="class:1", name="H21", course_id=course.id, start_location_id=loc.id)
    c.add_class(rc)
    c.add_competitor(Competitor(id="c1", first_name="A", last_name="B", class_id=rc.id))

    window = MainWindow()
    window._competition = c
    window._active_location_id = loc.id
    window._refresh_all()
    window._land_after_load()  # mirrors what _open_project does post-refresh

    assert "Lähdöt" in _visible_tab_labels(window)
    assert window._tabs.currentWidget() is not window._start_page


def test_bulk_clear_returns_to_aloitus(monkeypatch):
    _qapp()
    window = MainWindow()
    loc = next(iter(window._competition.start_locations.values()))
    course = Course(id="course:1", name="Rata 1", controls=["31"])
    window._competition.add_course(course)
    rc = RaceClass(id="class:1", name="H21", course_id=course.id, start_location_id=loc.id)
    window._competition.add_class(rc)
    window._competition.add_competitor(
        Competitor(id="c1", first_name="A", last_name="B", class_id=rc.id)
    )
    window._refresh_all()
    assert "Sarjat" in _visible_tab_labels(window)

    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    window._clear_courses_and_classes()

    assert _visible_tab_labels(window) == {"Aloitus"}
    assert window._tabs.currentWidget() is window._start_page


# --- v0.9.1: has_competition-portti (ennen "Uusi"/"Avaa") -------------------


def test_fresh_window_locks_imports_and_menus():
    _qapp()
    window = MainWindow()
    assert window._has_competition is False
    assert window._start_course_btn.isEnabled() is False
    assert window._start_entries_btn.isEnabled() is False
    assert window._competition_menu.menuAction().isEnabled() is False
    assert window._schedule_menu.menuAction().isEnabled() is False
    # Never shown (ready is False before a competition exists), so the
    # top bar with the active-location dropdown is hidden too.
    assert window._top_bar.isHidden()


def test_has_competition_unlocks_import_buttons_and_menus():
    _qapp()
    window = MainWindow()
    window._has_competition = True
    window._refresh_all()
    assert window._start_course_btn.isEnabled() is True
    assert window._start_entries_btn.isEnabled() is True
    assert window._competition_menu.menuAction().isEnabled() is True
    assert window._schedule_menu.menuAction().isEnabled() is True
    # Not yet ready (no courses/classes/competitors) -> top bar still hidden.
    assert window._top_bar.isHidden()


def test_top_bar_shown_once_ready():
    _qapp()
    window = MainWindow()
    window._has_competition = True
    loc = next(iter(window._competition.start_locations.values()))
    course = Course(id="course:1", name="Rata 1", controls=["31"])
    window._competition.add_course(course)
    rc = RaceClass(id="class:1", name="H21", course_id=course.id, start_location_id=loc.id)
    window._competition.add_class(rc)
    window._competition.add_competitor(
        Competitor(id="c1", first_name="A", last_name="B", class_id=rc.id)
    )
    window._refresh_all()
    assert not window._top_bar.isHidden()


def test_new_project_unlocks_menus_and_buttons(monkeypatch):
    """Drives the real _new_project() code path by monkeypatching the modal
    dialog's exec() to simulate the user accepting it with default values."""
    from PySide6.QtWidgets import QDialog

    from startplanner.gui.main_window import NewCompetitionDialog

    _qapp()
    window = MainWindow()
    monkeypatch.setattr(
        NewCompetitionDialog, "exec", lambda self: QDialog.DialogCode.Accepted
    )
    window._new_project()

    assert window._has_competition is True
    assert window._start_course_btn.isEnabled()
    assert window._start_entries_btn.isEnabled()
    assert window._competition_menu.menuAction().isEnabled()
    assert window._schedule_menu.menuAction().isEnabled()
    assert window._tabs.currentWidget() is window._start_page
