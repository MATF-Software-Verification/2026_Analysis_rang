# Pokretanje jedinicnih testova

Ovo su doctest testovi pisani direktno protiv
`rang/include/rang.hpp` (ne modifikuju i ne zavise od `rang`-ovog
sopstvenog `test/` direktorijuma). Provere dve stvari koje upstream
testovi ne pokrivaju:

1. `tests/test_ansi_codes.cpp` -- *tačan* `\033[<kod>m` niz bajtova za
   svaku vrednost `style`, `fg`, `bg`, `fgB`, `bgB` pod
   `control::Force`, plus da `control::Off` gasi ispis za sve
   kategorije. Upstream `test/test.cpp` samo provera da obojeni izlaz
   "razlikuje se od" / "je duzi od" plain stringa, za par slucajeva
   `fg::blue`.
2. `tests/test_supports_color_caching.cpp` -- dokumentuje/provera da
   `rang_implementation::supportsColor()` kesira svoju odluku
   zasnovanu na `$TERM` u lokalnoj `static` promenljivoj pri prvom
   pozivu, tako da promena `$TERM` kasnije u istom procesu nema
   efekta.

## Preduslovi

- g++ sa podrškom za C++11
- `doctest-dev` (Debian/Ubuntu: `sudo apt-get install -y doctest-dev`)
- `lcov` za opcioni izveštaj o pokrivenosti (`sudo apt-get install -y lcov`)

## Pokretanje

```sh
cd unit_tests
python3 run_tests.py
```

## Pokretanje sa merenjem pokrivenosti

```sh
cd unit_tests
python3 run_tests.py --coverage
```

Ovo instrumentira build sa `--coverage`, pokrece testove, i zatim
koristi `lcov`/`genhtml` da generise `unit_tests/coverage_html/index.html`
ogranicen samo na `rang.hpp`. Rezime se ispisuje i u terminalu.

Pokrivenost samo iz ovih testova (bez integracionih
testova u `../integration_tests`, koji pokrivaju granu za detekciju
terminala koja zahteva pravi terminal) je oko 62% linija / 94%
funkcija na Linux putanji; `#ifdef OS_WIN` grana je potpuno isključena
jer se ne prevodi na Linuxu.
