"""Shared exceptions."""


class StartPlannerError(Exception):
    """Base error."""


class ImportError_(StartPlannerError):
    """Import failed (named ImportError_ to avoid shadowing builtins)."""


class ValidationError(StartPlannerError):
    """Validation failed hard."""


class ScheduleError(StartPlannerError):
    """Scheduling failed."""


class PersistenceError(StartPlannerError):
    """Project save/load failed."""
