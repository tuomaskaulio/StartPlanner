# 1 Johdanto

## 1.1 Projektin tarkoitus

StartPlanner on avoimen lähdekoodin työpöytäsovellus suunnistuskilpailujen lähtökaavioiden suunnitteluun.

Ohjelman tavoitteena on automatisoida kilpailujen lähtöaikojen suunnittelu siten, että:

- Suomen Suunnistusliiton lajisääntöjä noudatetaan
- ratakohtaiset rajoitteet huomioidaan
- ensimmäisten rastien kuormitus tasataan
- kilpailijoiden lähtövirta pysyy mahdollisimman tasaisena
- jälki-ilmoittautuneet voidaan lisätä mahdollisimman pienillä muutoksilla olemassa olevaan lähtökaavioon.

Ohjelma ei ole tulospalveluohjelma eikä ratamestariohjelma.

StartPlanner toimii niiden rinnalla.

---

# 1.2 Tavoitteet

Projektin päätavoitteena on tehdä lähtökaavion laatimisesta:

- nopeampaa
- helpompaa
- virheettömämpää
- helposti muokattavaa

Tavoitteena ei ole tehdä täydellistä optimointia hinnalla millä hyvänsä.

Käyttäjän tulee aina voida muuttaa ohjelman ehdotusta.

---

# 1.3 Kohderyhmä

Ohjelman käyttäjiä ovat esimerkiksi

- kilpailunjohtaja
- ratamestari
- tulospalvelu
- kilpailusihteeri
- lähtöpäällikkö

Ohjelman käyttö ei edellytä ohjelmointiosaamista.

---

# 1.4 Suunnitteluperiaatteet

Projektissa noudatetaan seuraavia periaatteita.

## Avoin lähdekoodi

Koko projekti julkaistaan avoimena lähdekoodina.

Kaikki kehitys tapahtuu GitHubissa.

---

## Monialustaisuus

Ohjelman tulee toimia samalla koodilla

- Windowsissa
- Linuxissa
- macOS:ssa

Käyttöliittymä toteutetaan PySide6-kirjastolla.

---

## Ei toimittajalukkoa

Ohjelmaa ei sidota yhteen tulospalveluohjelmaan.

Kaikki tiedonsiirto tehdään importtereilla ja exporttereilla.

---

## Modulaarisuus

Kaikki tiedostomuodot toteutetaan omissa moduuleissaan.

Esimerkiksi

- Condes
- IRMA
- eResults

ovat toisistaan riippumattomia.

---

## Laajennettavuus

Myöhemmin voidaan lisätä uusia

- importtereita
- exporttereita
- optimointialgoritmeja
- raportteja

ilman että muu ohjelma muuttuu.

---

# 1.5 Projektin rajaus

StartPlanner EI sisällä

- ajanottoa
- emit-lukua
- tuloslaskentaa
- rastien suunnittelua
- karttojen piirtämistä

Nämä kuuluvat muihin ohjelmiin.

StartPlanner keskittyy lähtökaavioon.

---

# 1.6 Käyttöprosessi

Tyypillinen työnkulku on

1. Luodaan kilpailu.
2. Luetaan ratatiedot Condesista.
3. Luetaan ilmoittautuneet IRMAsta tai eResultsista.
4. Ohjelma muodostaa lähtökaavion.
5. Käyttäjä tarkistaa ehdotuksen.
6. Käyttäjä tekee tarvittavat muutokset.
7. Lähtökaavio lukitaan.
8. Mahdolliset jälki-ilmoittautuneet lisätään.
9. Lopullinen lähtökaavio viedään tulospalveluun tai Exceliin.

---

# 1.7 Projektin päätavoitteet

Projektin aikana rakennetaan seuraavat kokonaisuudet.

## Data Explorer

Kilpailun tietojen tarkastelu.

Sisältää

- sarjat
- radat
- kilpailijat
- ensimmäiset rastit
- yhteenvetotiedot

---

## Scheduler

Lähtökaavion muodostaminen.

Huomioi

- rata
- ensimmäinen rasti
- lähtövälit
- sarjaryhmät

---

## Optimizer

Parantaa automaattisesti lähtökaaviota.

Tavoitteena on tasainen kilpailijavirta.

---

## Manual Editor

Käyttäjä voi

- siirtää sarjoja
- siirtää yksittäisiä kilpailijoita
- lukita lähtöjä
- lisätä taukoja

---

## History

Kaikista muutoksista jää historia.

Esimerkiksi

- lähtöajan muutos
- lukitus
- jälki-ilmoittautuneen lisäys

Historia mahdollistaa muutosten seuraamisen ja tarvittaessa peruuttamisen.

---

# 1.8 Kehitysperiaatteet

Projektissa noudatetaan seuraavia ohjelmistokehityksen periaatteita.

- Selkeä arkkitehtuuri.
- Domain Driven Design -ajattelu.
- Pienet ja helposti testattavat luokat.
- Type hintit kaikkialla.
- Yksikkötestit kaikille ydinkomponenteille.
- Dokumentaatio päivitetään aina koodimuutosten yhteydessä.
- Koodi kirjoitetaan tuotantokelpoisena alusta alkaen.

---

# 1.9 Tiekartta

Ensimmäiset julkaisut etenevät seuraavasti.

v0.1
- kilpailun tietomalli
- Condes-luku
- Data Explorer

v0.2
- IRMA ILMOIT -luku + IOF CourseData
- ensimmäinen automaattinen lähtökaavio
- Excel/CSV-vienti ja `.spc`

v0.3
- optimointi
- lukitukset
- historia

v0.4
- käyttöliittymän viimeistely

v1.0
- ensimmäinen tuotantoversio
