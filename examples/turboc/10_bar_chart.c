/* 10 — 3D bar chart of marks with axis and labels (bar3d + outtextxy). */
#include <graphics.h>
#include <conio.h>
#include <stdio.h>
int main(void)
{
    int gd = DETECT, gm, i;
    int marks[5] = {72, 88, 65, 91, 58};
    char label[8];
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    line(80, 420, 600, 420);   /* x axis */
    line(80, 420, 80, 60);     /* y axis */
    outtextxy(240, 30, "Marks in 5 subjects");
    for (i = 0; i < 5; i++) {
        int x = 110 + i * 95, top = 420 - marks[i] * 3;
        setfillstyle(SOLID_FILL, i + 9);
        bar3d(x, top, x + 50, 420, 12, 1);
        sprintf(label, "%d", marks[i]);
        outtextxy(x + 15, top - 25, label);
    }
    getch();
    closegraph();
    return 0;
}
