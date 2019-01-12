# champai.py

from chailexer import ChaiLexer
from chaiparser import ChaiParser
from chaistat import ChaiStat

lexer = ChaiLexer()
parser = ChaiParser()

file = open('tests/test1.imp', 'r').read()

tree = parser.parse(lexer.tokenize(file))

manager = ChaiStat(parse_tree=tree, global_variables=parser.global_variables, memory_indexes=parser.memory_indexes)
manager.manage()


