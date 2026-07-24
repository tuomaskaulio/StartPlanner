# 2 Domain-malli

## 2.1 Johdanto

StartPlanner perustuu suunnistuskilpailun käsitteisiin (domainiin).

Ohjelman sisäinen tietomalli ei saa riippua yksittäisestä tiedostomuodosta (Condes, IRMA, eResults jne.), vaan kaikki tiedot muunnetaan yhteiseen malliin.

Kaikki ohjelman algoritmit käyttävät tätä mallia.

```
Condes XML
            \
IRMA --------> Domain Model --------> Scheduler
            /
EResults
```

Importterit muuttavat ulkoisen tiedon aina Domain-olioiksi.

---

# 2.2 Käsitteiden erottelu

| Käsite | Englantilainen nimi | Sisältö |
| ------ | ------------------- | ------- |
| Lähtö | `StartLocation` | Fyysinen tai looginen lähtöpaikka (esim. Lähtö 1) |
| Lähtökaavio | `ClassStartPlan` | Sarjojen ensimmäiset lähtöajat yhdessä lähdössä |
| Lähtölista | `StartList` | Kilpailijakohtaiset ajat ja numerot (jatkokehitys) |

StartPlannerin **päätuote** on lähtökaavio. Yksittäisten kilpailijoiden lähtöajat arvotaan tyypillisesti tulospalveluohjelmassa; lähtölista ei kuulu ydinlupaukseen.

---

# 2.3 Kilpailu (Competition)

Kilpailu on ohjelman päätason olio.

Kilpailu sisältää:

- kilpailun perustiedot
- yksi tai useampi lähtö (`StartLocation`)
- kaikki sarjat
- kaikki radat
- kaikki kilpailijat (ilmoittautumistieto)
- lähtökaaviot (yksi per lähtö)
- asetukset
- historian

Yhdessä ohjelmassa voi olla avoinna vain yksi kilpailu kerrallaan.

---

# 2.4 Lähtö (StartLocation)

Lähtö kuvaa fyysistä tai loogista lähtöpaikkaa.

Esimerkkejä: “Lähtö A”, “Lähtö 1”, “Koulun piha”.

| Kenttä | Selitys |
| ------ | ------- |
| id | yksilöllinen tunniste |
| nimi | näyttönimi |
| first_start | valinnainen ensimmäinen lähtöaika; tyhjä = kilpailun `competition_start` |

Kilpailussa on vähintään yksi lähtö. Jos lähtöjä ei ole määritelty, käytetään yhtä oletuslähtöä.

**Sarja kuuluu täsmälleen yhteen lähtöön.**

Eri lähtöjen lähtökaaviot suunnitellaan **itsenäisesti**. Niiden kellonajat eivät riipu toisistaan; jokaisella lähdöllä voi olla oma `first_start`.

---

# 2.5 Sarja (RaceClass)

Sarja kuvaa kilpailuluokkaa.

Esimerkkejä:

- H21
- D21
- H35
- D16
- RR
- TR

Sarjalla on vähintään seuraavat tiedot:

| Kenttä             | Selitys                         |
| ------------------ | ------------------------------- |
| id                 | yksilöllinen tunniste           |
| nimi               | H21                             |
| rata               | radan tunniste                  |
| lähtö              | `start_location_id`             |
| kilpailijamäärä    | osallistujien määrä             |
| arvioitu vauhti    | suhteellinen nopeus             |
| arvioitu rata-aika | minuuttia                       |
| lähtöväli          | oletus 2 min                    |
| järjestys          | `sort_order` (näyttö/kaavio)    |
| lukittu            | voiko ohjelma siirtää sarjaa    |

---

# 2.6 Rata (Course)

Rata kuvaa yhtä kilpailurataa.

Rata ei riipu sarjoista.

Useita sarjoja voi käyttää samaa rataa.

Radalla on vähintään:

| Kenttä | Selitys                     |
| ------ | --------------------------- |
| id     | tunniste                    |
| nimi   | A-rata                      |
| pituus | kilometreinä                |
| nousu  | metreinä                    |
| rastit | järjestetty lista rasteista |

Esimerkki

```
A-rata

31

45

38

82

100
```

Ensimmäinen rasti määritellään aina rastilistan ensimmäisestä alkiosta.

Rastilista sisältää vain kilpailurastit (`CourseControl type="Control"`).
Start- ja Finish-pisteitä ei lasketa mukaan. Näin IOF CourseData -tuonnissa
ensimmäinen rasti ei ole lähtöpiste (esim. `L1`) vaan ensimmäinen varsinainen rasti.

Ohjelma ei tallenna ensimmäistä rastia erillisenä Domain-kenttänä
(SQLite-projekti voi cachettaa sen luettavuuden vuoksi).

---

# 2.7 Ensimmäinen rasti

Ensimmäinen rasti on lähtökaavion tärkeimpiä tietoja.

Kaikki **saman lähdön** sarjat, joiden ensimmäinen rasti on sama, muodostavat ensimmäisen rastin ryhmän kyseisessä lähdössä.

**Säännön scope:** samassa lähdössä samaa ensimmäistä rastia kohti saa lähteä korkeintaan yksi kilpailija minuutissa (kaavion tasolla: sarjojen päällekkäiset minuuttislotit eivät saa ylikuormittaa rastia).

**Eri lähdöistä** saa lähteä samalle ensimmäiselle rastille samaan minuuttiin. Lähdöt eivät jaa 1. rastin kapasiteettia keskenään.

Esimerkki (sama lähtö)

```
H21 → 31

D21 → 31

H20 → 31
```

Nämä kolme sarjaa jakavat saman ensimmäisen rastin **tässä lähdössä**.

---

# 2.8 Kilpailija (Competitor)

Kilpailija kuuluu aina täsmälleen yhteen sarjaan.

Kilpailijalla on vähintään:

| Kenttä    | Selitys                  |
| --------- | ------------------------ |
| id        | tunniste                 |
| etunimi   |                          |
| sukunimi  |                          |
| seura     |                          |
| sarja     | viittaus sarjaan         |
| emit      | valinnainen              |
| lukittu   | voiko ohjelma siirtää    |

Ilmoittautumistieto tarvitaan kilpailijamääriin ja raportteihin. Yksittäisen kilpailijan lähtöaika ei kuulu Domain-ytimeen (ks. lähtölista, jatkokehitys).

---

# 2.9 Lähtökaavio (ClassStartPlan)

Lähtökaavio on StartPlannerin päätulos.

Se on **yhteen lähtöön** kuuluva järjestetty lista sarjojen sijoituksista.

Jokainen rivi (`ClassStart`) sisältää vähintään:

| Kenttä                 | Selitys                          |
| ---------------------- | -------------------------------- |
| sarja                  | `class_id`                       |
| ensimmäinen lähtöaika  | sarjan ensimmäisen kilpailijan aika |

Esimerkki

```
12:00  H21
12:10  D21
12:22  H20
```

Sarjan kesto kaaviossa johdetaan tarvittaessa:

```
kesto ≈ (kilpailijamäärä − 1) × lähtöväli
```

Kaikki automaattinen sijoittelu ja optimointi tehdään tähän rakenteeseen **lähdöittäin**.

Kilpailijatietoja ei muuteta kaaviota muodostaessa.

---

# 2.10 Lähtölista (StartList) — jatkokehitys

Lähtölista on kilpailijakohtainen lista lähtöajoista ja -numeroista.

Esimerkki

```
12:00 H21 Virtanen Aino 1
12:02 H21 Korhonen Elias 2
```

Yksittäisten kilpailijoiden ajat arvotaan yleensä tulospalveluohjelmassa. StartPlanner voi myöhemmin:

- tuottaa yksinkertaisen listan kaaviosta (lähtövälin mukaan), tai
- tuoda valmiin listan tulospalvelusta

Tämä ei ole v0.3-ydintoiminto.

> **v0.2-toteutus:** nykyinen koodi tuottaa vielä kilpailijakohtaisen `StartSchedule`-listan. Se on väliaikainen; speksin mukainen ydin on `ClassStartPlan`.

---

# 2.11 Sarjaryhmä

Useita sarjoja voidaan käsitellä yhtenä ryhmänä.

Esimerkki

```
H21

H20

H18
```

Ohjelma voi sijoittaa nämä peräkkäin saman lähdön kaaviossa.

Ryhmä voidaan myöhemmin lukita.

---

# 2.12 Lukitus

Lukitus estää ohjelmaa muuttamasta kohdetta.

Lukittavia kohteita ovat

- sarja
- aikajakso (lähdön sisällä)
- myöhemmin: yksittäinen kilpailija / listarivi (jos lähtölista käytössä)

Esimerkki

```
12:00–12:20

LUKITTU
```

Optimizer ei saa tehdä muutoksia lukitulle alueelle.

---

# 2.13 Jälki-ilmoittautunut

Jälki-ilmoittautunut on kilpailija, joka lisätään ilmoittautumisen jälkeen.

Kaavion tasolla vaikutus on yleensä kilpailijamäärän kasvu (sarjan kesto voi pidentyä). Yksittäisen paikan arpominen kuuluu tulospalveluun tai tulevaan lähtölista-ominaisuuteen.

---

# 2.14 Historia

Kaikista käyttäjän tekemistä muutoksista muodostetaan historiatieto.

Historiaan tallennetaan:

- aika
- toiminto
- käyttäjä (mahdollinen tulevaisuudessa)
- vanha arvo
- uusi arvo

Historia mahdollistaa muutosten seurannan ja myöhemmin myös kumoamisen.

---

# 2.15 Domain-säännöt

Domainissa noudatetaan seuraavia sääntöjä:

- Kilpailussa on vähintään yksi lähtö.
- Sarja kuuluu täsmälleen yhteen lähtöön.
- Sarja käyttää yhtä rataa.
- Rataa voi käyttää usea sarja (myös eri lähdöissä).
- Radalla on vähintään yksi kilpailurasti.
- Ensimmäinen rasti määräytyy rastilistasta.
- Lähtökaavio kuuluu yhteen lähtöön ja sisältää sarjojen ensimmäiset ajat.
- Eri lähdöt eivät jaa aikajanaa eivätkä 1. rastin kapasiteettia.
- Kilpailija kuuluu aina yhteen sarjaan.
- Lukittu kohde ei muutu automaattisesti.
- Kaikki muutokset kirjataan historiaan.

Nämä säännöt ovat ohjelman perusta, eikä niitä saa rikkoa missään moduulissa.
