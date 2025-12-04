// Implement the one-time pad (OTP) encryption algorithm.
// If the key is shorter than the message, it should be repeated cyclically.
//
// Hints:
// - Encrypt and decrypt by applying the XOR operation between each byte
//   of the message and the corresponding byte of the key.
// - A simple way to cycle through the key is to use the modulo operator
//   between the current index and the key length.

#include <stdint.h>
#include <stdio.h>

// The buffer struct deals with uint8_t (unsigned char) instead of char
// to allow bitwise operations on the data, which are only well-defined
// for unsigned integer types.
struct Buffer {
    size_t size;   // Size of the buffer.
    uint8_t *data; // Pointer to the buffer data.
};

// Use this to print a buffer containing ASCII data.
void print_string_buffer(struct Buffer const *buf) {
    for (size_t i = 0; i < buf->size; i++) {
        putchar(buf->data[i]);
    }
    puts("");
}

// Use this to print a buffer containing binary data.
void print_binary_buffer(struct Buffer const *buf) {
    for (size_t i = 0; i < buf->size; i++) {
        printf("\\x%02x", buf->data[i]);
    }
    puts("");
}

// Encryption and decryption can be done using the same function,
// as XOR is its own inverse.
void xor_crypt(struct Buffer *buf, struct Buffer const *key) {
    // TO-DO: Implement OTP encryption/decryption.
}

int main(void) {
    uint8_t data[] = "This is a very secret message";
    uint8_t key[] = "s3cr3t_p4ssw0rd";

    // TO-DO: Encrypt `data` in-place using the key, and print the result.

    // TO-DO: Decrypt the result using the key, and print the original message.

    return 0;
}
