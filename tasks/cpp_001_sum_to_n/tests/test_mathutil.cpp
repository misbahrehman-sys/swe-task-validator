#include <iostream>

#include "mathutil.h"

static int failures = 0;

static void expect_equal(int actual, int expected, const char* label) {
    if (actual != expected) {
        std::cout << "FAIL " << label << ": expected " << expected
                  << " but got " << actual << "\n";
        ++failures;
    } else {
        std::cout << "ok   " << label << "\n";
    }
}

int main() {
    expect_equal(sum_to_n(0), 0, "sum_to_n(0)");
    expect_equal(sum_to_n(-3), 0, "sum_to_n(-3)");
    expect_equal(sum_to_n(1), 1, "sum_to_n(1)");
    expect_equal(sum_to_n(5), 15, "sum_to_n(5)");
    return failures == 0 ? 0 : 1;
}
