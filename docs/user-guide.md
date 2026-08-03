# StartPlanner – käyttäjäohje

Versio 0.7. Uusi kilpailu -velho, PDF-vienti ja käyttäjäohje.

## Käynnistys

```bash
pip install -e ".[dev]"
startplanner
```

## Valmiit paketit (ilman kääntämistä)

Voit ladata valmiit asennuspaketit (macOS + Windows) GitHub Releases -sivulta:

https://github.com/tuomaskaulio/StartPlanner/releases

Pakkaukset eivät vaadi Pythonia tai kääntämistä — pakkaa zip-arkisto ja aja suoraan.

macOS-paketit ovat saatavilla kahdessa arkkitehtuurissa:
- **Apple Silicon (ARM)** — `StartPlanner-macOS-ARM.zip`
- **Intel (x86-64)** — `StartPlanner-macOS-Intel.zip`

Valitse oma prosessorisi mukaan tuleva paketti.

### macOS-käynnistys

Koska sovellus ei ole allekirjoitettu Apple Developer -sertifikaatilla, macOS saattaa estää
sen käynnistyksen ("developer cannot be verified"). Tämän voi ohittaa kahdella tavalla:

**Vaihtoehto 1: Käynnistä launcher-skriptillä (suositeltu)**

Pura zip-arkisto ja käynnistä sovellus `launch_macos.sh`-skriptillä:

```bash
cd StartPlanner
./launch_macos.sh
```

Skripti poistaa automaattisesti macOS:n latausattribuutin (quarantine), joka estää
allekirjoittamattomien binäärien käynnistyksen.

**Vaihtoehto 2: Poista quarantine manuaalisesti**

```bash
xattr -rd com.apple.quarantine StartPlanner/
./StartPlanner/StartPlanner
```

Paikallinen PyInstaller-build: ks. [README](../README.md#asennuspaketit).


## Tyypillinen työnkulku

1. **Uusi kilpailu** – ohjattu velho kysyy peräkkäin:
   - kilpailun tiedot (nimi, aloitusaika, lähtöväli, sarjaväli)
   - ratatiedot (Condes XML)
   - ilmoittautumiset (IRMA Pirilä CSV)
   Jokainen vaihe on valinnainen – voit painaa **Peruuta** milloin tahansa.
2. **Sarjat** – kytke puuttuvat sarjat radoihin; säädä lähtö ja lähtöväli.
3. **Sarjajärjestys** – raahaa sarjoja haluttuun järjestykseen (näkyy kaaviossa).
4. **Lähdöt** – nimeä lähdöt; tarvittaessa aseta lähdön oma 1. lähtöaika.
5. **Kilpailun asetukset** – kilpailun nimi, oletusväli, sarjaväli, kilpailun aloitusaika.
6. **Muodosta lähtökaavio** (aktiivinen lähtö). Tarkista **Huomiot**, aikajana ja ruudukko.
7. **Jälki-ilmoittautuneet** – tuo uusi IRMA-CSV ja päivitä kaavio (olemassa olevat ajat säilyvät).
8. **Vie** Excel / CSV / PDF / Ruudukko PDF. **Tallenna** projekti `.spc`-tiedostoon.

## Tuontiformaatit

| Toiminto | Muoto |
|----------|--------|
| Ratatiedot | IOF XML CourseData 3.0 (Condes-export) |
| Ilmoittautumiset / jälki-ilmot | IRMA Pirilä, `= ILMOIT` CSV |

## Näkymät

- **Lähdöt** – nimet, 1. lähtöaika (tai kilpailun oletus), sarjojen määrä
- **Sarjat** – rata, lähtö, lähtöväli, järjestysnumero
- **Sarjajärjestys** – drag & drop näyttöjärjestys (Lähtökaavio / Excel)
- **Ratajärjestys** – drag & drop: missä järjestyksessä saman radan sarjat lähtevät
- **Lähtökaavio** – näyttö *Sarjajärjestys* tai *Aika*
- **Ruudukko** – minuutti × rata
- **Huomiot** – validointiviestit (Virhe / Varoitus / Huomautus)

## Vienti

- **Excel** – Lähtökaavio (sarjajärjestyksessä), Yhteenveto (laatupisteet), Ruudukko per lähtö
- **CSV** – sama kaaviosisältö kuin Excelin Lähtökaavio
- **PDF** – kansilehti + kaavio per lähtö (tulosta PDF-ohjelmalla)
- **Ruudukko PDF** – maisema-A4, aktiivisen lähdön minuutti × rata -ruudukko

## Vinkkejä

- Lukitse sarja kaaviosta, jos aika ei saa muuttua optimoinnissa tai päivityksessä.
- Radan **Sarjaväli** Radat-välilehdellä yliajaa kilpailun oletussarjavälin.
- Kumoa / Tee uudelleen koskee aktiivisen lähdön kaaviota.
