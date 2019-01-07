# champai.py

from chailexer import ChaiLexer
from chaiparser import ChaiParser
from chaimaker import ChaiMaker

lexer = ChaiLexer()
parser = ChaiParser()

file = open('tests/program4.imp', 'r').read()

tree = parser.parse(lexer.tokenize(file))

maker = ChaiMaker(parse_tree=tree)
maker.make()


