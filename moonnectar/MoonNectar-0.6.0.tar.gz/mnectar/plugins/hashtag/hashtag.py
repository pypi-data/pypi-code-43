import logging
import tinydb

from lark import v_args

from mnectar.library.LarkSearchEngine import Grammar, transform
from mnectar.registry                 import Registry, Plugin
from mnectar.plugins.logic            import LogicQuery

import Registry.Library.SearchEngine.LogicEngineGrammar

_logger = logging.getLogger(__name__)

class HashtagLogicSearch(Grammar, registry=Registry.Library.SearchEngine.LogicEngineGrammar):
    _grammar = {
        "?column_expr":   ['hashtag_direct',],
        "hashtag_direct": ['"#" hashtag',
                           '"#"'],
        "hashtag":        ['/[A-Za-z0-9:_-]+/',],
    }

    hashtag = v_args(inline=True)(str)

    @v_args(inline=True)
    def hashtag_direct(self, hashtag = ""):
        if hashtag == "":
            return LogicQuery()['hashtag'].exists()
        else:
            return LogicQuery()['hashtag'].startswith(str(hashtag), ignorecase=True)

