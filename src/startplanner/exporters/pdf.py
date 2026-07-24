"""PDF exporter for ClassStartPlan (organizer printout)."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from startplanner.domain import Competition
from startplanner.exporters.excel import _plan_rows

_FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/Arial.ttf"),
)


class PdfExporter:
    def write(
        self,
        competition: Competition,
        path: str | Path,
        start_location_id: str | None = None,
    ) -> None:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        font_name = self._setup_font(pdf)
        pdf.add_page()
        pdf.set_font(font_name, "B", 16)
        title = competition.name or "Kilpailu"
        pdf.cell(0, 10, text=title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(font_name, size=11)
        event = (
            competition.event_date.isoformat() if competition.event_date else "—"
        )
        pdf.cell(0, 7, text=f"Päivä: {event}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(
            0,
            7,
            text=(
                "Kilpailun alku: "
                f"{competition.settings.competition_start.strftime('%H:%M')}"
            ),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.cell(
            0,
            7,
            text=(
                f"Oletusväli: {competition.settings.default_start_interval_min} min · "
                f"Sarjaväli: {competition.settings.class_gap_min} min"
            ),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(4)

        location_ids = (
            [start_location_id]
            if start_location_id
            else sorted(competition.plans.keys())
        )
        if not any(competition.plan_for(lid) for lid in location_ids):
            pdf.set_font(font_name, size=11)
            pdf.cell(0, 8, text="Ei lähtökaaviota.", new_x="LMARGIN", new_y="NEXT")
        else:
            for loc_id in location_ids:
                plan = competition.plan_for(loc_id)
                if not plan:
                    continue
                loc = competition.start_locations.get(loc_id)
                loc_name = loc.name if loc else loc_id
                pdf.set_font(font_name, "B", 13)
                pdf.cell(
                    0,
                    8,
                    text=f"Lähtö: {loc_name}",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                self._write_plan_table(pdf, competition, loc_id, font_name)
                pdf.ln(6)

        pdf.output(str(path))

    @staticmethod
    def _setup_font(pdf: FPDF) -> str:
        for candidate in _FONT_CANDIDATES:
            if candidate.is_file():
                pdf.add_font("AppSans", "", str(candidate))
                pdf.add_font("AppSans", "B", str(candidate))
                return "AppSans"
        return "Helvetica"

    def _write_plan_table(
        self,
        pdf: FPDF,
        competition: Competition,
        loc_id: str,
        font_name: str,
    ) -> None:
        rows = _plan_rows(competition, loc_id)
        if len(rows) <= 1:
            pdf.set_font(font_name, size=10)
            pdf.cell(0, 6, text="(tyhjä kaavio)", new_x="LMARGIN", new_y="NEXT")
            return
        headers = rows[0][1:]
        data = [r[1:] for r in rows[1:]]
        col_widths = [14, 18, 28, 16, 14, 28, 16]
        while len(col_widths) < len(headers):
            col_widths.append(20)
        col_widths = col_widths[: len(headers)]

        pdf.set_font(font_name, "B", 8)
        for width, header in zip(col_widths, headers):
            pdf.cell(width, 6, text=str(header), border=1)
        pdf.ln()
        pdf.set_font(font_name, size=8)
        for row in data:
            for width, value in zip(col_widths, row):
                pdf.cell(width, 5, text=str(value), border=1)
            pdf.ln()
