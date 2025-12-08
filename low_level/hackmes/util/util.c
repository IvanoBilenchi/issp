#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int dlog_enabled = 0;

static void random_reseed(void) {
    srand((unsigned int)time(NULL));
}

void dlog_init(int argc, char *argv[]) {
    random_reseed();
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-d") == 0 || strcmp(argv[i], "--debug") == 0) {
            dlog_enabled = 1;
            break;
        }
    }
}

static void p_dlog_data_small(char const *prompt, unsigned char const *data, size_t size) {
    printf("%s: ", prompt);
    unsigned long long buf = 0;
    for (size_t i = 0; i < size; ++i) {
        buf |= (unsigned long long)data[i] << (i * 8);
    }
    printf("0x%llx\n", buf);
}

void p_dlog_data(char const *prompt, unsigned char const *data, size_t size) {
    printf("[DEBUG] ");

    if (size <= sizeof(unsigned long long)) {
        p_dlog_data_small(prompt, data, size);
        return;
    }

    size_t indent = strlen(prompt) + 2;
    for (size_t i = 0; i < indent; ++i) {
        putchar(' ');
    }
    for (size_t i = 0; i < size; ++i) {
        printf("%2zu ", i);
    }
    printf("\n[DEBUG] %s: ", prompt);
    for (size_t i = 0; i < size; ++i) {
        printf("%02x ", data[i]);
    }
    printf("(%zu bytes)\n", size);
}

void user_input(char const *prompt, char *buf, size_t length) {
    fflush(stdin);
    if (prompt) printf("%s: ", prompt);

    length = length > 1023 ? 1023 : length;
    size_t temp_size = (length * 3) + 1;
    char *temp = calloc(temp_size, sizeof(char));

    if (!fgets(temp, (int)temp_size, stdin)) {
        free(temp);
        return;
    }

    size_t j = 0;
    for (char *c = temp; *c && j < length; ++c, ++j) {
        if (*c == '\n') {
            buf[j] = '\0';
        } else if (*c == '\\') {
            int read;
            sscanf(c + 1, "%2hhx%n", &buf[j], &read);
            c += read;
        } else {
            buf[j] = *c;
        }
    }
    if (j < length) buf[j] = '\0';

    free(temp);
}

static int scan_int(int *n) {
    int ret = scanf("%d", n);
    char c;
    while ((c = getchar()) != '\n' && c != EOF);
    return ret;
}

int user_input_int(char const *prompt) {
    int n;
    while (1) {
        if (prompt) printf("%s: ", prompt);
        if (scan_int(&n) == 1) break;
        puts("Invalid input, please enter an integer.");
    }
    return n;
}

int random_int(void) {
    return rand();
}

void random_string(char *buf, size_t length) {
    char const charset[] = "abcdefghijklmnopqrstuvwxyz0123456789";
    size_t const charset_size = sizeof(charset) - 1;

    for (size_t i = 0; i < length - 1; ++i) {
        int key = rand() % charset_size;
        buf[i] = charset[key];
    }
    buf[length - 1] = '\0';
}
