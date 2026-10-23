/* 27 — Rainbow: seven thick arcs in VIBGYOR order. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm, i, t;
    int c[7] = {LIGHTRED, BROWN, YELLOW, LIGHTGREEN, LIGHTBLUE, BLUE, MAGENTA};
    initgraph(&gd, &gm, "");
    for (i = 0; i < 7; i++) {
        setcolor(c[i]);
        for (t = 0; t < 12; t++) arc(320, 400, 0, 180, 250 - i * 12 - t);
    }
    getch();
    closegraph();
    return 0;
}
