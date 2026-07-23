# 5 Lähtökaavioalgoritmi

## 5.1 Tavoite

Lähtökaavioalgoritmin tehtävänä on muodostaa kilpailulle lähtökaavio, joka täyttää kaikki pakolliset säännöt ja tuottaa mahdollisimman tasaisen kilpailijavirran.

Algoritmi toimii deterministisesti. Samoilla lähtötiedoilla ja asetuksilla muodostuu aina sama lähtökaavio.

Satunnaisuutta ei käytetä.

---

# 5.2 Syöte

Algoritmi saa syötteenä ainoastaan Domain-mallin.

Syötteeseen kuuluvat:

- kilpailu
- sarjat
- kilpailijat
- radat
- asetukset
- mahdolliset lukitukset

Algoritmi ei lue tiedostoja eikä käytä käyttöliittymää.

---

# 5.3 Tulos

Tuloksena syntyy StartSchedule.

Lähtökaavio sisältää:

- kilpailijan
- lähtöajan
- lähtönumeron
- sarjan
- radan

Lähtökaavio voidaan muodostaa useita kertoja ilman että alkuperäinen kilpailudata muuttuu.

---

# 5.4 Vaihe 1 – Datan tarkistus

Ennen laskentaa tarkistetaan:

- kaikilla kilpailijoilla on sarja
- kaikilla sarjoilla on rata
- kaikilla radoilla on vähintään yksi rasti
- lähtöväli on määritelty
- kilpailun aloitusaika on asetettu

Virheellinen aineisto estää laskennan.

---

# 5.5 Vaihe 2 – Sarjojen ryhmittely

Sarjat ryhmitellään radan mukaan.

Esimerkki

Rata A

- H21
- H20

Rata B

- D21
- D20

Jokainen rata muodostaa yhden käsittelyryhmän.

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

Kullekin sarjalle varataan yhtenäinen aikajakso.

Sarjaa ei koskaan jaeta useaan osaan automaattisesti.

Esimerkki

```
12:00

12:02

12:04

12:06
```

ei

```
12:00

12:02

...

12:20

12:22
```

---

# 5.9 Vaihe 6 – Ensimmäisen rastin tarkistus

Kun sarja sijoitetaan, tarkistetaan jokainen lähtö.

Jos samalla minuutilla lähtisi toinen kilpailija samalle ensimmäiselle rastille,

sijoitusta siirretään eteenpäin, kunnes konflikti poistuu.

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

- siirtää lukittua kilpailijaa
- siirtää lukittua sarjaa
- käyttää lukittua aikajaksoa

Jos optimointi vaatisi lukituksen rikkomista,

ratkaisu hylätään.

---

# 5.13 Vaihe 10 – Validointi

Valmis lähtökaavio tarkistetaan.

Tarkistetaan ainakin:

- lähtövälit
- ensimmäiset rastit
- ratojen limitys
- päällekkäiset lähdöt
- lukitukset

Virheellinen lähtökaavio palautetaan virhetilassa.

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

Samoilla syötteillä syntyy aina sama tulos.

Tämä helpottaa:

- testausta
- virheiden selvittämistä
- historiatietojen vertailua
- käyttäjän luottamusta ohjelmaan

---

# 5.16 Suorituskykyvaatimukset

Tavoitteet:

- ensimmäinen ratkaisu alle 1 sekunti
- optimointi alle 5 sekuntia
- jälki-ilmoittautuneen lisäys alle 1 sekunti

Testikokona käytetään:

- 40 sarjaa
- 20 rataa
- 1000 kilpailijaa

---

# 5.17 Algoritmin laajennettavuus

Lähtökaavioalgoritmi toteutetaan omana palvelunaan.

Rajapinta:

```
SchedulerService
```

jonka vastuulla on:

- uuden lähtökaavion muodostaminen
- nykyisen lähtökaavion optimointi
- validointi
- laatupisteiden laskenta

Algoritmi ei tunne käyttöliittymää eikä tiedostomuotoja.

Kaikki syöte saadaan Domain-mallista.

Kaikki tulokset palautetaan Domain-malliin.
