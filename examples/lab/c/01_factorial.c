/* Factorial of n using a loop and recursion. */
#include <stdio.h>
long fact_rec(int n) { return n <= 1 ? 1 : n * fact_rec(n - 1); }
int main(void) {
    int n, i; long f = 1;
    printf("Enter n: ");
    if (scanf("%d", &n) != 1 || n < 0) { printf("Please enter a non-negative number\n"); return 1; }
    for (i = 2; i <= n; i++) f *= i;
    printf("Loop: %d! = %ld\nRecursion: %d! = %ld\n", n, f, n, fact_rec(n));
    return 0;
}
