# lizard

Drugi alat u ovom seminarskom radu koji **nije** rađen na vežbama
kursa (uz `cppcheck`) -- potreban za pravilo "najmanje 2 alata koja
nisu rađena na vežbama". `lizard` je Python alat koji leksički
(bez kompajliranja/preprocesiranja) računa **ciklomatsku
kompleksnost (CCN)**, broj linija bez komentara (NLOC), broj
parametara i dužinu za svaku funkciju u fajlu.

Baš zato što radi leksički, a ne kroz stvarnu kompilaciju,
`lizard` -- kao i `cppcheck` -- vidi **ceo** `rang.hpp`, uključujući
Windows-only granu (`isMsysPty`, `SGR2Attr`, `setWinSGR`, ...), iako
se taj kod na ovoj (Linux) platformi ne prevodi i nijedan dinamički
alat (testovi, Valgrind) ga ne pokriva.

## Reprodukcija

```sh
cd lizard
./run_lizard.sh
```

`lizard` nije dostupan kao apt paket. Skript ga automatski instalira
u privatni virtualenv (`lizard/.venv`, van git-a, videti
`.gitignore`) ako `lizard` binarni fajl vec nije na `PATH`-u.
Cuva `lizard.log` i `lizard-version.txt` pored sebe (vec sacuvano iz
poslednjeg pokretanja).

## Nalazi

Pokrenuto bez posebnih pragova (default: upozorenje na CCN > 15,
duzinu funkcije > 1000 linija, ili > 100 parametara) -- **0
upozorenja** na svih 24 funkcije u fajlu.

- **Najveca ciklomatska kompleksnost:** `isTerminal` (CCN 11,
  Windows-only telo funkcije -- provera niza uslova za MSYS/Cygwin
  pty i ANSI konzolu), zatim `isMsysPty` (CCN 9, Windows-only parsing
  handle-a) i `SGR2Attr` (CCN 8, Windows-only konverzija SGR koda u
  native atribut). Sve tri su, ociglledno, u Windows-only grani --
  najkompleksniji dio biblioteke je upravo onaj koji ni jedan
  dinamicki alat u ovom seminarskom radu nije mogao pokrenuti.
- Prosecna CCN po funkciji je **3.4** (24 funkcije, 386 NLOC) --
  potpuno uobicajena vrednost za malu, direktnu biblioteku; nema
  funkcija koje bi bile kandidat za refaktorisanje samo na osnovu
  kompleksnosti.
- Na Unix putanji (koja je i dinamicki testirana) najkompleksnija je
  `supportsColor` (CCN 4, petlja + `strstr` provera liste terminala)
  -- ista funkcija u kojoj je crno-kutijskim testovima (odeljak 3.2 u
  `ProjectAnalysisReport.md`) pronadjen konkretan bag (lazna
  detekcija boja za `*-mono` terminale). Njena kompleksnost je niska,
  sto potvrdjuje da taj bag nije posledica komplikovane logike, vec
  pogresnog izbora *nacina* poredjenja (podstring umesto tacnog
  poredjenja).
