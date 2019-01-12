# chaistat.py
import logging
from chaiasm import *
from chaiman import *


class ChaiStat(ChaiMan):
    """
    Performs static analysis of code
    """

    def __init__(self, parse_tree, global_variables, memory_indexes):
        self.parse_tree = parse_tree

        self.global_variables = global_variables
        self.memory_indexes = memory_indexes

        self.assembly_code = []
        self.generator = ChaiAsm(parse_tree, global_variables, memory_indexes)

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
                return self.generator.generate_value(value=value_holder), Registries.Value.value

            elif isinstance(value_holder, Int):
                # If we're given variable from which we have to get
                return self.generator.generate_get_value_of_variable(memory_index=self.get_object_memory_location(
                    value_holder)), Registries.Value.value

    def assign(self, assignment):
        """
        Handles the assignment of value to variable
        :return:
        """
        code = []
        to = assignment.identifier
        expression_code, result_reg = self.unwrap_expression(assignment.expression)

        code.extend(expression_code)
        code.extend(self.generator.generate_set_value_from_registry(to=to, from_registry=result_reg))

        return code

    def write(self, write):
        """
        Handles the printing of value to stdout
        :param write:
        :return:
        """
        return self.generator.generate_write(write.from_variable)

    def translate(self, commands):
        """
        Manages the translation
        :return: generated assembly code
        """
        code = []

        for command in commands:

            if isinstance(command, Assign):
                translated_code = self.assign(command)

            elif isinstance(command, Write):
                translated_code = self.write(command)

            self.generator.program_counter += len(translated_code)
            code.extend(translated_code)

        return code

    def insert_jumps(self, translated_commands):
        """
        Inserts absolute jump values into placeholders in translated code
        :type translated_commands: list of translated commands (code)
        :return:
        """
        for i in range(0, len(translated_commands)):
            command = translated_commands[i].split()

            if '$' in command[-1] and ('JZERO' or 'JUMP' in command[0]):
                # If last element contains a placeholder (it is JZERO or JUMP)

                for j in range(0, len(translated_commands)):
                    placeholder_candidate = translated_commands[j].split()

                    if command[-1] in placeholder_candidate[0]:
                        # Replace the placeholder with absolute jump index
                        command[-1] = str(j)
                        translated_commands[i] = ' '.join(command)
                        placeholder_candidate.pop(0)
                        translated_commands[j] = ' '.join(placeholder_candidate)

        return translated_commands

    def manage(self):
        """
        Runs the code
        :return:
        """
        # print("Code tree: {}".format(self.tree))

        logging.basicConfig(level=logging.DEBUG)

        # Divide the program into header (declarations) and code
        header = self.parse_tree[0]
        body = self.parse_tree[1]

        logging.debug("Code header: {}".format(header))
        logging.debug("Code body: {}".format(body))


        # self.alloc_global_vars(header)
        logging.debug("Global variables: {}".format(self.global_variables))
        logging.debug("Assigned indexes: {}".format(self.memory_indexes))

        output = self.translate(body)
        output.append('HALT')

        output = self.insert_jumps(output)

        logging.debug("Chaistat output: {}".format(output))

        outf = open('tests/test1.o', 'w').write('\n'.join(output))