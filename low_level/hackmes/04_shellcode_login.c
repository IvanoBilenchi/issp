// 1. Identify the security flaw(s) in this program (type and root cause),
//    and propose the necessary code fix(es).
// 2. Craft a malicious input that successfully executes the shellcode function.

#include <stdio.h>
#include <string.h>

#include "util.h"

#define BUF_SIZE 16

void shellcode(void) {
    puts("You got shell!");
}

void greet(void) {
    puts("Welcome, admin!");
}

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);
    dlog_fun(greet);
    dlog_fun(shellcode);

    struct {
        char buf[BUF_SIZE];
        void (*auth_success)(void);
    } data = { .auth_success = greet };
    dlog_var(data);

    user_input("Password", data.buf, sizeof(data));
    dlog_var(data);

    if (strcmp(data.buf, "p4ssw0rd") == 0) {
        data.auth_success();
        return 0;
    }

    puts("Authentication failure.");
    return 1;
}
