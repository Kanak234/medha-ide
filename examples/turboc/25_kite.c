/* 25 — Kite: diamond with drawpoly, two coloured halves, tail with lines. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm;
    int kite[] = {320, 60, 440, 200, 320, 340, 200, 200, 320, 60};
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    drawpoly(5, kite);
    line(320, 60, 320, 340);
    setfillstyle(SOLID_FILL, LIGHTRED);   floodfill(280, 200, WHITE);
    setfillstyle(SOLID_FILL, YELLOW);     floodfill(360, 200, WHITE);
    setcolor(LIGHTGRAY);
    line(320, 340, 300, 400); line(300, 400, 340, 440); line(340, 440, 310, 470);
    getch();
    closegraph();
    return 0;
}
