# StartPlanner – käyttäjäohje

Versio 0.9. Ohjattu Aloitus-välilehti uuden kilpailun perustamiseen, PDF-vienti ja käyttäjäohje.

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

1. **Uusi kilpailu** (Tiedosto-valikko) – dialogi kysyy kilpailun tiedot
   (nimi, aloitusaika, lähtöväli, sarjaväli) kerralla. Sovellus avautuu
   **Aloitus**-välilehdelle. Ennen kuin kilpailu on luotu tai avattu
   (**Avaa .spc…**), Aloitus-sivun tuontipainikkeet sekä **Kilpailu**- ja
   **Lähtökaavio**-valikot pysyvät ei-käytettävissä.
2. **Aloitus** – ohjaa perustamisen kahdella painikkeella:
   - **Lataa ratatiedot…** (Condes XML)
   - **Lataa ilmoittautumiset…** (IRMA Pirilä CSV)
   Muut välilehdet (Sarjat, Lähdöt, Lähtökaavio, jne.) sekä yläpalkin
   aktiivinen lähtö -valikko pysyvät piilossa kunnes molemmat on ladattu —
   sama sääntö koskee myös vanhan `.spc`-projektin avaamista, jos siitä
   puuttuu vielä ratatiedot tai ilmoittautumiset. Kun molemmat on ladattu,
   Aloitukseen ilmestyy kolmas painike, **Toteuta lähtökaavio**, ja kaikki
   muut välilehdet avautuvat.
3. **Sarjat** – kytke puuttuvat sarjat radoihin; säädä lähtö ja lähtöväli.
   Sarjan (ja sen kilpailijat) voi poistaa oikealla klikkauksella.
4. **Sarjajärjestys** – raahaa sarjoja haluttuun järjestykseen (näkyy kaaviossa).
5. **Radat** – rataväli näkyy täällä; radan (ja sen sarjat) voi poistaa oikealla
   klikkauksella, tai kaikki radat ja sarjat kerralla "Poista kaikki radat ja
   sarjat" -painikkeella.
6. **Lähdöt** – nimeä lähdöt; tarvittaessa aseta lähdön oma 1. lähtöaika.
7. **Kilpailun asetukset** – kilpailun nimi, oletusväli, sarjaväli, kilpailun aloitusaika.
8. **Muodosta lähtökaavio** (aktiivinen lähtö). Tarkista **Huomiot**, aikajana ja ruudukko.
9. **Jälki-ilmoittautuneet** – tuo uusi IRMA-CSV ja päivitä kaavio (olemassa olevat ajat säilyvät).
   Yksittäisen kilpailijan voi poistaa Kilpailijat-välilehdellä oikealla klikkauksella.
10. **Vie** Excel / CSV / PDF / Ruudukko PDF. **Tallenna** projekti `.spc`-tiedostoon.

## Tuontiformaatit

| Toiminto | Muoto |
|----------|--------|
| Ratatiedot | IOF XML CourseData 3.0 (Condes-export) |
| Ilmoittautumiset / jälki-ilmot | IRMA Pirilä, `= ILMOIT` CSV |

## Näkymät

- **Lähdöt** – nimet, 1. lähtöaika (tai kilpailun oletus), sarjojen määrä
- **Sarjat** – rata, lähtö, lähtöväli, tyhjät lähtöajat, järjestysnumero
- **Sarjajärjestys** – drag & drop näyttöjärjestys (Lähtökaavio / Excel)
- **Ratajärjestys** – drag & drop: missä järjestyksessä saman radan sarjat lähtevät
- **Lähtökaavio** – näyttö *Sarjajärjestys* tai *Aika*
- **Ruudukko** – minuutti × rata
- **Huomiot** – validointiviestit (Virhe / Varoitus / Huomautus)

## Tyhjät lähtöajat sarjan edellä

**Sarjat**-välilehdellä voi määrittää jokaiselle sarjalle **Tyhjiä ennen** -arvon
(0–30). Se kertoo, montako tyhjää lähtöaikaa jätetään sarjan eteen samalla radalla.

- **Oletus on 0**, jolloin sarjat seuraavat toisiaan normaalisti sarjavälin
  (oletus 2 min) jälkeen.
- **Arvo 1** tarkoittaa yhtä tyhjää lähtöaikaa. Jos sarjan lähtöväli on 2 minuuttia,
  edellisen sarjan viimeisen lähdön ja tämän sarjan ensimmäisen lähdön väliin jää
  `sarjaväli (2) + 1 × lähtöväli (2) = 4 minuuttia` (esim. 11:24 → 11:28).
- **Arvo 2** tarkoittaa kahta tyhjää lähtöaikaa → `2 + 2 × 2 = 6 minuuttia` (11:24 → 11:30).
- Jos sarja on radan **ensimmäinen**, tyhjät ajat siirtävät sen alkua:
  `tyhjät × lähtöväli` minuuttia lähdön aloituksen jälkeen.

## Vienti

- **Excel** – Lähtökaavio (sarjajärjestyksessä), Yhteenveto (laatupisteet), Ruudukko per lähtö
- **CSV** – sama kaaviosisältö kuin Excelin Lähtökaavio
- **PDF** – kansilehti + kaavio per lähtö (tulosta PDF-ohjelmalla)
- **Ruudukko PDF** – maisema-A4, aktiivisen lähdön minuutti × rata -ruudukko

## Vinkkejä

- Lukitse sarja kaaviosta, jos aika ei saa muuttua optimoinnissa tai päivityksessä.
  Lukitus säilyy myös kilpailijoiden poiston yli — jos kilpailijamäärän kasvu
  työntää myöhemmät sarjat seuraavalle vuorokaudelle, se näkyy "(+1 pv)"
  -merkintänä ja varoituksena Huomiot-välilehdellä.
- Radan **Sarjaväli** Radat-välilehdellä yliajaa kilpailun oletussarjavälin.
- Kumoa / Tee uudelleen koskee aktiivisen lähdön kaaviota.
