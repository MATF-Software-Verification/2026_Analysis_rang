#!/usr/bin/env bash
# Pokrenuti iz lizard/. lizard je Python alat za merenje ciklomatske
# kompleksnosti (CCN) po funkciji -- nije dostupan kao apt paket, pa
# ovaj skript instalira privatni venv (lizard/.venv, van git-a) ako
# `lizard` binarni fajl vec nije dostupan u PATH-u.
set -uo pipefail

if ! command -v lizard >/dev/null 2>&1; then
    if [ ! -x .venv/bin/lizard ]; then
        python3 -m venv .venv
        .venv/bin/pip install --quiet lizard
    fi
    LIZARD=.venv/bin/lizard
else
    LIZARD=lizard
fi

"$LIZARD" --version > lizard-version.txt 2>&1

"$LIZARD" --languages cpp ../rang/include/rang.hpp > lizard.log 2>&1

cat lizard.log
