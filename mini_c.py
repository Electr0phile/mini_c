tokens = (
        'INTEGER', 'VARIABLE', 'TYPE',
        'SEMICOLON', 'EQUALS',
        )

# Tokens

t_VARIABLE  = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_TYPE      = r'(int|float)'
t_SEMICOLON = r';'
t_EQUALS    = r'='
t_INTEGER   = r'[1-9][0-9]*'

# Ignore

t_ignore = '\t '

# Count lines

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

# Error handling

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build lexer

import ply.lex as lex
lexer = lex.lex()

# Parsing rules

AST = {}

def p_root_body(p):
    'root : body'
    AST['root'] = p[1]

def p_empty(p):
    'empty : '
    pass

def p_body_line_body(p):
    'body : line body'
    p[0] = { 'line': p[1], 'body': p[2] }

def p_body_empty(p):
    'body : empty'
    p[0] = None

def p_line_declaration(p):
    'line : declaration'
    p[0] = { 'declaration' : p[1] }

def p_line_assignment(p):
    'line : assignment'
    p[0] = { 'assignment' : p[1] }

def p_declaration(p):
    'declaration : TYPE VARIABLE SEMICOLON'
    p[0] = { 'type' : p[1], 'variable': p[2] }

def p_assignment(p):
    'assignment : VARIABLE EQUALS expression SEMICOLON'
    p[0] = { 'variable' : p[1], 'expression': p[3] }

def p_expression_variable(p):
    'expression : VARIABLE'
    p[0] = { 'variable' : p[1] }

def p_expression_integer(p):
    'expression : INTEGER'
    p[0] = { 'integer' : p[1] }

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

while True:
    try:
        s = input('> ')
    except EOFError:
        break
    parser.parse(s)
    print(AST)
