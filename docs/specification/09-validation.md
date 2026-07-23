# 9 Validointi ja lajisäännöt

## 9.1 Johdanto

Validoinnin tarkoituksena on varmistaa, että kilpailun tiedot ja muodostettu lähtökaavio ovat teknisesti oikeita sekä Suomen Suunnistusliiton lajisääntöjen mukaisia.

Validointi suoritetaan:

- aineiston tuonnin jälkeen
- ennen lähtökaavion muodostamista
- optimoinnin jälkeen
- ennen vientiä
- käyttäjän pyynnöstä

Kaikki havaitut ongelmat näytetään käyttäjälle.

---

# 9.2 Validointitasot

Validointi jakautuu neljään tasoon.

## Taso 1 – Datan eheys

Tarkistetaan että:

- kilpailulla on nimi
- kilpailulla on lähtöaika
- jokaisella sarjalla on rata
- jokaisella radalla on vähintään yksi rasti
- jokainen kilpailija kuuluu sarjaan

---

## Taso 2 – Lähtökaavion eheys

Tarkistetaan että:

- jokaisella kilpailijalla on lähtöaika
- lähtöajat ovat yksikäsitteisiä
- lähtöjärjestys on looginen
- kaikki kilpailijat ovat mukana

---

## Taso 3 – Lajisäännöt

Tarkistetaan esimerkiksi:

- saman radan sarjoja ei ole lomitettu
- lähtöväli toteutuu
- sama ensimmäinen rasti ei kuormitu liikaa
- lähtöajat ovat oikeassa järjestyksessä

---

## Taso 4 – Suositukset

Esimerkiksi:

- kilpailijavirta on tasainen
- sarjojen välinen tauko on riittävä
- nopeammat sarjat lähtevät ennen hitaampia

Näiden rikkominen ei estä vientiä.

---

# 9.3 Virheluokat

Kaikki löydökset luokitellaan.

## Virhe

Estää lähtökaavion hyväksymisen.

Esimerkkejä:

- puuttuva rata
- puuttuva lähtöaika
- kaksi kilpailijaa samalla minuutilla samalle ensimmäiselle rastille
- lähtöväli liian lyhyt

---

## Varoitus

Lähtökaavio voidaan hyväksyä.

Esimerkkejä:

- kilpailijavirta epätasainen
- pitkä tauko sarjojen välillä
- erittäin pieni sarja suuren sarjan välissä

---

## Huomautus

Informatiivinen ilmoitus.

Esimerkkejä:

- sarjassa vain yksi kilpailija
- rataa käyttää vain yksi sarja
- kilpailijalla ei ole Emit-numeroa

---

# 9.4 Validointisäännöt

## Kilpailu

- kilpailun nimi on annettu
- kilpailupäivä on asetettu
- ensimmäinen lähtöaika on asetettu

---

## Sarja

- nimi on yksilöllinen
- rata on määritelty
- lähtöväli on positiivinen

---

## Rata

- rastiluettelo ei ole tyhjä
- ensimmäinen rasti löytyy
- rastit ovat yksilöllisessä järjestyksessä

---

## Kilpailija

- nimi on annettu
- kuuluu sarjaan
- lähtöaika löytyy

---

# 9.5 Lähtövälin tarkistus

Samassa sarjassa tarkistetaan:

```
lähtöaika(n+1) − lähtöaika(n)
```

Erotuksen tulee olla vähintään sarjan lähtöväli.

Oletusarvo:

```
2 minuuttia
```

---

# 9.6 Ensimmäisen rastin tarkistus

Kaikki kilpailijat ryhmitellään ensimmäisen rastin mukaan.

Jokaiselle minuutille lasketaan lähtijöiden määrä.

Esimerkki:

| Aika  | Rasti 31 |
| ----- | -------: |
| 12:00 |        1 |
| 12:01 |        1 |
| 12:02 |        1 |

Jos samalla minuutilla lähtee useampi kilpailija samalle ensimmäiselle rastille, muodostuu virhe.

---

# 9.7 Radan tarkistus

Tarkistetaan että:

- samalla radalla olevat sarjat ovat yhtenäisinä jaksoina
- sarjat eivät lomitu
- radan käyttö on jatkuvaa

---

# 9.8 Lukitusten tarkistus

Varmistetaan että:

- lukittuja kilpailijoita ei ole siirretty
- lukittuja sarjoja ei ole muutettu
- lukitut aikajaksot ovat ennallaan

Lukituksen rikkominen on aina virhe.

---

# 9.9 Optimoinnin jälkeinen validointi

Optimoinnin jälkeen suoritetaan täydellinen validointi.

Jos pakollinen sääntö rikkoutuu:

- optimointi perutaan
- käyttäjälle näytetään virheilmoitus
- alkuperäinen lähtökaavio säilytetään

---

# 9.10 Validointiraportti

Validoinnin tuloksena muodostetaan raportti.

Raportti sisältää:

- virheet
- varoitukset
- huomautukset
- yhteenvetotiedot

Esimerkki:

```
Virheitä:
0

Varoituksia:
2

Huomautuksia:
5

Laatupisteet:
96 / 100
```

---

# 9.11 Automaattiset korjaukset

Ohjelma voi ehdottaa automaattisia korjauksia.

Esimerkiksi:

- siirrä sarjaa kaksi minuuttia myöhemmäksi
- lisää puuttuva tauko
- korjaa ensimmäisen rastin konflikti
- lisää puuttuva lähtöaika

Käyttäjä hyväksyy korjaukset erikseen.

---

# 9.12 Validoinnin laajennettavuus

Jokainen validointisääntö toteutetaan omana luokkanaan.

Esimerkki:

```python
class ValidationRule:

    id: str

    name: str

    severity: Severity

    def validate(self, competition):
        ...
```

ValidationService suorittaa kaikki rekisteröidyt säännöt.

Uusia sääntöjä voidaan lisätä ilman muutoksia olemassa olevaan koodiin.

---

# 9.13 Suunnitteluperiaatteet

Validointi noudattaa seuraavia periaatteita:

- Sääntöjen tarkistus on nopeaa ja determinististä.
- Kaikki tarkistukset voidaan suorittaa automaattisesti.
- Käyttäjä saa aina selkeän selityksen ongelmasta.
- Vakavat virheet estävät viennin.
- Varoitukset eivät estä käyttöä.
- Validointi on helposti laajennettavissa uusille kilpailumuodoille ja tuleville lajisääntömuutoksille.