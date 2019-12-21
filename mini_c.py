# Tokens

t_INTEGER   = r'\d+'
t_FLOAT     = r'\d*\.\d+'
t_INCR      = r'\+\+'
t_PLUS      = r'\+'
t_DIGIT_STRING = r'"%d[\\]n"'
t_FLOAT_STRING = r'"%f[\\]n"'
t_STRING = r'"[a-zA-Z_0-9\*\\\:\.!?@#$%^&\(\)-_=\[\]/\+\{\}~`,<>; ]*"' # TODO: add more symbols
 


# Literals are used in productions as is
literals = '[]{}(),;=><-*/&"'


# All types are treated as TYPE tokens
reserved = {
            'int' : 'INT_TYPE',
            'float' : 'FLOAT_TYPE',
            'void' : 'VOID_TYPE',
            'if'    : 'IF',
            'for'    : 'FOR',
            'return' : 'RETURN',
            'printf' : 'PRINTF',
        }

tokens = [
        'INTEGER',
        'FLOAT',
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
    ''' function : type_func VARIABLE rbl arguments rbr cbl body cbr '''
    p[0] = {
            'function_name': p[2],
            'span': p.linespan(0),
            'return_type': p[1],
            'arguments': p[4],
            'body' : p[7],
            }

def p_function_body_error(p):
    ''' function : type_func VARIABLE rbl error rbr cbl body cbr '''
    ERRORS.append( ( p.lineno(0), "Error in function arguments" ) )
    p[0] = {
            'function_name': p[2],
            'span': p.linespan(0),
            'return_type': p[1],
            'arguments': {}, # TODO: think about this
            'body' : p[7],
            }

def p_argunments_names_one(p):
    ''' arguments : type_num variable_or_pointer '''
    p[0] = [{ 'type': p[1], 'variable': p[2] }]

def p_arguments_names_recursion(p):
    ''' arguments : type_num variable_or_pointer comma arguments '''
    p[0] = [{ 'type': p[1], 'variable': p[2]}] + p[4]

def p_argunments_types_void(p):
    ''' arguments : VOID_TYPE '''
    p[0] = [{ 'type': p[1] }]

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

def p_line_error(p):
    'line : error semicolon'
    ERRORS.append( ( p.lineno(0), "Unrecognized command!" ) )
    p[0] = { 'span' : p.linespan(0), 'type': 'printf', 'value': p[1]}


### Line expansions ###

def p_declaration(p):
    '''declaration : type_num variable_list semicolon '''
    p[0] = { 'type' : p[1], 'variables': p[2] }

def p_declaration_error(p):
    '''declaration : type_num error semicolon '''
    ERRORS.append( ( p.lineno(0), "Error in declaration" ) )
    p[0] = { 'type' : p[1], 'variables': [] }

def p_variable_list_one(p):
    '''
    variable_list : variable_or_pointer
                  | array
    '''
    p[0] = [p[1]]

def p_variable_list_recursion(p):
    '''
    variable_list : variable_or_pointer comma variable_list
                  | array comma variable_list
    '''
    p[0] = [p[1]] + p[3]

def p_assignment(p):
    '''
    assignment : variable_or_pointer eq expr_1 semicolon
               | array eq expr_1 semicolon
    '''
    p[0] = { 'variable' : p[1], 'expression': p[3] }

def p_assignment_error(p):
    '''
    assignment : error eq expr_1 semicolon
    '''
    ERRORS.append( ( p.lineno(0), "Incorrect left side assignment expression!" ) )
    p[0] = { 'variable' : "", 'expression': p[3] }

def p_assignment_address(p):
    '''
    assignment : variable_or_pointer eq '&' VARIABLE semicolon
               | array eq '&' VARIABLE semicolon
    '''
    p[0] = { 'variable' : p[1], 'expression': ('&', p[4]) }

def p_assignment_address_error(p):
    '''
    assignment : error eq '&' VARIABLE semicolon
    '''
    ERRORS.append( ( p.lineno(0), "Incorrect left side assignment expression!" ) )
    p[0] = { 'variable' : "", 'expression': ('&', p[4]) }

def p_return_expr(p):
    ''' return_expr : RETURN expr_1 semicolon '''
    p[0] = { 'expression': p[2] }

def p_return_expr_empty(p):
    ''' return_expr : RETURN semicolon '''
    p[0] = { 'expression': None }

def p_expr_line(p):
    ''' expr_line : expr_1 semicolon '''
    p[0] = { 'expression': p[1] }

def p_printf_expr_digit_float(p):
    '''
    printf_expr : PRINTF rbl STRING  rbr semicolon
                | PRINTF rbl digit_print rbr semicolon
                | PRINTF rbl float_print rbr semicolon

    '''
    p[0] = p[3]

def p_printf_expr_digit_float(p):
    '''
    printf_expr : PRINTF rbl error rbr semicolon

    '''
    ERRORS.append( ( p.lineno(0), "Unrecognized printf function argument!" ) )
    p[0] = p[3]

def p_print_digit(p):
    '''
    digit_print : DIGIT_STRING comma expr_1
    '''
    p[0] = {'digit' : p[3]}

def p_print_float(p):
    '''
    float_print : FLOAT_STRING comma expr_1
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
           | FLOAT
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
    if_clause : IF rbl expr_1 rbr cbl body cbr
    '''
    p[0] = {
            'expression' : p[3],
            'body' : p[6],
            }

### For loops ###

def p_for_loop(p):
    '''
    for_loop : FOR rbl assignment expr_1 semicolon expr_1 rbr cbl body cbr
    '''
    p[0] = {
            'initialization' : p[3],
            'condition' : p[4],
            'operation' : p[6],
            'body' : p[9]
            }

### Function call ###

def p_function_call(p):
    '''function_call : VARIABLE rbl arguments_call rbr '''
    p[0] = { 'function_name': p[1], 'arguments': p[3] }

def p_arguments_names_call_one(p):
    ''' arguments_call : expr_1 '''
    p[0] = [{ 'expression': p[1] }]

def p_arguments_names_call_recursion(p):
    ''' arguments_call : expr_1 comma arguments_call '''
    p[0] = [{ 'expression': p[1]}] + p[3]

### Arrays ###

def p_array(p):
    ''' array : VARIABLE sbl expr_1 sbr '''
    p[0] = { 'array_name': p[1], 'index': p[3] }

### Error handling nonterminals ###

def p_type_func(p):
    ''' type_func : INT_TYPE
                  | FLOAT_TYPE
                  | VOID_TYPE '''
    p[0] = p[1]

def p_type_func_error(p):
    ''' type_func : error '''
    ERRORS.append( ( p.lineno(0), "Unrecognized type!" ) )
    p[0] = ""

def p_type_num(p):
    ''' type_num : INT_TYPE
                 | FLOAT_TYPE '''
    p[0] = p[1]

def p_type_num_error(p):
    ''' type_num : error '''
    ERRORS.append( ( p.lineno(0), "Unrecognized type!" ) )
    p[0] = ""

def p_round_bracket_left(p):
    ''' rbl : '('
            | empty '''
    if p[1] != '(':
        ERRORS.append( ( p.lineno(0), "Missing left paranthesis!" ) )

def p_round_bracket_right(p):
    ''' rbr : ')'
            | empty '''
    if p[1] != ')':
        ERRORS.append( ( p.lineno(0), "Missing right paranthesis!" ) )

def p_curly_bracket_left(p):
    ''' cbl : '{'
            | empty '''
    if p[1] != '{':
        ERRORS.append( ( p.lineno(0), "Missing left curly bracket!" ) )

def p_curly_bracket_right(p):
    ''' cbr : '}'
            | empty '''
    if p[1] != '}':
        ERRORS.append( ( p.lineno(0), "Missing right curly bracket!" ) )

def p_square_bracket_left(p):
    ''' sbl : '['
            | empty '''
    if p[1] != '[':
        ERRORS.append( ( p.lineno(0), "Missing left square bracket!" ) )

def p_square_bracket_right(p):
    ''' sbr : ']'
            | empty '''
    if p[1] != ']':
        ERRORS.append( ( p.lineno(0), "Missing right square bracket!" ) )

def p_semicolon(p):
    ''' semicolon : ';'
                  | empty '''
    if p[1] != ';':
        ERRORS.append( ( p.lineno(0), "Missing semicolon!" ) )

def p_comma(p):
    ''' comma : ','
              | empty '''
    if p[1] != ',':
        ERRORS.append( ( p.lineno(0), "Missing comma!" ) )

def p_equality(p):
    ''' eq : '='
           | empty '''
    if p[1] != '=':
        ERRORS.append( ( p.lineno(0), "Missing equality sign!" ) )

### Helpers ###

def p_empty(p):
    'empty : '
    pass

def p_error(t):
    print(t.lexpos)
    print('Linenumber: ', t.lineno)
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

test_file = open("test.txt", "r")

data = test_file.read();
print(data);
test_file.close();

parser.parse(data, tracking=True)

import json
print("AST:")
print(json.dumps(AST, indent=2))
print("ERRORS:")
print(json.dumps(ERRORS, indent=2))
print(AST)
print(ERRORS)
