# 3 Lähtökaavion muodostaminen

## 3.1 Johdanto

Lähtökaavio (`ClassStartPlan`) on StartPlannerin tärkein toiminto.

Se tuottaa **yhden lähdön** (`StartLocation`) sarjoille ensimmäiset lähtöajat huomioiden:

- lajisäännöt (saman lähdön sisällä)
- ratojen käyttö
- ensimmäiset rastit (lähdöittäin)
- kilpailijavirran tasaisuus (sarjatasolla)
- käyttäjän tekemät lukitukset

Suunnittelu tehdään **lähdöittäin**. Eri lähdöt eivät jaa aikajanaa.

Algoritmi ei pyri löytämään matemaattisesti optimaalista ratkaisua, vaan käytännössä hyvin toimivan kaavion.

Lopullinen päätös on aina käyttäjällä.

Kilpailijakohtainen lähtölista ei ole tämän luvun tavoite (ks. jatkokehitys / tulospalvelu).

---

# 3.2 Syötetiedot

Lähtökaavion muodostamiseen tarvitaan vähintään seuraavat tiedot.

## Kilpailu ja lähtö

- kilpailun nimi
- käsiteltävä `StartLocation`
- lähdön aikajanan alku (ensimmäinen mahdollinen lähtöaika)

## Sarjat (kyseisessä lähdössä)

- sarjan nimi
- rata
- kilpailijamäärä
- lähtöväli
- `start_location_id`

## Radat

- ensimmäinen rasti
- pituus
- nousu

Ilmoittautuneet tarvitaan kilpailijamääriin; yksittäisiä lähtöaikoja ei vaadita.
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

Jos **samassa lähdössä** samalla radalla kilpailee useita sarjoja, niiden aikajaksoja ei saa lomittaa kaaviossa.

Esimerkki (lähtökaavio)

```
H21  12:00   (58 hlö, 2 min → kestää ~1 h 54 min)

D21  14:00
```

Ei sallittu: saman radan sarjojen päällekkäiset aikavälit samassa lähdössä.

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

Tämä on ohjelman tärkein sääntö **yhden lähdön sisällä**.

Jos samassa lähdössä usealla radalla on sama ensimmäinen rasti,
kyseiselle rastille saa lähteä korkeintaan

```
1 kilpailija / minuutti
```

Kaavion tasolla tämä tarkoittaa, etteivät eri sarjojen peittävät minuuttislotit
saa tuottaa kahta lähtijää samalle rastille samaan minuuttiin.

Esimerkki (sallittu, sama lähtö)

```
12:00 H21 (1. rasti 31)
12:01 D21 (1. rasti 31)
```

Ei sallittu (sama lähtö, sama minuutti, sama 1. rasti)

```
12:00 H21
12:00 D21
```

**Eri lähdöt:** sama 1. rasti samaan minuuttiin on sallittu, koska lähdöt ovat itsenäisiä.
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

Ohjelman tavoitteena on pitää lähtevien kilpailijoiden määrä mahdollisimman tasaisena **lähdön sisällä**.

Arvio tehdään **sarjatasolla**: kullakin minuutilla lähtijöitä ≈ 1 / lähtöväli niille sarjoille, joiden kaavio peittää kyseisen minuutin.

Tätä kutsutaan kilpailijavirran optimoinniksi. Se ei edellytä kilpailijakohtaista lähtölistaa.
---

# 3.10 Rajoitteiden prioriteetti

Kaikki säännöt eivät ole yhtä tärkeitä.

Ohjelma käyttää seuraavaa prioriteettia.

## Pakolliset

Näitä ei saa koskaan rikkoa **käsiteltävässä lähdössä**.

- lukitukset
- sama rata ei limittäin (saman lähdön sisällä)
- sama ensimmäinen rasti (saman lähdön sisällä)
- lähtöväli (sarjan sisäinen, kaavion kestossa)
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

- sarja
- aikajakso (lähdön sisällä)
- kokonainen rata (lähdön kontekstissa)

Optimizer ei saa muuttaa lukittua kohdetta.

---

# 3.12 Jälki-ilmoittautuneet

Kun sarjaan tulee uusia kilpailijoita, kaavion tasolla päivitetään kilpailijamäärä (ja tarvittaessa kestovaraus).

Koko lähdön kaaviota ei muodosteta turhaan uudelleen, jos pieni siirto riittää.

Yksittäisen kilpailijan paikan arpominen kuuluu tulospalveluun tai tulevaan lähtölista-ominaisuuteen.

---

# 3.13 Algoritmin vaiheet

Lähtökaavio muodostetaan **yhdelle lähdölle** seuraavasti.

## Vaihe 1

Valitse `StartLocation` ja lue sen sarjat.

## Vaihe 2

Ryhmittele sarjat radoittain (lähdön sisällä).

## Vaihe 3

Laske ensimmäiset rastit.

## Vaihe 4

Järjestä sarjat (käyttäjä / nopeus / pituus).

## Vaihe 5

Sijoita sarjat aikajanalle (`ClassStart.first_start_time`).

## Vaihe 6

Tarkista ensimmäisen rastin kuormitus (vain tämä lähtö).

## Vaihe 7

Korjaa ristiriidat siirtämällä kokonaisia sarjoja.

## Vaihe 8

Tasaa kilpailijavirtaa sarjatasolla.

## Vaihe 9

Tarkista lukitukset.

## Vaihe 10

Palauta `ClassStartPlan`.

---

# 3.14 Optimointitavoite

Hyvä lähtökaavio täyttää seuraavat ehdot.

✓ Lajisäännöt toteutuvat käsiteltävässä lähdössä.

✓ Sarjat ovat loogisessa järjestyksessä.

✓ Samalle radalle lähtevät sarjat ovat peräkkäin (eivät limittäin).

✓ Ensimmäiselle rastille ei muodostu ruuhkaa **tässä lähdössä**.

✓ Kilpailijavirta on tasainen (sarja-arvio).

✓ Käyttäjän tekemät lukitukset säilyvät.

---

# 3.15 Käyttäjän rooli

StartPlanner tekee aina ehdotuksen valitulle lähdölle.

Käyttäjä voi:

- hyväksyä ehdotuksen sellaisenaan
- siirtää kokonaisia sarjoja (muuttaa ensimmäistä lähtöaikaa)
- lisätä taukoja
- lukita sarjoja tai aikajaksoja
- suorittaa optimoinnin uudelleen
- vaihtaa käsiteltävää lähtöä

Ohjelma ei koskaan estä käyttäjää tekemästä perusteltuja manuaalisia muutoksia, mutta se varoittaa, jos muutos rikkoo pakollisia sääntöjä.