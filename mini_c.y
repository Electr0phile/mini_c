%{

#include <stdio.h>

/* define a union of values for a node */
union node_value {
    void *null;
    int integer;
    char variable[20];
};

/* define a tree node for an AST */
struct node {
    char type[20];
    union node_value value;
    int number_of_children;
    struct node ** children;
};

struct node *root;

struct node * add_node (char *, union node_value, int, struct node **);

int dfs(struct node *n);

%}

%union {
    int integer;
    char variable[20];
    char *type;
    struct node * nodetype;
}

%token <integer> INTEGER
%token <variable> VARIABLE
%token <type> TYPE

%type <nodetype> root body line declaration assignment expression

%%

root:           body                            {
                                                    struct node ** children = (struct node **) malloc(sizeof(struct node *));
                                                    children[0] = $1;
                                                    root = add_node("root", (union node_value) NULL, 1, children);
                                                }
    ;

body:           line body                       {
                                                    struct node ** children = (struct node **) malloc(sizeof(struct node *) * 2);
                                                    children[0] = $1;
                                                    children[1] = $2;
                                                    $$ = add_node("body", (union node_value) NULL, 2, children);
                                                }
    |           /* empty */                     {
                                                    $$ = add_node("body", (union node_value) NULL, 0, NULL);
                                                }
    ;

line:           declaration                     {
                                                    struct node ** children = (struct node **) malloc(sizeof(struct node *));
                                                    children[0] = $1;
                                                    $$ = add_node("line", (union node_value) NULL, 1, children);
                                                }
    |           assignment                      {
                                                    struct node ** children = (struct node **) malloc(sizeof(struct node *));
                                                    children[0] = $1;
                                                    $$ = add_node("line", (union node_value) NULL, 1, children);
                                                }
    ;

declaration:    TYPE VARIABLE ';'               {
                                                    $$ = add_node("declaration", (union node_value) NULL, 0, NULL);
                                                }
           ;

assignment:     VARIABLE '=' expression ';'     {
                                                    struct node ** children = (struct node **) malloc(sizeof(struct node *) * 2);
                                                    union node_value v;
                                                    strcpy(v.variable, $1);
                                                    children[0] = add_node("variable", v, 0, NULL);
                                                    children[1] = $3;
                                                    $$ = add_node("assignment", (union node_value) NULL, 2, children);
                                                }
          ;

expression:     VARIABLE                        {
                                                    union node_value v;
                                                    strcpy(v.variable, yylval.variable);
                                                    $$ = add_node("variable", v, 0, NULL);
                                                }
          |     INTEGER                         {
                                                    union node_value v;
                                                    v.integer = yylval.integer;
                                                    $$ = add_node("integer", v, 0, NULL);
                                                }
          ;

%%

extern FILE *yyin;

struct node * add_node (char *node_type, union node_value value, int number_of_children, struct node **children)
{
    struct node *new_node;
    new_node = (struct node *) malloc(sizeof(struct node));
    strcpy(new_node->type, node_type);
    if (value.null != NULL) {
        new_node->value = value;
    }
    new_node->number_of_children = number_of_children;
    new_node->children = children;

    return new_node;
}


int dfs(struct node *n)
{
    printf("{ %s : ", n->type);

    struct node * child;
    for (int i=0; i<(n->number_of_children); i++) {
        child = n->children[i];
        dfs(child);
    }

    printf(" }");

    return 0;
}

main()
{

    yyin = stdin;

    yyparse();

    dfs(root);

}

yyerror(s)
char *s;
{
    fprintf(stderr, "%s\n", s);
}
