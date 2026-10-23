/* 13 — Bresenham's line algorithm (integer only, all octants). */
#include <graphics.h>
#include <conio.h>
#include <stdlib.h>
void bresenham(int x0, int y0, int x1, int y1, int colour)
{
    int dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
    int dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
    int err = dx + dy, e2;
    for (;;) {
        putpixel(x0, y0, colour);
        if (x0 == x1 && y0 == y1) break;
        e2 = 2 * err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
    }
}
int main(void)
{
    int gd = DETECT, gm, i;
    initgraph(&gd, &gm, "");
    for (i = 0; i <= 600; i += 40)
        bresenham(320, 240, 20 + i, 20, i / 40 % 15 + 1);
    getch();
    closegraph();
    return 0;
}
