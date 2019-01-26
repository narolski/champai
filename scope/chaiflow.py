# chaiflow.py

import operator


class ControlFlow:
    """
    Defines common interface for control flow methods.
    """
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

    def return_condition(self):
        return self.condition

    def return_commands(self):
        return self.commands

class ControlOperation:
    """
    One-line operations like assignments, reads etc.
    """


class Assign(ControlOperation):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    # def __repr__(self):
    #     return str("\n\t<{} := {}>".format(self.identifier, self.unwrap_expression))


class Read(ControlOperation):
    def __init__(self, to_variable):
        super().__init__()
        self.to_variable = to_variable

    # def __repr__(self):
    #     return str("\n<Read to {}>".format(self.to_variable))


class Write(ControlOperation):
    def __init__(self, from_variable):
        self.from_variable = from_variable

    # def __repr__(self):
    #     return str("\n<Write from {}>".format(self.from_variable))


class While(ControlFlow):
    def __init__(self, condition, commands):
        super().__init__(condition, commands)

    # def __repr__(self):
    #     return str("\n<While {} do>\n{}\n".format(self.condition, self.commands))


class DoWhile(ControlFlow):
    def __init__(self, condition, commands):
        super().__init__(condition, commands)


    # def __repr__(self):
    #     return str("\n<do>\n{}\n<while {}>\n".format(self.commands, self.condition))


class If(ControlFlow):
    def __init__(self, condition, commands):
        super().__init__(condition, commands)

    # def __repr__(self):
    #     return str("\n<If {} do>\n\t{}\n".format(self.condition, self.commands))


class IfElse(If):
    def __init__(self, condition, commands, alt_commands):
        super().__init__(condition, commands)
        self.alt_commands = alt_commands

    def return_alt_commands(self):
        return self.alt_commands

    # def __repr__(self):
    #     return str("\n<If {} do>\n\t{}\n<else>\n\t{}\n".format(self.condition, self.commands, self.alt_commands))


class For():
    def __init__(self, iterator, from_val, to_val, commands):
        self.pidentifier = iterator
        self.from_val = from_val
        self.to_val = to_val
        self.commands = commands

    def return_for_loop_conditions(self):
        return self.pidentifier, self.from_val, self.to_val

    # def __repr__(self):
    #     return str("\n<For {} from {} to {} do>\n{}\n".format(self.pidentifier, self.from_val, self.to_val, self.commands))


class ForDownTo():
    def __init__(self, iterator, from_val, to_val, commands):
        self.pidentifier = iterator
        self.from_val = from_val
        self.to_val = to_val
        self.commands = commands

    def return_for_downto_loop_conditions(self):
        return self.pidentifier, self.from_val, self.to_val


class Condition:
    def __init__(self, p, relate, q):
        self.p = p
        self.q = q
        self.relate = relate

    # def __repr__(self):
    #     return str("<{} {} {}>".format(self.p, str(self.relate), self. q))

    def get_relation(self):
        return {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '=': operator.eq,
            '!=': operator.ne
            }[self.relate]

    def return_condition(self):
        return self.p, self.get_relation(), self.q


class Value:
    def __init__(self, a):
        self.a = a

    def return_value(self):
        return self.a


class Operation(Value):
    def __init__(self, a, operand, b):
        super().__init__(a)
        self.operand = operand
        self.b = b

    def get_operand(self):
        return {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.floordiv, # TODO: Check if this is correct for the GVM
            '%': operator.mod,
        }[self.operand]

    def return_expression(self):
        return self.a, self.get_operand(), self.b












