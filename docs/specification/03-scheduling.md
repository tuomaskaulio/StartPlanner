# 3 Lähtökaavion muodostaminen

## 3.1 Johdanto

Lähtökaavio on StartPlannerin tärkein toiminto.

Lähtökaavion muodostamisen tavoitteena on löytää mahdollisimman hyvä lähtöjärjestys huomioiden:

- lajisäännöt
- kilpailun erityispiirteet
- ratojen käyttö
- ensimmäiset rastit
- kilpailijavirran tasaisuus
- käyttäjän tekemät lukitukset

Algoritmi ei pyri löytämään matemaattisesti optimaalista ratkaisua, vaan käytännössä hyvin toimivan lähtökaavion.

Lopullinen päätös on aina käyttäjällä.

---

# 3.2 Syötetiedot

Lähtökaavion muodostamiseen tarvitaan vähintään seuraavat tiedot.

## Kilpailu

- kilpailun nimi
- ensimmäinen lähtö
- viimeinen lähtö (valinnainen)

## Sarjat

- sarjan nimi
- rata
- kilpailijamäärä

## Radat

- ensimmäinen rasti
- pituus
- nousu

## Kilpailijat

- sarja
- mahdolliset lukitukset

---

# 3.3 Lähtöväli

Jokaisella sarjalla on lähtöväli.

Oletusarvo on

```
2 minuuttia
```

Lähtövälin tulee olla käyttäjän muutettavissa.

Esimerkkejä

| Sarja      | Lähtöväli |
| ---------- | --------: |
| H21        |     2 min |
| D21        |     2 min |
| RR         |     1 min |
| Kuntosarja |     1 min |

---

# 3.4 Sarjat samalla radalla

Jos samalla radalla kilpailee useita sarjoja, niiden lähtöjä ei saa lomittaa.

Esimerkki

```
H21

12:00

12:02

12:04

12:06

D21

12:10

12:12

12:14
```

Ei sallittu

```
12:00 H21

12:02 D21

12:04 H21

12:06 D21
```

Syynä on kilpailun selkeys ja ratojen tasapuolinen käyttö.

---

# 3.5 Sarjojen välinen tauko

Sarjojen väliin voidaan jättää tauko.

Tauko voi olla

- 0 minuuttia
- 1 minuutti
- 2 minuuttia
- käyttäjän määrittelemä

Oletus

```
2 minuuttia
```

Tauon tarkoitus on erottaa sarjat toisistaan.

---

# 3.6 Sama ensimmäinen rasti

Tämä on ohjelman tärkein sääntö.

Jos usealla radalla on sama ensimmäinen rasti,

niin kyseiselle rastille saa lähteä korkeintaan

```
1 kilpailija / minuutti
```

Esimerkki

```
12:00 H21

12:01 D21

12:02 H20

12:03 D20
```

Kaikilla ensimmäinen rasti

```
31
```

Sallittu.

Ei sallittu

```
12:00 H21

12:00 D21
```

jos ensimmäinen rasti on sama.

---

# 3.7 Nopeiden sarjojen sijoittaminen

Lähtökaavio muodostetaan lähtökohtaisesti

nopeimmasta hitaimpaan.

Esimerkki

```
H21

D21

H20

D20

H18

D18

...

RR

TR
```

Perustelut

- kilpailun kärki saadaan maaliin aikaisemmin
- tulospalvelu saa tärkeimmät sarjat ensin
- TV- ja kuulutustarpeet

Käyttäjän tulee voida muuttaa järjestystä.

---

# 3.8 Sarjojen järjestys

Sarjajärjestys muodostuu seuraavista tekijöistä.

Ensisijaisesti

1. käyttäjän määräämä järjestys

Muuten

1. arvioitu nopeus
2. radan pituus
3. kilpailuaika

---

# 3.9 Tasainen kilpailijavirta

Ohjelman tavoitteena on pitää lähtevien kilpailijoiden määrä mahdollisimman tasaisena.

Esimerkki

Huono

```
12:00 14 kilpailijaa

12:01 1 kilpailija

12:02 0 kilpailijaa

12:03 9 kilpailijaa
```

Hyvä

```
12:00 5

12:01 5

12:02 5

12:03 5
```

Tätä kutsutaan kilpailijavirran optimoinniksi.

---

# 3.10 Rajoitteiden prioriteetti

Kaikki säännöt eivät ole yhtä tärkeitä.

Ohjelma käyttää seuraavaa prioriteettia.

## Pakolliset

Näitä ei saa koskaan rikkoa.

- lukitukset
- sama rata ei limittäin
- sama ensimmäinen rasti
- lähtöväli

---

## Tärkeät

Pyritään toteuttamaan aina.

- nopeammat ennen hitaampia
- tasainen kilpailijavirta

---

## Toivottavat

Jos mahdollista.

- sarjojen väliset tauot
- käyttäjän suosima järjestys

---

# 3.11 Lukitukset

Lukitukset estävät automaattiset muutokset.

Lukita voidaan

- kilpailija
- sarja
- aikajakso
- kokonainen rata

Optimizer ei saa muuttaa lukittua kohdetta.

---

# 3.12 Jälki-ilmoittautuneet

Kun kilpailuun tulee uusia kilpailijoita,

ohjelma ei saa muodostaa koko lähtökaaviota uudelleen.

Tavoitteena on tehdä mahdollisimman pieni muutos.

Optimoinnin tavoitteet

1. sijoita uusi kilpailija

2. siirrä mahdollisimman vähän muita

3. säilytä kaikki lukitukset

4. noudata lajisääntöjä

---

# 3.13 Algoritmin vaiheet

Lähtökaavio muodostetaan seuraavasti.

## Vaihe 1

Lue kilpailun tiedot.

## Vaihe 2

Ryhmittele sarjat radoittain.

## Vaihe 3

Laske ensimmäiset rastit.

## Vaihe 4

Järjestä sarjat nopeuden mukaan.

## Vaihe 5

Sijoita sarjat aikajanalle.

## Vaihe 6

Tarkista ensimmäisen rastin kuormitus.

## Vaihe 7

Korjaa mahdolliset ristiriidat.

## Vaihe 8

Optimoi kilpailijavirta.

## Vaihe 9

Tarkista lukitukset.

## Vaihe 10

Muodosta valmis lähtökaavio.

---

# 3.14 Optimointitavoite

Hyvä lähtökaavio täyttää seuraavat ehdot.

✓ Lajisäännöt toteutuvat.

✓ Sarjat ovat loogisessa järjestyksessä.

✓ Samalle radalle lähtevät sarjat ovat peräkkäin.

✓ Ensimmäiselle rastille ei muodostu ruuhkaa.

✓ Kilpailijavirta on tasainen.

✓ Jälki-ilmoittautuneet voidaan lisätä pienillä muutoksilla.

✓ Käyttäjän tekemät lukitukset säilyvät.

---

# 3.15 Käyttäjän rooli

StartPlanner tekee aina ehdotuksen.

Käyttäjä voi:

- hyväksyä ehdotuksen sellaisenaan
- muuttaa yksittäisiä lähtöjä
- siirtää kokonaisia sarjoja
- lisätä taukoja
- lukita lähtöjä
- suorittaa optimoinnin uudelleen

Ohjelma ei koskaan estä käyttäjää tekemästä perusteltuja manuaalisia muutoksia, mutta se varoittaa, jos muutos rikkoo pakollisia sääntöjä.
