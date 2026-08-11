"""High-level import/export orchestration."""

from __future__ import annotations

from pathlib import Path

from startplanner.domain import Competition
from startplanner.exporters.excel import CsvExporter, ExcelExporter
from startplanner.exporters.pdf import PdfExporter
from startplanner.importers.condes_coursedata import CondesCourseDataImporter
from startplanner.importers.irma_ilmoit import IrmaIlmoitImporter


class ImportService:
    def __init__(self) -> None:
        self._condes = CondesCourseDataImporter()
        self._irma = IrmaIlmoitImporter()

    def import_coursedata(
        self, path: str | Path, competition: Competition | None = None
    ) -> Competition:
        if competition is None:
            competition = self._condes.read(path)
        else:
            self._condes.merge(competition, path)
        competition.ensure_default_start_location()
        self._link_classes_to_courses(competition)
        return competition

    def import_entries(
        self, competition: Competition, path: str | Path, *, late: bool = False
    ) -> int:
        competition.ensure_default_start_location()
        return self._irma.apply_to(competition, path, late=late)

    @staticmethod
    def _link_classes_to_courses(competition: Competition) -> None:
        for rc in competition.classes.values():
            if not rc.course_id and rc.name in competition.class_course_map:
                rc.course_id = competition.class_course_map[rc.name]


class ExportService:
    def export_excel(self, competition: Competition, path: str | Path) -> None:
        ExcelExporter().write(competition, path)

    def export_csv(self, competition: Competition, path: str | Path) -> None:
        CsvExporter().write(competition, path)

    def export_pdf(self, competition: Competition, path: str | Path) -> None:
        PdfExporter().write(competition, path)

    def export_grid_pdf(
        self,
        competition: Competition,
        path: str | Path,
        start_location_id: str | None = None,
    ) -> None:
        PdfExporter().write_grid(competition, path, start_location_id)
