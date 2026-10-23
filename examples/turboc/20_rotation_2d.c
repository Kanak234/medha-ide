/* 20 — 2D rotation of a triangle about a pivot by 45 degrees. */
#include <graphics.h>
#include <conio.h>
#include <math.h>
int main(void)
{
    int gd = DETECT, gm, i, px = 320, py = 240;
    int p[6] = {320, 240, 450, 240, 400, 140}, q[6];
    double a = 45 * M_PI / 180.0;
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    line(p[0], p[1], p[2], p[3]); line(p[2], p[3], p[4], p[5]); line(p[4], p[5], p[0], p[1]);
    for (i = 0; i < 6; i += 2) {
        double x = p[i] - px, y = p[i + 1] - py;
        q[i] = px + (int)(x * cos(a) - y * sin(a));
        q[i + 1] = py + (int)(x * sin(a) + y * cos(a));
    }
    setcolor(LIGHTCYAN);
    line(q[0], q[1], q[2], q[3]); line(q[2], q[3], q[4], q[5]); line(q[4], q[5], q[0], q[1]);
    getch();
    closegraph();
    return 0;
}
