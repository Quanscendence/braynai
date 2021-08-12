# Generated from .\abc.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .abcParser import abcParser
else:
    from abcParser import abcParser

# This class defines a complete generic visitor for a parse tree produced by abcParser.

class abcVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by abcParser#prog.
    def visitProg(self, ctx:abcParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by abcParser#statements.
    def visitStatements(self, ctx:abcParser.StatementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by abcParser#statement.
    def visitStatement(self, ctx:abcParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by abcParser#expr.
    def visitExpr(self, ctx:abcParser.ExprContext):
        return self.visitChildren(ctx)



del abcParser