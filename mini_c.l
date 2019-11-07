%{

/* a small subset of c language */

#include "y.tab.h"

%}
%%

[ \t]+

int |
float           {
                    /* detect a type */
                    strcpy(yylval.type, yytext);
                    return TYPE;
                }

0 |
[1-9][0-9]*     {
                    /* detect integer number */
                    yylval.integer = atoi(yytext);
                    return INTEGER;
                }

[a-z][a-z0-9]*  {
                    /* detect arbitrary variable */
                    /* CAREFUL: if variable size is longer than 20 there will be segfault */
                    strcpy(yylval.variable, yytext);
                    return VARIABLE;
                }

; |
=               {   return yytext[0];   }

.|\n

%%
