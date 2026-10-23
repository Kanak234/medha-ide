// Inheritance and virtual functions (runtime polymorphism).
#include <iostream>
#include <memory>
#include <vector>
struct Shape { virtual double area() const = 0; virtual ~Shape() = default; };
struct Circle : Shape { double r; explicit Circle(double r) : r(r) {} double area() const override { return 3.14159 * r * r; } };
struct Square : Shape { double s; explicit Square(double s) : s(s) {} double area() const override { return s * s; } };
int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(2));
    shapes.push_back(std::make_unique<Square>(3));
    for (const auto &s : shapes) std::cout << "area = " << s->area() << '\n';
}
