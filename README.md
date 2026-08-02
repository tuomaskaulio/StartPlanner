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

## Käyttäjäohje

Katso [docs/user-guide.md](docs/user-guide.md).

## Tyypillinen työnkulku (v0.6)

1. Tuo ratatiedot (IOF CourseData 3.0, Condes) – useita XML:iä kerralla ok
2. Tuo ilmoittautumiset (IRMA Pirilä)
3. Kytke sarjat radoihin; säädä lähtö, väli ja Sarjajärjestys
4. Kilpailun asetukset (nimi, ajat); tarvittaessa radan sarjaväli
5. Lähdöt + muodosta lähtökaavio
6. Tuo jälki-ilmoittautuneet ja päivitä kaavio tarvittaessa
7. Tarkista Huomiot / aikajana / ruudukko; optimoi tai lukitse
8. Vie Excel / CSV / PDF
9. Tallenna `.spc`

Esimerkkiaineistot: `samples/sample-small/` ja `samples/sample-medium/`.

## Asennuspaketit

Paikallinen PyInstaller-build (ei notarizationia / allekirjoitusta):

```bash
pip install -e ".[packaging]"
# macOS:
./packaging/build_macos.sh
# Windows (PowerShell):
./packaging/build_windows.ps1
```

Tuloste: `dist/StartPlanner/`. macOS voi varoittaa allekirjoittamattomasta sovelluksesta (Gatekeeper) — salli järjestelmäasetuksista tarvittaessa. GitHub Releases -paketeissa macOS on saatavilla sekä Apple Silicon (ARM) että Intel (x86-64) -arkkitehtuureille.


## Testit

```bash
pytest
```

## Versio

Nykyinen kehitysversio: **0.6.0** (PDF, Excel-ruudukko, käyttäjäohje, paketoinnin alku).
