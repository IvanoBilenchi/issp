#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Helper: print `size` elements of a double array on a single line.
void print_array(char const *msg, double *arr, size_t size) {
    printf("%s:", msg);
    for (size_t i = 0; i < size; ++i) {
        printf(" %.2f", arr[i]);
    }
    puts("");
}

void basic_usage(void) {
    size_t size = 5;

    // Dynamically allocate an array of `size` doubles on the heap.
    double *arr = malloc(size * sizeof(*arr));

    // Pointers and arrays are closely related, so we index the allocation with the usual array
    // syntax.
    for (size_t i = 0; i < size; ++i) {
        arr[i] = (double)i + 1;
    }
    print_array("Dynamically allocated array", arr, size);

    // Free the memory once we are done with it.
    free(arr);
}

void malloc_vs_calloc(void) {
    size_t size = 8;

    // malloc returns uninitialized memory: reading it before writing is undefined behavior and
    // often yields garbage.
    double *arr = malloc(size * sizeof(*arr));
    print_array("Allocated with malloc", arr, size);
    free(arr);

    // calloc zero-initializes the memory it returns.
    arr = calloc(size, sizeof(*arr));
    print_array("Allocated with calloc", arr, size);
    free(arr);
}

// qsort comparator: it receives `void *` to two elements and must return a negative, zero, or
// positive value when the first sorts before, equal to, or after the second. (a > b) - (a < b)
// yields exactly that, without overflow.
static int compare_doubles(void const *a, void const *b) {
    double da = *(double const *)a;
    double db = *(double const *)b;
    return (da > db) - (da < db);
}

void sort_unknown_size(void) {
    // Motivation for the heap: we don't know the input size at compile time. Here the numbers
    // arrive as strings (as program arguments would), and the count is only known at run time, so
    // we allocate exactly as much as needed instead of guessing a fixed-size (or variable-length)
    // stack array.
    char const *input[] = { "3.5", "1.0", "4.5", "1.5", "9.0", "2.5", "6.0" };
    size_t count = sizeof(input) / sizeof(*input);

    double *numbers = malloc(count * sizeof(*numbers));
    for (size_t i = 0; i < count; ++i) {
        numbers[i] = strtod(input[i], NULL);
    }

    print_array("Before sorting", numbers, count);
    qsort(numbers, count, sizeof(*numbers), compare_doubles);
    print_array("After sorting", numbers, count);

    free(numbers);
}

void memory_leak(void) {
    // Overwriting the only pointer to an allocation before freeing it leaks the memory: there is no
    // longer any way to reach it to call free().
    double *arr = malloc(8 * sizeof(*arr));
    printf("First allocation:  %p\n", (void *)arr);

    // BUG: we reassign `arr` without freeing the first block first.
    arr = malloc(8 * sizeof(*arr));
    printf("Second allocation: %p\n", (void *)arr);
    printf("The first block is now unreachable and cannot be freed (leak).\n");

    free(arr); // frees only the second block
}

void use_after_free(void) {
    char *msg = malloc(16);
    strcpy(msg, "hello");
    printf("Before free: %s\n", msg);

    free(msg);
    // `msg` now dangles. Reusing it is undefined behavior. Allocating the same size often hands
    // back the very same block, so the stale pointer suddenly "sees" unrelated new data.
    char *other = malloc(16);
    strcpy(other, "ATTACKER");
    printf("After free, reading through the stale pointer: %s\n", msg);

    free(other);
}

void heap_overflow(void) {
    char *first = malloc(16);
    char *second = malloc(16);
    strcpy(second, "second buffer");
    print_addr("first ", first);
    print_addr("second", second);
    printf("second before overflow: %s\n", second);

    // Writing more than 16 bytes into `first` runs past its allocation and corrupts adjacent heap
    // memory, here the start of `second`.
    memset(first, 'A', 32);
    printf("second after overflow:  %.13s\n", second);

    free(first);
    free(second);
}

void double_free(void) {
    char *buf = malloc(16);
    free(buf);
    // Freeing the same block twice corrupts the allocator's bookkeeping and typically aborts the
    // program.
    free(buf);
    puts("(if you see this, the double free was not detected)");
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(basic_usage);
    run_func(malloc_vs_calloc);
    run_func(sort_unknown_size);
    run_func(memory_leak);
    run_unsafe(use_after_free);
    run_unsafe(heap_overflow);
    run_unsafe(double_free);
    return 0;
}
