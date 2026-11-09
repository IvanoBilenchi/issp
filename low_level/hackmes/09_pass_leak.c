// 1. Identify the security flaw(s) in this program (type and root cause),
//    and propose the necessary code fix(es).
// 2. Craft a malicious input that successfully leaks the secret password.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "util.h"

#define BUF_SIZE 32
#define PASS_SIZE 16

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);

    char *password = malloc(PASS_SIZE);
    random_string(password, PASS_SIZE - 1);
    dlog_var(password);

    char buf[BUF_SIZE];
    while (1) {
        user_input("Password", buf, sizeof(buf) - 1);
        if (strcmp(buf, password) == 0) break;
        printf(buf);
        puts(" is not the correct password.");
    }

    puts("Welcome, admin!");
    free(password);
    return 0;
}
