"""Validation service — hard scheduling and data-integrity rules."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from startplanner.domain import Competition, RaceClass
from startplanner.validation.issues import Issue, Severity, ValidationReport


class ValidationService:
    def validate(
        self, competition: Competition, *, require_schedule: bool = False
    ) -> ValidationReport:
        issues: list[Issue] = []
        issues.extend(self._data_integrity(competition))
        if require_schedule or competition.schedule.starts:
            issues.extend(self._schedule_rules(competition))
        return ValidationReport(issues)

    def _data_integrity(self, competition: Competition) -> list[Issue]:
        issues: list[Issue] = []
        if not competition.name.strip():
            issues.append(
                Issue("competition.name", Severity.ERROR, "Kilpailulta puuttuu nimi")
            )
        for course in competition.courses.values():
            if not course.controls:
                issues.append(
                    Issue(
                        "course.controls",
                        Severity.ERROR,
                        f"Radalla {course.name} ei ole rasteja",
                        "course",
                        course.id,
                    )
                )
        for rc in competition.classes.values():
            if not rc.course_id:
                issues.append(
                    Issue(
                        "class.course",
                        Severity.ERROR,
                        f"Sarjalta {rc.name} puuttuu rata",
                        "class",
                        rc.id,
                    )
                )
            elif rc.course_id not in competition.courses:
                issues.append(
                    Issue(
                        "class.course",
                        Severity.ERROR,
                        f"Sarjan {rc.name} rataa ei löydy",
                        "class",
                        rc.id,
                    )
                )
            if rc.start_interval_min <= 0:
                issues.append(
                    Issue(
                        "class.interval",
                        Severity.ERROR,
                        f"Sarjan {rc.name} lähtöväli on virheellinen",
                        "class",
                        rc.id,
                    )
                )
        for comp in competition.competitors.values():
            if not comp.class_id or comp.class_id not in competition.classes:
                issues.append(
                    Issue(
                        "competitor.class",
                        Severity.ERROR,
                        f"Kilpailijalta {comp.full_name} puuttuu sarja",
                        "competitor",
                        comp.id,
                    )
                )
            if not comp.first_name and not comp.last_name:
                issues.append(
                    Issue(
                        "competitor.name",
                        Severity.ERROR,
                        "Kilpailijalta puuttuu nimi",
                        "competitor",
                        comp.id,
                    )
                )
        return issues

    def _schedule_rules(self, competition: Competition) -> list[Issue]:
        issues: list[Issue] = []
        starts = competition.schedule.sorted_starts()
        if not starts:
            issues.append(
                Issue("schedule.empty", Severity.ERROR, "Lähtökaavio on tyhjä")
            )
            return issues

        scheduled_competitors = {s.competitor_id for s in starts}
        for comp in competition.competitors.values():
            rc = competition.classes.get(comp.class_id)
            if rc and rc.course_id and comp.id not in scheduled_competitors:
                issues.append(
                    Issue(
                        "schedule.missing_competitor",
                        Severity.ERROR,
                        f"Kilpailijalta {comp.full_name} puuttuu lähtöaika",
                        "competitor",
                        comp.id,
                    )
                )

        # Per-class start interval
        by_class: dict[str, list] = defaultdict(list)
        for start in starts:
            by_class[start.class_id].append(start)
        for class_id, class_starts in by_class.items():
            rc = competition.classes.get(class_id)
            if not rc:
                continue
            ordered = sorted(class_starts, key=lambda s: s.start_time)
            for prev, cur in zip(ordered, ordered[1:]):
                delta = (cur.start_time - prev.start_time).total_seconds() / 60
                if delta + 1e-9 < rc.start_interval_min:
                    issues.append(
                        Issue(
                            "schedule.interval",
                            Severity.ERROR,
                            f"Sarjan {rc.name} lähtöväli rikkoo "
                        f"{rc.start_interval_min} min sääntöä",
                            "class",
                            rc.id,
                        )
                    )
                    break

        # Same course classes must not interleave
        issues.extend(self._course_interleave(competition, by_class))

        # First control: max 1 competitor per minute
        by_minute_control: dict[tuple[str, datetime], list[str]] = defaultdict(list)
        for start in starts:
            rc = competition.classes.get(start.class_id)
            if not rc:
                continue
            first = competition.first_control_for_class(rc)
            if not first:
                continue
            minute = start.start_time.replace(second=0, microsecond=0)
            by_minute_control[(first, minute)].append(start.competitor_id)
        for (control, minute), competitor_ids in by_minute_control.items():
            if len(competitor_ids) > 1:
                issues.append(
                    Issue(
                        "schedule.first_control",
                        Severity.ERROR,
                        f"Ensimmäinen rasti {control} ylikuormittuu klo {minute.strftime('%H:%M')} "
                        f"({len(competitor_ids)} kilpailijaa)",
                        "control",
                        control,
                    )
                )

        return issues

    def _course_interleave(
        self, competition: Competition, by_class: dict[str, list]
    ) -> list[Issue]:
        issues: list[Issue] = []
        by_course: dict[str, list[tuple[RaceClass, datetime, datetime]]] = defaultdict(list)
        for class_id, class_starts in by_class.items():
            rc = competition.classes.get(class_id)
            if not rc or not rc.course_id or not class_starts:
                continue
            times = [s.start_time for s in class_starts]
            by_course[rc.course_id].append((rc, min(times), max(times)))

        for course_id, spans in by_course.items():
            course = competition.courses.get(course_id)
            course_name = course.name if course else course_id
            ordered = sorted(spans, key=lambda t: t[1])
            for (a_rc, _a0, a1), (b_rc, b0, _b1) in zip(ordered, ordered[1:]):
                if b0 <= a1:
                    issues.append(
                        Issue(
                            "schedule.course_interleave",
                            Severity.ERROR,
                            f"Radan {course_name} sarjat {a_rc.name} ja {b_rc.name} limittäin",
                            "course",
                            course_id,
                        )
                    )
        return issues
