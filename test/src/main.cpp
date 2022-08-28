#include "lib.hpp"
#include "lib2.hpp"

#include <iostream>

extern void print_int(int val);

int main() {
    lib::test_print();
    print_int(lib2::mul(6, 7));

    return 0;
}
