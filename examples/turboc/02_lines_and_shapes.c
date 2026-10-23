/* 02 — Basic shapes: line, rectangle, circle, ellipse, arc. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    setcolor(WHITE);       line(20, 20, 620, 20);
    setcolor(LIGHTRED);    rectangle(50, 60, 200, 160);
    setcolor(YELLOW);      circle(320, 110, 50);
    setcolor(LIGHTGREEN);  ellipse(500, 110, 0, 360, 80, 40);
    setcolor(LIGHTCYAN);   arc(320, 330, 0, 180, 100);
    getch();
    closegraph();
    return 0;
}
