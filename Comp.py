
# !/usr/bin/env python

# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
#
# Class-based example contributed to PLY by David McNab
# -----------------------------------------------------------------------------

import sys

sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc
import os


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                          1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        # print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run(self):
        while 1:
            try:
                s = raw_input('calc > ')
            except EOFError:
                break
            if not s:
                continue
            result = yacc.parse(s)
            print((result))


class Root:
    def __init__(self, value):
        self.type = "root"
        self.root = value

    def __str__(self):
        result = "Root->" + str(self.root)
        return result

class Body(Root):
    def __init__(self, value = "", next = "None"):
        self.type = "body"
        self.value = value
        self.next = next

    def __str__(self):
        result = "Body->" + str(self.value) + "\n" + "Body->" + str(self.next)
        return result

class Line(Body):
    def __init__(self, value1):
        self.type = "line"
        self.value1 = value1

    def __str__(self):
        result = "Line->" + str(self.value1)
        return result

class Declaration(Line):
    def __init__(self, value1, value2):
        self.type = "declaration"
        self.value1 = value1
        self.value2 = value2

    def __str__(self):
        result = "Declaration->" + str(self.value1) + "\n" + "Declaration->" + str(self.value2)
        return result

class Assignment(Line):
    def __init__(self, value1, value2):
        self.type = "assignment"
        self.value1 = value1
        self.value2 = value2

    def __str__(self):
        result = "Assignment->" + str(self.value1) + "\n" + "Assignment->" + str(self.value2)
        return result

class Expr():
    def __init__(self, vakue):
        self.type = "expression"
        self.value = vakue
    def __str__(self):
        result = "Expr->" + str(self.value)
        return result


class Integer(Expr):
    def __init__(self, vakue):
        self.type = "integer"
        self.value = vakue

    def __str__(self):
        result = "Integer->" + str(self.value)
        return result

class Variable(Expr):
    def __init__(self, vakue):
        self.type = "variable"
        self.value = vakue

    def __str__(self):
        result = "Variable->" + str(self.value)
        return result

class Type:
    def __init__(self, value):
        self.type = "type"
        self.value = value

    def __str__(self):
        result = "Type->" + str(self.value)
        return result

class Number:
    def __init__(self, value):
        self.type = "number"
        self.value = value

    def __str__(self):
        result = "Number->" + str(self.value)
        return result

class Calc(Parser):
    tokens = (
        'NUMBER', 'INT', 'IDENTIFIER', 'FLOAT', 'COLON', 'EQUAL'
    )

    # Tokens
    t_EQUAL = r'='
    t_COLON = r';'
    t_INT = r'int'
    t_FLOAT = r'float'


    reserved = {
        'int': 'INT',
        'float': 'FLOAT',
    }

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'IDENTIFIER')  # Check for reserved words
        return t

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        # print "parsed number %s" % repr(t.value)
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules
    def p_root(self, p):
        'root : body'

        p[0] = Root(p[1])

    def p_empty(self, p):
        'empty :'
        pass

    def p_body(self, p):
        'body : line body'
        p[0] = Body(p[1], p[2])

    def p_empty_body(self,p):
        'body : empty'
        p[0] = Body()

    def p_line(self, p):
        """
        line : declaration
            | assignment

        """
        p[0] = Line(p[1])

    def p_declaration(self, p):
        """
        declaration : type var COLON
        """
        p[0] = Declaration(p[1], p[2])

    def p_assignment(self, p):
        """
        assignment : var EQUAL expression COLON
        """
        p[0] = Assignment(p[1], p[3])

    def p_expression(self, p):
        """
        expression : var
                   | number
        """
        p[0] = Expr(p[1])
    def p_type(self,p):
        """
        type : INT
            | FLOAT
        """
        p[0] = Type(p[1])

    def p_var(self,p):
        """
        var : IDENTIFIER
        """
        p[0] = Variable(p[1])

    def p_number(self, p):
        """
        number : NUMBER
        """
        p[0] = Number(p[1])

    def p_error(self, p):
        if p:
            print(p)
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")


if __name__ == '__main__':
    calc = Calc()
    calc.run()

