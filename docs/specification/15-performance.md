# 15 Suorituskyky

## 15.1 Johdanto

StartPlanneria käytetään myös suurissa kansallisissa kilpailuissa.

Siksi suorituskyky on osa tuotteen laatua, ei jälkikäteen tehtävä optimointi.

Tämä luku määrittelee:

- suorituskykytavoitteet
- mittarit
- optimointiperiaatteet

---

# 15.2 Suorituskykyperiaatteet

- Käyttöliittymä pysyy responsiivisena.
- Raskaat laskennat eivät lukitse GUI:ta.
- Samat syötteet tuottavat saman tuloksen (determinismi).
- Ensin oikeellisuus, sitten nopeus.
- Optimointi mitataan automaattisesti CI:ssä Large-aineistolla.

---

# 15.3 Referenssiaineisto

Suorituskyky mitataan ainakin seuraavalla Large-aineistolla:

- 40 sarjaa
- 20 rataa
- 1200 kilpailijaa

Lisäksi stress_test-aineisto:

- ≥ 2000 kilpailijaa
- monia samoja ensimmäisiä rasteja
- tiukat lukitukset

---

# 15.4 Tavoitteet

| Toiminto                     | Tavoite (Large) | Ehdoton yläraja |
| ---------------------------- | --------------: | --------------: |
| Projektin avaus              |           1 s   |            3 s  |
| Condes-tuonti                |           2 s   |            5 s  |
| IRMA-tuonti                  |           2 s   |            5 s  |
| Lähtökaavion muodostus       |           1 s   |            3 s  |
| Optimointi                   |           5 s   |           15 s  |
| Validointi                   |         500 ms  |            2 s  |
| Excel-vienti                 |           2 s   |            5 s  |
| Undo / Redo                  |         100 ms  |          300 ms |
| Yksittäisen kilpailijan siirto |        50 ms  |          200 ms |
| Historialistan avaus         |         300 ms  |            1 s  |

Jos ehdoton yläraja ylittyy CI:ssä, julkaisua ei tehdä ilman erillistä päätöstä.

---

# 15.5 Mittarit

Jokaisesta suorituskykyajosta kerätään:

| Mittari              | Selite                              |
| -------------------- | ----------------------------------- |
| wall_time_ms         | Kokonaisaika                        |
| cpu_time_ms          | Prosessoriaika                      |
| peak_memory_mb       | Huippumuisti                        |
| competitors          | Kilpailijoiden määrä                |
| classes              | Sarjojen määrä                      |
| courses              | Rankojen määrä                      |
| algorithm            | Käytetty optimizer-plugin           |
| quality_score        | Lopputuloksen laatupisteet          |
| validation_errors    | Virheiden määrä ajon jälkeen        |

Tulokset tallennetaan testiraporttiin.

Trendit seurataan versiosta toiseen.

---

# 15.6 Käyttöliittymän responsiivisuus

GUI ei koskaan suorita raskasta laskentaa UI-säikeessä.

Periaatteet:

- tuonti, optimointi ja vienti ajetaan taustalla
- edistyminen näytetään käyttäjälle
- käyttäjä voi peruuttaa pitkän operaation, jos se on turvallista
- näkymäpäivytykset tehdään tapahtumien kautta, ei jatkuvalla pollauksella

Tavoite: UI reagoi syötteeseen alle 100 ms myös Large-aineistolla, kun laskenta on käynnissä.

---

# 15.7 Algoritmien optimointiperiaatteet

1. **Nopea kelvollinen ratkaisu ensin**
   - Greedy / Balanced tuottaa käyttökelpoisen kaavion nopeasti.
2. **Raskas optimointi vain tarvittaessa**
   - OR-Tools tai vastaava vain isoihin kilpailuihin tai käyttäjän pyynnöstä.
3. **Paikalliset muutokset**
   - Jälki-ilmoittautunut sijoitetaan ilman koko kaavion uudelleenlaskentaa, jos mahdollista.
4. **Indeksit ja ryhmittelyt**
   - Ensimmäinen rasti, rata ja aika-indeksit pidetään muistissa.
5. **Vältä turhia kopioita**
   - Domain-objektien kopiointi vain Undo/snapshot-tarpeisiin.
6. **Mittaa ennen mikro-optimointia**
   - Muutokset perustuvat mittauksiin, ei arvailuun.

---

# 15.8 Muistin käyttö

Tavoitteet Large-aineistolla:

| Tila                         | Peak RSS |
| ---------------------------- | -------: |
| Projekti auki, ei optimointia |  ≤ 300 MB |
| Optimoinnin aikana            |  ≤ 600 MB |
| Stress test (≥ 2000)          | ≤ 1.0 GB |

Jos muistiraja ylittyy, tutkitaan ensin Domain-kopiot, historian tiivistys ja pluginien väliaikaistiedostot.

---

# 15.9 Tallennus ja I/O

`.spc`-tallennus:

- atominen transaktio
- vain muuttuneet taulut päivitetään mahdollisuuksien mukaan
- automaattinen tallennus ei saa jumittaa UI:ta

Tuonti/vienti:

- suoratoisto suurille CSV/XML-tiedostoille
- älä pidä koko vientitiedostoa muistissa, jos mahdollista

---

# 15.10 Regressioiden esto

Jokainen julkaisuvertailu sisältää suorituskykytestit.

Jos seinäaika kasvaa yli 20 % edelliseen julkaisuun nähden samalla aineistolla:

- avataan suorituskyky-issue
- regressio merkitään testiraporttiin
- korjaus priorisoidaan ennen seuraavaa minor-julkaisua

---

# 15.11 Suunnitteluperiaatteet

- Suorituskykyvaatimukset ovat osa speksiä, eivät toivelistaa.
- Mittarit ovat automaattisia ja toistettavia.
- UI pysyy käytettävänä raskaan laskennan aikana.
- Nopea kelvollinen tulos on tärkeämpi kuin teoreettinen optima.
- Suorituskykyä ei optimoida oikeellisuuden kustannuksella.
