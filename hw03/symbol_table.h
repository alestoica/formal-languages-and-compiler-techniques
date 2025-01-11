#ifndef SYMBOL_TABLE_H
#define SYMBOL_TABLE_H

#include <stdio.h>

typedef struct Node {
    char value[100];
    int index;
    struct Node *left, *right;
} Node;

typedef struct SymbolTable {
    Node *root;
    int current_index;
} SymbolTable;

extern SymbolTable ts;

void collect_nodes(Node *root, Node **node_list, int *count);
int compare_nodes(const void *a, const void *b);
Node* create_node(const char *value, int index);
void insert_node(Node **root, const char *value, int index);
int add_to_symbol_table(const char *value);
void traverse_and_save(Node *root, FILE *file);

#endif
