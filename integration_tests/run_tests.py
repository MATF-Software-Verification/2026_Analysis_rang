#!/usr/bin/env python3
"""Black-box tests for rang's control::Auto terminal/color auto-detection.

Builds test/term_probe.cpp (a tiny program that prints
fg::red + "MARK" + style::reset under control::Auto) and runs it under
two conditions for a matrix of $TERM values:

  1. Attached to a real pty (stdout *is* a terminal) -- checks whether
     rang emits ANSI escape bytes, and compares that against what a
     correctly-implemented whitelist check should decide. This is how
     we surface the substring-matching false positive in
     rang_implementation::supportsColor(): TERM values like
     "xterm-mono" / "vt100-mono" are real terminfo entries for
     *monochrome* terminals, but they contain "xterm"/"vt100" as a
     substring, so rang's `strstr`-based check wrongly treats them as
     color-capable.

  2. Attached to a plain pipe (stdout is NOT a terminal) -- asserts
     that no escape bytes are ever emitted, regardless of $TERM. This
     is a hard pass/fail check of rang's isTerminal() gating and is
     the thing this script's exit code reflects.

Usage:
    python3 run_tests.py
"""
import os
import pty
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
RANG_INCLUDE = REPO_ROOT / "rang" / "include"
BUILD_DIR = HERE / "build"
SOURCE = HERE / "tests" / "term_probe.cpp"
BINARY = BUILD_DIR / "term_probe"

ESC = b"\x1b"

# (TERM value or None, "should a correct impl treat this as color-capable?", note)
CASES = [
    ("xterm", True, "canonical color terminal"),
    ("linux", True, "canonical color terminal (Linux console)"),
    ("dumb", False, "explicitly non-color terminal"),
    ("totally-unknown-term", False, "unrecognized TERM, correctly rejected"),
    (None, False, "TERM unset, correctly rejected"),
    ("xterm-mono", False, "real terminfo entry for a MONOCHROME xterm"),
    ("vt100-mono", False, "real terminfo entry for a MONOCHROME vt100"),
]


def build():
    BUILD_DIR.mkdir(exist_ok=True)
    cmd = ["g++", "-std=c++11", "-Wall", "-Wextra", f"-I{RANG_INCLUDE}",
           str(SOURCE), "-o", str(BINARY)]
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def env_for(term):
    env = dict(os.environ)
    if term is None:
        env.pop("TERM", None)
    else:
        env["TERM"] = term
    return env


def run_in_pty(env):
    pid, master_fd = pty.fork()
    if pid == 0:
        os.execvpe(str(BINARY), [str(BINARY)], env)
        os._exit(127)  # unreachable unless exec fails
    chunks = []
    while True:
        try:
            data = os.read(master_fd, 4096)
        except OSError:
            break
        if not data:
            break
        chunks.append(data)
    os.waitpid(pid, 0)
    os.close(master_fd)
    return b"".join(chunks)


def run_in_pipe(env):
    result = subprocess.run([str(BINARY)], env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.stdout


def main():
    build()

    print()
    print(f"{'TERM':<24} {'pty: has ESC':<14} {'pipe: has ESC':<14} note")
    print("-" * 90)

    pipe_violations = []
    known_bugs = []

    for term, should_be_color, note in CASES:
        env = env_for(term)
        pty_out = run_in_pty(env)
        pipe_out = run_in_pipe(env)

        pty_has_esc = ESC in pty_out
        pipe_has_esc = ESC in pipe_out

        label = term if term is not None else "(unset)"
        print(f"{label:<24} {str(pty_has_esc):<14} {str(pipe_has_esc):<14} {note}")

        # Hard invariant: isTerminal() must gate off ANSI codes whenever
        # stdout is not a terminal, no matter what $TERM says.
        if pipe_has_esc:
            pipe_violations.append(term)

        # Informational: does rang's whitelist match a "should be
        # color-capable" ground truth when attached to a real pty?
        if pty_has_esc != should_be_color:
            known_bugs.append((term, note))

    print()
    if known_bugs:
        print("Mismatches between rang's substring-based whitelist and the"
              " correct decision (pty-attached):")
        for term, note in known_bugs:
            print(f"  - TERM={term!r}: {note}")
        print("These are reported as findings, not test failures -- rang's"
              " substring matching against its whitelist is the documented"
              " (if debatable) implementation.")

    if pipe_violations:
        print(f"\nFAIL: ANSI escapes leaked to a non-terminal stdout for"
              f" TERM values: {pipe_violations}")
        sys.exit(1)

    print("\nPASS: no ANSI escapes were ever emitted to a non-terminal stdout.")
    sys.exit(0)


if __name__ == "__main__":
    main()
