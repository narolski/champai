# chaiparser.py
from sly import Parser
from chailexer import ChaiLexer
from scope.chaivars import *
from scope.chaiflow import *

import logging


class ChaiParser(Parser):
    """
    Defines grammar's rules and actions
    """
    # scope = ChaiScope()
    tokens = ChaiLexer.tokens
    debugfile = 'parser.out'

    global_variables = {}

    # Declares precedence
    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
    )

    # program:
    # Handles the program division into declarations
    @_('DECLARE declarations IN commands END')
    def program(self, p):
        return [p[1], p[3]]
        # return (Header(declared_vars=p[1]), p[3])

    # declarations:
    # Handles the variable declarations
    @_('declarations PIDENTIFIER SEMICOLON')
    def declarations(self, p):
        p[0] = list(p[0]) if p[0] else []
        # p[0].append(('int', p[1], p.lineno))

        p[0].append(Int(pidentifier=p[1], lineno=p.lineno))
        return p[0]

    @_('declarations PIDENTIFIER LPAREN NUMBER COLON NUMBER RPAREN SEMICOLON')
    def declarations(self, p):
        p[0] = list(p[0]) if p[0] else []
        # p[0].append(('int[]', p[1], p[3], p[5], p.lineno))
        p[0].append(IntArray(pidentifier=p[1], lineno=p.lineno, from_val=p[3], to_val=p[5]))

        return p[0]

    @_('empty')
    def declarations(self, p):
        return []

    # commands:
    @_('commands command')
    def commands(self, p):
        p[0] = list(p[0]) if p[0] else []
        p[0].append(p[1])
        return p[0]

    @_('command')
    def commands(self, p):
        return list((p[0],))

    # command:
    # Handles command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        # return ('assign', p[0], p[2])
        return Assign(identifier=p[0], expression=p[2])

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        # return ('if', p[1], p[3])
        return If(condition=p[1], commands=p[3])

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        # return ('if_else', p[1], p[3], p[5])
        return IfElse(condition=p[1], commands=p[3], alt_commands=p[5])

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        # return ('while', p[1], p[3])
        return While(condition=p[1], commands=p[3])

    @_('DO commands WHILE condition ENDDO')
    def command(self, p):
        # return ('do_while', p[1], p[3])
        return DoWhile(condition=p[1], commands=p[3])

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        # pidentifier = ('int', p[1], p.lineno)
        # return ('for', pidentifier, p[3], p[5], p[7])
        pidentifier = Int(pidentifier=p[1], lineno=p.lineno)
        return For(pidentifier=pidentifier, from_val=p[3], to_val=p[5], commands=p[7])

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        pidentifier = Int(pidentifier=p[1], lineno=p.lineno)
        return ForDownTo(pidentifier=pidentifier, from_val=p[3], to_val=p[5], commands=p[7])

    @_('READ identifier SEMICOLON')
    def command(self, p):
        # return ('read', p[1])
        return Read(to_variable=p[1])

    @_('WRITE value SEMICOLON')
    def command(self, p):
        # return ('write', p[1])
        return Write(from_variable=p[1])

    # expression:
    # Handles expressions
    @_('value')
    def expression(self, p):
        # return p[0]
        return ValueAssignment(a=p[0])

    @_('value PLUS value',
       'value MINUS value',
       'value TIMES value',
       'value DIVIDE value',
       'value MODULO value')
    def expression(self, p):
        # return ('expression', p[1], p[0], p[2])
        return Expression(a=p[0], operand=p[1], b=p[2])

    # condition:
    # Handles conditional statements
    @_('value EQUALS value',
       'value NOT_EQUALS value',
       'value LESSER_THAN value',
       'value GREATER_THAN value',
       'value LESSER_EQUALS value',
       'value GREATER_EQUALS value')
    def condition(self, p):
        # return ('condition', p[1], p[0], p[2])
        return Condition(p[0], p[1], p[2])

    # value:
    # Handles value statements
    @_('NUMBER',
       'identifier')
    def value(self, p):
        return p[0]

    # identifier:
    # Handles identifier statements
    @_('PIDENTIFIER')
    def identifier(self, p):
        # return ('int', p[0], p.lineno)
        return Int(pidentifier=p[0], lineno=p.lineno)

    @_('PIDENTIFIER LPAREN PIDENTIFIER RPAREN')
    def identifier(self, p):
        # i = ('int', p[2], p.lineno)
        i = Int(pidentifier=p[2], lineno=p.lineno)
        # return ('int[]', p[0], i, p.lineno)
        return IntArrayElement(array_pid=p[0], element=i, lineno=p.lineno)

    @_('PIDENTIFIER LPAREN NUMBER RPAREN')
    def identifier(self, p):
        # return ('int[]', p[0], p[2], p.lineno)
        return IntArrayElement(array_pid=p[0], element=p[2], lineno=p.lineno)

    @_('')
    def empty(self, p):
        pass

    # Error handling
    def error(self, p):
        logging.error("Line {}, unknown input {}".format(p.lineno, p.value))
        raise Exception("Line {}, unknown input {}".format(p.lineno, p.value))



