// 1. Identify the security flaw(s) in this program (type and root cause),
//    and propose the necessary code fix(es).
// 2. Craft a malicious input that successfully executes the shellcode function.

#include <stdio.h>

#include "util.h"

#define BUF_SIZE 16

void shellcode(void) {
    puts("You got shell!");
}

void greet(char const *name) {
    printf("Hello, %s!\n", name);
}

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);
    dlog_fun(greet);
    dlog_fun(shellcode);

    struct {
        char buf[BUF_SIZE];
        void (*fun)(char const *);
    } data;
    data.fun = greet;
    dlog_var(data);

    user_input("User name", data.buf, sizeof(data));
    dlog_var(data);

    data.fun(data.buf);
    return 0;
}
