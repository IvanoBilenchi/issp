// 1. Identify the security flaw(s) in this program (type and root cause),
//    and propose the necessary code fix(es).
// 2. Craft a malicious input that bypasses the password check and successfully
//    authenticates as the admin user.

#include <stdio.h>
#include <string.h>

#include "util.h"

#define BUF_SIZE 16
#define PASS_SIZE 16

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);

    struct {
        char buf[BUF_SIZE];
        char password[PASS_SIZE];
    } data;
    random_string(data.password, sizeof(data.password) - 1);

    user_input("Password", data.buf, sizeof(data));
    dlog_var(data);

    if (strcmp(data.buf, data.password)) {
        puts("Access denied.");
        return 1;
    }

    puts("Welcome, admin!");
    return 0;
}
