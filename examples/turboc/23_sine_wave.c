/* 23 — Sine wave plotted point by point with putpixel. */
#include <graphics.h>
#include <conio.h>
#include <math.h>
int main(void)
{
    int gd = DETECT, gm, x;
    initgraph(&gd, &gm, "");
    setcolor(DARKGRAY); line(0, 240, 639, 240);
    for (x = 0; x < 640; x++)
        putpixel(x, 240 - (int)(120 * sin(x * 4 * M_PI / 640)), LIGHTGREEN);
    getch();
    closegraph();
    return 0;
}
