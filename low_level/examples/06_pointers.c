#include "utils.h"
#include <stdio.h>

void basic_manipulation(void) {
    // Declare and initialize a variable.
    int a = 42;
    // Declare a pointer to an int and initialize it to NULL.
    int *a_ptr = NULL;
    // Take the address of the variable, and store it in the pointer.
    a_ptr = &a;

    printf("Value of `a`: %d\n", a);
    printf("Value of `a_ptr` (address of a): %p\n", (void *)a_ptr);
    printf("Value of `*a_ptr` (dereference): %d\n", *a_ptr);

    // Changing the variable is visible through the pointer...
    a = 43;
    printf("Value of `*a_ptr` after changing `a`: %d\n", *a_ptr);
    // ...and the variable can be modified through the pointer.
    *a_ptr = 44;
    printf("Value of `a` after changing `*a_ptr`: %d\n", a);
}

// Takes a pointer: it can mutate the caller's variable.
void add_to(int *a, int b) {
    *a += b;
}

// Takes the value by copy: changes stay local to this function.
void add_to_value(int a, int b) {
    a += b;
}

void pass_by_pointer_vs_value(void) {
    int a = 10;
    // The caller and the callee refer to the same variable through the pointer.
    printf("Address of `a` in caller:  %p\n", (void *)&a);
    add_to(&a, 5);
    printf("After add_to(&a, 5):       10 + 5 = %d\n", a); // 15

    a = 10;
    // Passing by value copies `a`; the function works on its own copy.
    add_to_value(a, 5);
    printf("After add_to_value(a, 5):  10 + 5 = %d\n", a); // still 10
}

int *get_a(void) {
    int a = 42;
    // Returning the address of a local variable: `a` ceases to exist when this function returns, so
    // the pointer immediately dangles. (Some compilers, such as GCC, even return NULL here, making
    // the dereference crash.)
    return &a;
}

void waste_stack(void) {
    // Reuses the stack slot that `get_a`'s `a` occupied, to show the dangling pointer now reads
    // whatever landed there.
    int filler = 1234;
    printf("(filler = %d)\n", filler);
}

void dangling_pointer(void) {
    int *a_ptr = get_a();
    printf("Value of `*a_ptr` right after return: %d\n", *a_ptr);
    waste_stack();
    printf("Value of `*a_ptr` after another call: %d\n", *a_ptr); // likely changed
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(basic_manipulation);
    run_func(pass_by_pointer_vs_value);
    run_unsafe(dangling_pointer);
    return 0;
}
