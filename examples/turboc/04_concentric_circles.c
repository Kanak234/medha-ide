/* 04 — Concentric circles in all 15 colours (loop + setcolor). */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm, r, c = 1;
    initgraph(&gd, &gm, "");
    for (r = 15; r <= 225; r += 15) {
        setcolor(c);
        circle(getmaxx() / 2, getmaxy() / 2, r);
        c = c % 15 + 1;
    }
    getch();
    closegraph();
    return 0;
}
