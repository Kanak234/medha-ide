/* 32 — Move a box with the arrow keys; ESC quits. Shows Turbo's 0 + scan code keys. */
#include <graphics.h>
#include <conio.h>
int main(void)
{
    int gd = DETECT, gm, x = 300, y = 220, key;
    initgraph(&gd, &gm, "");
    for (;;) {
        cleardevice();
        setfillstyle(SOLID_FILL, LIGHTGREEN);
        bar(x, y, x + 40, y + 40);
        outtextxy(10, 460, "arrows move, ESC quits");
        key = getch();
        if (key == 27) break;
        if (key == 0) {                 /* extended key: next byte is the scan code */
            key = getch();
            if (key == 72) y -= 10;     /* up    */
            if (key == 80) y += 10;     /* down  */
            if (key == 75) x -= 10;     /* left  */
            if (key == 77) x += 10;     /* right */
        }
    }
    closegraph();
    return 0;
}
