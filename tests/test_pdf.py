"""PDF export tests."""

from pathlib import Path

from startplanner.services.import_service import ExportService, ImportService
from startplanner.services.scheduler_service import SchedulerService

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_SMALL = ROOT / "samples" / "sample-small"


def test_pdf_export_creates_file(tmp_path: Path):
    competition = ImportService().import_coursedata(
        next(SAMPLE_SMALL.glob("*_coursedata.xml"))
    )
    ImportService().import_entries(competition, SAMPLE_SMALL / "ilmoittautumiset.csv")
    SchedulerService().apply(competition)
    path = tmp_path / "kaavio.pdf"
    ExportService().export_pdf(competition, path)
    assert path.is_file()
    assert path.stat().st_size > 100
    assert path.read_bytes()[:4] == b"%PDF"
