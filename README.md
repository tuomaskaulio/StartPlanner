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

## Tyypillinen työnkulku (v0.5)

1. Tuo IOF CourseData (Condes-export)
2. Tuo IRMA-ilmoittautumiset (`= ILMOIT` CSV)
3. Kytke puuttuvat sarjat radoihin Sarjat-välilehdellä; säädä lähtö ja lähtöväli tarvittaessa
4. Säädä kilpailun asetukset ja tarvittaessa radan sarjaväli Radat-välilehdellä
5. Hallitse lähtöjä Lähdöt-välilehdellä; muodosta lähtökaavio
6. Tuo jälki-ilmoittautuneet ja päivitä kaavio tarvittaessa
7. Tarkista laatu, aikajana ja Huomiot; optimoi tai siirrä/lukitse sarjoja
8. Vie Exceliin / CSV:hen
9. Tallenna projekti `.spc`-tiedostoon

Esimerkkiaineistot (anonymisoidut): `samples/sample-small/` ja `samples/sample-medium/`.

## Testit

```bash
pytest
```

## Versio

Nykyinen kehitysversio: **0.5.0** (sarja/rata-yliajot, Lähdöt, Huomiot, tasapainotettu kaavio).
