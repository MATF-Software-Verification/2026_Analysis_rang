#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest/doctest.h>

#include "rang.hpp"
#include <sstream>
#include <string>

using namespace std;
using namespace rang;

// rang's own test suite (rang/test/test.cpp) only checks that colored
// output "is longer than" / "differs from" the plain string under
// control::Force. These tests instead pin down the *exact* byte sequence
// rang emits for every enum value on the ANSI (Linux) code path, since
// that is the actual contract users of the library rely on.

TEST_CASE("fg emits exact \\033[<code>m sequence for every value")
{
    setControlMode(control::Force);

    ostringstream ss;
    ss << fg::black;
    REQUIRE(ss.str() == "\033[30m");

    ss.str("");
    ss << fg::red;
    REQUIRE(ss.str() == "\033[31m");

    ss.str("");
    ss << fg::green;
    REQUIRE(ss.str() == "\033[32m");

    ss.str("");
    ss << fg::yellow;
    REQUIRE(ss.str() == "\033[33m");

    ss.str("");
    ss << fg::blue;
    REQUIRE(ss.str() == "\033[34m");

    ss.str("");
    ss << fg::magenta;
    REQUIRE(ss.str() == "\033[35m");

    ss.str("");
    ss << fg::cyan;
    REQUIRE(ss.str() == "\033[36m");

    ss.str("");
    ss << fg::gray;
    REQUIRE(ss.str() == "\033[37m");

    ss.str("");
    ss << fg::reset;
    REQUIRE(ss.str() == "\033[39m");
}

TEST_CASE("bg emits exact \\033[<code>m sequence for every value")
{
    setControlMode(control::Force);

    ostringstream ss;
    ss << bg::black;
    REQUIRE(ss.str() == "\033[40m");

    ss.str("");
    ss << bg::yellow;
    REQUIRE(ss.str() == "\033[43m");

    ss.str("");
    ss << bg::gray;
    REQUIRE(ss.str() == "\033[47m");

    ss.str("");
    ss << bg::reset;
    REQUIRE(ss.str() == "\033[49m");
}

TEST_CASE("fgB (bright fg) emits exact \\033[<code>m sequence")
{
    setControlMode(control::Force);

    ostringstream ss;
    ss << fgB::black;
    REQUIRE(ss.str() == "\033[90m");

    ss.str("");
    ss << fgB::gray;
    REQUIRE(ss.str() == "\033[97m");
}

TEST_CASE("bgB (bright bg) emits exact \\033[<code>m sequence")
{
    setControlMode(control::Force);

    ostringstream ss;
    ss << bgB::black;
    REQUIRE(ss.str() == "\033[100m");

    ss.str("");
    ss << bgB::gray;
    REQUIRE(ss.str() == "\033[107m");
}

TEST_CASE("style emits exact \\033[<code>m sequence for every value")
{
    setControlMode(control::Force);

    ostringstream ss;
    ss << style::reset;
    REQUIRE(ss.str() == "\033[0m");

    ss.str("");
    ss << style::bold;
    REQUIRE(ss.str() == "\033[1m");

    ss.str("");
    ss << style::underline;
    REQUIRE(ss.str() == "\033[4m");

    ss.str("");
    ss << style::crossed;
    REQUIRE(ss.str() == "\033[9m");
}

TEST_CASE("multiple modifiers concatenate in stream order without extra bytes")
{
    setControlMode(control::Force);

    ostringstream ss; 
    ss << fg::red << style::bold << "hi" << style::reset;
    REQUIRE(ss.str() == "\033[31m\033[1mhi\033[0m");
}

TEST_CASE("control::Off suppresses every enum category, not just fg")
{
    setControlMode(control::Off);

    ostringstream ss;
    ss << fg::red << bg::blue << fgB::green << bgB::yellow << style::bold
       << "plain";
    REQUIRE(ss.str() == "plain");

    setControlMode(control::Auto);  // restore library default for other tests
}
