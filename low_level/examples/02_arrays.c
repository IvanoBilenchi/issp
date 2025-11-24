#include "utils.h"
#include <stdint.h>
#include <stdio.h>

#define SIZE 16

void print_array(char const *msg, int *array, size_t size) {
    printf("%s:", msg);
    for (size_t i = 0; i < size; ++i) {
        printf(" %d", array[i]);
    }
    puts("");
}

void uninitialized(void) {
    int array[SIZE];

    array[0] = 1;
    array[1] = 2;
    array[2] = 3;
    array[3] = 4;
    array[4] = 5;

    print_array("Initialized", array, 5);
    print_array("Uninitialized", array, SIZE);
    print_array("Out-of-bounds", array, 128);
}

void initialized(void) {
    int array_a[SIZE] = {};
    print_array("Zero-initialized", array_a, SIZE);

    int array_b[SIZE] = { 1, 2, 3, [5] = 4, [7] = 5, [13] = 6 };
    print_array("Zero-initialized with some elements set", array_b, SIZE);

    int array_C[] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
    print_array("All elements set", array_C, SIZE);
}

void sizing(void) {
    int array[SIZE];
    printf("sizeof(int): %zu\n", sizeof(int));
    printf("SIZE * sizeof(int): %zu\n", SIZE * sizeof(int));
    printf("sizeof(array): %zu\n", sizeof(array));
}

int main(void) {
    run_func(uninitialized);
    run_func(initialized);
    run_func(sizing);
    return 0;
}
