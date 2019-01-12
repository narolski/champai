from enum import Enum

class Registries(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'
    H = 'H'

    Constant = 'A'  # Holds memory index
    MemoryIndex = 'A'
    Value = 'H'     # Holds value of last loaded variable from memory

    ExpressionFirstOperand = 'B'   # a in a + b
    ExpressionSecondOperand = 'C'  # b in a + b
    ExpressionMulFirstOperand = 'B'
    ExpressionMulSecondOperand = 'C'

    ExpressionAddResult = 'B'
    ExpressionSubResult = 'B'
    ExpressionMulResult = 'D'
    ExpressionDivResult = 'D'
    ExpressionModResult = 'F'