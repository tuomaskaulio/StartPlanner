# 6 Ohjelmistoarkkitehtuuri

## 6.1 Johdanto

StartPlanner toteutetaan kerrosarkkitehtuurina (Layered Architecture).

Jokaisella kerroksella on selkeä vastuualue.

Kerrokset eivät saa ohittaa toisiaan.

```
                    GUI
                     │
          ┌──────────┴──────────┐
          │                     │
      Services            Validation
          │                     │
          └──────────┬──────────┘
                     │
                 Domain Model
                     │
         ┌───────────┴────────────┐
         │                        │
     Importers               Exporters
         │                        │
    External Files         External Files
```

Jokainen kerros voidaan testata itsenäisesti.

---

# 6.2 Kerrokset

## GUI

Vastaa ainoastaan käyttöliittymästä.

GUI:

- näyttää tietoja
- vastaanottaa käyttäjän komennot
- kutsuu Service-kerrosta

GUI EI:

- lue XML-tiedostoja
- laske lähtökaavioita
- muuta Domain-olioita suoraan

---

## Services

Service-kerros sisältää ohjelman liiketoimintalogiikan.

Esimerkkejä:

- CompetitionService
- SchedulerService
- ImportService
- ExportService
- ValidationService
- HistoryService

GUI kommunikoi ainoastaan tämän kerroksen kanssa.

---

## Domain

Domain sisältää kilpailun tietomallin.

Esimerkkejä:

- Competition
- Course
- Class
- Competitor
- Start
- StartSchedule

Domain ei tunne käyttöliittymää eikä tiedostoja.

---

## Importers

Importterit lukevat ulkoisia tiedostoja.

Esimerkiksi

- Condes
- IRMA
- eResults

Importteri muodostaa aina Domain-olion.

---

## Exporters

Exportterit kirjoittavat tietoja ulkoisiin tiedostoihin.

Esimerkkejä:

- Excel
- PDF
- CSV
- eResults

Exportteri käyttää aina Domain-mallia.

---

# 6.3 Hakemistorakenne

Projektin rakenne:

```
src/
    startplanner/
        domain/
        services/
        importers/
        exporters/
        gui/
        settings/
        history/
        validation/
        utils/

tests/

docs/

samples/

resources/
```

---

# 6.4 Domain

Domain sisältää vain tietomallin.

```
Competition

Class

Course

Competitor

Start

StartSchedule

Settings
```

Domain-olioiden tulee olla mahdollisimman riippumattomia.

Niissä ei saa olla käyttöliittymäkoodia.

---

# 6.5 Services

Service-kerros muodostaa ohjelman ytimen.

Suunnitellut palvelut:

## CompetitionService

Vastaa kilpailun käsittelystä.

Toimintoja:

- uusi kilpailu
- avaa kilpailu
- tallenna kilpailu

---

## SchedulerService

Vastaa lähtökaavion muodostamisesta.

Toimintoja:

- muodosta lähtökaavio
- optimoi
- lisää jälki-ilmoittautuneet
- validoi

---

## ImportService

Lukee ulkoisia tiedostoja.

Esimerkiksi

```
load_condes()

load_irma()

load_eresults()
```

---

## ExportService

Vie tietoja.

Esimerkiksi

```
export_excel()

export_pdf()

export_csv()
```

---

## HistoryService

Tallentaa kaikki muutokset.

Mahdollistaa myöhemmin:

- Undo
- Redo
- Audit Log

---

## ValidationService

Tarkistaa että

- lajisäännöt toteutuvat
- tiedot ovat ehjiä
- lähtökaavio on kelvollinen

---

# 6.6 Importterit

Jokainen tiedostomuoto toteutetaan omana moduulinaan.

```
importers/

condes.py

irma.py

eresults.py
```

Yhteinen rajapinta:

```
Importer

load(file)

↓

Competition
```

Näin uusia tiedostomuotoja voidaan lisätä muuttamatta muuta ohjelmaa.

---

# 6.7 Exportterit

Sama periaate.

```
exporters/

excel.py

pdf.py

csv.py
```

Rajapinta:

```
Exporter

export(schedule)
```

---

# 6.8 Plugin-arkkitehtuuri

Kaikki importterit ja exportterit toimivat plugineina.

Rajapinta:

```
ImporterPlugin

supports()

read()

validate()
```

```
ExporterPlugin

supports()

write()
```

Tulevaisuudessa myös optimointialgoritmit voivat olla plugineita.

Esimerkiksi

```
GreedyOptimizer

BalancedOptimizer

ORToolsOptimizer
```

Käyttäjä voi valita algoritmin asetuksista.

---

# 6.9 Tapahtumamalli

Service-kerros lähettää tapahtumia käyttöliittymälle.

Esimerkkejä:

```
CompetitionLoaded

ScheduleCreated

ScheduleOptimized

CompetitorAdded

HistoryChanged
```

GUI päivittää näkymän tapahtumien perusteella.

GUI ei jatkuvasti kysy tietoja.

---

# 6.10 Riippuvuudet

Sallitut riippuvuudet:

```
GUI
 ↓
Services
 ↓
Domain
```

Importterit:

```
Importer

↓

Domain
```

Exportterit:

```
Exporter

↓

Domain
```

Domain ei saa riippua mistään ylemmästä kerroksesta.

---

# 6.11 Virheenkäsittely

Kaikki virheet käsitellään poikkeuksina.

Esimerkiksi:

```
InvalidCourseDataError

ImportError

ScheduleConflictError

ValidationError
```

GUI näyttää käyttäjälle ymmärrettävän virheilmoituksen.

Lokit sisältävät tarkemmat tiedot.

---

# 6.12 Lokitus

Kaikki tärkeät tapahtumat kirjataan lokiin.

Esimerkkejä:

- kilpailu avattu
- Condes luettu
- IRMA luettu
- lähtökaavio muodostettu
- optimointi suoritettu
- vienti Exceliin

Lokitiedostot tallennetaan päivämäärän mukaan.

---

# 6.13 Testattavuus

Kaikki Services-kerroksen luokat tulee voida testata ilman käyttöliittymää.

Kaikille algoritmeille kirjoitetaan yksikkötestit.

Importtereille käytetään oikeita esimerkkiaineistoja.

GUI-testit pidetään minimissä.

---

# 6.14 Tulevaisuuden laajennukset

Arkkitehtuurin tulee mahdollistaa uusien ominaisuuksien lisääminen ilman suuria muutoksia.

Esimerkkejä:

- useita lähtöpaikkoja
- viestikilpailut
- sprinttikilpailut
- online-julkaisu
- pilvitallennus
- REST API
- useita kieliä
- lisäraportit

Perusarkkitehtuuria ei tarvitse muuttaa näiden lisäämiseksi.
