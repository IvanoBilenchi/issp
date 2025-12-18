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
    uint64_t hash = 5381;
    for (size_t i = 0; i < buf->size; i++) {
        hash = (hash << 5U) + hash + buf->data[i];
    }
    return hash;
}

void xor_crypt(struct Buffer *buf, struct Buffer const *key) {
    for (size_t i = 0; i < buf->size; i++) {
        buf->data[i] ^= key->data[i % key->size];
    }
}

uint64_t compute_mac(struct Buffer const *data, struct Buffer const *key) {
    uint64_t mac = hash(data);
    struct Buffer hash_buf = { sizeof(mac), (uint8_t *)&mac };
    xor_crypt(&hash_buf, key);
    return mac;
}

bool verify_mac(struct Buffer const *data, struct Buffer const *key, uint64_t mac) {
    return compute_mac(data, key) == mac;
}

int main(void) {
    uint8_t message[] = "This message should be authenticated";
    uint8_t key[] = "s3cr3t_p4ssw0rd";

    struct Buffer msg_buf = { sizeof(message) - 1, message };
    struct Buffer key_buf = { sizeof(key) - 1, key };

    // Compute the MAC of the message.
    uint64_t mac = compute_mac(&msg_buf, &key_buf);
    printf("MAC: 0x%016" PRIX64 "\n", mac);

    // Verify the MAC of the message.
    if (verify_mac(&msg_buf, &key_buf, mac)) {
        puts("Message is authentic");
    } else {
        puts("Message is not authentic");
    }

    // Modify the message and verify the MAC again.
    message[0] = 't';
    if (verify_mac(&msg_buf, &key_buf, mac)) {
        puts("Message is authentic");
    } else {
        puts("Message is not authentic");
    }

    return 0;
}
