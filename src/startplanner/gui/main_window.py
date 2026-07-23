"""PySide6 main window for ClassStartPlan workflow (v0.4)."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTimeEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from startplanner.domain import ClassStart, ClassStartPlan, Competition, StartLocation
from startplanner.domain.errors import ScheduleError, StartPlannerError
from startplanner.services.competition_service import CompetitionService
from startplanner.services.history_service import HistoryService
from startplanner.services.import_service import ExportService, ImportService
from startplanner.services.optimizer_service import OptimizerService
from startplanner.services.quality_service import QualityService
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService


class SettingsDialog(QDialog):
    def __init__(self, competition: Competition, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Kilpailun asetukset")
        self._competition = competition
        layout = QFormLayout(self)
        self._interval = QSpinBox()
        self._interval.setRange(1, 30)
        self._interval.setValue(competition.settings.default_start_interval_min)
        self._gap = QSpinBox()
        self._gap.setRange(0, 60)
        self._gap.setValue(competition.settings.class_gap_min)
        self._start = QTimeEdit()
        self._start.setDisplayFormat("HH:mm")
        cs = competition.settings.competition_start
        self._start.setTime(QTime(cs.hour, cs.minute))
        layout.addRow("Oletuslähtöväli (min)", self._interval)
        layout.addRow("Sarjojen väli (min)", self._gap)
        layout.addRow("Kilpailun aloitusaika", self._start)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def apply(self) -> None:
        self._competition.settings.default_start_interval_min = self._interval.value()
        self._competition.settings.class_gap_min = self._gap.value()
        t = self._start.time()
        from datetime import time as dtime

        self._competition.settings.competition_start = dtime(t.hour(), t.minute())


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StartPlanner 0.4")
        self.resize(1200, 750)

        self._competition = Competition(name="Uusi kilpailu")
        self._competition.ensure_default_start_location()
        self._active_location_id = next(iter(self._competition.start_locations))
        self._project_path: Path | None = None
        self._competition_service = CompetitionService()
        self._import_service = ImportService()
        self._export_service = ExportService()
        self._scheduler = SchedulerService()
        self._validator = ValidationService()
        self._quality = QualityService()
        self._optimizer = OptimizerService()
        self._history = HistoryService()
        self._history_baseline()

        self._build_ui()
        self._refresh_all()

    def _history_baseline(self) -> None:
        self._history.clear()
        plan = self._competition.plan_for(self._active_location_id)
        self._history.push("Alku", plan)

    def _record_plan(self, description: str) -> None:
        plan = self._competition.plan_for(self._active_location_id)
        self._history.push(description, plan)

    def _build_ui(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("Tiedosto")
        file_menu.addAction("Uusi", self._new_project)
        file_menu.addAction("Avaa .spc…", self._open_project)
        file_menu.addAction("Tallenna", self._save_project)
        file_menu.addAction("Tallenna nimellä…", self._save_project_as)
        file_menu.addSeparator()
        file_menu.addAction("Tuo CourseData…", self._import_coursedata)
        file_menu.addAction("Tuo ilmoittautumiset…", self._import_entries)
        file_menu.addSeparator()
        file_menu.addAction("Vie Excel…", self._export_excel)
        file_menu.addAction("Vie CSV…", self._export_csv)

        edit_menu = menu.addMenu("Muokkaa")
        self._undo_action = edit_menu.addAction("Kumoa", self._undo)
        self._undo_action.setShortcut("Ctrl+Z")
        self._redo_action = edit_menu.addAction("Tee uudelleen", self._redo)
        self._redo_action.setShortcut("Ctrl+Shift+Z")
        edit_menu.addSeparator()
        edit_menu.addAction("Kilpailun asetukset…", self._edit_settings)

        schedule_menu = menu.addMenu("Lähtökaavio")
        schedule_menu.addAction("Muodosta lähtökaavio (aktiivinen lähtö)", self._build_schedule)
        schedule_menu.addAction("Optimoi (aktiivinen lähtö)", self._optimize)
        schedule_menu.addAction("Validoi", self._validate)
        schedule_menu.addSeparator()
        schedule_menu.addAction("Siirrä valittu sarja…", self._move_selected_class)
        schedule_menu.addAction("Lukitse / avaa valittu sarja", self._toggle_lock_selected)
        schedule_menu.addSeparator()
        schedule_menu.addAction("Lisää lähtö…", self._add_start_location)

        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.addWidget(QLabel("Aktiivinen lähtö:"))
        self._location_combo = QComboBox()
        self._location_combo.currentIndexChanged.connect(self._on_location_changed)
        top_layout.addWidget(self._location_combo, stretch=1)
        self._quality_label = QLabel("Laatu: —")
        top_layout.addWidget(self._quality_label)

        splitter = QSplitter()
        self._tree = QTreeWidget()
        self._tree.setHeaderLabel("Kilpailu")
        self._tree.itemClicked.connect(self._on_tree_clicked)
        splitter.addWidget(self._tree)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(top)
        self._tabs = QTabWidget()
        self._classes_table = QTableWidget()
        self._courses_table = QTableWidget()
        self._competitors_table = QTableWidget()
        self._plan_table = QTableWidget()
        self._plan_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._plan_table.customContextMenuRequested.connect(self._plan_context_menu)
        self._plan_table.cellDoubleClicked.connect(self._plan_double_clicked)
        self._timeline_table = QTableWidget()
        self._issues_table = QTableWidget()
        self._tabs.addTab(self._classes_table, "Sarjat")
        self._tabs.addTab(self._courses_table, "Radat")
        self._tabs.addTab(self._competitors_table, "Kilpailijat")
        self._tabs.addTab(self._plan_table, "Lähtökaavio")
        self._tabs.addTab(self._timeline_table, "Aikajana")
        self._tabs.addTab(self._issues_table, "Issues")
        right_layout.addWidget(self._tabs)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 3)

        self.setCentralWidget(splitter)
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status_label = QLabel()
        self._status.addWidget(self._status_label)
        self._update_history_actions()

    def _update_history_actions(self) -> None:
        self._undo_action.setEnabled(self._history.can_undo())
        self._redo_action.setEnabled(self._history.can_redo())

    def _new_project(self) -> None:
        self._competition = Competition(name="Uusi kilpailu")
        self._competition.ensure_default_start_location()
        self._active_location_id = next(iter(self._competition.start_locations))
        self._project_path = None
        self._history_baseline()
        self._refresh_all()

    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Avaa projekti", "", "StartPlanner (*.spc)")
        if not path:
            return
        try:
            self._competition = self._competition_service.load(path)
            self._competition.ensure_default_start_location()
            self._active_location_id = next(iter(self._competition.start_locations))
            self._project_path = Path(path)
            self._history_baseline()
            self._refresh_all()
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Virhe", str(exc))

    def _save_project(self) -> None:
        if self._project_path is None:
            self._save_project_as()
            return
        try:
            self._competition_service.save(self._competition, self._project_path)
            self._status.showMessage(f"Tallennettu: {self._project_path}", 3000)
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Virhe", str(exc))

    def _save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Tallenna projekti", "", "StartPlanner (*.spc)")
        if not path:
            return
        if not path.endswith(".spc"):
            path += ".spc"
        self._project_path = Path(path)
        self._save_project()

    def _import_coursedata(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Tuo CourseData", "", "XML (*.xml);;All (*)"
        )
        if not path:
            return
        try:
            self._competition = self._import_service.import_coursedata(
                path, self._competition
            )
            self._active_location_id = next(iter(self._competition.start_locations))
            self._history_baseline()
            self._refresh_all()
            self._status.showMessage(f"CourseData tuotu: {Path(path).name}", 4000)
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Tuontivirhe", str(exc))

    def _import_entries(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Tuo ilmoittautumiset", "", "CSV (*.csv);;All (*)"
        )
        if not path:
            return
        try:
            n = self._import_service.import_entries(self._competition, path)
            self._refresh_all()
            self._status.showMessage(f"Tuotu {n} kilpailijaa", 4000)
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Tuontivirhe", str(exc))

    def _build_schedule(self) -> None:
        try:
            plan = self._scheduler.apply(self._competition, self._active_location_id)
            self._record_plan("Muodosta lähtökaavio")
            self._refresh_all()
            self._tabs.setCurrentWidget(self._plan_table)
            score = self._quality.score(self._competition, self._active_location_id)
            self._status.showMessage(
                f"Lähtökaavio: {len(plan)} sarjaa · laatu {score.as_text()}", 5000
            )
        except ScheduleError as exc:
            QMessageBox.warning(self, "Ei voida muodostaa", str(exc))
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Virhe", str(exc))

    def _optimize(self) -> None:
        if not self._competition.plan_for(self._active_location_id):
            QMessageBox.information(self, "Optimoi", "Muodosta ensin lähtökaavio.")
            return
        try:
            before = self._quality.score(self._competition, self._active_location_id)
            plan = self._optimizer.optimize(self._competition, self._active_location_id)
            self._record_plan("Optimoi")
            self._refresh_all()
            after = self._quality.score(self._competition, self._active_location_id)
            self._tabs.setCurrentWidget(self._plan_table)
            self._status.showMessage(
                f"Optimoitu ({len(plan)} sarjaa): {before.total} → {after.total}",
                5000,
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Optimointi", str(exc))

    def _validate(self) -> None:
        self._refresh_issues()
        self._tabs.setCurrentWidget(self._issues_table)

    def _edit_settings(self) -> None:
        dlg = SettingsDialog(self._competition, self)
        if dlg.exec() != QDialog.Accepted:
            return
        dlg.apply()
        self._refresh_all()
        self._status.showMessage("Asetukset päivitetty", 3000)

    def _undo(self) -> None:
        snap = self._history.undo()
        if snap is None:
            return
        self._apply_plan_snapshot(snap.plan)
        self._refresh_all()
        self._status.showMessage(f"Kumottu → {snap.description}", 3000)

    def _redo(self) -> None:
        snap = self._history.redo()
        if snap is None:
            return
        self._apply_plan_snapshot(snap.plan)
        self._refresh_all()
        self._status.showMessage(f"Toistettu: {snap.description}", 3000)

    def _apply_plan_snapshot(self, plan: ClassStartPlan | None) -> None:
        if plan is None:
            self._competition.plans.pop(self._active_location_id, None)
        else:
            self._competition.set_plan(deepcopy(plan))

    def _add_start_location(self) -> None:
        name, ok = QInputDialog.getText(self, "Lisää lähtö", "Lähdön nimi:")
        if not ok or not name.strip():
            return
        loc = StartLocation(id=f"start:{uuid4()}", name=name.strip())
        self._competition.add_start_location(loc)
        self._active_location_id = loc.id
        self._history_baseline()
        self._refresh_all()

    def _selected_plan_class_id(self) -> str | None:
        row = self._plan_table.currentRow()
        if row < 0:
            return None
        item = self._plan_table.item(row, 1)
        if not item:
            return None
        name = item.text()
        rc = self._competition.get_class_by_name(name)
        return rc.id if rc else None

    def _move_selected_class(self) -> None:
        class_id = self._selected_plan_class_id()
        if not class_id:
            QMessageBox.information(self, "Siirrä", "Valitse sarja lähtökaaviosta.")
            return
        plan = self._competition.plan_for(self._active_location_id)
        if not plan:
            return
        entry = plan.entry_for_class(class_id)
        if not entry:
            return
        rc = self._competition.classes.get(class_id)
        if rc and (rc.locked or entry.locked):
            QMessageBox.warning(self, "Siirrä", "Sarja on lukittu.")
            return
        current = entry.first_start_time.strftime("%H:%M")
        text, ok = QInputDialog.getText(
            self, "Siirrä sarja", "Uusi 1. lähtöaika (HH:MM):", text=current
        )
        if not ok or not text.strip():
            return
        try:
            hh, mm = text.strip().split(":")
            new_time = entry.first_start_time.replace(hour=int(hh), minute=int(mm), second=0)
        except ValueError:
            QMessageBox.warning(self, "Siirrä", "Anna aika muodossa HH:MM.")
            return
        self._set_class_first_time(class_id, new_time, "Siirrä sarja")

    def _toggle_lock_selected(self) -> None:
        class_id = self._selected_plan_class_id()
        if not class_id:
            QMessageBox.information(self, "Lukitse", "Valitse sarja lähtökaaviosta.")
            return
        plan = self._competition.plan_for(self._active_location_id)
        if not plan or not plan.entry_for_class(class_id):
            return
        entries = []
        for e in plan.entries:
            locked = e.locked
            if e.class_id == class_id:
                locked = not e.locked
            entries.append(
                ClassStart(
                    id=e.id,
                    class_id=e.class_id,
                    first_start_time=e.first_start_time,
                    locked=locked,
                )
            )
        self._competition.set_plan(
            ClassStartPlan(start_location_id=plan.start_location_id, entries=entries)
        )
        self._record_plan("Lukitse/avaa")
        self._refresh_all()

    def _set_class_first_time(
        self, class_id: str, new_time: datetime, description: str
    ) -> None:
        plan = self._competition.plan_for(self._active_location_id)
        if not plan:
            return
        entries = []
        for e in plan.entries:
            if e.class_id == class_id:
                entries.append(
                    ClassStart(
                        id=str(uuid4()),
                        class_id=e.class_id,
                        first_start_time=new_time,
                        locked=e.locked,
                    )
                )
            else:
                entries.append(e)
        self._competition.set_plan(
            ClassStartPlan(start_location_id=plan.start_location_id, entries=entries)
        )
        self._record_plan(description)
        self._refresh_all()

    def _plan_double_clicked(self, row: int, _col: int) -> None:
        self._plan_table.selectRow(row)
        self._move_selected_class()

    def _plan_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.addAction("Siirrä…", self._move_selected_class)
        menu.addAction("Lukitse / avaa", self._toggle_lock_selected)
        menu.exec(self._plan_table.viewport().mapToGlobal(pos))

    def _export_excel(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Vie Excel", "", "Excel (*.xlsx)")
        if not path:
            return
        if not path.endswith(".xlsx"):
            path += ".xlsx"
        try:
            self._export_service.export_excel(self._competition, path)
            self._status.showMessage(f"Viety: {path}", 4000)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Vientivirhe", str(exc))

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Vie CSV", "", "CSV (*.csv)")
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"
        try:
            self._export_service.export_csv(self._competition, path)
            self._status.showMessage(f"Viety: {path}", 4000)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Vientivirhe", str(exc))

    def _on_location_changed(self, index: int) -> None:
        if index < 0:
            return
        loc_id = self._location_combo.itemData(index)
        if loc_id:
            self._active_location_id = loc_id
            self._history_baseline()
            self._refresh_plan_and_status()

    def _on_tree_clicked(self, item: QTreeWidgetItem, _col: int) -> None:
        mapping = {
            "Sarjat": self._classes_table,
            "Radat": self._courses_table,
            "Kilpailijat": self._competitors_table,
            "Lähtökaavio": self._plan_table,
            "Aikajana": self._timeline_table,
            "Issues": self._issues_table,
        }
        key = item.text(0)
        if key in mapping:
            self._tabs.setCurrentWidget(mapping[key])

    def _refresh_location_combo(self) -> None:
        self._location_combo.blockSignals(True)
        self._location_combo.clear()
        for loc in sorted(
            self._competition.start_locations.values(), key=lambda x: x.name
        ):
            self._location_combo.addItem(loc.name, loc.id)
        idx = self._location_combo.findData(self._active_location_id)
        if idx >= 0:
            self._location_combo.setCurrentIndex(idx)
        elif self._location_combo.count():
            self._location_combo.setCurrentIndex(0)
            self._active_location_id = self._location_combo.currentData()
        self._location_combo.blockSignals(False)

    def _refresh_all(self) -> None:
        self._competition.ensure_default_start_location()
        if self._active_location_id not in self._competition.start_locations:
            self._active_location_id = next(iter(self._competition.start_locations))
        self._refresh_location_combo()
        self._refresh_tree()
        self._fill_table(
            self._classes_table,
            ["Sarja", "Lähtö", "Rata", "Kilpailijoita", "Lähtöväli"],
            [
                [
                    rc.name,
                    (
                        self._competition.start_locations[rc.start_location_id].name
                        if rc.start_location_id in self._competition.start_locations
                        else "—"
                    ),
                    (
                        self._competition.courses[rc.course_id].name
                        if rc.course_id in self._competition.courses
                        else "—"
                    ),
                    str(self._competition.competitor_count(rc.id)),
                    str(rc.start_interval_min),
                ]
                for rc in sorted(self._competition.classes.values(), key=lambda c: c.name)
            ],
        )
        self._fill_table(
            self._courses_table,
            ["Rata", "Pituus (m)", "Nousu", "1. rasti", "Rasteja"],
            [
                [
                    c.name,
                    str(c.length_m),
                    str(c.climb_m),
                    c.first_control or "—",
                    str(len(c.controls)),
                ]
                for c in sorted(self._competition.courses.values(), key=lambda x: x.name)
            ],
        )
        self._fill_table(
            self._competitors_table,
            ["Nimi", "Seura", "Sarja", "Emit"],
            [
                [
                    comp.full_name,
                    comp.club,
                    self._competition.classes[comp.class_id].name
                    if comp.class_id in self._competition.classes
                    else "—",
                    comp.emit or "",
                ]
                for comp in sorted(
                    self._competition.competitors.values(),
                    key=lambda c: (c.last_name, c.first_name),
                )
            ],
        )
        self._refresh_plan_and_status()
        self._refresh_issues()
        self._update_history_actions()

    def _refresh_plan_and_status(self) -> None:
        plan = self._competition.plan_for(self._active_location_id)
        rows: list[list[str]] = []
        if plan:
            for entry in plan.sorted_entries():
                rc = self._competition.classes.get(entry.class_id)
                course = self._competition.course_for_class(rc) if rc else None
                rows.append(
                    [
                        entry.first_start_time.strftime("%H:%M"),
                        rc.name if rc else "",
                        str(self._competition.competitor_count(entry.class_id)),
                        str(rc.start_interval_min if rc else ""),
                        course.name if course else "",
                        (course.first_control if course else "") or "",
                        "kyllä" if entry.locked or (rc and rc.locked) else "",
                    ]
                )
        self._fill_table(
            self._plan_table,
            ["1. lähtöaika", "Sarja", "Kilpailijoita", "Lähtöväli", "Rata", "1. rasti", "Lukittu"],
            rows,
        )
        self._refresh_timeline(plan)
        c = self._competition
        loc = c.start_locations.get(self._active_location_id)
        plan_n = len(plan) if plan else 0
        if plan and plan.entries:
            score = self._quality.score(c, self._active_location_id)
            self._quality_label.setText(f"Laatu: {score.as_text()}")
        else:
            self._quality_label.setText("Laatu: —")
        self._status_label.setText(
            f"{c.name}  |  Lähtö: {loc.name if loc else '—'}  |  "
            f"Sarjoja {len(c.classes)}  |  "
            f"Kilpailijoita {len(c.competitors)}  |  "
            f"Kaavion sarjoja {plan_n}"
        )
        self._update_history_actions()

    def _refresh_timeline(self, plan: ClassStartPlan | None) -> None:
        if not plan or not plan.entries:
            self._fill_table(self._timeline_table, ["Aika", "Sarjat lähdössä"], [])
            return
        minute_classes: dict[datetime, list[str]] = {}
        for entry in plan.sorted_entries():
            rc = self._competition.classes.get(entry.class_id)
            if not rc:
                continue
            n = max(self._competition.competitor_count(rc.id), 1)
            for i in range(n):
                minute = (
                    entry.first_start_time
                    + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
                minute_classes.setdefault(minute, []).append(rc.name)
        rows = [
            [m.strftime("%H:%M"), ", ".join(names)]
            for m, names in sorted(minute_classes.items())
        ]
        self._fill_table(self._timeline_table, ["Aika", "Sarjat lähdössä"], rows)

    def _refresh_issues(self) -> None:
        report = self._validator.validate(
            self._competition,
            start_location_id=self._active_location_id,
            require_plan=bool(self._competition.plan_for(self._active_location_id)),
        )
        self._fill_table(
            self._issues_table,
            ["Vakavuus", "Sääntö", "Viesti"],
            [[i.severity.value, i.rule_id, i.message] for i in report.issues],
        )

    def _refresh_tree(self) -> None:
        self._tree.clear()
        root = QTreeWidgetItem([self._competition.name or "Kilpailu"])
        for label in (
            "Lähdöt",
            "Sarjat",
            "Radat",
            "Kilpailijat",
            "Lähtökaavio",
            "Aikajana",
            "Issues",
        ):
            root.addChild(QTreeWidgetItem([label]))
        self._tree.addTopLevelItem(root)
        self._tree.expandAll()

    @staticmethod
    def _fill_table(table: QTableWidget, headers: list[str], rows: list[list[str]]) -> None:
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r, c, item)
        table.resizeColumnsToContents()
