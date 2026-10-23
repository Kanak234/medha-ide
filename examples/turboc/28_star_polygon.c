/* 28 — Five-pointed star with fillpoly; vertices from polar coordinates. */
#include <graphics.h>
#include <conio.h>
#include <math.h>
int main(void)
{
    int gd = DETECT, gm, i, pts[20];
    initgraph(&gd, &gm, "");
    for (i = 0; i < 10; i++) {
        double r = (i % 2) ? 70 : 170, a = (i * 36 - 90) * M_PI / 180.0;
        pts[2 * i] = 320 + (int)(r * cos(a));
        pts[2 * i + 1] = 240 + (int)(r * sin(a));
    }
    setcolor(YELLOW);
    setfillstyle(SOLID_FILL, YELLOW);
    fillpoly(10, pts);
    getch();
    closegraph();
    return 0;
}
