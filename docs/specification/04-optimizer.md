# 4 Optimointimoottori

## 4.1 Johdanto

StartPlannerin optimointimoottorin tehtävänä on muodostaa kilpailulle mahdollisimman hyvä lähtökaavio.

Koska lähtökaavion muodostamiseen vaikuttaa useita samanaikaisia rajoitteita, ongelmaa ei käsitellä yksittäisenä laskukaavana vaan rajoiteoptimointina (Constraint Optimization Problem).

Optimointimoottori pyrkii löytämään hyvän käytännön ratkaisun kohtuullisessa ajassa.

Tavoitteena ei ole löytää matemaattisesti optimaalista ratkaisua.

---

# 4.2 Optimoinnin periaatteet

Optimointi tapahtuu vaiheittain.

1. muodostetaan ensimmäinen kelvollinen lähtökaavio
2. tarkistetaan sääntörikkomukset
3. parannetaan ratkaisua iteratiivisesti
4. lopetetaan, kun parannuksia ei enää löydy

Ensimmäinen ratkaisu on aina käyttökelpoinen.

Optimointi vain parantaa sitä.

---

# 4.3 Optimointitasot

Optimointi jakautuu kolmeen tasoon.

## Taso 1 – Pakolliset ehdot

Näitä ei saa koskaan rikkoa.

- lähtöväli
- sama rata ei limittäin
- ensimmäinen rasti
- lukitut lähdöt
- käyttäjän tekemät lukitukset

Jos jokin näistä rikkoutuu, ratkaisu hylätään.

---

## Taso 2 – Tärkeät tavoitteet

Pyritään toteuttamaan mahdollisimman hyvin.

- tasainen kilpailijavirta
- nopeammat sarjat ensin
- sarjojen looginen järjestys

Näiden rikkominen kasvattaa kustannusta.

---

## Taso 3 – Pehmeät tavoitteet

Näitä voidaan rikkoa tarvittaessa.

- sarjojen välinen tauko
- käyttäjän suosima järjestys
- esteettisesti selkeä lähtökaavio

---

# 4.4 Kustannusfunktio

Jokaiselle lähtökaaviolle lasketaan kustannusarvo.

Pienempi arvo tarkoittaa parempaa lähtökaaviota.

Esimerkki

```
Cost =

100000 × pakolliset virheet

+

500 × ensimmäisen rastin konfliktit

+

200 × kilpailijavirran epätasaisuus

+

100 × väärä sarjajärjestys

+

20 × tarpeettomat tauot
```

Painokertoimet ovat käyttäjän muutettavissa asetuksista.

---

# 4.5 Kilpailijavirran mittaaminen

Optimointimoottori laskee jokaiselle minuutille

- lähtevien kilpailijoiden määrän
- kumulatiivisen määrän

Esimerkki

| Aika  | Lähtijöitä |
| ----- | ---------: |
| 12:00 |          4 |
| 12:01 |          5 |
| 12:02 |          4 |
| 12:03 |          5 |
| 12:04 |          4 |

Tasainen vaihtelu on tavoiteltavaa.

Suuria piikkejä pyritään välttämään.

---

# 4.6 Ensimmäisen rastin kuormitus

Jokaiselle ensimmäiselle rastille muodostetaan oma aikajana.

Esimerkki

Rasti 31

| Aika  | Lähtijöitä |
| ----- | ---------: |
| 12:00 |          1 |
| 12:01 |          1 |
| 12:02 |          1 |

Jos samalla minuutilla olisi kaksi kilpailijaa samalle ensimmäiselle rastille, syntyy sääntörikkomus.

---

# 4.7 Sarjojen sijoittaminen

Sarjat sijoitetaan kokonaisuuksina.

Algoritmi ei hajota sarjaa useaan osaan ilman käyttäjän nimenomaista hyväksyntää.

Esimerkki

```
H21

12:00

12:02

12:04

12:06
```

ei koskaan

```
12:00

12:02

D21

12:04

12:06
```

Tämä tekee lähtökaaviosta helposti luettavan.

---

# 4.8 Jälki-ilmoittautuneet

Jälki-ilmoittautuneiden lisääminen on oma optimointitehtävänsä.

Algoritmi toimii seuraavasti.

1. Etsi vapaat lähtöpaikat.
2. Tarkista sääntöjen toteutuminen.
3. Laske muutoksen kustannus.
4. Valitse pienimmän kustannuksen ratkaisu.

Tavoitteena on siirtää mahdollisimman vähän olemassa olevia lähtöjä.

---

# 4.9 Lukitukset

Lukitut kohteet poistetaan optimoinnista.

Optimointimoottori käsittelee niitä kiinteinä.

Lukita voidaan

- kilpailija
- sarja
- aikajakso
- lähtö
- kokonainen rataryhmä

---

# 4.10 Optimoinnin pysäytysehdot

Optimointi lopetetaan, kun jokin seuraavista täyttyy.

- parannuksia ei enää löydy
- käyttäjän määrittämä aikaraja saavutetaan
- maksimimäärä iteraatioita saavutetaan
- käyttäjä keskeyttää optimoinnin

---

# 4.11 Suorituskyky

Tyypillinen kilpailu

- 40 sarjaa
- 800 kilpailijaa
- 15 rataa

tulee optimoida alle viidessä sekunnissa tavallisella työasemalla.

Ensimmäinen käyttökelpoinen lähtökaavio tulee muodostaa alle yhdessä sekunnissa.

---

# 4.12 Tulevaisuuden laajennukset

Optimointimoottori suunnitellaan siten, että uusia optimointialgoritmeja voidaan lisätä ilman muutoksia käyttöliittymään.

Esimerkkejä tulevista algoritmeista:

- Ahne algoritmi (Greedy)
- Simulated Annealing
- Tabu Search
- Geneettinen algoritmi
- OR-Tools Constraint Solver

Käyttäjä voi myöhemmin valita käytettävän optimointimenetelmän asetuksista.

---

# 4.13 Optimointimoottorin rajapinta

Optimointimoottori toimii palveluna.

```
SchedulerService
    │
    ▼
Optimizer
    │
    ▼
StartSchedule
```

Rajapinnan tulee mahdollistaa ainakin seuraavat toiminnot:

- muodosta uusi lähtökaavio
- optimoi nykyinen lähtökaavio
- lisää jälki-ilmoittautuneet
- tarkista sääntöjen toteutuminen
- laske lähtökaavion laatupisteet

Optimointimoottori ei saa riippua käyttöliittymästä eikä tiedostomuodoista.

Se käyttää ainoastaan ohjelman Domain-mallia.
