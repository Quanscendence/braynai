# https://tomassetti.me/antlr-mega-tutorial/
import sys
from abcLexer import abcLexer
from abcParser import abcParser
from abc_lang_visitor import AbcLangVisitor
from antlr4 import *

def main():
    filepath  = 'test_file.mylang'
    input     = FileStream(filepath)
    lexer     = abcLexer(input)
    stream    = CommonTokenStream(lexer)
    parser    = abcParser(stream)
    tree      = parser.prog()

    visitor   = AbcLangVisitor()
    return visitor.visit(tree)

if __name__ == '__main__':
    main()


# conversation with vishwa sep-2-2019
#
# You9:07 PM
# function(column_name, value)
# function == and, or, not, user_defined
# You9:09 PM
# and(  greater_than_or_equal_to(attr1, 6), lesser_than_or_equal_to(attr3, 5) )
# or (  greater_than_or_equal_to(attr1, 6), lesser_than_or_equal_to(attr3, 5) )
# and(  greater_than_or_equal_to(attr1, 6), lesser_than_or_equal_to(attr3, 5) )
#
# ==>
#
# attr1 >= 6 && attr3 <= 5
# You9:11 PM
# and, or, not
# You9:12 PM
# max(`attr4`, 7)
# You9:13 PM
# def and_or(list_of_functions[], condition=and)
# def internal_function(column, value, operation)
# You9:14 PM
# def internal_function(column, value, operation = '==')
