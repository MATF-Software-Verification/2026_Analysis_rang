#!/usr/bin/env python3
"""Builds and runs the doctest-based unit tests against rang.hpp.

Usage:
    python3 run_tests.py               # build + run the tests
    python3 run_tests.py --coverage    # also produce an lcov coverage report
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
RANG_INCLUDE = REPO_ROOT / "rang" / "include"
BUILD_DIR = HERE / "build"
TEST_SOURCES = [
    HERE / "tests" / "test_ansi_codes.cpp",
    HERE / "tests" / "test_supports_color_caching.cpp",
]
BINARY = BUILD_DIR / "unit_tests_bin"


def run(cmd, **kwargs):
    print("+ " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, check=True, **kwargs)


def build(coverage: bool):
    BUILD_DIR.mkdir(exist_ok=True)
    cmd = [
        "g++",
        "-std=c++11",
        "-Wall",
        "-Wextra",
        "-g",
        "-O0",
        f"-I{RANG_INCLUDE}",
    ]
    if coverage:
        cmd += ["--coverage"]
    cmd += [str(s) for s in TEST_SOURCES]
    cmd += ["-o", str(BINARY)]
    run(cmd, cwd=BUILD_DIR)


def run_tests():
    result = subprocess.run([str(BINARY)], cwd=BUILD_DIR)
    return result.returncode


def coverage_report():
    if shutil.which("lcov") is None or shutil.which("genhtml") is None:
        print("lcov/genhtml not found; skipping coverage report", file=sys.stderr)
        return
    info = BUILD_DIR / "coverage.info"
    run([
        "lcov",
        "--capture",
        "--directory", str(BUILD_DIR),
        "--output-file", str(info),
        "--include", f"{RANG_INCLUDE}/*",
        "--rc", "branch_coverage=1",
    ])
    run(["lcov", "--summary", str(info)])
    html_dir = HERE / "coverage_html"
    run(["genhtml", str(info), "--output-directory", str(html_dir), "--branch-coverage"])
    print(f"HTML coverage report: {html_dir / 'index.html'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", action="store_true",
                         help="instrument the build and produce an lcov report")
    args = parser.parse_args()

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    build(coverage=args.coverage)
    rc = run_tests()

    if args.coverage:
        coverage_report()

    sys.exit(rc)


if __name__ == "__main__":
    main()
