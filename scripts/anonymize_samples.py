#!/usr/bin/env python3
"""One-shot anonymizer used to create public sample fixtures.

Historical sources (kompassi-2025 / am-pitka-2023) were removed after the first run.
Re-running requires restoring those private source directories privately — do not
commit real personal data.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"

LAST_NAMES = [
    "Virtanen",
    "Korhonen",
    "Makinen",
    "Nieminen",
    "Hakkinen",
    "Laine",
    "Heikkinen",
    "Koskinen",
    "Jarvinen",
    "Lehtinen",
    "Saarinen",
    "Salminen",
    "Rantanen",
    "Aalto",
    "Tamminen",
]
FIRST_NAMES = [
    "Aino",
    "Elias",
    "Helmi",
    "Onni",
    "Aada",
    "Eero",
    "Sofia",
    "Leo",
    "Emma",
    "Otto",
    "Lilja",
    "Vaino",
    "Venla",
    "Noel",
    "Saimi",
]


def _decode(raw: bytes) -> tuple[str, str]:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace"), "latin-1"


def _stable_int(key: str, mod: int) -> int:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % mod


def fake_name(key: str) -> str:
    last = LAST_NAMES[_stable_int(key + ":last", len(LAST_NAMES))]
    first = FIRST_NAMES[_stable_int(key + ":first", len(FIRST_NAMES))]
    return f"{last} {first}"


def fake_club(original: str, club_map: dict[str, str]) -> str:
    if original not in club_map:
        idx = len(club_map)
        # AAA, AAB, ... style codes
        a = idx // (26 * 26)
        b = (idx // 26) % 26
        c = idx % 26
        club_map[original] = f"{chr(65 + a)}{chr(65 + b)}{chr(65 + c)}"
    return club_map[original]


def anonymize_ilmoit_csv(
    src: Path,
    dest: Path,
    *,
    id_start: int,
    emit_start: int,
    club_map: dict[str, str],
) -> tuple[int, int]:
    text, _enc = _decode(src.read_bytes())
    lines = text.splitlines()
    out: list[str] = []
    next_id = id_start
    next_emit = emit_start
    for line in lines:
        if not line.strip() or line.startswith("="):
            out.append(line)
            continue
        parts = line.split(",")
        if len(parts) < 3:
            out.append(line)
            continue
        class_name = parts[0].strip()
        old_id = parts[1].strip()
        key = f"{class_name}:{old_id}:{parts[2]}"
        name = fake_name(key)
        club = fake_club(parts[3].strip() if len(parts) > 3 else "", club_map)
        emit_raw = parts[4].strip() if len(parts) > 4 else ""
        if emit_raw in ("", "0"):
            emit = emit_raw
        else:
            emit = str(next_emit)
            next_emit += 1
        new_id = str(next_id)
        next_id += 1
        rest = parts[5:] if len(parts) > 5 else []
        out.append(",".join([class_name, new_id, name, club, emit, *rest]))
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Write UTF-8 for public samples (importer still accepts cp1252)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    return next_id, next_emit


def anonymize_coursedata(src: Path, dest: Path, event_name: str) -> None:
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(src), parser)
    root = tree.getroot()
    ns = {"iof": "http://www.orienteering.org/datastandard/3.0"}

    for name_el in root.findall("iof:Event/iof:Name", ns):
        name_el.text = event_name

    # Also handle default namespace without prefix in findall via local-name
    for el in root.xpath("//*[local-name()='Event']/*[local-name()='Name']"):
        el.text = event_name

    for tag in ("Position", "MapPosition", "Map"):
        for el in root.xpath(f"//*[local-name()='{tag}']"):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)

    # Neutralize creator string slightly (keep Condes version info for format realism)
    creator = root.get("creator")
    if creator:
        root.set("creator", re.sub(r"Condes version [\d.]+", "Condes", creator))

    dest.parent.mkdir(parents=True, exist_ok=True)
    tree.write(
        str(dest),
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )


def build_sample_small() -> None:
    src_dir = SAMPLES / "kompassi-2025"
    dest_dir = SAMPLES / "sample-small"
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)

    club_map: dict[str, str] = {}
    anonymize_ilmoit_csv(
        src_dir / "ilmoittautumiset.csv",
        dest_dir / "ilmoittautumiset.csv",
        id_start=100001,
        emit_start=200001,
        club_map=club_map,
    )
    xml_src = next(src_dir.glob("*_coursedata.xml"))
    anonymize_coursedata(
        xml_src,
        dest_dir / "sample_small_coursedata.xml",
        "Sample Small Event",
    )
    (dest_dir / "README.md").write_text(
        "# Sample Small (anonymized)\n\n"
        "- `sample_small_coursedata.xml` — IOF 3.0 CourseData with ClassCourseAssignment\n"
        "- `ilmoittautumiset.csv` — IRMA `= ILMOIT` entries (~38 competitors)\n\n"
        "Synthetic names/clubs/ids. Course and class structure preserved for tests.\n",
        encoding="utf-8",
    )


def build_sample_medium() -> None:
    src_dir = SAMPLES / "am-pitka-2023"
    dest_dir = SAMPLES / "sample-medium"
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)

    club_map: dict[str, str] = {}
    next_id, next_emit = anonymize_ilmoit_csv(
        src_dir / "ilmoittautumiset.csv",
        dest_dir / "ilmoittautumiset.csv",
        id_start=110001,
        emit_start=210001,
        club_map=club_map,
    )
    anonymize_ilmoit_csv(
        src_dir / "jalki_ilmoittautumiset.csv",
        dest_dir / "jalki_ilmoittautumiset.csv",
        id_start=next_id,
        emit_start=next_emit,
        club_map=club_map,
    )

    xmls = sorted(src_dir.glob("*_coursedata.xml"))
    # Preserve scale distinction with neutral names
    for xml in xmls:
        name = xml.name.lower()
        if "10000" in name:
            dest_name = "sample_medium_10000_coursedata.xml"
        elif "7500" in name:
            dest_name = "sample_medium_7500_coursedata.xml"
        else:
            dest_name = f"sample_medium_{xml.stem}_coursedata.xml"
        anonymize_coursedata(xml, dest_dir / dest_name, "Sample Medium Event")

    (dest_dir / "README.md").write_text(
        "# Sample Medium (anonymized)\n\n"
        "- `sample_medium_10000_coursedata.xml` / `sample_medium_7500_coursedata.xml`\n"
        "- `ilmoittautumiset.csv` — ~201 competitors\n"
        "- `jalki_ilmoittautumiset.csv` — late entries fixture (v0.3)\n\n"
        "Synthetic personal data. Import both CourseData files and merge.\n",
        encoding="utf-8",
    )


def remove_legacy() -> None:
    for name in ("kompassi-2025", "am-pitka-2023"):
        path = SAMPLES / name
        if path.exists():
            shutil.rmtree(path)


def main() -> None:
    if not (SAMPLES / "kompassi-2025").exists():
        raise SystemExit("Source samples/kompassi-2025 missing")
    if not (SAMPLES / "am-pitka-2023").exists():
        raise SystemExit("Source samples/am-pitka-2023 missing")
    build_sample_small()
    build_sample_medium()
    remove_legacy()
    print("Wrote samples/sample-small and samples/sample-medium; removed legacy dirs.")


if __name__ == "__main__":
    main()
