# chaiman.py
from chaiasm import ChaiAsm

from scope.chaivars import *
from scope.chaiflow import *

class ChaiMan:
    """
    Interprets the generated parse tree and manages code's translation.
    Also handles the memory management.
    """

    def __init__(self, parse_tree, global_variables, memory_indexes):
        self.parse_tree = parse_tree

        self.global_variables = global_variables
        self.memory_indexes = memory_indexes

        self.assembly_code = []
        self.program_counter = 0

    def get_memory_location(self, pidentifier):
        """
        Returns the location in memory of given pidentifier (variable)
        :param pidentifier: variable identifier
        :return: memory index
        """
        return self.memory_indexes[pidentifier]

    def get_object_memory_location(self, object):
        """
        Returns the location in memory of given object
        :param object: object
        :return: memory index
        """
        return self.memory_indexes[object.pidentifier]

    def get_object_from_memory(self, pidentifier):
        """
        Returns the object from memory
        :param pidentifier: object identifier
        :return: object
        """
        return self.global_variables[pidentifier]

    def manage(self):
        """
        Manages the translation
        :return:
        """
        pass

    def run(self):
        """
        Runs the code
        :return:
        """
        pass
