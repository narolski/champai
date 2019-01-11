# chaiasm.py
from chaistat import ChaiStat


class ChaiAsm(ChaiStat):
    """
    Handles the translation into assembly code.
    """
    def __init__(self, parse_tree):
        super().__init__(parse_tree)


