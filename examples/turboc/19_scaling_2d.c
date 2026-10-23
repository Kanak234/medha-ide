/* 19 — 2D scaling of a rectangle about a fixed point (its corner). */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm;
    float sx = 2.0f, sy = 1.5f;
    int x1 = 100, y1 = 100, x2 = 200, y2 = 180;
    initgraph(&gd, &gm, "");
    setcolor(WHITE);   rectangle(x1, y1, x2, y2);
    setcolor(LIGHTGREEN);
    rectangle(x1, y1, x1 + (int)((x2 - x1) * sx), y1 + (int)((y2 - y1) * sy));
    outtextxy(20, 450, "Scaling sx=2.0 sy=1.5 about (100,100)");
    getch();
    closegraph();
    return 0;
}
