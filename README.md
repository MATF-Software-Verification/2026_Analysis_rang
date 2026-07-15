# 2026_Analysis_rang

Seminarski rad iz kursa Verifikacija softvera (MATF) -- analiza
otvorenog projekta [`rang`](https://github.com/agauniyal/rang), header-only
C++11 biblioteke za ANSI boje/stilove u `std::cout`/`cerr`/`clog`.

## Autor

- Ime i prezime: Mateja Stojanovic
- Broj indeksa: 1107/2025
- Email: stojanovic.mateja@gmail.com
- GitHub: [MSZ2](https://github.com/MSZ2)

## Analizirani projekat

- Repozitorijum: https://github.com/agauniyal/rang
- Grana: `master`
- Commit heš: `56419fe3348a475c8dd83852d907794cec0ec798` (tag `v3.3`)
- Uključen kao git submodule na putanji [`rang/`](rang).

Opis projekta i cilj analize su u
[`ProjectAnalysisReport.md`](ProjectAnalysisReport.md#1-uvod-i-opis-projekta).

## Korišćeni alati

Ukupno 6 alata/tehnika, u skladu sa pravilima predmeta (testovi kao
jedna stavka po kategoriji, najviše 1 Valgrind alat, najviše 1 alat za
formatiranje/stil, najmanje 2 alata koja nisu rađena na vežbama).

|  # | Alat / tehnika                                    | Direktorijum         | Pokrivenost vežbama                                              |
| -: | ------------------------------------------------- | -------------------- | ---------------------------------------------------------------- |
|  1 | Jedinični testovi (doctest) + lcov pokrivenost    | `unit_tests/`        | Delimično (lcov je rađen, ali C++ test framework nije)           |
|  2 | Crna kutija / integracioni testovi (Python + PTY) | `integration_tests/` | Delimično (analiza crne kutije je rađena, ali ne ovim pristupom) |
|  3 | Valgrind – Memcheck                               | `valgrind/memcheck/` | Da                                                               |
|  4 | clang-format                                      | `clang-format/`      | Delimično (Clang je pominjan u statičkoj analizi)                |
|  5 | cppcheck (statička analiza)                       | `cppcheck/`          | Ne                                                           |
|  6 | lizard (ciklomatska kompleksnost)                 | `lizard/`            | Ne                                                           |

Stavke 5 i 6 nisu deo plana vežbi ovog kursa (vežbe pokrivaju
Valgrind (memcheck/cachegrind/callgrind/hellgrind/drd), gdb, perf,
VTune, eBPF, KLEE, CBMC i Clang statičku analizu, ali ne cppcheck ni
lizard) -- čime je zadovoljeno pravilo "najmanje 2 alata koja nisu
rađena na vežbama".

### Preduslovi (Ubuntu/Debian)

```sh
sudo apt-get update
sudo apt-get install -y cmake clang-format cppcheck valgrind lcov \
    meson ninja-build doctest-dev python3
```

`lizard` nije dostupan kao apt paket -- `lizard/run_lizard.sh` ga sam
instalira u privatni virtualenv ako nije već na `PATH`-u (potreban je
samo `python3-venv`, koji dolazi sa `python3` na većini distribucija).

### Reprodukcija rezultata

Svaki direktorijum ima svoj `README.md`/`RunningTests.md` sa detaljima;
ukratko:

```sh
# 1) jedinicni testovi + pokrivenost
cd unit_tests && python3 run_tests.py --coverage && cd ..

# 2) crna kutija / integracioni testovi
cd integration_tests && python3 run_tests.py && cd ..

# 3) Valgrind memcheck
cd valgrind/memcheck && ./run_memcheck.sh && cd ../..

# 4) clang-format provera stila
cd clang-format && ./run_clang_format.sh && cd ..

# 5) cppcheck staticka analiza
cd cppcheck && ./run_cppcheck.sh && cd ..

# 6) lizard ciklomatska kompleksnost
cd lizard && ./run_lizard.sh && cd ..
```

Osnovni build same biblioteke (CMake/Meson/Conan) je nepromenjen u
odnosu na original.

## Zaključci

Detaljna analiza i obrazloženje nalaza su u
[`ProjectAnalysisReport.md`](ProjectAnalysisReport.md). Ukratko:

- `rang.hpp` je mala, uredna biblioteka bez dinamičke alokacije na
  Linux/macOS putanji -- Valgrind memcheck je potpuno "čist" (0
  grešaka) na svim test binarnim fajlovima, što je očekivan, a ne
  iznenađujući, rezultat.
- Pronađen je konkretan nalaz u logici detekcije boja:
  `rang_implementation::supportsColor()` poredi `$TERM` sa listom
  poznatih terminala korišćenjem `strstr` (podstring pretraga) umesto
  tačnog poređenja. Zbog toga se realni terminfo unosi za
  monohromatske terminale (`xterm-mono`, `vt100-mono`) pogrešno
  prepoznaju kao "podržava boje", jer sadrže `"xterm"`/`"vt100"` kao
  podstring. Ovo je demonstrirano crno-kutijskim (integracionim)
  testovima u `integration_tests/`.
- `supportsColor()` i `isTerminal()` keširaju svoj rezultat u
  `static` promenljivama inicijalizovanim pri prvom pozivu u procesu
  -- kasnije promene `$TERM` u istom procesu nemaju efekta. Ovo je
  demonstrirano jediničnim testom u `unit_tests/`.
- `clang-format` i `cppcheck` nalaze su kozmetički/informativni
  (jedna linija preko 80 kolona u Windows-only kodu; par stilskih
  napomena) -- nema realnih bagova pronađenih statičkom analizom.
- `lizard` (ciklomatska kompleksnost) potvrđuje da je bag sa
  `-mono` terminalima posledica pogrešnog *izbora* poređenja
  (`strstr` umesto tačnog), a ne komplikovane logike --
  `supportsColor()` ima nisku CCN (4). Najkompleksnije funkcije u
  celom fajlu (`isTerminal`, `isMsysPty`, `SGR2Attr`, CCN 8-11) su u
  Windows-only grani, koju ni jedan dinamički alat ovde ne pokriva.
- Pokrivenost kodom jedinicnim testovima na Linux putanji je ~62%
  linija / ~94% funkcija / ~23% grana pri poslednjem merenju (vidi
  `unit_tests/RunningTests.md`); ostatak su grane koje zahtevaju
  stvaran terminal (pokrivene integracionim testovima) i ceo
  `#ifdef OS_WIN` blok, koji se na Linuxu ne prevodi.
