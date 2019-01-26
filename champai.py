# champai.py
import argparse

from chailex import ChaiLex
from chaiparse import ChaiParse
from chaistat import ChaiStat


def parse_arguments():
    """
    Parses the arguments given by the user.
    :return: parsed arguments from stdin
    """
    parser = argparse.ArgumentParser(description='Champai GLang Compiler')

    parser.add_argument(
        'filepath',
        help='.imp file containing code in GLang'
        )

    parser.add_argument(
        '--out',
        default="a.o",
        help='output file containing compiled code'
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

    try:
        tree = parser.parse(lexer.tokenize(code))
        manager = ChaiStat(parse_tree=tree, global_variables=parser.global_variables, memory_indexes=parser.memory_indexes,
                       next_free_memory_index=parser.next_free_memory_index)

        assembly_code = manager.compile()
    except Exception as e:
        print(e)
        exit(1)

    with open(output_file, 'w') as file:
            file.write(assembly_code)


if __name__ == "__main__":
    main()