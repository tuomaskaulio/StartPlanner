"""SQLite .spc project persistence."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, time
from pathlib import Path
from uuid import uuid4

from startplanner.domain import (
    Competition,
    Competitor,
    Course,
    RaceClass,
    Settings,
    Start,
    StartSchedule,
)
from startplanner.domain.errors import PersistenceError

SCHEMA = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS competition (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    event_date TEXT,
    settings_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    length_m INTEGER NOT NULL,
    climb_m INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS course_controls (
    course_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    control_id TEXT NOT NULL,
    PRIMARY KEY (course_id, seq)
);
CREATE TABLE IF NOT EXISTS classes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    course_id TEXT,
    start_interval_min INTEGER NOT NULL,
    estimated_speed REAL NOT NULL,
    sort_order INTEGER NOT NULL,
    locked INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS competitors (
    id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    club TEXT NOT NULL,
    class_id TEXT NOT NULL,
    emit TEXT,
    birth_year INTEGER,
    locked INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS starts (
    id TEXT PRIMARY KEY,
    competitor_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    start_time TEXT NOT NULL,
    start_number INTEGER NOT NULL,
    locked INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS class_course_map (
    class_name TEXT PRIMARY KEY,
    course_id TEXT NOT NULL
);
"""


class SpcStore:
    PROJECT_VERSION = "1"

    def save(self, competition: Competition, path: str | Path) -> None:
        p = Path(path)
        try:
            if p.exists():
                p.unlink()
            conn = sqlite3.connect(p)
            try:
                conn.executescript(SCHEMA)
                self._write(conn, competition)
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error as exc:
            raise PersistenceError(f"Tallennus epäonnistui: {exc}") from exc

    def load(self, path: str | Path) -> Competition:
        p = Path(path)
        if not p.exists():
            raise PersistenceError(f"Projektia ei löydy: {p}")
        try:
            conn = sqlite3.connect(p)
            try:
                return self._read(conn)
            finally:
                conn.close()
        except sqlite3.Error as exc:
            raise PersistenceError(f"Avaus epäonnistui: {exc}") from exc

    def _write(self, conn: sqlite3.Connection, competition: Competition) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            ("project_version", self.PROJECT_VERSION),
        )
        conn.execute(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            ("uuid", competition.id or str(uuid4())),
        )
        conn.execute(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            ("modified", now),
        )
        settings = {
            "default_start_interval_min": competition.settings.default_start_interval_min,
            "class_gap_min": competition.settings.class_gap_min,
            "competition_start": competition.settings.competition_start.strftime("%H:%M"),
        }
        conn.execute(
            "INSERT INTO competition(id, name, event_date, settings_json) VALUES (?, ?, ?, ?)",
            (
                competition.id,
                competition.name,
                competition.event_date.isoformat() if competition.event_date else None,
                json.dumps(settings),
            ),
        )
        for course in competition.courses.values():
            conn.execute(
                "INSERT INTO courses(id, name, length_m, climb_m) VALUES (?, ?, ?, ?)",
                (course.id, course.name, course.length_m, course.climb_m),
            )
            for seq, control in enumerate(course.controls):
                conn.execute(
                    "INSERT INTO course_controls(course_id, seq, control_id) VALUES (?, ?, ?)",
                    (course.id, seq, control),
                )
        for rc in competition.classes.values():
            conn.execute(
                "INSERT INTO classes(id, name, course_id, start_interval_min, "
                "estimated_speed, sort_order, locked) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    rc.id,
                    rc.name,
                    rc.course_id,
                    rc.start_interval_min,
                    rc.estimated_speed,
                    rc.sort_order,
                    int(rc.locked),
                ),
            )
        for comp in competition.competitors.values():
            conn.execute(
                "INSERT INTO competitors(id, first_name, last_name, club, class_id, "
                "emit, birth_year, locked) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    comp.id,
                    comp.first_name,
                    comp.last_name,
                    comp.club,
                    comp.class_id,
                    comp.emit,
                    comp.birth_year,
                    int(comp.locked),
                ),
            )
        for start in competition.schedule.starts:
            conn.execute(
                "INSERT INTO starts(id, competitor_id, class_id, course_id, "
                "start_time, start_number, locked) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    start.id,
                    start.competitor_id,
                    start.class_id,
                    start.course_id,
                    start.start_time.isoformat(timespec="seconds"),
                    start.start_number,
                    int(start.locked),
                ),
            )
        for class_name, course_id in competition.class_course_map.items():
            conn.execute(
                "INSERT INTO class_course_map(class_name, course_id) VALUES (?, ?)",
                (class_name, course_id),
            )

    def _read(self, conn: sqlite3.Connection) -> Competition:
        row = conn.execute(
            "SELECT id, name, event_date, settings_json FROM competition LIMIT 1"
        ).fetchone()
        if not row:
            raise PersistenceError("Projektista puuttuu kilpailutieto")
        settings_data = json.loads(row[3])
        hh, mm = settings_data.get("competition_start", "12:00").split(":")
        settings = Settings(
            default_start_interval_min=int(settings_data.get("default_start_interval_min", 2)),
            class_gap_min=int(settings_data.get("class_gap_min", 2)),
            competition_start=time(int(hh), int(mm)),
        )
        competition = Competition(
            id=row[0],
            name=row[1],
            event_date=date.fromisoformat(row[2]) if row[2] else None,
            settings=settings,
        )
        for c in conn.execute("SELECT id, name, length_m, climb_m FROM courses"):
            controls = [
                r[0]
                for r in conn.execute(
                    "SELECT control_id FROM course_controls WHERE course_id=? ORDER BY seq",
                    (c[0],),
                )
            ]
            competition.add_course(
                Course(id=c[0], name=c[1], length_m=c[2], climb_m=c[3], controls=controls)
            )
        for r in conn.execute(
            "SELECT id, name, course_id, start_interval_min, estimated_speed, sort_order, locked "
            "FROM classes"
        ):
            competition.add_class(
                RaceClass(
                    id=r[0],
                    name=r[1],
                    course_id=r[2],
                    start_interval_min=r[3],
                    estimated_speed=r[4],
                    sort_order=r[5],
                    locked=bool(r[6]),
                )
            )
        for r in conn.execute(
            "SELECT id, first_name, last_name, club, class_id, emit, birth_year, locked "
            "FROM competitors"
        ):
            competition.add_competitor(
                Competitor(
                    id=r[0],
                    first_name=r[1],
                    last_name=r[2],
                    club=r[3],
                    class_id=r[4],
                    emit=r[5],
                    birth_year=r[6],
                    locked=bool(r[7]),
                )
            )
        starts: list[Start] = []
        for r in conn.execute(
            "SELECT id, competitor_id, class_id, course_id, start_time, start_number, locked "
            "FROM starts"
        ):
            starts.append(
                Start(
                    id=r[0],
                    competitor_id=r[1],
                    class_id=r[2],
                    course_id=r[3],
                    start_time=datetime.fromisoformat(r[4]),
                    start_number=r[5],
                    locked=bool(r[6]),
                )
            )
        competition.schedule = StartSchedule(starts=starts)
        for r in conn.execute("SELECT class_name, course_id FROM class_course_map"):
            competition.class_course_map[r[0]] = r[1]
        return competition
