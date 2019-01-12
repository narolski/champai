# chaiasm.py
from chairegs import Registries
from chaiman import ChaiMan
from scope.chaivars import *
from scope.chaiflow import *


class ChaiAsm(ChaiMan):
    """
    Handles the translation into assembly code.
    """
    def __init__(self, parse_tree, global_variables, memory_indexes):
        super().__init__(parse_tree, global_variables, memory_indexes)
        self.program_counter = 0
        self.jump_identifier = 0

    def get_jump_identifier(self):
        jid = self.jump_identifier
        self.jump_identifier += 1
        return jid

    def generate_constant(self, constant_value, target_registry=Registries.Constant.value):
        """
        Generates the constant in given target registry
        :param constant_value: value of constant to generate
        :param target_registry: registry where to store the value
        :return: code
        """
        code = []
        code.append('SUB {} {}'.format(target_registry, target_registry))
        code.extend(self.generate_append_constant(constant_value, target_registry))
        return code

    def generate_append_constant(self, constant_value, target_registry=Registries.Constant.value):
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

    def generate_value(self, value, target_registry=Registries.Value.value):
        """
        Generates the given value and stores it in given registry
        :param value: value to generate
        :param target_registry: registry to store the value
        :return:
        """
        return self.generate_constant(constant_value=value, target_registry=target_registry)

    def generate_get_value_of_variable(self, memory_index, target_registry=Registries.Value.value):
        """
        Generates code responsible for getting value of variable from memory
        :param target_registry: registry which will hold the value of variable
        :param memory_index: memory index storing the value
        :return: code
        """
        code = []
        code.extend(self.generate_constant(constant_value=memory_index, target_registry=Registries.Constant.value))
        code.append('LOAD {}'.format(target_registry))
        return code

    def generate_get_value_of_array_element(self, array_element, target_registry=Registries.Value.value):
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
            element_memory_location = element_index_value_holder - array.from_val + 1 + self.get_object_memory_location(
                array)

            code.extend(self.generate_get_value_of_variable(memory_index=element_memory_location, target_registry=target_registry))

        elif isinstance(element_index_value_holder, Int):
            # If we have to get the index of array element from the variable's value
            code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(
                element_index_value_holder), target_registry=target_registry))

            # Calculate the array offset
            element_memory_offset = 1 - array.from_val + self.get_object_memory_location(array)

            if element_memory_offset > 0:
                code.extend(self.generate_append_constant(constant_value=element_memory_offset,
                                                          target_registry=target_registry))

        # NOTE: Grammar does not allow to use value of array as index
        return code

    def generate_set_value_from_registry_to_address(self, to_address, from_registry=Registries.Value.value):
        """
        Sets the value obtained from registry to given memory address
        :param to_address:
        :param from_registry:
        :return:
        """
        code = []
        code.extend(self.generate_constant(constant_value=to_address))
        code.append('STORE {}'.format(from_registry))
        return code

    def generate_set_value_from_registry(self, to, from_registry=Registries.Value.value):
        """
        Sets the value of variable to value stored in given registry
        :param to: variable
        :param from_registry:
        :return:
        """
        if isinstance(to, Int):
            # If assigning to integer variable
            return self.generate_set_value_from_registry_to_address(to_address=self.get_object_memory_location(to),
                                                                    from_registry=from_registry)

        elif isinstance(to, IntArrayElement):
            # If assigning to array element
            array = to.array
            value_holder = to.get_value_holder()

            if isinstance(value_holder, int):
                # If index of the array is known
                element_memory_location = value_holder - array.from_val + 1 + self.get_object_memory_location(array)
                return self.generate_set_value_from_registry_to_address(to_address=element_memory_location,
                                                                        from_registry=from_registry)

            elif isinstance(value_holder, Int):
                # If we have to obtain array index from another variable's value
                code = []
                element_memory_offset = 1 - array.from_val + self.get_object_memory_location(array)

                code.append(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(
                            value_holder), target_registry=Registries.MemoryIndex.value))
                code.append(self.generate_append_constant(constant_value=element_memory_offset,
                                                          target_registry=Registries.MemoryIndex))

                return code

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
            code.extend(self.generate_value(value=first_operand,
                                                      target_registry=Registries.ExpressionFirstOperand.value))

        elif isinstance(first_operand, Int):
            # If a is a variable from which we have to get the value
            code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(first_operand),
                                                                      target_registry=Registries.ExpressionFirstOperand.value))

        elif isinstance(first_operand, IntArrayElement):
            # If a is an array value_holder from which we have to get the value
            code.extend(self.generate_get_value_of_array_element(array_element=first_operand,
                                                                 target_registry=Registries.ExpressionFirstOperand.value))

        if isinstance(second_operand, int):
            # If b is a concrete integer value
            code.extend(self.generate_value(value=second_operand,
                                                      target_registry=Registries.ExpressionSecondOperand.value))

        elif isinstance(second_operand, Int):
            # If b is a variable from which we have to get the value
            code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(second_operand),
                                                                      target_registry=Registries.ExpressionSecondOperand.value))

        elif isinstance(second_operand, IntArrayElement):
            # If b is an array value_holder from which we have to get the value
            code.extend(self.generate_get_value_of_array_element(array_element=second_operand,
                                                                 target_registry=Registries.ExpressionSecondOperand.value))

        # Perform operation on registers
        if oper == operator.add:
            code.append('ADD {} {}'.format(Registries.ExpressionFirstOperand.value,
                                           Registries.ExpressionSecondOperand.value))
            result_reg = Registries.ExpressionAddResult.value

        elif oper == operator.sub:
            code.append('SUB {} {}'.format(Registries.ExpressionFirstOperand.value,
                                           Registries.ExpressionSecondOperand.value))
            result_reg = Registries.ExpressionSubResult.value

        elif oper == operator.mul:
            # TODO: Improve
            identifier = self.get_jump_identifier()

            code.append('SUB D D'.format(identifier)) # 1 - Clean B for use later

            code.append('$mulzerocheck_{} $nextmuliter_{} JZERO C $end_{}'.format(identifier, identifier, identifier))
            # 2 -
            # while b > 0
            code.append('JODD C $mulodd_{}'.format(identifier))  # 3 - if b is odd jump to 6
            code.append('ADD B B')  # 4 - a = a * 2
            code.append('HALF C')  # 5 - d = d / 2
            code.append('JUMP $mulzerocheck_{}'.format(identifier))  # 6 - goto line 1
            code.append('$mulodd_{} ADD D B'.format(identifier))  # 7 - result += a
            code.append('ADD B B')  # 8
            code.append('HALF C')  # 9
            code.append('JUMP $nextmuliter_{}'.format(identifier))  # 10

            # This bit might be changed (but at what cost?)
            code.append('$end_{} INC A'.format(identifier))

            result_reg = Registries.ExpressionMulResult.value

        elif oper == operator.floordiv or oper == operator.mod:
            # TODO: Improve
            identifier = self.get_jump_identifier()

            # regD = regA / regB

            code.append('COPY A B')
            code.append('COPY B C')

            code.append('JZERO B $dzero_{}'.format(identifier))
            code.append('COPY E B')
            code.append('$l1_{} COPY D E'.format(identifier))
            code.append('SUB D A')
            code.append('JZERO D $shle_{}'.format(identifier))
            code.append('JUMP $div_{}'.format(identifier))

            code.append('$shle_{} ADD E E'.format(identifier))
            code.append('JUMP $l1_{}'.format(identifier))
            code.append('$div_{} SUB D D'.format(identifier))

            code.append('$l2_{} COPY C E'.format(identifier))
            code.append('SUB C A')
            code.append('JZERO C $one_{}'.format(identifier))
            code.append('ADD D D')
            code.append('HALF E')
            code.append('JUMP $check_{}'.format(identifier))

            code.append('$one_{} ADD D D'.format(identifier))
            code.append('INC D')
            code.append('SUB A E')
            code.append('HALF E')

            code.append('$check_{} COPY C B'.format(identifier))
            code.append('SUB C E')
            code.append('JZERO C $l2_{}'.format(identifier))
            code.append('JUMP $end_{}'.format(identifier))

            code.append('$dzero_{} SUB A A'.format(identifier))
            code.append('SUB D D'.format(identifier))

            # This can be improved, too!
            code.append('$end_{} INC H'.format(identifier))

            result_reg = Registries.ExpressionDivResult.value

        return code, result_reg

    def generate_write(self, from_variable):
        """
        Handles generation of code responsible for writing out variable's value to stdout
        :param from_variable:
        :return:
        """
        code = []

        if isinstance(from_variable, int):
            code.extend(self.generate_value(value=from_variable))

        elif isinstance(from_variable, Int):
            code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(
                from_variable)))

        elif isinstance(from_variable, IntArrayElement):
            code.extend(self.generate_get_value_of_array_element(array_element=from_variable))

        code.append('PUT {}'.format(Registries.Value.value))
        return code



