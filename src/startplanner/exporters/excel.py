"""Excel and CSV exporters for start lists."""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook

from startplanner.domain import Competition


def _rows(competition: Competition) -> list[list[str]]:
    header = ["Aika", "Sarja", "Kilpailija", "Seura", "Rata", "1. rasti", "Lähtönumero", "Emit"]
    rows = [header]
    for start in competition.schedule.sorted_starts():
        comp = competition.competitors.get(start.competitor_id)
        rc = competition.classes.get(start.class_id)
        course = competition.courses.get(start.course_id)
        first = course.first_control if course else ""
        rows.append(
            [
                start.start_time.strftime("%H:%M"),
                rc.name if rc else "",
                comp.full_name if comp else "",
                comp.club if comp else "",
                course.name if course else "",
                first or "",
                str(start.start_number),
                (comp.emit or "") if comp else "",
            ]
        )
    return rows


class ExcelExporter:
    def write(self, competition: Competition, path: str | Path) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = "Lähtökaavio"
        for r_idx, row in enumerate(_rows(competition), start=1):
            for c_idx, value in enumerate(row, start=1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        wb.save(path)


class CsvExporter:
    def write(self, competition: Competition, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerows(_rows(competition))
