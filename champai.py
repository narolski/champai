# champai.py
import argparse

from chailex import ChaiLex
from chaiparse import ChaiParse
from chaistat import ChaiStat
from chaispeed import ChaiSpeed


def parse_arguments():
    """
    Parses the arguments given by the user.
    :return: parsed arguments from stdin
    """
    parser = argparse.ArgumentParser(description='Champai GLang Compiler')

    parser.add_argument(
        'input_file',
        help='.imp file containing code in GLang'
    )

    parser.add_argument(
        '--out',
        default="a.o",
        help='output the result of compilation to file'
    )

    return parser.parse_args()


def perform_compilation(input_file, output_file):
    """
    Performs the compilation of given input file.
    :return:
    """
    lexer = ChaiLex()
    parser = ChaiParse()

    with open(input_file, 'r') as file:
        code = file.read()

    # try:
    tree = parser.parse(lexer.tokenize(code))

    optimizer = ChaiSpeed(global_variables=parser.global_variables,
                          memory_indexes=parser.memory_indexes, next_free_memory_index=parser.next_free_memory_index)

    optimizer.optimize_memory_allocations(parse_tree=tree[1])

    manager = ChaiStat(parse_tree=tree, global_variables=optimizer.global_variables,
                       memory_indexes=optimizer.memory_indexes,
                       next_free_memory_index=optimizer.next_free_memory_index)

    assembly_code = manager.compile()

    with open(output_file, 'w') as file:
        file.write(assembly_code)
    # except Exception as e:
    #     print(e)
    #     exit(1)

def main():
    arguments = parse_arguments()
    perform_compilation(arguments.input_file, arguments.out)

if __name__ == "__main__":
    main()
