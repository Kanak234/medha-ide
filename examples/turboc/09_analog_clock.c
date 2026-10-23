/* 09 — Analog clock face for 10:10:30 — trig for hand positions, 12 hour marks. */
#include <graphics.h>
#include <conio.h>
#include <math.h>
void hand(int cx, int cy, double angle_deg, int len, int colour)
{
    double a = (angle_deg - 90) * M_PI / 180.0;   /* 0° = 12 o'clock */
    setcolor(colour);
    line(cx, cy, cx + (int)(len * cos(a)), cy + (int)(len * sin(a)));
}
int main(void)
{
    int gd = DETECT, gm, i, cx = 320, cy = 240, h = 10, m = 10, s = 30;
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    circle(cx, cy, 180);
    for (i = 0; i < 12; i++) {
        double a = i * 30 * M_PI / 180.0;
        setfillstyle(SOLID_FILL, YELLOW);
        fillellipse(cx + (int)(160 * cos(a)), cy + (int)(160 * sin(a)), 5, 5);
    }
    hand(cx, cy, (h % 12) * 30 + m * 0.5, 90, LIGHTRED);  /* hour   */
    hand(cx, cy, m * 6, 130, LIGHTGREEN);                 /* minute */
    hand(cx, cy, s * 6, 150, LIGHTCYAN);                  /* second */
    getch();
    closegraph();
    return 0;
}
