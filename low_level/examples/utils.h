#ifndef UTILS_H
#define UTILS_H

#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Demo selection: when the program is run with no arguments, all "safe" demos run. When one or more
// demo names are passed on the command line, only those run. This lets a single example hold many
// demos, including a few that crash or abort by design (see `run_unsafe`), without running them
// unless asked.

static int p_demo_argc = 0;
static char **p_demo_argv = NULL;

static inline void examples_init(int argc, char **argv) {
    p_demo_argc = argc;
    p_demo_argv = argv;
}

// Return true if `name` should run: either no names were given, or `name` appears among the
// command-line arguments.
static inline bool p_demo_selected(char const *name) {
    if (p_demo_argc <= 1) return true;
    for (int i = 1; i < p_demo_argc; ++i) {
        if (strcmp(p_demo_argv[i], name) == 0) return true;
    }
    return false;
}

static inline void p_demo_header(char const *name) {
    puts(name);
    printf("%.*s\n", (int)strlen(name), "--------------------------------------------------");
}

// Return the program's name, i.e. argv[0] with any leading path stripped.
static inline char const *p_demo_prog(void) {
    if (p_demo_argc < 1 || p_demo_argv == NULL || p_demo_argv[0] == NULL) return "program";
    char const *slash = strrchr(p_demo_argv[0], '/');
    return slash != NULL ? slash + 1 : p_demo_argv[0];
}

// Run a demo function, printing its name as a header. Safe to run by default.
#define run_func(func)                                                                             \
    do {                                                                                           \
        if (p_demo_selected(#func)) {                                                              \
            p_demo_header(#func);                                                                  \
            func();                                                                                \
            puts("");                                                                              \
        }                                                                                          \
    } while (0)

// Run a demo that may crash or abort by design. It runs only when named explicitly on the command
// line, never as part of a no-argument run. Otherwise it prints a hint so students can discover and
// opt into it.
#define run_unsafe(func)                                                                           \
    do {                                                                                           \
        if (p_demo_argc > 1 && p_demo_selected(#func)) {                                           \
            p_demo_header(#func);                                                                  \
            func();                                                                                \
            puts("");                                                                              \
        } else {                                                                                   \
            printf(#func " (skipped, may crash: run with '%s " #func "')\n", p_demo_prog());       \
        }                                                                                          \
    } while (0)

// Print a labelled pointer value.
static inline void print_addr(char const *label, void const *ptr) {
    printf("%s: %p\n", label, ptr);
}

// Print a labelled hex dump of `size` bytes at `data`, with byte offsets. Useful for inspecting how
// values and padding are laid out in memory.
static inline void print_bytes(char const *label, void const *data, size_t size) {
    unsigned char const *bytes = data;
    size_t indent = strlen(label) + 2;
    for (size_t i = 0; i < indent; ++i) putchar(' ');
    for (size_t i = 0; i < size; ++i) printf("%2zu ", i);
    printf("\n%s: ", label);
    for (size_t i = 0; i < size; ++i) printf("%02x ", bytes[i]);
    printf("(%zu bytes)\n", size);
}

#endif // UTILS_H
