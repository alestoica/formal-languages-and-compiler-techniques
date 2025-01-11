%{
#include <stdio.h>
#include <stdlib.h>

extern int yylineno;
extern int yyparse();
extern FILE *yyin;

void yyerror(const char *s);

%}

%union {
    char* str;
}

%token INCLUDE USING NAMESPACE STD INT FLOAT MAIN RETURN STRUCT TYPEDEF CIN COUT ENDL WHILE IF ELSE
%token LT GT EQ NEQ PLUS MINUS MUL DIV MOD INCR DECR ASSIGN
%token ID CONST
%token SEMICOLON COMMA LPAREN RPAREN LBRACE RBRACE

%type <str> ID CONST

%%

program:
    program_headers INT MAIN LPAREN RPAREN LBRACE declarations instruction_list RETURN CONST SEMICOLON RBRACE
    ;

program_headers:
    include_program_header using_program_header
    ;

include_program_header:
    INCLUDE LT "iostream" GT
    ;

using_program_header:
    USING NAMESPACE STD SEMICOLON
    ;

declarations:
    typedef_struct_declaration data_type variable_list SEMICOLON
    | data_type variable_list SEMICOLON
    ;

typedef_struct_declaration:
    TYPEDEF STRUCT LBRACE struct_declarations RBRACE ID SEMICOLON
    ;

struct_declarations:
    struct_declaration
    | struct_declarations struct_declaration
    ;

struct_declaration:
    data_type ID SEMICOLON
    ;

variable_list:
    ID
    | variable_list COMMA ID
    ;

data_type:
    INT
    | FLOAT
    | ID
    ;

instruction_list:
    instruction SEMICOLON
    | instruction_list instruction SEMICOLON
    ;

instruction:
    assign_instruction
    | if_instruction
    | io_instruction
    | while_loop
    ;

assign_instruction:
    ID ASSIGN expression
    | ID operator_assign CONST
    | ID INCR
    | INCR ID
    | ID DECR
    | DECR ID
    ;

operator_assign:
    PLUS ASSIGN
    | MINUS ASSIGN
    ;

expression:
    value
    | expression operator value
    ;

value:
    ID
    | CONST
    ;

if_instruction:
    IF LPAREN boolean_expression RPAREN LBRACE instruction_list RBRACE
    | IF LPAREN boolean_expression RPAREN LBRACE instruction_list RBRACE ELSE LBRACE instruction_list RBRACE
    ;

boolean_expression:
    ID bool_operator expression
    ;

bool_operator:
    LT
    | GT
    | EQ
    | NEQ
    ;

io_instruction:
    CIN io_input SEMICOLON
    | COUT io_output SEMICOLON
    ;

io_input:
    io_input ID
    | ID
    ;

io_output:
    io_output ID
    | ID
    | ENDL
    ;

while_loop:
    WHILE LPAREN boolean_expression RPAREN LBRACE instruction_list RBRACE
    ;

operator:
    PLUS
    | MINUS
    | MUL
    | DIV
    | MOD
    ;

%%

void yyerror(const char *s) {
    printf("Syntax error at line %d: %s\n", yylineno, s);
}
