/* 16 — 4-connected boundary fill written by hand (iterative stack, no recursion depth issue). */
#include <graphics.h>
#include <conio.h>
#define MAXS 20000
static int sx[MAXS], sy[MAXS];
void boundary_fill(int x, int y, int fill, int border)
{
    int top = 0;
    sx[top] = x; sy[top] = y; top++;
    while (top > 0) {
        int c;
        top--; x = sx[top]; y = sy[top];
        c = getpixel(x, y);
        if (c == border || c == fill) continue;
        putpixel(x, y, fill);
        if (top + 4 < MAXS) {
            sx[top] = x + 1; sy[top] = y; top++;
            sx[top] = x - 1; sy[top] = y; top++;
            sx[top] = x; sy[top] = y + 1; top++;
            sx[top] = x; sy[top] = y - 1; top++;
        }
    }
}
int main(void)
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    setcolor(WHITE);
    rectangle(250, 180, 390, 300);
    boundary_fill(320, 240, LIGHTBLUE, WHITE);
    getch();
    closegraph();
    return 0;
}
