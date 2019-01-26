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

    def __init__(self):
        self.global_variables = {}
        self.memory_indexes = {}
        self.next_free_memory_index = 0
        self.iterator_num = 0

    def declare_global_variable(self, variable):
        """
        Declares global variable in global variables dictionary
        :param variable:
        :return:
        """
        if not variable.pidentifier in self.global_variables.keys():
            self.global_variables[variable.pidentifier] = variable
            self.memory_indexes[variable.pidentifier] = self.next_free_memory_index

            if isinstance(variable, Int):
                self.next_free_memory_index += 1
            elif isinstance(variable, IntArray):
                self.next_free_memory_index += variable.length
        else:
            raise Exception("Variable with pidentifier {} was already declared".format(variable.pidentifier))

    def get_global_variable(self, pidentifier):
        return self.global_variables[pidentifier]

    def solve_iterator_collision(self):
        num = self.iterator_num
        self.iterator_num += 1
        return num

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

        integer = Int(pidentifier=p[1], lineno=p.lineno)
        self.declare_global_variable(integer)

        p[0].append(integer)
        return p[0]

    @_('declarations PIDENTIFIER LPAREN NUMBER COLON NUMBER RPAREN SEMICOLON')
    def declarations(self, p):
        p[0] = list(p[0]) if p[0] else []
        # p[0].append(('int[]', p[1], p[3], p[5], p.lineno))
        array = IntArray(pidentifier=p[1], lineno=p.lineno, from_val=p[3], to_val=p[5])
        self.declare_global_variable(array)

        p[0].append(array)
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
        return DoWhile(condition=p[3], commands=p[1])

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        # pidentifier = ('int', p[1], p.lineno)
        # return ('for', pidentifier, p[3], p[5], p[7])
        # if p[1] in self.global_variables.keys():
        #     p[1] = p[1] + '_{}'.format(self.solve_iterator_collision())

        iterator = Int(pidentifier=p[1], lineno=p.lineno)
        iterator.set_as_iterator()
        iterator.set_value_has_been_set()

        if iterator.pidentifier not in self.global_variables.keys():
            self.declare_global_variable(iterator)

        return For(iterator=iterator, from_val=p[3], to_val=p[5], commands=p[7])

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):

        # if p[1] in self.global_variables.keys():
        #     p[1] = p[1] + '_{}'.format(self.solve_iterator_collision())

        iterator = Int(pidentifier=p[1], lineno=p.lineno)
        iterator.set_as_iterator()
        iterator.set_value_has_been_set()

        if iterator.pidentifier not in self.global_variables.keys():
            self.declare_global_variable(iterator)

        return ForDownTo(iterator=iterator, from_val=p[3], to_val=p[5], commands=p[7])

    @_('READ identifier SEMICOLON')
    def command(self, p):
        # return ('read', p[1])
        return Read(to_variable=p[1])

    @_('WRITE value SEMICOLON')
    def command(self, p):
        # return ('write', p[1])
        return Write(from_variable=p[1])

    # unwrap_expression:
    # Handles expressions
    @_('value')
    def expression(self, p):
        # return p[0]
        return Value(a=p[0])

    @_('value PLUS value',
       'value MINUS value',
       'value TIMES value',
       'value DIVIDE value',
       'value MODULO value')
    def expression(self, p):
        # return ('unwrap_expression', p[1], p[0], p[2])
        return Operation(a=p[0], operand=p[1], b=p[2])

    # condition:
    # Handles conditional statements
    @_('value LESSER_EQUALS value',
       'value GREATER_EQUALS value',
       'value EQUALS value',
       'value NOT_EQUALS value',
       'value LESSER_THAN value',
       'value GREATER_THAN value',)
    def condition(self, p):
        # return ('condition', p[1], p[0], p[2])
        return Condition(p[0], p[1], p[2])

    # value:
    # Handles value statements
    @_('identifier')
    def value(self, p):
        return p[0]

    @_('NUMBER')
    def value(self, p):
        return int(p[0])


    # identifier:
    # Handles identifier statements
    @_('PIDENTIFIER')
    def identifier(self, p):
        # return ('int', p[0], p.lineno)
        # return self.get_global_variable(pidentifier=p[0])
        return Int(pidentifier=p[0], lineno=p.lineno)

    @_('PIDENTIFIER LPAREN PIDENTIFIER RPAREN')
    def identifier(self, p):
        # i = ('int', p[2], p.lineno)
        # i = self.get_global_variable(pidentifier=p[2])
        i = Int(pidentifier=p[2], lineno=p.lineno)

        return IntArrayElement(array=self.get_global_variable(pidentifier=p[0]), value_holder=i, lineno=p.lineno)

    @_('PIDENTIFIER LPAREN NUMBER RPAREN')
    def identifier(self, p):
        # return ('int[]', p[0], p[2], p.lineno)
        return IntArrayElement(array=self.get_global_variable(pidentifier=p[0]), value_holder=int(p[2]),
                               lineno=p.lineno)

    @_('')
    def empty(self, p):
        pass

    # Error handling
    def error(self, p):
        # logging.error("Line {}, unknown input {}".format(p.lineno, p.value))
        raise Exception("Unknown input '{}' in line {}".format(p.value, p.lineno))



