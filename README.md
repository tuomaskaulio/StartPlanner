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

## Tyypillinen työnkulku (v0.4)

1. Tuo IOF CourseData (Condes-export)
2. Tuo IRMA-ilmoittautumiset (`= ILMOIT` CSV)
3. Säädä kilpailun asetukset tarvittaessa
4. Valitse / lisää lähtö, muodosta lähtökaavio (sarjojen 1. ajat)
5. Tarkista laatu, aikajana ja issues; optimoi tai siirrä/lukitse sarjoja
6. Vie Exceliin / CSV:hen
7. Tallenna projekti `.spc`-tiedostoon

Esimerkkiaineistot (anonymisoidut): `samples/sample-small/` ja `samples/sample-medium/`.

## Testit

```bash
pytest
```

## Versio

Nykyinen kehitysversio: **0.4.0** (laatu, optimointi, undo/redo, aikajana).
