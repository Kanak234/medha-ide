// MEDHĀ STUDIO — Genuine C Doubly Linked List Demo
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
    printf("[MEDHĀ C Demo] Creating Doubly Linked List: 10 <-> 20 <-> 30 <-> 40\n");

    Node* head = create_node(10);
    Node* n2 = create_node(20);
    Node* n3 = create_node(30);
    Node* n4 = create_node(40);

    head->next = n2; n2->prev = head;
    n2->next = n3;   n3->prev = n2;
    n3->next = n4;   n4->prev = n3;

    // Traverse & Print to Terminal
    Node* curr = head;
    printf("Traversing List Nodes: ");
    while (curr) {
        printf("[%d] <-> ", curr->data);
        curr = curr->next;
    }
    printf("NULL\n");

    // Emit live __DSA__ JSON Payload for Real-Time Graphical Canvas
    printf("__DSA__:{\"type\": \"doubly_linked_list\", \"name\": \"head_ptr\", \"nodes\": [10, 20, 30, 40]}\n");

    return 0;
}
