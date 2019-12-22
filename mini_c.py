# Tokens

t_INTEGER   = r'([1-9][0-9]*|0)'
t_INCR      = r'\+\+'
t_PLUS      = r'\+'
t_DIGIT_STRING = r'"%d[\\]n"'
t_FLOAT_STRING = r'"%f[\\]n"'
t_STRING = r'"[a-zA-Z_0-9\*\\ ]*"'



# Literals are used in productions as is
literals = '[]{}(),;=><-*/&"'


# All types are treated as TYPE tokens
reserved = {
            'int' : 'TYPE',
            'float' : 'TYPE',
            'void' : 'TYPE',
            'if'    : 'IF',
            'for'    : 'FOR',
            'return' : 'RETURN',
            'printf' : 'PRINTF',
        }

tokens = [
        'INTEGER',
        'VARIABLE',
        'PLUS',
        'INCR',
        'DIGIT_STRING',
        'FLOAT_STRING',
        'STRING',
        ] + list(reserved.values())

# Since types are captured by variable regexp,
#  we have to define a separate type ID that resolves
#  this conflict inside its definition
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # If value of t is one of reserved values, return TYPE
    #  else return VARIABLE
    t.type = reserved.get(t.value,'VARIABLE')
    return t

# Ignore

t_ignore = '\t '

# Count lines

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build lexer

import ply.lex as lex
lexer = lex.lex()

# Parsing rules

# Root structure of abstract synthax tree is a list of function definitions
AST = []
ERRORS = []

### Function list level ###

# At the top level of AST we simply parse
#  a list of function declarations

def p_function_list(p):
    ' function_list : function function_list '
    AST.insert(0, p[1])

def p_function_list_empty(p):
    ' function_list : empty '
    pass


### Function definition level ###

# At this level we parse a function. Function is
#  represented by a dictionary with following fields:
#  'function_name' - name of function
#  'span' - tuple of first and las line of function
#  'return_type' - type of return value
#  'arguments' - list of arguments, it may either be
#   a list of types or a list of dicts ('type', 'variable')
#  'body' - list of lines

def p_function_body(p):
    ''' function : TYPE VARIABLE '(' arguments ')' '{' body '}' '''
    p[0] = {
            'function_name': p[2],
            'span': p.linespan(0),
            'return_type': p[1],
            'arguments': p[4],
            'body' : p[7],
            }

def p_function_body_error_1(p):
    ''' function : error VARIABLE '(' arguments ')' '{' body '}' '''
    p[0] = {
            'function_name': p[2],
            'span': p.linespan(0),
            'return_type': p[1],
            'arguments': p[4],
            'body' : p[7],
            }

def p_argunments_names_one(p):
    ''' arguments : TYPE variable_or_pointer '''
    p[0] = [{ 'type': p[1], 'variable': p[2] }]

def p_arguments_names_recursion(p):
    ''' arguments : TYPE variable_or_pointer ',' arguments '''
    p[0] = [{ 'type': p[1], 'variable': p[2]}] + p[4]

def p_argunments_types_one(p):
    ''' arguments : TYPE '''
    p[0] = [{ 'type': p[1] }]

def p_arguments_types_recursion(p):
    ''' arguments : TYPE ',' arguments '''
    p[0] = [{ 'type': p[1]}] + p[3]


### Function body level ###

# Function body consists of a list of lines

def p_body_line_body(p):
    'body : line body'
    p[0] = [p[1]] + p[2]

def p_body_empty(p):
    'body : empty'
    p[0] = []


### Line level ###

# Here various types of lines are defined
#  Any line has a field 'span' which consists of
#  a tuple of numbers, first being a code line at which
#  the line begins and last being a code line at which
#  the line ends.
#  These are made so that the debugger could execute the line
#  only after it ends in the source code.

def p_line_declaration(p):
    'line : declaration'
    p[0] = { 'span': p.linespan(0), 'type':'declaration', 'value' : p[1] }

def p_line_assignment(p):
    'line : assignment'
    p[0] = { 'span' : p.linespan(0), 'type':'assignment', 'value' : p[1] }

def p_line_if_clause(p):
    'line : if_clause'
    p[0] = { 'span' : p.linespan(0), 'type':'if_clause', 'value' : p[1] }

def p_line_for_loop(p):
    'line : for_loop'
    p[0] = { 'span' : p.linespan(0), 'type':'for_loop', 'value' : p[1] }

def p_line_expr(p):
    ' line : expr_line '
    p[0] = { 'span': p.linespan(0), 'type':'expr_line', 'value' : p[1] }

def p_line_return(p):
    'line : return_expr'
    p[0] = { 'span' : p.linespan(0), 'type': 'return', 'value': p[1]}

def p_line_printf(p):
    'line : printf_expr'
    p[0] = { 'span' : p.linespan(0), 'type': 'printf', 'value': p[1]}


### Line expansions ###

def p_declaration(p):
    '''declaration : TYPE variable_list ';' '''
    p[0] = { 'type' : p[1], 'variables': p[2] }

def p_declaration_error_semicolon(p):
    '''declaration : TYPE variable_list '''
    p[0] = { 'error' : 'missing semicolon' }

def p_variable_list_one(p):
    '''
    variable_list : variable_or_pointer
                  | array
    '''
    p[0] = [p[1]]

def p_variable_list_recursion(p):
    '''
    variable_list : variable_or_pointer ',' variable_list
                  | array ',' variable_list
    '''
    p[0] = [p[1]] + p[3]

def p_assignment(p):
    '''
    assignment : variable_or_pointer '=' expr_1 ';'
               | array '=' expr_1 ';'
    '''
    p[0] = { 'variable' : p[1], 'expression': p[3] }

def p_assignment_error_expr(p):
    '''
    assignment : variable_or_pointer '=' error ';'
               | array '=' error ';'
    '''
    p[0] = { 'error' : 'incorrect expression' }

def p_assignment_address(p):
    '''
    assignment : variable_or_pointer '=' '&' VARIABLE ';'
               | array '=' '&' VARIABLE ';'
    '''
    p[0] = { 'variable' : p[1], 'expression': ('&', p[4]) }

def p_return_expr(p):
    ''' return_expr : RETURN expr_1 ';' '''
    p[0] = { 'expression': p[2] }

def p_return_expr_empty(p):
    ''' return_expr : RETURN ';' '''
    p[0] = { 'expression': None }

def p_expr_line(p):
    ''' expr_line : expr_1 ';' '''
    p[0] = { 'expression': p[1] }

def p_printf_expr_digit_float(p):
    '''
    printf_expr : PRINTF '(' STRING  ')' ';'
                | PRINTF '(' digit ')' ';'
                | PRINTF '(' float ')' ';'

    '''
    p[0] = p[3]

def p_print_digit(p):
    '''
    digit : DIGIT_STRING ',' expr_1
    '''
    p[0] = {'digit' : p[3]}

def p_print_float(p):
    '''
    float : FLOAT_STRING ',' expr_1
    '''
    p[0] = {'float' : p[3]}

### Pointers and variables ###

def p_pointer(p):
    '''
    variable_or_pointer : '*' VARIABLE
                        | VARIABLE
    '''
    if p[1] == '*':
        p[0] = ('*', p[2])
    else:
        p[0] = (None, p[1])


### Expression handler ###

def p_expr_1_lr(p):
    '''
    expr_1 : expr_2 '>' expr_1
           | expr_2 '<' expr_1
    '''
    p[0] = {
            'op' : p[2],
            'left' : p[1],
            'right' : p[3],
            }

def p_expr_1_2(p):
    '''
    expr_1 : expr_2
    '''
    p[0] = p[1]

def p_expr_2_lr(p):

    '''
    expr_2 : expr_3 PLUS expr_2
           | expr_3 '-' expr_2
    '''
    p[0] = {
            'op' : p[2],
            'left' : p[1],
            'right' : p[3],
            }

def p_expr_2_3(p):
    '''
    expr_2 : expr_3
    '''
    p[0] = p[1]

def p_expr_3_lr(p):

    '''
    expr_3 : expr_4 '*' expr_3
           | expr_4 '/' expr_3
    '''
    p[0] = {
            'op' : p[2],
            'left' : p[1],
            'right' : p[3],
            }

def p_expr_3_4(p):
    '''
    expr_3 : expr_4
    '''
    p[0] = p[1]

def p_expr_4(p):
    '''
    expr_4 : '-' expr_5
           | expr_5
    '''
    if p[1] == '-':
        p[0] = {
                'op' : p[1],
                'left' : None,
                'right' : p[2],
                }
    else:
        p[0] = p[1]

def p_expr_5_incr(p):
    '''
    expr_5 : variable_or_pointer INCR
    '''
    p[0] = {
            'op' : p[2],
            'left' : p[1],
            'right' : None,
            }

def p_expr_5_6(p):
    '''
    expr_5 : expr_6
    '''
    p[0] = p[1]


def p_expr_6(p):
    '''
    expr_6 : INTEGER
           | variable_or_pointer
           | function_call
           | array
           | '(' expr_1 ')'
    '''
    if p[1] == '(':
        p[0] = p[2]
    else:
        p[0] = p[1]


### If statements ###

def p_if_only(p):
    '''
    if_clause : IF '(' expr_1 ')' '{' body '}'
    '''
    p[0] = {
            'expression' : p[3],
            'body' : p[6],
            }

### For loops ###

def p_for_loop(p):
    '''
    for_loop : FOR '(' assignment expr_1 ';' expr_1 ')' '{' body '}'
    '''
    p[0] = {
            'initialization' : p[3],
            'condition' : p[4],
            'operation' : p[6],
            'body' : p[9]
            }

def p_for_loop_error_open_bracket(p):
    '''
    for_loop : FOR '(' assignment expr_1 ';' expr_1 ')' body '}'
    '''
    p[0] = { 'error' : 'missing opening bracket' }

def p_for_loop_error_close_bracket(p):
    '''
    for_loop : FOR '(' assignment expr_1 ';' expr_1 ')' '{' body
    '''
    p[0] = { 'error' : 'missing opening bracket' }

### Function call ###

def p_function_call(p):
    '''function_call : VARIABLE '(' arguments_call ')' '''
    p[0] = { 'function_name': p[1], 'arguments': p[3] }

def p_arguments_names_call_one(p):
    ''' arguments_call : expr_1 '''
    p[0] = [{ 'expression': p[1] }]

def p_arguments_names_call_recursion(p):
    ''' arguments_call : expr_1 ',' arguments_call '''
    p[0] = [{ 'expression': p[1]}] + p[3]

### Arrays ###

def p_array(p):
    ''' array : VARIABLE '[' expr_1 ']' '''
    p[0] = { 'array_name': p[1], 'index': p[3] }

### Helpers ###

def p_empty(p):
    'empty : '
    pass

def p_error(t):
    print(t.lexpos)
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

data = \
r"""int main(void){
    int a[5], a
    a[5] = a + b;
}
"""

parser.parse(data, tracking=True)

import json
print(json.dumps(AST, indent=2))
print(AST)
