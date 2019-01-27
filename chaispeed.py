# chaispeed.py
import logging
from collections import defaultdict

from scope.chaivars import *
from scope.chaiflow import *


class ChaiSpeed:

    def __init__(self, global_variables, memory_indexes, next_free_memory_index):
        self.global_variables = global_variables
        self.memory_indexes = memory_indexes
        self.next_free_memory_index = next_free_memory_index

    def get_object_from_memory(self, pidentifier):
        """
        Returns the object from memory
        :param pidentifier: object identifier
        :return: object
        """
        return self.global_variables[pidentifier]

    def count_occurences(self, parse_tree):
        """
        Counts the number of occurences of variables.
        :return:
        """
        occurences = defaultdict(int)

        for operation in parse_tree:

            if isinstance(operation, Read):
                occurences[operation.to_variable.pidentifier] += 1

            elif isinstance(operation, Write):
                occurences[operation.from_variable.pidentifier] += 1

            elif isinstance(operation, Assign):
                occurences[operation.identifier.pidentifier] += 1

                if isinstance(operation.expression, Value):

                    if isinstance(operation.expression.a, Int):
                        occurences[operation.expression.a.pidentifier] += 1

                    elif isinstance(operation.expression.a, IntArrayElement):
                        occurences[operation.expression.a.array.pidentifier] += 1

                        if isinstance(operation.expression.a.value_holder, Int):
                            occurences[operation.expression.a.value_holder.pidentifier] += 1

                elif isinstance(operation.expression, Operation):

                    if isinstance(operation.expression.a, Int):
                        occurences[operation.expression.a.pidentifier] += 1

                    elif isinstance(operation.expression.a, IntArrayElement):
                        occurences[operation.expression.a.array.pidentifier] += 1

                        if isinstance(operation.expression.a.value_holder, Int):
                            occurences[operation.expression.a.value_holder.pidentifier] += 1

                    if isinstance(operation.expression.b, Int):
                        occurences[operation.expression.b.pidentifier] += 1

                    elif isinstance(operation.expression.b, IntArrayElement):
                        occurences[operation.expression.b.array.pidentifier] += 1

                        if isinstance(operation.expression.b.value_holder, Int):
                            occurences[operation.expression.b.value_holder.pidentifier] += 1

            elif isinstance(operation, (While, DoWhile, If, IfElse)):

                if isinstance(operation.condition.p, Int):
                    occurences[operation.condition.p.pidentifier] += 1

                elif isinstance(operation.condition.p, IntArrayElement):
                    occurences[operation.condition.p.array.pidentifier] += 1

                    if isinstance(operation.condition.p.value_holder, Int):
                        occurences[operation.condition.p.value_holder.pidentifier] += 1

                if isinstance(operation.condition.q, Int):
                    occurences[operation.condition.q.pidentifier] += 1

                elif isinstance(operation.condition.q, IntArrayElement):
                    occurences[operation.condition.q.array.pidentifier] += 1

                    if isinstance(operation.condition.q.value_holder, Int):
                        occurences[operation.condition.q.value_holder.pidentifier] += 1

                internal_occurences = self.count_occurences(parse_tree=operation.commands)

                for key, value in internal_occurences.items():
                    val = value
                    if isinstance(operation, (While, DoWhile)):
                        val = value * 20 # weight of loop

                    occurences[key] += val

                if isinstance(operation, IfElse):
                    else_occurences = self.count_occurences(parse_tree=operation.alt_commands)

                    for key, value in else_occurences.items():
                        occurences[key] += value

            elif isinstance(operation, (For, ForDownTo)):

                # Iterator has the highest possible priority
                occurences[operation.pidentifier.pidentifier] += 1 * 2 * 50 + 1

                if isinstance(operation.from_val, Int):
                    occurences[operation.from_val.pidentifier] += 1 * 20

                elif isinstance(operation.from_val, IntArrayElement):
                    occurences[operation.from_val.array.pidentifier] += 1 * 20

                    if isinstance(operation.from_val.value_holder, Int):
                        occurences[operation.from_val.value_holder.pidentifier] += 1 * 20

                if isinstance(operation.to_val, Int):
                    occurences[operation.to_val.pidentifier] += 1 * 20

                elif isinstance(operation.to_val, IntArrayElement):
                    occurences[operation.to_val.array.pidentifier] += 1 * 20

                    if isinstance(operation.to_val.value_holder, Int):
                        occurences[operation.to_val.value_holder.pidentifier] += 1 * 20

                internal_occurences = self.count_occurences(parse_tree=operation.commands)

                for key, value in internal_occurences.items():
                    occurences[key] += value * 20

        return occurences

    def rearrange_allocations(self, occurences):
        """
        Changes the allocated memory block for declared variables given their occurences
        :param occurences: defaultdict of occurences
        :param self:
        :return:
        """
        current_globs = self.global_variables
        current_mems = self.memory_indexes

        global_vars = {}
        mem_indexes = {}
        next_free_mem_index = 0

        for pidentifier, value in sorted(occurences.items(), key=operator.itemgetter(1), reverse=True):

            if pidentifier in self.global_variables.keys() and pidentifier in self.memory_indexes.keys():
                object = self.get_object_from_memory(pidentifier=pidentifier)
                global_vars[pidentifier] = object
                mem_indexes[pidentifier] = next_free_mem_index

                if isinstance(object, Int):

                    if object.get_is_iterator():
                        # Declare iterator helpers here!
                        lbound = Int(pidentifier='for_lbound_{}'.format(object.pidentifier),
                                     lineno=object.lineno)
                        lbound.set_value_has_been_set()
                        lbound.set_as_iterator()

                        ubound = Int(pidentifier='for_ubound_{}'.format(object.pidentifier),
                                     lineno=object.lineno)
                        ubound.set_value_has_been_set()
                        ubound.set_as_iterator()

                        # Declare ubound, lbound
                        global_vars[lbound.pidentifier] = lbound
                        global_vars[ubound.pidentifier] = ubound

                        mem_indexes[lbound.pidentifier] = next_free_mem_index + 1
                        mem_indexes[ubound.pidentifier] = next_free_mem_index + 2

                        next_free_mem_index += 2

                    next_free_mem_index += 1

                elif isinstance(object, IntArray):
                    next_free_mem_index += object.length

                # Remove object
                del self.memory_indexes[pidentifier]
                del self.global_variables[pidentifier]

        if len(self.global_variables) > 0 or len(self.memory_indexes) > 0:
            # Panic mode
            logging.debug("Panic mode for rearranging vars. Globs contents: {}, indexes: {}".format(
                self.global_variables, self.memory_indexes))
            self.global_variables = current_globs
            self.memory_indexes = current_mems

        else:
            # All is fine, so make the change!
            logging.debug("Making change to memory!")
            self.global_variables = global_vars
            self.memory_indexes = mem_indexes
            self.next_free_memory_index

    def optimize_memory_allocations(self, parse_tree):
        """
        Performs the optimizations of memory allocations.
        :return:
        """
        occurences = self.count_occurences(parse_tree=parse_tree)
        self.rearrange_allocations(occurences=occurences)