#!/usr/bin/env bash
# Pokrenuti iz clang-format/. Provera rang.hpp protiv sopstvenog
# .clang-format fajla iz projekta.
set -uo pipefail

STYLE=../rang/.clang-format
TARGET=../rang/include/rang.hpp

clang-format --version > clang-format-version.txt

clang-format --style="file:$STYLE" --dry-run "$TARGET" > dry-run.log 2>&1
DRY_RUN_RC=$?

clang-format --style="file:$STYLE" "$TARGET" > rang.hpp.formatted
diff -u "$TARGET" rang.hpp.formatted > rang.hpp.diff
rm -f rang.hpp.formatted

echo "izlazni kod dry-run provere: $DRY_RUN_RC (0 = kod je vec uskladjen)"
echo "broj linija u diff-u: $(grep -c '^[<>+-]' rang.hpp.diff)"
echo "vidi dry-run.log i rang.hpp.diff"
