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

void auth_failure(void) {
    puts("Access denied.");
}

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);
    dlog_fun(auth_failure);
    dlog_fun(shellcode);

    struct {
        char buf[BUF_SIZE];
        int authenticated;
        void (*error)(void);
    } data;
    data.authenticated = 0;
    data.error = auth_failure;
    dlog_var(data);

    user_input("Password", data.buf, sizeof(data));

    if (strcmp(data.buf, "p4ssw0rd") == 0) {
        data.authenticated = 1;
    }

    dlog_var(data);

    if (!data.authenticated) {
        data.error();
        return 1;
    }

    puts("Welcome, admin!");
    return 0;
}
