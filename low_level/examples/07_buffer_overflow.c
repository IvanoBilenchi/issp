#include <stdio.h>

void overwrite_string(char *string) {
    for (size_t i = 0; string[i]; i++) {
        string[i] = (char)('A' + (i % 4));
    }
}

int main(void) {
    char important[] = "Important data";
    char string[8] = "Unimportant data";
    overwrite_string(string);
    printf("string: %s\n", string);
    printf("important: %s\n", important);
    return 0;
}
