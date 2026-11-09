#include "utils.h"
#include <stddef.h>
#include <stdio.h>

struct MyStruct {
    int int_field;
    float float_field;
    char *string_field;
};

// Helper: print all three fields of a struct on a single line. The `->` operator dereferences the
// pointer and accesses a field in one step.
void print_struct(char const *msg, struct MyStruct *var) {
    printf("%s: %d, %.2f, %s\n", msg, var->int_field, var->float_field, var->string_field);
}

void basic_manipulation(void) {
    // Declare a struct variable, then set each field by name with the dot (`.`) operator.
    struct MyStruct var;
    var.int_field = 10;
    var.float_field = 5.0;
    var.string_field = "Hello";
    print_struct("Set fields", &var);
}

void initialization(void) {
    // The ways to initialize a struct. In every form, any field left unset is zero-initialized.

    // Zero initializer: all fields set to zero.
    struct MyStruct b = { 0 };
    print_struct("Zero initializer", &b);

    // Designated initializer: set chosen fields by name (preferred, as it does not depend on field
    // order).
    struct MyStruct c = { .float_field = 10.0 };
    print_struct("Designated initializer", &c);

    // Positional initializer: values given in field declaration order.
    struct MyStruct d = { 10, 10.0, "Hello" };
    print_struct("Positional initializer", &d);
}

void uninitialized(void) {
    // Reading uninitialized fields is undefined behavior. The garbage char* in `string_field`,
    // printed with %s, is very likely to crash.
    struct MyStruct a;
    print_struct("Uninitialized", &a);
}

void layout(void) {
    // A struct is a single contiguous block, but the compiler inserts padding so each field meets
    // its alignment requirement. Knowing the exact layout matters when reasoning about what sits
    // next to what in memory.
    printf("sizeof(struct MyStruct): %zu\n", sizeof(struct MyStruct));
    printf("offsetof(int_field):    %zu\n", offsetof(struct MyStruct, int_field));
    printf("offsetof(float_field):  %zu\n", offsetof(struct MyStruct, float_field));
    printf("offsetof(string_field): %zu\n", offsetof(struct MyStruct, string_field));

    // Here the fields happen to pack with no gaps (4 + 4 + 8 = 16). Reordering them, e.g. char then
    // int, would force the compiler to insert padding so each field stays aligned, and sizeof would
    // grow accordingly.
    struct MyStruct d = { 10, 10.0, "Hello" };
    print_bytes("Bytes", &d, sizeof(d));
}

int get_int_field_ptr(struct MyStruct *a) {
    return a->int_field;
}

void set_int_field_ptr(struct MyStruct *a, int value) {
    print_addr("  struct address in set_int_field_ptr", a);
    a->int_field = value; // writes through to the caller's struct
}

void set_int_field(struct MyStruct a, int value) {
    print_addr("  struct address in set_int_field    ", &a);
    a.int_field = value; // modifies a local copy; lost on return
}

void functions(void) {
    struct MyStruct a = { .int_field = 5 };
    print_addr("struct address in caller             ", &a);

    // Passing by pointer: the function sees the same struct and its write sticks.
    set_int_field_ptr(&a, 10);
    printf("after set_int_field_ptr(&a, 10): %d\n", a.int_field); // 10

    // Passing by value: the function gets a copy at a different address, so its write has no effect
    // on the caller. That is the answer to the slide's "No effect in the calling function. Why?".
    set_int_field(a, 20);
    printf("after set_int_field(a, 20):      %d\n", a.int_field); // still 10
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(basic_manipulation);
    run_func(initialization);
    run_func(layout);
    run_func(functions);
    run_unsafe(uninitialized);
    return 0;
}
