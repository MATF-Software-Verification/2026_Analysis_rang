# Valgrind (memcheck)

Jedini korišćeni Valgrind alat u ovom seminarskom radu (pravilo:
najviše 1 Valgrind alat). Pokreće se nad dve grupe binarnih fajlova,
odvojeno:

- **originalni kod projekta** -- `rang/test/test.cpp` (upstream
  doctest suite, prevedena kao `all_rang_tests`), `colorTest.cpp`,
  `envTermMissing.cpp`.
- **testovi dodati za ovaj seminarski rad** -- `unit_tests_bin`
  (jedinicni testovi iz `unit_tests/tests/`) i `term_probe`
  (crno-kutijski harness iz `integration_tests/tests/`).

## Reprodukcija

```sh
cd valgrind/memcheck
./run_memcheck.sh
```

Skripta prevodi sve binarne fajlove, pokrece ih pod
`--tool=memcheck --leak-check=full --show-leak-kinds=all
--track-origins=yes`, i cuva `<binarni-fajl>.log` pored sebe (vec
sacuvano iz poslednjeg pokretanja).

## Rezultat

Svih pet binarnih fajlova (i originalni kod projekta i dodati
testovi): **0 gresaka, 0 curenja memorije**
(`ERROR SUMMARY: 0 errors from 0 contexts`,
`All heap blocks were freed -- no leaks are possible`).

Ovo je očekivan, a ne iznenađujuci, rezultat: Unix/macOS grana u
`rang.hpp` (`#if defined(OS_LINUX) || defined(OS_MAC)`) ne alocira
memoriju samostalno -- samo čita `$TERM` preko `getenv`, zove
`isatty`, i piše kratke literal stringove kroz `operator<<`. Jedino
mesto u čitavom fajlu koje alocira (`std::unique_ptr` u `isMsysPty`)
je unutar `#ifdef OS_WIN` grane i ne prevodi se na ovoj platformi --
vidi `../../cppcheck` za to kako je ta grana ipak statički provere na
"drugi način".
