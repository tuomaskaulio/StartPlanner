# Phased Load Balancing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tasaa minuuttikuorma automaattisen tavoitekuorman ympärille ja vaiheista pitkät kahden minuutin sarjat parillisille tai parittomille minuuteille.

**Architecture:** Scheduler laskee tavoitekuorman nykyisestä aikatauluikkunasta. Kelvolliset aloitusajat pisteytetään koko sarjan lähtövirran perusteella; 2 minuutin sarjoille arvioidaan molemmat vaihepariteetit. Jos ikkuna laajenee, lukitsemattomat muut radat tasataan uudelleen uuden tavoitekuorman avulla.

**Tech Stack:** Python 3.12+, dataclasses/domain model, pytest, Ruff.

## Global Constraints

- Sama syöte tuottaa aina saman kaavion.
- Sama rata ei lomitu saman lähtöpaikan sisällä.
- Sama ensimmäinen rasti enintään 1 kilpailija/min/lähtöpaikka.
- Lukitut sarjat ja ajat eivät muutu.
- Ei OR-Tools- tai muuta raskasta solver-riippuvuutta.

---

### Task 1: Tavoitekuorma ja vaiheistus

**Files:**
- Modify: `src/startplanner/services/scheduler_service.py`
- Test: `tests/test_flow.py`

**Interfaces:**
- Produces: `_target_load(total_starts: int, start: datetime, end: datetime) -> float`
- Produces: `_candidate_times(earliest: datetime, latest: datetime, interval_min: int, phased: bool) -> list[datetime]`

- [ ] Lisää testit, jotka varmistavat automaattisen tavoitekuorman ja 2 minuutin sarjojen molemmat vaihepariteetit.
- [ ] Aja kohdistetut testit ja varmista niiden epäonnistuvan.
- [ ] Lisää deterministiset apumetodit tavoitekuormalle ja kandidaattiajoille.
- [ ] Aja kohdistetut testit ja varmista niiden onnistuvan.

### Task 2: Tavoitekuormakustannus

**Files:**
- Modify: `src/startplanner/services/scheduler_service.py`
- Test: `tests/test_flow.py`

**Interfaces:**
- Consumes: `_target_load`, `_candidate_times`
- Produces: `_placement_flow_score(..., target_load: float, window_start: datetime, window_end: datetime) -> tuple`

- [ ] Lisää testi, jossa tasainen 2–3 lähtijää/min voittaa 0/5-kuorman.
- [ ] Korvaa tyhjäaukkoihin perustuva score neliöpoikkeamalla tavoitekuormasta, huippukuormalla, tyhjillä minuuteilla ja deterministisellä aika-tie-breakillä.
- [ ] Suodata 2 minuutin pitkien sarjojen kandidaatit vaiheittain ja valitse halvempi vaihe.
- [ ] Aja flow- ja rinnakkaisuustestit.

### Task 3: Laajennetun ikkunan uudelleentasoitus

**Files:**
- Modify: `src/startplanner/services/scheduler_service.py`
- Test: `tests/test_flow.py`

**Interfaces:**
- Consumes: lopullinen `fill_window`
- Produces: uudelleen tasattu `ClassStartPlan`

- [ ] Lisää regressiotesti, jossa alkuperäinen ikkuna ylittyy ja uusi maksimi täyttyy ilman harvaa loppuhäntää.
- [ ] Laske tavoitekuorma uudelleen jokaiselle uudelleentasoituskierrokselle lopullisen ikkunan ja kaikkien lähtijöiden perusteella.
- [ ] Säilytä pullonkaularata ja lukitut sarjat; sijoita muut radat uudelleen tavoitekuormakustannuksella.
- [ ] Varmista determinismi ajamalla sama build kahdesti ja vertaamalla aikoja.

### Task 4: Dokumentaatio ja verifiointi

**Files:**
- Modify: `docs/specification/03-scheduling.md`
- Modify: `CHANGELOG.md`

- [ ] Kuvaa automaattinen tavoitekuorma ja parillinen/pariton vaiheistus.
- [ ] Aja `python -m pytest -q`.
- [ ] Aja `python -m ruff check src/startplanner/services/scheduler_service.py tests/test_flow.py`.
- [ ] Tarkista medium-aineiston kesto, tyhjät minuutit, huippukuorma ja varianssi.

