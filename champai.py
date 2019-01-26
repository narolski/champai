# champai.py

from chailexer import ChaiLexer
from chaiparser import ChaiParser
from chaistat import ChaiStat

lexer = ChaiLexer()
parser = ChaiParser()

filename = '9-sort'

file = open('tests/gebala/{}.imp'.format(filename), 'r').read()

tree = parser.parse(lexer.tokenize(file))

manager = ChaiStat(parse_tree=tree, global_variables=parser.global_variables, memory_indexes=parser.memory_indexes,
                   next_free_memory_index=parser.next_free_memory_index, filename=filename)
manager.manage()


