"""Competition lifecycle helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from startplanner.domain import Competition, Settings
from startplanner.persistence.spc_store import SpcStore


class CompetitionService:
    def __init__(self) -> None:
        self._store = SpcStore()

    def new_competition(
        self,
        name: str = "Uusi kilpailu",
        event_date: date | None = None,
        settings: Settings | None = None,
    ) -> Competition:
        competition = Competition(
            name=name,
            event_date=event_date,
            settings=settings or Settings(),
        )
        competition.ensure_default_start_location()
        return competition

    def save(self, competition: Competition, path: str | Path) -> None:
        self._store.save(competition, path)

    def load(self, path: str | Path) -> Competition:
        return self._store.load(path)

    def clear_competitors(self, competition: Competition) -> int:
        """Remove all competitors from the competition.

        Returns the number of competitors removed.
        """
        return competition.clear_competitors()
