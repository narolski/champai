# chailexer.py
from sly import Lexer


class ChaiLexer(Lexer):
    """
    Defines the lexer for the Champai compiler.
    """

    # Defines tokens used by lexer
    tokens = {
        DECLARE, IN,

        THEN, ELSE, ENDIF, IF,
        WHILE, ENDWHILE, ENDDO,
        FROM, DOWNTO, TO, ENDFOR, FOR,

        READ, WRITE,
        LPAREN, RPAREN,
        SEMICOLON, COLON,

        PIDENTIFIER, NUMBER,

        PLUS, MINUS, TIMES, DIVIDE, MODULO,
        EQUALS, NOT_EQUALS, LESSER_THAN, GREATER_THAN,
        LESSER_EQUALS, GREATER_EQUALS,
        ASSIGN, DO, END
    }

    DECLARE = r'DECLARE'
    IN = r'IN'

    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDIF = r'ENDIF'

    DO = r'DO'
    WHILE = r'WHILE'
    ENDWHILE = r'ENDWHILE'
    ENDDO = r'ENDDO'

    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    DOWNTO = r'DOWNTO'
    ENDFOR = r'ENDFOR'

    READ = r'READ'
    WRITE = r'WRITE'

    ASSIGN = r':='
    SEMICOLON = r';'
    COLON = r':'

    PIDENTIFIER = r'[_a-z]+'
    NUMBER = r'\d+'

    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    MODULO = r'%'

    LESSER_EQUALS = r'<='
    GREATER_EQUALS = r'>='
    EQUALS = r'='
    NOT_EQUALS = r'!='
    LESSER_THAN = r'<'
    GREATER_THAN = r'>'

    LPAREN = r'\('
    RPAREN = r'\)'

    END = r'END'

    # Ignore rules
    ignore = ' \t\r'
    ignore_comment = r'\[[^\]]*\]'

    # Tracks line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # Implements error handling
    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1
