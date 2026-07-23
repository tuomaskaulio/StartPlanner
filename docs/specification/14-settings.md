# 14 Asetukset

## 14.1 Johdanto

StartPlannerin asetukset jaetaan kolmeen tasoon:

1. kilpailukohtaiset
2. käyttäjäkohtaiset
3. järjestelmäkohtaiset

Tavoitteena on, että sama ohjelma toimii eri kilpailuissa ja eri käyttäjillä ilman, että asetukset sekoittuvat.

---

# 14.2 Asetustasot

## Kilpailukohtaiset asetukset

Tallentuvat projektitiedostoon (`.spc`).

Koskevat vain avointa kilpailua.

Esimerkkejä:

- oletuslähtöväli
- sarjojen välinen tauko
- käytettävä optimointialgoritmi
- raporttien otsikot
- kilpailukohtaiset värit
- julkaisuprofiili

## Käyttäjäkohtaiset asetukset

Tallentuvat käyttäjän koneelle, erillään projektista.

Esimerkkejä:

- kieli
- teema
- viimeksi avatut projektit
- oletuskansiot
- näkymien leveydet
- pikanäppäimet

## Järjestelmäkohtaiset asetukset

Koskevat asennusta tai organisaatiota.

Esimerkkejä:

- plugin-hakemistot
- lokituksen taso
- päivitysten tarkistus
- oletustiedostomuodot
- suorituskykyrajoitukset
- organisaation oletusraporttipohjat

---

# 14.3 Prioriteetti

Kun sama asetus voidaan määritellä usealla tasolla, käytetään seuraavaa järjestystä:

1. kilpailukohtainen
2. käyttäjäkohtainen
3. järjestelmäkohtainen
4. ohjelman oletusarvo

Esimerkki:

```
ohjelman oletus: lähtöväli = 2 min
käyttäjä:        lähtöväli = 2 min
kilpailu:        lähtöväli = 1 min  → käytetään 1 min
```

Käyttäjälle näytetään, miltä tasolta arvo tulee.

---

# 14.4 Kilpailukohtaiset asetukset

Kilpailukohtaiset asetukset vaikuttavat lähtökaavion muodostukseen ja raportointiin.

| Asetus                    | Oletus              |
| ------------------------- | ------------------- |
| default_start_interval    | 2 min               |
| class_gap_minutes         | 2 min               |
| optimizer_plugin          | BalancedOptimizer   |
| first_control_capacity    | 1 / min             |
| allow_warnings_on_export  | true                |
| quality_score_weights     | ohjelman oletukset  |
| report_title              | kilpailun nimi      |
| time_display_format       | HH:MM               |

Kilpailukohtaiset asetukset kulkevat projektin mukana toiseen koneeseen.

---

# 14.5 Käyttäjäkohtaiset asetukset

Käyttäjäkohtaiset asetukset parantavat käyttömukavuutta, mutta eivät muuta kilpailun sääntöjä.

| Asetus                 | Oletus        |
| ---------------------- | ------------- |
| language               | fi            |
| theme                  | system        |
| recent_projects_max    | 10            |
| default_import_folder  | käyttäjän koti |
| default_export_folder  | käyttäjän koti |
| autosave_minutes       | 5             |
| show_quality_score     | true          |
| confirm_destructive    | true          |

Käyttäjäasetukset eivät siirry `.spc`-tiedoston mukana.

---

# 14.6 Järjestelmäkohtaiset asetukset

Järjestelmäasetukset määritellään asennus- tai ylläpitotasolla.

| Asetus                   | Oletus                |
| ------------------------ | --------------------- |
| plugin_directories       | ohjelman plugins/     |
| log_level                | info                  |
| max_competitors_soft     | 2000                  |
| enable_external_plugins  | false (v1)            |
| telemetry                | off                   |
| update_check             | manual                |

Järjestelmäasetuksia ei yleensä muokata tavallisessa kilpailukäytössä.

---

# 14.7 Tallennuspaikat

| Taso         | Tallennuspaikka                          |
| ------------ | ---------------------------------------- |
| Kilpailu     | `.spc` → `settings`-taulu                |
| Käyttäjä     | käyttöjärjestelmän asetushakemisto       |
| Järjestelmä  | asennuksen config-tiedosto / admin-asetus |

Esimerkki käyttäjäasetuksista:

```
~/.config/StartPlanner/settings.json
```

Windowsissa käytetään vastaavaa AppData-sijaintia.

---

# 14.8 Asetusten käyttöliittymä

Asetukset-ikkuna jaetaan välilehtiin:

- Kilpailu
- Käyttäjä
- Järjestelmä (jos oikeudet sallivat)

Jokaisessa kentässä näytetään:

- nykyinen arvo
- oletusarvo
- taso, jolta arvo tulee
- lyhyt selite

Vaaralliset muutokset vaativat vahvistuksen.

Esimerkiksi:

- ulkoisten pluginien käyttöönotto
- lähtövälin muuttaminen kesken optimoinnin
- automaattisen tallennuksen poisto

---

# 14.9 Validointi

Asetukset validoidaan tallennuksen yhteydessä.

Esimerkkejä:

- lähtöväli > 0
- tauko ≥ 0
- tuntematon optimizer_plugin hylätään
- polkujen on oltava olemassa tai luotavissa

Virheellinen asetus ei korvaa aiempaa kelvollista arvoa.

---

# 14.10 Muutosten vaikutus

Jotkut asetukset vaikuttavat heti:

- kieli
- teema
- näkymäasetukset

Jotkut vaativat uudelleenlaskennan:

- lähtöväli
- optimointialgoritmi
- ensimmäisen rastin kapasiteetti

Käyttäjälle kerrotaan, jos muutos edellyttää uutta optimointia tai validointia.

---

# 14.11 Suunnitteluperiaatteet

- Kilpailun säännöt kulkevat projektin mukana.
- Käyttäjän mieltymykset pysyvät konekohtaisina.
- Järjestelmäasetukset ovat harvoin muutettavia.
- Oletusarvot ovat turvallisia kansalliseen kilpailuun.
- Asetusten lähde on aina näkyvissä.
- Virheellinen asetus ei saa rikkoa avointa projektia.
