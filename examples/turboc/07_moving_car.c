/* 07 — Moving car: draw, wait, erase (cleardevice), move — the classic animation loop. */
#include <graphics.h>
#include <conio.h>
#include <dos.h>
void car(int x)
{
    setcolor(LIGHTRED);
    rectangle(x, 300, x + 160, 340);
    rectangle(x + 30, 260, x + 120, 300);
    setfillstyle(SOLID_FILL, RED);
    floodfill(x + 80, 320, LIGHTRED);
    setcolor(WHITE);
    circle(x + 35, 345, 18);
    circle(x + 125, 345, 18);
}
int main(void)
{
    int gd = DETECT, gm, x;
    initgraph(&gd, &gm, "");
    for (x = 0; x <= 460; x += 20) {
        cleardevice();
        setcolor(GREEN); line(0, 364, 639, 364);   /* road */
        car(x);
        delay(15);
    }
    outtextxy(200, 420, "press any key");
    getch();
    closegraph();
    return 0;
}
