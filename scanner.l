%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Global variables for position tracking */
int line_num = 1;
int col_num  = 1;
int tok_line = 1;
int tok_col  = 1;

/* Capture start position and advance column before every rule action */
#define YY_USER_ACTION          \
    tok_line = line_num;        \
    tok_col  = col_num;         \
    col_num += yyleng;

#define PRINT_TOKEN(tok) \
    printf("Line %3d, Col %3d | Token: %-12s | Lexeme: \"%s\"\n", \
           tok_line, tok_col, (tok), yytext)

#define PRINT_ERROR(msg, ...) \
    fprintf(stderr, "LEXICAL ERROR [Line %d, Col %d]: " msg "\n", \
            tok_line, tok_col, ##__VA_ARGS__)
%}

%option noyywrap

/* Definitions Section */
letter   [a-zA-Z]
digit    [0-9]
alnum    [a-zA-Z0-9]
special  [.#$_]
ws       [ \t\r]

%%

"else"   { PRINT_TOKEN("ELSE");   }
"if"     { PRINT_TOKEN("IF");     }
"int"    { PRINT_TOKEN("INT");    }
"return" { PRINT_TOKEN("RETURN"); }
"void"   { PRINT_TOKEN("VOID");   }
"while"  { PRINT_TOKEN("WHILE");  }

"<="     { PRINT_TOKEN("LTE");    }
">="     { PRINT_TOKEN("GTE");    }
"=="     { PRINT_TOKEN("EQ");     }
"!="     { PRINT_TOKEN("NEQ");    }
"+"      { PRINT_TOKEN("PLUS");   }
"-"      { PRINT_TOKEN("MINUS");  }
"*"      { PRINT_TOKEN("TIMES");  }
"/"      { PRINT_TOKEN("DIVIDE"); }
"<"      { PRINT_TOKEN("LT");     }
">"      { PRINT_TOKEN("GT");     }
"="      { PRINT_TOKEN("ASSIGN"); }
";"      { PRINT_TOKEN("SEMI");   }
","      { PRINT_TOKEN("COMMA");  }
"("      { PRINT_TOKEN("LPAREN"); }
")"      { PRINT_TOKEN("RPAREN"); }
"["      { PRINT_TOKEN("LBRACKET"); }
"]"      { PRINT_TOKEN("RBRACKET"); }
"{"      { PRINT_TOKEN("LBRACE");   }
"}"      { PRINT_TOKEN("RBRACE");   }

"/*" {
    int c, prev = 0;
    int cmt_line = tok_line;
    int cmt_col  = tok_col;

    while (1) {
        c = input();
        if (c == EOF) {
            fprintf(stderr, "LEXICAL ERROR [Line %d, Col %d]: "
                "Reached end of file inside unclosed comment "
                "(comment opened at line %d, col %d)\n",
                line_num, col_num, cmt_line, cmt_col);
            yyterminate();
        }

        if (c == '\n') {
            line_num++;
            col_num = 1;
        } else {
            col_num++;
        }

        if (prev == '*' && c == '/') break;
        prev = c;
    }
}

{letter}({letter}|{digit})*({special}{alnum}+)? {
    PRINT_TOKEN("ID");
}

{letter}({letter}|{digit})*{special} {
    PRINT_ERROR("Invalid identifier \"%s\" -- special character '%c' must be followed by a letter or digit",
        yytext, yytext[yyleng - 1]);
}

({digit}+|{digit}+\.{digit}*)([Ee][+-]?{digit}+)? {
    PRINT_TOKEN("NUM");
}

({digit}+|{digit}+\.{digit}*)[Ee][+-] {
    PRINT_ERROR("Invalid number \"%s\" -- exponent sign must be immediately followed by one or more digits",
        yytext);
}

\n      { line_num++; col_num = 1; }
{ws}+   { /* skip whitespace */ }

. {
    PRINT_ERROR("Invalid character '%s' (ASCII %d) -- not in the language alphabet",
        yytext, (unsigned char)yytext[0]);
}

%%

int main(int argc, char *argv[]) {
    if (argc > 1) {
        yyin = fopen(argv[1], "r");
        if (!yyin) {
            fprintf(stderr, "Error: cannot open file '%s'\n", argv[1]);
            return 1;
        }
        fprintf(stdout, "Scanning: %s\n\n", argv[1]);
    } else {
        yyin = stdin;
        fprintf(stdout, "Reading from stdin (press Ctrl+D to end):\n\n");
    }

    printf("%-25s %-14s %s\n", "Position", "Token", "Lexeme");
    printf("%-25s %-14s %s\n", "-------------------------", "--------------", "---------------------------");

    yylex();

    if (argc > 1) fclose(yyin);
    printf("\n[Done]\n");
    return 0;
}