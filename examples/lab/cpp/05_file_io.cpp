// File handling: write lines to a file, then read them back.
#include <fstream>
#include <iostream>
#include <string>
int main() {
    {
        std::ofstream out("notes.txt");
        out << "MEDHA lab\nfile handling\n";
    }
    std::ifstream in("notes.txt");
    std::string line;
    int n = 0;
    while (std::getline(in, line)) std::cout << ++n << ": " << line << '\n';
}
