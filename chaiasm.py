# chaiasm.py
from chairegs import Registries
from chaiman import ChaiMan
from scope.chaivars import *
from scope.chaiflow import *

import logging


class ChaiAsm(ChaiMan):
    """
    Handles the translation into assembly code.
    """

    def __init__(self, parse_tree, global_variables, memory_indexes, next_free_memory_index):
        super().__init__(parse_tree, global_variables, memory_indexes, next_free_memory_index)
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

    def generate_get_value(self, operand, target_registry=Registries.Value.value):
        """
        Stores in target registry value of variable a
        :param memory_index:
        :param target_registry:
        :return:
        """
        code = []

        # Store in registries values of variables

        if isinstance(operand, int):
            # If a is a concrete integer value
            code.extend(self.generate_value(value=operand,
                                            target_registry=target_registry))

        # Check if variable has been referenced before assignment
        elif self.get_variable_assigned_to_value(variable=operand):

            if isinstance(operand, Int):
                # If a is a variable from which we have to get the value
                code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(operand),
                                                                target_registry=target_registry))

            elif isinstance(operand, IntArrayElement):
                # If a is an array value_holder from which we have to get the value
                code.extend(self.generate_get_value_of_array_element(array_element=operand,
                                                                     target_registry=target_registry))
        else:
            raise Exception(
                "generate_get_value: variable '{}' referenced before assignment".format(operand.pidentifier))

        return code

    def generate_get_value_of_variable(self, memory_index, target_registry=Registries.Value.value):
        """
        Generates code responsible for getting value of variable from memory
        :param target_registry: registry which will hold the value of variable
        :param memory_index: memory index storing the value
        :return: code
        """
        code = []

        # if self.get_variable_assigned_to_value(self.get_object_from_memory(
        #         pidentifier=self.get_pidentifier_assigned_to_mem_index(
        #         index=memory_index))):

        code.extend(self.generate_constant(constant_value=memory_index, target_registry=Registries.Constant.value))
        code.append('LOAD {}'.format(target_registry))
        return code

        # else:
        #     raise Exception("get_value_of_variable: variable at memory index '{}' referenced before "
        #                     "assignment".format(memory_index))

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

            # logging.debug("get_value_of_array_element: getting value from array '{}' at index '{}".format(array,
            #                                                                                               element_index_value_holder))

            code.extend(self.generate_get_value_of_variable(memory_index=element_memory_location,
                                                            target_registry=target_registry))

        elif isinstance(element_index_value_holder, Int):
            # If we have to get the index of array element from the variable's value
            code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(
                element_index_value_holder), target_registry=Registries.MemoryIndex.value))

            # Add 1
            code.append('INC {}'.format(Registries.MemoryIndex.value))

            # Subtract array's from_val
            code.extend(self.generate_value(value=array.from_val, target_registry=Registries.G.value))
            code.append('SUB {} {}'.format(Registries.MemoryIndex.value, Registries.G.value))

            # Add memory location of array
            code.extend(self.generate_append_constant(constant_value=self.get_object_memory_location(array),
                                                      target_registry=Registries.MemoryIndex.value))

            # Load variable from memory to target_registry
            code.append('LOAD {}'.format(target_registry))

            # Calculate the array offset
            # element_memory_offset = 1 - array.from_val + self.get_object_memory_location(array)

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

                logging.debug("Value holder mem index: {}, offset should be: {}".format(self.get_object_memory_location(
                    value_holder), element_memory_offset))

                code.extend(self.generate_get_value_of_variable(memory_index=self.get_object_memory_location(
                    value_holder), target_registry=Registries.MemoryIndex.value))

                # Add 1
                code.append('INC {}'.format(Registries.MemoryIndex.value))

                # Subtract array's from_val
                code.extend(self.generate_value(value=array.from_val, target_registry=Registries.G.value))
                code.append('SUB {} {}'.format(Registries.MemoryIndex.value, Registries.G.value))

                # Add memory location of array
                code.extend(self.generate_append_constant(constant_value=self.get_object_memory_location(array),
                                                          target_registry=Registries.MemoryIndex.value))

                # Load variable from memory to target_registry
                code.append('STORE {}'.format(from_registry))

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
        code.extend(self.generate_get_value(operand=first_operand,
                                            target_registry=Registries.ExpressionFirstOperand.value))

        code.extend(self.generate_get_value(operand=second_operand,
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

            code.append('SUB D D'.format(identifier))  # 1 - Clean B for use later

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

            if oper == operator.floordiv:
                result_reg = Registries.ExpressionDivResult.value
            elif oper == operator.mod:
                code.append('COPY D A')
                result_reg = Registries.ExpressionModResult.value

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

    def generate_read(self, to_variable):
        """
        Handles generation of code responsible for assigning value from stdin to variable.
        :param to_variable:
        :return:
        """
        code = []

        code.append('GET {}'.format(Registries.Value.value))
        code.extend(self.generate_set_value_from_registry(to=to_variable))

        return code

    def generate_conditional_statement(self, first_operand, second_operand, oper):
        """
        Generates the conditional statement for given operations
        :param first_operand:
        :param second_operand:
        :param oper: comparison operator
        :return:
        """
        code = []

        # Get values of first operand, second operand to registries
        code.extend(self.generate_get_value(operand=first_operand,
                                            target_registry=Registries.ConditionFirstOperand.value))
        code.extend(self.generate_get_value(operand=second_operand,
                                            target_registry=Registries.ConditionSecondOperand.value))

        comp_code, jump_id = self.generate_comparison(oper=oper)
        code.extend(comp_code)

        return code, jump_id

    def generate_comparison(self, oper):
        """
        Generates code responsible of performing comparisons between given operands
        :param oper: comparison operator
        :return: assembly code
        """
        code = []

        first_reg = Registries.ConditionFirstOperand.value
        second_reg = Registries.ConditionSecondOperand.value
        jump_identifier = self.get_jump_identifier()

        if oper == operator.gt:
            # is a > b -> (is a - b > 0 <-> is a - b < 0)
            # (because we only work with positive numbers)
            code.append('SUB {} {} # GT/LT CONDITION'.format(first_reg, second_reg))
            code.append('JZERO {} $end_cond_{}'.format(first_reg, jump_identifier))
            # Afterwards $end_cond_{} -> jump to end (of commands

        elif oper == operator.lt:
            code.append('SUB {} {} # GT/LT CONDITION'.format(second_reg, first_reg))
            code.append('JZERO {} $end_cond_{}'.format(second_reg, jump_identifier))
            # Afterwards $end_cond_{} -> jump to end (of commands

        elif oper == operator.ge:
            # is a >= b
            code.append('INC {} # GE/LE COND'.format(first_reg))
            code.append('SUB {} {}'.format(first_reg, second_reg))
            code.append('JZERO {} $end_cond_{}'.format(first_reg, jump_identifier))
            # Afterwards $end_cond_{} -> jump to end (of commands)

        elif oper == operator.le:
            code.append('INC {} # GE/LE COND'.format(second_reg))
            code.append('SUB {} {}'.format(second_reg, first_reg))
            code.append('JZERO {} $end_cond_{}'.format(second_reg, jump_identifier))

        elif oper == operator.eq:
            # is a == b
            code.append('INC {} # BEGIN EQ COND'.format(second_reg))
            code.append('SUB {} {}'.format(second_reg, first_reg))
            code.append('JZERO {} $end_cond_{}'.format(second_reg, jump_identifier))
            code.append('DEC {}'.format(second_reg))
            code.append('JZERO {} $commands_cond_{}'.format(second_reg, jump_identifier))
            code.append('JUMP $end_cond_{}'.format(jump_identifier))
            # $end_cond_{} -> jump to commands

        elif oper == operator.ne:
            # is a != b
            code.append('INC {} # BEGIN NEQ COND'.format(second_reg))
            code.append('SUB {} {}'.format(second_reg, first_reg))
            code.append('JZERO {} $commands_cond_{}'.format(second_reg, jump_identifier))
            code.append('DEC {}'.format(second_reg))
            code.append('JZERO {} $end_cond_{}'.format(second_reg, jump_identifier))
            # $end_cond_{} -> jump to end

        return code, jump_identifier

    def generate_for_preparations(self, loop_iterator, loop_lower_bound, loop_upper_bound):
        """
        Generates the code preparing the for loop execution
        :param loop_iterator: variable
        :param loop_lower_bound: value
        :param loop_upper_bound: value
        :return:
        """
        code = []

        # Set the initial value of iterator
        code.extend(self.generate_get_value(operand=loop_lower_bound,
                                            target_registry=Registries.ConditionFirstOperand.value))
        code.extend(self.generate_set_value_from_registry(from_registry=Registries.ConditionFirstOperand.value,
                                                          to=loop_iterator))

        # Store upper bound value in second comparison registry
        code.extend(self.generate_get_value(operand=loop_upper_bound,
                                            target_registry=Registries.ConditionSecondOperand.value))

        # Create variable upper_bound
        ubound = Int(pidentifier='for_ubound_{}'.format(loop_iterator.pidentifier), lineno=loop_iterator.lineno)
        ubound.set_as_iterator()
        ubound.set_value_has_been_set()
        self.declare_global_variable(variable=ubound)

        # Store value of upper_bound in variable
        code.extend(self.generate_set_value_from_registry(to=ubound,
                                                          from_registry=Registries.ConditionSecondOperand.value))

        # Generate the comparison code
        comp_code, jump_id = self.generate_comparison(oper=operator.le)
        code.extend(comp_code)

        return code, jump_id

    def generate_for_comparison(self, loop_iterator):
        """
        Generates the for loop condition comparison (performed after initial preparations)
        :param loop_iterator:
        :return:
        """
        code = []

        # Get value of loop iterator to registry and increment it by one (i++)
        code.extend(self.generate_get_value(operand=loop_iterator,
                                            target_registry=Registries.ConditionFirstOperand.value))
        code.extend(self.generate_append_constant(constant_value=1,
                                                  target_registry=Registries.ConditionFirstOperand.value))

        # Store updated value of loop iterator
        code.extend(self.generate_set_value_from_registry(to=loop_iterator,
                                                          from_registry=Registries.ConditionFirstOperand.value))

        # Get value of loop_upper_bound to second registry
        ubound = self.get_object_from_memory(pidentifier='for_ubound_{}'.format(loop_iterator.pidentifier))

        logging.debug("Ubound got from mem: {}, mem: {}, globs: {}".format(ubound, self.memory_indexes,
                                                                           self.global_variables))

        code.extend(self.generate_get_value(operand=ubound,
                                            target_registry=Registries.ConditionSecondOperand.value))

        # Generate comparison code with <= operator
        comp_code, jump_id = self.generate_comparison(oper=operator.le)
        code.extend(comp_code)

        return code, jump_id

    def generate_for_downto_preparations(self, loop_iterator, loop_lower_bound, loop_upper_bound):
        """
        Generates the code preparing the for loop execution
        :param loop_iterator: variable
        :param loop_lower_bound: value
        :param loop_upper_bound: value
        :return:
        """
        code = []

        # Set the initial value of iterator
        code.extend(self.generate_get_value(operand=loop_upper_bound,
                                            target_registry=Registries.ConditionFirstOperand.value))
        code.extend(self.generate_set_value_from_registry(from_registry=Registries.ConditionFirstOperand.value,
                                                          to=loop_iterator))

        # Store upper bound value in second comparison registry
        code.extend(self.generate_get_value(operand=loop_lower_bound,
                                            target_registry=Registries.ConditionSecondOperand.value))

        # Create variable upper_bound
        lbound = Int(pidentifier='for_lbound_{}'.format(loop_iterator.pidentifier), lineno=loop_iterator.lineno)
        lbound.set_value_has_been_set()
        lbound.set_as_iterator()
        self.declare_global_variable(variable=lbound)

        # Store value of upper_bound in variable
        code.extend(self.generate_set_value_from_registry(to=lbound,
                                                          from_registry=Registries.ConditionSecondOperand.value))

        # Generate the comparison code
        comp_code, jump_id = self.generate_comparison(oper=operator.ge)
        code.extend(comp_code)

        return code, jump_id

    def generate_for_downto_comparison(self, loop_iterator):
        """
        Generates the for loop condition comparison (performed after initial preparations)
        :param loop_iterator:
        :return:
        """
        code = []

        # Get value of loop iterator to registry and decrement it by one (i++)
        code.extend(self.generate_get_value(operand=loop_iterator,
                                            target_registry=Registries.ConditionFirstOperand.value))
        code.append('DEC {}'.format(Registries.ConditionFirstOperand.value))

        # Store updated value of loop iterator
        code.extend(self.generate_set_value_from_registry(to=loop_iterator,
                                                          from_registry=Registries.ConditionFirstOperand.value))

        # Get value of loop_upper_bound to second registry
        lbound = self.get_object_from_memory(pidentifier='for_lbound_{}'.format(loop_iterator.pidentifier))

        logging.debug("Lbound got from mem: {}, mem: {}, globs: {}".format(lbound, self.memory_indexes,
                                                                           self.global_variables))

        code.extend(self.generate_get_value(operand=lbound,
                                            target_registry=Registries.ConditionSecondOperand.value))

        # Generate comparison code with <= operator
        comp_code, jump_id = self.generate_comparison(oper=operator.ge)
        code.extend(comp_code)

        return code, jump_id
