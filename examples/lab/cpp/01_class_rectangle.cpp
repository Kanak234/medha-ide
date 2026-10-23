// Class with constructor and member functions.
#include <iostream>
class Rectangle {
    double w, h;
public:
    Rectangle(double width, double height) : w(width), h(height) {}
    double area() const { return w * h; }
    double perimeter() const { return 2 * (w + h); }
};
int main() {
    double w, h;
    std::cout << "Width and height: ";
    std::cin >> w >> h;
    Rectangle r(w, h);
    std::cout << "Area = " << r.area() << ", Perimeter = " << r.perimeter() << '\n';
}
