# 5 Lähtökaavioalgoritmi

## 5.1 Tavoite

Lähtökaavioalgoritmin tehtävänä on muodostaa **yhden lähdön** (`StartLocation`) `ClassStartPlan`, joka täyttää pakolliset säännöt ja tuottaa mahdollisimman tasaisen kilpailijavirran sarjatasolla.

Algoritmi toimii deterministisesti. Samoilla lähtötiedoilla ja asetuksilla muodostuu aina sama kaavio.

Satunnaisuutta ei käytetä.

Kilpailijakohtaista lähtölistaa ei tuoteta (jatkokehitys / tulospalvelu).

---

# 5.2 Syöte

Algoritmi saa syötteenä Domain-mallin ja käsiteltävän lähdön tunnisteen.

Syötteeseen kuuluvat:

- kilpailu
- `start_location_id`
- kyseisen lähdön sarjat
- radat
- kilpailijamäärät (sarjoittain)
- asetukset
- mahdolliset lukitukset

Algoritmi ei lue tiedostoja eikä käytä käyttöliittymää.

---

# 5.3 Tulos

Tuloksena syntyy `ClassStartPlan`.

Jokainen rivi sisältää:

- sarjan
- ensimmäisen lähtöajan
- (johdettuna) radan ja 1. rastin raportointia varten

Kaavio voidaan muodostaa uudelleen ilman että ilmoittautumisdata muuttuu.

> **v0.2:** toteutus palauttaa vielä kilpailijakohtaisen `StartSchedule`-listan. Speksin mukainen tulos on `ClassStartPlan`.

---

# 5.4 Vaihe 1 – Datan tarkistus

Ennen laskentaa tarkistetaan:

- `start_location_id` on olemassa
- kaikilla käsiteltävillä sarjoilla on rata ja lähtö
- kaikilla radoilla on vähintään yksi kilpailurasti
- lähtöväli on määritelty
- lähdön aikajanan alku on asetettu
- kilpailijamäärä on tiedossa (tai 0)

Virheellinen aineisto estää laskennan.

---

# 5.5 Vaihe 2 – Sarjojen ryhmittely

Käsitellään vain valitun lähdön sarjat.

Sarjat ryhmitellään radan mukaan.
---

# 5.6 Vaihe 3 – Ensimmäisen rastin ryhmittely

Jokaisesta radasta selvitetään ensimmäinen rasti.

Esimerkki

Rata A → 31

Rata B → 31

Rata C → 45

Tämän jälkeen muodostetaan ensimmäisen rastin ryhmät.

Rasti 31

- rata A
- rata B

Rasti 45

- rata C

Näitä käytetään myöhemmin konfliktien estämiseen.

---

# 5.7 Vaihe 4 – Sarjojen järjestäminen

Sarjat järjestetään.

Oletusjärjestys:

1. käyttäjän määrittämä järjestys
2. arvioitu kilpailunopeus
3. radan pituus
4. sarjan nimi

Järjestys on vakaa.

Jos kaksi sarjaa ovat muuten samanarvoisia, niiden keskinäinen järjestys ei muutu.

---

# 5.8 Vaihe 5 – Sarjojen sijoittaminen

Sarjat sijoitetaan aikajanalle yksi kerrallaan.

Kullekin sarjalle asetetaan `first_start_time`. Sarjan peittämä aikaväli on

```
[first, first + (n − 1) × interval]
```

Sarjaa ei koskaan jaeta useaan osaan automaattisesti.
---

# 5.9 Vaihe 6 – Ensimmäisen rastin tarkistus

Kun sarja sijoitetaan, tarkistetaan sen peittämät minuutit suhteessa muihin
**saman lähdön** sarjoihin, joilla on sama ensimmäinen rasti.

Jos kapasiteetti (1 / min) ylittyy, sijoitusta siirretään eteenpäin.
---

# 5.10 Vaihe 7 – Sarjojen väliset tauot

Kun sarja päättyy,

lisätään asetusten mukainen tauko.

Oletusarvo:

2 minuuttia.

Tauko voidaan poistaa, jos käyttäjä niin määrittää.

---

# 5.11 Vaihe 8 – Kilpailijavirran tasaus

Kun kaikki sarjat on sijoitettu,

lasketaan kilpailijamäärä jokaiselle minuutille.

Jos havaitaan suuria vaihteluita,

sarjoja voidaan siirtää kokonaisina eteen- tai taaksepäin.

Siirto tehdään vain, jos:

- kaikki pakolliset säännöt säilyvät
- kustannus pienenee

---

# 5.12 Vaihe 9 – Lukitusten tarkistus

Kaikki lukitut kohteet tarkistetaan.

Optimointi ei saa:

- siirtää lukittua sarjaa
- käyttää lukittua aikajaksoa

Jos optimointi vaatisi lukituksen rikkomista,

ratkaisu hylätään.

---

# 5.13 Vaihe 10 – Validointi

Valmis `ClassStartPlan` tarkistetaan (vain kyseinen lähtö).

Tarkistetaan ainakin:

- ensimmäisen rastin kapasiteetti
- ratojen limitys
- lukitukset

Virheellinen kaavio palautetaan virhetilassa.

---

# 5.14 Laatupisteet

Jokaiselle lähtökaaviolle lasketaan laatupisteet.

Esimerkki:

| Osa-alue                | Maksimi |
| ----------------------- | ------: |
| Sääntöjen noudattaminen |      50 |
| Ensimmäiset rastit      |      20 |
| Kilpailijavirta         |      15 |
| Sarjajärjestys          |      10 |
| Tauot                   |       5 |

Yhteensä:

100 pistettä.

Tarkoitus ei ole "kilpailuttaa" lähtökaavioita, vaan antaa käyttäjälle nopeasti käsitys siitä, kuinka hyvä ehdotus on.

---

# 5.15 Algoritmin deterministisyys

Algoritmin tulee olla deterministinen.

Samoilla syötteillä (mukaan lukien `start_location_id`) syntyy aina sama tulos.

---

# 5.16 Suorituskykyvaatimukset

Tavoitteet:

- ensimmäinen kaavio alle 1 sekunti
- optimointi alle 5 sekuntia

Testikokona käytetään:

- 40 sarjaa / lähtö
- 20 rataa
- 1000 kilpailijaa (määrätietoina)

---

# 5.17 Algoritmin laajennettavuus

Lähtökaavioalgoritmi toteutetaan omana palvelunaan.

Rajapinta:

```
SchedulerService
```

jonka vastuulla on:

- uuden `ClassStartPlan`-kaavion muodostaminen yhdelle lähdölle
- nykyisen kaavion optimointi
- validointi
- laatupisteiden laskenta

Algoritmi ei tunne käyttöliittymää eikä tiedostomuotoja.

Kaikki syöte saadaan Domain-mallista.

Kaikki tulokset palautetaan Domain-malliin.
