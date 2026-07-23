"""Validation issues and rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"


@dataclass(frozen=True)
class Issue:
    rule_id: str
    severity: Severity
    message: str
    target_type: str | None = None
    target_id: str | None = None


@dataclass
class ValidationReport:
    issues: list[Issue]

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity is Severity.WARNING]

    @property
    def notes(self) -> list[Issue]:
        return [i for i in self.issues if i.severity is Severity.NOTE]

    @property
    def ok(self) -> bool:
        return not self.errors
