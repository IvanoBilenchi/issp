#include <stdio.h>

int main(int argc, char *argv[]) {
    // The first argument is always the program's invocation name or path.
    printf("Invoked as: %s\n", argv[0]);

    if (argc <= 1) {
        // No names specified.
        puts("Nobody to greet.");
        // Non-zero exit codes signal an error. Inspect it with `echo $?`.
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
