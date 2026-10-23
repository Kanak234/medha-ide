/* 30 — Box border drawn with characters using gotoxy/putch and coloured background. */
#include <conio.h>
int main(void)
{
    int i;
    textbackground(BLUE);
    clrscr();
    textcolor(LIGHTCYAN);
    for (i = 10; i <= 70; i++) { gotoxy(i, 5); putch('-'); gotoxy(i, 18); putch('-'); }
    for (i = 5; i <= 18; i++)  { gotoxy(10, i); putch('|'); gotoxy(70, i); putch('|'); }
    textcolor(WHITE);
    gotoxy(30, 11); cprintf("MEDHA Turbo C mode");
    getch();
    return 0;
}
