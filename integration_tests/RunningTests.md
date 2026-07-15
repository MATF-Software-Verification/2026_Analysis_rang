# Pokretanje crno-kutijskih (integracionih) testova

`tests/term_probe.cpp` je mali program koji ispisuje
`fg::red << "MARK" << style::reset` pod `control::Auto` (podrazumevani
rezim rada `rang`-a). `run_tests.py` ga prevede jednom, pa ga onda
pokrece kao poseban proces za matricu vrednosti `$TERM`, u dva
scenarija:

1. Pod pravim pty-om (`os.forkpty`) -- stdout je stvarno terminal,
   pa `rang_implementation::isTerminal()` vraca true, i preostaje
   samo pitanje šta `supportsColor()` odlucuje na osnovu `$TERM`.
2. Pod obicnim pipe-om -- stdout nije terminal, pa `isTerminal()`
   mora vratiti false i nikakvi ANSI bajtovi ne bi trebalo da se
   ispisu, bez obzira na `$TERM`.

Svaka vrednost `$TERM` se pokrece u novom procesu, pa ovo nije
pod uticajem kesiranja `supportsColor()` po procesu (vidi
`../unit_tests/tests/test_supports_color_caching.cpp` za to).

## Preduslovi

- g++ sa podrškom za C++11
- Linux (koristi `os.forkpty`, POSIX-only)

## Pokretanje

```sh
cd integration_tests
python3 run_tests.py
```

## Šta se provera / šta je pronadjeno

- Čvrsta provera (izlazni kod skripte): nikad se ne ispisuje ANSI
  escape bajt na stdout koji nije terminal, za bilo koju vrednost
  `$TERM`. Ovo važi u trenutnoj verziji `rang`-a.
- Nalaz (prijavljen, ne kao tvrda greška):
  `rang_implementation::supportsColor()` poredi `$TERM` sa svojom
  listom (`"ansi"`, `"color"`, `"console"`, `"cygwin"`, `"gnome"`,
  `"konsole"`, `"kterm"`, `"linux"`, `"msys"`, `"putty"`, `"rxvt"`,
  `"screen"`, `"vt100"`, `"xterm"`) koristeci `strstr` (podstring
  pretragu) umesto tacnog/prefiksnog poredjenja imena terminala.
  Realni terminfo unosi kao `xterm-mono` i `vt100-mono` (monohromatske
  varijante) sadrze `"xterm"`/`"vt100"` kao podstring i zbog toga se
  pogresno prepoznaju kao terminali koji podrzavaju boje, iako je
  cela poenta `-mono` sufiksa da terminal to ne podrzava. 
  Moglo bi se dodati provera sufixa u originalni izvorni kod.

