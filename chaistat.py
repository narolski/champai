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

    def if_statement(self, operation):
        """
        Handles the conditional statement (if, if-else)
        :param operation: control flow operation wrapper
        :return: assembly code
        """
        code = []
        first_operand, oper, second_operand = operation.condition.return_condition()
        commands = operation.commands

        # Generate condition check
        cond_code, jump_identifier = self.generator.generate_conditional_statement(first_operand=first_operand,
                                                              second_operand=second_operand,
                                                                  oper=oper)
        code.extend(cond_code)

        # Delegate translation of commands
        translated_commands = self.translate(commands)

        if oper == operator.eq or oper == operator.ne:
            # If dealing with eq or neq append $commands_cond_{} marker to first line of commands
            translated_commands[0] = '$commands_cond_{} '.format(jump_identifier) + translated_commands[0]

        if isinstance(operation, IfElse):
            # If handling if-else, jump through if commands upon execution
            translated_commands.append('JUMP $end_jumpthrough_else_{}'.format(jump_identifier))

        code.extend(translated_commands)
        code.append('$end_cond_{} INC A'.format(jump_identifier))

        # If handling if-else statement
        if isinstance(operation, IfElse):
            alt_commands = operation.return_alt_commands()
            code.extend(self.translate(alt_commands))

            # Add marker for end
            code.append("$end_jumpthrough_else_{} INC A".format(jump_identifier))

        return code

    def while_statement(self, operation):
        """
        Handles the while statement control flow operation
        :param operation: control flow operation wrapper
        :return: assembly code
        """
        code = []
        first_operand, oper, second_operand = operation.condition.return_condition()
        commands = operation.commands

        # Generate condition check
        cond_code, jump_identifier = self.generator.generate_conditional_statement(first_operand=first_operand,
                                                                                   second_operand=second_operand,
                                                                                   oper=oper)

        cond_code[0] = '$while_cond_check_{} '.format(jump_identifier) + cond_code[0]
        code.extend(cond_code)

        # Delegate translation of commands
        translated_commands = self.translate(commands)

        if oper == operator.eq or oper == operator.ne:
            # If dealing with eq or neq append $commands_cond_{} marker to first line of commands
            translated_commands[0] = '$commands_cond_{} '.format(jump_identifier) + translated_commands[0]

        code.extend(translated_commands)

        # Return to condition check after command execution
        code.append('JUMP $while_cond_check_{}'.format(jump_identifier))

        # Mark end of loop
        code.append('$end_cond_{} INC A'.format(jump_identifier))

        return code

    def do_while_statement(self, operation):
        """
        Handles do-while statement control flow operation
        :param operation:
        :return:
        """
        code = []
        first_operand, oper, second_operand = operation.condition.return_condition()
        commands = operation.commands

        # Generate condition check
        cond_code, jump_identifier = self.generator.generate_conditional_statement(first_operand=first_operand,
                                                                                   second_operand=second_operand,
                                                                                   oper=oper)

        # Delegate translation of commands
        translated_commands = self.translate(commands)

        # Mark where to jump to perform do part of statement
        translated_commands[0] = '$commands_cond_{} '.format(jump_identifier) + translated_commands[0]

        code.extend(translated_commands)
        code.extend(cond_code)

        # This time after condition jump to the commands
        code.append('JUMP $commands_cond_{}'.format(jump_identifier))

        # Mark end of loop
        code.append('$end_cond_{} INC A'.format(jump_identifier))

        return code

    def read(self, read):
        """
        Handles the reading of value from stdin
        :param read:
        :return:
        """
        return self.generator.generate_read(read.to_variable)

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

            elif isinstance(command, Read):
                translated_code = self.read(command)

            elif isinstance(command, If):
                translated_code = self.if_statement(command)

            elif isinstance(command, While):
                translated_code = self.while_statement(command)

            elif isinstance(command, DoWhile):
                translated_code = self.do_while_statement(command)

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

            # Find placeholder
            if '$' in command[0]:
                placeholder = command[0]

                for j in range(0, len(translated_commands)):
                    jump_command_candidate = translated_commands[j].split()

                    if placeholder in jump_command_candidate[-1]:
                        # Replace placeholder in JUMP/JODD/JZERO with absolute index
                        jump_command_candidate[-1] = str(i)
                        translated_commands[j] = ' '.join(jump_command_candidate)

                # Remove placeholder after all replacements have been performed
                command.pop(0)
                translated_commands[i] = ' '.join(command)

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
        # NOTE: Need to go through twice to eliminate double-jumps in single line.
        output = self.insert_jumps(output)


        logging.debug("Chaistat output: {}".format(output))

        outf = open('tests/test3.o', 'w').write('\n'.join(output))