/* 05 — Indian national flag: three bands, Ashoka Chakra with 24 spokes, pole. */
#include <graphics.h>
#include <conio.h>
#include <math.h>
int main(void)
{
    int gd = DETECT, gm, i, x0 = 150, y0 = 80, w = 360, h = 80;
    double a;
    initgraph(&gd, &gm, "");
    setfillstyle(SOLID_FILL, BROWN);     bar(x0 - 12, y0, x0 - 4, 460);       /* pole       */
    setfillstyle(SOLID_FILL, LIGHTRED);  bar(x0, y0, x0 + w, y0 + h);         /* saffron    */
    setfillstyle(SOLID_FILL, WHITE);     bar(x0, y0 + h, x0 + w, y0 + 2 * h); /* white      */
    setfillstyle(SOLID_FILL, GREEN);     bar(x0, y0 + 2 * h, x0 + w, y0 + 3 * h); /* green  */
    setcolor(BLUE);
    circle(x0 + w / 2, y0 + 3 * h / 2, 35);                                   /* chakra     */
    for (i = 0; i < 24; i++) {                                                /* 24 spokes  */
        a = i * 2 * M_PI / 24;
        line(x0 + w / 2, y0 + 3 * h / 2, x0 + w / 2 + (int)(35 * cos(a)), y0 + 3 * h / 2 + (int)(35 * sin(a)));
    }
    getch();
    closegraph();
    return 0;
}
