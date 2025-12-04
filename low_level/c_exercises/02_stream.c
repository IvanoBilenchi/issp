// Implement a program that reads a file, encrypts it using a stream cipher,
// and writes the result to a new file. Since stream cypher encryption and
// decryption are the same operation, the same program can be used for both.
//
// File paths and the key should be passed as command line arguments.
// The stream cipher should work by XORing the plaintext with a pseudorandom
// keystream. The keystream should be initialized with a hash of the key.
//
// Test the program by encrypting a file and then decrypting it again using
// the same key. The decrypted file should match the original file.
//
// Hints:
// - The length of the key passed as command line argument can be
//   obtained using the `strlen` function from `<string.h>`. Using
//   `sizeof` on a `char *` variable will return the size of the pointer,
//   not the length of the string it points to.
// - You can use any random number generator to generate the keystream,
//   such as an LCG or a LFSR. The xorshift LFSR is simple and efficient:
//   https://en.wikipedia.org/wiki/xorshift
// - The keystream generator function is essentially a PRNG. It takes
//   a state variable as input and returns an output number. In doing so,
//   it also updates the state variable to a new value, so that the next
//   call to the function will produce a different number.
// - Since the `prng` function generates 64-bit numbers, you can use
//   the lower 8 bits of each generated number as the keystream byte
//   to XOR with the plaintext byte (uint8_t key_byte = prng(state) & 0xFF).

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Buffer {
    size_t size;
    uint8_t *data;
};

/**
 * Retrieves the size of a file.
 *
 * @param path The path to the file.
 * @return The size of the file in bytes, or 0 if the file cannot be opened.
 */
size_t get_file_size(char const *path) {
    FILE *file = fopen(path, "rb");
    if (file == NULL) return 0;
    size_t size = (fseek(file, 0, SEEK_END) == 0) ? ftell(file) : 0;
    fclose(file);
    return size;
}

/**
 * Reads the contents of a file into a buffer.
 *
 * @param path The path to the file.
 * @param buf The buffer to read the file contents into.
 * @return True if the file was read successfully, false otherwise.
 */
bool read_file(char const *path, struct Buffer *buf) {
    FILE *file = fopen(path, "rb");
    if (file == NULL) return false;
    size_t read = fread(buf->data, 1, buf->size, file);
    fclose(file);
    return read == buf->size;
}

/**
 * Writes the contents of a buffer to a file.
 *
 * @param path The path to the file.
 * @param buf The buffer containing the data to write.
 * @return True if the file was written successfully, false otherwise.
 */
bool write_file(char const *path, struct Buffer const *buf) {
    FILE *file = fopen(path, "wb");
    if (file == NULL) return false;
    size_t written = fwrite(buf->data, 1, buf->size, file);
    fclose(file);
    return written == buf->size;
}

uint64_t prng(uint64_t *state) {
    // TO-DO: Implement any simple PRNG. Remember to update the state.
    return *state;
}

uint64_t hash(struct Buffer const *buf) {
    // TO-DO: Reuse the `hash` function from the previous exercise.
    return 0xFFFFFFFFFFFFFFF;
}

void crypt(struct Buffer *buf, struct Buffer const *key) {
    // TO-DO: Implement the stream cipher by XORing each byte of the buffer
    //        with a byte from the keystream. Start by initializing the PRNG
    //        state using the hash of the key.
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: %s <input_file> <output_file> <key>\n", argv[0]);
        return 1;
    }

    char const *input_path = argv[1];
    char const *output_path = argv[2];
    char const *key = argv[3];

    // TO-DO: Read the input file into a suitably sized, dynamically allocated buffer.

    // TO-DO: Encrypt/decrypt the buffer using the stream cipher.

    // TO-DO: Release any allocated memory.

    return 0;
}
