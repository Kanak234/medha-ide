/* Array of structures: read 3 students and print the topper. */
#include <stdio.h>
struct student { char name[30]; int marks; };
int main(void) {
    struct student s[3]; int i, top = 0;
    for (i = 0; i < 3; i++) {
        printf("Name and marks of student %d: ", i + 1);
        scanf("%29s %d", s[i].name, &s[i].marks);
        if (s[i].marks > s[top].marks) top = i;
    }
    printf("Topper: %s (%d)\n", s[top].name, s[top].marks);
    return 0;
}
