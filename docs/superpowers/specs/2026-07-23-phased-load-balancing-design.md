# Vaiheistettu kuormatasapainotus

## Tavoite

Lähtökaavio pitää minuuttikuorman mahdollisimman tasaisena automaattisesti lasketun
tavoitekuorman ympärillä. Kahden minuutin lähtövälin pitkät sarjat vaiheistetaan
parillisille tai parittomille minuuteille PDF-esimerkin tapaan.

## Tavoitekuorma

Tavoitekuorma lasketaan:

`kaikki lähtijät / aikatauluikkunan minuutit`

Jos aikatauluikkuna laajenee, tavoitekuorma lasketaan uudelleen uuden maksimin
perusteella ennen viimeistä tasoituskierrosta.

## Sijoituksen kustannus

Jokaiselle kelvolliselle aloitusminuutille lasketaan kustannus:

1. minuuttikuorman neliöpoikkeama tavoitekuormasta koko sarjan lähtövirran ajalta
2. suurin minuuttikuorma sijoituksen jälkeen
3. tyhjien minuuttien määrä
4. aikatauluikkunan ylitys
5. deterministinen aikaisempi aika tasatilanteessa

Pakolliset rajoitteet tarkistetaan ennen kustannusta:

- sama rata ei lomitu
- sama ensimmäinen rasti enintään 1 kilpailija/min
- lukitut ajat eivät muutu
- sarjan lähtöväli säilyy

## Vaiheistus

Kun `start_interval_min == 2` ja sarjassa on useita kilpailijoita, arvioidaan
erikseen parillinen ja pariton aloitusminuutti. Valitaan vaihe, jonka
kokonaiskustannus on pienempi. Muut lähtövälit käyttävät samaa kustannusfunktiota
ilman erityistä vaihepakkoa.

## Ajoitusjärjestys

1. Pullonkaularata sijoitetaan selkärangaksi.
2. Muiden ratojen ensimmäiset sarjat sijoitetaan tavoitekuorman mukaan.
3. Saman radan seuraavat sarjat ketjutetaan radan edellisen sarjan jälkeen, mutta
   niiden kelvollisista aloitusajoista valitaan tasaisin.
4. Jos aikataulu venyy, lukitsemattomat muut radat tasataan uudelleen uuden
   maksimi-ikkunan sisään.

## Testaus

- automaattinen tavoitekuorma
- kahden minuutin sarjojen parillinen/pariton vaiheistus
- kuormavarianssi pienenee nykyisestä
- tyhjät minuutit vähenevät
- pakolliset validointisäännöt säilyvät
- sama syöte tuottaa aina saman kaavion

