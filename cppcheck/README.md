# cppcheck

Jedan od alata u ovom seminarskom radu koji nisu rađeni na
vežbama kursa (vežbe pokrivaju Clang-ovu sopstvenu statičku analizu/
clang-tidy, KLEE i CBMC, ali ne cppcheck). Pokrenut nad
`rang/include/rang.hpp` sa `--enable=all --inconclusive`.

cppcheck sam prepoznaje `#if`/`#elif` granu za platformu u fajlu
(unix vs `WIN32` vs `APPLE`) i automatski ponovo provera fajl za svaku
konfiguraciju koju pronadje. Zbog toga je ovo jedini alat u čitavom
seminarskom radu koji uopšte pregleda Windows-only kod
(`isMsysPty`, `SGR`/`setWinSGR`/`SGR2Attr`, `setWinColorNative`, ...)
-- svi ostali alati ovde (testovi, memcheck) pokrivaju
samo `#if defined(OS_LINUX) || defined(OS_MAC)` granu, jer se
Windows-only grana jednostavno ne prevodi na ovoj platformi.

## Reprodukcija

```sh
cd cppcheck
./run_cppcheck.sh
```

Cuva `cppcheck.log` pored sebe (vec sacuvano iz poslednjeg
pokretanja).

## Nalazi

- (samo `WIN32` konfiguracija) `Condition 'supportsColor()' is
  always true'` na liniji 477. Na Windows-u je `supportsColor()`
  hardkodirano `static constexpr bool result = true;` (komentar u
  kodu: "All windows versions support colors through native console
  methods"), pa u `operator<<`-ovoj `control::Auto` grani izraz
  `supportsColor() && isTerminal(...)` uvek evaluira desnu stranu --
  ispravno i namerno, samo redundantna provera na toj platformi.
  Informativno, ne bag.
- `redundantCopyLocalConst` (inconclusive):
  `const control option = rang_implementation::controlMode();` u
  `operator<<` kopira rezultat atomskog citanja u lokalnu `const
  control` promenljivu umesto da vezuje const referencu. `control` je
  obican scoped enum (int ispod haube), pa ovo nema merljiv uticaj na
  performanse -- stilska napomena, ne vredi menjati.
- `unusedFunction` za `setWinTermMode`/`setControlMode`: ocekivano
  lazno pozitivno. cppcheck analizira samo ovaj header izolovano, pa
  ne vidi da su ovo javne funkcije biblioteke, pozivane iz
  `rang/test/test.cpp` i `rang/test/colorTest.cpp`.
- Nema nikakvih nalaza za `APPLE`/`unix` konfiguracije osim ova dva
  zajednicka, i nema nalaza unutar same Windows-only grane
  (`isMsysPty`, `SGR` bit-manipulacione funkcije, `SGR2Attr`) --
  staticka analiza tu nije pronasla nista sumnjivo, sto je najbliza
  stvar verifikaciji te grane u citavom ovom seminarskom radu.
