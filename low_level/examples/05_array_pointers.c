#include "utils.h"
#include <stdio.h>

void underscore_to_space(char *str) {
    for (size_t i = 0; str[i]; ++i) {
        if (str[i] == '_') {
            str[i] = ' ';
        }
    }
}

void string_manipulation(void) {
    char str[] = "this_was_a_snake_case_string";
    underscore_to_space(str);
    printf("%s\n", str);
}

void array_pointer_behavior(void) {
    int a = 10;
    int *a_ptr = &a;
    printf("Value of `a`: %d\n", a);
    printf("Value of `a_ptr[0]`: %d\n", a_ptr[0]);
    printf("Value of `a_ptr[1]`: %d\n", a_ptr[1]);
    printf("Value of `a_ptr[2]`: %d\n", a_ptr[2]);
    printf("Value of `a_ptr[3]`: %d\n", a_ptr[3]);
}

int main(void) {
    run_func(string_manipulation);
    run_func(array_pointer_behavior);
    return 0;
}
