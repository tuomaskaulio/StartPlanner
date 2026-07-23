# 13 Historia

## 13.1 Johdanto

Historia on StartPlannerin mekanismi, jolla kaikki kilpailuprojektiin tehdyt muutokset säilytetään.

Historia mahdollistaa:

- Undo
- Redo
- audit trail -seurannan
- muutosten vertailun

Historia tallennetaan projektitiedostoon (`.spc`), jotta työ voidaan palauttaa myöhemmin samaan tilaan.

---

# 13.2 Tavoitteet

Historian tavoitteet ovat:

- käyttäjä voi peruuttaa virheellisen muutoksen
- kilpailunjärjestäjä näkee, mitä on muutettu ja milloin
- optimointi ja manuaaliset muutokset ovat jäljitettävissä
- eri lähtökaavioversioita voidaan vertailla
- historia ei hidasta normaalia käyttöä merkittävästi

---

# 13.3 Historiatietue

Jokainen muutos muodostaa historiatietueen.

Tallennettavat kentät:

| Kenttä        | Selite                          |
| ------------- | ------------------------------- |
| id            | Tietueen tunniste               |
| timestamp     | Aikaleima                       |
| action        | Toiminnon tyyppi                |
| target_type   | Kohteen tyyppi (sarja, kilpailija, …) |
| target_id     | Kohteen tunniste                |
| old_value     | Edellinen arvo                  |
| new_value     | Uusi arvo                       |
| user          | Käyttäjä (jos tiedossa)         |
| source        | Manuaalinen / optimointi / tuonti |
| description   | Ihmisen luettava selite         |

Esimerkki:

```
18:32  H21 siirretty 12:10 → 12:12  (manuaalinen)
18:34  Optimointi suoritettu         (BalancedOptimizer)
18:36  D20 lukittu                   (manuaalinen)
```

---

# 13.4 Undo

Undo peruuttaa viimeisimmän muutoksen.

Säännöt:

- Undo palauttaa Domain-tilan edelliseen snapshotiin tai käänteiseen operaatioon.
- Lukituksia ei rikota Undo-operaatiolla ilman erillistä vahvistusta.
- Undo itse kirjataan historiaan, jotta Redo on mahdollista.
- Jos muutosta ei voida peruuttaa turvallisesti, käyttäjälle näytetään selitys.

Tyypillisiä Undo-kohteita:

- kilpailijan siirto
- sarjan siirto
- lukituksen asetus/poisto
- optimoinnin tulos
- jälki-ilmoittautuneen lisäys

---

# 13.5 Redo

Redo palauttaa Undo:lla peruutetun muutoksen.

Säännöt:

- Redo on käytettävissä vain, jos Undo-pino ei ole tyhjä.
- Uusi manuaalinen muutos tyhjentää Redo-pinon.
- Redo tuottaa saman lopputilan kuin alkuperäinen muutos.
- Operaatio on deterministinen.

Käyttöliittymässä Undo ja Redo ovat aina näkyvissä, mutta pois käytöstä kun pino on tyhjä.

---

# 13.6 Audit trail

Audit trail on historian pitkäaikainen jälki.

Se säilyttää:

- kaikki merkittävät muutokset
- optimoinnit
- tuonnit ja viennit
- lukitukset
- validointiajot (valinnainen)
- julkaistut versiot

Audit trail ei ole sama asia kuin Undo-pino.

| Ominaisuus   | Undo/Redo      | Audit trail        |
| ------------ | -------------- | ------------------ |
| Tarkoitus    | Nopea peruutus | Jäljitettävyys     |
| Elinkaari    | Istunto/projekti | Pitkäaikainen    |
| Muokattavuus | Pinorakenne    | Liitevain lukeminen |
| Käyttö       | Työskentely    | Tarkastus / raportti |

Audit trailia ei normaalisti siivota automaattisesti.

Käyttäjä voi tarvittaessa rajata näkymää suodattimilla.

---

# 13.7 Muutosten vertailu

Historia tukee kahden tilan vertailua.

Vertailtavia kohteita:

- kaksi historiapistettä
- kaksi lähtökaavioversiota
- ennen optimointia / jälkeen optimoinnin
- ennen jälki-ilmoittautuneita / jälkeen

Vertailun tulos näyttää esimerkiksi:

- siirtyneet kilpailijat
- muuttuneet lähtöajat
- lisätyt ja poistetut lukitukset
- muuttuneet laatupisteet
- validointierot

Esimerkki:

```
Versio 1 → Versio 2

Siirrettyjä kilpailijoita: 14
Muuttuneita sarjoja: 3
Laatupisteet: 88 → 96
```

Vertailu on vain luku -toiminto: se ei muuta projektia.

---

# 13.8 Snapshotit ja versiot

Suuret muutokset voivat luoda snapshotin.

Esimerkkejä:

- automaattinen ensimmäinen ehdotus
- optimoinnin jälkeen
- ennen julkaisua
- käyttäjän nimeämä versio

Snapshotit liittyvät projektitiedoston tulevaisuuden moniversiotukeen (ks. luku 11).

Ensimmäisessä versiossa riittää lineaarinen historia + Undo/Redo.

Snapshot-vertailu voidaan lisätä ilman Domain-mallin muutosta.

---

# 13.9 Tallennus

Historia tallennetaan `.spc`-tiedoston `history`-tauluun.

Tallennusperiaatteet:

- jokainen hyväksytty muutos kirjoitetaan samaan transaktioon Domain-päivityksen kanssa
- historia ei saa jäädä epäsynkroniin Domain-tilan kanssa
- suurissa kilpailuissa vanhat Undo-askeleet voidaan tiivistää, mutta audit trail säilyy

---

# 13.10 Suorituskyky

Historia ei saa hidastaa normaalia muokkausta.

Tavoitteet:

| Toiminto                | Maksimiaika |
| ----------------------- | ----------: |
| Yhden muutoksen kirjaus |       50 ms |
| Undo                    |      100 ms |
| Redo                    |      100 ms |
| Historialistan avaus    |      300 ms |
| Kahden version vertailu |        1 s |

Large-testiaineistolla (≈ 1200 kilpailijaa).

---

# 13.11 Käyttöliittymä

Historia-näkymä näyttää aikajärjestyksessä:

- aikaleiman
- kuvauksen
- lähteen
- mahdollisuuden hypätä tietueeseen

Käyttäjä voi:

- suodattaa toiminnon mukaan
- hakea sarjaa tai kilpailijaa
- avata vertailun kahden rivin välillä
- palauttaa valitun snapshotin (myöhemmässä versiossa)

---

# 13.12 Suunnitteluperiaatteet

- Jokainen käyttäjän tekemä muutos on jäljitettävissä.
- Undo/Redo on nopea ja turvallinen.
- Audit trail on pysyvä.
- Vertailu auttaa ymmärtämään muutosten vaikutuksen.
- Historia tallennetaan projektiin, ei erilliseen lokitiedostoon.
- Historian epäonnistuminen ei saa hävittää Domain-dataa.
