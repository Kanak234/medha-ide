/* 01 — Hello Graphics: the first graphics.h program of every BCA lab.
   Concepts: initgraph, setcolor, settextstyle, outtextxy, getch, closegraph. */
#include <graphics.h>
#include <conio.h>
void main()
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "C:\\TURBOC3\\BGI");   /* old BGI path is accepted as-is */
    setcolor(YELLOW);
    settextstyle(DEFAULT_FONT, HORIZ_DIR, 3);
    outtextxy(150, 200, "Hello, Graphics!");
    setcolor(LIGHTGRAY);
    settextstyle(DEFAULT_FONT, HORIZ_DIR, 1);
    outtextxy(220, 260, "press any key to exit");
    getch();
    closegraph();
}
