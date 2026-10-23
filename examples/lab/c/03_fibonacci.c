/* First n Fibonacci numbers. */
#include <stdio.h>
int main(void) {
    int n, i; long a = 0, b = 1, t;
    printf("How many terms? ");
    scanf("%d", &n);
    for (i = 0; i < n; i++) { printf("%ld ", a); t = a + b; a = b; b = t; }
    printf("\n");
    return 0;
}
