#include <stdio.h>

int main(int argc, char *argv[]) {
    if (argc <= 1) {
        // No names specified.
        puts("Nobody to greet.");
        return 1;
    }
    /*
      Greet everyone mentioned
      in the program arguments.
    */
    for (int i = 1; i < argc; ++i) {
        printf("%d. Hello, %s!\n", i, argv[i]);
    }
    return 0;
}
