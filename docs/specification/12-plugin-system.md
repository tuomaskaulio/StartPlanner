# 12 Plugin-järjestelmä

## 12.1 Johdanto

StartPlannerin laajennettavuus perustuu plugin-järjestelmään.

Pluginit mahdollistavat uusien ominaisuuksien lisäämisen ilman muutoksia Domain- tai Service-kerroksen ytimeen.

Ensimmäisessä vaiheessa plugineina toteutetaan:

- importterit
- exportterit
- optimointialgoritmit

Myöhemmin sama malli voidaan laajentaa myös validointisääntöihin, raportteihin ja ulkoisiin integraatioihin.

---

# 12.2 Tavoitteet

Plugin-järjestelmän tavoitteet ovat:

- uudet tiedostomuodot ilman ydinkoodin muutoksia
- vaihtoehtoiset optimointialgoritmit
- selkeä rajapinta kolmansille osapuolille
- turvallinen lataus ja rekisteröinti
- yhtenäinen käyttäjäkokemus riippumatta pluginista

Käyttäjän ei tarvitse tietää, onko toiminto toteutettu ytimessä vai pluginissa.

---

# 12.3 Plugin-tyypit

## ImporterPlugin

Lukee ulkoisen tiedoston ja muuntaa sen Domain-malliin.

## ExporterPlugin

Kirjoittaa Domain-mallin ulkoiseen tiedostomuotoon.

## OptimizerPlugin

Tuottaa tai parantaa lähtökaavion Domain-mallin perusteella.

## Tulevat tyypit

Esimerkiksi:

- ValidationPlugin
- ReportPlugin
- IntegrationPlugin

Näitä ei toteuteta ensimmäisessä versiossa, mutta rajapintamalli suunnitellaan laajennettavaksi.

---

# 12.4 Yhteinen metatieto

Jokainen plugin ilmoittaa:

| Kenttä           | Selite                         |
| ---------------- | ------------------------------ |
| id               | Yksilöllinen tunniste          |
| name             | Näyttönimi                     |
| version          | Pluginin versio                |
| api_version      | Tuettu StartPlanner API-versio |
| description      | Lyhyt kuvaus                   |
| author           | Tekijä                         |
| supported_formats| Tuettujen muotojen lista       |

Esimerkki:

```
id: condes_xml
name: Condes XML
version: 1.0.0
api_version: 1
```

---

# 12.5 Importerit

Importer lukee tiedoston ja palauttaa Domain-objektin.

Rajapinta:

```python
class ImporterPlugin:

    id: str
    name: str
    version: str

    def supports(self, file_path: str) -> bool:
        ...

    def read(self, file_path: str) -> Competition:
        ...

    def validate_source(self, file_path: str) -> list[Issue]:
        ...
```

## Toiminta

1. Käyttäjä valitsee tiedoston.
2. PluginRegistry etsii tukevan importterin.
3. Importteri lukee tiedoston.
4. Tulokset siirretään Domain-malliin.
5. Validointi suoritetaan.

## Sisäänrakennetut importterit (v1)

- Condes XML
- IRMA / ilmoittautumisraportti
- eResults (kun muoto varmistuu)
- CSV (yksinkertainen sarja/kilpailija-tuonti)

Importteri ei koskaan muuta alkuperäistä tiedostoa.

---

# 12.6 Exporterit

Exporter kirjoittaa Domain-mallin ulkoiseen muotoon.

Rajapinta:

```python
class ExporterPlugin:

    id: str
    name: str
    version: str

    def supports(self, format_name: str) -> bool:
        ...

    def write(self, competition: Competition, target_path: str) -> None:
        ...
```

## Toiminta

1. Käyttäjä valitsee vientimuodon.
2. Validointi suoritetaan tarvittaessa.
3. Exportteri muodostaa tiedoston.
4. Tiedosto tallennetaan käyttäjän valitsemaan paikkaan.

## Sisäänrakennetut exportterit (v1)

- Excel (.xlsx)
- CSV
- PDF (lähtöluettelo)
- tulostusvalmis lähtökaavio

Vienti ei muuta avointa projektia.

---

# 12.7 Optimointialgoritmit

Optimointialgoritmit toteutetaan plugineina, jotta eri strategioita voidaan vaihtaa asetuksista.

Rajapinta:

```python
class OptimizerPlugin:

    id: str
    name: str
    version: str

    def optimize(
        self,
        competition: Competition,
        constraints: Constraints,
        options: OptimizerOptions,
    ) -> ScheduleResult:
        ...
```

## Esimerkkialgoritmit

| Plugin              | Käyttötarkoitus                         |
| ------------------- | --------------------------------------- |
| GreedyOptimizer     | Nopea ensimmäinen ehdotus               |
| BalancedOptimizer   | Tasainen kilpailijavirta                |
| ORToolsOptimizer    | Raskaampi optimointi isoihin kilpailuihin |

Käyttäjä valitsee oletusalgoritmin asetuksista.

Kilpailukohtaisesti voidaan käyttää eri algoritmia.

---

# 12.8 PluginRegistry

Kaikki pluginit rekisteröidään käynnistyksessä.

```python
class PluginRegistry:

    def register(self, plugin) -> None:
        ...

    def find_importer(self, file_path: str) -> ImporterPlugin | None:
        ...

    def find_exporter(self, format_name: str) -> ExporterPlugin | None:
        ...

    def list_optimizers(self) -> list[OptimizerPlugin]:
        ...
```

Rekisteri vastaa:

- pluginien löytämisestä
- version tarkistuksesta
- päällekkäisten tunnisteiden estämisestä
- käyttöliittymälle tarjottavasta listasta

---

# 12.9 Lataus ja sijoittelu

Sisäänrakennetut pluginit toimitetaan ohjelman mukana.

Ulkoiset pluginit voidaan myöhemmin ladata erillisestä hakemistosta:

```
plugins/
├── importers/
├── exporters/
└── optimizers/
```

Ensimmäisessä versiossa tuetaan vain sisäänrakennettuja plugineita.

Ulkoisten pluginien lataus lisätään, kun turvallisuusmalli on valmis.

---

# 12.10 Turvallisuus

Plugin ei saa:

- suorittaa mielivaltaista verkkoon lähetystä ilman käyttäjän lupaa
- muuttaa projektitiedostoa suoraan ohittaen Persistence-kerroksen
- rikkoa Domain-sääntöjä

Kaikki pluginien tuottama data validoidaan ennen kuin se hyväksytään projektiin.

Tuntematon tai yhteensopimaton plugin ohitetaan ja käyttäjälle näytetään varoitus.

---

# 12.11 Virheiden käsittely

Pluginin virheet eivät kaada koko ohjelmaa.

Jos plugin epäonnistuu:

1. Virhe kirjataan lokiin.
2. Käyttäjälle näytetään selkeä viesti.
3. Avoin projekti säilytetään ennallaan.
4. Tarvittaessa tarjotaan vaihtoehtoista pluginiä.

---

# 12.12 Testaus

Jokaiselle pluginille kirjoitetaan omat testit.

Testataan ainakin:

- `supports()` tunnistaa oikeat tiedostot
- `read()` / `write()` / `optimize()` toimivat testiaineistolla
- virheelliset syötteet tuottavat hallitun virheen
- Domain-säännöt säilyvät

Uusi plugin ei saa rikkoa olemassa olevia testejä.

---

# 12.13 Tulevat laajennukset

Plugin-malli mahdollistaa myöhemmin esimerkiksi:

- OE2010 / Eventor / IOF XML -tuonnin
- verkkopalveluiden integraatiot
- mukautetut raporttipohjat
- kilpailumuotokohtaiset validointisäännöt
- yhteisön toimittamat algoritmit

Näiden lisääminen ei saa edellyttää Domain-mallin uudelleenkirjoittamista.

---

# 12.14 Suunnitteluperiaatteet

- Ydin pysyy ohueksi; vaihtelu menee plugineihin.
- Kaikki pluginit käyttävät Domain-mallia.
- Pluginien rajapinnat ovat pieniä ja vakaita.
- Uusi plugin voidaan lisätä ilman ytimen muutosta.
- Epäonnistunut plugin ei saa vaarantaa käyttäjän työtä.
- Sisäänrakennetut pluginit riittävät v1-tuotantoon.
