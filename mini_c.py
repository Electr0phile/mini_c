# Tokens

t_INTEGER   = r'[1-9][0-9]*'

# Literals are used in productions as is
literals = "{}(),;="

# All types are treated as TYPE tokens
reserved = {
            'int' : 'TYPE',
            'float' : 'TYPE',
            'void' : 'TYPE',
        }

tokens = [
        'INTEGER',
        'VARIABLE',
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
#  'linespan' - tuple of first and las line of function
#  'return_type' - type of return value
#  'arguments' - list of arguments, it may either be
#   a list of types or a list of dicts ('type', 'variable')
#  'body' - list of lines

def p_function_body(p):
    ''' function : TYPE VARIABLE '(' arguments ')' '{' body '}' '''
    p[0] = {
            'function_name': p[2],
            'linespan': (p.lineno(1), p.lineno(8)),
            'return_type': p[1],
            'arguments': p[4],
            'body' : p[7],
            }

def p_argunments_names_one(p):
    ''' arguments : TYPE VARIABLE '''
    p[0] = [{ 'type': p[1], 'variable': p[2] }]

def p_arguments_names_recursion(p):
    ''' arguments : TYPE VARIABLE ',' arguments '''
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
#  Any line has a field 'linespan' which consists of
#  a tuple of numbers, first being a code line at which
#  the line begins and last being a code line at which
#  the line ends.
#  These are made so that the debugger could execute the line
#  only after it ends in the source code.

def p_line_declaration(p):
    'line : declaration'
    p[0] = { 'linespan': p[1][0], 'declaration' : p[1][1] }

def p_line_assignment(p):
    'line : assignment'
    p[0] = { 'linespan' : p[1][0], 'assignment' : p[1][1] }

def p_declaration(p):
    '''declaration : TYPE variable_list ';' '''
    p[0] = ( (p.lineno(1), p.lineno(3)), { 'type' : p[1], 'variables': p[2] })

def p_variable_list_one(p):
    'variable_list : VARIABLE'
    p[0] = [p[1]]

def p_variable_list_recursion(p):
    '''variable_list : VARIABLE ',' variable_list '''
    p[0] = [p[1]] + p[3]

def p_assignment(p):
    '''assignment : VARIABLE '=' expression ';' '''
    p[0] = ( (p.lineno(1), p.lineno(4)), { 'variable' : p[1], 'expression': p[3] })

def p_expression_variable(p):
    'expression : VARIABLE'
    print(p.type)
    p[0] = { 'variable' : p[1] }

def p_expression_integer(p):
    'expression : INTEGER'
    p[0] = { 'integer' : p[1] }

def p_empty(p):
    'empty : '
    pass

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

data = \
"""
int sum(int a, int b) { asdf = 10; } \n \
\n \
int main(int, float){ \n \
    int a,b,c; \n \
    a = 10; \n \
}
"""

parser.parse(data)

import json
print(json.dumps(AST, indent=4))
