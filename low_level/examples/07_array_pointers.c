#include "utils.h"
#include <stdint.h>
#include <stdio.h>

void underscore_to_space(char *str) {
    // `str` is a pointer to the caller's array: it sees the same memory, so the edits below are
    // visible to the caller.
    printf("Address of `str` in callee: %p\n", (void *)str);
    for (size_t i = 0; str[i]; ++i) {
        if (str[i] == '_') {
            str[i] = ' ';
        }
    }
}

void array_decays_to_pointer(void) {
    char str[] = "this_was_a_snake_case_string";
    // In almost all contexts an array "decays" to a pointer to its first element, which is why we
    // can pass it to a function taking `char *`.
    printf("Address of `str` in caller: %p\n", (void *)str);
    underscore_to_space(str);
    printf("%s\n", str);
}

void process_array(int32_t const *array, size_t size) {
    // Inside the function the array has already decayed to a pointer, so sizeof(array) is the size
    // of a pointer (8), not of the original array. That is why the length cannot be recovered here
    // and must be passed in.
    printf("sizeof(array) inside callee: %zu (a pointer)\n", sizeof(array));
    printf("Sum of %zu elements:", size);
    int32_t sum = 0;
    for (size_t i = 0; i < size; ++i) {
        sum += array[i];
    }
    printf(" %d\n", sum);
}

void passing_the_size(void) {
    int32_t array[] = { 1, 2, 3, 4, 5 };
    // For plain arrays we must pass the length explicitly, since the callee only receives a
    // pointer. Strings get away without it thanks to the NULL terminator.
    size_t size = sizeof(array) / sizeof(*array);
    printf("sizeof(array) in caller: %zu (the whole array)\n", sizeof(array));
    process_array(array, size);
}

void subscript_on_non_array(void) {
    // `a` is a single int, not an array. Subscripting its pointer past [0] is an out-of-bounds
    // read. We put `a` in a struct next to a known neighbor so the result is deterministic instead
    // of random stack garbage.
    struct {
        int a;
        int neighbors[3];
    } data = { .a = 10, .neighbors = { 111, 222, 333 } };

    int *a_ptr = &data.a;
    printf("Value of `a_ptr[0]`: %d\n", a_ptr[0]); // 10, the int itself
    // a_ptr[1], a_ptr[2], ... walk into the adjacent memory (the neighbors).
    printf("Value of `a_ptr[1]`: %d (out of bounds)\n", a_ptr[1]);
    printf("Value of `a_ptr[2]`: %d (out of bounds)\n", a_ptr[2]);
    printf("Value of `a_ptr[3]`: %d (out of bounds)\n", a_ptr[3]);
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(array_decays_to_pointer);
    run_func(passing_the_size);
    run_func(subscript_on_non_array);
    return 0;
}
