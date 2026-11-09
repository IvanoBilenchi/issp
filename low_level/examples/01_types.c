#include "utils.h"
#include <limits.h>
#include <stdint.h>
#include <stdio.h>

void sizes(void) {
    // The base data types have implementation-defined sizes. `char` is always 1 byte, but the rest
    // only have minimum guarantees (int >= 2, ...).
    printf("sizeof(char): %zu\n", sizeof(char));
    printf("sizeof(int): %zu\n", sizeof(int));
    printf("sizeof(float): %zu\n", sizeof(float));
    printf("sizeof(double): %zu\n", sizeof(double));

    // Size modifiers select integers of different widths.
    printf("sizeof(short): %zu\n", sizeof(short));
    printf("sizeof(long): %zu\n", sizeof(long));
    printf("sizeof(long long): %zu\n", sizeof(long long));

    // `size_t` holds the size of any object; it is what `sizeof` returns.
    printf("sizeof(size_t): %zu\n", sizeof(size_t));

    // The fixed-size integer types from <stdint.h> have the same size everywhere, which is why we
    // prefer them for portable low-level code.
    printf("sizeof(int8_t): %zu\n", sizeof(int8_t));
    printf("sizeof(int16_t): %zu\n", sizeof(int16_t));
    printf("sizeof(int32_t): %zu\n", sizeof(int32_t));
    printf("sizeof(int64_t): %zu\n", sizeof(int64_t));
}

void casting(void) {
    int a = 10;
    int b = 4;

    // Integer division is performed between a and b, and the result is then converted to a float.
    float res = a / b;
    printf("a / b = %.1f\n", res); // 2.0

    // If we type-cast `a` to a float, the compiler will treat the whole operation as a float
    // division, returning the expected result.
    res = (float)a / b;
    printf("(float)a / b = %.1f\n", res); // 2.5

    // When operands have different types, the compiler converts automatically. Here `a` is promoted
    // to float, so the division is a float division.
    float c = 4;
    printf("a / c = %.1f\n", a / c); // 2.5
}

void overflow(void) {
    // Unsigned integer overflow (and underflow) are well-defined: the value wraps around modulo
    // 2^N, in both directions.
    uint32_t a = 0;
    a--;
    printf("Unsigned underflow: a = %u\n", a); // 2^32 - 1 = 4294967295
    a++;
    printf("Unsigned overflow: a = %u\n", a); // back to 0

    // Signed integer overflow (and underflow) are undefined behavior. Most compilers happen to wrap
    // around too, but the standard guarantees nothing.
    int b = INT_MIN;
    printf("Signed underflow: b = %d\n", --b);
    printf("Signed overflow: b = %d\n", ++b);
}

void initialization(void) {
    // Automatic variables are not initialized by default, leading to undefined behavior if accessed
    // before being assigned a value.
    int a = 42;
    printf("Initialized automatic var: %d\n", a); // Ok

    int b;
    printf("Uninitialized automatic var: %d\n", b); // Undefined behavior

    // Static and global variables are initialized to zero.
    static int c = 42;
    printf("Initialized static var: %d\n", c); // Ok

    static int d;
    printf("Uninitialized static var: %d\n", d); // Also ok
}

void storage_class(void) {
    // An `auto` (default) variable lives on the stack and is recreated, hence reset, every time the
    // block is entered.
    int automatic = 0;
    ++automatic;
    printf("Automatic counter: %d\n", automatic); // Always 1

    // A `static` local variable persists for the whole program lifetime, so it keeps its value
    // across calls.
    static int persistent = 0;
    ++persistent;
    printf("Static counter: %d\n", persistent); // 1, 2, 3, ... across calls
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(sizes);
    run_func(casting);
    run_func(overflow);
    run_func(initialization);
    // Called a few times to show the static counter keeping its value.
    run_func(storage_class);
    run_func(storage_class);
    run_func(storage_class);
    return 0;
}
