"""In-memory undo/redo for ClassStartPlan snapshots."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from startplanner.domain import ClassStartPlan


@dataclass
class PlanSnapshot:
    description: str
    plan: ClassStartPlan | None


class HistoryService:
    def __init__(self, *, limit: int = 50) -> None:
        self._limit = limit
        self._undo: list[PlanSnapshot] = []
        self._redo: list[PlanSnapshot] = []

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def push(self, description: str, plan: ClassStartPlan | None) -> None:
        self._undo.append(PlanSnapshot(description, deepcopy(plan) if plan else None))
        if len(self._undo) > self._limit:
            self._undo.pop(0)
        self._redo.clear()

    def can_undo(self) -> bool:
        return len(self._undo) > 1

    def can_redo(self) -> bool:
        return bool(self._redo)

    def undo(self) -> PlanSnapshot | None:
        if not self.can_undo():
            return None
        current = self._undo.pop()
        self._redo.append(current)
        return deepcopy(self._undo[-1])

    def redo(self) -> PlanSnapshot | None:
        if not self.can_redo():
            return None
        snap = self._redo.pop()
        self._undo.append(snap)
        return deepcopy(snap)
