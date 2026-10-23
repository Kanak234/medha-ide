/* 15 — Midpoint ellipse algorithm (two regions). */
#include <graphics.h>
#include <conio.h>
void plot4(int xc, int yc, int x, int y, int c)
{
    putpixel(xc + x, yc + y, c); putpixel(xc - x, yc + y, c);
    putpixel(xc + x, yc - y, c); putpixel(xc - x, yc - y, c);
}
void ellipse_mid(int xc, int yc, long rx, long ry, int c)
{
    long x = 0, y = ry, rx2 = rx * rx, ry2 = ry * ry;
    long px = 0, py = 2 * rx2 * y;
    long p = ry2 - rx2 * ry + rx2 / 4;
    while (px < py) {                                 /* region 1 */
        plot4(xc, yc, (int)x, (int)y, c);
        x++; px += 2 * ry2;
        if (p < 0) p += ry2 + px;
        else { y--; py -= 2 * rx2; p += ry2 + px - py; }
    }
    p = (long)(ry2 * (x + 0.5) * (x + 0.5) + rx2 * (y - 1) * (y - 1) - rx2 * ry2);
    while (y >= 0) {                                  /* region 2 */
        plot4(xc, yc, (int)x, (int)y, c);
        y--; py -= 2 * rx2;
        if (p > 0) p += rx2 - py;
        else { x++; px += 2 * ry2; p += rx2 - py + px; }
    }
}
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    ellipse_mid(320, 240, 220, 120, YELLOW);
    getch();
    closegraph();
    return 0;
}
