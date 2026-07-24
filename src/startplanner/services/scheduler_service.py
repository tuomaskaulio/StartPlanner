"""Greedy deterministic ClassStartPlan builder (per StartLocation)."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from uuid import uuid4

from startplanner.domain import (
    ClassStart,
    ClassStartPlan,
    Competition,
    RaceClass,
)
from startplanner.domain.errors import ScheduleError


class SchedulerService:
    def build(
        self,
        competition: Competition,
        start_location_id: str | None = None,
        *,
        preserve_existing: bool = False,
    ) -> ClassStartPlan:
        location_id = self._resolve_location(competition, start_location_id)
        classes = self._ordered_classes(competition, location_id)
        if not classes:
            raise ScheduleError(
                "Ei sijoitettavia sarjoja tässä lähdössä (rata ja kilpailijat puuttuvat)"
            )

        start = competition.start_datetime_for(location_id)
        course_durations = self._course_durations(competition, classes)
        bottleneck_id = self._bottleneck_course_id(competition, course_durations)
        estimated_window = self._schedule_window_end(start, course_durations)
        total_starts = sum(
            max(competition.competitor_count(rc.id), 1) for rc in classes
        )
        target_load = self._target_load(total_starts, start, estimated_window)

        existing = competition.plan_for(location_id)
        locked_times: dict[str, datetime] = {}
        existing_entries: dict[str, ClassStart] = {}
        if existing:
            for entry in existing.entries:
                existing_entries[entry.class_id] = entry
                rc = competition.classes.get(entry.class_id)
                if preserve_existing:
                    locked_times[entry.class_id] = entry.first_start_time
                elif rc and (rc.locked or entry.locked):
                    locked_times[entry.class_id] = entry.first_start_time

        bottleneck_classes = [rc for rc in classes if rc.course_id == bottleneck_id]
        other_classes = [rc for rc in classes if rc.course_id != bottleneck_id]

        # Pass 1: spine + others (may overflow estimated window).
        occupied: dict[str, set[datetime]] = {}
        course_end: dict[str, datetime] = {}
        minute_load: dict[datetime, int] = defaultdict(int)
        entries: list[ClassStart] = []

        self._seed_locked(
            competition,
            locked_times,
            occupied,
            course_end,
            minute_load,
        )

        for rc in bottleneck_classes:
            self._place_class(
                competition=competition,
                rc=rc,
                start=start,
                window_end=estimated_window,
                course_durations=course_durations,
                occupied=occupied,
                course_end=course_end,
                minute_load=minute_load,
                locked_times=locked_times,
                existing_entries=existing_entries,
                entries=entries,
                mode="earliest",
                target_load=target_load,
            )

        # Effective fill window: at least estimated; grow with actual spine end.
        window_end = max(
            estimated_window,
            self._entries_last_minute(competition, entries) or estimated_window,
        )

        for rc in other_classes:
            mode = "balanced" if rc.course_id not in course_end else "earliest"
            self._place_class(
                competition=competition,
                rc=rc,
                start=start,
                window_end=window_end,
                course_durations=course_durations,
                occupied=occupied,
                course_end=course_end,
                minute_load=minute_load,
                locked_times=locked_times,
                existing_entries=existing_entries,
                entries=entries,
                mode=mode,
                target_load=target_load,
            )

        # Pass 2: use the actual maximum end (may exceed estimated bottleneck) as
        # the fill window and redistribute unlocked non-bottleneck classes evenly.
        actual_end = self._entries_last_minute(competition, entries)
        fill_window = window_end
        if actual_end is not None and actual_end > fill_window:
            fill_window = actual_end
        if other_classes:
            entries, _occupied, _course_end, _minute_load = self._rebalance_others(
                competition=competition,
                start=start,
                window_end=fill_window,
                course_durations=course_durations,
                bottleneck_classes=bottleneck_classes,
                other_classes=other_classes,
                locked_times=locked_times,
                existing_entries=existing_entries,
                entries=entries,
                total_starts=total_starts,
            )

        return ClassStartPlan(start_location_id=location_id, entries=entries)

    def _rebalance_others(
        self,
        *,
        competition: Competition,
        start: datetime,
        window_end: datetime,
        course_durations: dict[str, int],
        bottleneck_classes: list[RaceClass],
        other_classes: list[RaceClass],
        locked_times: dict[str, datetime],
        existing_entries: dict[str, ClassStart],
        entries: list[ClassStart],
        total_starts: int,
    ) -> tuple[
        list[ClassStart],
        dict[str, set[datetime]],
        dict[str, datetime],
        dict[datetime, int],
    ]:
        keep_ids = {rc.id for rc in bottleneck_classes} | set(locked_times.keys())
        kept = [e for e in entries if e.class_id in keep_ids]
        occupied: dict[str, set[datetime]] = {}
        course_end: dict[str, datetime] = {}
        minute_load: dict[datetime, int] = defaultdict(int)
        target_load = self._target_load(total_starts, start, window_end)

        for entry in kept:
            rc = competition.classes.get(entry.class_id)
            if not rc or not rc.course_id:
                continue
            course = competition.course_for_class(rc)
            if not course or not course.first_control:
                continue
            n = max(competition.competitor_count(rc.id), 1)
            for i in range(n):
                slot = (
                    entry.first_start_time
                    + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
                occupied.setdefault(course.first_control, set()).add(slot)
                minute_load[slot] += 1
            course_end[rc.course_id] = max(
                course_end.get(rc.course_id, entry.first_start_time),
                competition.class_span_end(rc, entry.first_start_time),
            )

        new_entries = list(kept)
        for rc in other_classes:
            if rc.id in locked_times:
                # Already in kept
                continue
            mode = "balanced" if rc.course_id not in course_end else "earliest"
            self._place_class(
                competition=competition,
                rc=rc,
                start=start,
                window_end=window_end,
                course_durations=course_durations,
                occupied=occupied,
                course_end=course_end,
                minute_load=minute_load,
                locked_times=locked_times,
                existing_entries=existing_entries,
                entries=new_entries,
                mode=mode,
                target_load=target_load,
            )
        return new_entries, occupied, course_end, minute_load

    def _seed_locked(
        self,
        competition: Competition,
        locked_times: dict[str, datetime],
        occupied: dict[str, set[datetime]],
        course_end: dict[str, datetime],
        minute_load: dict[datetime, int],
    ) -> None:
        for class_id, placement in locked_times.items():
            rc = competition.classes.get(class_id)
            if not rc or not rc.course_id:
                continue
            course = competition.course_for_class(rc)
            if not course or not course.first_control:
                continue
            n = max(competition.competitor_count(rc.id), 1)
            for i in range(n):
                slot = (
                    placement + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
                occupied.setdefault(course.first_control, set()).add(slot)
                minute_load[slot] += 1
            course_end[rc.course_id] = max(
                course_end.get(rc.course_id, placement),
                competition.class_span_end(rc, placement),
            )

    @staticmethod
    def _entries_last_minute(
        competition: Competition, entries: list[ClassStart]
    ) -> datetime | None:
        last: datetime | None = None
        for entry in entries:
            rc = competition.classes.get(entry.class_id)
            if not rc:
                continue
            end = competition.class_span_end(rc, entry.first_start_time)
            if last is None or end > last:
                last = end
        return last

    def _place_class(
        self,
        *,
        competition: Competition,
        rc: RaceClass,
        start: datetime,
        window_end: datetime,
        course_durations: dict[str, int],
        occupied: dict[str, set[datetime]],
        course_end: dict[str, datetime],
        minute_load: dict[datetime, int],
        locked_times: dict[str, datetime],
        existing_entries: dict[str, ClassStart],
        entries: list[ClassStart],
        mode: str,
        target_load: float,
    ) -> None:
        n = max(competition.competitor_count(rc.id), 1)
        course = competition.course_for_class(rc)
        assert course is not None and course.first_control
        first_control = course.first_control
        gap = timedelta(minutes=competition.class_gap_for_course(rc.course_id))

        if rc.id in locked_times:
            placement = locked_times[rc.id]
        else:
            earliest = start
            if rc.course_id in course_end:
                earliest = max(earliest, course_end[rc.course_id] + gap)
            if mode == "balanced":
                # Leave room for the whole course stream inside the window.
                course_dur = course_durations.get(rc.course_id or "", 1)
                latest = window_end - timedelta(minutes=max(course_dur - 1, 0))
                if latest < earliest:
                    latest = earliest
                placement = self._find_balanced_placement(
                    earliest=earliest,
                    latest=latest,
                    count=n,
                    interval_min=rc.start_interval_min,
                    first_control=first_control,
                    occupied=occupied,
                    minute_load=minute_load,
                    target_load=target_load,
                    window_start=start,
                    window_end=window_end,
                    phased=rc.start_interval_min == 2 and n > 1,
                )
            else:
                placement = self._find_earliest_placement(
                    earliest=earliest,
                    count=n,
                    interval_min=rc.start_interval_min,
                    first_control=first_control,
                    occupied=occupied,
                )

        prev = existing_entries.get(rc.id)
        entry_locked = (
            prev.locked
            if prev is not None
            else (rc.locked or rc.id in locked_times)
        )
        entries.append(
            ClassStart(
                id=prev.id if prev is not None else str(uuid4()),
                class_id=rc.id,
                first_start_time=placement,
                locked=entry_locked,
            )
        )
        if rc.id not in locked_times:
            for i in range(n):
                slot = (
                    placement + timedelta(minutes=i * rc.start_interval_min)
                ).replace(second=0, microsecond=0)
                occupied.setdefault(first_control, set()).add(slot)
                minute_load[slot] += 1

            last_time = competition.class_span_end(rc, placement)
            if rc.course_id:
                course_end[rc.course_id] = max(
                    course_end.get(rc.course_id, last_time), last_time
                )

    def apply(
        self,
        competition: Competition,
        start_location_id: str | None = None,
        *,
        preserve_existing: bool = False,
    ) -> ClassStartPlan:
        plan = self.build(
            competition, start_location_id, preserve_existing=preserve_existing
        )
        competition.set_plan(plan)
        return plan

    def update(
        self, competition: Competition, start_location_id: str | None = None
    ) -> ClassStartPlan:
        """Reschedule while keeping existing plan times fixed."""
        return self.apply(competition, start_location_id, preserve_existing=True)

    def _resolve_location(
        self, competition: Competition, start_location_id: str | None
    ) -> str:
        competition.ensure_default_start_location()
        if start_location_id:
            if start_location_id not in competition.start_locations:
                raise ScheduleError(f"Tuntematon lähtö: {start_location_id}")
            return start_location_id
        return next(iter(competition.start_locations))

    def _ordered_classes(
        self, competition: Competition, start_location_id: str
    ) -> list[RaceClass]:
        classes = [
            rc
            for rc in competition.classes_at_location(start_location_id)
            if rc.course_id
            and rc.course_id in competition.courses
            and competition.courses[rc.course_id].first_control
            and competition.competitor_count(rc.id) > 0
        ]

        def sort_key(rc: RaceClass) -> tuple:
            n = max(competition.competitor_count(rc.id), 1)
            stream = self._class_stream_minutes(rc, n)
            course = competition.course_for_class(rc)
            length = course.length_m if course else 0
            return (-stream, -rc.estimated_speed, -length, rc.sort_order, rc.name)

        return sorted(classes, key=sort_key)

    @staticmethod
    def _class_stream_minutes(rc: RaceClass, count: int) -> int:
        if count <= 1:
            return 1
        return (count - 1) * rc.start_interval_min + 1

    @staticmethod
    def _course_durations(
        competition: Competition, classes: list[RaceClass]
    ) -> dict[str, int]:
        by_course: dict[str, list[RaceClass]] = defaultdict(list)
        for rc in classes:
            if rc.course_id:
                by_course[rc.course_id].append(rc)
        durations: dict[str, int] = {}
        for course_id, rcs in by_course.items():
            total = 0
            for rc in rcs:
                n = max(competition.competitor_count(rc.id), 1)
                total += SchedulerService._class_stream_minutes(rc, n)
            gap = competition.class_gap_for_course(course_id)
            total += gap * max(len(rcs) - 1, 0)
            durations[course_id] = total
        return durations

    @staticmethod
    def _bottleneck_course_id(
        competition: Competition, durations: dict[str, int]
    ) -> str | None:
        if not durations:
            return None

        def key(course_id: str) -> tuple:
            course = competition.courses.get(course_id)
            name = course.name if course else course_id
            return (-durations[course_id], name)

        return min(durations.keys(), key=key)

    @staticmethod
    def _schedule_window_end(
        start: datetime, durations: dict[str, int]
    ) -> datetime:
        if not durations:
            return start
        # Duration includes first and last minute of the stream.
        minutes = max(durations.values())
        return start + timedelta(minutes=max(minutes - 1, 0))

    @staticmethod
    def _target_load(
        total_starts: int, window_start: datetime, window_end: datetime
    ) -> float:
        minutes = max(
            int((window_end - window_start).total_seconds() // 60) + 1,
            1,
        )
        return total_starts / minutes

    @staticmethod
    def _candidate_times(
        earliest: datetime,
        latest: datetime,
        *,
        interval_min: int,
        phased: bool,
    ) -> list[datetime]:
        first = earliest.replace(second=0, microsecond=0)
        limit = latest.replace(second=0, microsecond=0)
        if limit < first:
            return [first]

        candidates: list[datetime] = []
        t = first
        while t <= limit:
            candidates.append(t)
            t += timedelta(minutes=1)
        if not phased or interval_min <= 1:
            return candidates

        first_phase = SchedulerService._minute_index(first) % interval_min
        return sorted(
            candidates,
            key=lambda candidate: (
                SchedulerService._minute_index(candidate) % interval_min
                != first_phase,
                candidate,
            ),
        )

    @staticmethod
    def _minute_index(value: datetime) -> int:
        return value.toordinal() * 24 * 60 + value.hour * 60 + value.minute

    def _find_earliest_placement(
        self,
        *,
        earliest: datetime,
        count: int,
        interval_min: int,
        first_control: str,
        occupied: dict[str, set[datetime]],
    ) -> datetime:
        t = earliest.replace(second=0, microsecond=0)
        busy = occupied.get(first_control, set())
        while True:
            if self._slots_available(t, count, interval_min, busy):
                return t
            t += timedelta(minutes=1)

    def _find_balanced_placement(
        self,
        *,
        earliest: datetime,
        latest: datetime,
        count: int,
        interval_min: int,
        first_control: str,
        occupied: dict[str, set[datetime]],
        minute_load: dict[datetime, int],
        target_load: float,
        window_start: datetime,
        window_end: datetime,
        phased: bool,
    ) -> datetime:
        """Place within [earliest, latest]; if none fit, extend minimally after latest."""
        busy = occupied.get(first_control, set())
        best: datetime | None = None
        best_score: tuple[float, int, int, int, float] | None = None
        candidates = self._candidate_times(
            earliest,
            latest,
            interval_min=interval_min,
            phased=phased,
        )

        for t in candidates:
            if self._slots_available(t, count, interval_min, busy):
                score = self._placement_flow_score(
                    t,
                    count,
                    interval_min,
                    minute_load,
                    target_load=target_load,
                    window_start=window_start,
                    window_end=window_end,
                )
                if best_score is None or score < best_score:
                    best_score = score
                    best = t

        if best is not None:
            return best
        # Overflow: extend past window with earliest valid slot.
        return self._find_earliest_placement(
            earliest=max(earliest, latest + timedelta(minutes=1)),
            count=count,
            interval_min=interval_min,
            first_control=first_control,
            occupied=occupied,
        )

    @staticmethod
    def _slots_available(
        start: datetime,
        count: int,
        interval_min: int,
        busy: set[datetime],
    ) -> bool:
        for i in range(count):
            slot = (start + timedelta(minutes=i * interval_min)).replace(
                second=0, microsecond=0
            )
            if slot in busy:
                return False
        return True

    @staticmethod
    def _placement_flow_score(
        start: datetime,
        count: int,
        interval_min: int,
        minute_load: dict[datetime, int],
        *,
        target_load: float,
        window_start: datetime,
        window_end: datetime,
    ) -> tuple[float, int, int, int, float]:
        """Lower is better: target deviation, peak, empties, overflow, earlier."""
        slots = [
            (start + timedelta(minutes=i * interval_min)).replace(
                second=0, microsecond=0
            )
            for i in range(count)
        ]
        max_after = 0
        empty_filled = 0
        deviation_delta = 0.0
        overflow = 0
        for slot in slots:
            cur = minute_load.get(slot, 0)
            if cur == 0:
                empty_filled += 1
            after = cur + 1
            max_after = max(max_after, after)
            deviation_delta += (after - target_load) ** 2 - (
                cur - target_load
            ) ** 2
            if slot < window_start or slot > window_end:
                overflow += 1
        return (
            deviation_delta,
            max_after,
            -empty_filled,
            overflow,
            float(SchedulerService._minute_index(start)),
        )

