# Generated from ES.g4 by ANTLR 4.7.2
import json
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ESParser import ESParser
else:
    from ESParser import ESParser

# This class defines a complete listener for a parse tree produced by ESParser.
class ESListener(ParseTreeListener):
    # pila para llevar un control de quien es el padre del siguiente bool
    pile_ancestors = []
    # pila para ir guardando en memoria la query recontruida
    bools_pile = []
    # objeto para guardar en memoria todos los filtros que están dentro de una sentencia must, must_not o should
    sentence_reconstructed = []


    def reconstruct_filter(self, ctx):
        text = ctx.getText()
        return json.loads(text)

    # Enter a parse tree produced by ESParser#boolean.
    def enterBoolean(self, ctx:ESParser.BooleanContext):
        self.bools_pile.append({})

    # Exit a parse tree produced by ESParser#boolean.
    def exitBoolean(self, ctx:ESParser.BooleanContext):
        if len(self.bools_pile) > 1:
            bool_ancestor = self.pile_ancestors[len(self.pile_ancestors) - 1]
            new_bool_statement = self.bools_pile[len(self.bools_pile) - 1]

            self.bools_pile[len(self.bools_pile) - 2][bool_ancestor] = [{
                "bool": new_bool_statement
            }]
            self.bools_pile.pop(len(self.bools_pile) -1 )

    # Enter a parse tree produced by ESParser#boolfilter.
    def enterBoolfilter(self, ctx:ESParser.BoolfilterContext):
        pass

    # Exit a parse tree produced by ESParser#boolfilter.
    def exitBoolfilter(self, ctx:ESParser.BoolfilterContext):
        pass


    # Enter a parse tree produced by ESParser#mustnot.
    def enterMustnot(self, ctx:ESParser.MustnotContext):
        self.pile_ancestors.append('must_not')
        
    # Exit a parse tree produced by ESParser#mustnot.
    def exitMustnot(self, ctx:ESParser.MustnotContext):
        if len(self.sentence_reconstructed) > 0:
            self.bools_pile[len(self.bools_pile) - 1]['must_not'] = self.sentence_reconstructed   
        
        self.pile_ancestors.pop(len(self.pile_ancestors) - 1)
        self.sentence_reconstructed = []
    
    # Enter a parse tree produced by ESParser#should.
    def enterShould(self, ctx:ESParser.ShouldContext):
        self.pile_ancestors.append('should')

    # Exit a parse tree produced by ESParser#should.
    def exitShould(self, ctx:ESParser.ShouldContext):
        if len(self.sentence_reconstructed) > 0:
            self.bools_pile[len(self.bools_pile) - 1]['should'] = self.sentence_reconstructed
        
        self.pile_ancestors.pop(len(self.pile_ancestors) - 1)
        self.sentence_reconstructed = []

    # Enter a parse tree produced by ESParser#must.
    def enterMust(self, ctx:ESParser.MustContext):
        self.pile_ancestors.append('must')

    # Exit a parse tree produced by ESParser#must.
    def exitMust(self, ctx:ESParser.MustContext):
        if len(self.sentence_reconstructed) > 0:
            self.bools_pile[len(self.bools_pile) - 1]['must'] = self.sentence_reconstructed
        self.pile_ancestors.pop(len(self.pile_ancestors) - 1)
        self.sentence_reconstructed = []

    # Enter a parse tree produced by ESParser#filterrule.
    def enterFilterrule(self, ctx:ESParser.FilterruleContext):
        pass

    # Exit a parse tree produced by ESParser#filterrule.
    def exitFilterrule(self, ctx:ESParser.FilterruleContext):
        pass


    # Enter a parse tree produced by ESParser#matchfilter.
    def enterMatchfilter(self, ctx:ESParser.MatchfilterContext):
        pass

    # Exit a parse tree produced by ESParser#matchfilter.
    def exitMatchfilter(self, ctx:ESParser.MatchfilterContext):
        filter = self.reconstruct_filter(ctx)
        self.sentence_reconstructed.append(filter)


    # Enter a parse tree produced by ESParser#notexists.
    def enterNotexists(self, ctx:ESParser.NotexistsContext):
        pass

    # Exit a parse tree produced by ESParser#notexists.
    def exitNotexists(self, ctx:ESParser.NotexistsContext):
        filter = self.reconstruct_filter(ctx)
        self.sentence_reconstructed.append(filter)


    # Enter a parse tree produced by ESParser#exists.
    def enterExists(self, ctx:ESParser.ExistsContext):
        pass

    # Exit a parse tree produced by ESParser#exists.
    def exitExists(self, ctx:ESParser.ExistsContext):
        filter = self.reconstruct_filter(ctx)
        self.sentence_reconstructed.append(filter)


    # Enter a parse tree produced by ESParser#rangerule.
    def enterRangerule(self, ctx:ESParser.RangeruleContext):
        pass

    # Exit a parse tree produced by ESParser#rangerule.
    def exitRangerule(self, ctx:ESParser.RangeruleContext):
        filter = self.reconstruct_filter(ctx)
        self.sentence_reconstructed.append(filter)


    # Enter a parse tree produced by ESParser#term.
    def enterTerm(self, ctx:ESParser.TermContext):
        pass

    # Exit a parse tree produced by ESParser#term.
    def exitTerm(self, ctx:ESParser.TermContext):
        filter = self.reconstruct_filter(ctx)
        self.sentence_reconstructed.append(filter)


    # Enter a parse tree produced by ESParser#querystring.
    def enterQuerystring(self, ctx:ESParser.QuerystringContext):
        pass

    # Exit a parse tree produced by ESParser#querystring.
    def exitQuerystring(self, ctx:ESParser.QuerystringContext):
        text = ctx.getText()
        
        # ñapa meanwhile
        if "all_fields" in text and "true" in text:
            text = text.replace("all_fields", "default_field")
            text = text.replace("true", '"*"')

        self.sentence_reconstructed.append(json.loads(text))
