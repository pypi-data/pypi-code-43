# Generated from prolog.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .prologParser import prologParser
else:
    from prologParser import prologParser

# This class defines a complete generic visitor for a parse tree produced by prologParser.

class prologVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by prologParser#program.
    def visitProgram(self, ctx:prologParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#clauselist.
    def visitClauselist(self, ctx:prologParser.ClauselistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#clause.
    def visitClause(self, ctx:prologParser.ClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#directive.
    def visitDirective(self, ctx:prologParser.DirectiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#predicatelist.
    def visitPredicatelist(self, ctx:prologParser.PredicatelistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#simplepredicate.
    def visitSimplepredicate(self, ctx:prologParser.SimplepredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#functor.
    def visitFunctor(self, ctx:prologParser.FunctorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#atom.
    def visitAtom(self, ctx:prologParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#predicateterm.
    def visitPredicateterm(self, ctx:prologParser.PredicatetermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#termlist.
    def visitTermlist(self, ctx:prologParser.TermlistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by prologParser#term.
    def visitTerm(self, ctx:prologParser.TermContext):
        return self.visitChildren(ctx)



del prologParser