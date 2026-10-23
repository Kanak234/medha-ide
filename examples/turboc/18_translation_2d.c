/* 18 — 2D translation of a triangle: P' = P + (tx, ty). Original white, translated yellow. */
#include <graphics.h>
#include <conio.h>
void tri(int p[6], int colour)
{
    setcolor(colour);
    line(p[0], p[1], p[2], p[3]); line(p[2], p[3], p[4], p[5]); line(p[4], p[5], p[0], p[1]);
}
int main(void)
{
    int gd = DETECT, gm, i, tx = 200, ty = 120;
    int p[6] = {100, 200, 200, 100, 250, 220}, q[6];
    initgraph(&gd, &gm, "");
    tri(p, WHITE);
    for (i = 0; i < 6; i += 2) { q[i] = p[i] + tx; q[i + 1] = p[i + 1] + ty; }
    tri(q, YELLOW);
    outtextxy(20, 450, "Translation tx=200 ty=120");
    getch();
    closegraph();
    return 0;
}
