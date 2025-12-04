#include "utils.h"
#include <stdio.h>

void basic_manipulation(void) {
    int a = 42;
    int *a_ptr = NULL;
    a_ptr = &a;
    printf("Value of `a`: %d\n", a);
    printf("Value of `a_ptr`: %p\n", a_ptr);
    printf("Value of `*a_ptr`: %d\n", *a_ptr);
    a = 43;
    printf("Value of `*a_ptr` after changing `a`: %d\n", *a_ptr);
    *a_ptr = 44;
    printf("Value of `a` after changing `*a_ptr`: %d\n", a);
}

void add_to(int *a, int b) {
    *a += b;
}

void manipulation_via_pointer(void) {
    int a = 10;
    add_to(&a, 5);
    printf("10 + 5 = %d\n", a);
}

int *get_a(void) {
    int a = 42;
    return &a;
}

void dangling_pointer(void) {
    int *a_ptr = get_a();
    printf("Value of `*a_ptr`: %d\n", *a_ptr);
}

void type_confusion(void) {
    unsigned char num = 127;
    printf("Value of `num`: %u (%x)\n", num, num);

    void *void_ptr = &num;
    unsigned *typed_ptr = void_ptr;
    printf("Value of `*((unsigned *)&num)`: %u (%x)\n", *typed_ptr, *typed_ptr);
}

int main(void) {
    run_func(basic_manipulation);
    run_func(manipulation_via_pointer);
    run_func(dangling_pointer);
    run_func(type_confusion);
    return 0;
}
