# 10 Testausstrategia

## 10.1 Johdanto

StartPlannerin tavoitteena on tuottaa luotettava ja toistettava lähtökaavio kaikissa kilpailuissa.

Jokainen uusi ominaisuus testataan automaattisesti ennen julkaisua.

Testauksen tavoitteet ovat:

- estää virheet
- varmistaa lajisääntöjen noudattaminen
- säilyttää ohjelman suorituskyky
- mahdollistaa turvallinen jatkokehitys

---

# 10.2 Testitasot

Projektissa käytetään neljää testitasoa.

## Yksikkötestit (Unit Tests)

Testaavat yksittäisiä luokkia ja metodeja.

Esimerkkejä:

- Competitor
- Course
- RaceClass
- SchedulerService
- ValidationService

Yksikkötestit eivät käytä käyttöliittymää tai tiedostoja.

---

## Integraatiotestit

Testaavat usean komponentin yhteistyötä.

Esimerkkejä:

- Condes → Domain
- IRMA → Domain
- Scheduler → Validation
- Export → Excel

---

## Järjestelmätestit

Testataan koko työnkulku.

Esimerkki:

1. Luo uusi kilpailu
2. Lue Condes
3. Lue IRMA
4. Muodosta lähtökaavio
5. Optimoi
6. Vie Exceliin

Kaikkien vaiheiden tulee onnistua ilman virheitä.

---

## Regressiotestit

Varmistavat, ettei vanha toiminnallisuus rikkoudu uusien muutosten yhteydessä.

Jokainen aiemmin havaittu virhe saa oman regressiotestinsä.

---

# 10.3 Testiaineistot

Projektissa ylläpidetään pysyvää testiaineistokokoelmaa.

```
samples/

small/

medium/

large/

edge_cases/
```

---

## Small

Pieni kilpailu

- 3 sarjaa
- 2 rataa
- 25 kilpailijaa

Soveltuu yksikkötesteihin.

---

## Medium

Keskisuuri kilpailu

- 15 sarjaa
- 8 rataa
- 250 kilpailijaa

Soveltuu integraatiotesteihin.

---

## Large

Suuri kilpailu

- 40 sarjaa
- 20 rataa
- 1200 kilpailijaa

Suorituskykytestit.

---

## Edge Cases

Sisältää poikkeustapauksia.

Esimerkiksi:

- yksi kilpailija
- tyhjä sarja
- sama ensimmäinen rasti kaikilla
- puuttuva rata
- puuttuva lähtöaika
- erittäin suuri kilpailu

---

# 10.4 Yksikkötestit

Kaikille palveluille kirjoitetaan yksikkötestit.

Esimerkiksi:

```
tests/

test_scheduler.py

test_validation.py

test_import_condes.py

test_export_excel.py

test_history.py
```

Tavoitteena on vähintään 90 % testikattavuus Services- ja Domain-kerroksissa.

---

# 10.5 Algoritmitestit

Lähtökaavioalgoritmille laaditaan erilliset testit.

Tarkistetaan muun muassa:

- lähtövälit
- ensimmäiset rastit
- sarjojen järjestys
- lukitukset
- optimointi

Algoritmin tulee antaa sama tulos samoilla syötteillä.

---

# 10.6 Validointitestit

Jokainen validointisääntö testataan erikseen.

Esimerkiksi:

- puuttuva rata
- liian lyhyt lähtöväli
- ensimmäisen rastin konflikti
- lukituksen rikkominen

---

# 10.7 Import- ja export-testit

Jokaiselle tiedostomuodolle ylläpidetään testiaineisto.

Testit varmistavat, että:

- tiedostot voidaan lukea
- tiedot siirtyvät oikein Domain-malliin
- vienti tuottaa odotetun rakenteen

---

# 10.8 Suorituskykytestit

Suorituskyky mitataan automaattisesti.

Tavoitteet:

| Toiminto               | Maksimiaika |
| ---------------------- | ----------: |
| Condes-tuonti          |         2 s |
| IRMA-tuonti            |         2 s |
| Lähtökaavion muodostus |         1 s |
| Optimointi             |         5 s |
| Excel-vienti           |         2 s |

Mittaukset suoritetaan Large-testiaineistolla.

---

# 10.9 Käyttöliittymätestit

Käyttöliittymä testataan pääasiassa manuaalisesti.

Automaattisesti testataan:

- ikkunoiden avautuminen
- tärkeimmät painikkeet
- tiedoston avaaminen
- vientitoiminnot

Varsinainen liiketoimintalogiikka testataan ilman käyttöliittymää.

---

# 10.10 Jatkuva integraatio (CI)

Kaikki muutokset tarkistetaan automaattisesti.

CI suorittaa:

1. Koodin tyylitarkistuksen
2. Yksikkötestit
3. Integraatiotestit
4. Regressiotestit
5. Testikattavuuden mittauksen

Julkaisua ei tehdä, jos yksikin testi epäonnistuu.

---

# 10.11 Testikattavuus

Tavoitteet:

| Osa       | Tavoite |
| --------- | ------: |
| Domain    |   100 % |
| Services  |    95 % |
| Importers |    90 % |
| Exporters |    90 % |
| GUI       |    60 % |

GUI:n osalta täydellistä kattavuutta ei tavoitella.

---

# 10.12 Hyväksymistestaus

Ennen julkaisua ohjelma testataan oikealla kilpailuaineistolla.

Testit sisältävät:

- pieni kilpailu
- kansallinen kilpailu
- arvokilpailun kokoinen kilpailu

Hyväksymistestin suorittaa vähintään yksi henkilö, joka ei ole osallistunut kyseisen ominaisuuden toteutukseen.

---

# 10.13 Korjatut virheet

Jokaisesta korjatusta virheestä kirjoitetaan regressiotesti.

Virhettä ei katsota korjatuksi ennen kuin regressiotesti on lisätty.

---

# 10.14 Testauksen suunnitteluperiaatteet

- Testit kirjoitetaan mahdollisimman lähelle toteutusta.
- Testien tulee olla nopeasti suoritettavia.
- Testien tulee olla deterministisiä.
- Testit eivät saa riippua internet-yhteydestä tai ulkoisista palveluista.
- Kaikki testiaineistot säilytetään versionhallinnassa.
- Jokainen julkaisu perustuu onnistuneesti läpäistyihin testeihin.