# StartPlanner

Avoimen lähdekoodin työpöytäsovellus suunnistuskilpailujen lähtökaavioiden suunnitteluun.

## Vaatimukset

- Python ≥ 3.12
- macOS / Windows / Linux

## Asennus

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Käynnistys

```bash
startplanner
# tai
python -m startplanner.main
```

## Tyypillinen työnkulku (v0.2)

1. Tuo IOF CourseData (Condes-export)
2. Tuo IRMA-ilmoittautumiset (`= ILMOIT` CSV)
3. Muodosta lähtökaavio
4. Tarkista issues-lista
5. Vie Exceliin / CSV:hen
6. Tallenna projekti `.spc`-tiedostoon

Esimerkkiaineistot (anonymisoidut): `samples/sample-small/` ja `samples/sample-medium/`.

## Testit

```bash
pytest
```

## Versio

Nykyinen kehitysversio: **0.2.0** (ensimmäinen käyttökelpoinen).
