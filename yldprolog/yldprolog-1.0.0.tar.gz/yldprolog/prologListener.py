# Generated from prolog.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .prologParser import prologParser
else:
    from prologParser import prologParser

# This class defines a complete listener for a parse tree produced by prologParser.
class prologListener(ParseTreeListener):

    # Enter a parse tree produced by prologParser#program.
    def enterProgram(self, ctx:prologParser.ProgramContext):
        pass

    # Exit a parse tree produced by prologParser#program.
    def exitProgram(self, ctx:prologParser.ProgramContext):
        pass


    # Enter a parse tree produced by prologParser#clauselist.
    def enterClauselist(self, ctx:prologParser.ClauselistContext):
        pass

    # Exit a parse tree produced by prologParser#clauselist.
    def exitClauselist(self, ctx:prologParser.ClauselistContext):
        pass


    # Enter a parse tree produced by prologParser#clause.
    def enterClause(self, ctx:prologParser.ClauseContext):
        pass

    # Exit a parse tree produced by prologParser#clause.
    def exitClause(self, ctx:prologParser.ClauseContext):
        pass


    # Enter a parse tree produced by prologParser#directive.
    def enterDirective(self, ctx:prologParser.DirectiveContext):
        pass

    # Exit a parse tree produced by prologParser#directive.
    def exitDirective(self, ctx:prologParser.DirectiveContext):
        pass


    # Enter a parse tree produced by prologParser#predicatelist.
    def enterPredicatelist(self, ctx:prologParser.PredicatelistContext):
        pass

    # Exit a parse tree produced by prologParser#predicatelist.
    def exitPredicatelist(self, ctx:prologParser.PredicatelistContext):
        pass


    # Enter a parse tree produced by prologParser#simplepredicate.
    def enterSimplepredicate(self, ctx:prologParser.SimplepredicateContext):
        pass

    # Exit a parse tree produced by prologParser#simplepredicate.
    def exitSimplepredicate(self, ctx:prologParser.SimplepredicateContext):
        pass


    # Enter a parse tree produced by prologParser#functor.
    def enterFunctor(self, ctx:prologParser.FunctorContext):
        pass

    # Exit a parse tree produced by prologParser#functor.
    def exitFunctor(self, ctx:prologParser.FunctorContext):
        pass


    # Enter a parse tree produced by prologParser#atom.
    def enterAtom(self, ctx:prologParser.AtomContext):
        pass

    # Exit a parse tree produced by prologParser#atom.
    def exitAtom(self, ctx:prologParser.AtomContext):
        pass


    # Enter a parse tree produced by prologParser#predicateterm.
    def enterPredicateterm(self, ctx:prologParser.PredicatetermContext):
        pass

    # Exit a parse tree produced by prologParser#predicateterm.
    def exitPredicateterm(self, ctx:prologParser.PredicatetermContext):
        pass


    # Enter a parse tree produced by prologParser#termlist.
    def enterTermlist(self, ctx:prologParser.TermlistContext):
        pass

    # Exit a parse tree produced by prologParser#termlist.
    def exitTermlist(self, ctx:prologParser.TermlistContext):
        pass


    # Enter a parse tree produced by prologParser#term.
    def enterTerm(self, ctx:prologParser.TermContext):
        pass

    # Exit a parse tree produced by prologParser#term.
    def exitTerm(self, ctx:prologParser.TermContext):
        pass


