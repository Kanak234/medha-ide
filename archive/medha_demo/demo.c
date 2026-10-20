// MEDHĀ IDE — C Doubly Linked List Demo
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
    struct Node* prev;
} Node;

Node* create_node(int data) {
    Node* n = (Node*)malloc(sizeof(Node));
    n->data = data;
    n->next = NULL;
    n->prev = NULL;
    return n;
}

int main() {
    Node* head = create_node(10);
    head->next = create_node(20);
    head->next->prev = head;
    head->next->next = create_node(30);
    head->next->next->prev = head->next;

    printf("MEDHĀ IDE C Demo: Doubly Linked List [10 <-> 20 <-> 30]\n");
    return 0;
}
