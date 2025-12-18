// 1. Identify the security flaw(s) in this program (type and root cause),
//    and propose the necessary code fix(es).
// 2. Craft a malicious input that successfully leaks the secret string.

#include <stdio.h>

#include "util.h"

#define BUF_SIZE 16
#define SECRET_SIZE 16

int main(int argc, char *argv[]) {
    dlog_init(argc, argv);
    dlog_fun(main);

    struct {
        char buf[BUF_SIZE];
        char secret[SECRET_SIZE];
    } data = { 0 };
    random_string(data.secret, sizeof(data.secret) - 1);

    user_input("Echo", data.buf, sizeof(data.buf));
    dlog_var(data);

    printf("%s\n", data.buf);
    return 0;
}
