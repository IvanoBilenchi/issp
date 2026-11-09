#include "utils.h"
#include <stdio.h>
#include <string.h>

void basic_manipulation(void) {
    // Initialized from a string literal: the compiler sizes the array to fit the text plus its NULL
    // terminator. Characters can then be changed in place, turning "string" into "strong".
    char string[] = "string";
    string[3] = 'o';
    printf("String: %s\n", string);
    // A string's length (strlen) stops at the NULL terminator; its size (sizeof) includes that
    // terminator, so it is one byte larger.
    printf("String length: %zu\n", strlen(string));
    printf("String size: %zu\n", sizeof(string));
}

void oob_read(void) {
    // We place the buffer right before a secret so the leak is deterministic: field order within a
    // struct is guaranteed, unlike local variable order.
    struct {
        char string[4];
        char secret[8];
    } data;
    memcpy(data.secret, "SECRET!", 8); // includes the trailing '\0'

    // Four characters, but no room left for a NULL terminator.
    data.string[0] = 'a';
    data.string[1] = 'b';
    data.string[2] = 'c';
    data.string[3] = 'd';

    // Without a terminator, printf keeps reading past the buffer until it finds a zero byte,
    // spilling into `secret`: it prints "abcdSECRET!".
    print_bytes("Bytes", &data, sizeof(data));
    printf("String without NULL terminator: %s\n", data.string);

    // Shortening the string and terminating it stops the read at the boundary.
    data.string[3] = '\0';
    printf("String with NULL terminator: %s\n", data.string);
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(basic_manipulation);
    run_func(oob_read);
    return 0;
}
