"""PySide6 main window for ClassStartPlan workflow (v0.6)."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, time, timedelta
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QDate, Qt, QTime
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
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

from startplanner.domain import (
    ClassStart,
    ClassStartPlan,
    Competition,
    Settings,
    StartLocation,
    format_start_time,
)
from startplanner.domain.errors import ScheduleError, StartPlannerError
from startplanner.services.class_service import ClassService
from startplanner.services.competition_service import CompetitionService
from startplanner.services.course_grid import build_course_grid
from startplanner.services.history_service import HistoryService
from startplanner.services.import_service import ExportService, ImportService
from startplanner.services.optimizer_service import OptimizerService
from startplanner.services.quality_service import QualityService
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService
from startplanner.validation.issues import Severity

_SEVERITY_FI = {
    Severity.ERROR: "Virhe",
    Severity.WARNING: "Varoitus",
    Severity.NOTE: "Huomautus",
}


class SettingsDialog(QDialog):
    def __init__(self, competition: Competition, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Kilpailun asetukset")
        self._competition = competition
        layout = QFormLayout(self)
        self._name = QLineEdit(competition.name)
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
        layout.addRow("Kilpailun nimi", self._name)
        layout.addRow("Oletuslähtöväli (min)", self._interval)
        layout.addRow("Sarjojen väli (min)", self._gap)
        layout.addRow("Kilpailun aloitusaika", self._start)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def apply(self) -> None:
        name = self._name.text().strip()
        if name:
            self._competition.name = name
        self._competition.settings.default_start_interval_min = self._interval.value()
        self._competition.settings.class_gap_min = self._gap.value()
        t = self._start.time()
        from datetime import time as dtime

        self._competition.settings.competition_start = dtime(t.hour(), t.minute())


class NewCompetitionDialog(QDialog):
    """Dialog for creating a new competition with all required settings."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Uusi kilpailu")
        self.setModal(True)
        layout = QFormLayout(self)

        self._name = QLineEdit()
        self._name.setPlaceholderText("esim. Kevyttely 2026")
        layout.addRow("Kilpailun nimi *", self._name)

        self._date = QDateEdit()
        self._date.setDisplayFormat("dd.MM.yyyy")
        self._date.setDate(QDate.currentDate())
        self._date.setCalendarPopup(True)
        layout.addRow("Päivämäärä", self._date)

        self._interval = QSpinBox()
        self._interval.setRange(1, 30)
        self._interval.setValue(2)
        layout.addRow("Oletuslähtöväli (min)", self._interval)

        self._gap = QSpinBox()
        self._gap.setRange(0, 60)
        self._gap.setValue(2)
        layout.addRow("Sarjojen väli (min)", self._gap)

        self._start = QTimeEdit()
        self._start.setDisplayFormat("HH:mm")
        self._start.setTime(QTime(12, 0))
        layout.addRow("Kilpailun aloitusaika", self._start)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self) -> None:
        if not self._name.text().strip():
            QMessageBox.warning(self, "Täytä kentät", "Kilpailun nimi on pakollinen.")
            return
        super().accept()

    @property
    def name(self) -> str:
        return self._name.text().strip()

    @property
    def event_date(self) -> date:
        return self._date.date().toPython()

    @property
    def start_interval(self) -> int:
        return self._interval.value()

    @property
    def class_gap(self) -> int:
        return self._gap.value()

    @property
    def start_time(self) -> time:
        t = self._start.time()
        return time(t.hour(), t.minute())


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StartPlanner 0.6")
        self.resize(1200, 750)

        self._competition = Competition(name="Uusi kilpailu")
        self._competition.ensure_default_start_location()
        self._active_location_id = next(iter(self._competition.start_locations))
        self._project_path: Path | None = None
        self._class_service = ClassService()
        self._competition_service = CompetitionService()
        self._import_service = ImportService()
        self._export_service = ExportService()
        self._scheduler = SchedulerService()
        self._validator = ValidationService()
        self._quality = QualityService()
        self._optimizer = OptimizerService()
        self._histories: dict[str, HistoryService] = {}
        self._reset_all_history()

        self._build_ui()
        self._refresh_all()

    def _active_history(self) -> HistoryService:
        """History stack for the active start location, created lazily.

        Kept per-location (not a single shared stack) so that switching the
        active start location — a routine action, not a reset — never
        discards undo/redo state for other locations.
        """
        history = self._histories.get(self._active_location_id)
        if history is None:
            history = HistoryService()
            history.push("Alku", self._competition.plan_for(self._active_location_id))
            self._histories[self._active_location_id] = history
        return history

    def _reset_all_history(self) -> None:
        """Discard undo/redo for every location (new/opened/imported competition)."""
        self._histories = {}
        self._active_history()

    def _record_plan(self, description: str) -> None:
        plan = self._competition.plan_for(self._active_location_id)
        self._active_history().push(description, plan)

    def _build_ui(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("Tiedosto")
        file_menu.addAction("Uusi", self._new_project)
        file_menu.addAction("Avaa .spc…", self._open_project)
        file_menu.addAction("Tallenna", self._save_project)
        file_menu.addAction("Tallenna nimellä…", self._save_project_as)
        file_menu.addSeparator()
        file_menu.addAction(
            "Tuo ratatiedot (IOF CourseData 3.0, Condes)…",
            self._import_coursedata,
        )
        file_menu.addAction(
            "Tuo ilmoittautumiset (IRMA Pirilä)…",
            self._import_entries,
        )
        file_menu.addAction(
            "Tuo jälki-ilmoittautuneet (IRMA Pirilä)…",
            self._import_late_entries,
        )
        file_menu.addSeparator()
        file_menu.addAction("Vie Excel…", self._export_excel)
        file_menu.addAction("Vie CSV…", self._export_csv)
        file_menu.addAction("Vie PDF…", self._export_pdf)
        file_menu.addAction("Vie ruudukko PDF…", self._export_grid_pdf)

        edit_menu = menu.addMenu("Muokkaa")
        self._undo_action = edit_menu.addAction("Kumoa", self._undo)
        self._undo_action.setShortcut("Ctrl+Z")
        self._redo_action = edit_menu.addAction("Tee uudelleen", self._redo)
        self._redo_action.setShortcut("Ctrl+Shift+Z")
        edit_menu.addSeparator()
        edit_menu.addAction("Kilpailun asetukset…", self._edit_settings)

        schedule_menu = menu.addMenu("Lähtökaavio")
        schedule_menu.addAction("Muodosta lähtökaavio (aktiivinen lähtö)", self._build_schedule)
        schedule_menu.addAction("Päivitä lähtökaavio (aktiivinen lähtö)", self._update_schedule)
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

        self._start_page = QWidget()
        start_layout = QVBoxLayout(self._start_page)
        start_layout.addWidget(
            QLabel(
                "Tuo ensin ratatiedot ja ilmoittautumiset. Kun molemmat on "
                "tuotu, muut välilehdet avautuvat ja lähtökaavion voi "
                "toteuttaa."
            )
        )
        self._start_course_status = QLabel()
        start_layout.addWidget(self._start_course_status)
        start_course_btn = QPushButton("Lataa ratatiedot…")
        start_course_btn.clicked.connect(self._import_coursedata)
        start_layout.addWidget(start_course_btn)
        self._start_entries_status = QLabel()
        start_layout.addWidget(self._start_entries_status)
        start_entries_btn = QPushButton("Lataa ilmoittautumiset…")
        start_entries_btn.clicked.connect(self._import_entries)
        start_layout.addWidget(start_entries_btn)
        self._start_build_btn = QPushButton("Toteuta lähtökaavio")
        self._start_build_btn.clicked.connect(self._build_schedule)
        start_layout.addWidget(self._start_build_btn)
        start_layout.addStretch()

        self._locations_page = QWidget()
        locations_layout = QVBoxLayout(self._locations_page)
        self._locations_table = QTableWidget()
        locations_layout.addWidget(self._locations_table)
        add_loc_btn = QPushButton("Lisää lähtö…")
        add_loc_btn.clicked.connect(self._add_start_location)
        locations_layout.addWidget(add_loc_btn)
        self._locations_table.itemChanged.connect(self._on_location_name_changed)

        self._classes_table = QTableWidget()
        self._classes_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._classes_table.customContextMenuRequested.connect(
            self._classes_context_menu
        )
        self._class_order_page = QWidget()
        class_order_layout = QVBoxLayout(self._class_order_page)
        class_order_layout.addWidget(
            QLabel(
                "Raahaa sarjoja näyttöjärjestyksen mukaan (Lähtökaavio / Excel). "
                "Radan lähtöjärjestys on omassa välilehdessä."
            )
        )
        self._class_order_list = QListWidget()
        self._class_order_list.setDragDropMode(QAbstractItemView.InternalMove)
        self._class_order_list.setDefaultDropAction(Qt.MoveAction)
        self._class_order_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._class_order_list.model().rowsMoved.connect(self._on_class_order_rows_moved)
        class_order_layout.addWidget(self._class_order_list)

        self._course_order_page = QWidget()
        course_order_layout = QVBoxLayout(self._course_order_page)
        course_order_layout.addWidget(
            QLabel(
                "Valitse rata ja raahaa sarjat siihen järjestykseen, "
                "jossa ne lähtevät tällä radalla."
            )
        )
        course_pick_row = QHBoxLayout()
        course_pick_row.addWidget(QLabel("Rata:"))
        self._course_order_combo = QComboBox()
        self._course_order_combo.currentIndexChanged.connect(
            self._refresh_course_order_list
        )
        course_pick_row.addWidget(self._course_order_combo, stretch=1)
        course_order_layout.addLayout(course_pick_row)
        self._course_order_list = QListWidget()
        self._course_order_list.setDragDropMode(QAbstractItemView.InternalMove)
        self._course_order_list.setDefaultDropAction(Qt.MoveAction)
        self._course_order_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._course_order_list.model().rowsMoved.connect(
            self._on_course_order_rows_moved
        )
        course_order_layout.addWidget(self._course_order_list)

        self._courses_page = QWidget()
        courses_layout = QVBoxLayout(self._courses_page)
        self._courses_table = QTableWidget()
        self._courses_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._courses_table.customContextMenuRequested.connect(
            self._courses_context_menu
        )
        courses_layout.addWidget(self._courses_table)
        clear_courses_btn = QPushButton("Poista kaikki radat ja sarjat")
        clear_courses_btn.clicked.connect(self._clear_courses_and_classes)
        courses_layout.addWidget(clear_courses_btn)
        self._competitors_page = QWidget()
        competitors_layout = QVBoxLayout(self._competitors_page)
        self._competitors_table = QTableWidget()
        self._competitors_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._competitors_table.customContextMenuRequested.connect(
            self._competitors_context_menu
        )
        competitors_layout.addWidget(self._competitors_table)
        clear_competitors_btn = QPushButton("Poista kaikki kilpailijat")
        clear_competitors_btn.clicked.connect(self._clear_competitors)
        competitors_layout.addWidget(clear_competitors_btn)
        self._plan_page = QWidget()
        plan_layout = QVBoxLayout(self._plan_page)
        plan_sort_row = QHBoxLayout()
        plan_sort_row.addWidget(QLabel("Näytä järjestettynä:"))
        self._plan_sort_combo = QComboBox()
        self._plan_sort_combo.addItem("Sarjajärjestys", "class")
        self._plan_sort_combo.addItem("Aika", "time")
        self._plan_sort_combo.currentIndexChanged.connect(self._refresh_plan_and_status)
        plan_sort_row.addWidget(self._plan_sort_combo)
        plan_sort_row.addStretch()
        plan_layout.addLayout(plan_sort_row)
        self._plan_table = QTableWidget()
        self._plan_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._plan_table.customContextMenuRequested.connect(self._plan_context_menu)
        self._plan_table.cellDoubleClicked.connect(self._plan_double_clicked)
        plan_layout.addWidget(self._plan_table)
        self._timeline_table = QTableWidget()
        self._grid_table = QTableWidget()
        self._issues_table = QTableWidget()
        self._tabs.addTab(self._start_page, "Aloitus")
        self._tabs.addTab(self._locations_page, "Lähdöt")
        self._tabs.addTab(self._classes_table, "Sarjat")
        self._tabs.addTab(self._class_order_page, "Sarjajärjestys")
        self._tabs.addTab(self._course_order_page, "Ratajärjestys")
        self._tabs.addTab(self._courses_page, "Radat")
        self._tabs.addTab(self._competitors_page, "Kilpailijat")
        self._tabs.addTab(self._plan_page, "Lähtökaavio")
        self._tabs.addTab(self._timeline_table, "Aikajana")
        self._tabs.addTab(self._grid_table, "Ruudukko")
        self._tabs.addTab(self._issues_table, "Huomiot")
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
        history = self._active_history()
        self._undo_action.setEnabled(history.can_undo())
        self._redo_action.setEnabled(history.can_redo())

    def _new_project(self) -> None:
        dlg = NewCompetitionDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        self._competition = self._competition_service.new_competition(
            name=dlg.name,
            event_date=dlg.event_date,
            settings=Settings(
                default_start_interval_min=dlg.start_interval,
                class_gap_min=dlg.class_gap,
                competition_start=dlg.start_time,
            ),
        )
        self._active_location_id = next(iter(self._competition.start_locations))
        self._project_path = None
        self._reset_all_history()
        self._refresh_all()
        self._tabs.setCurrentWidget(self._start_page)

    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Avaa projekti", "", "StartPlanner (*.spc)")
        if not path:
            return
        try:
            self._competition = self._competition_service.load(path)
            self._competition.ensure_default_start_location()
            self._active_location_id = next(iter(self._competition.start_locations))
            self._project_path = Path(path)
            self._reset_all_history()
            self._refresh_all()
            self._land_after_load()
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Virhe", str(exc))

    def _land_after_load(self) -> None:
        """After loading a competition that may already be fully set up,
        jump past the Aloitus gate if there's nothing left to do there."""
        if self._setup_complete() and self._tabs.currentWidget() is self._start_page:
            self._tabs.setCurrentIndex(1)

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
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Tuo ratatiedot (IOF CourseData 3.0, Condes)",
            "",
            "XML (*.xml);;All (*)",
        )
        if not paths:
            return
        try:
            competition = self._competition
            for i, path in enumerate(paths):
                if i == 0 and (
                    not competition.courses and not competition.classes
                ):
                    competition = self._import_service.import_coursedata(path)
                else:
                    competition = self._import_service.import_coursedata(
                        path, competition
                    )
            self._competition = competition
            self._active_location_id = next(iter(self._competition.start_locations))
            self._reset_all_history()
            self._refresh_all()
            self._status.showMessage(f"Ratatiedot tuotu: {len(paths)} tiedostoa", 4000)
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Tuontivirhe", str(exc))

    def _import_entries(self) -> None:
        self._import_entries_file(late=False)

    def _import_late_entries(self) -> None:
        self._import_entries_file(late=True)

    def _import_entries_file(self, *, late: bool) -> None:
        title = (
            "Tuo jälki-ilmoittautuneet (IRMA Pirilä)"
            if late
            else "Tuo ilmoittautumiset (IRMA Pirilä)"
        )
        path, _ = QFileDialog.getOpenFileName(self, title, "", "CSV (*.csv);;All (*)")
        if not path:
            return
        try:
            had_plan = bool(self._competition.plans)
            before = len(self._competition.competitors)
            n = self._import_service.import_entries(self._competition, path)
            self._refresh_all()
            self._status.showMessage(f"Tuotu {n} kilpailijaa", 4000)
            if had_plan and len(self._competition.competitors) > before:
                reply = QMessageBox.question(
                    self,
                    "Päivitä lähtökaavio",
                    "Ilmoittautumiset muuttuivat. Päivitetäänkö lähtökaavio?\n"
                    "Kaaviossa jo olevat sarjojen ajat säilyvät.",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    self._update_schedule(quiet=True)
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Tuontivirhe", str(exc))

    def _update_schedule(self, *, quiet: bool = False) -> None:
        if not self._competition.plan_for(self._active_location_id):
            if not quiet:
                QMessageBox.information(
                    self, "Päivitä", "Muodosta ensin lähtökaavio tälle lähdölle."
                )
            return
        try:
            before_n = len(self._competition.plan_for(self._active_location_id) or [])
            plan = self._scheduler.update(self._competition, self._active_location_id)
            self._record_plan("Päivitä kaavio")
            self._refresh_all()
            if not quiet:
                self._tabs.setCurrentWidget(self._plan_page)
            score = self._quality.score(self._competition, self._active_location_id)
            self._status.showMessage(
                f"Kaavio päivitetty: {before_n} → {len(plan)} sarjaa · laatu {score.as_text()}",
                5000,
            )
        except ScheduleError as exc:
            if not quiet:
                QMessageBox.warning(self, "Ei voida päivittää", str(exc))
        except StartPlannerError as exc:
            if not quiet:
                QMessageBox.critical(self, "Virhe", str(exc))

    def _build_schedule(self) -> None:
        try:
            plan = self._scheduler.apply(self._competition, self._active_location_id)
            self._record_plan("Muodosta lähtökaavio")
            self._refresh_all()
            self._tabs.setCurrentWidget(self._plan_page)
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
            self._tabs.setCurrentWidget(self._plan_page)
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
        snap = self._active_history().undo()
        if snap is None:
            return
        self._apply_plan_snapshot(snap.plan)
        self._refresh_all()
        self._status.showMessage(f"Kumottu → {snap.description}", 3000)

    def _redo(self) -> None:
        snap = self._active_history().redo()
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
        self._active_history()  # establish baseline for the new location only
        self._refresh_all()

    def _clear_competitors(self) -> None:
        n = len(self._competition.competitors)
        if n == 0:
            QMessageBox.information(self, "Poista kilpailijat", "Kilpailu on jo tyhjä.")
            return
        reply = QMessageBox.question(
            self,
            "Poista kaikki kilpailijat",
            f"Poistetaanko kaikki {n} kilpailijaa?\n\n"
            "Tätä ei voi perua.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        removed = self._competition_service.clear_competitors(self._competition)
        self._refresh_all()
        self._status.showMessage(f"Poistettu {removed} kilpailijaa", 4000)

    def _selected_plan_class_id(self) -> str | None:
        row = self._plan_table.currentRow()
        if row < 0:
            return None
        item = self._plan_table.item(row, 2)
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
        new_time = self._prompt_new_start_time(entry.first_start_time)
        if new_time is None:
            return
        self._set_class_first_time(class_id, new_time, "Siirrä sarja")

    def _prompt_new_start_time(self, current: datetime) -> datetime | None:
        """Ask for a new start time (HH:MM) plus an optional next-day flag.

        The resulting date is always the competition date (or today, if
        unset) — crossing midnight is rare, so it's an explicit checkbox
        rather than a full calendar date picker.
        """
        event_date = self._competition.event_date or date.today()
        dlg = QDialog(self)
        dlg.setWindowTitle("Siirrä sarja")
        layout = QFormLayout(dlg)
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(QTime(current.hour, current.minute))
        layout.addRow("Uusi 1. lähtöaika", time_edit)
        next_day = QCheckBox("Siirrä seuraavalle vuorokaudelle (+1 pv)")
        next_day.setChecked(current.date() == event_date + timedelta(days=1))
        layout.addRow(next_day)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addRow(buttons)
        if dlg.exec() != QDialog.Accepted:
            return None
        t = time_edit.time()
        return self._resolve_move_datetime(
            time(t.hour(), t.minute()), next_day.isChecked(), event_date
        )

    @staticmethod
    def _resolve_move_datetime(new_time: time, next_day: bool, event_date: date) -> datetime:
        day = event_date + timedelta(days=1) if next_day else event_date
        return datetime.combine(day, new_time)

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

    def _export_pdf(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Vie PDF", "", "PDF (*.pdf)")
        if not path:
            return
        if not path.endswith(".pdf"):
            path += ".pdf"
        try:
            self._export_service.export_pdf(self._competition, path)
            self._status.showMessage(f"Viety: {path}", 4000)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Vientivirhe", str(exc))

    def _export_grid_pdf(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Vie ruudukko PDF", "", "PDF (*.pdf)"
        )
        if not path:
            return
        if not path.endswith(".pdf"):
            path += ".pdf"
        try:
            self._export_service.export_grid_pdf(
                self._competition, path, self._active_location_id
            )
            self._status.showMessage(f"Viety: {path}", 4000)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Vientivirhe", str(exc))

    def _on_location_changed(self, index: int) -> None:
        if index < 0:
            return
        loc_id = self._location_combo.itemData(index)
        if loc_id:
            self._active_location_id = loc_id
            # Switching the active location must not discard its undo/redo
            # history — _active_history() only creates a baseline if this
            # location has never been visited before.
            self._active_history()
            self._refresh_plan_and_status()

    def _on_tree_clicked(self, item: QTreeWidgetItem, _col: int) -> None:
        mapping = {
            "Aloitus": self._start_page,
            "Lähdöt": self._locations_page,
            "Sarjat": self._classes_table,
            "Sarjajärjestys": self._class_order_page,
            "Ratajärjestys": self._course_order_page,
            "Radat": self._courses_page,
            "Kilpailijat": self._competitors_page,
            "Lähtökaavio": self._plan_page,
            "Aikajana": self._timeline_table,
            "Ruudukko": self._grid_table,
            "Huomiot": self._issues_table,
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

    def _setup_complete(self) -> bool:
        c = self._competition
        return bool(c.courses) and bool(c.classes) and bool(c.competitors)

    def _refresh_start_page(self, ready: bool) -> None:
        c = self._competition
        if c.courses or c.classes:
            self._start_course_status.setText(
                f"✓ Ratatiedot ladattu ({len(c.courses)} rataa, {len(c.classes)} sarjaa)"
            )
        else:
            self._start_course_status.setText("Ratatietoja ei ole vielä ladattu.")
        if c.competitors:
            self._start_entries_status.setText(
                f"✓ Ilmoittautumiset ladattu ({len(c.competitors)} kilpailijaa)"
            )
        else:
            self._start_entries_status.setText("Ilmoittautumisia ei ole vielä ladattu.")
        self._start_build_btn.setVisible(ready)

    def _apply_tab_gating(self, ready: bool) -> None:
        for i in range(self._tabs.count()):
            if self._tabs.widget(i) is self._start_page:
                continue
            self._tabs.setTabVisible(i, ready)
        if not ready and self._tabs.currentWidget() is not self._start_page:
            self._tabs.setCurrentWidget(self._start_page)

    def _refresh_all(self) -> None:
        self._competition.ensure_default_start_location()
        if self._active_location_id not in self._competition.start_locations:
            self._active_location_id = next(iter(self._competition.start_locations))
        ready = self._setup_complete()
        self._refresh_location_combo()
        self._refresh_start_page(ready)
        self._refresh_tree(ready)
        self._refresh_locations_table()
        self._refresh_classes_table()
        self._refresh_class_order_list()
        self._refresh_course_order_combo()
        self._refresh_courses_table()
        self._refresh_competitors_table()
        self._refresh_plan_and_status()
        self._refresh_issues()
        self._update_history_actions()
        self._apply_tab_gating(ready)

    def _refresh_locations_table(self) -> None:
        headers = ["Nimi", "1. lähtö", "Sarjoja"]
        locations = sorted(
            self._competition.start_locations.values(), key=lambda loc: loc.name
        )
        self._locations_table.blockSignals(True)
        self._locations_table.clear()
        self._locations_table.setColumnCount(len(headers))
        self._locations_table.setHorizontalHeaderLabels(headers)
        self._locations_table.setRowCount(len(locations))
        readonly = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        default_start = self._competition.settings.competition_start
        default_tip = f"Oletus: {default_start.strftime('%H:%M')}"

        for row, loc in enumerate(locations):
            n_classes = sum(
                1
                for rc in self._competition.classes.values()
                if rc.start_location_id == loc.id
            )
            name_item = QTableWidgetItem(loc.name)
            name_item.setData(Qt.UserRole, loc.id)
            self._locations_table.setItem(row, 0, name_item)

            start_widget = QWidget()
            start_layout = QHBoxLayout(start_widget)
            start_layout.setContentsMargins(0, 0, 0, 0)
            time_edit = QTimeEdit()
            time_edit.setDisplayFormat("HH:mm")
            time_edit.setToolTip(default_tip)
            use_default = QCheckBox("Oletus")
            use_default.setToolTip(default_tip)
            effective = loc.first_start if loc.first_start is not None else default_start
            time_edit.blockSignals(True)
            use_default.blockSignals(True)
            time_edit.setTime(QTime(effective.hour, effective.minute))
            use_default.setChecked(loc.first_start is None)
            time_edit.setEnabled(loc.first_start is not None)
            time_edit.blockSignals(False)
            use_default.blockSignals(False)

            def _apply(
                location_id: str = loc.id,
                te: QTimeEdit = time_edit,
                cb: QCheckBox = use_default,
            ) -> None:
                self._on_location_first_start_changed(location_id, te, cb)

            use_default.toggled.connect(
                lambda checked, te=time_edit, apply=_apply: (
                    te.setEnabled(not checked),
                    apply(),
                )
            )
            time_edit.timeChanged.connect(lambda _t, apply=_apply: apply())
            start_layout.addWidget(time_edit)
            start_layout.addWidget(use_default)
            self._locations_table.setCellWidget(row, 1, start_widget)

            count_item = QTableWidgetItem(str(n_classes))
            count_item.setFlags(readonly)
            self._locations_table.setItem(row, 2, count_item)
        self._locations_table.blockSignals(False)
        self._locations_table.resizeColumnsToContents()

    def _on_location_first_start_changed(
        self, location_id: str, time_edit: QTimeEdit, use_default: QCheckBox
    ) -> None:
        if use_default.isChecked():
            first_start: time | None = None
        else:
            t = time_edit.time()
            first_start = time(t.hour(), t.minute())
        try:
            self._class_service.set_location_first_start(
                self._competition, location_id, first_start
            )
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Lähtö", str(exc))
            self._refresh_locations_table()
            return

    def _on_location_name_changed(self, item: QTableWidgetItem) -> None:
        if item.column() != 0:
            return
        location_id = item.data(Qt.UserRole)
        if not location_id:
            return
        try:
            self._class_service.rename_start_location(
                self._competition, location_id, item.text()
            )
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Lähtö", str(exc))
            self._refresh_locations_table()
            return
        self._refresh_location_combo()
        self._refresh_classes_table()
        self._refresh_plan_and_status()

    def _refresh_class_order_list(self) -> None:
        self._class_order_list.blockSignals(True)
        self._class_order_list.clear()
        classes = sorted(
            self._competition.classes.values(),
            key=lambda c: (c.sort_order, c.name),
        )
        for rc in classes:
            item = QListWidgetItem(rc.name)
            item.setData(Qt.UserRole, rc.id)
            self._class_order_list.addItem(item)
        self._class_order_list.blockSignals(False)

    def _on_class_order_rows_moved(self, *_args: object) -> None:
        class_ids: list[str] = []
        for row in range(self._class_order_list.count()):
            item = self._class_order_list.item(row)
            if item is None:
                continue
            class_id = item.data(Qt.UserRole)
            if class_id:
                class_ids.append(class_id)
        try:
            self._class_service.reorder_classes(self._competition, class_ids)
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Sarjajärjestys", str(exc))
            self._refresh_class_order_list()
            return
        self._refresh_classes_table()
        self._refresh_plan_and_status()

    def _refresh_course_order_combo(self) -> None:
        current = self._course_order_combo.currentData()
        self._course_order_combo.blockSignals(True)
        self._course_order_combo.clear()
        # Prefer courses that already have assigned classes.
        courses_with_classes = [
            course
            for course in sorted(
                self._competition.courses.values(), key=lambda c: c.name
            )
            if any(
                rc.course_id == course.id for rc in self._competition.classes.values()
            )
        ]
        courses = courses_with_classes or sorted(
            self._competition.courses.values(), key=lambda c: c.name
        )
        for course in courses:
            n = sum(
                1
                for rc in self._competition.classes.values()
                if rc.course_id == course.id
            )
            label = f"{course.name} ({n})" if n else course.name
            self._course_order_combo.addItem(label, course.id)
        idx = self._course_order_combo.findData(current) if current is not None else -1
        if idx < 0 and self._course_order_combo.count():
            idx = 0
        if idx >= 0:
            self._course_order_combo.setCurrentIndex(idx)
        self._course_order_combo.blockSignals(False)
        self._refresh_course_order_list()

    def _refresh_course_order_list(self, *_args: object) -> None:
        self._course_order_list.blockSignals(True)
        self._course_order_list.clear()
        course_id = self._course_order_combo.currentData()
        if course_id:
            classes = sorted(
                (
                    rc
                    for rc in self._competition.classes.values()
                    if rc.course_id == course_id
                ),
                key=lambda c: (c.course_order, c.name),
            )
            for rc in classes:
                item = QListWidgetItem(rc.name)
                item.setData(Qt.UserRole, rc.id)
                self._course_order_list.addItem(item)
            if not classes:
                hint = QListWidgetItem("(Ei sarjoja tällä radalla — kytke Sarjat-välilehdellä)")
                hint.setFlags(Qt.NoItemFlags)
                self._course_order_list.addItem(hint)
        self._course_order_list.blockSignals(False)

    def _on_course_order_rows_moved(self, *_args: object) -> None:
        course_id = self._course_order_combo.currentData()
        if not course_id:
            return
        class_ids: list[str] = []
        for row in range(self._course_order_list.count()):
            item = self._course_order_list.item(row)
            if item is None:
                continue
            class_id = item.data(Qt.UserRole)
            if class_id:
                class_ids.append(class_id)
        try:
            self._class_service.reorder_course_classes(
                self._competition, course_id, class_ids
            )
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Ratajärjestys", str(exc))
            self._refresh_course_order_list()
            return
        self._refresh_classes_table()
        self._refresh_plan_and_status()

    def _refresh_classes_table(self) -> None:
        headers = [
            "Järjestys",
            "Sarja",
            "Lähtö",
            "Rata",
            "Kilpailijoita",
            "Lähtöväli",
            "Tyhjiä ennen",
        ]
        classes = sorted(
            self._competition.classes.values(),
            key=lambda c: (c.sort_order, c.name),
        )
        self._classes_table.clear()
        self._classes_table.setColumnCount(len(headers))
        self._classes_table.setHorizontalHeaderLabels(headers)
        self._classes_table.setRowCount(len(classes))
        missing_bg = QBrush(QColor(255, 230, 230))
        readonly = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        for row, rc in enumerate(classes):
            missing = not rc.course_id or rc.course_id not in self._competition.courses

            order_spin = QSpinBox()
            order_spin.setRange(0, 9999)
            order_spin.setValue(rc.sort_order)
            order_spin.valueChanged.connect(
                lambda value, class_id=rc.id: self._on_class_sort_order_changed(
                    class_id, value
                )
            )
            self._classes_table.setCellWidget(row, 0, order_spin)

            name_item = QTableWidgetItem(rc.name)
            name_item.setData(Qt.UserRole, rc.id)
            name_item.setFlags(readonly)
            if missing:
                name_item.setBackground(missing_bg)
            self._classes_table.setItem(row, 1, name_item)

            loc_combo = QComboBox()
            loc_combo.blockSignals(True)
            for loc in sorted(
                self._competition.start_locations.values(), key=lambda x: x.name
            ):
                loc_combo.addItem(loc.name, loc.id)
            idx = loc_combo.findData(rc.start_location_id)
            if idx >= 0:
                loc_combo.setCurrentIndex(idx)
            loc_combo.blockSignals(False)
            loc_combo.currentIndexChanged.connect(
                lambda _idx, class_id=rc.id, cb=loc_combo: self._on_class_location_changed(
                    class_id, cb
                )
            )
            self._classes_table.setCellWidget(row, 2, loc_combo)

            combo = QComboBox()
            combo.blockSignals(True)
            combo.addItem("—", None)
            for course in sorted(
                self._competition.courses.values(), key=lambda c: c.name
            ):
                combo.addItem(course.name, course.id)
            if rc.course_id:
                idx = combo.findData(rc.course_id)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            combo.blockSignals(False)
            combo.currentIndexChanged.connect(
                lambda _idx, class_id=rc.id, cb=combo: self._on_class_course_changed(
                    class_id, cb
                )
            )
            self._classes_table.setCellWidget(row, 3, combo)

            count_item = QTableWidgetItem(str(self._competition.competitor_count(rc.id)))
            count_item.setFlags(readonly)
            if missing:
                count_item.setBackground(missing_bg)
            self._classes_table.setItem(row, 4, count_item)

            interval = QSpinBox()
            interval.setRange(1, 30)
            interval.setValue(rc.start_interval_min)
            interval.valueChanged.connect(
                lambda value, class_id=rc.id: self._on_class_interval_changed(
                    class_id, value
                )
            )
            self._classes_table.setCellWidget(row, 5, interval)

            empty_slots = QSpinBox()
            empty_slots.setRange(0, 30)
            empty_slots.setValue(rc.empty_slots_before)
            empty_slots.setToolTip(
                "Tyhjien lähtöaikojen määrä ennen tätä sarjaa samalla radalla"
            )
            empty_slots.valueChanged.connect(
                lambda value, class_id=rc.id: self._on_class_empty_slots_changed(
                    class_id, value
                )
            )
            self._classes_table.setCellWidget(row, 6, empty_slots)

        self._classes_table.resizeColumnsToContents()

    def _on_class_sort_order_changed(self, class_id: str, value: int) -> None:
        try:
            self._class_service.set_sort_order(self._competition, class_id, value)
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Järjestys", str(exc))
            self._refresh_classes_table()
            return
        self._refresh_classes_table()
        self._refresh_class_order_list()
        self._refresh_plan_and_status()

    def _on_class_location_changed(self, class_id: str, combo: QComboBox) -> None:
        location_id = combo.currentData()
        try:
            self._class_service.assign_start_location(
                self._competition, class_id, location_id
            )
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Lähtö", str(exc))
            self._refresh_classes_table()
            return
        self._refresh_locations_table()
        self._refresh_classes_table()
        self._refresh_issues()
        self._refresh_plan_and_status()

    def _on_class_interval_changed(self, class_id: str, value: int) -> None:
        try:
            self._class_service.set_start_interval(self._competition, class_id, value)
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Lähtöväli", str(exc))
            self._refresh_classes_table()
            return
        self._refresh_plan_and_status()

    def _on_class_empty_slots_changed(self, class_id: str, value: int) -> None:
        try:
            self._class_service.set_empty_slots_before(
                self._competition, class_id, value
            )
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Tyhjät lähtöajat", str(exc))
            self._refresh_classes_table()
            return
        self._refresh_plan_and_status()

    def _on_class_course_changed(self, class_id: str, combo: QComboBox) -> None:
        course_id = combo.currentData()
        try:
            self._class_service.assign_course(self._competition, class_id, course_id)
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Rata", str(exc))
            self._refresh_classes_table()
            return
        self._refresh_classes_table()
        self._refresh_course_order_combo()
        self._refresh_issues()
        self._refresh_plan_and_status()

    def _selected_classes_table_class_id(self) -> str | None:
        row = self._classes_table.currentRow()
        if row < 0:
            return None
        item = self._classes_table.item(row, 1)  # column 0 is a QSpinBox widget
        return item.data(Qt.UserRole) if item else None

    def _classes_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.addAction("Poista sarja…", self._delete_selected_class)
        menu.exec(self._classes_table.viewport().mapToGlobal(pos))

    def _delete_selected_class(self) -> None:
        class_id = self._selected_classes_table_class_id()
        if not class_id:
            QMessageBox.information(self, "Poista sarja", "Valitse sarja.")
            return
        rc = self._competition.classes.get(class_id)
        if not rc:
            return
        n = self._competition.competitor_count(class_id)
        reply = QMessageBox.question(
            self,
            "Poista sarja",
            f"Poistetaanko sarja {rc.name}?\n\n"
            f"Samalla poistuu {n} kilpailijaa ja sarjan lähtökaavion rivit.\n"
            "Tätä ei voi perua.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self._class_service.remove_class(self._competition, class_id)
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Poista sarja", str(exc))
            return
        self._refresh_all()
        self._status.showMessage(f"Sarja poistettu: {rc.name}", 4000)

    def _refresh_courses_table(self) -> None:
        headers = ["Rata", "Pituus (m)", "Nousu", "1. rasti", "Rasteja", "Sarjaväli (min)"]
        courses = sorted(self._competition.courses.values(), key=lambda c: c.name)
        self._courses_table.clear()
        self._courses_table.setColumnCount(len(headers))
        self._courses_table.setHorizontalHeaderLabels(headers)
        self._courses_table.setRowCount(len(courses))
        readonly = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        default_gap = self._competition.settings.class_gap_min

        for row, course in enumerate(courses):
            values = [
                course.name,
                str(course.length_m),
                str(course.climb_m),
                course.first_control or "—",
                str(len(course.controls)),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(readonly)
                item.setData(Qt.UserRole, course.id)
                self._courses_table.setItem(row, col, item)

            gap = QSpinBox()
            gap.setRange(0, 60)
            gap.setSpecialValueText(" ")
            gap.setToolTip(f"Oletus: {default_gap} min")
            gap.blockSignals(True)
            gap.setValue(course.class_gap_min if course.class_gap_min is not None else 0)
            gap.blockSignals(False)
            gap.valueChanged.connect(
                lambda value, course_id=course.id: self._on_course_gap_changed(
                    course_id, value
                )
            )
            self._courses_table.setCellWidget(row, 5, gap)

        self._courses_table.resizeColumnsToContents()

    def _on_course_gap_changed(self, course_id: str, value: int) -> None:
        gap_min = None if value == 0 else value
        try:
            self._class_service.set_course_class_gap(
                self._competition, course_id, gap_min
            )
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Sarjaväli", str(exc))
            self._refresh_courses_table()
            return
        self._refresh_plan_and_status()

    def _selected_course_id(self) -> str | None:
        row = self._courses_table.currentRow()
        if row < 0:
            return None
        item = self._courses_table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _courses_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.addAction("Poista rata…", self._delete_selected_course)
        menu.exec(self._courses_table.viewport().mapToGlobal(pos))

    def _delete_selected_course(self) -> None:
        course_id = self._selected_course_id()
        if not course_id:
            QMessageBox.information(self, "Poista rata", "Valitse rata.")
            return
        course = self._competition.courses.get(course_id)
        if not course:
            return
        classes = [
            rc for rc in self._competition.classes.values() if rc.course_id == course_id
        ]
        n_competitors = sum(self._competition.competitor_count(rc.id) for rc in classes)
        reply = QMessageBox.question(
            self,
            "Poista rata",
            f"Poistetaanko rata {course.name}?\n\n"
            f"Samalla poistuu {len(classes)} sarjaa ja {n_competitors} kilpailijaa "
            "sekä niiden lähtökaavion rivit.\nTätä ei voi perua.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self._class_service.remove_course(self._competition, course_id)
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Poista rata", str(exc))
            return
        self._refresh_all()
        self._status.showMessage(f"Rata poistettu: {course.name}", 4000)

    def _clear_courses_and_classes(self) -> None:
        n_courses = len(self._competition.courses)
        n_classes = len(self._competition.classes)
        if n_courses == 0 and n_classes == 0:
            QMessageBox.information(
                self, "Poista radat ja sarjat", "Radat ja sarjat ovat jo tyhjät."
            )
            return
        n_competitors = len(self._competition.competitors)
        reply = QMessageBox.question(
            self,
            "Poista kaikki radat ja sarjat",
            f"Poistetaanko kaikki {n_courses} rataa ja {n_classes} sarjaa?\n\n"
            f"Samalla poistuu myös kaikki {n_competitors} kilpailijaa.\n"
            "Tätä ei voi perua.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        removed_courses, removed_classes = self._class_service.clear_courses_and_classes(
            self._competition
        )
        self._refresh_all()
        self._status.showMessage(
            f"Poistettu {removed_courses} rataa ja {removed_classes} sarjaa", 4000
        )

    def _refresh_competitors_table(self) -> None:
        headers = ["Nimi", "Seura", "Sarja", "Emit"]
        competitors = sorted(
            self._competition.competitors.values(),
            key=lambda c: (c.last_name, c.first_name),
        )
        readonly = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        self._competitors_table.clear()
        self._competitors_table.setColumnCount(len(headers))
        self._competitors_table.setHorizontalHeaderLabels(headers)
        self._competitors_table.setRowCount(len(competitors))
        for row, comp in enumerate(competitors):
            values = [
                comp.full_name,
                comp.club,
                self._competition.classes[comp.class_id].name
                if comp.class_id in self._competition.classes
                else "—",
                comp.emit or "",
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(readonly)
                item.setData(Qt.UserRole, comp.id)
                self._competitors_table.setItem(row, col, item)
        self._competitors_table.resizeColumnsToContents()

    def _selected_competitor_id(self) -> str | None:
        row = self._competitors_table.currentRow()
        if row < 0:
            return None
        item = self._competitors_table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _competitors_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.addAction("Poista valittu", self._delete_selected_competitor)
        menu.exec(self._competitors_table.viewport().mapToGlobal(pos))

    def _delete_selected_competitor(self) -> None:
        competitor_id = self._selected_competitor_id()
        if not competitor_id:
            QMessageBox.information(self, "Poista", "Valitse kilpailija.")
            return
        comp = self._competition.competitors.get(competitor_id)
        if not comp:
            return
        reply = QMessageBox.question(
            self,
            "Poista kilpailija",
            f"Poistetaanko {comp.full_name}?\n\nTätä ei voi perua.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self._competition_service.remove_competitor(self._competition, competitor_id)
        except StartPlannerError as exc:
            QMessageBox.warning(self, "Poista", str(exc))
            return
        self._refresh_all()
        self._status.showMessage(f"Poistettu: {comp.full_name}", 4000)

    def _refresh_plan_and_status(self) -> None:
        plan = self._competition.plan_for(self._active_location_id)
        rows: list[list[str]] = []
        if plan:
            sort_by = self._plan_sort_combo.currentData() or "class"
            orders = {rc.id: rc.sort_order for rc in self._competition.classes.values()}
            names = {rc.id: rc.name for rc in self._competition.classes.values()}
            for entry in plan.sorted_entries(
                by=sort_by, class_sort_order=orders, class_names=names
            ):
                rc = self._competition.classes.get(entry.class_id)
                course = self._competition.course_for_class(rc) if rc else None
                rows.append(
                    [
                        str(rc.sort_order if rc else ""),
                        format_start_time(
                            entry.first_start_time, self._competition.event_date
                        ),
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
            [
                "Järjestys",
                "1. lähtöaika",
                "Sarja",
                "Kilpailijoita",
                "Lähtöväli",
                "Rata",
                "1. rasti",
                "Lukittu",
            ],
            rows,
        )
        self._refresh_timeline(plan)
        self._refresh_course_grid(plan)
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
        event_date = self._competition.event_date
        rows = [
            [format_start_time(m, event_date), ", ".join(names)]
            for m, names in sorted(minute_classes.items())
        ]
        self._fill_table(self._timeline_table, ["Aika", "Sarjat lähdössä"], rows)

    def _refresh_course_grid(self, plan: ClassStartPlan | None) -> None:
        grid = build_course_grid(self._competition, plan)
        table = self._grid_table
        table.clear()
        if not grid.minutes:
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Aika", "Yht"])
            table.setRowCount(0)
            return

        headers = ["Aika", "Yht"]
        for col in grid.columns:
            fc = col.first_control or "—"
            headers.append(f"{col.course_name}\n(1. rasti {fc})")

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(grid.minutes))

        readonly = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        event_date = self._competition.event_date
        for row, minute in enumerate(grid.minutes):
            time_item = QTableWidgetItem(format_start_time(minute, event_date))
            time_item.setFlags(readonly)
            table.setItem(row, 0, time_item)

            total_item = QTableWidgetItem(str(grid.total(minute)))
            total_item.setFlags(readonly)
            total_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, total_item)

            for col_idx, col in enumerate(grid.columns, start=2):
                text = grid.cell(minute, col.course_id)
                item = QTableWidgetItem(text)
                item.setFlags(readonly)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col_idx, item)

        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)

    def _refresh_issues(self) -> None:
        report = self._validator.validate(
            self._competition,
            start_location_id=self._active_location_id,
            require_plan=bool(self._competition.plan_for(self._active_location_id)),
        )
        self._fill_table(
            self._issues_table,
            ["Vakavuus", "Sääntö", "Viesti"],
            [
                [_SEVERITY_FI.get(i.severity, i.severity.value), i.rule_id, i.message]
                for i in report.issues
            ],
        )

    def _refresh_tree(self, ready: bool = True) -> None:
        self._tree.clear()
        root = QTreeWidgetItem([self._competition.name or "Kilpailu"])
        labels = ["Aloitus"]
        if ready:
            labels += [
                "Lähdöt",
                "Sarjat",
                "Sarjajärjestys",
                "Ratajärjestys",
                "Radat",
                "Kilpailijat",
                "Lähtökaavio",
                "Aikajana",
                "Ruudukko",
                "Huomiot",
            ]
        for label in labels:
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
