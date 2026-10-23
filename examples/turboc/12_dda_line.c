/* 12 — DDA line drawing algorithm with putpixel (no line() used). */
#include <graphics.h>
#include <conio.h>
#include <stdlib.h>
#include <math.h>
void dda(int x1, int y1, int x2, int y2, int colour)
{
    int dx = x2 - x1, dy = y2 - y1, k;
    int steps = abs(dx) > abs(dy) ? abs(dx) : abs(dy);
    float xinc = dx / (float)steps, yinc = dy / (float)steps, x = x1, y = y1;
    for (k = 0; k <= steps; k++) {
        putpixel((int)floor(x + 0.5), (int)floor(y + 0.5), colour);
        x += xinc; y += yinc;
    }
}
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    dda(50, 400, 600, 80, YELLOW);
    dda(50, 80, 600, 400, LIGHTCYAN);
    outtextxy(240, 440, "DDA line algorithm");
    getch();
    closegraph();
    return 0;
}
