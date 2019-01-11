# chaiasm.py
import operator

from chaistat import ChaiStat
from chairegs import Registries

from scope.chaivars import *
from scope.chaiflow import *


class ChaiAsm(ChaiStat):
    """
    Handles the translation into assembly code.
    """
    def __init__(self, parse_tree):
        super().__init__(parse_tree)

    def generate_constant(self, constant_value, target_registry=Registries.Constant):
        """
        Generates the constant in given target registry
        :param constant_value: value of constant to generate
        :param target_registry: registry where to store the value
        :return: code
        """
        code = []
        code.append('SUB {} {}'.format(target_registry, target_registry))
        code.extend(self.append_constant(constant_value, target_registry))
        return code

    def append_constant(self, constant_value, target_registry=Registries.Constant):
        """
        Appends to the target registry given constant value
        :param constant_value:
        :param target_registry:
        :return:
        """
        code = []

        if 0 < constant_value < 10:
            for i in range(constant_value):
                code.append('INC {}'.format(target_registry))
        else:
            bin_repr = str(bin(constant_value)[2:])
            repr_length = len(bin_repr)

            for i in range(0, repr_length):
                if bin_repr[i] == '1':
                    code.append('INC {}'.format(target_registry))
                if i < (repr_length - 1):
                    code.append('ADD {} {}'.format(target_registry, target_registry))

        return code

    def generate_value(self, value, target_registry=Registries.Value):
        """
        Generates the given value and stores it in given registry
        :param value: value to generate
        :param target_registry: registry to store the value
        :return:
        """
        return self.generate_constant(constant_value=value, target_registry=target_registry)

    def generate_get_value_of_variable(self, memory_index, target_registry=Registries.Value):
        """
        Generates code responsible for getting value of variable from memory
        :param target_registry: registry which will hold the value of variable
        :param memory_index: memory index storing the value
        :return: code
        """
        code = []
        code.extend(self.generate_constant(constant_value=memory_index, target_registry=Registries.Constant))
        code.append('LOAD {}'.format(target_registry))
        return code

    def generate_get_value_of_array_element(self, array_element, target_registry=Registries.Value):
        """
        Returns the value of given array value_holder
        :param array_element:
        :param target_registry:
        :return:
        """
        code = []

        array = array_element.array
        element_index_value_holder = array_element.value_holder

        if isinstance(element_index_value_holder, int):
            # If index of array is known
            element_memory_index = element_index_value_holder - array.from_val + 1 + self.get_object_memory_location(
                array)

            code.extend(self.generate_get_value_of_variable(memory_index=element_memory_index, target_registry=target_registry))

        elif isinstance(element_index_value_holder, Int):
            # If we have to get the index of array element from the variable's value
            code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(
                element_index_value_holder), target_registry=target_registry))

            # Calculate the array offset
            element_memory_offset = 1 - array.from_val + self.get_object_memory_location(array)

            if element_memory_offset > 0:
                code.extend(self.append_constant(constant_value=element_memory_offset,
                                                 target_registry=target_registry))

        # NOTE: Grammar does not allow to use value of array as index
        return code

    def generate_set_value_from_registry(self, to, from_registry=Registries.Value):
        """
        Sets the value of variable to value stored in given registry
        :param to: variable
        :param from_registry:
        :return:
        """
        code = []

        if isinstance(to, Int):
            # If assigning to integer variable
            memory_location = self.get_object_memory_location(to)
            code.extend(self.generate_constant(constant_value=memory_location))
            code.append('STORE {}'.format(from_registry))

        elif isinstance(to, IntArrayElement):
            # If assigning to array element
            array = to.array


    def generate_calculate_expression(self, first_operand, second_operand, oper):
        """
        Performs the calculation of given expression value
        :param first_operand: variable or value
        :param second_operand: variable or value
        :param oper: operator
        :return:
        """
        code = []

        # Store in registries values of variables
        if isinstance(first_operand, int):
            # If a is a concrete integer value
            code.extend(self.generator.generate_value(value=first_operand,
                                                      target_registry=Registries.ExpressionFirstOperand))

        elif isinstance(first_operand, Int):
            # If a is a variable from which we have to get the value
            code.extend(self.generator.generate_get_value_of_variable(memory_index=self.get_memory_location(first_operand),
                                                                      target_registry=Registries.ExpressionFirstOperand))

        elif isinstance(first_operand, IntArrayElement):
            # If a is an array value_holder from which we have to get the value
            code.extend(self.generate_get_value_of_array_element(array_element=first_operand,
                                                                 target_registry=Registries.ExpressionFirstOperand))

        if isinstance(second_operand, int):
            # If b is a concrete integer value
            code.extend(self.generator.generate_value(value=second_operand,
                                                      target_registry=Registries.ExpressionSecondOperand))

        elif isinstance(second_operand, Int):
            # If b is a variable from which we have to get the value
            code.extend(self.generator.generate_get_value_of_variable(memory_index=self.get_memory_location(second_operand),
                                                                      target_registry=Registries.ExpressionSecondOperand))

        elif isinstance(second_operand, IntArrayElement):
            # If b is an array value_holder from which we have to get the value
            code.extend(self.generate_get_value_of_array_element(array_element=second_operand,
                                                                 target_registry=Registries.ExpressionSecondOperand))

        # Perform operation on registers
        if oper == operator.add:
            code.append('ADD {} {}'.format(Registries.ExpressionFirstOperand, Registries.ExpressionSecondOperand))

        elif oper == operator.sub:
            code.append('ADD {} {}'.format(Registries.ExpressionFirstOperand, Registries.ExpressionSecondOperand))

        elif oper == operator.mul:
            pass

        elif oper == operator.floordiv:
            pass

        return code





