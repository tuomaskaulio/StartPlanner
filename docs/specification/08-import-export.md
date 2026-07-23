# 8 Tiedostomuodot ja integraatiot

## 8.1 Johdanto

StartPlanner toimii muiden suunnistusohjelmien rinnalla.

Ohjelman tarkoitus ei ole korvata:

- Condesia
- eResultsia
- IRMAa

vaan täydentää niitä lähtökaavioiden suunnittelussa.

Kaikki tiedonsiirto toteutetaan import- ja export-moduuleilla.

---

# 8.2 Tuetut tiedostomuodot

Ensimmäisessä tuotantoversiossa tuetaan seuraavia tiedostomuotoja.

| Ohjelma  | Tuonti | Vienti |
| -------- | :----: | :----: |
| Condes   |   ✓    |   -    |
| IRMA     |   ✓    |   -    |
| eResults |   ✓    |   ✓    |
| Excel    |   ✓    |   ✓    |
| CSV      |   ✓    |   ✓    |
| PDF      |   -    |   ✓    |

Myöhemmin voidaan lisätä uusia tiedostomuotoja ilman muutoksia ohjelman ytimeen.

---

# 8.3 Condes

Condes toimii ratojen ensisijaisena tietolähteenä.

Condesista luetaan:

- kilpailun nimi
- kilpailupäivä
- sarjat
- radat
- rastiluettelot
- ensimmäinen rasti
- radan pituus
- nousu

Condesia ei koskaan muuteta.

StartPlanner käyttää sitä vain lukulähteenä.

---

# 8.4 IRMA

IRMA toimii ensisijaisena ilmoittautumistietojen lähteenä.

IRMAsta luetaan:

- kilpailijat
- sarjat
- seurat
- Emit-numerot (jos saatavilla)
- ilmoittautumistila

Ohjelma ei kirjoita tietoja takaisin IRMAan.

---

# 8.5 eResults

eResults toimii vaihtoehtoisena tietolähteenä.

Ohjelmasta voidaan lukea:

- kilpailijat
- sarjat
- lähtöajat (jos olemassa)
- Emit-numerot
- kilpailun perustiedot

Lisäksi tavoitteena on tukea lähtökaavion vientiä takaisin eResultsiin.

Vienti toteutetaan erillisenä pluginina.

---

# 8.6 Excel

Excel on tärkein vientimuoto.

**Ensisijainen vienti (lähtökaavio):**

- sarja
- ensimmäinen lähtöaika
- lähtö (`StartLocation`)
- kilpailijamäärä
- lähtöväli
- rata
- 1. rasti

Valinnaisesti myöhemmin:

- kilpailijakohtainen lähtölista (jos tuotettu tai tuotu)
- ensimmäisen rastin kuormitusraportti lähdöittäin
- kilpailijavirran raportti

Excel-vienti käyttää valmista pohjaa, jota voidaan myöhemmin muokata.
---

# 8.7 CSV

CSV toimii yleisenä tiedonsiirtomuotona.

CSV-viennissä voidaan valita vietävät kentät.

Esimerkkejä:

- kilpailijat
- lähtöajat
- sarjat
- radat

Kenttien järjestys on käyttäjän määritettävissä.

---

# 8.8 PDF

PDF-vientiä käytetään tulostettaviin raportteihin.

Ensimmäisessä versiossa tuetaan:

- lähtöluettelo
- sarjaluettelo
- rataluettelo
- ensimmäisen rastin yhteenveto

---

# 8.9 Projektitiedosto (.spc)

StartPlanner käyttää omaa projektitiedostoaan.

Päätetiedosto:

```
Kilpailu.spc
```

Projektitiedosto sisältää:

- kilpailun tiedot
- radat
- sarjat
- kilpailijat
- lähtökaavion
- lukitukset
- historian
- asetukset

Projektitiedosto on ohjelman ensisijainen tallennusmuoto.

---

# 8.10 Import-prosessi

Import tapahtuu seuraavasti.

1. Käyttäjä valitsee tiedoston.
2. Sopiva importteri tunnistetaan.
3. Tiedosto validoidaan.
4. Tiedot muunnetaan Domain-olioiksi.
5. Käyttäjälle näytetään yhteenveto.
6. Käyttäjä hyväksyy tuonnin.

Virhetilanteessa alkuperäistä projektia ei muuteta.

---

# 8.11 Export-prosessi

Export tapahtuu seuraavasti.

1. Käyttäjä valitsee vientimuodon.
2. Käyttäjä valitsee vietävät tiedot.
3. Exportteri muodostaa tiedoston.
4. Käyttäjä valitsee tallennuspaikan.
5. Ohjelma tallentaa tiedoston.

---

# 8.12 Plugin-rajapinta

Kaikki tiedostomuodot toteutetaan plugin-rajapinnan kautta.

Yhteinen rajapinta:

```python
class ImportPlugin:
    def supports(self, file_path: str) -> bool:
        ...

    def read(self, file_path: str) -> Competition:
        ...
```

```python
class ExportPlugin:
    def supports(self, format_name: str) -> bool:
        ...

    def write(self, competition: Competition) -> None:
        ...
```

Kaikki pluginit rekisteröidään ohjelman käynnistyessä.

---

# 8.13 Virheiden käsittely

Importin aikana havaittavat virheet jaetaan kolmeen luokkaan.

## Estävät virheet

Esimerkiksi:

- tiedostoa ei voi lukea
- XML on virheellinen
- pakolliset tiedot puuttuvat

Tuonti keskeytetään.

---

## Varoitukset

Esimerkiksi:

- Emit-numero puuttuu
- seura puuttuu
- radan nousu puuttuu

Tuontia voidaan jatkaa.

---

## Huomautukset

Esimerkiksi:

- ylimääräisiä kenttiä
- tuntemattomia XML-elementtejä

Kirjataan lokiin.

---

# 8.14 Versioyhteensopivuus

Jokainen importteri ilmoittaa tukemansa tiedostoversiot.

Esimerkiksi:

| Muoto      | Versiot                |
| ---------- | ---------------------- |
| Condes XML | 10–11                  |
| IRMA       | ilmoittautumisraportti |
| eResults   | määritellään myöhemmin |

Tuntemattomasta versiosta annetaan varoitus.

---

# 8.15 Tulevat integraatiot

Arkkitehtuuri mahdollistaa myöhemmin:

- OE2010
- Eventor
- IOF XML
- REST API
- verkkopalvelut
- pilvitallennus

Näiden lisääminen ei edellytä muutoksia ohjelman Domain- tai Service-kerroksiin.

---

# 8.16 Suunnitteluperiaatteet

Kaikissa integraatioissa noudatetaan seuraavia periaatteita:

- Alkuperäisiä tiedostoja ei koskaan muuteta.
- Kaikki tiedot muunnetaan ensin Domain-malliin.
- Tuonti ja vienti ovat toisistaan riippumattomia.
- Uudet tiedostomuodot voidaan lisätä plugineina.
- Virhetilanteet eivät saa rikkoa avointa projektia.