/* 11 — Pie chart of monthly expenses using pieslice with different fill colours. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm, i, start = 0;
    int share[4] = {40, 25, 20, 15};          /* percent */
    int colour[4] = {LIGHTRED, LIGHTGREEN, YELLOW, LIGHTBLUE};
    initgraph(&gd, &gm, "");
    for (i = 0; i < 4; i++) {
        int end = start + share[i] * 360 / 100;
        setfillstyle(SOLID_FILL, colour[i]);
        pieslice(320, 240, start, end, 150);
        start = end;
    }
    outtextxy(230, 420, "Rent Food Travel Books");
    getch();
    closegraph();
    return 0;
}
