/* 14 — Midpoint circle algorithm using 8-way symmetry. */
#include <graphics.h>
#include <conio.h>
void plot8(int xc, int yc, int x, int y, int c)
{
    putpixel(xc + x, yc + y, c); putpixel(xc - x, yc + y, c);
    putpixel(xc + x, yc - y, c); putpixel(xc - x, yc - y, c);
    putpixel(xc + y, yc + x, c); putpixel(xc - y, yc + x, c);
    putpixel(xc + y, yc - x, c); putpixel(xc - y, yc - x, c);
}
void midpoint_circle(int xc, int yc, int r, int c)
{
    int x = 0, y = r, p = 1 - r;
    while (x <= y) {
        plot8(xc, yc, x, y, c);
        x++;
        if (p < 0) p += 2 * x + 1;
        else { y--; p += 2 * (x - y) + 1; }
    }
}
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    midpoint_circle(320, 240, 150, LIGHTMAGENTA);
    midpoint_circle(320, 240, 80, LIGHTGREEN);
    getch();
    closegraph();
    return 0;
}
