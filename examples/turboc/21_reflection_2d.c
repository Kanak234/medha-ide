/* 21 — Reflection of a triangle about the x axis drawn through the screen centre. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm, cy = 240;
    int p[6] = {200, 100, 300, 200, 150, 200};
    initgraph(&gd, &gm, "");
    setcolor(DARKGRAY); line(0, cy, 639, cy);             /* mirror line */
    setcolor(WHITE);
    line(p[0], p[1], p[2], p[3]); line(p[2], p[3], p[4], p[5]); line(p[4], p[5], p[0], p[1]);
    setcolor(LIGHTMAGENTA);                                /* y' = 2*cy - y */
    line(p[0], 2 * cy - p[1], p[2], 2 * cy - p[3]);
    line(p[2], 2 * cy - p[3], p[4], 2 * cy - p[5]);
    line(p[4], 2 * cy - p[5], p[0], 2 * cy - p[1]);
    getch();
    closegraph();
    return 0;
}
