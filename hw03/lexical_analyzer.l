%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol_table.h"

int line_number = 1;

typedef struct {
    char token[100];
    int code;
} AtomCode;

AtomCode atom_codes[] = {
    {"ID", 0}, {"CONST", 1}, {"main", 2}, {"int", 3}, {"float", 4},
    {"typedef", 5}, {"struct", 6}, {"(", 7}, {")", 8}, {"{", 9},
    {"}", 10}, {"return", 11}, {",", 12}, {";", 13}, {"=", 14},
    {"++", 15}, {"--", 16}, {"+", 17}, {"-", 18}, {"*", 19},
    {"/", 20}, {"%", 21}, {"if", 22}, {"else", 23}, {"cin", 24},
    {"cout", 25}, {"endl", 26}, {">>", 27}, {"<<", 28}, {"while", 29},
    {">", 30}, {"<", 31}, {"!=", 32}, {"==", 33}, {"#", 34},
    {"include", 35}, {"iostream", 36}, {"using", 37}, {"namespace", 38},
    {"std", 39}, {"do", 40}, {"repeta", 41}, {"pana cand", 42}
};

int get_atom_code(const char *token) {
    for (size_t i = 0; i < sizeof(atom_codes) / sizeof(atom_codes[0]); ++i) {
        if (strcmp(atom_codes[i].token, token) == 0) {
            return atom_codes[i].code;
        }
    }
    return -1;
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

void save_ts() {
    FILE *file = fopen("ts.txt", "w");
    if (!file) {
        printf("Failed to open symbol table file.\n");
        return;
    }
    traverse_and_save(ts.root, file);
    fclose(file);
}
%}

%option noyywrap

DIGIT       [0-9]
LETTER      [a-zA-Z_]
ID          {LETTER}({LETTER}|{DIGIT})*
CONST       {DIGIT}+|[1-9]{DIGIT}+"."{DIGIT}*
KEYWORD     "int"|"float"|"main"|"return"|"typedef"|"struct"|"if"|"else"|"while"|"cin"|"cout"|"endl"|"include"|"iostream"|"using"|"namespace"|"std"|"do"|"repeta"|"pana cand"
OPERATOR    "+"|"-"|"*"|"/"|"%"|"!="|"=="|">"|"<"|"="|"++"|"--"
SEPARATOR   "("|")"|"{"|"}"|";"|","|"<<"|">>"|"<"|">"|"#"

%%

[ \t\r]+                    ;

\n { line_number++; }

{KEYWORD} {
    add_to_fip(yytext, get_atom_code(yytext), -1);
}

{OPERATOR} {
    add_to_fip(yytext, get_atom_code(yytext), -1);
}

{SEPARATOR} {
    add_to_fip(yytext, get_atom_code(yytext), -1);
}

{CONST} {
    int index = add_to_symbol_table(yytext);
    add_to_fip(yytext, get_atom_code("CONST"), index);
}

{ID} {
    int index = add_to_symbol_table(yytext);
    add_to_fip(yytext, get_atom_code("ID"), index);
}

. {
    printf("ERROR: Invalid character '%s' at line %d\n", yytext, line_number);
}

%%

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input file>\n", argv[0]);
        exit(1);
    }

    FILE *input_file = fopen(argv[1], "r");
    if (!input_file) {
        perror("fopen");
        exit(1);
    }

    yyin = input_file;
    yylex();

    save_fip();
    save_ts();

    fclose(input_file);
    return 0;
}
