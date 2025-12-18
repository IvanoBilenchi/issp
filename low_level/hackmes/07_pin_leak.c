// 1. Identify the security flaw(s) in this program (type and root cause),
//    and propose the necessary code fix(es).
// 2. Craft a malicious input that successfully leaks the secret PIN.

#include <stdio.h>
#include <stdlib.h>

#include "util.h"

#define BUF_SIZE 32

unsigned long random_pin(void) {
    return random_int() % 100000000;
}

unsigned long string_to_pin(char const *str) {
    return strtoul(str, NULL, 10);
}

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);

    struct {
        unsigned long pin;
        char buf[BUF_SIZE];
    } data = { .pin = random_pin() };

    while (1) {
        user_input("8-digit PIN", data.buf, sizeof(data.buf) - 1);
        if (data.pin == string_to_pin(data.buf)) break;
        printf(data.buf);
        puts(" is not the correct PIN.");
        dlog_var(data.buf);
    }

    puts("Welcome, admin!");
    return 0;
}
