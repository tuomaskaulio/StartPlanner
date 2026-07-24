# 16 Tiekartta

## 16.1 Johdanto

Tiekartta kuvaa StartPlannerin kehityksen versiosta v0.1 versioon v2.0.

Versiot ovat tavoitteellisia. Yksittäisten ominaisuuksien järjestys voi tarkentua toteutuksen edetessä, mutta julkaisujen päämäärät pysyvät.

---

# 16.2 Periaatteet

- Jokainen versio on käytettävä omassa laajuudessaan.
- Ydin (Domain + Scheduler + Validation) vakautetaan ensin.
- GUI ja integraatiot rakennetaan ytimen päälle.
- Tuotantoon (v1.0) ei mennä ilman kattavia testejä ja oikeaa kilpailuaineistoa.
- v2.0 laajentaa kilpailumuotoja ja integraatioita rikkomatta v1-projekteja.

---

# 16.3 v0.1 – Perusta

**Tavoite:** ohjelman runko ja tietomalli.

Sisältää:

- kilpailun Domain-malli
- projektirakenne
- Condes-tuonnin ensimmäinen versio
- Data Explorer / perusnäkymä tietoihin
- kehitysympäristö, linttaus ja CI-runko

Ei vielä automaattista lähtökaaviota.

---

# 16.4 v0.2 – Ensimmäinen käyttökelpoinen versio

**Tavoite:** tuonti + automaattinen ehdotus oikealla aineistolla.

Sisältää:

- IOF CourseData (Condes) -tuonti, myös usean XML:n merge ja nimeen perustuva sarja↔rata
- IRMA `= ILMOIT` -ilmoittautumisraportin tuonti
- SchedulerService:n greedy-algoritmi (deterministinen)
- lähtövälien ja ensimmäisen rastin perussäännöt
- perusvalidointi + issues-lista GUI:ssa
- Excel- ja CSV-vienti
- `.spc` tallenna/avaa
- esimerkkiaineistot: anonymisoidut sample-small + sample-medium

**Drift speksiin nähden:** v0.2 tuottaa vielä kilpailijakohtaisen listan (`StartSchedule`) yhdelle implisiittiselle lähdölle. Speksin mukainen ydin (`ClassStartPlan` + `StartLocation`) tulee v0.3:ssa.

---

# 16.5 v0.3 – Lähdöt ja lähtökaavio ytimenä

**Tavoite:** speksin mukainen domain ja UI.

Sisältää:

- `StartLocation` (useita lähtöjä)
- sarja → lähtö -kytkentä
- `ClassStartPlan` Schedulerin tuloksena (sarja + 1. lähtöaika)
- suunnittelu ja validointi **lähdöittäin** (1. rasti -sääntö vain saman lähdön sisällä)
- GUI: lähtövalitsin + kaavionäkymä (ei kilpailijalistaa ytimessä)
- Excel/CSV-vienti kaaviona
- lukitukset (sarja / aikajakso) ja perushistoria

---

# 16.6 v0.4 – Optimointi ja UI-viimeistely

**Tavoite:** päivittäiseen kilpailutyöhön sopiva hiominen.

**Tila:** toteutettu sovelluksessa **0.4.0** (PDF-vienti ja käyttäjäkohtaiset asetukset jäävät myöhempään hiomiseen).

Sisältää:

- optimointimoottori / laatupisteet
- aikajananäkymä
- Undo / Redo
- viennin viimeistely (Excel-yhteenveto; PDF myöhemmin)
- asetukset (kilpailu; käyttäjäasetukset myöhemmin)
- `.spc` tuotantokelpoisena migraatioineen

---

# 16.6.1 v0.5 – Kilpailukäyttö

**Tavoite:** päivittäiset aukot ennen v1.0:aa.

**Tila:** toteutettu sovelluksessa **0.5.0**.

Sisältää:

- manuaalinen sarja ↔ rata -kytkentä (AM-aukot tms.)
- jälki-ilmoittautumiset ja kaavion päivitys lukitukset / ajat säilyttäen
- `SchedulerService.update()` olemassa olevien aikojen säilytykseen
- rinnakkaiset radat (sama 1. rasti max 1/min), pullonkaulaikkuna, tavoitekuorma
- Ruudukko-näkymä; Lähdöt-välilehti; lähdön/radan/sarjan yliajot
- Sarjajärjestys (spinbox + DnD-välilehti); Huomiot-suomennos

---

# 16.6.2 v0.6 – Vienti, ohje ja paketoinnin alku

**Tavoite:** järjestäjän paperi ja asennettavuus kohti v1.0:aa.

**Tila:** toteutettu sovelluksessa **0.6.0**.

Sisältää:

- PDF-vienti (tulostus PDF-ohjelmalla)
- Excel-ruudukkovälilehti; kaavio viennissä sarjajärjestyksessä
- usean CourseData-tiedoston tuonti; kilpailun nimi asetuksissa
- käyttäjäohjeen perusversio
- PyInstaller-skriptit macOS/Windows (ei vielä notarization / MSI)

Vielä auki ennen v1.0: issue-korjausehdotukset, käyttäjäasetukset, plugin-rajapinta, Large-suorituskyky, hyväksyntä oikealla kilpailulla.

---

# 16.7 v1.0 – Tuotantoversio

**Tavoite:** ensimmäinen vakaa julkaisu kansallisiin kilpailuihin.

Sisältää:

- dokumentoidut import/export-pluginit
- täysi validointi lajisääntöineen
- suorituskykytavoitteet Large-aineistolla
- regressiotestit ja hyväksymistestaus oikealla kilpailulla
- asennuspaketit (Windows, macOS, Linux) – allekirjoitus/notarize
- käyttäjäohjeen täydennys

v1.0:n jälkeen `.spc`-muodon yhteensopivuus säilytetään.

---

# 16.8 v1.x – Vakiinnuttaminen

**Tavoite:** palaute, bugikorjaukset ja pienet parannukset.

Esimerkkejä:

- lisää vientipohjia
- parempi korjausehdotus-UI
- esimerkkikilpailukirjaston laajennus
- suorituskykyparannukset
- lokalisoinnin täydennys
- ulkoisten pluginien kokeellinen tuki

Ei riko v1.0-projektitiedostoja.

---

# 16.9 v2.0 – Laajennukset

**Tavoite:** uudet kilpailumuodot ja integraatiot.

Sisältää tai valmistautuu sisältämään:

- viestikilpailut
- sprinttikilpailut / tiheämpi lähtötahti
- useita lähtöpaikkoja
- useita lähtökaavioversioita samassa projektissa
- vahvempi plugin-ekosysteemi
- REST API (valinnainen)
- pilvitallennuksen ensimmäinen malli (valinnainen)

v2.0 voi vaatia projektiversion noston, mutta vanhat projektit avataan migraatiolla.

---

# 16.10 Julkaisukriteerit

Versiota ei julkaista, jos:

- kriittiset testit epäonnistuvat
- Large-suorituskyky ylittää ehdottoman rajan
- tunnettu sääntövirhe estää kelvollisen kaavion
- `.spc`-migraatio rikkoo vanhoja projekteja

Jokaisella major/minor-julkaisulla on:

- muutosloki
- testiraportti
- lyhyt päivitysohje

---

# 16.11 Yhteenveto

| Versio | Päämäärä                                      |
| ------ | --------------------------------------------- |
| v0.1   | Domain + Condes + runko                       |
| v0.2   | Tuonti + lista-painotteinen ehdotus (legacy)  |
| v0.3   | StartLocation + ClassStartPlan ytimenä        |
| v0.4   | Optimointi ja UI-viimeistely                  |
| v0.5   | Kilpailukäyttö (kytkennät, update, ruudukko)  |
| v0.6   | PDF, ohje, paketoinnin alku                   |
| v1.0   | Tuotantokelpoinen julkaisu                    |
| v1.x   | Vakaus ja palaute                             |
| v2.0   | Uudet muodot ja integraatiot                  |

---

# 16.12 Suunnitteluperiaatteet

- Julkaise pienin hyödyllinen kokonaisuus.
- Pidä projektitiedosto yhteensopivana.
- Mittaa laatua testeillä ja oikeilla kilpailuilla.
- Laajenna plugineilla, älä ytimen haarautumisella.
