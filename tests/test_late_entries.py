"""Jälki-ilmoittautuneiden seuranta (v0.9.4).

Kilpailijoille tallennetaan nyt pysyvä `late`-lippu sen mukaan, tuotiinko
heidät "Tuo ilmoittautumiset" vai "Tuo jälki-ilmoittautuneet" -toiminnolla.
Aiemmin `late`-parametri vaikutti vain tiedostonvalintadialogin otsikkoon,
ei tallennettuun dataan.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFileDialog  # noqa: E402

from startplanner.domain import Competition, Competitor, RaceClass, StartLocation  # noqa: E402
from startplanner.gui.main_window import MainWindow  # noqa: E402
from startplanner.importers.irma_ilmoit import IrmaIlmoitImporter  # noqa: E402
from startplanner.persistence.spc_store import SpcStore  # noqa: E402
from startplanner.services.competition_service import CompetitionService  # noqa: E402
from startplanner.services.import_service import ImportService  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MEDIUM = ROOT / "samples" / "sample-medium"
ENTRIES_CSV = SAMPLE_MEDIUM / "ilmoittautumiset.csv"
LATE_ENTRIES_CSV = SAMPLE_MEDIUM / "jalki_ilmoittautumiset.csv"


def _qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


def _basic_competition() -> Competition:
    c = Competition(name="Testi")
    loc = StartLocation(id="start:default", name="Lähtö 1")
    c.add_start_location(loc)
    c.add_class(RaceClass(id="class:1", name="H21", start_location_id=loc.id))
    return c


# --- Domain -------------------------------------------------------------


def test_competitor_late_defaults_to_false():
    comp = Competitor(id="1", first_name="A", last_name="B")
    assert comp.late is False


def test_competitor_late_true():
    comp = Competitor(id="1", first_name="A", last_name="B", late=True)
    assert comp.late is True


# --- Importer / service --------------------------------------------------


def test_irma_importer_apply_to_tags_late_when_requested():
    c = _basic_competition()
    IrmaIlmoitImporter().apply_to(c, LATE_ENTRIES_CSV, late=True)
    assert c.competitors
    assert all(comp.late for comp in c.competitors.values())


def test_irma_importer_apply_to_defaults_to_not_late():
    c = _basic_competition()
    IrmaIlmoitImporter().apply_to(c, ENTRIES_CSV)
    assert c.competitors
    assert all(not comp.late for comp in c.competitors.values())


def test_import_service_threads_late_flag():
    c = _basic_competition()
    ImportService().import_entries(c, ENTRIES_CSV, late=False)
    ImportService().import_entries(c, LATE_ENTRIES_CSV, late=True)
    assert any(comp.late for comp in c.competitors.values())
    assert any(not comp.late for comp in c.competitors.values())


# --- Persistence -----------------------------------------------------------


def test_spc_roundtrip_preserves_late_flag(tmp_path):
    c = _basic_competition()
    c.add_competitor(
        Competitor(id="a", first_name="A", last_name="A", class_id="class:1", late=False)
    )
    c.add_competitor(
        Competitor(id="b", first_name="B", last_name="B", class_id="class:1", late=True)
    )
    path = tmp_path / "roundtrip.spc"
    svc = CompetitionService()
    svc.save(c, path)
    loaded = svc.load(path)
    assert loaded.competitors["a"].late is False
    assert loaded.competitors["b"].late is True


def test_load_old_spc_without_late_column_defaults_to_false(tmp_path):
    """Simulates a .spc saved before v0.9.4 (no `late` column on
    competitors) — must still load, defaulting every competitor to False."""
    path = tmp_path / "old.spc"
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE competition (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, event_date TEXT,
            settings_json TEXT NOT NULL
        );
        CREATE TABLE start_locations (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, first_start TEXT
        );
        CREATE TABLE courses (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, length_m INTEGER NOT NULL,
            climb_m INTEGER NOT NULL, class_gap_min INTEGER
        );
        CREATE TABLE course_controls (
            course_id TEXT NOT NULL, seq INTEGER NOT NULL, control_id TEXT NOT NULL,
            PRIMARY KEY (course_id, seq)
        );
        CREATE TABLE classes (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, course_id TEXT,
            start_location_id TEXT, start_interval_min INTEGER NOT NULL,
            estimated_speed REAL NOT NULL, sort_order INTEGER NOT NULL,
            course_order INTEGER NOT NULL, locked INTEGER NOT NULL,
            empty_slots_before INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE competitors (
            id TEXT PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            club TEXT NOT NULL, class_id TEXT NOT NULL, emit TEXT,
            birth_year INTEGER, locked INTEGER NOT NULL
        );
        CREATE TABLE class_starts (
            id TEXT PRIMARY KEY, start_location_id TEXT NOT NULL, class_id TEXT NOT NULL,
            first_start_time TEXT NOT NULL, locked INTEGER NOT NULL
        );
        CREATE TABLE class_course_map (
            class_name TEXT PRIMARY KEY, course_id TEXT NOT NULL
        );
        """
    )
    conn.execute(
        "INSERT INTO competition(id, name, event_date, settings_json) VALUES (?, ?, ?, ?)",
        (
            "comp:1",
            "Vanha kilpailu",
            None,
            '{"default_start_interval_min": 2, "class_gap_min": 2, "competition_start": "12:00"}',
        ),
    )
    conn.execute(
        "INSERT INTO start_locations(id, name, first_start) VALUES (?, ?, ?)",
        ("start:default", "Lähtö 1", None),
    )
    conn.execute(
        "INSERT INTO classes(id, name, course_id, start_location_id, start_interval_min, "
        "estimated_speed, sort_order, course_order, locked, empty_slots_before) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("class:1", "H21", None, "start:default", 2, 0.0, 0, 0, 0, 0),
    )
    conn.execute(
        "INSERT INTO competitors(id, first_name, last_name, club, class_id, emit, "
        "birth_year, locked) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("comp:1", "Matti", "Ahola", "", "class:1", None, None, 0),
    )
    conn.commit()
    conn.close()

    loaded = SpcStore().load(path)
    comp = loaded.competitors["comp:1"]
    assert comp.late is False


# --- GUI ---------------------------------------------------------------


def test_start_late_entries_button_gated_by_has_competition():
    _qapp()
    window = MainWindow()
    assert window._start_late_entries_btn.isEnabled() is False
    window._has_competition = True
    window._refresh_all()
    assert window._start_late_entries_btn.isEnabled() is True


def test_start_late_entries_button_imports_and_tags_late(monkeypatch):
    _qapp()
    window = MainWindow()
    window._has_competition = True
    window._competition = _basic_competition()
    window._active_location_id = "start:default"
    window._refresh_all()

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *a, **k: (str(LATE_ENTRIES_CSV), "")),
    )
    window._start_late_entries_btn.click()

    assert window._competition.competitors
    assert all(comp.late for comp in window._competition.competitors.values())


def test_refresh_start_page_shows_late_count():
    _qapp()
    window = MainWindow()
    window._has_competition = True
    window._competition = _basic_competition()
    window._competition.add_competitor(
        Competitor(id="a", first_name="A", last_name="A", class_id="class:1", late=False)
    )
    window._competition.add_competitor(
        Competitor(id="b", first_name="B", last_name="B", class_id="class:1", late=True)
    )
    window._active_location_id = "start:default"
    window._refresh_all()

    text = window._start_entries_status.text()
    assert "2 kilpailijaa" in text
    assert "1 jälki-ilmoittautunutta" in text
