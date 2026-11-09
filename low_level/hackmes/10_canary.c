// 1. Identify the security flaw(s) in this program (type and root cause),
//    and propose the necessary code fix(es).
// 2. Craft a malicious input that bypasses the password check and successfully
//    authenticates as the admin user.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "util.h"

#define BUF_SIZE 16
#define PASS_SIZE 16

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);

    int const canary_value = random_int();
    char password[PASS_SIZE];
    random_string(password, sizeof(password) - 1);

    struct {
        char buf[BUF_SIZE];
        int canary;
        int authenticated;
    } data = { .canary = canary_value };
    dlog_var(data);

    user_input("Password", data.buf, sizeof(data));

    if (strcmp(data.buf, password) == 0) {
        data.authenticated = 1;
    }

    dlog_var(data);

    if (data.canary != canary_value) {
        puts("Smashing detected, aborting...");
        return 1;
    }

    if (!data.authenticated) {
        puts("Access denied.");
        return 1;
    }

    puts("Welcome, admin!");
    return 0;
}
