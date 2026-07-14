#include <doctest/doctest.h>

#include "rang.hpp"
#include <cstdlib>

// rang_implementation::supportsColor() memoizes its result in a
// function-local `static const bool`, initialized from an
// immediately-invoked lambda on the *first* call in the process. This
// means every later call returns the same answer no matter how $TERM
// changes afterwards -- a real caveat for anything that flips $TERM at
// runtime and expects rang to re-detect. This test pins down that
// contract directly against the (internal, but reachable) function
// rather than relying on process spawning.

TEST_CASE(
  "supportsColor() ignores TERM changes made after its first invocation")
{
    setenv("TERM", "xterm", 1);
    const bool first = rang::rang_implementation::supportsColor();

    // Flip TERM to a value with none of the whitelisted substrings.
    setenv("TERM", "totally-unrecognized-term", 1);
    const bool second = rang::rang_implementation::supportsColor();

    // Regardless of what "first" happened to be (it may already have
    // been cached by an earlier test in this binary), a second call
    // right after changing TERM must return the identical cached
    // value -- proving the decision is frozen after the first call.
    REQUIRE(first == second);
}
