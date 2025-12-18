// Implement a simple 64 bit message authentication code (MAC) by encrypting
// a digest using the `xor_crypt` function from the previous exercise.
//
// Hints:
// - You can choose any hash function you like, even a non-cryptographic one.
//   One simple hash function is djb2: http://www.cse.yorku.ca/~oz/hash.html
// - When encrypting the hash to produce the MAC, you can treat the hash value
//   as a buffer by using its address and size:
//
//   uint64_t mac = hash(data);
//   struct Buffer hash_buf = { sizeof(mac), (uint8_t *)&mac };
//   ...
//
//   Note: Normally, accessing a variable through a pointer of a different type
//         leads to undefined behavior. However, in the specific case of using
//         a pointer to a character type (e.g. uint8_t*), it is explicitly
//         allowed by the C standard.

#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

struct Buffer {
    size_t size;
    uint8_t *data;
};

uint64_t hash(struct Buffer const *buf) {
    // TO-DO: Compute and return a 64-bit hash of the given buffer.
    return 0xFFFFFFFFFFFFFFFF;
}

void xor_crypt(struct Buffer *buf, struct Buffer const *key) {
    // TO-DO: Reuse the `xor_crypt` function from the previous exercise.
}

uint64_t compute_mac(struct Buffer const *data, struct Buffer const *key) {
    // TO-DO: Compute and return a 64-bit MAC for the given data and key.
    return 0xFFFFFFFFFFFFFFFF;
}

bool verify_mac(struct Buffer const *data, struct Buffer const *key, uint64_t mac) {
    // TO-DO: Verify that the provided MAC matches the computed MAC.
    return false;
}

int main(void) {
    uint8_t message[] = "This message should be authenticated";
    uint8_t key[] = "s3cr3t_p4ssw0rd";

    struct Buffer msg_buf = { sizeof(message) - 1, message };
    struct Buffer key_buf = { sizeof(key) - 1, key };

    // TO-DO: Compute the MAC of the message.

    // TO-DO: Verify the MAC of the message.

    // TO-DO: Modify the message and verify the MAC again.

    return 0;
}
