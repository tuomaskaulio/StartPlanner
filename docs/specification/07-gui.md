# 7 Käyttöliittymä

## 7.1 Suunnitteluperiaatteet

StartPlanner on työpöytäsovellus.

Käyttöliittymä toteutetaan PySide6-kirjastolla.

Käyttöliittymän tavoitteet ovat:

- selkeä
- nopea käyttää
- vähän klikkauksia
- kaikki tärkeä tieto näkyvissä
- turvallinen käyttää

Ohjelma ei koskaan tee käyttäjän tietämättä muutoksia lähtökaavioon.

---

# 7.2 Käyttöliittymän rakenne

Ohjelma koostuu seuraavista näkymistä.

```
+------------------------------------------------------+
| Valikko                                               |
+------------------------------------------------------+
| Työkalurivi                                           |
+------------------------------------------------------+
| Kilpailupuu | Päänäkymä                              |
|             |                                        |
|             |                                        |
|             |                                        |
|             |                                        |
+------------------------------------------------------+
| Tilarivi                                             |
+------------------------------------------------------+
```

---

# 7.3 Kilpailupuu

Vasen reuna sisältää kilpailun rakenteen.

```
Kilpailu

    Sarjat

    Radat

    Kilpailijat

    Lähtökaavio

    Historia

    Asetukset

    Loki
```

Kilpailupuu toimii ohjelman päänavigointina.

---

# 7.4 Sarjanäkymä

Sarjanäkymässä näytetään kaikki sarjat.

Esimerkki

| Sarja | Rata | Kilpailijoita | Lähtöväli | Lukittu |
| ----- | ---- | ------------: | --------: | ------- |
| H21   | A    |            58 |         2 |         |
| D21   | B    |            41 |         2 |         |
| H20   | A    |            31 |         2 |         |

Sarjoja voidaan:

- järjestää
- lukita
- muuttaa lähtöväliä
- muuttaa järjestystä

---

# 7.5 Ratanäkymä

Näyttää kaikki radat.

| Rata | Pituus | Nousu | Ensimmäinen rasti |
| ---- | -----: | ----: | ----------------: |
| A    |   12.4 |   285 |                31 |
| B    |    9.2 |   210 |                31 |
| C    |    7.5 |   170 |                45 |

Rataa napsauttamalla voidaan tarkastella rastiluetteloa.

---

# 7.6 Kilpailijanäkymä

Näyttää kaikki kilpailijat.

Suodatus:

- sarja
- seura
- nimi

Näytettävät tiedot:

- nimi
- seura
- sarja
- Emit
- lähtöaika
- lukittu

---

# 7.7 Lähtökaavio

Ohjelman tärkein näkymä.

Taulukko:

| Aika | Sarja | Kilpailija | Rata | 1. rasti | Lukittu |
| ---- | ----- | ---------- | ---- | -------- | ------- |

Mahdolliset toiminnot:

- siirrä kilpailijaa
- siirrä sarjaa
- lisää tauko
- lukitse
- poista lukitus

---

# 7.8 Graafinen aikajana

Lähtökaavio voidaan näyttää myös aikajanana.

Esimerkki

```
12:00  ███ H21

12:10  ███ D21

12:20  ███ H20

12:30  ███ D20
```

Tämä helpottaa kokonaisuuden hahmottamista.

---

# 7.9 Ensimmäisen rastin näkymä

Ohjelmassa on oma näkymä ensimmäisille rasteille.

| Rasti | Lähtöjä |
| ----- | ------: |
| 31    |      48 |
| 45    |      37 |
| 52    |      26 |

Valittaessa rasti näytetään aikajana.

```
12:00

12:01

12:02

12:03
```

Mahdolliset konfliktit korostetaan punaisella.

---

# 7.10 Kilpailijavirta

Ohjelma näyttää kilpailijavirran kuvaajana.

X-akseli

- aika

Y-akseli

- lähtijöiden määrä

Tasainen kuvaaja kertoo hyvästä lähtökaaviosta.

---

# 7.11 Optimointinäkymä

Näyttää optimoinnin tulokset.

Esimerkki

```
Lähtökaavio

Laatupisteet

92 / 100
```

Lisäksi näytetään

- tehdyt muutokset
- ratkaistut konfliktit
- jäljellä olevat huomautukset

---

# 7.12 Historia

Historia näyttää kaikki muutokset.

| Aika  | Toiminto      |
| ----- | ------------- |
| 18:22 | H21 siirretty |
| 18:24 | D21 lukittu   |
| 18:30 | Optimointi    |

Historia mahdollistaa myöhemmin Undo- ja Redo-toiminnot.

---

# 7.13 Asetukset

Käyttäjä voi muuttaa esimerkiksi:

- lähtöväli
- sarjojen välinen tauko
- optimointialgoritmi
- värit
- kieli

Asetukset tallennetaan kilpailuprojektiin.

---

# 7.14 Tilarivi

Tilarivi näyttää esimerkiksi:

```
Sarjoja

24

Kilpailijoita

814

Ratoja

12

Ensimmäisiä rasteja

8

Laatupisteet

94 / 100
```

---

# 7.15 Varoitukset

Ohjelma näyttää varoitukset omassa paneelissaan.

Esimerkkejä:

⚠ Sama ensimmäinen rasti samalla minuutilla

⚠ Lukittu sarja estää optimoinnin

⚠ Sarjalta puuttuu rata

⚠ Kilpailijalta puuttuu lähtöaika

Varoitukset voidaan suodattaa vakavuuden mukaan.

---

# 7.16 Vedä ja pudota

Lähtökaaviossa voidaan käyttää Drag & Drop -toimintoa.

Mahdolliset kohteet:

- kilpailija
- sarja
- tauko

Ohjelma tarkistaa sääntöjen toteutumisen ennen muutoksen hyväksymistä.

---

# 7.17 Työnkulku

Tyypillinen käyttö:

1. Luo uusi kilpailuprojekti (.spc)
2. Tuo ratatiedot Condesista
3. Tuo ilmoittautuneet IRMAsta tai eResultsista
4. Tarkista sarjat ja radat
5. Muodosta lähtökaavio
6. Tarkastele laatupisteitä ja varoituksia
7. Tee tarvittavat manuaaliset muutokset
8. Lukitse valmiit sarjat tai lähdöt
9. Lisää mahdolliset jälki-ilmoittautuneet
10. Vie valmis lähtökaavio Exceliin, PDF:ään tai tulospalveluun

---

# 7.18 Käyttöliittymän suunnitteluperiaatteet

- Kaikki tärkeimmät toiminnot ovat saavutettavissa enintään kahdella klikkauksella.
- Käyttäjä näkee aina, mitä tietoa parhaillaan käsitellään.
- Ohjelma ei tee peruuttamattomia muutoksia ilman vahvistusta.
- Kaikista virheistä annetaan selkeä ja ymmärrettävä ilmoitus.
- Käyttöliittymän tulee toimia myös suurilla kilpailuilla (yli 1000 kilpailijaa) ilman havaittavaa hidastumista.
