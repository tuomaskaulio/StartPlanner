"""Minimal PySide6 main window for v0.2 workflow."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from startplanner.domain import Competition
from startplanner.domain.errors import ScheduleError, StartPlannerError
from startplanner.services.competition_service import CompetitionService
from startplanner.services.import_service import ExportService, ImportService
from startplanner.services.scheduler_service import SchedulerService
from startplanner.services.validation_service import ValidationService


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StartPlanner 0.2")
        self.resize(1100, 700)

        self._competition = Competition(name="Uusi kilpailu")
        self._project_path: Path | None = None
        self._competition_service = CompetitionService()
        self._import_service = ImportService()
        self._export_service = ExportService()
        self._scheduler = SchedulerService()
        self._validator = ValidationService()

        self._build_ui()
        self._refresh_all()

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

        schedule_menu = menu.addMenu("Lähtökaavio")
        schedule_menu.addAction("Muodosta lähtökaavio", self._build_schedule)
        schedule_menu.addAction("Validoi", self._validate)

        splitter = QSplitter()
        self._tree = QTreeWidget()
        self._tree.setHeaderLabel("Kilpailu")
        self._tree.itemClicked.connect(self._on_tree_clicked)
        splitter.addWidget(self._tree)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self._tabs = QTabWidget()
        self._classes_table = QTableWidget()
        self._courses_table = QTableWidget()
        self._competitors_table = QTableWidget()
        self._schedule_table = QTableWidget()
        self._issues_table = QTableWidget()
        self._tabs.addTab(self._classes_table, "Sarjat")
        self._tabs.addTab(self._courses_table, "Radat")
        self._tabs.addTab(self._competitors_table, "Kilpailijat")
        self._tabs.addTab(self._schedule_table, "Lähtökaavio")
        self._tabs.addTab(self._issues_table, "Issues")
        right_layout.addWidget(self._tabs)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 3)

        self.setCentralWidget(splitter)
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status_label = QLabel()
        self._status.addWidget(self._status_label)

    def _new_project(self) -> None:
        self._competition = Competition(name="Uusi kilpailu")
        self._project_path = None
        self._refresh_all()

    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Avaa projekti", "", "StartPlanner (*.spc)")
        if not path:
            return
        try:
            self._competition = self._competition_service.load(path)
            self._project_path = Path(path)
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
            self._scheduler.apply(self._competition)
            self._refresh_all()
            self._status.showMessage(
                f"Lähtökaavio: {len(self._competition.schedule)} lähtöä", 4000
            )
        except ScheduleError as exc:
            QMessageBox.warning(self, "Ei voida muodostaa", str(exc))
        except StartPlannerError as exc:
            QMessageBox.critical(self, "Virhe", str(exc))

    def _validate(self) -> None:
        self._refresh_issues()
        self._tabs.setCurrentWidget(self._issues_table)

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

    def _on_tree_clicked(self, item: QTreeWidgetItem, _col: int) -> None:
        mapping = {
            "Sarjat": self._classes_table,
            "Radat": self._courses_table,
            "Kilpailijat": self._competitors_table,
            "Lähtökaavio": self._schedule_table,
            "Issues": self._issues_table,
        }
        key = item.text(0)
        if key in mapping:
            self._tabs.setCurrentWidget(mapping[key])

    def _refresh_all(self) -> None:
        self._refresh_tree()
        self._fill_table(
            self._classes_table,
            ["Sarja", "Rata", "Kilpailijoita", "Lähtöväli"],
            [
                [
                    rc.name,
                    (
                        self._competition.courses[rc.course_id].name
                        if rc.course_id in self._competition.courses
                        else "—"
                    ),
                    str(len(self._competition.competitors_in_class(rc.id))),
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
        self._fill_table(
            self._schedule_table,
            ["Aika", "Sarja", "Kilpailija", "Rata", "1. rasti", "Nro"],
            [
                [
                    s.start_time.strftime("%H:%M"),
                    self._competition.classes[s.class_id].name
                    if s.class_id in self._competition.classes
                    else "",
                    self._competition.competitors[s.competitor_id].full_name
                    if s.competitor_id in self._competition.competitors
                    else "",
                    self._competition.courses[s.course_id].name
                    if s.course_id in self._competition.courses
                    else "",
                    (
                        self._competition.courses[s.course_id].first_control
                        if s.course_id in self._competition.courses
                        else ""
                    )
                    or "",
                    str(s.start_number),
                ]
                for s in self._competition.schedule.sorted_starts()
            ],
        )
        self._refresh_issues()
        c = self._competition
        self._status_label.setText(
            f"{c.name}  |  Sarjoja {len(c.classes)}  |  "
            f"Kilpailijoita {len(c.competitors)}  |  "
            f"Ratoja {len(c.courses)}  |  "
            f"Lähtöjä {len(c.schedule)}"
        )

    def _refresh_issues(self) -> None:
        report = self._validator.validate(
            self._competition, require_schedule=bool(self._competition.schedule.starts)
        )
        self._fill_table(
            self._issues_table,
            ["Vakavuus", "Sääntö", "Viesti"],
            [[i.severity.value, i.rule_id, i.message] for i in report.issues],
        )

    def _refresh_tree(self) -> None:
        self._tree.clear()
        root = QTreeWidgetItem([self._competition.name or "Kilpailu"])
        for label in ("Sarjat", "Radat", "Kilpailijat", "Lähtökaavio", "Issues"):
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
