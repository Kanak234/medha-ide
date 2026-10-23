/* 22 — Cohen–Sutherland line clipping: grey = original line, green = clipped part. */
#include <graphics.h>
#include <conio.h>
enum { INSIDE = 0, LEFT = 1, RIGHT = 2, BOTTOM = 4, TOP = 8 };
int xmin = 200, ymin = 150, xmax = 440, ymax = 330;
int code(int x, int y)
{
    int c = INSIDE;
    if (x < xmin) c |= LEFT; else if (x > xmax) c |= RIGHT;
    if (y < ymin) c |= TOP;  else if (y > ymax) c |= BOTTOM;
    return c;
}
void clip(int x1, int y1, int x2, int y2)
{
    int c1 = code(x1, y1), c2 = code(x2, y2), accept = 0;
    for (;;) {
        if (!(c1 | c2)) { accept = 1; break; }
        if (c1 & c2) break;
        {
            int c = c1 ? c1 : c2, x = 0, y = 0;
            if (c & TOP)         { x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1); y = ymin; }
            else if (c & BOTTOM) { x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1); y = ymax; }
            else if (c & RIGHT)  { y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1); x = xmax; }
            else                 { y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1); x = xmin; }
            if (c == c1) { x1 = x; y1 = y; c1 = code(x1, y1); }
            else         { x2 = x; y2 = y; c2 = code(x2, y2); }
        }
    }
    if (accept) { setcolor(LIGHTGREEN); line(x1, y1, x2, y2); }
}
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    setcolor(WHITE);    rectangle(xmin, ymin, xmax, ymax);
    setcolor(DARKGRAY); line(100, 100, 550, 400);
    clip(100, 100, 550, 400);
    getch();
    closegraph();
    return 0;
}
