"""PDF exporter for ClassStartPlan (organizer printout)."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from startplanner.domain import Competition
from startplanner.exporters.excel import _plan_rows
from startplanner.services.course_grid import CourseGrid, build_course_grid

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

    def write_grid(
        self,
        competition: Competition,
        path: str | Path,
        start_location_id: str | None = None,
    ) -> None:
        """Landscape PDF of the minute × course grid for one or more starts."""
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=12)
        font_name = self._setup_font(pdf)

        location_ids = (
            [start_location_id]
            if start_location_id
            else sorted(competition.plans.keys())
        )
        wrote_any = False
        for loc_id in location_ids:
            plan = competition.plan_for(loc_id)
            if not plan or not plan.entries:
                continue
            grid = build_course_grid(competition, plan)
            if not grid.minutes:
                continue
            wrote_any = True
            loc = competition.start_locations.get(loc_id)
            loc_name = loc.name if loc else loc_id
            pdf.add_page()
            pdf.set_font(font_name, "B", 14)
            title = competition.name or "Kilpailu"
            pdf.cell(
                0,
                8,
                text=f"{title} — Ruudukko — {loc_name}",
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.ln(2)
            self._write_grid_table(pdf, grid, font_name)

        if not wrote_any:
            pdf.add_page()
            pdf.set_font(font_name, size=11)
            pdf.cell(
                0,
                8,
                text="Ei ruudukkoa (muodosta ensin lähtökaavio).",
                new_x="LMARGIN",
                new_y="NEXT",
            )

        pdf.output(str(path))

    def _write_grid_table(
        self, pdf: FPDF, grid: CourseGrid, font_name: str
    ) -> None:
        headers = ["Aika", "Yht"] + [
            f"{col.course_name} ({col.first_control or '—'})" for col in grid.columns
        ]
        usable = pdf.w - pdf.l_margin - pdf.r_margin
        n_cols = len(headers)
        time_w = 14.0
        total_w = 10.0
        rest = max(usable - time_w - total_w, 20.0)
        course_w = rest / max(n_cols - 2, 1)
        if course_w < 12:
            course_w = 12.0
            rest = course_w * max(n_cols - 2, 1)
            scale = usable / (time_w + total_w + rest)
            time_w *= scale
            total_w *= scale
            course_w *= scale
        widths = [time_w, total_w] + [course_w] * (n_cols - 2)

        row_h = 5.0
        font_size = 7 if n_cols <= 10 else 6
        pdf.set_font(font_name, "B", font_size)
        for width, header in zip(widths, headers):
            pdf.cell(width, row_h + 1, text=self._clip(str(header), width), border=1)
        pdf.ln()

        pdf.set_font(font_name, size=font_size)
        for minute in grid.minutes:
            if pdf.get_y() > pdf.h - pdf.b_margin - row_h * 2:
                pdf.add_page()
                pdf.set_font(font_name, "B", font_size)
                for width, header in zip(widths, headers):
                    pdf.cell(
                        width,
                        row_h + 1,
                        text=self._clip(str(header), width),
                        border=1,
                    )
                pdf.ln()
                pdf.set_font(font_name, size=font_size)

            values = [
                minute.strftime("%H:%M"),
                str(grid.total(minute)),
            ] + [grid.cell(minute, col.course_id) for col in grid.columns]
            for width, value in zip(widths, values):
                pdf.cell(width, row_h, text=self._clip(str(value), width), border=1)
            pdf.ln()

    @staticmethod
    def _clip(text: str, width_mm: float) -> str:
        """Rough clip so long class names fit a narrow cell."""
        max_chars = max(int(width_mm / 1.8), 3)
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 1] + "…"

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
