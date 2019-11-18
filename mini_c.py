# Tokens

t_SEMICOLON = r';'
t_EQUALS    = r'='
t_INTEGER   = r'[1-9][0-9]*'

reserved = {
            'int' : 'INT_TYPE',
            'float' : 'FLOAT_TYPE',
        }

tokens = [
        'INTEGER', 'ID',
        'SEMICOLON', 'EQUALS', 'VARIABLE',
        ] + list(reserved.values())

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'VARIABLE')    # Check for reserved words
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

AST = {}

def p_main_body(p):
    'main : body'
    AST['main'] = { 'body' : p[1] }

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
    p[0] = { 'linespan': p[1][0], 'declaration' : p[1][1] }

def p_line_assignment(p):
    'line : assignment'
    p[0] = { 'linespan' : p[1][0], 'assignment' : p[1][1] }

def p_declaration(p):
    'declaration : type VARIABLE SEMICOLON'
    p[0] = ( (p[1][0], p.lineno(3)), { 'type' : p[1][1], 'variable': p[2] })

def p_assignment(p):
    'assignment : VARIABLE EQUALS expression SEMICOLON'
    p[0] = ( (p.lineno(1), p.lineno(4)), { 'variable' : p[1], 'expression': p[3] })

def p_expression_variable(p):
    'expression : VARIABLE'
    print(p.type)
    p[0] = { 'variable' : p[1] }

def p_expression_integer(p):
    'expression : INTEGER'
    p[0] = { 'integer' : p[1] }

def p_type(p):
    'type : INT_TYPE'
    '     | FLOAT_TYPE'
    p[0] = ( p.lineno(1), p[1] )

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

data = open('test.txt', 'r')

parser.parse(data.read())

import json
print(json.dumps(AST, indent=4))
