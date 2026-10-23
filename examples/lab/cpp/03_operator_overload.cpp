// Operator overloading: add two complex numbers with +.
#include <iostream>
struct Complex {
    double re, im;
    Complex operator+(const Complex &o) const { return {re + o.re, im + o.im}; }
};
std::ostream &operator<<(std::ostream &os, const Complex &c) { return os << c.re << " + " << c.im << "i"; }
int main() {
    Complex a{1.5, 2}, b{0.5, -4};
    std::cout << a << "  plus  " << b << "  =  " << a + b << '\n';
}
