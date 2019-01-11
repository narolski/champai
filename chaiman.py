# chaiman.py
from scope.chaivars import *
from scope.chaiflow import *

class ChaiMan:
    """
    Interprets the generated parse tree and manages code's translation.
    """

    def __init__(self, parse_tree):
        self.parse_tree = parse_tree

        self.global_variables = {}
        self.memory_indexes = {}

        self.assembly_code = []
        self.program_counter = 0

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
