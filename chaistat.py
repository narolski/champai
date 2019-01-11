# chaistat.py
from chaiman import ChaiMan
from chairegs import Registries
from chaiasm import ChaiAsm

from scope.chaivars import *
from scope.chaiflow import *


class ChaiStat(ChaiMan):
    """
    Performs static analysis of code
    """

    def __init__(self, parse_tree):
        self.generator = ChaiAsm(parse_tree)

        super().__init__(parse_tree)

    def unwrap_expression(self, expression):
        """
        Generates the code responsible for getting the value of an expression
        :param expression: given expresion
        :return: value of expression
        """

        if isinstance(expression, Operation):
            # If dealing with math operation: a +/-/:/% b
            a, oper, b = expression.return_expression()

            return self.generator.generate_calculate_expression(first_operand=a, second_operand=b, oper=oper)

        elif isinstance(expression, Value):
            # If we're given the value of unwrap_expression
            value_holder = expression.return_value()

            if isinstance(value_holder, int):
                # If we have concrete integer value at this point
                return self.generator.generate_value(value=value_holder)

            elif isinstance(value_holder, Int):
                # If we're given variable from which we have to get
                return self.generator.generate_get_value_of_variable(memory_index=self.get_memory_location(value_holder))




    def assign(self, assignment):
        """
        Handles the assignment of value to variable
        :return:
        """
        code = []
        to = self.get_memory_location(assignment.identifier)
        value = self.unwrap_expression(assignment.unwrap_expression)

        if isinstance(assignment.identifier, Int):
            # Get memory address of integer
            code.extend()





