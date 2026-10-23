/* 03 — Smiley face: circle + floodfill for the face, filled eyes, arc for the smile. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    setcolor(YELLOW);
    circle(320, 240, 120);
    setfillstyle(SOLID_FILL, YELLOW);
    floodfill(320, 240, YELLOW);          /* fill the face up to its yellow border */
    setcolor(BLACK);
    setfillstyle(SOLID_FILL, BLACK);
    fillellipse(275, 200, 15, 20);        /* left eye  */
    fillellipse(365, 200, 15, 20);        /* right eye */
    arc(320, 250, 200, 340, 70);          /* smile     */
    arc(320, 250, 200, 340, 71);
    getch();
    closegraph();
    return 0;
}
