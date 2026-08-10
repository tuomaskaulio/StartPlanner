"""'Siirrä sarja' -dialogin päivämäärälaskenta (v0.8.6).

Vuorokauden ylitys on käytännössä harvinaista, joten dialogi kysyy vain
kellonajan ja valinnaisen "+1 pv" -ruudun sen sijaan että käyttäjä valitsisi
täyden päivämäärän. Lopullinen päivä on aina kilpailun päivä (tai tämä
päivä, jos sitä ei ole asetettu) — ei koskaan rivin vanhasta raakapäivästä
johdettu.
"""

from __future__ import annotations

from datetime import date, time

from startplanner.gui.main_window import MainWindow


def test_resolve_move_datetime_same_day():
    result = MainWindow._resolve_move_datetime(time(9, 30), False, date(2026, 8, 15))
    assert result.date() == date(2026, 8, 15)
    assert (result.hour, result.minute) == (9, 30)


def test_resolve_move_datetime_next_day():
    result = MainWindow._resolve_move_datetime(time(0, 15), True, date(2026, 8, 15))
    assert result.date() == date(2026, 8, 16)
    assert (result.hour, result.minute) == (0, 15)


def test_resolve_move_datetime_ignores_original_date_entirely():
    """Even a same-day time far from midnight must resolve to the
    competition date, never to whatever raw date the caller happened to
    pass around — the date always comes from `event_date` + the checkbox."""
    result = MainWindow._resolve_move_datetime(time(23, 59), False, date(2026, 1, 1))
    assert result.date() == date(2026, 1, 1)
