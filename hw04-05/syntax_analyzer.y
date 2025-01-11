%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

extern void save_fip();
extern void save_ts();

extern int yylex();
extern int yyparse();
extern FILE* yyin;

extern int line_number;
void yyerror(char *s);

int nrTemp = 1;

void newTempVariable(char* s) {
    sprintf(s, "temp%d", nrTemp);
    nrTemp++;
}

char variables[100][100];
int nrVariables = 0;

void addVariable(char* s) {
    for(int i = 0; i < nrVariables; i++)
        if(strcmp(variables[i], s) == 0)
            return;

    memset(variables[nrVariables], 0, sizeof(variables[nrVariables]));
    strncpy(variables[nrVariables], s, sizeof(variables[nrVariables]) - 1);
    nrVariables++;
}

char instructions[100][700];
int nrInstructions = 0;

void addInstruction(char s[]) {
	strcpy(instructions[nrInstructions++], s);
}

int isNumeric(char *s) {
    char firstChar = *s;
    return (firstChar >= '0' && firstChar <= '9');
}

void addBracketsAroundString(char *s) {
    if (s == NULL || *s == '\0')
        return;
    size_t length = strlen(s);
    memmove(s + 1, s, length + 1);
    s[0] = '[';
    s[length + 1] = ']';
    s[length + 2] = '\0';
}

%}

%union {
    int ival;
    char *sval;
    struct {
        char varName[100];
        char code[700];
    } expr;
}

%token <ival> CONST
%token <sval> ID
%token INT MAIN RETURN INCLUDE USING NAMESPACE STD CIN COUT IOSTREAM
%token SHL SHR LT GT LE GE EQ NE INC DEC ADD SUB MUL DIV MOD ASSIGN ADD_ASSIGN SUB_ASSIGN MUL_ASSIGN DIV_ASSIGN MOD_ASSIGN INCLUDE_IOSTREAM
%token SEMICOLON LBRACE RBRACE LPAREN RPAREN COMMA ENDL HASH

%type <expr> expression value assign_instruction
%type <sval> operator arithmetic_assignment

%%

program:
    program_headers INT MAIN LPAREN RPAREN LBRACE declarations instruction_list RETURN CONST SEMICOLON RBRACE
    ;

program_headers:
    include_program_header using_program_header
    ;

include_program_header:
    HASH INCLUDE LT IOSTREAM GT
    ;

using_program_header:
    USING NAMESPACE STD SEMICOLON
    ;

declarations:
    /* empty */
    | data_type variable_list SEMICOLON declarations
    ;

variable_list:
    ID { addVariable($1); }
    | ID COMMA variable_list { addVariable($1); }
    ;

data_type:
    INT
    ;

instruction_list:
    /* empty */
    | instruction instruction_list
    ;

instruction:
    io_instruction
    | assign_instruction
    ;

io_instruction:
    i_instruction
    | o_instruction
    ;

i_instruction:
    CIN SHR ID SEMICOLON {
        char instr[700];
        sprintf(instr, "\n mov EAX, %s\n push EAX\n push dword read_int_fmt\n call [scanf]\n add ESP, 8", $3);
        addInstruction(instr);
    }
    ;

o_instruction:
    COUT SHL ID SEMICOLON {
        char instr[700];
        sprintf(instr, "\n mov EAX, [%s]\n push EAX\n push dword write_int_fmt\n call [printf]\n add ESP, 8\n", $3);
        addInstruction(instr);
    }
    | COUT SHL ENDL SEMICOLON {
        char instr[700];
        sprintf(instr, "\n push dword write_line_fmt\n call [printf]\n add ESP, 4\n");
        addInstruction(instr);
    }
    ;

assign_instruction:
    ID ASSIGN expression SEMICOLON {
        addInstruction($3.code);

        if (isNumeric($3.varName)) {
           char instr[700];
           sprintf(instr, "\n mov eax, %s\n", $3.varName);
           addInstruction(instr);
        } else {
           char instr[700];
           sprintf(instr, "\n mov eax, [%s]\n", $3.varName);
           addInstruction(instr);
        }

        char instr[700];
        sprintf(instr, "\n mov [%s], eax\n", $1);
        addInstruction(instr);
    }
    | ID arithmetic_assignment value SEMICOLON {
        newTempVariable($$.varName);
        addVariable($$.varName);
        sprintf($$.code, "\n %s\n %s\n", "", $3.code);

        if (!isNumeric($3.varName))
            addBracketsAroundString($3.varName);

        char instr[700];
        if (strcmp($2, "ADD_ASSIGN") == 0) {
           sprintf(instr, "\n mov eax, [%s]\n add eax, %s\n mov [%s], eax\n", $1, $3.varName, $$.varName);
        } else if (strcmp($2, "SUB_ASSIGN") == 0) {
           sprintf(instr, "\n mov eax, [%s]\n sub eax, %s\n mov [%s], eax\n", $1, $3.varName, $$.varName);
        } else if (strcmp($2, "MUL_ASSIGN") == 0) {
           sprintf(instr, "\n mov eax, [%s]\n imul eax, %s\n mov [%s], eax\n", $1, $3.varName, $$.varName);
        } else if (strcmp($2, "DIV_ASSIGN") == 0) {
           sprintf(instr, "\n mov eax, [%s]\n mov edx, 0\n div %s\n mov [%s], eax\n", $1, $3.varName, $$.varName);
        } else if (strcmp($2, "MOD_ASSIGN") == 0) {
           sprintf(instr, "\n mov eax, [%s]\n mov edx, 0\n div %s\n mov [%s], edx\n", $1, $3.varName, $$.varName);
        }
        addInstruction(instr);
    }
    | ID INC SEMICOLON {
        char instr[700];
        sprintf(instr, "\n inc [%s]\n", $1);
        addInstruction(instr);
    }
    | INC ID SEMICOLON {
        char instr[700];
        sprintf(instr, "\n inc [%s]\n", $2);
        addInstruction(instr);
    }
    | ID DEC SEMICOLON {
        char instr[700];
        sprintf(instr, "\n dec [%s]\n", $1);
        addInstruction(instr);
    }
    | DEC ID SEMICOLON {
        char instr[700];
        sprintf(instr, "\n dec [%s]\n", $2);
        addInstruction(instr);
    }
    ;

arithmetic_assignment:
    ADD_ASSIGN { $$ = strdup("ADD_ASSIGN"); }
    | SUB_ASSIGN { $$ = strdup("SUB_ASSIGN"); }
    | MUL_ASSIGN { $$ = strdup("MUL_ASSIGN"); }
    | DIV_ASSIGN { $$ = strdup("DIV_ASSIGN"); }
    | MOD_ASSIGN { $$ = strdup("MOD_ASSIGN"); }
    ;

expression:
    value {
        strcpy($$.code, $1.code);
        strcpy($$.varName, $1.varName);
    }
    | value operator expression {
        newTempVariable($$.varName);
        addVariable($$.varName);

        sprintf($$.code, "\n %s\n %s\n", $1.code, $3.code);

        if (!isNumeric($1.varName))
            addBracketsAroundString($1.varName);

        if (!isNumeric($3.varName))
            addBracketsAroundString($3.varName);

        char instr[700];
        if (strcmp($2, "ADD") == 0) {
            sprintf(instr, "\n mov eax, %s\n add eax, %s\n mov [%s], eax\n", $1.varName, $3.varName, $$.varName);
        } else if (strcmp($2, "SUB") == 0) {
            sprintf(instr, "\n mov eax, %s\n sub eax, %s\n mov [%s], eax\n", $1.varName, $3.varName, $$.varName);
        } else if (strcmp($2, "MUL") == 0) {
            sprintf(instr, "\n mov eax, %s\n imul eax, %s\n mov [%s], eax\n", $1.varName, $3.varName, $$.varName);
        } else if (strcmp($2, "DIV") == 0) {
            sprintf(instr, "\n mov eax, %s\n mov edx, 0\n div %s\n mov [%s], eax\n", $1.varName, $3.varName, $$.varName);
        } else if (strcmp($2, "MOD") == 0) {
            sprintf(instr, "\n mov eax, %s\n mov edx, 0\n div %s\n mov [%s], edx\n", $1.varName, $3.varName, $$.varName);
        }

        addInstruction(instr);
    }
    ;

value:
    ID {
        strcpy($$.code, "");
        strcpy($$.varName, $1);
    }
    | CONST {
        strcpy($$.code, "");
        sprintf($$.varName, "%d", $1);
    }
    ;

operator:
    ADD { $$ = strdup("ADD"); }
    | SUB { $$ = strdup("SUB"); }
    | MUL { $$ = strdup("MUL"); }
    | DIV { $$ = strdup("DIV"); }
    | MOD { $$ = strdup("MOD"); }
    ;

%%

void yyerror(char *s) {
    extern char* yytext;
    printf("Syntax error for symbol '%s' at line: %d! \n", yytext, line_number);
    exit(1);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input file>\n", argv[0]);
        exit(1);
    }

    FILE *inputFile = fopen(argv[1], "r");
    if (!inputFile) {
        perror("fopen input file");
        exit(1);
    }

    yyin = inputFile;

    yyparse();

    // save_fip();
    // save_ts();

    fclose(inputFile);

    printf("Correct file!\n");

    FILE *asmFile = fopen("output.asm", "w");
    if (!asmFile) {
        perror("fopen asm file");
        exit(1);
    }

    fprintf(asmFile, "bits 32\n");
    fprintf(asmFile, "global start\n");
    fprintf(asmFile, "extern exit\n");
    fprintf(asmFile, "import exit msvcrt.dll\n");
    fprintf(asmFile, "extern printf\n");
    fprintf(asmFile, "import printf msvcrt.dll\n");
    fprintf(asmFile, "extern scanf\n");
    fprintf(asmFile, "import scanf msvcrt.dll\n");
    fprintf(asmFile, "\n\nsegment data use32 class=data\n");
    fprintf(asmFile, "\nwrite_int_fmt DB \"%%d \", 0\n");
    fprintf(asmFile, "write_line_fmt DB 0xA, 0x0\n");
    fprintf(asmFile, "read_int_fmt DB \"%%i\", 0\n");
    fprintf(asmFile, "\n");

    for (int i = 0; i < nrVariables; i++) {
        // printf("variable %d: %s", i, variables[i]);
        fprintf(asmFile, " %s DD 0\n", variables[i]);
    }

    fprintf(asmFile, "\n\nsegment code use32 class=code\n\n");
    fprintf(asmFile, "\nstart:\n");

    for (int i = 0; i < nrInstructions; i++) {
        fprintf(asmFile, " %s\n", instructions[i]);
    }

    fprintf(asmFile, " push dword 0\n");
    fprintf(asmFile, " call [exit]\n");

    fclose(asmFile);

    printf("Assembly code has been written to 'output.asm' file.\n");

    return 0;
}
