/* Check whether a number is prime (trial division up to sqrt(n)). */
#include <stdio.h>
int main(void) {
    int n, i, prime = 1;
    printf("Enter a number: ");
    scanf("%d", &n);
    if (n < 2) prime = 0;
    for (i = 2; (long)i * i <= n && prime; i++)
        if (n % i == 0) prime = 0;
    printf("%d is %s\n", n, prime ? "prime" : "not prime");
    return 0;
}
