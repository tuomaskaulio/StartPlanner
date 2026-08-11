# Changelog

## 0.9.3

- Ruudukon viimeinen sarake ei enää veny muita ratasarakkeita leveämmäksi — kaikki ratasarakkeet ovat nyt samanlevyisiä
- Ruudukkoon lisätty värit: sarakkeen tausta on sama kaikilla samalla 1. rastilla alkavilla radoilla (helpottaa lähtökonfliktien havaitsemista), ja jokaisella sarjalla on oma, koko ruudukon läpi identtinen, vaalea soluväri

## 0.9.2

- Korjattu bugi, jossa ratatietojen tuonti nollasi kilpailun asetukset (aloitusaika, oletuslähtöväli, sarjaväli), nimen ja päivämäärän oletusarvoihin — tuonti yhdistetään nyt aina olemassa olevaan kilpailuun, ei koskaan luo uutta tyhjää kilpailua tuonnin yhteydessä
- Aloitus-välilehdelle uusi "Luo uusi kilpailu…" -painike; toisin kuin muut Aloitus-sivun painikkeet, se on aina käytettävissä
- "Kilpailun asetukset…" siirretty Muokkaa-valikosta Kilpailu-valikkoon

## 0.9.1

- Uusi "Kilpailu"-päävalikko kokoaa tuontitoiminnot (ratatiedot, ilmoittautumiset, jälki-ilmoittautuneet), jotka olivat aiemmin Tiedosto-valikossa
- Ennen kuin kilpailu on luotu ("Uusi") tai avattu ("Avaa .spc…"), Aloitus-sivun tuontipainikkeet sekä "Kilpailu"- ja "Lähtökaavio"-valikot (mm. "Lisää lähtö…") pysyvät ei-käytettävissä
- Yläpalkin aktiivinen lähtö -alasvetovalikko piilotetaan Aloitus-näkymässä, koska se ei ole merkityksellinen ennen kuin lähtökaavio on käytettävissä

## 0.9.0

- Uusi "Aloitus"-välilehti ohjaa uuden kilpailun perustamisen: ratatietojen tuonti, ilmoittautumisten tuonti ja lähtökaavion toteutus samalta sivulta
- Muut välilehdet piilotetaan kunnes sekä ratatiedot että ilmoittautumiset on tuotu; sääntö perustuu kilpailun tietoihin ja koskee yhtä lailla uutta kuin avattua projektia — jos data myöhemmin tyhjenee (esim. "Poista kaikki radat ja sarjat"), sovellus palaa Aloitukseen
- Poistettu vanha kysymysketju uuden kilpailun jälkeen ("tuodaanko ratatiedot nyt?" / "tuodaanko ilmoittautumiset nyt?" / "muodostetaanko kaavio automaattisesti?") ja siihen liittynyt valintaruutu — Aloitus-välilehden painikkeet korvaavat sen

## 0.8.7

- Kilpailijat-välilehdellä voi nyt poistaa yksittäisen kilpailijan (oikea klikkaus → "Poista valittu")
- Radat- ja Sarjat-välilehdillä voi poistaa yksittäisen radan tai sarjan oikealla klikkauksella; poisto pyyhkii kaskadina myös radan/sarjan kilpailijat, lähtökaavion rivit sekä rata↔sarja-tuontikytkennät, jotta projektiin ei jää orpoja viittauksia
- Uusi "Poista kaikki radat ja sarjat" -painike Radat-välilehdellä tyhjentää koko rata- ja sarjarakenteen kerralla (kuten "Poista kaikki kilpailijat")

## 0.8.6

- "Siirrä sarja" -dialogi yksinkertaistettu takaisin pelkäksi kellonajaksi; täyden päivämäärävalitsimen sijaan on nyt valintaruutu "Siirrä seuraavalle vuorokaudelle (+1 pv)" harvinaista vuorokauden ylitystä varten
- `Competition.clear_competitors()` ei enää nollaa sarjojen tai lähtöaikojen lukituksia — lukitukset säilyvät "Poista kaikki kilpailijat" -toiminnon yli. Mahdollinen vuorokauden ylitys näkyy silti "(+1 pv)" -merkintänä ja `plan.next_day`-varoituksena Huomiot-välilehdellä

## 0.8.5

- README päivitetty: versiotiedot ajan tasalle, maininta tekoälyavusteisesta kehityksestä ja käytöstä omalla vastuulla

## 0.8.4

- Aktiivisen lähdön vaihto ei enää tyhjennä koko kumoa/tee uudelleen -historiaa; kumoushistoria on nyt lähtökohtainen
- Projektin tallennus (`.spc`) on atominen: kirjoitus tehdään väliaikaistiedostoon ja vaihdetaan lopulliseksi vasta onnistumisen jälkeen, joten kesken jäänyt tallennus ei enää tuhoa vanhaa projektitiedostoa
- "Siirrä sarja" -dialogissa voi nyt valita myös päivämäärän, joten sarjan voi siirtää seuraavalle vuorokaudelle
- Condes-tuonnissa desimaaliluku-tokenit (esim. rataetäisyys "3.2") eivät enää päädy virheellisesti sarjatunnisteeksi

## 0.8.3

- Korjattu virhe, jossa lukittu sarja säilytti vanhan lähtöaika-ankkurinsa mutta varasi paikat uuden, elävän kilpailijamäärän mukaan — tämä saattoi työntää radan seuraavat sarjat seuraavalle vuorokaudelle "Poista kaikki kilpailijat" + uuden ilmoittautumislistan tuonnin jälkeen
- `Competition.clear_competitors()` nollaa nyt myös lähtökaavion ja sarjojen lukitukset, koska vanha lukittu kellonaika ei ole enää luotettava koko roolituksen pyyhkimisen jälkeen

## 0.8.2

- Lähtöaika, joka siirtyy kilpailupäivästä seuraavalle vuorokaudelle, näytetään merkinnällä "(+1 pv)" lähtökaaviossa, aikajanalla, ruudukossa sekä Excel/CSV/PDF-vienneissä (ennen näytettiin vain "HH:MM" ja vuorokausi hävisi näkyvistä)
- Validointi varoittaa, kun sarjan lähtöaika osuu eri vuorokaudelle kuin kilpailupäivä (`plan.next_day`)

## 0.8.1

- Kilpailusta voi poistaa kaikki kilpailijat (painike "Poista kaikki kilpailijat" Kilpailijat-välilehdellä)

## 0.8.0

- Sarjalle voi määrittää tyhjien lähtöaikojen määrän ennen sarjaa (`empty_slots_before`). Oletus 0. Sarjan ja edellisen radan sarjan väliin jätetään `sarjaväli + tyhjät × lähtöväli` minuuttia. Jos sarja on radan ensimmäinen, se alkaa `tyhjät × lähtöväli` minuuttia lähdön aloituksen jälkeen.

## 0.7.3

- Kiinnitetty macOS-käynnistysongelma Intel-koneilla: PyInstallerin pakkaamat `.so`/`.dylib`-tiedostot sisältävät vanhentuneita adhoc-allekirjoituksia, jotka macOS hylkää ("library load disallowed by system policy"). Build allekirjoittaa nyt kaikki bundlatut binäärit uudelleen adhoc-allekirjoituksella.

## 0.7.2

- Kiinnitetty Gatekeeper-ongelma: poistetaan UPX-pakkaus ja quarantaine-attribuutit macOS-buildistä

## 0.7.1

- GitHub Releases -paketointi: macOS-versio julkaistaan sekä Apple Silicon (ARM) että Intel (x86-64) -arkkitehtuureille

## 0.7.0

- Uuden kilpailun luominen: dialogi kysyy kaikki tarvittavat tiedot (nimi, päivämäärä, lähtöväli, sarjojen väli, aloitusaika) yhdellä kerralla
- Uuden kilpailun jälkeen ohjelman ehdottaa automaattisesti ratatietojen ja ilmoittautumisten tuomista
- Lähtökaavion automaattinen ehdotus tuonnin jälkeen, kun kaikki tiedot ovat valmiita
- Käyttäjäohjeeseen lisätty osio valmista paketista (GitHub Releases)

## 0.6.0

- PDF-vienti (kansilehti + lähtökaavio per lähtö, sarjajärjestyksessä)
- Ruudukko-PDF (maisema-A4, aktiivinen lähtö)
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
