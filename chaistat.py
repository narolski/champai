# chaistat.py
from chaiman import ChaiMan


class ChaiStat(ChaiMan):
    """
    Performs static analysis of code
    """

    def __init__(self, parse_tree):
        super().__init__(parse_tree)



    def assignment(self, to, value):
        """
        Handles the assignment of value to variable
        :return:
        """


