/* 29 — conio.h text menu: clrscr, gotoxy, textcolor, cprintf, getch (no graphics mode). */
#include <conio.h>
#include <stdio.h>
void main()
{
    int ch;
    clrscr();
    textcolor(YELLOW);
    gotoxy(30, 5);  cprintf("=== MAIN MENU ===");
    textcolor(LIGHTGREEN);
    gotoxy(30, 7);  cprintf("1. Add record");
    gotoxy(30, 8);  cprintf("2. Show records");
    gotoxy(30, 9);  cprintf("3. Exit");
    textcolor(WHITE);
    gotoxy(30, 11); cprintf("Choice: ");
    ch = getch();
    gotoxy(30, 13); cprintf("You pressed key code %d", ch);
    getch();
}
