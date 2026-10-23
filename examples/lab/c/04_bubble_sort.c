/* Bubble sort of n integers (stops early when already sorted). */
#include <stdio.h>
int main(void) {
    int a[100], n, i, j, t, swapped;
    printf("How many numbers (max 100)? ");
    scanf("%d", &n);
    if (n < 1 || n > 100) return 1;
    printf("Enter %d numbers: ", n);
    for (i = 0; i < n; i++) scanf("%d", &a[i]);
    for (i = 0; i < n - 1; i++) {
        swapped = 0;
        for (j = 0; j < n - 1 - i; j++)
            if (a[j] > a[j + 1]) { t = a[j]; a[j] = a[j + 1]; a[j + 1] = t; swapped = 1; }
        if (!swapped) break;
    }
    printf("Sorted: ");
    for (i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
    return 0;
}
