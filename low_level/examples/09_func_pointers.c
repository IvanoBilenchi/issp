#include <stdint.h>
#include <stdio.h>

// Two functions with the same signature `int (int)`, so a single function pointer of that type can
// be made to point at either one.
int plus_one(int val) {
    return val + 1;
}

int minus_one(int val) {
    return val - 1;
}

int main(void) {
    // A function pointer stores the address of a function.
    int (*func)(int);

    // Point it at `plus_one` and call through it.
    func = plus_one;
    printf("func -> plus_one  (%p)\n", (void *)(uintptr_t)func);
    printf("func(1) = %d\n", func(1));

    // The pointer value alone decides which function runs. Repointing it makes the very same call
    // site run different code: an attacker who manages to overwrite a function pointer can redirect
    // execution to another function.
    func = minus_one;
    printf("func -> minus_one (%p)\n", (void *)(uintptr_t)func);
    printf("func(1) = %d\n", func(1));

    return 0;
}
