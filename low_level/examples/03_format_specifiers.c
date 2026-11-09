#include "utils.h"
#include <stdint.h>
#include <stdio.h>

// This example deliberately misuses printf to show undefined behavior. The compiler will emit
// warnings for the mismatched calls below: those warnings are the whole point, so they are left in
// on purpose.

void common_specifiers(void) {
    // Each specifier tells printf how to interpret and format its argument.
    int n = -42;
    unsigned u = 42;
    size_t z = sizeof(int);
    double d = 3.14159;
    char c = 'A';
    char const *s = "hello";
    void *p = &n;

    printf("%%d  (int):      %d\n", n);
    printf("%%u  (unsigned): %u\n", u);
    printf("%%x  (hex):      %x\n", u);
    printf("%%zu (size_t):   %zu\n", z);
    printf("%%.2f (double):  %.2f\n", d);
    printf("%%c  (char):     %c\n", c);
    printf("%%s  (string):   %s\n", s);
    printf("%%p  (pointer):  %p\n", p);
}

void extra_arguments(void) {
    // More arguments than specifiers: the extras are simply ignored.
    printf("Only one is printed: %d\n", 1, 2, 3);
}

void missing_arguments(void) {
    // Fewer arguments than specifiers: printf reads whatever happens to be in the argument-passing
    // registers or on the stack. This is the basis of format-string attacks, which abuse it to leak
    // memory. The output is garbage and varies from run to run.
    printf("Four unprovided ints: %x %x %x %x\n");
}

void type_mismatch(void) {
    // The specifier and the argument type disagree: %d expects a 4-byte int, but a double is 8
    // bytes with a completely different bit layout.
    double d = 3.14159;
    printf("Reading a double with %%d: %d\n", d);
}

void missing_string_arg(void) {
    // %s with no argument makes printf treat garbage as a char* and follow it. That pointer is
    // almost never valid, so this usually crashes.
    printf("Unprovided string: %s\n");
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(common_specifiers);
    run_func(extra_arguments);
    run_func(missing_arguments);
    run_func(type_mismatch);
    run_unsafe(missing_string_arg);
    return 0;
}
