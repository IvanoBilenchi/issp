#include "utils.h"
#include <stdio.h>
#include <string.h>

// Overwrites the string in place with the repeating pattern ABCDABCD..., until it reaches a NULL
// terminator. If the buffer is not terminated, it keeps going past the end, corrupting whatever
// follows: an out-of-bounds write.
void overwrite_string(char *string) {
    for (size_t i = 0; string[i]; ++i) {
        string[i] = (char)('A' + (i % 4));
    }
}

void overflow(void) {
    // `string` and `important` are adjacent and in a guaranteed order because they are struct
    // fields. `string` is 8 bytes but gets a 16-char literal, so it is filled completely with no
    // room for a terminator (the compiler warns about this). The overwrite therefore runs off the
    // end of `string` and only stops at the terminator inside `important`, corrupting it.
    struct {
        char string[8];
        char important[15];
    } data;
    memcpy(data.string, "Unimportant data", 8); // exactly 8 bytes, not terminated
    strcpy(data.important, "Important data");

    print_bytes("Before", &data, sizeof(data));
    printf("string before:    %.8s\n", data.string);
    printf("important before: %s\n", data.important);

    overwrite_string(data.string);

    print_bytes("After", &data, sizeof(data));
    printf("string after:     %.8s\n", data.string);
    printf("important after:  %s\n", data.important); // now also ABCD...
}

void stack_locals(void) {
    // The exact code from the slide, with two separate local variables. Whether `string` actually
    // overflows into `important` depends on how the compiler orders locals on the stack, so this is
    // illustrative and not guaranteed. It may also trip the stack protector and abort.
    char important[] = "Important data";
    char string[8] = "Unimportant data";
    print_addr("Address of important", important);
    print_addr("Address of string   ", string);
    overwrite_string(string);
    printf("string: %.8s\n", string);
    printf("important: %s\n", important);
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(overflow);
    run_unsafe(stack_locals);
    return 0;
}
