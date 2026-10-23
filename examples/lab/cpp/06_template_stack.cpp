// Class template: a simple stack for any type.
#include <iostream>
#include <stdexcept>
#include <vector>
template <typename T> class Stack {
    std::vector<T> data;
public:
    void push(const T &x) { data.push_back(x); }
    T pop() { if (data.empty()) throw std::runtime_error("stack empty"); T x = data.back(); data.pop_back(); return x; }
    bool empty() const { return data.empty(); }
};
int main() {
    Stack<int> s;
    for (int i = 1; i <= 3; i++) s.push(i * 10);
    while (!s.empty()) std::cout << s.pop() << ' ';
    std::cout << '\n';
}
