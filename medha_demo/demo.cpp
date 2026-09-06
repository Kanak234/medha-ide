// MEDHĀ IDE — C++ Binary Search Tree Demo
#include <iostream>

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}
};

int main() {
    TreeNode* root = new TreeNode(50);
    root->left = new TreeNode(30);
    root->right = new TreeNode(70);
    root->left->left = new TreeNode(20);
    root->left->right = new TreeNode(40);

    std::cout << "MEDHĀ IDE C++ Demo: BST Created with Root (50)\n";
    return 0;
}
