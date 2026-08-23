# StartPlanner

Avoimen lähdekoodin työpöytäsovellus suunnistuskilpailujen lähtökaavioiden suunnitteluun.

> **Huomioitavaa:** Ohjelma on kehitetty pääosin tekoälyn (Claude) avulla. Käyttö on omalla vastuulla — ohjelmalle ei anneta mitään takuita toimivuudesta tai virheettömyydestä, eikä sen tuottamia lähtökaavioita tule käyttää tarkistamatta niitä ennen kilpailua.

## Lataa sovellus

Uusin valmis versio ladataan täältä: **[github.com/tuomaskaulio/StartPlanner/releases/latest](https://github.com/tuomaskaulio/StartPlanner/releases/latest)**

Avaa linkki, vieritä sivun alaosaan kohtaan **Assets** ja lataa oman käyttöjärjestelmäsi mukainen tiedosto:

| Käyttöjärjestelmä | Ladattava tiedosto |
| --- | --- |
| Windows | `StartPlanner-Windows.zip` |
| Mac (uudemmat, Apple Silicon / M-sarja) | `StartPlanner-macOS-ARM.zip` |
| Mac (vanhemmat, Intel) | `StartPlanner-macOS-Intel.zip` |

Pura ladattu zip-tiedosto ja käynnistä sovellus (Windowsissa `StartPlanner.exe`, Macissa `StartPlanner.app`). Sovellusta ei ole allekirjoitettu, joten käyttöjärjestelmä voi varoittaa tuntemattomasta kehittäjästä — ks. huomautus alla kohdassa [Asennuspaketit](#asennuspaketit).

Alla olevat asennusohjeet (Python, `pip install`) ovat vaihtoehto niille, jotka haluavat ajaa sovelluksen lähdekoodista.

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

Tuloste: `dist/StartPlanner/` (Windows) ja `dist/StartPlanner.app` (macOS, sis. Dock/Finder-ikonin). macOS voi varoittaa allekirjoittamattomasta sovelluksesta (Gatekeeper) — salli järjestelmäasetuksista tarvittaessa. Vastaavasti Windows Defender SmartScreen voi varoittaa tuntemattomasta julkaisijasta — valitse "Lisätietoja" → "Suorita silti".

Valmiiksi rakennetut paketit löytyvät lataamatta koodia [GitHub Releasesista](https://github.com/tuomaskaulio/StartPlanner/releases/latest), macOS sekä Apple Silicon (ARM) että Intel (x86-64) -arkkitehtuureille.


## Testit

```bash
pytest
```

## Versio

Nykyinen versio: **0.9.6**. Versiohistoria ja muutokset: [CHANGELOG.md](CHANGELOG.md). Kaikki julkaistut versiot ja lataukset: [GitHub Releases](https://github.com/tuomaskaulio/StartPlanner/releases).
