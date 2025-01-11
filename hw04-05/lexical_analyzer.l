%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "analyzer.tab.h"

int line_number = 1;

typedef struct {
    char token[100];
    int code;
} AtomCode;

AtomCode atom_codes[] = {
    {"ID", 0},
    {"CONST", 1},
    {"main", 2},
    {"int", 3},
    {"(", 4},
    {")", 5},
    {"{", 6},
    {"}", 7},
    {"return", 8},
    {",", 9},
    {";", 10},
    {"=", 11},
    {"++", 12},
    {"--", 13},
    {"+", 14},
    {"-", 15},
    {"*", 16},
    {"/", 17},
    {"%", 18},
    {"cin", 19},
    {"cout", 20},
    {"endl", 21},
    {">>", 22},
    {"<<", 23},
    {">", 24},
    {"<", 25},
    {"!=", 26},
    {"==", 27},
    {"#", 28},
    {"include", 29},
    {"iostream", 30},
    {"using", 31},
    {"namespace", 32},
    {"std", 33}
};

int get_atom_code(const char *token) {
    for (size_t i = 0; i < sizeof(atom_codes) / sizeof(atom_codes[0]); ++i) {
        if (strcmp(atom_codes[i].token, token) == 0) {
            return atom_codes[i].code;
        }
    }
    return -1;
}

typedef struct Node {
    char value[100];
    int index;
    struct Node *left, *right;
} Node;

typedef struct {
    Node *root;
    int current_index;
} TS;

TS ts = {NULL, 1};

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

void save_ts() {
    FILE *file = fopen("ts.txt", "w");
    if (!file) {
        printf("Failed to open symbol table file.\n");
        return;
    }
    traverse_and_save(ts.root, file);
    fclose(file);
}

typedef struct {
    char token[100];
    int atom_code;
    int atom_code_ts;
} FIP;

FIP fip[1000];
int fip_size = 0;

void add_to_fip(const char *token, int atom_code, int atom_code_ts) {
    strcpy(fip[fip_size].token, token);
    fip[fip_size].atom_code = atom_code;
    fip[fip_size].atom_code_ts = atom_code_ts;
    fip_size++;
}

void save_fip() {
    FILE *file = fopen("fip.txt", "w");
    if (!file) {
        printf("Failed to open FIP file.\n");
        return;
    }
    for (int i = 0; i < fip_size; i++) {
        const char *token = fip[i].token;
        int atom_code = fip[i].atom_code;
        int atom_code_ts = fip[i].atom_code_ts;

        if (atom_code_ts == -1) {
            if (strlen(token) <= 3) {
                fprintf(file, "%s\t\t%d\t\t%s\n", token, atom_code, "-");
            } else if (strlen(token) > 3 && strlen(token) <= 7) {
                fprintf(file, "%s\t\t%d\t\t%s\n", token, atom_code, "-");
            } else if (strlen(token) > 7) {
                fprintf(file, "%s\t%d\t\t%s\n", token, atom_code, "-");
            }
        } else {
            if (strlen(token) <= 3) {
                fprintf(file, "%s\t\t%d\t\t%d\n", token, atom_code, atom_code_ts);
            } else if (strlen(token) > 3 && strlen(token) <= 7) {
                fprintf(file, "%s\t\t%d\t\t%d\n", token, atom_code, atom_code_ts);
            } else if (strlen(token) > 7) {
                fprintf(file, "%s\t%d\t\t%d\n", token, atom_code, atom_code_ts);
            }
        }
    }
    fclose(file);
}
%}

%option noyywrap

DIGIT       [0-9]
LETTER      [a-zA-Z_]
ID          {LETTER}({LETTER}|{DIGIT})*
CONST       {DIGIT}+|[1-9]{DIGIT}+"."{DIGIT}*

%%

[ \t\r]+            { ; }

\n                  { line_number++; }

"int"               { add_to_fip(yytext, get_atom_code(yytext), -1); return INT; }
"main"              { add_to_fip(yytext, get_atom_code(yytext), -1); return MAIN; }
"return"            { add_to_fip(yytext, get_atom_code(yytext), -1); return RETURN; }
"include"           { add_to_fip(yytext, get_atom_code(yytext), -1); return INCLUDE; }
"iostream"          { add_to_fip(yytext, get_atom_code(yytext), -1); return IOSTREAM; }
"using"             { add_to_fip(yytext, get_atom_code(yytext), -1); return USING; }
"namespace"         { add_to_fip(yytext, get_atom_code(yytext), -1); return NAMESPACE; }
"std"               { add_to_fip(yytext, get_atom_code(yytext), -1); return STD; }
"cin"               { add_to_fip(yytext, get_atom_code(yytext), -1); return CIN; }
"cout"              { add_to_fip(yytext, get_atom_code(yytext), -1); return COUT; }
"endl"              { add_to_fip(yytext, get_atom_code(yytext), -1); return ENDL; }

"<="                { add_to_fip(yytext, get_atom_code(yytext), -1); return LE; }
">="                { add_to_fip(yytext, get_atom_code(yytext), -1); return GE; }
"=="                { add_to_fip(yytext, get_atom_code(yytext), -1); return EQ; }
"!="                { add_to_fip(yytext, get_atom_code(yytext), -1); return NE; }
"++"                { add_to_fip(yytext, get_atom_code(yytext), -1); return INC; }
"--"                { add_to_fip(yytext, get_atom_code(yytext), -1); return DEC; }
"+"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return ADD; }
"-"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return SUB; }
"*"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return MUL; }
"/"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return DIV; }
"%"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return MOD; }
"="                 { add_to_fip(yytext, get_atom_code(yytext), -1); return ASSIGN; }
"+="                { add_to_fip(yytext, get_atom_code(yytext), -1); return ADD_ASSIGN; }
"-="                { add_to_fip(yytext, get_atom_code(yytext), -1); return SUB_ASSIGN; }
"*="                { add_to_fip(yytext, get_atom_code(yytext), -1); return MUL_ASSIGN; }
"/="                { add_to_fip(yytext, get_atom_code(yytext), -1); return DIV_ASSIGN; }
"%="                { add_to_fip(yytext, get_atom_code(yytext), -1); return MOD_ASSIGN; }

"<<"                { add_to_fip(yytext, get_atom_code(yytext), -1); return SHL; }
">>"                { add_to_fip(yytext, get_atom_code(yytext), -1); return SHR; }
"<"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return LT; }
">"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return GT; }
"#"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return HASH; }
";"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return SEMICOLON; }
","                 { add_to_fip(yytext, get_atom_code(yytext), -1); return COMMA; }
"{"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return LBRACE; }
"}"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return RBRACE; }
"("                 { add_to_fip(yytext, get_atom_code(yytext), -1); return LPAREN; }
")"                 { add_to_fip(yytext, get_atom_code(yytext), -1); return RPAREN; }

{CONST}             { int index = add_to_symbol_table(yytext); add_to_fip(yytext, get_atom_code("CONST"), index); yylval.ival = atoi(yytext); return CONST; }

{ID}                { int index = add_to_symbol_table(yytext); add_to_fip(yytext, get_atom_code("ID"), index); yylval.sval = strdup(yytext); return ID; }

. {
    printf("Lexical error for character '%s' at line %d\n", yytext, line_number);
    exit(1);
}

%%
