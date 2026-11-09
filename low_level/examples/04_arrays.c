#include "utils.h"
#include <stdio.h>

#define SIZE 16

// Helper: print `size` elements of an int array on a single line.
void print_array(char const *msg, int *array, size_t size) {
    printf("%s:", msg);
    for (size_t i = 0; i < size; ++i) {
        printf(" %d", array[i]);
    }
    puts("");
}

void contiguous(void) {
    int array[SIZE];

    array[0] = 1;
    array[1] = 2;
    array[2] = 3;
    array[3] = 4;
    array[4] = 5;

    print_array("Initialized", array, 5);

    // Arrays store their elements in a contiguous block of memory: each element sits one
    // `sizeof(int)` after the previous one.
    for (size_t i = 0; i < 5; ++i) {
        printf("&array[%zu] = %p\n", i, (void *)&array[i]);
    }

    // Accessing elements 5..15 reads uninitialized (garbage) memory.
    print_array("Uninitialized", array, SIZE);
}

void out_of_bounds(void) {
    // Local variable order on the stack is not guaranteed, so to make this leak deterministic we
    // place the array next to its "victim" inside a struct, whose field order the standard does
    // guarantee. Reading past the array walks straight into `secret`.
    struct {
        int array[4];
        int secret[4];
    } data = { .array = { 1, 2, 3, 4 }, .secret = { 1111, 2222, 3333, 4444 } };

    print_array("In bounds", data.array, 4);

    // No bounds checking exists in C: array[4], array[5], ... just keep reading the adjacent
    // memory, which here is the secret.
    printf("Out-of-bounds read:");
    for (size_t i = 4; i < 8; ++i) {
        printf(" %d", data.array[i]); // leaks data.secret
    }
    puts("");
}

void initialized(void) {
    // Zero-initialization (the slides use `{ 0 }`, which is portable to C99).
    int array_a[SIZE] = { 0 };
    print_array("Zero-initialized", array_a, SIZE);

    int array_b[SIZE] = { 1, 2, 3, [5] = 4, [7] = 5, [13] = 6 };
    print_array("Zero-initialized with some elements set", array_b, SIZE);

    int array_c[] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
    print_array("All elements set", array_c, SIZE);
}

void sizing(void) {
    int array[SIZE];
    // The size of an array in bytes is its length times the element size.
    printf("sizeof(int): %zu\n", sizeof(int));
    printf("SIZE * sizeof(int): %zu\n", SIZE * sizeof(int));
    printf("sizeof(array): %zu\n", sizeof(array));
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(contiguous);
    run_func(out_of_bounds);
    run_func(initialized);
    run_func(sizing);
    return 0;
}
