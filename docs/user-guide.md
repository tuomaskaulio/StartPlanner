# StartPlanner – käyttäjäohje

Versio 0.6. Suunnistuskilpailun **lähtökaavion** (sarjojen ensimmäiset lähtöajat lähdöittäin) suunnittelu.

## Käynnistys

```bash
pip install -e ".[dev]"
startplanner
```

Asennuspaketin (macOS/Windows) rakentaminen: ks. [README](../README.md#asennuspaketit).

## Tyypillinen työnkulku

1. **Tuo ratatiedot** – IOF CourseData 3.0 XML (Condes). Voit valita useita XML-tiedostoja kerralla.
2. **Tuo ilmoittautumiset** – IRMA Pirilä `= ILMOIT` CSV.
3. **Sarjat** – kytke puuttuvat sarjat radoihin; säädä lähtö ja lähtöväli.
4. **Sarjajärjestys** – raahaa sarjoja haluttuun järjestykseen (näkyy kaaviossa).
5. **Lähdöt** – nimeä lähdöt; tarvittaessa aseta lähdön oma 1. lähtöaika.
6. **Kilpailun asetukset** – kilpailun nimi, oletusväli, sarjaväli, kilpailun aloitusaika.
7. **Muodosta lähtökaavio** (aktiivinen lähtö). Tarkista **Huomiot**, aikajana ja ruudukko.
8. **Jälki-ilmoittautuneet** – tuo uusi IRMA-CSV ja päivitä kaavio (olemassa olevat ajat säilyvät).
9. **Vie** Excel / CSV / PDF / Ruudukko PDF. **Tallenna** projekti `.spc`-tiedostoon.

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
