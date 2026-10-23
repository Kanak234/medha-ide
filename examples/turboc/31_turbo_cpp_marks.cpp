// 31 — Classic Turbo C++ console program: iostream.h, void main, clrscr, getch.
#include <iostream.h>
#include <conio.h>
void main()
{
    clrscr();
    int m[3], total = 0;
    for (int i = 0; i < 3; i++) {
        cout << "Enter marks " << i + 1 << ": ";
        cin >> m[i];
        total += m[i];
    }
    cout << "Total = " << total << endl;
    cout << "Average = " << total / 3.0 << endl;
    getch();
}
