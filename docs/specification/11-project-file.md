# 11 Projektitiedosto (.spc)

## 11.1 Johdanto

StartPlanner käyttää omaa projektitiedostoaan.

Projektitiedoston tiedostopääte on:

```
.spc
```

Projektitiedosto sisältää kaiken kilpailuun liittyvän tiedon.

Esimerkki:

```
SM2028.spc
```

Käyttäjän näkökulmasta kyseessä on yksi tiedosto.

Sisäisesti tiedosto on SQLite-tietokanta.

---

# 11.2 Tavoitteet

Projektitiedoston tavoitteet ovat:

- yksi tiedosto kilpailua kohden
- nopea tallennus
- turvallinen tallennus
- historian säilyminen
- Undo / Redo
- versionhallinta
- yhteensopivuus tulevien ohjelmaversioiden kanssa

---

# 11.3 Tallennettavat tiedot

Projektiin tallennetaan kaikki käyttäjän työ.

Esimerkiksi:

- kilpailun perustiedot
- sarjat
- radat
- kilpailijat
- lähtökaavio
- käyttäjän tekemät muutokset
- lukitukset
- asetukset
- historia
- validointitulokset

Projektin avaaminen palauttaa täsmälleen saman tilanteen, jossa työ tallennettiin.

---

# 11.4 Tietokantarakenne

Projektitiedosto sisältää seuraavat päätaulut.

```
competition

classes

courses

course_controls

competitors

starts

locks

settings

history

validation_results

metadata
```

Myöhemmin voidaan lisätä uusia tauluja ilman, että vanhat projektit rikkoutuvat.

---

# 11.5 Metadata

Metadata sisältää projektin perustiedot.

Esimerkiksi:

| Kenttä              | Selite                |
| ------------------- | --------------------- |
| project_version     | Projektimuodon versio |
| application_version | StartPlannerin versio |
| created             | Luontiaika            |
| modified            | Viimeisin muokkaus    |
| author              | Projektin tekijä      |
| uuid                | Projektin tunniste    |

UUID:n avulla voidaan tunnistaa sama projekti eri tietokoneilla.

---

# 11.6 Kilpailun tiedot

Kilpailutaulu sisältää esimerkiksi:

- kilpailun nimi
- päivämäärä
- järjestäjä
- kilpailukeskus
- ensimmäinen lähtö
- viimeinen lähtö
- huomautukset

Kilpailun tietoja voidaan päivittää ohjelman käytön aikana.

---

# 11.7 Sarjat

Sarjataulu sisältää:

- tunniste
- nimi
- rata
- lähtöväli
- arvioitu nopeus
- järjestys
- lukittu

---

# 11.8 Radat

Ratataulu sisältää:

- nimi
- pituus
- nousu
- ensimmäinen rasti
- rastiluettelo

Rastit tallennetaan omaan tauluunsa.

---

# 11.9 Kilpailijat

Kilpailijataulu sisältää esimerkiksi:

- nimi
- seura
- sarja
- Emit-numero
- lähtöaika
- lähtönumero
- tila

Kilpailijan tunniste säilyy koko projektin ajan.

---

# 11.10 Lukitukset

Lukitukset tallennetaan omaan tauluunsa.

Lukittavia kohteita ovat:

- kilpailija
- sarja
- aikajakso

Lukitukselle tallennetaan myös:

- käyttäjä
- aikaleima
- syy (valinnainen)

---

# 11.11 Historia

Kaikki muutokset tallennetaan historiaan.

Esimerkiksi:

| Aika  | Tapahtuma     |
| ----- | ------------- |
| 18:32 | H21 siirretty |
| 18:34 | Optimointi    |
| 18:36 | D20 lukittu   |

Historia mahdollistaa myöhemmin Undo- ja Redo-toiminnot.

---

# 11.12 Validointitulokset

Viimeisin validointi tallennetaan projektiin.

Tallennetaan esimerkiksi:

- virheet
- varoitukset
- huomautukset
- laatupisteet
- validointiaika

Näin projekti voidaan avata myöhemmin ilman uutta validointia.

---

# 11.13 Asetukset

Projektiin tallennetaan kilpailukohtaiset asetukset.

Esimerkiksi:

- lähtöväli
- sarjojen välinen tauko
- optimointialgoritmi
- värit
- raporttiasetukset

Käyttäjän yleiset asetukset tallennetaan erikseen.

---

# 11.14 Tallennus

Tallennus suoritetaan transaktiona.

Vaiheet:

1. Aloita transaktio
2. Päivitä muuttuneet tiedot
3. Tarkista eheys
4. Commit

Virhetilanteessa suoritetaan Rollback.

Projekti ei koskaan jää osittain tallennetuksi.

---

# 11.15 Varmuuskopiointi

Ennen ensimmäistä tallennusta voidaan luoda automaattinen varmuuskopio.

Esimerkki:

```
SM2028.spc

↓

SM2028_backup_2028-05-16_1830.spc
```

Automaattisten varmuuskopioiden määrä on käyttäjän määritettävissä.

---

# 11.16 Projektin päivitys

Kun vanha projekti avataan uudemmalla ohjelmaversiolla:

1. Projektin versio tarkistetaan.
2. Tarvittavat tietokantamuutokset suoritetaan.
3. Projekti päivitetään automaattisesti.

Alkuperäinen projekti säilytetään varmuuskopiona.

---

# 11.17 Tietoturva

Projektitiedosto ei sisällä suoritettavaa koodia.

Kaikki syötetiedot validoidaan ennen tallennusta.

SQLite-tietokantaa käytetään vain paikallisesti.

Ohjelma ei lähetä kilpailutietoja internetiin ilman käyttäjän erillistä toimintoa.

---

# 11.18 Tiedoston eheys

Projektin yhteydessä voidaan tallentaa tarkistussumma.

Projektia avattaessa tarkistetaan:

- tietokannan eheys
- taulurakenne
- pakolliset kentät
- mahdolliset vauriot

Jos virheitä havaitaan, käyttäjälle tarjotaan mahdollisuus avata projekti vain luku -tilassa.

---

# 11.19 Tulevaisuuden laajennukset

Projektimuodon tulee mahdollistaa:

- useita lähtökaavioita samassa projektissa
- eri optimointiversioiden tallennus
- useita käyttäjiä
- pilvitallennus
- digitaalinen allekirjoitus
- liitetiedostot (esim. kilpailuohje PDF)

Näiden ominaisuuksien lisääminen ei saa rikkoa olemassa olevia projektitiedostoja.

---

# 11.20 Suunnitteluperiaatteet

Projektitiedoston suunnittelussa noudatetaan seuraavia periaatteita:

- Yksi kilpailu = yksi projektitiedosto.
- Tallennus on atominen ja turvallinen.
- Kaikki käyttäjän tekemät muutokset voidaan säilyttää.
- Projektimuoto on laajennettava.
- Vanhat projektit ovat avattavissa myös uusilla ohjelmaversioilla.
- Käyttäjän ei tarvitse tietää projektitiedoston sisäisestä rakenteesta.