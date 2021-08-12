# Generated from .\abc.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .abcParser import abcParser
else:
    from abcParser import abcParser

# This class defines a complete listener for a parse tree produced by abcParser.
class abcListener(ParseTreeListener):

    # Enter a parse tree produced by abcParser#prog.
    def enterProg(self, ctx:abcParser.ProgContext):
        pass

    # Exit a parse tree produced by abcParser#prog.
    def exitProg(self, ctx:abcParser.ProgContext):
        pass


    # Enter a parse tree produced by abcParser#statements.
    def enterStatements(self, ctx:abcParser.StatementsContext):
        pass

    # Exit a parse tree produced by abcParser#statements.
    def exitStatements(self, ctx:abcParser.StatementsContext):
        pass


    # Enter a parse tree produced by abcParser#statement.
    def enterStatement(self, ctx:abcParser.StatementContext):
        pass

    # Exit a parse tree produced by abcParser#statement.
    def exitStatement(self, ctx:abcParser.StatementContext):
        pass


    # Enter a parse tree produced by abcParser#expr.
    def enterExpr(self, ctx:abcParser.ExprContext):
        pass

    # Exit a parse tree produced by abcParser#expr.
    def exitExpr(self, ctx:abcParser.ExprContext):
        pass


