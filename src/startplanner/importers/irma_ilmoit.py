"""IRMA = ILMOIT registration CSV importer."""

from __future__ import annotations

from pathlib import Path

from startplanner.domain import Competition, Competitor, RaceClass
from startplanner.domain.errors import ImportError_


def _decode(raw: bytes) -> str:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def _split_name(full: str) -> tuple[str, str]:
    full = full.strip()
    if not full:
        return "", ""
    parts = full.split()
    if len(parts) == 1:
        return parts[0], ""
    # IRMA often: "Last First" or "Last First Middle"
    return parts[0], " ".join(parts[1:])


class IrmaIlmoitImporter:
    def supports(self, path: str | Path) -> bool:
        p = Path(path)
        if p.suffix.lower() != ".csv":
            return False
        try:
            text = _decode(p.read_bytes()[:200])
        except OSError:
            return False
        return text.lstrip().startswith("= ILMOIT")

    def read(
        self, path: str | Path, *, late: bool = False
    ) -> list[tuple[str, Competitor]]:
        """Return list of (class_name, competitor) without attaching to competition."""
        p = Path(path)
        try:
            text = _decode(p.read_bytes())
        except OSError as exc:
            raise ImportError_(f"Ilmoittautumistiedostoa ei voi lukea: {exc}") from exc
        lines = text.splitlines()
        if not lines or not lines[0].lstrip().startswith("= ILMOIT"):
            raise ImportError_("Tiedosto ei ole IRMA ILMOIT -muotoinen")

        rows: list[tuple[str, Competitor]] = []
        for line in lines[1:]:
            if not line.strip() or line.startswith("="):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            class_name = parts[0].strip()
            external_id = parts[1].strip()
            last, first = _split_name(parts[2])
            club = parts[3].strip() if len(parts) > 3 else ""
            emit = parts[4].strip() if len(parts) > 4 else ""
            birth_year = None
            if len(parts) > 5 and parts[5].strip().isdigit():
                birth_year = int(parts[5].strip())
            if emit in ("", "0"):
                emit_val = None
            else:
                emit_val = emit
            competitor = Competitor(
                id=f"comp:{external_id}" if external_id else f"comp:{class_name}:{last}:{first}",
                first_name=first,
                last_name=last,
                club=club,
                emit=emit_val,
                birth_year=birth_year,
                late=late,
            )
            rows.append((class_name, competitor))
        return rows

    def apply_to(
        self, competition: Competition, path: str | Path, *, late: bool = False
    ) -> int:
        rows = self.read(path, late=late)
        count = 0
        for class_name, competitor in rows:
            rc = competition.get_class_by_name(class_name)
            if rc is None:
                course_id = competition.class_course_map.get(class_name)
                rc = RaceClass(
                    id=f"class:{class_name}",
                    name=class_name,
                    course_id=course_id,
                    start_interval_min=competition.settings.default_start_interval_min,
                )
                competition.add_class(rc)
            elif not rc.course_id:
                rc.course_id = competition.class_course_map.get(class_name)
            competitor.class_id = rc.id
            competition.add_competitor(competitor)
            count += 1
        # Ensure classes from map exist even without entries? skip
        self._apply_course_map(competition)
        return count

    def _apply_course_map(self, competition: Competition) -> None:
        for rc in competition.classes.values():
            if not rc.course_id and rc.name in competition.class_course_map:
                rc.course_id = competition.class_course_map[rc.name]
