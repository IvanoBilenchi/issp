#include "utils.h"
#include <stdio.h>

void correct_usage(void) {
    unsigned char num = 127;

    // A void pointer can hold the address of any type...
    void *void_ptr = &num;

    // ...but it cannot be dereferenced directly:
    //   printf("%d\n", *void_ptr); // Error: dereferencing a void pointer.
    // It must first be cast back to the correct, concrete type.
    unsigned char *typed_ptr = void_ptr;
    printf("Value of `num` through the right type: %u\n", *typed_ptr);
}

void type_confusion_read(void) {
    // Here the void pointer is converted to the WRONG type. The compiler does not reject this. We
    // place `num` next to a known neighbor so the garbage is deterministic rather than random stack
    // contents.
    struct {
        unsigned char num;
        unsigned char neighbors[7];
    } data = { .num = 0x7f, .neighbors = { 0xde, 0xad, 0xbe, 0xef, 0x11, 0x22, 0x33 } };

    print_bytes("Bytes", &data, sizeof(data));

    void *void_ptr = &data.num;
    // `num` is 1 byte, but we read it as an 8-byte value: dereferencing reads 7 bytes past the
    // object (straight into `neighbors`).
    unsigned long long *wrong = void_ptr;
    printf("Read as unsigned long long: 0x%llx\n", *wrong);
    printf("(only the lowest byte, 0x7f, actually belongs to `num`)\n");
}

void type_confusion_write(void) {
    // Writing through a too-large type is even worse: it corrupts the neighbor.
    struct {
        unsigned char num;
        unsigned char neighbors[7];
    } data = { .num = 0x7f, .neighbors = { 0 } };

    print_bytes("Before", &data, sizeof(data));

    void *void_ptr = &data.num;
    unsigned long long *wrong = void_ptr;
    // Storing an 8-byte value writes over `num` AND all of `neighbors`.
    *wrong = 0xffffffffffffffffULL;

    print_bytes("After", &data, sizeof(data));
    printf("`neighbors` was overwritten by a write meant for a 1-byte `num`\n");
}

int main(int argc, char *argv[]) {
    examples_init(argc, argv);
    run_func(correct_usage);
    run_func(type_confusion_read);
    run_func(type_confusion_write);
    return 0;
}
