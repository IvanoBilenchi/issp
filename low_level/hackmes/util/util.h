#ifndef UTIL_H
#define UTIL_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/// Set to true to enable debug logging.
extern int dlog_enabled;

/**
 * Log a debug message.
 *
 * @param fmt The format string.
 * @param ... The arguments for the format string.
 */
#define dlog(fmt, ...)                                                                             \
    do {                                                                                           \
        if (dlog_enabled) printf("[DEBUG] " fmt, __VA_ARGS__);                                     \
    } while (0)

/**
 * Log the address of a function.
 *
 * @param fun The function to log.
 */
#define dlog_fun(fun)                                                                              \
    do {                                                                                           \
        if (dlog_enabled) printf("[DEBUG] " #fun ": %p\n", fun);                                   \
    } while (0)

/**
 * Log the contents of a variable.
 *
 * @param var The variable to log.
 */
#define dlog_var(var)                                                                              \
    do {                                                                                           \
        if (dlog_enabled) p_dlog_data(#var, (unsigned char const *)&(var), sizeof(var));           \
    } while (0)

/**
 * Initialize the debug logging system.
 *
 * @param argc The argument count from main().
 * @param argv The argument vector from main().
 */
void dlog_init(int argc, char *argv[]);

/**
 * Get user input from stdin.
 *
 * @param prompt The prompt to display to the user.
 * @param buf The buffer to store the user input.
 * @param length The maximum length of the user input.
 *
 * @note Maximum length is capped at 1023 bytes.
 * @note Supports binary input by allowing hex escape sequences,
 *       e.g. "Hi\ff\33" -> 4 bytes message (2 ASCII characters, 2 HEX bytes).
 */
void user_input(char const *prompt, char *buf, size_t length);

/**
 * Get an integer input from stdin.
 *
 * @param prompt The prompt to display to the user.
 *
 * @return The integer input from the user.
 */
int user_input_int(char const *prompt);

/**
 * Generate a random integer.
 *
 * @return A random integer.
 */
int random_int(void);

/**
 * Generate a random string.
 *
 * @param buf The buffer to store the random string.
 * @param length The length of the random string.
 */
void random_string(char *buf, size_t length);

// Private

void p_dlog_data(char const *prompt, unsigned char const *data, size_t size);

#endif // UTIL_H
