// STL: read numbers into a vector, sort, find max and average.
#include <algorithm>
#include <iostream>
#include <numeric>
#include <vector>
int main() {
    int n;
    std::cout << "How many numbers? ";
    std::cin >> n;
    std::vector<int> v(n);
    std::cout << "Enter them: ";
    for (int &x : v) std::cin >> x;
    std::sort(v.begin(), v.end());
    for (int x : v) std::cout << x << ' ';
    if (!v.empty())
        std::cout << "\nmax = " << v.back() << ", average = " << std::accumulate(v.begin(), v.end(), 0.0) / v.size() << '\n';
}
