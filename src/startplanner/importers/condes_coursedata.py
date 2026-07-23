"""IOF 3.0 CourseData (Condes) importer."""

from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

from startplanner.domain import Competition, Course
from startplanner.domain.errors import ImportError_

IOF_NS = "http://www.orienteering.org/datastandard/3.0"
NS = {"iof": IOF_NS}


def _text(el: etree._Element | None, path: str, default: str = "") -> str:
    if el is None:
        return default
    found = el.find(path, NS)
    if found is None or found.text is None:
        return default
    return found.text.strip()


def class_tokens_from_course_name(name: str) -> list[str]:
    """Split Condes combined course names into class tokens."""
    parts = re.split(r"[/ ]+", name.strip())
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        if re.fullmatch(r"\d+", part):
            continue
        tokens.append(part)
    return tokens


class CondesCourseDataImporter:
    def supports(self, path: str | Path) -> bool:
        p = Path(path)
        if p.suffix.lower() != ".xml":
            return False
        try:
            head = p.read_bytes()[:500].decode("utf-8", errors="ignore")
        except OSError:
            return False
        return "CourseData" in head

    def read(self, path: str | Path) -> Competition:
        p = Path(path)
        try:
            tree = etree.parse(str(p))
        except etree.XMLSyntaxError as exc:
            raise ImportError_(f"Virheellinen CourseData-XML: {exc}") from exc
        root = tree.getroot()
        competition = Competition()
        competition.name = _text(root, "iof:Event/iof:Name") or p.stem
        self._merge_into(competition, root)
        return competition

    def merge(self, competition: Competition, path: str | Path) -> None:
        p = Path(path)
        try:
            tree = etree.parse(str(p))
        except etree.XMLSyntaxError as exc:
            raise ImportError_(f"Virheellinen CourseData-XML: {exc}") from exc
        root = tree.getroot()
        if not competition.name:
            competition.name = _text(root, "iof:Event/iof:Name") or p.stem
        self._merge_into(competition, root)

    def _merge_into(self, competition: Competition, root: etree._Element) -> None:
        for course_el in root.findall(".//iof:Course", NS):
            name = _text(course_el, "iof:Name")
            if not name:
                continue
            existing = competition.get_course_by_name(name)
            length = int(_text(course_el, "iof:Length", "0") or 0)
            climb = int(_text(course_el, "iof:Climb", "0") or 0)
            controls: list[str] = []
            for cc in course_el.findall("iof:CourseControl", NS):
                if cc.get("type") != "Control":
                    continue
                cid = _text(cc, "iof:Control")
                if cid:
                    controls.append(cid)
            if existing:
                if not existing.controls and controls:
                    existing.controls = controls
                if existing.length_m == 0 and length:
                    existing.length_m = length
                if existing.climb_m == 0 and climb:
                    existing.climb_m = climb
                course = existing
            else:
                course = Course(
                    id=f"course:{name}",
                    name=name,
                    length_m=length,
                    climb_m=climb,
                    controls=controls,
                )
                competition.add_course(course)

            for token in class_tokens_from_course_name(name):
                competition.class_course_map.setdefault(token, course.id)

        for assign in root.findall(".//iof:ClassCourseAssignment", NS):
            class_name = _text(assign, "iof:ClassName")
            course_name = _text(assign, "iof:CourseName")
            if not class_name or not course_name:
                continue
            course = competition.get_course_by_name(course_name)
            if course:
                competition.class_course_map[class_name] = course.id
