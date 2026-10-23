/* 26 — Snowman: stacked filled circles, eyes, nose triangle with fillpoly. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm;
    int nose[] = {320, 135, 350, 142, 320, 149};
    initgraph(&gd, &gm, "");
    setbkcolor(BLUE); cleardevice();
    setcolor(WHITE); setfillstyle(SOLID_FILL, WHITE);
    fillellipse(320, 360, 90, 90);
    fillellipse(320, 230, 65, 65);
    fillellipse(320, 130, 45, 45);
    setcolor(BLACK); setfillstyle(SOLID_FILL, BLACK);
    fillellipse(305, 120, 5, 5); fillellipse(335, 120, 5, 5);
    setcolor(LIGHTRED); setfillstyle(SOLID_FILL, LIGHTRED);
    fillpoly(3, nose);
    getch();
    closegraph();
    return 0;
}
