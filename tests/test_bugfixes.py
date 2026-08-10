"""Regression tests for bugs found in a full-codebase review (2026-08).

1. SpcStore.save deleted the existing project file before writing the new
   one, so a failed write (disk full, crash, unrelated bug) destroyed the
   user's data with nothing to replace it. Save must be atomic.
2. MainWindow shared a single HistoryService across all start locations and
   reset it on every combo-box switch, silently discarding undo/redo for
   whichever location the user had just been editing.
3. class_tokens_from_course_name only stripped pure-integer tokens, so a
   decimal course-length token (e.g. "3.2") in a Condes course name leaked
   through as a bogus class token.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import date
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from startplanner.domain import (  # noqa: E402
    Competition,
    Competitor,
    Course,
    RaceClass,
    Settings,
    StartLocation,
)
from startplanner.domain.errors import PersistenceError  # noqa: E402
from startplanner.gui.main_window import MainWindow  # noqa: E402
from startplanner.importers.condes_coursedata import (  # noqa: E402
    class_tokens_from_course_name,
)
from startplanner.persistence.spc_store import SpcStore  # noqa: E402


def _tiny_competition() -> Competition:
    competition = Competition(
        name="Testikilpailu", event_date=date(2026, 8, 15), settings=Settings()
    )
    loc = StartLocation(id="start:default", name="Lähtö 1")
    competition.add_start_location(loc)
    course = Course(id="course:1", name="Rata 1", controls=["31"])
    competition.add_course(course)
    rc = RaceClass(id="class:1", name="H21", course_id=course.id, start_location_id=loc.id)
    competition.add_class(rc)
    return competition


# --- 1. Atomic save --------------------------------------------------------


def test_save_preserves_existing_file_when_write_fails(tmp_path, monkeypatch):
    path = tmp_path / "proj.spc"
    store = SpcStore()
    competition = _tiny_competition()
    store.save(competition, path)
    original_bytes = path.read_bytes()

    def _boom(self, conn, competition) -> None:
        raise sqlite3.OperationalError("disk full (simulated)")

    monkeypatch.setattr(SpcStore, "_write", _boom)

    with pytest.raises(PersistenceError):
        store.save(competition, path)

    assert path.read_bytes() == original_bytes, "old project file was lost on a failed save"
    assert list(tmp_path.glob(".*.tmp-*")) == [], "temp file leaked after a failed save"


def test_save_leaves_no_temp_file_on_success(tmp_path):
    path = tmp_path / "proj.spc"
    SpcStore().save(_tiny_competition(), path)
    assert path.exists()
    assert list(tmp_path.glob(".*.tmp-*")) == []


# --- 2. Per-location undo/redo history -------------------------------------


def _qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_switching_active_location_preserves_undo_history():
    _qapp()
    window = MainWindow()
    competition = window._competition

    loc_a = next(iter(competition.start_locations.values()))
    loc_b = StartLocation(id="start:b", name="Lähtö B")
    competition.add_start_location(loc_b)

    course = Course(id="course:1", name="Rata 1", controls=["31"])
    competition.add_course(course)
    rc_a = RaceClass(id="class:a", name="H21", course_id=course.id, start_location_id=loc_a.id)
    rc_b = RaceClass(id="class:b", name="D21", course_id=course.id, start_location_id=loc_b.id)
    competition.add_class(rc_a)
    competition.add_class(rc_b)
    competition.add_competitor(
        Competitor(id="c1", first_name="A", last_name="B", class_id=rc_a.id)
    )
    competition.add_competitor(
        Competitor(id="c2", first_name="C", last_name="D", class_id=rc_b.id)
    )

    window._active_location_id = loc_a.id
    window._refresh_all()
    window._build_schedule()
    assert window._active_history().can_undo()

    idx_b = window._location_combo.findData(loc_b.id)
    idx_a = window._location_combo.findData(loc_a.id)
    assert idx_b >= 0 and idx_a >= 0

    window._on_location_changed(idx_b)
    window._on_location_changed(idx_a)

    assert window._active_history().can_undo(), (
        "switching the active start location wiped its undo history"
    )


def test_new_location_gets_its_own_fresh_history_without_touching_others():
    _qapp()
    window = MainWindow()
    competition = window._competition
    loc_a = next(iter(competition.start_locations.values()))

    course = Course(id="course:1", name="Rata 1", controls=["31"])
    competition.add_course(course)
    rc_a = RaceClass(id="class:a", name="H21", course_id=course.id, start_location_id=loc_a.id)
    competition.add_class(rc_a)
    competition.add_competitor(
        Competitor(id="c1", first_name="A", last_name="B", class_id=rc_a.id)
    )
    window._active_location_id = loc_a.id
    window._refresh_all()
    window._build_schedule()
    assert window._active_history().can_undo()

    loc_b = StartLocation(id="start:b", name="Lähtö B")
    competition.add_start_location(loc_b)
    window._active_location_id = loc_b.id
    window._active_history()
    assert not window._active_history().can_undo()

    window._active_location_id = loc_a.id
    assert window._active_history().can_undo()


# --- 3. Condes class-token parsing ------------------------------------------


def test_class_tokens_from_course_name_strips_decimal_length_tokens():
    assert class_tokens_from_course_name("3.2 H21") == ["H21"]
    assert class_tokens_from_course_name("H21 3,4") == ["H21"]
    assert class_tokens_from_course_name("6 H75/D60/D65") == ["H75", "D60", "D65"]
