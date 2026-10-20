import { FileItem } from '../types';

export interface DemoProject {
  id: string;
  name: string;
  category: 'AI/ML' | 'Systems' | 'Web' | 'JVM' | 'Database' | 'Mobile';
  description: string;
  language: string;
  files: FileItem[];
}

export const DEMO_PROJECTS: DemoProject[] = [
  {
    id: 'cpp-algo-project',
    name: 'C++ Modern Data Structures & Algorithms Suite',
    category: 'Systems',
    description: 'High-performance C++20 algorithms, BST trees, Quicksort, and memory allocation profiling.',
    language: 'cpp',
    files: [
      {
        id: 'cpp-1',
        name: 'main.cpp',
        path: '/cpp-algo-project/main.cpp',
        type: 'file',
        language: 'cpp',
        content: `#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>

// Binary Search Tree Node definition
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

// Insert into Binary Search Tree - O(log n) average
TreeNode* insertBST(TreeNode* root, int val) {
    if (!root) return new TreeNode(val);
    if (val < root->val) root->left = insertBST(root->left, val);
    else root->right = insertBST(root->right, val);
    return root;
}

// In-order traversal - O(n) Time, O(h) Space
void inOrderTraversal(TreeNode* root) {
    if (!root) return;
    inOrderTraversal(root->left);
    std::cout << root->val << " ";
    inOrderTraversal(root->right);
}

int main() {
    std::cout << "=== MEDHĀ IDE C++ Performance Suite ===" << std::endl;
    
    TreeNode* root = nullptr;
    std::vector<int> data = {45, 12, 78, 3, 24, 61, 89};
    
    for (int val : data) {
        root = insertBST(root, val);
    }
    
    std::cout << "Sorted In-Order BST Traversal: ";
    inOrderTraversal(root);
    std::cout << std::endl;
    
    return 0;
}`
      },
      {
        id: 'cpp-2',
        name: 'CMakeLists.txt',
        path: '/cpp-algo-project/CMakeLists.txt',
        type: 'file',
        language: 'cpp',
        content: `cmake_minimum_required(VERSION 3.20)
project(CppAlgoSuite LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(CppAlgoSuite main.cpp)`
      },
      {
        id: 'cpp-3',
        name: 'README.md',
        path: '/cpp-algo-project/README.md',
        type: 'file',
        language: 'markdown' as any,
        content: `# C++ Data Structures & Algorithms

This demo project showcases high-performance modern C++20 data structures.

## Complexity Summary
- **Insert BST:** Average \`O(log n)\`, Worst \`O(n)\`
- **In-Order Traversal:** \`O(n)\` Time, \`O(h)\` Auxiliary Space
- **Compiler:** GCC 15.2 / Clang LLVM`
      }
    ]
  },
  {
    id: 'python-aiml-project',
    name: 'Python AI/ML & NumPy Data Science Pipeline',
    category: 'AI/ML',
    description: 'Neural network forward pass, matrix operations, complexity evaluation, and model inference.',
    language: 'python',
    files: [
      {
        id: 'py-1',
        name: 'main.py',
        path: '/python-aiml-project/main.py',
        type: 'file',
        language: 'python',
        content: `import time
import math

class SimpleNeuralLayer:
    """
    Single Dense Layer Matrix Operation
    Time Complexity: O(n * m)
    Space Complexity: O(m)
    """
    def __init__(self, input_dim, output_dim):
        self.weights = [[0.05 * (i + j) for j in range(output_dim)] for i in range(input_dim)]
        self.biases = [0.1] * output_dim

    def forward(self, x):
        output = []
        for j in range(len(self.biases)):
            dot_product = sum(x[i] * self.weights[i][j] for i in range(len(x)))
            # ReLU Activation function: max(0, x)
            activated = max(0.0, dot_product + self.biases[j])
            output.append(activated)
        return output

if __name__ == "__main__":
    print("=== MEDHĀ-IDE Python AI/ML Inference Pipeline ===")
    layer = SimpleNeuralLayer(input_dim=4, output_dim=3)
    sample_input = [1.5, -0.8, 2.3, 0.4]
    
    start_time = time.perf_counter()
    output = layer.forward(sample_input)
    elapsed = (time.perf_counter() - start_time) * 1000
    
    print(f"Layer Input Vector: {sample_input}")
    print(f"Activated Output:  {[round(v, 4) for v in output]}")
    print(f"Inference Time:     {elapsed:.4f} ms")`
      },
      {
        id: 'py-2',
        name: 'README.md',
        path: '/python-aiml-project/README.md',
        type: 'file',
        language: 'markdown' as any,
        content: `# Python AI/ML Neural Layer Demo

Demonstrates zero-dependency matrix dot product forward propagation with ReLU activation.

## Complexity
- **Time:** \`O(n × m)\` where n = input_dim and m = output_dim.
- **Space:** \`O(m)\` output allocation.`
      }
    ]
  },
  {
    id: 'ts-web-project',
    name: 'TypeScript & React Offline Web Application',
    category: 'Web',
    description: 'Component-driven web app with offline state persistence, responsive layout, and zero dependencies.',
    language: 'typescript',
    files: [
      {
        id: 'ts-1',
        name: 'App.tsx',
        path: '/ts-web-project/App.tsx',
        type: 'file',
        language: 'typescript',
        content: `import React, { useState } from 'react';

export function App() {
  const [items, setItems] = useState<string[]>(['Offline Cache', 'Monaco Editor', 'Big-O Engine']);
  const [inputVal, setInputVal] = useState('');

  const addItem = () => {
    if (!inputVal.trim()) return;
    setItems([...items, inputVal.trim()]);
    setInputVal('');
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <h1>MEDHĀ-IDE Offline React Component</h1>
      <p>Status: <strong>100% Offline Functional</strong></p>
      
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <input 
          value={inputVal} 
          onChange={(e) => setInputVal(e.target.value)} 
          placeholder="Enter feature title..."
        />
        <button onClick={addItem}>Add Feature</button>
      </div>

      <ul>
        {items.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    </div>
  );
}`
      },
      {
        id: 'ts-2',
        name: 'README.md',
        path: '/ts-web-project/README.md',
        type: 'file',
        language: 'markdown' as any,
        content: `# TypeScript Offline Web App
Demonstrates component state management and reactivity in MEDHĀ IDE.`
      }
    ]
  },
  {
    id: 'c-systems-project',
    name: 'C Systems Memory & Process Control',
    category: 'Systems',
    description: 'ISO C17 standard project with dynamic memory management, pointers, and POSIX process structures.',
    language: 'c',
    files: [
      {
        id: 'c-1',
        name: 'main.c',
        path: '/c-systems-project/main.c',
        type: 'file',
        language: 'c',
        content: `#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* createNode(int data) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (!newNode) return NULL;
    newNode->data = data;
    newNode->next = NULL;
    return newNode;
}

int main() {
    printf("=== MEDHĀ IDE C17 Memory System ===\\n");
    Node* head = createNode(100);
    if (head) {
        head->next = createNode(200);
        printf("Node 1: %d, Node 2: %d\\n", head->data, head->next->data);
        free(head->next);
        free(head);
    }
    printf("Memory freed successfully.\\n");
    return 0;
}`
      }
    ]
  },
  {
    id: 'rust-systems-project',
    name: 'Rust Memory-Safe Concurrency Engine',
    category: 'Systems',
    description: 'Zero-cost abstractions, pattern matching, ownership tracking, and thread-safe data structures.',
    language: 'rust',
    files: [
      {
        id: 'rs-1',
        name: 'main.rs',
        path: '/rust-systems-project/main.rs',
        type: 'file',
        language: 'rust',
        content: `fn main() {
    println!("=== MEDHĀ IDE Rust Engine ===");
    let numbers = vec![1, 2, 3, 4, 5];
    let sum: i32 = numbers.iter().sum();
    println!("Vector sum: {}", sum);
    assert_eq!(sum, 15);
    println!("Ownership verification passed.");
}`
      }
    ]
  },
  {
    id: 'go-backend-project',
    name: 'Go Microservices & Goroutine Pipeline',
    category: 'Systems',
    description: 'Concurrent channel worker pools, struct embedding, and high-performance I/O handling.',
    language: 'go',
    files: [
      {
        id: 'go-1',
        name: 'main.go',
        path: '/go-backend-project/main.go',
        type: 'file',
        language: 'go',
        content: `package main

import "fmt"

func main() {
	fmt.Println("=== MEDHĀ IDE Go Microservice Pipeline ===")
	messages := make(chan string)
	go func() {
		messages <- "Goroutine worker channel active."
	}()
	msg := <-messages
	fmt.Println("Received:", msg)
}`
      }
    ]
  },
  {
    id: 'java-enterprise-project',
    name: 'Java Enterprise OOP & Stream API',
    category: 'JVM',
    description: 'Modern Java 21 Object-Oriented architecture, functional lambda expressions, and collection streams.',
    language: 'java',
    files: [
      {
        id: 'java-1',
        name: 'Main.java',
        path: '/java-enterprise-project/Main.java',
        type: 'file',
        language: 'java',
        content: `import java.util.List;

public class Main {
    public static void main(String[] args) {
        System.out.println("=== MEDHĀ IDE Java 21 Engine ===");
        List<String> items = List.of("Sarasvatī", "Kālī", "Mahālakṣmī", "Vaishnavī");
        items.stream()
             .map(String::toUpperCase)
             .forEach(item -> System.out.println("Subsystem: " + item));
    }
}`
      }
    ]
  }
];
