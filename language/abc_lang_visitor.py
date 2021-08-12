from abcParser import abcParser
from abcVisitor import abcVisitor as AbcVisitorOriginal

# from grammar.build.abcParser import abcParser
# from grammar.build.abcVisitor import abcVisitor as AbcVisitorOriginal

class AbcLangVisitor(AbcVisitorOriginal):
    # ctx stands for context
    # Visit a parse tree produced by abcParser#prog.
    def visitProg(self, ctx:abcParser.ProgContext):
        return super().visitProg(ctx)


    # Visit a parse tree produced by abcParser#statements.
    def visitStatements(self, ctx:abcParser.StatementsContext):
        return super().visitStatements(ctx)


    # Visit a parse tree produced by abcParser#statement.
    def visitStatement(self, ctx:abcParser.StatementContext):
        result = None
        if (ctx.expr()):
            result = self.visitExpr(ctx.expr()) # ctx.expr(0) is not used as there is only one context
            print("Expression:", str(ctx.expr().getText()), "=", str(result))
        else:
            result = super().visitStatement(ctx) # the safety net
        return result

        # return super().visitStatement(ctx)


    # Visit a parse tree produced by abcParser#expr.
    def visitExpr(self, ctx:abcParser.ExprContext):
        if (ctx.NUM()):
            return int(ctx.NUM().getText())

        # if (ctx.MATH()):
        #     print(" String: ", str(ctx.MATH().getText()))
        #     exit()

        if (ctx.ADD()):
            return self.visitExpr(ctx.expr(0)) + self.visitExpr(ctx.expr(1)) # 0 stands for the first expression and the 1 stands for the second expression

        if (ctx.SUB()):
            return self.visitExpr(ctx.expr(0)) - self.visitExpr(ctx.expr(1)) # 0 stands for the first expression and the 1 stands for the second expression

        if (ctx.MUL()):
            return self.visitExpr(ctx.expr(0)) * self.visitExpr(ctx.expr(1)) # 0 stands for the first expression and the 1 stands for the second expression

        if (ctx.DIV()):
            return self.visitExpr(ctx.expr(0)) / self.visitExpr(ctx.expr(1)) # 0 stands for the first expression and the 1 stands for the second expression




        # return super().visitExpr(ctx)
