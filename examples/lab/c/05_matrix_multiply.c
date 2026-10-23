/* Multiply two 2x2 matrices. */
#include <stdio.h>
int main(void) {
    int a[2][2], b[2][2], c[2][2] = {{0}}, i, j, k;
    printf("Enter matrix A (4 numbers): ");
    for (i = 0; i < 2; i++) for (j = 0; j < 2; j++) scanf("%d", &a[i][j]);
    printf("Enter matrix B (4 numbers): ");
    for (i = 0; i < 2; i++) for (j = 0; j < 2; j++) scanf("%d", &b[i][j]);
    for (i = 0; i < 2; i++) for (j = 0; j < 2; j++) for (k = 0; k < 2; k++) c[i][j] += a[i][k] * b[k][j];
    for (i = 0; i < 2; i++) printf("%d %d\n", c[i][0], c[i][1]);
    return 0;
}
