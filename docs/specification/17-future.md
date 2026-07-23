# 17 Tulevaisuuden kehitys

## 17.1 Johdanto

Tämä luku kuvaa ominaisuuksia, joita ei vaadita v1.0:aan, mutta joihin arkkitehtuuri varautuu.

Tavoite on pitää ovi auki ilman, että nykyinen ydin monimutkaistuu ennenaikaisesti.

Kaikki tässä luvussa mainitut ominaisuudet edellyttävät erillistä suunnittelua ennen toteutusta.

---

# 17.2 Viestit

Viestikilpailuissa lähtökaavio liittyy vaihtoihin, osuuksiin ja joukkueisiin.

Tarvittavia laajennuksia:

- joukkue- ja osuusmalli Domainiin
- vaihtoalueen aikataulutus
- osuuskohtaiset radat
- joukkueiden lukitukset
- viestikohtaiset validointisäännöt

v1 Domain ei mallinna viestejä täysin, mutta kilpailija/sarja/rata-abstraktiot pidetään laajennettavina.

---

# 17.3 Sprintit

Sprintissä lähtöväli voi olla lyhyempi ja ensimmäisen rastin kuormitus kriittisempi.

Tarvittavia laajennuksia:

- alle 1 minuutin lähtövälit (tarvittaessa sekuntitarkkuus)
- tiukempi first-control-kapasiteetti
- sprinttikohtaiset laatukriteerit
- nopea uudelleenoptimointi myöhäisille ilmoittautumisille

Aikaleuvojen sisäinen esitys suunnitellaan siten, että sekunnit voidaan ottaa käyttöön ilman tietomallin uudelleenkirjoitusta.

---

# 17.4 Useita lähtöpaikkoja

Suurissa kilpailuissa voi olla useita fyysisiä lähtöpaikkoja.

Tarvittavia laajennuksia:

- `StartLocation`-entiteetti
- sarjan tai radan kytkentä lähtöpaikkaan
- lähtöpaikkakohtainen kapasiteetti
- raportit lähtöpaikoittain
- validointi: kilpailija/sarja oikeassa paikassa

Lähtökaavion ydin algoritmi säilyy: sijainti on lisärajoite, ei erillinen tuote.

---

# 17.5 Pilvitallennus

Paikallinen `.spc`-tiedosto pysyy ensisijaisena.

Pilvitallennus olisi valinnainen lisäpalvelu:

- projektin synkronointi laitteiden välillä
- jaettu lukuoikeus järjestäjätiimille
- versionointi pilvessä
- konfliktienselvitys

Periaatteet:

- ei pakollista tiliä v1:ssä
- ei automaattista lähetystä ilman käyttäjän lupaa
- paikallinen kopio toimii aina offline

---

# 17.6 REST API

REST API mahdollistaisi integroinnin muihin järjestelmiin.

Mahdollisia käyttötapauksia:

- tuonti ulkoisesta ilmoittautumisjärjestelmästä
- lähtökaavion julkaisu tulospalveluun
- validointiraportin haku
- headless-optimointi palvelimella

API rakennettaisiin Service-kerroksen päälle, ei GUI:n päälle.

Ensimmäinen versio voisi olla vain luku (export/status).

---

# 17.7 Mobiilituki

Mobiilituki ei ole työpöytäsovelluksen korvaaja.

Mahdollisia käyttötapoja:

- lähtökaavion selaus puhelimella
- lukitusten ja huomautusten katselu maastossa
- ilmoitukset muutoksista
- kevyt hyväksyntä/julkaisu

Raskas muokkaus ja optimointi pysyvät työpöydällä.

Mobiili käyttäisi todennäköisesti samaa REST/pilvikerrosta.

---

# 17.8 Muut mahdolliset laajennukset

- digitaalinen allekirjoitus julkaistulle kaaviolle
- liitetiedostot projektiin (kilpailuohje PDF)
- monikieliset raportit
- yhteisöpluginit
- live-yhteys tulospalveluun
- saavutettavuusparannukset

Nämä priorisoidaan käyttäjäpalautteen mukaan v1.x / v2.0-vaiheessa.

---

# 17.9 Arkkitehtuurirajoitteet

Tulevat ominaisuudet eivät saa:

- rikkoa Domain-sääntöjä
- ohittaa validointia
- pakottaa verkkoa offline-käyttöön
- hajottaa `.spc`-yhteensopivuutta ilman migraatiota
- sekoittaa kilpailu-, käyttäjä- ja järjestelmäasetuksia

Jokainen merkittävä laajennus saa oman suunnitteludokumentin ennen toteutusta.

---

# 17.10 Suunnitteluperiaatteet

- v1 ratkaisee henkilökohtaisen metsäsunnistuksen lähtökaavion.
- v2 laajentaa muotoja ja kanavia.
- Laajennukset tulevat plugineina ja uusina Domain-entiteetteinä, ei erillisinä ohjelmina.
- Käyttäjän työ lokalilla koneella säilyy aina mahdollisena.
- Tulevaisuus suunnitellaan, mutta toteutetaan vasta kun tarve on todennettu.
