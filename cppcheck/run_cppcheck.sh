#!/usr/bin/env bash
# Pokrenuti iz cppcheck/. cppcheck sam prepoznaje #if/#elif granu za
# platformu u rang.hpp i automatski provera svaku konfiguraciju
# (unix, WIN32, APPLE) u jednom prolazu.
set -uo pipefail

cppcheck --version > cppcheck-version.txt

(cd ../rang && cppcheck --enable=all --inconclusive --std=c++11 --language=c++ \
    --suppress=missingIncludeSystem \
    -I include include/rang.hpp) > cppcheck.log 2>&1

cat cppcheck.log
