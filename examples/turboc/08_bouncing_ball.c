/* 08 — Bouncing ball: velocity reverses at the screen edges; stops on a key. */
#include <graphics.h>
#include <conio.h>
#include <dos.h>
int main(void)
{
    int gd = DETECT, gm, x = 100, y = 100, dx = 12, dy = 9, r = 20, steps;
    initgraph(&gd, &gm, "");
    for (steps = 0; steps < 60 && !kbhit(); steps++) {
        cleardevice();
        setcolor(LIGHTGREEN);
        setfillstyle(SOLID_FILL, LIGHTGREEN);
        fillellipse(x, y, r, r);
        x += dx; y += dy;
        if (x - r <= 0 || x + r >= getmaxx()) dx = -dx;   /* hit left/right wall */
        if (y - r <= 0 || y + r >= getmaxy()) dy = -dy;   /* hit top/bottom wall */
        delay(10);
    }
    getch();
    closegraph();
    return 0;
}
