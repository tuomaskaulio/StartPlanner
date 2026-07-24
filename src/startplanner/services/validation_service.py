"""Validation service — ClassStartPlan rules per StartLocation."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from startplanner.domain import ClassStartPlan, Competition, RaceClass
from startplanner.validation.issues import Issue, Severity, ValidationReport


class ValidationService:
    def validate(
        self,
        competition: Competition,
        *,
        start_location_id: str | None = None,
        require_plan: bool = False,
    ) -> ValidationReport:
        issues: list[Issue] = []
        issues.extend(self._data_integrity(competition))
        locations = (
            [start_location_id]
            if start_location_id
            else list(competition.plans.keys())
            or list(competition.start_locations.keys())
        )
        for loc_id in locations:
            if not loc_id:
                continue
            plan = competition.plan_for(loc_id)
            if require_plan or plan:
                if not plan:
                    issues.append(
                        Issue(
                            "plan.missing",
                            Severity.ERROR,
                            f"Lähdöltä {loc_id} puuttuu lähtökaavio",
                            "start_location",
                            loc_id,
                        )
                    )
                else:
                    issues.extend(self._plan_rules(competition, plan))
        return ValidationReport(issues)

    def _data_integrity(self, competition: Competition) -> list[Issue]:
        issues: list[Issue] = []
        if not competition.name.strip():
            issues.append(
                Issue("competition.name", Severity.ERROR, "Kilpailulta puuttuu nimi")
            )
        if not competition.start_locations:
            issues.append(
                Issue(
                    "competition.start_location",
                    Severity.ERROR,
                    "Kilpailulta puuttuu lähtö",
                )
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
            if not rc.start_location_id:
                issues.append(
                    Issue(
                        "class.start_location",
                        Severity.ERROR,
                        f"Sarjalta {rc.name} puuttuu lähtö",
                        "class",
                        rc.id,
                    )
                )
            elif (
                competition.start_locations
                and rc.start_location_id not in competition.start_locations
            ):
                issues.append(
                    Issue(
                        "class.start_location",
                        Severity.ERROR,
                        f"Sarjan {rc.name} lähtöä ei löydy",
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

    def _plan_rules(
        self, competition: Competition, plan: ClassStartPlan
    ) -> list[Issue]:
        issues: list[Issue] = []
        if not plan.entries:
            issues.append(
                Issue(
                    "plan.empty",
                    Severity.ERROR,
                    "Lähtökaavio on tyhjä",
                    "start_location",
                    plan.start_location_id,
                )
            )
            return issues

        by_class = {e.class_id: e for e in plan.entries}
        for rc in competition.classes_at_location(plan.start_location_id):
            if (
                rc.course_id
                and competition.competitor_count(rc.id) > 0
                and rc.id not in by_class
            ):
                issues.append(
                    Issue(
                        "plan.missing_class",
                        Severity.ERROR,
                        f"Sarjalta {rc.name} puuttuu ensimmäinen lähtöaika",
                        "class",
                        rc.id,
                    )
                )

        # Course interleave within location
        by_course: dict[str, list[tuple[RaceClass, datetime, datetime]]] = defaultdict(
            list
        )
        for entry in plan.entries:
            rc = competition.classes.get(entry.class_id)
            if not rc or not rc.course_id:
                continue
            end = competition.class_span_end(rc, entry.first_start_time)
            by_course[rc.course_id].append((rc, entry.first_start_time, end))

        for course_id, spans in by_course.items():
            course = competition.courses.get(course_id)
            course_name = course.name if course else course_id
            ordered = sorted(spans, key=lambda t: t[1])
            for (a_rc, _a0, a1), (b_rc, b0, _b1) in zip(ordered, ordered[1:]):
                if b0 <= a1:
                    issues.append(
                        Issue(
                            "plan.course_interleave",
                            Severity.ERROR,
                            f"Radan {course_name} sarjat {a_rc.name} ja {b_rc.name} limittäin",
                            "course",
                            course_id,
                        )
                    )

        # First control: at most 1 competitor per minute within this location
        load: dict[tuple[str, datetime], float] = defaultdict(float)
        for entry in plan.entries:
            rc = competition.classes.get(entry.class_id)
            if not rc:
                continue
            first = competition.first_control_for_class(rc)
            if not first:
                continue
            n = max(competition.competitor_count(rc.id), 1)
            for i in range(n):
                minute = (
                    entry.first_start_time + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
                load[(first, minute)] += 1.0
        for (control, minute), count in load.items():
            if count > 1 + 1e-9:
                issues.append(
                    Issue(
                        "plan.first_control",
                        Severity.ERROR,
                        f"Ensimmäinen rasti {control} ylikuormittuu klo "
                        f"{minute.strftime('%H:%M')} ({int(count)} kilpailijaa)",
                        "control",
                        control,
                    )
                )

        issues.extend(self._window_overflow(competition, plan))
        return issues

    def _window_overflow(
        self, competition: Competition, plan: ClassStartPlan
    ) -> list[Issue]:
        from startplanner.services.scheduler_service import SchedulerService

        classes = [
            rc
            for rc in competition.classes_at_location(plan.start_location_id)
            if rc.course_id
            and rc.course_id in competition.courses
            and competition.courses[rc.course_id].first_control
            and competition.competitor_count(rc.id) > 0
        ]
        if not classes:
            return []
        scheduler = SchedulerService()
        durations = scheduler._course_durations(competition, classes)
        bottleneck_id = scheduler._bottleneck_course_id(competition, durations)
        if not bottleneck_id or not durations:
            return []
        start = competition.start_datetime_for(plan.start_location_id)
        window_end = scheduler._schedule_window_end(start, durations)
        last_start: datetime | None = None
        for entry in plan.entries:
            rc = competition.classes.get(entry.class_id)
            if not rc:
                continue
            end = competition.class_span_end(rc, entry.first_start_time)
            if last_start is None or end > last_start:
                last_start = end
        if last_start is None or last_start <= window_end:
            return []
        overflow_min = int((last_start - window_end).total_seconds() // 60)
        if overflow_min <= 0:
            return []
        course = competition.courses.get(bottleneck_id)
        course_name = course.name if course else bottleneck_id
        return [
            Issue(
                "plan.window_overflow",
                Severity.WARNING,
                f"Aikataulu ylitti pullonkaularadan keston "
                f"(rata {course_name}, +{overflow_min} min)",
                "start_location",
                plan.start_location_id,
            )
        ]
