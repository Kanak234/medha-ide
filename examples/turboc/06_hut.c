/* 06 — Hut: polygon roof, rectangle walls, door and window, coloured with floodfill. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm;
    int roof[] = {150, 200, 320, 80, 490, 200, 150, 200};
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    drawpoly(4, roof);
    rectangle(170, 200, 470, 400);
    rectangle(290, 290, 350, 400);   /* door   */
    rectangle(190, 240, 250, 290);   /* window */
    setfillstyle(SOLID_FILL, RED);       floodfill(320, 150, WHITE);
    setfillstyle(SOLID_FILL, BROWN);     floodfill(400, 300, WHITE);
    setfillstyle(SOLID_FILL, DARKGRAY);  floodfill(320, 350, WHITE);
    setfillstyle(SOLID_FILL, LIGHTCYAN); floodfill(220, 265, WHITE);
    getch();
    closegraph();
    return 0;
}
