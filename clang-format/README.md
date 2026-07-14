# clang-format

Jedini alat za formatiranje/stilske provere u ovom seminarskom radu. 
Provera `rang/include/rang.hpp` protiv sopstvenog `.clang-format`
fajla projekta (WebKit brace style,4 razmaka, 80 kolona).

## Reprodukcija

```sh
cd clang-format
./run_clang_format.sh
```

Cuva `dry-run.log` (upozorenja clang-format-a) i `rang.hpp.diff`
(unified diff onoga sto bi clang-format promenio).

## Rezultat

`rang.hpp` je skoro potpuno uskladjen sa sopstvenim stilom. Jedino
kršenje je jedna linija preko 80 kolona, unutar Windows-only funkcije
`isMsysPty` (`#ifdef OS_WIN`, ne prevodi se i ne izvrsava na ovom
Linux okruzenju):

```cpp
std::wstring name(pNameInfo->FileName, pNameInfo->FileNameLength / sizeof(WCHAR));
```

koju bi clang-format prebacio u dve linije.
