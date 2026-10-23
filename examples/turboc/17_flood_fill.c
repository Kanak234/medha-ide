/* 17 — floodfill() on overlapping circles: each region gets its own colour. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    circle(270, 240, 100);
    circle(370, 240, 100);
    setfillstyle(SOLID_FILL, LIGHTRED);   floodfill(200, 240, WHITE);
    setfillstyle(SOLID_FILL, LIGHTGREEN); floodfill(320, 240, WHITE);
    setfillstyle(SOLID_FILL, LIGHTBLUE);  floodfill(440, 240, WHITE);
    getch();
    closegraph();
    return 0;
}
