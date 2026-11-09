#include "utils.h"
#include <stdio.h>

void for_while_equivalence(void) {
    // A for loop bundles the init, condition, and step of an equivalent while loop into one line.
    // Both print the same sequence.
    printf("for:  ");
    for (int i = 0; i < 5; ++i) {
        printf("%d ", i);
    }
    puts("");

    // The same loop, written out as a while loop:
    printf("while:");
    int i = 0;
    while (i < 5) {
        printf(" %d", i);
        ++i;
    }
    puts("");
}

static void switch_or_if(int a) {
    printf("a = %d -> switch: ", a);
    switch (a) {
        case 0: puts("zero"); break;
        case 1: puts("one"); break;
        default: puts("other"); break;
    }

    // A switch over a handful of constants is equivalent to an if-else chain.
    printf("a = %d -> if:     ", a);
    if (a == 0) {
        puts("zero");
    } else if (a == 1) {
        puts("one");
    } else {
        puts("other");
    }
}

void switch_if_equivalence(void) {
    // Run a few values through both forms to show they behave identically.
    switch_or_if(0);
    switch_or_if(1);
    switch_or_if(2);
}

void truthiness(void) {
    // Comparisons and logical operators always evaluate to 1 (true) or 0.
    printf("(3 > 2) = %d\n", 3 > 2);
    printf("(2 > 3) = %d\n", 2 > 3);
    printf("(1 && 0) = %d\n", 1 && 0);

    // Any non-zero value is considered true, not just 1.
    int values[] = { 0, 1, -1, 42 };
    for (size_t i = 0; i < sizeof(values) / sizeof(*values); ++i) {
        printf("%d is %s\n", values[i], values[i] ? "true" : "false");
    }
}

static int noisy_true(void) {
    puts("  noisy_true() was called");
    return 1;
}

void short_circuit(void) {
    // In `a && b`, b is only evaluated if a is true. In `a || b`, b is only evaluated if a is
    // false. noisy_true() prints a line when it runs, and each branch prints a line when it is
    // taken, so what is NOT printed below is the point.
    puts("0 && noisy_true():");
    if (0 && noisy_true()) {
        // Never printed: the left operand is false, so `&&` is already false and noisy_true() is
        // never evaluated.
        puts("  branch taken");
    }
    puts("1 || noisy_true():");
    if (1 || noisy_true()) {
        // Printed: the left operand is true, so `||` is already true. The branch runs, yet
        // noisy_true() was still skipped.
        puts("  branch taken");
    }
    puts("(noisy_true() never printed its line: it was skipped both times)");
}

void bitwise(void) {
    // The bitwise operators, printed in hex so the bit patterns are easy to follow (0x0f =
    // 00001111, 0x35 = 00110101).
    unsigned char a = 0x0f;
    unsigned char b = 0x35;
    printf("a        = 0x%02x\n", a);
    printf("b        = 0x%02x\n", b);
    printf("~a       = 0x%02x\n", (unsigned char)~a);
    printf("a & b    = 0x%02x\n", a & b);
    printf("a | b    = 0x%02x\n", a | b);
    printf("a ^ b    = 0x%02x\n", a ^ b);
    printf("b << 1   = 0x%02x\n", (unsigned char)(b << 1));
    printf("b >> 1   = 0x%02x\n", b >> 1);
}

void other_operators(void) {
    // Prefix vs postfix increment: both change the variable, but evaluate to the new and old value
    // respectively.
    int i = 5;
    printf("i++ evaluates to %d, ", i++);
    printf("then i = %d\n", i);
    i = 5;
    printf("++i evaluates to %d, ", ++i);
    printf("then i = %d\n", i);

    // Assignment is an expression: it evaluates to the assigned value.
    int a;
    printf("(a = 7) evaluates to %d\n", a = 7);

    // Compound assignment: a += b is a = a + b.
    a += 3;
    printf("a += 3 -> a = %d\n", a);

    // Ternary conditional operator.
    printf("max(4, 9) = %d\n", 4 > 9 ? 4 : 9);

    // Comma operator: evaluates both, yields the second.
    int b = (puts("  (side effect of comma operator)"), 42);
    printf("comma result = %d\n", b);
}

// A function that takes two parameters and returns a value.
int add_two_integers(int a, int b) {
    return a + b;
}

void functions(void) {
    // Call the function, passing arguments and using its return value.
    int result = add_two_integers(2, 3);
    printf("add_two_integers(2, 3) = %d\n", result);
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(for_while_equivalence);
    run_func(switch_if_equivalence);
    run_func(truthiness);
    run_func(short_circuit);
    run_func(bitwise);
    run_func(other_operators);
    run_func(functions);
    return 0;
}
