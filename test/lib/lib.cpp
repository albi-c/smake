#include "lib.hpp"

#include "util/util.hpp"

#include <iostream>

namespace lib {
    void test_print() {
        std::cout << "Hello! " << lib::add(2, 8) << "\n";
    }
};
