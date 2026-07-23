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

# 16.4 v0.2 – Ensimmäinen lähtökaavio

**Tavoite:** käyttökelpoinen automaattinen ehdotus.

Sisältää:

- IOF CourseData (Condes) -tuonti, myös usean XML:n merge ja nimeen perustuva sarja↔rata
- IRMA `= ILMOIT` -ilmoittautumisraportin tuonti
- SchedulerService:n greedy-algoritmi (deterministinen)
- lähtövälien ja ensimmäisen rastin perussäännöt
- perusvalidointi + issues-lista GUI:ssa
- Excel- ja CSV-vienti
- `.spc` tallenna/avaa
- esimerkkiaineistot: anonymisoidut sample-small (complete) + sample-medium

Käyttäjä voi tuottaa ensimmäisen kaavion oikealla aineistolla.

---

# 16.5 v0.3 – Optimointi ja jäljitettävyys

**Tavoite:** muokattavuus ilman kaaosta.

Sisältää:

- optimointimoottori
- lukitukset
- historia (audit trail)
- Undo / Redo
- laatupisteet
- korjausehdotusten ensimmäinen versio

---

# 16.6 v0.4 – Käyttöliittymän viimeistely

**Tavoite:** päivittäiseen kilpailutyöhön sopiva UI.

Sisältää:

- aikajananäkymä
- sarja- ja kilpailijamuokkaus
- validointiraportti UI:ssa
- viennin viimeistely (Excel, CSV, PDF)
- asetukset (kilpailu / käyttäjä)
- `.spc`-projektitiedosto tuotantokelpoisena

---

# 16.7 v1.0 – Tuotantoversio

**Tavoite:** ensimmäinen vakaa julkaisu kansallisiin kilpailuihin.

Sisältää:

- dokumentoidut import/export-pluginit
- täysi validointi lajisääntöineen
- suorituskykytavoitteet Large-aineistolla
- regressiotestit ja hyväksymistestaus oikealla kilpailulla
- asennuspaketit (Windows, macOS, Linux)
- käyttäjäohjeen perusversio

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

| Versio | Päämäärä                          |
| ------ | --------------------------------- |
| v0.1   | Domain + Condes + runko           |
| v0.2   | Ensimmäinen automaattinen kaavio  |
| v0.3   | Optimointi, lukitukset, historia  |
| v0.4   | UI ja viennin viimeistely         |
| v1.0   | Tuotantokelpoinen julkaisu        |
| v1.x   | Vakaus ja palaute                 |
| v2.0   | Uudet muodot ja integraatiot      |

---

# 16.12 Suunnitteluperiaatteet

- Julkaise pienin hyödyllinen kokonaisuus.
- Pidä projektitiedosto yhteensopivana.
- Mittaa laatua testeillä ja oikeilla kilpailuilla.
- Laajenna plugineilla, älä ytimen haarautumisella.
