# chaivars.py


class Variable:
    """
    Defines common interface for variables
    """
    def __init__(self, pidentifier, lineno):
        self.pidentifier = pidentifier
        self.lineno = lineno
        self.value = None
        self.updated_after_compilation = True
        super().__init__()

    def set_updated_after_compilation(self):
        self.updated_after_compilation = True
        self.value = None


class Int(Variable):
    """
    Defines integer representation in Champai.
    """
    def __init__(self, pidentifier, lineno):
        self.is_iterator = True
        super().__init__(pidentifier=pidentifier, lineno=lineno)

    def __repr__(self):
        return str("[Integer {}, line {}]".format(self.pidentifier, self.lineno))


class IntArray(Variable):
    def __init__(self, pidentifier, lineno, from_val, to_val):
        self.from_val = int(from_val)
        self.to_val = int(to_val)

        if self.to_val >= self.from_val:
            self.offset = self.from_val
            self.length = self.to_val - self.from_val + 1 + 1 # because of storing offset
        else:
            raise Exception("Invalid array bounds: declared IntArray[{}:{}]".format(self.from_val, self.to_val))
        super().__init__(pidentifier, lineno)


class IntArrayElement(Variable):
    def __init__(self, array, value_holder, lineno):
        self.array = array
        self.value_holder = value_holder # int or variable
        self.updated_after_compilation = True
        super().__init__(array.pidentifier, lineno)




