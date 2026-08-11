# StartPlanner

Avoimen lähdekoodin työpöytäsovellus suunnistuskilpailujen lähtökaavioiden suunnitteluun.

> **Huomioitavaa:** Ohjelma on kehitetty pääosin tekoälyn (Claude) avulla. Käyttö on omalla vastuulla — ohjelmalle ei anneta mitään takuita toimivuudesta tai virheettömyydestä, eikä sen tuottamia lähtökaavioita tule käyttää tarkistamatta niitä ennen kilpailua.

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

## Tyypillinen työnkulku

1. Tuo ratatiedot (IOF CourseData 3.0, Condes) – useita XML:iä kerralla ok
2. Tuo ilmoittautumiset (IRMA Pirilä)
3. Kytke sarjat radoihin; säädä lähtö, väli ja Sarjajärjestys
4. Kilpailun asetukset (nimi, ajat); tarvittaessa radan sarjaväli
5. Lähdöt + muodosta lähtökaavio
6. Tuo jälki-ilmoittautuneet ja päivitä kaavio tarvittaessa
7. Tarkista Huomiot / aikajana / ruudukko; optimoi tai lukitse
8. Vie Excel / CSV / PDF
9. Tallenna `.spc`

Esimerkkiaineistot: `samples/sample-small/`, `samples/sample-medium/` ja `samples/sample-medium-large/`.

## Asennuspaketit

Paikallinen PyInstaller-build (ei notarizationia / allekirjoitusta):

```bash
pip install -e ".[packaging]"
# macOS:
./packaging/build_macos.sh
# Windows (PowerShell):
./packaging/build_windows.ps1
```

Tuloste: `dist/StartPlanner/` (Windows) ja `dist/StartPlanner.app` (macOS, sis. Dock/Finder-ikonin). macOS voi varoittaa allekirjoittamattomasta sovelluksesta (Gatekeeper) — salli järjestelmäasetuksista tarvittaessa. GitHub Releases -paketeissa macOS on saatavilla sekä Apple Silicon (ARM) että Intel (x86-64) -arkkitehtuureille.


## Testit

```bash
pytest
```

## Versio

Nykyinen versio: **0.9.5**. Versiohistoria ja muutokset: [CHANGELOG.md](CHANGELOG.md).
