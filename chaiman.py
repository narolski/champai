# chaiman.py
import logging

from scope.chaivars import *
from scope.chaiflow import *


class ChaiMan:

    def __init__(self, parse_tree, global_variables, memory_indexes, next_free_memory_index):
        self.parse_tree = parse_tree
        self.global_variables = global_variables
        self.memory_indexes = memory_indexes
        self.next_free_memory_index = next_free_memory_index

    def get_memory_location(self, pidentifier):
        """
        Returns the location in memory of given pidentifier (variable)
        :param pidentifier: variable identifier
        :return: memory index
        """
        return self.memory_indexes[pidentifier]

    def get_pidentifier_assigned_to_mem_index(self, index):
        """
        Returns the object assigned to given memory index
        :param index: memory index
        :return:
        """
        for var, mem_index in self.memory_indexes.items():
            if mem_index == index:
                return var

    def get_object_memory_location(self, object):
        """
        Returns the location in memory of given object
        :param object: object
        :return: memory index
        """
        # if self.get_variable_assigned_to_value(variable=object):
        return self.memory_indexes[object.pidentifier]
        # else:
        #     raise Exception("get_object_memory_location: object '{}' referenced before assignment".format(object))

    def get_object_from_memory(self, pidentifier):
        """
        Returns the object from memory
        :param pidentifier: object identifier
        :return: object
        """
        return self.global_variables[pidentifier]

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

    def set_variable_assigned_to_value(self, variable):
        """
        Sets status of variable assignment to value to TRUE.
        Used for later checks of variable reference before assignment
        :param variable: var which has been assigned value
        :return:
        """
        if variable.pidentifier in self.global_variables.keys():
            self.global_variables[variable.pidentifier].set_value_has_been_set()
        else:
            raise Exception("Assigning value to undeclared variable '{}'".format(variable.pidentifier))

    def get_variable_assigned_to_value(self, variable):
        """
        Returns the status of variable assignment to value.
        :param variable:
        :return:
        """
        return self.global_variables[variable.pidentifier].get_value_has_been_set_status()


