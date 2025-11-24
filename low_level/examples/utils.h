#ifndef UTILS_H
#define UTILS_H

#define run_func(func)                                                                             \
    do {                                                                                           \
        puts(#func);                                                                               \
        printf("%.*s\n", (int)(sizeof(#func) - 1), "------------------------------");              \
        func();                                                                                    \
        puts("");                                                                                  \
    } while (0)

#endif // UTILS_H
