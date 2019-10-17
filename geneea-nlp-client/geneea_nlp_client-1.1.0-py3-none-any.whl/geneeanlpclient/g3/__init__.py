from geneeanlpclient.g3.request import (
    Request,

    ParaSpec,
    AnalysisType,
    LanguageCode,
    Domain,
    TextType,
    Diacritization,
)

from geneeanlpclient.g3.model import (
    Analysis,

    Language,
    Entity,
    Tag,
    Relation,

    Paragraph,
    Sentence,
    Token,
    TokenSupport,
    TectoToken,
    CharSpan,

    Sentiment,
    Vector,
)

from geneeanlpclient.g3.reader import fromDict
from geneeanlpclient.g3.writer import toDict
from geneeanlpclient.g3.f2converter import fromF2Dict, toF2Dict

from geneeanlpclient.g3.client import Client

from geneeanlpclient.common.ud import UPos, UFeats, UDep
