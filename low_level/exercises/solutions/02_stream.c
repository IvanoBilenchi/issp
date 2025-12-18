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
    uint64_t x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    return *state = x;
}

uint64_t hash(struct Buffer const *buf) {
    uint64_t hash = 5381;
    for (size_t i = 0; i < buf->size; i++) {
        hash = (hash << 5U) + hash + buf->data[i];
    }
    return hash;
}

void crypt(struct Buffer *buf, struct Buffer const *key) {
    uint64_t state = hash(key);

    // A zero state will generate a keystream of zeros.
    if (!state) state = 0xFFFFFFFF;

    for (size_t i = 0; i < buf->size; i++) {
        uint8_t key_byte = prng(&state) & 0xFF;
        buf->data[i] ^= key_byte;
    }
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: %s <input_file> <output_file> <key>\n", argv[0]);
        return 1;
    }

    char const *input_path = argv[1];
    char const *output_path = argv[2];
    char const *key = argv[3];

    // Read the input file into a suitably sized, dynamically allocated buffer.
    size_t size = get_file_size(input_path);
    if (size == 0) {
        printf("Failed to get file size\n");
        return 1;
    }

    struct Buffer buffer = { .size = size, .data = malloc(size) };
    if (buffer.data == NULL) {
        printf("Failed to allocate memory\n");
        return 1;
    }

    if (!read_file(input_path, &buffer)) {
        printf("Failed to read file\n");
        return 1;
    }

    // Encrypt/decrypt the buffer using the stream cipher.
    struct Buffer key_buf = { .size = strlen(key), .data = (uint8_t *)key };
    crypt(&buffer, &key_buf);

    if (!write_file(output_path, &buffer)) {
        printf("Failed to write file\n");
        return 1;
    }

    // Release any allocated memory.
    free(buffer.data);
    return 0;
}
