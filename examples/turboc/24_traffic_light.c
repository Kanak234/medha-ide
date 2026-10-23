/* 24 — Traffic light: red → yellow → green with delay(). */
#include <graphics.h>
#include <conio.h>
#include <dos.h>
void lamp(int y, int on, int colour)
{
    setfillstyle(SOLID_FILL, on ? colour : DARKGRAY);
    fillellipse(320, y, 40, 40);
}
int main(void)
{
    int gd = DETECT, gm, step;
    int colours[3] = {LIGHTRED, YELLOW, LIGHTGREEN};
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    rectangle(260, 60, 380, 420);
    for (step = 0; step < 3; step++) {
        lamp(120, step == 0, colours[0]);
        lamp(240, step == 1, colours[1]);
        lamp(360, step == 2, colours[2]);
        delay(150);
    }
    getch();
    closegraph();
    return 0;
}
