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

# 2.2 Kilpailu (Competition)

Kilpailu on ohjelman päätason olio.

Kilpailu sisältää:

- kilpailun perustiedot
- kaikki sarjat
- kaikki radat
- kaikki kilpailijat
- lähtökaavion
- asetukset
- historian

Yhdessä ohjelmassa voi olla avoinna vain yksi kilpailu kerrallaan.

---

# 2.3 Sarja (Class)

Sarja kuvaa kilpailuluokkaa.

Esimerkkejä:

- H21
- D21
- H35
- D16
- RR
- TR

Sarjalla on vähintään seuraavat tiedot:

| Kenttä             | Selitys                      |
| ------------------ | ---------------------------- |
| id                 | yksilöllinen tunniste        |
| nimi               | H21                          |
| rata               | radan tunniste               |
| kilpailijamäärä    | osallistujien määrä          |
| arvioitu vauhti    | suhteellinen nopeus          |
| arvioitu rata-aika | minuuttia                    |
| lähtöväli          | oletus 2 min                 |
| lukittu            | voiko ohjelma siirtää sarjaa |

---

# 2.4 Rata (Course)

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

# 2.5 Ensimmäinen rasti

Ensimmäinen rasti on lähtökaavion tärkeimpiä tietoja.

Kaikki sarjat, joiden ensimmäinen rasti on sama, muodostavat ensimmäisen rastin ryhmän.

Lähtökaavassa samaa ensimmäistä rastia kohti saa lähteä korkeintaan yksi kilpailija minuutissa.

Tämä sääntö koskee kaikkia sarjoja.

Esimerkki

```
H21 → 31

D21 → 31

H20 → 31
```

Nämä kolme sarjaa jakavat saman ensimmäisen rastin.

---

# 2.6 Kilpailija (Competitor)

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

Lähtöaika ja lähtönumero kuuluvat `Start`-olioon, eivät kilpailijaan.

---

# 2.7 Lähtö (Start)

Lähtö kuvaa yhden kilpailijan lähtöä.

Lähtö sisältää:

- kilpailijan
- lähtöajan
- lähtönumeron

Lähtö ei kuulu kilpailijaan.

Lähtö kuuluu lähtökaavioon.

Näin sama kilpailija voidaan tarvittaessa sijoittaa uudelleen ilman, että kilpailijatietoja muutetaan.

---

# 2.8 Lähtökaavio (Start Schedule)

Lähtökaavio on järjestetty lista lähdöistä.

Esimerkki

```
12:00 H21 1

12:02 H21 2

12:04 H21 3

12:06 D21 1
```

Kaikki optimointi tehdään tähän rakenteeseen.

Kilpailijatietoja ei muuteta.

---

# 2.9 Sarjaryhmä

Useita sarjoja voidaan käsitellä yhtenä ryhmänä.

Esimerkki

```
H21

H20

H18
```

Ohjelma voi sijoittaa nämä peräkkäin.

Ryhmä voidaan myöhemmin lukita.

---

# 2.10 Lukitus

Lukitus estää ohjelmaa muuttamasta kohdetta.

Lukittavia kohteita ovat

- kilpailija
- sarja
- lähtö
- aikajakso

Esimerkki

```
12:00–12:20

LUKITTU
```

Optimizer ei saa tehdä muutoksia lukitulle alueelle.

---

# 2.11 Jälki-ilmoittautunut

Jälki-ilmoittautunut on kilpailija, joka lisätään lähtökaavion muodostamisen jälkeen.

Ohjelman tavoitteena on sijoittaa jälki-ilmoittautunut niin, että mahdollisimman vähän olemassa olevia lähtöjä tarvitsee siirtää.

Vaihtoehdot:

- automaattinen sijoitus
- käyttäjän valitsema paikka
- kokonaan uusi lähtöväli

---

# 2.12 Historia

Kaikista käyttäjän tekemistä muutoksista muodostetaan historiatieto.

Historiaan tallennetaan:

- aika
- toiminto
- käyttäjä (mahdollinen tulevaisuudessa)
- vanha arvo
- uusi arvo

Historia mahdollistaa muutosten seurannan ja myöhemmin myös kumoamisen.

---

# 2.13 Domain-säännöt

Domainissa noudatetaan seuraavia sääntöjä:

- Kilpailija kuuluu aina yhteen sarjaan.
- Sarja käyttää yhtä rataa.
- Rataa voi käyttää usea sarja.
- Radalla on vähintään yksi rasti.
- Ensimmäinen rasti määräytyy rastilistasta.
- Lähtö kuuluu lähtökaavioon.
- Kilpailijaa ei poisteta lähtökaaviota muokattaessa.
- Lukittu kohde ei muutu automaattisesti.
- Kaikki muutokset kirjataan historiaan.

Nämä säännöt ovat ohjelman perusta, eikä niitä saa rikkoa missään moduulissa.
