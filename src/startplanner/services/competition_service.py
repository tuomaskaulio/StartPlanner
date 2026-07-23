"""Competition lifecycle helpers."""

from __future__ import annotations

from pathlib import Path

from startplanner.domain import Competition
from startplanner.persistence.spc_store import SpcStore


class CompetitionService:
    def __init__(self) -> None:
        self._store = SpcStore()

    def new_competition(self, name: str = "Uusi kilpailu") -> Competition:
        competition = Competition(name=name)
        competition.ensure_default_start_location()
        return competition


    def save(self, competition: Competition, path: str | Path) -> None:
        self._store.save(competition, path)

    def load(self, path: str | Path) -> Competition:
        return self._store.load(path)
