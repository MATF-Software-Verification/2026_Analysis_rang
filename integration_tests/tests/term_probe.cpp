// Minimal harness for black-box testing of rang's terminal auto-detection.
// Prints a fixed marker wrapped in fg::red/style::reset under
// control::Auto (the library default), so an external harness can check
// for the presence/absence of ANSI escape bytes depending on whether
// stdout is a real terminal and what $TERM is set to.
#include "rang.hpp"

int main()
{
    rang::setControlMode(rang::control::Auto);
    std::cout << rang::fg::red << "MARK" << rang::style::reset;
    std::cout.flush();
    return 0;
}
