#!/usr/bin/env bash
# Pokrenuti iz valgrind/memcheck/. Prevodi binarne fajlove i pusta ih
# kroz Valgrind memcheck, odvojeno za originalni kod projekta i za
# testove dodate za ovaj seminarski rad.
set -uo pipefail

mkdir -p build

RANG_INCLUDE=../../rang/include

# --- originalni kod projekta (rang/test/*) ---
g++ -std=c++11 -g -O0 -I$RANG_INCLUDE ../../rang/test/test.cpp -o build/all_rang_tests
g++ -std=c++11 -g -O0 -I$RANG_INCLUDE ../../rang/test/colorTest.cpp -o build/colorTest
g++ -std=c++11 -g -O0 -I$RANG_INCLUDE ../../rang/test/envTermMissing.cpp -o build/envTermMissing

# --- testovi dodati za ovaj seminarski rad ---
g++ -std=c++11 -g -O0 -I$RANG_INCLUDE \
    ../../unit_tests/tests/test_ansi_codes.cpp \
    ../../unit_tests/tests/test_supports_color_caching.cpp \
    -o build/unit_tests_bin
g++ -std=c++11 -g -O0 -I$RANG_INCLUDE ../../integration_tests/tests/term_probe.cpp -o build/term_probe

MEMCHECK_FLAGS="--tool=memcheck --leak-check=full --show-leak-kinds=all --track-origins=yes --error-exitcode=1"

run() {
    name="$1"
    echo "=== memcheck: $name ==="
    valgrind $MEMCHECK_FLAGS --log-file="$name.log" "build/$name" >/dev/null 2>&1
    echo "izlazni kod: $? (log: $name.log)"
}

echo "----- originalni kod projekta (rang/test) -----"
run all_rang_tests
run colorTest
run envTermMissing

echo "----- testovi dodati za ovaj seminarski rad -----"
run unit_tests_bin
run term_probe

echo
echo "Svi logovi su u valgrind/memcheck/*.log"
