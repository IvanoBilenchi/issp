#include <stdio.h>

int plus_one(int val) {
    return val + 1;
}

int main(void) {
    // Function pointer declaration.
    int (*func)(int);
    // Set the function pointer to the address of the `plus_one` function.
    func = plus_one;
    // Call the function through the function pointer.
    int val = func(1);
    printf("1 + 1 = %d\n", val);
    return 0;
}
