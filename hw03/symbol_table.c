#include "symbol_table.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

SymbolTable ts = {NULL, 1};

void collect_nodes(Node *root, Node **node_list, int *count) {
    if (root == NULL) return;
    collect_nodes(root->left, node_list, count);
    node_list[*count] = root;
    (*count)++;
    collect_nodes(root->right, node_list, count);
}

int compare_nodes(const void *a, const void *b) {
    Node *nodeA = *(Node **)a;
    Node *nodeB = *(Node **)b;
    return nodeA->index - nodeB->index;
}

Node* create_node(const char *value, int index) {
    Node *node = (Node *)malloc(sizeof(Node));
    strcpy(node->value, value);
    node->index = index;
    node->left = node->right = NULL;
    return node;
}

void insert_node(Node **root, const char *value, int index) {
    if (*root == NULL) {
        *root = create_node(value, index);
        return;
    }
    if (strcmp(value, (*root)->value) < 0) {
        insert_node(&(*root)->left, value, index);
    } else if (strcmp(value, (*root)->value) > 0) {
        insert_node(&(*root)->right, value, index);
    }
}

int find_node(Node *root, const char *value) {
    if (root == NULL) {
        return -1;
    }
    if (strcmp(value, root->value) == 0) {
        return root->index;
    } else if (strcmp(value, root->value) < 0) {
        return find_node(root->left, value);
    } else {
        return find_node(root->right, value);
    }
}

int add_to_symbol_table(const char *value) {
    Node *current = ts.root;
    while (current != NULL) {
        if (strcmp(value, current->value) == 0) {
            return current->index;
        } else if (strcmp(value, current->value) < 0) {
            current = current->left;
        } else {
            current = current->right;
        }
    }
    insert_node(&ts.root, value, ts.current_index);
    return ts.current_index++;
}

void traverse_and_save(Node *root, FILE *file) {
    if (root == NULL) return;

    Node *node_list[1000];
    int count = 0;
    collect_nodes(root, node_list, &count);

    qsort(node_list, count, sizeof(Node *), compare_nodes);

    for (int i = 0; i < count; i++) {
        Node *node = node_list[i];
        const char *symbol = node->value;
        int index = node->index;
        int left_index = (node->left != NULL) ? node->left->index : -1;
        int right_index = (node->right != NULL) ? node->right->index : -1;

        if (strlen(symbol) > 3) {
            fprintf(file, "%s\t\t%d\t\t%d\t\t%d\n", symbol, index, left_index, right_index);
        } else {
            fprintf(file, "%s\t\t%d\t\t%d\t\t%d\n", symbol, index, left_index, right_index);
        }
    }
}
