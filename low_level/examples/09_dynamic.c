#include "utils.h"
#include <stdio.h>
#include <stdlib.h>

void print_array(char const *msg, double *arr, size_t size) {
    printf("%s:", msg);
    for (size_t i = 0; i < size; i++) {
        printf(" %.2f", arr[i]);
    }
    puts("");
}

void basic_usage(void) {
    size_t size = 5;

    // Dynamically allocate an array of `size` doubles.
    double *arr = malloc(size * sizeof(*arr));

    // Since pointers and arrays are closely related in C, we can use array
    // indexing syntax to access elements of the dynamically allocated array.
    for (size_t i = 0; i < size; i++) {
        arr[i] = (double)i + 1;
    }
    print_array("Dynamically allocated array", arr, 5);

    // Free the dynamically allocated memory when done.
    free(arr);
}

void initialization(void) {
    size_t size = 128;

    // Accessing the memory area returned by malloc before initializing it
    // is undefined behavior. Sometimes we may be lucky and still get zeros,
    // but often we get garbage values.
    double *arr = malloc(size * sizeof(*arr));
    print_array("Allocated with malloc", arr, size);
    free(arr);

    // Using calloc guarantees that the allocated memory is initialized to zero.
    arr = calloc(size, sizeof(*arr));
    print_array("Allocated with calloc", arr, size);
    free(arr);
}

int main(void) {
    run_func(basic_usage);
    run_func(initialization);
    return 0;
}
