# Changelog

## 0.6.0

- PDF-vienti (kansilehti + lähtökaavio per lähtö, sarjajärjestyksessä)
- Excel/CSV: rivit sarjajärjestyksessä; Excelissä Ruudukko-välilehti per lähtö
- Usean CourseData-XML:n tuonti kerralla
- Kilpailun nimi kilpailun asetuksissa
- Selkeämmät tuontivalikot (IOF CourseData 3.0 / IRMA Pirilä)
- Käyttäjäohje (`docs/user-guide.md`)
- PyInstaller-skriptit macOS/Windows (`packaging/`)
- `course_grid` siirretty services-kerrokseen (vienti ei riipu GUI:sta)
- Ratajärjestys: erillinen `course_order` saman radan sarjoille (DnD + scheduler)

## 0.5.0

- Sarja ↔ rata -editori Sarjat-välilehdellä (puuttuvat korostettu)
- Sarjat: muokattava lähtö ja lähtöväli
- Sarjat: muokattava järjestys (`sort_order`); lista sort_orderin mukaan
- Sarjajärjestys-välilehti: drag&drop -järjestys (vain nimet)
- Lähtökaavio: Järjestys-sarake; näyttö Sarjajärjestys (oletus) tai Aika
- Lähdöt: yliajettava 1. lähtöaika (`StartLocation.first_start`)
- Radat: yliajettava sarjaväli (`Course.class_gap_min`)
- Lähdöt-välilehti (lista, nimeäminen, lisää lähtö)
- Jälki-ilmoittautuneet + lähtökaavion päivitys (olemassa olevat ajat säilyvät)
- Issues → Huomiot (vakavuudet suomeksi)
- `SchedulerService.update()` inkrementaaliseen kaavion päivitykseen
- Scheduler: eri radat voivat lähteä rinnakkain; sama 1. rasti max 1/min
- Tasaisempi kilpailijavirta: pitkät sarjat ensin, lyhyet täyttävät tyhjät minuutit
- Aikataulu rajattu pullonkaularadan kestoon (muut radat rinnakkain samassa ikkunassa)
- Jos ikkuna venyy, uusi maksimi on tasoituksen raja (tyhjät minuutit täytetään uudelleen)
- Automaattinen tavoitekuorma ja 2 min -sarjojen parillinen/pariton vaiheistus
- Ruudukko-näkymä: minuutti × rata, sarjan nimi solussa
- Varoitus `plan.window_overflow`, jos aikataulu ylittää pullonkaulan

## 0.4.0

- Laatupisteet (0–100) ja kevyt optimoija lähtökaaviolle
- Undo / Redo kaavion muutoksille
- Aikajanavälilehti; sarjan siirto ja lukitus kaaviosta
- Kilpailun asetukset (lähtöväli, sarjaväli, aloitusaika)
- Excel-vientiin Yhteenveto-välilehti laatupisteineen

## 0.3.0

- `StartLocation` ja lähdöittäinen `ClassStartPlan` (sarja + 1. lähtöaika)
- Scheduler ja validointi lähdöittäin (1. rasti -sääntö vain saman lähdön sisällä)
- GUI: lähtövalitsin + kaavionäkymä
- Excel/CSV-vienti kaaviona; `.spc` v2 (`start_locations`, `class_starts`)

## 0.2.0

- Domain-malli, validointi ja greedy-scheduler
- IOF CourseData- ja IRMA ILMOIT -tuonti
- Excel/CSV-vienti ja `.spc`-projektitiedosto
- Minimaalinen PySide6-käyttöliittymä
- Esimerkkiaineistot: anonymisoidut sample-small ja sample-medium

## 0.1.0

- Projektirunko
