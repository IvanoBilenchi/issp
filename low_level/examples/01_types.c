#include "utils.h"
#include <limits.h>
#include <stdio.h>

void division(void) {
    int a = 10;
    int b = 4;

    // Integer division is performed between a and b,
    // and the result is then converted to a float.
    float res = a / b;
    printf("a / b = %.1f\n", res); // 2.0

    // If we type-cast `a` to a float, the compiler
    // will treat the whole operation as a float
    // division, returning the expected result.
    res = (float)a / b;
    printf("(float)a / b = %.1f\n", res); // 2.5
}

void overflow(void) {
    // Unsigned integer overflow (and underflow) are
    // well-defined, causing wrap-around behavior.
    unsigned a = 0;
    printf("Unsigned underflow: a = %u\n", --a);
    printf("Unsigned overflow: a = %u\n", ++a);

    // Signed integer overflow (and underflow) cause
    // undefined behavior, though most compilers
    // implement wrap-around behavior as well.
    int b = INT_MIN;
    printf("Signed underflow: b = %d\n", --b);
    printf("Signed overflow: b = %d\n", ++b);
}

void initialization(void) {
    // Automatic variables are not initialized by default,
    // leading to undefined behavior if accessed before
    // being assigned a value.
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

int main(void) {
    run_func(division);
    run_func(overflow);
    run_func(initialization);
    return 0;
}
