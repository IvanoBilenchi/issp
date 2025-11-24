#include "utils.h"
#include <stdio.h>

struct MyStruct {
    int int_field;
    float float_field;
    char *string_field;
};

void print_struct(char const *msg, struct MyStruct *var) {
    printf("%s: %d, %.2f, %s\n", msg, var->int_field, var->float_field, var->string_field);
}

void basic_manipulation(void) {
    struct MyStruct var;
    var.int_field = 10;
    var.float_field = 5.0;
    var.string_field = "Hello";
    print_struct("Set fields", &var);
}

void initialization(void) {
    struct MyStruct a;
    print_struct("Uninitialized", &a);

    struct MyStruct b = {};
    print_struct("Zero initializer", &b);

    struct MyStruct c = { .float_field = 10.0 };
    print_struct("Designated initializer", &c);

    struct MyStruct d = { 10, 10.0, "Hello" };
    print_struct("Positional initializer", &d);
}

int get_int_field(struct MyStruct a) {
    return a.int_field;
}
int get_int_field_ptr(struct MyStruct *a) {
    return a->int_field;
}
void set_int_field_ptr(struct MyStruct *a, int value) {
    a->int_field = value;
}
void set_int_field(struct MyStruct a, int value) {
    a.int_field = value;
}

void functions(void) {
    struct MyStruct a = { .int_field = 5 };

    printf("get_int_field(a): %d\n", get_int_field(a));
    printf("get_int_field_ptr(&a): %d\n", get_int_field_ptr(&a));

    set_int_field_ptr(&a, 10);
    printf("set_int_field_ptr(&a, 10): %d\n", a.int_field);

    set_int_field(a, 20);
    printf("set_int_field(a, 20): %d\n", a.int_field);
}

int main(void) {
    run_func(basic_manipulation);
    run_func(initialization);
    run_func(functions);
    return 0;
}
