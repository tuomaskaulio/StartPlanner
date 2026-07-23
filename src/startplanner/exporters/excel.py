"""Excel and CSV exporters for ClassStartPlan."""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook

from startplanner.domain import Competition


def _plan_rows(competition: Competition, start_location_id: str | None = None) -> list[list[str]]:
    header = [
        "Lähtö",
        "1. lähtöaika",
        "Sarja",
        "Kilpailijoita",
        "Lähtöväli",
        "Rata",
        "1. rasti",
    ]
    rows = [header]
    location_ids = (
        [start_location_id]
        if start_location_id
        else sorted(competition.plans.keys())
    )
    for loc_id in location_ids:
        plan = competition.plan_for(loc_id)
        if not plan:
            continue
        loc = competition.start_locations.get(loc_id)
        loc_name = loc.name if loc else loc_id
        for entry in plan.sorted_entries():
            rc = competition.classes.get(entry.class_id)
            course = competition.course_for_class(rc) if rc else None
            rows.append(
                [
                    loc_name,
                    entry.first_start_time.strftime("%H:%M"),
                    rc.name if rc else "",
                    str(competition.competitor_count(entry.class_id)),
                    str(rc.start_interval_min if rc else ""),
                    course.name if course else "",
                    (course.first_control if course else "") or "",
                ]
            )
    return rows


class ExcelExporter:
    def write(
        self,
        competition: Competition,
        path: str | Path,
        start_location_id: str | None = None,
    ) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = "Lähtökaavio"
        for r_idx, row in enumerate(_plan_rows(competition, start_location_id), start=1):
            for c_idx, value in enumerate(row, start=1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        wb.save(path)


class CsvExporter:
    def write(
        self,
        competition: Competition,
        path: str | Path,
        start_location_id: str | None = None,
    ) -> None:
        with Path(path).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerows(_plan_rows(competition, start_location_id))
