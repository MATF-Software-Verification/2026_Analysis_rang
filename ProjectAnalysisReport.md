# Analiza projekta `rang`

Autor: Mateja Stojanovic (indeks 1107/2025)
Kurs: Verifikacija softvera
Analizirani projekat: [agauniyal/rang](https://github.com/agauniyal/rang), grana `master`, commit `56419fe3348a475c8dd83852d907794cec0ec798` (tag `v3.3`)

## 1. Uvod i opis projekta

`rang` je header-only C++11 biblioteka (jedan fajl,
`rang/include/rang.hpp`, ~500 linija) koja dodaje ANSI boje/stilove za
`std::cout`/`std::cerr`/`std::clog` kroz preklopljen `operator<<` za pet
skoupljenih enumeracija: `rang::style`, `rang::fg`, `rang::bg`,
`rang::fgB` (bright foreground), `rang::bgB` (bright background).
Ponašanje se kontroliše preko dva globalna atomska stanja:

- `rang::control` (`Off` / `Auto` / `Force`) -- da li se boje ikada
  ispisuju, i ako da, da li se prvo provera da terminal podržava boje.
- `rang::winTerm` (`Auto` / `Ansi` / `Native`) -- na Windows-u, da li
  se koristi ANSI escape sekvence ili native Console API.

Biblioteka ima dve potpuno odvojene implementacije "ispod haube":

- Unix (`#if defined(OS_LINUX) || defined(OS_MAC)`): jednostavno
  piše `"\033[<code>m"` gde je `<code>` numerička vrednost enum člana.
  Detekcija terminala (`isTerminal`) koristi `isatty(fileno(...))`, a
  detekcija podrške za boje (`supportsColor`) čita `$TERM` i traži
  podstring iz fiksne liste poznatih terminala.
- Windows (`#ifdef OS_WIN`): znatno kompleksnija -- emulira ANSI
  SGR kodove kroz `SetConsoleTextAttribute`, uključujući ručno praćenje
  stanja (`SGR` struktura), konverziju RGB->native atribut
  (`ansi2attr`), i detekciju MSYS/Cygwin pty-ova (`isMsysPty`).

Pošto je analiza rađena na Linuxu, Windows-only grana koda se ni ne
prevodi u ovom okruženju (nema `<windows.h>`), pa je jedini alat koji
je uopšte "video" tu granu kôda `cppcheck` (odeljak 3.5) -- svi ostali
alati (testovi, Valgrind) su isključivo pokrivali Unix granu.

## 2. Cilj analize

Cilj nije bio isključivo pronalaženje bagova (biblioteka je mala,
zrela, i verzionisana od 2016. godine), već sistematska primena šest
razlicitih alata/tehnika verifikacije softvera nad realnim, iako
kompaktnim, C++ projektom, i dokumentovanje šta svaki alat *stvarno*
može, a šta ne može, da otkrije na ovakvom kodu (npr. Valgrind ne
može ništa reći o Windows-only kodu koji se ne prevodi;
crna kutija ne moze testirati internu keš logiku bez pristupa
internom API-ju).

## 3. Alati i nalazi

### 3.1 Jedinični testovi (doctest) + lcov pokrivenost

Direktorijum: [`unit_tests/`](unit_tests)

Upstream test suite (`rang/test/test.cpp`) već postoji i pokriva
kombinacije `control` x `winTerm` za `cout`/`cerr`/`clog`, ali samo
provera da je izlaz "duži od" / "različit od" ulaznog stringa -- nikad
ne provera *tačan* niz bajtova. Takođe, `control::Auto` (podrazumevana
vrednost!) nije testiran nijednom u upstream suite-u.

Dodati testovi (`unit_tests/tests/`) provereju:

- Tačan ANSI kod za svaku vrednost svih pet enumeracija pod
  `control::Force` (npr. `fg::red` mora dati tačno `"\033[31m"`, ne
  samo "nešto duže od ulaza").
- Da `control::Off` gasi ispis za sve kategorije (`fg`, `bg`, `fgB`,
  `bgB`, `style`), ne samo za `fg` kao u upstream testu.
- Da se višestruki modifikatori u jednom stream-u konkateniraju bez
  dodatnih bajtova (`fg::red << style::bold << "hi" << style::reset`).
- Keširanje `supportsColor()`: pošto je `rang_implementation::
  supportsColor` dostupna funkcija (nije `static`/anonimni namespace,
  samo je u internom namespace-u), test je poziva direktno i pokazuje
  da drugi poziv, nakon promene `$TERM` između poziva, i dalje vraća
  *isti* rezultat kao prvi -- jer je implementirana kao
  `static const bool result = [](){ ... }();` unutar funkcije,
  inicijalizovana samo jednom po procesu.

Pokrivenost kodom (lcov, `python3 run_tests.py --coverage`):
62.2% linija / 93.8% funkcija / 22.6% grana na Unix putanji (Windows
grana je potpuno isključena iz merenja jer se ne prevodi). Grane koje
nedostaju su uglavnom u `isTerminal()`/`supportsColor()` -- zahtevaju
stvaran terminal (pty), što jedinicni testovi namerno ne rade (to je
posao integracionih testova, odeljak 3.2).

### 3.2 Crna kutija / integracioni testovi

Direktorijum: [`integration_tests/`](integration_tests)

Pošto `isTerminal()` interno poredi `os.rdbuf()` sa `std::cout.rdbuf()`
i zove `isatty(fileno(stdout))`, ne može se testirati kroz
`std::ostringstream` -- potreban je pravi (pseudo)terminal. Napisan je
mali harness (`tests/term_probe.cpp`) koji ispisuje
`fg::red << "MARK" << style::reset` pod `control::Auto`, i Python
skripta koja ga pokreće:

1. Pod pravim pty-om (`os.forkpty`), za matricu `$TERM` vrednosti.
2. Pod običnim pipe-om (bez terminala), za istu matricu.

Nalaz (bag u logici detekcije boja): `supportsColor()` poredi
`$TERM` sa listom `["ansi", "color", "console", "cygwin", "gnome",
"konsole", "kterm", "linux", "msys", "putty", "rxvt", "screen",
"vt100", "xterm"]` koristeći `strstr` (podstring pretraga), ne
tačno poređenje imena terminala. Realni terminfo unosi za
monohromatske varijante terminala -- `xterm-mono`, `vt100-mono`
-- sadrže `"xterm"`/`"vt100"` kao podstring, pa ih `rang` pogrešno
prepoznaje kao terminale koji podržavaju boje, iako je čitava poenta
`-mono` sufiksa da terminal *nema* podršku za boje. Test harness
potvrđuje ovo direktno: kada je `$TERM=xterm-mono` i stdout je pravi
pty, `rang` ispisuje ANSI escape bajtove.

Ovo je blaga, ali realna greška -- najverovatnije bez praktičnog
uticaja u praksi (retko se koristi `-mono` terminfo profil), ali je
konkretan primer gde pretpostavka "podstring => isti terminal" ne
važi.

Provera koja *nije* pukla: bez obzira na `$TERM`, kada stdout
nije terminal (obican pipe), `rang` nikad ne ispisuje ANSI kodove.
`isTerminal()` gating radi ispravno u svim testiranim slučajevima --
ovo je čvrsta (hard pass/fail) provera koje ovaj skript vraca exit kod.

### 3.3 Valgrind -- memcheck

Direktorijum: [`valgrind/memcheck/`](valgrind/memcheck)

Pokrenut sa `--leak-check=full --show-leak-kinds=all
--track-origins=yes`, odvojeno nad dve grupe binarnih fajlova (radi
jasne razlike izmedju provere originalnog koda projekta i provere
koda dodatog za ovaj seminarski rad):

- originalni kod projekta: `rang/test/test.cpp` (upstream doctest
  suite), `colorTest.cpp`, `envTermMissing.cpp`.
- testovi dodati za ovaj seminarski rad: `unit_tests_bin`
  (jedinicni testovi iz odeljka 3.1), `term_probe` (crno-kutijski
  harness iz odeljka 3.2).

Rezultat: 0 grešaka, 0 curenja memorije, na svih pet binarnih
fajlova (i originalni kod i dodati testovi). Ovo je očekivano, ne
iznenađujuce: Unix putanja u
`rang.hpp` ne alocira memoriju samostalno -- samo čita `$TERM`
(`getenv`), zove `isatty`, i piše kratke literal stringove kroz
`operator<<`. Jedino mesto u celom fajlu koje alocira (`std::
unique_ptr` u `isMsysPty`) je unutar `#ifdef OS_WIN` i ne postoji na
ovoj platformi.

### 3.4 clang-format

Direktorijum: [`clang-format/`](clang-format)

Provera `rang/include/rang.hpp` protiv sopstvenog `.clang-format`
fajla iz projekta (WebKit brace style, 4 razmaka, 80 kolona).

Nalaz: samo jedna linija premašuje 80 kolona -- unutar `isMsysPty`
(Windows-only funkcija):

```cpp
std::wstring name(pNameInfo->FileName, pNameInfo->FileNameLength / sizeof(WCHAR));
```

Kozmetički nalaz, konzistentan sa time da je to deo koda koji se
najmanje održava/testira (Windows-only, a projekat se najviše
razvija/testira na Linux/macOS CI).

### 3.5 cppcheck (staticka analiza)

Direktorijum: [`cppcheck/`](cppcheck)

Pokrenut sa `--enable=all --inconclusive` nad `rang.hpp`. cppcheck
sam detektuje `#if`/`#elif` platform granu u fajlu i automatski
provera svaku konfiguraciju (`WIN32`, `APPLE`, `unix/linux`) u jednom
prolazu -- ovo je jedini alat u čitavom seminarskom radu koji
uopšte pregleda Windows-only kod (`isMsysPty`, `SGR`
struktura/funkcije, `SGR2Attr`), pošto se taj kod ne prevodi ni
testira ni jednim drugim alatom ovde.

Nalazi:

- (`WIN32` konfiguracija) `Condition 'supportsColor()' is always
  true'` na liniji 477 -- na Windows-u je `supportsColor()` fiksno
  `true` (komentar u kodu: "All windows versions support colors
  through native console methods"), pa je `supportsColor() &&
  isTerminal(...)` redundantna provera na toj platformi. Namerno,
  informativno, ne bag.
- (inconclusive) `redundantCopyLocalConst` -- lokalna `const control
  option` kopija umesto reference; `control` je mali enum (int
  ispod haube), praktično nula uticaja na performanse.
- `unusedFunction` za `setWinTermMode`/`setControlMode` -- lažno
  pozitivno, jer cppcheck analizira samo ovaj fajl izolovano i ne vidi
  pozive iz `rang/test/*.cpp`.
- Nema nalaza unutar same Windows-only grane (`isMsysPty`, `SGR`
  funkcije) -- statička analiza nije pronašla ništa sumnjivo, što je
  jedini oblik verifikacije te grane dostupan u ovom seminarskom radu.

### 3.6 lizard (ciklomatska kompleksnost)

Direktorijum: [`lizard/`](lizard)

Drugi alat koji nije rađen na vežbama (uz cppcheck). `lizard` je
leksički Python alat -- ne kompajlira/preprocesira kôd, samo ga
parsira -- pa, baš kao cppcheck, "vidi" ceo `rang.hpp`, uključujući
Windows-only granu koju nijedan dinamički alat u ovom radu ne
pokriva. Mereno: ciklomatska kompleksnost (CCN), broj linija bez
komentara (NLOC), broj parametara i dužina, po funkciji.

Nalazi:

- 0 upozorenja na svih 24 funkcije u fajlu (default pragovi:
  CCN > 15, dužina > 1000 linija, > 100 parametara) -- nema funkcije
  koja bi bila kandidat za razbijanje/refaktorisanje samo na osnovu
  kompleksnosti.
- Prosečna CCN po funkciji: 3.4 (386 NLOC ukupno, 24 funkcije) --
  uobičajena vrednost za malu, direktnu biblioteku.
- Tri najkompleksnije funkcije su sve u Windows-only grani:
  `isTerminal` (CCN 11), `isMsysPty` (CCN 9) i `SGR2Attr` (CCN 8) --
  potvrđuje da je najkompleksniji deo biblioteke upravo onaj koji
  nijedan dinamički alat (testovi, Valgrind) u ovom seminarskom radu
  nije mogao pokrenuti, samo statička analiza (cppcheck, lizard).
- Na Unix putanji (koja *je* dinamički testirana) najkompleksnija je
  `supportsColor` (CCN 4). Ista funkcija je mesto konkretnog baga
  pronađenog crno-kutijskim testovima (odeljak 3.2) -- niska CCN
  potvrđuje da taj bag nije posledica komplikovane kontrolne logike,
  već pogrešnog *izbora* poređenja (`strstr` podstring umesto tačnog
  poređenja imena terminala).

## 4. Zaključci

1. `rang.hpp` je čist na Valgrind memcheck-u -- 0 grešaka na svim
   test binarnim fajlovima. Ovo je posledica jednostavnosti Unix
   implementacije (nema dinamičke alokacije, nema ručne aritmetike
   pokazivača), a ne posledica temeljnosti postojećih testova --
   vrednost ovog alata ovde je pre svega u *potvrdi* da je kod
   bezbedan, ne u pronalasku grešaka.
2. Konkretan, demonstriran bag postoji u logici detekcije boja:
   `supportsColor()` koristi podstring pretragu (`strstr`) umesto
   tačnog poređenja imena terminala, što uzrokuje lažno pozitivnu
   detekciju za realne monohromatske terminfo profile (`xterm-mono`,
   `vt100-mono`). Ovo je pronađeno i demonstrirano isključivo kroz
   crno-kutijske integracione testove sa pravim pty-om -- ni jedinicni
   testovi ni statička analiza ne bi ovo otkrili, jer zahteva
   pokretanje sa različitim `$TERM` vrednostima protiv realnog
   terminala.
3. Keširanje internog stanja (`supportsColor()`/`isTerminal()`)
   je namerna optimizacija (jedan `getenv`/`isatty` poziv po procesu),
   ali je "zamka" za bilo koji kôd koji menja `$TERM` u toku izvršavanja
   i očekuje da `rang` to primeti -- neće. Ovo je dokumentovano i
   testirano jediničnim testom koji poziva internu funkciju direktno.
4. Windows-only kod je jedini deo biblioteke koji nije bilo moguće
   dinamički testirati u ovom okruženju (nema Windows-a). cppcheck i
   lizard su jedini alati koji ga statički pregledaju (oba leksicki, bez
   kompajliranja), i ne pronalaze ništa sumnjivo -- ali ovo je slabija
   garancija od dinamičkog testiranja, i predstavlja realno ograničenje
   ove analize, ne dokaz da je taj kod bagfree.
5. clang-format nalaz je čisto kozmetički (jedna linija preko 80
   kolona, u Windows-only kodu) -- potvrđuje da projekat drži dobar
   nivo stilske konzistentnosti i da mu clang-tidy/clang-format nisu
   neophodni kao gate u CI, iako bi mogli biti korisni.
6. lizard potvrđuje da bag sa `-mono` terminfo profilima nije
   posledica komplikovane logike -- `supportsColor()` ima nisku
   ciklomatsku kompleksnost (CCN 4); najkompleksnije funkcije u celom
   fajlu (`isTerminal`, `isMsysPty`, `SGR2Attr`, sve CCN 8-11) su baš
   one iz Windows-only grane koju nijedan dinamički alat ovde ne
   pokriva, što dodatno naglašava ograničenje iz tačke 4.
7. Sveukupno, `rang` je primer malog, dobro fokusiranog header-only
   projekta gde je "težak" alat za memorijsku verifikaciju (Valgrind)
   manje koristan od ciljanih crno-kutijskih testova specifičnih za
   domensku logiku biblioteke (detekcija terminala/boja) -- najveći
   pronađeni nalaz (bug sa `-mono` terminfo profilima) došao je upravo
   od najjeftinijeg, najmanje "alatski teškog" pristupa: pisanja
   testova koji stvarno simuliraju kako se biblioteka koristi u praksi.
