# Copyright 2019 Geneea Analytics s.r.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Except the fromDict function, all functions and classes defined in this file are only internal helpers.
#
# Conventions:
#  - variables prefixed with 'raw' refer to dictionaries based on the json objects returned by the API


import re
import warnings
from typing import Any, Iterable, List, Optional

from geneeanlpclient.common import ud
from geneeanlpclient.common.dictutil import JsonType, getValue
from geneeanlpclient.g3.model import (Analysis, CharSpan, Language, Sentiment, Paragraph, Sentence, Relation, Entity, Tag,
    TectoToken, Token, TreeBuilder, Tree, TokenSupport, Vector, Node)

STD_KEYS = frozenset([
    'id', 'language', 'paragraphs',
    'entities', 'tags', 'relations',
    'docSentiment', 'itemSentiments', 'docVectors', 'itemVectors',
    'usedChars', 'metadata', 'debugInfo', 'version'
])
""" Standard keys used in G3 analysis JSON """


def fromDict(rawAnalysis: JsonType) -> Analysis:
    """
    Reads the Analysis object from a JSON-based dictionary as returned from Geneea G3 API.
    """
    return _Reader().fromDict(rawAnalysis)


class _Reader:

    def __init__(self) -> None:
        self.registry = dict()
        self.version = (3, 2, 0)

    @property
    def versionMajor(self) -> int:
        return self.version[0]

    @property
    def versionMinor(self) -> int:
        return self.version[1]

    @property
    def versionFix(self) -> int:
        return self.version[2]

    def _register(self, obj: Any) -> None:
        self.registry[obj._id] = obj

    def _registerAll(self, objs: Optional[Iterable[Any]]) -> None:
        if objs:
            for obj in objs:
                self._register(obj)

    def resolveId(self, id: str) -> Optional[Any]:
        if id is None:
            return None
        if id not in self.registry:
            raise ValueError(f'Unknown object ID used as a reference: "{id}"')
        return self.registry.get(id)

    def resolveIds(self, ids: Iterable[str]) -> List[Any]:
        return list(filter(None, map(self.resolveId, ids)))

    def _readVersion(self, rawAnalysis: JsonType) -> None:
        version = rawAnalysis.get('version', '3.0.0')
        verMatch = re.fullmatch(r'^([0-9]+)\.([0-9]+)\.([0-9]+)$', version)
        if not verMatch:
            raise ValueError(f'unsupported API version "{version}"')
        verMajor, verMinor, verFix = tuple(map(int, verMatch.groups()))
        if verMajor != 3 or verMinor > 2:
            raise ValueError(f'unsupported API version "{version}", major ver.num != 3 or minor ver.num > 2')
        self.version = verMajor, verMinor, verFix

    def _readSentiment(self, rawSentiment: JsonType) -> Sentiment:
        return Sentiment(
            mean=rawSentiment['mean'],
            label=rawSentiment['label'],
            positive=rawSentiment['positive'],
            negative=rawSentiment['negative'],
        )

    def _readVectors(self, rawVectors: List[JsonType]) -> List[Vector]:
        return [Vector(
            name=vec['mean'],
            version=vec['version'],
            values=vec['values'],
        ) for vec in rawVectors]

    def _readToken(self, rawToken: JsonType, *, tokenIdx: int) -> Token:
        useOrigTextField = self.versionMinor > 1
        text = rawToken['text'] if useOrigTextField else rawToken['corrText']
        off = rawToken['off'] if useOrigTextField else rawToken['corrOff']
        origText = rawToken.get('origText') if useOrigTextField else rawToken['text']
        origOff = rawToken.get('origOff') if useOrigTextField else rawToken['off']

        if (origText is not None and origText != text) or (origOff is not None and origOff != off):
            origCharSpan = CharSpan.withLen(
                origOff if origOff is not None else off,
                len(origText if origText is not None else text)
            )
        else:
            origCharSpan = None

        posStr = rawToken.get('pos')
        fncStr = rawToken.get('fnc')
        if fncStr:
            # legacy non-UD function 'clause'
            if fncStr.upper() == 'CLAUSE':
                fnc = ud.UDep.ROOT
            else:
                fnc = ud.UDep.fromStr(fncStr)
        else:
            fnc = None

        tok = Token(
            id=rawToken['id'],
            idx=tokenIdx,  # sentence based index
            text=text,
            charSpan=CharSpan.withLen(off, len(text)),
            origText=origText,
            origCharSpan=origCharSpan,
            deepLemma=rawToken.get('dLemma'),
            lemma=rawToken.get('lemma'),
            pos=ud.UPos.fromStr(posStr) if posStr else None,
            feats=rawToken.get('feats'),
            morphTag=rawToken.get('mTag'),
            fnc=fnc,
        )
        self._register(tok)
        return tok

    def _readTectoToken(self, raw: JsonType, *, tokenIdx: int) -> TectoToken:
        tokens = self.resolveIds(raw.get('tokenIds', []))
        tt = TectoToken(
            id=raw['id'],
            idx=tokenIdx,  # sentence based index
            lemma=raw.get('lemma'),
            feats=raw.get('feats'),
            fnc=raw.get('fnc', ud.UDep.DEP.toStr()),
            tokens=TokenSupport.of(tokens) if tokens else None,
            entityMention=raw.get('entityMentionId'),  # will be replaced by mention obj. later
            entity=None  # will be filled later
        )
        self._register(tt)
        return tt

    def _createTree(self, rawTokens: List[JsonType], tokens: List[Node]) -> Tree[Node]:
        tb = TreeBuilder[Node]()
        tb.addNodes(tokens)

        for rawToken in rawTokens:
            if 'parId' in rawToken:
                parent = self.resolveId(rawToken['parId'])
                child = self.resolveId(rawToken['id'])
                tb.addDependency(childIdx=child.idx, parentIdx=parent.idx)

        return tb.build()

    def _readSentence(self, rawSentence: JsonType) -> Sentence:
        rawTokens = rawSentence.get('tokens', [])
        tokens = [self._readToken(raw, tokenIdx=idx) for idx, raw in enumerate(rawTokens)]

        rawTectoTokens = rawSentence.get('tecto', [])
        tectoTokens = [self._readTectoToken(raw, tokenIdx=idx) for idx, raw in enumerate(rawTectoTokens)]

        if tokens[0].fnc:
            tree = self._createTree(rawTokens=rawTokens, tokens=tokens)
            tectoTree = self._createTree(rawTokens=rawTectoTokens, tokens=tectoTokens)
        else:
            tree = tectoTree = None

        sentence = Sentence(
            id=rawSentence['id'],
            root=tree.root if tree else None,
            tokens=tokens,
            tectoRoot=tectoTree.root if tectoTree else None,
            tectoTokens=tectoTokens
        )
        for t in sentence.tokens:
            t.sentence = sentence
        for tt in sentence.tectoTokens:
            tt.sentence = sentence

        self._register(sentence)
        return sentence

    def _readParagraph(self, rawPara: JsonType) -> Paragraph:
        useOrigTextField = self.versionMinor > 1
        para = Paragraph(
            id=rawPara['id'],
            type=rawPara['type'],
            text=rawPara['text'] if useOrigTextField else rawPara['corrText'],
            origText=rawPara.get('origText') if useOrigTextField else rawPara['text'],
            sentences=[self._readSentence(rawS) for rawS in rawPara['sentences']],
        )
        for s in para.sentences:
            s.paragraph = para
        self._register(para)
        return para

    def _readEntityMention(self, raw: JsonType) -> Entity.Mention:
        return Entity.Mention(
            id=raw['id'],
            mwl=raw['mwl'],
            text=raw['text'],
            tokens=TokenSupport.of(self.resolveIds(raw.get('tokenIds', []))),
            derivedFrom=raw.get('derivedFromEntityId'),  # will be replaced by entity obj. later
            feats=raw.get('feats'),
        )

    def _readEntity(self, raw: JsonType) -> Entity:
        ent = Entity(
            id=raw['id'],
            gkbId=raw.get('gkbId'),
            stdForm=raw['stdForm'],
            type=raw['type'],
            feats=raw.get('feats'),
            mentions=[self._readEntityMention(rm) for rm in raw.get('mentions', [])],
        )
        for m in ent.mentions:
            m.mentionOf = ent
        self._register(ent)
        self._registerAll(ent.mentions)
        return ent

    def _readTagMention(self, raw: JsonType) -> Tag.Mention:
        return Tag.Mention(
            id=raw['id'],
            tokens=TokenSupport.of(self.resolveIds(raw.get('tokenIds', []))),
            feats=raw.get('feats'),
        )

    def _readTag(self, raw: JsonType) -> Tag:
        tag = Tag(
            id=raw['id'],
            gkbId=raw.get('gkbId'),
            stdForm=raw['stdForm'],
            type=raw['type'],
            relevance=raw['relevance'],
            feats=raw.get('feats'),
            mentions=[self._readTagMention(rm) for rm in raw.get('mentions', [])],
        )
        for m in tag.mentions:
            m.mentionOf = tag
        self._register(tag)
        self._registerAll(tag.mentions)
        return tag

    def _readRelationArg(self, raw: JsonType) -> Relation.Argument:
        return Relation.Argument(
            name=raw['name'],
            type=raw['type'],
            entity=self.resolveId(raw.get('entityId')),
        )

    def _readRelationSupport(self, raw: JsonType) -> Relation.Support:
        return Relation.Support(
            tokens=TokenSupport.of(self.resolveIds(raw.get('tokenIds', []))),
            tectoToken=self.resolveId(raw.get('tectoId')),
        )

    def _readRelation(self, raw: JsonType) -> Relation:
        rel = Relation(
            id=raw['id'],
            textRepr=raw['textRepr'],
            name=raw['name'],
            type=raw['type'],
            args=[self._readRelationArg(ra) for ra in raw.get('args', [])],
            feats=raw.get('feats'),
            support=[self._readRelationSupport(rs) for rs in raw.get('support', [])],
        )
        self._register(rel)
        return rel

    def fromDict(self, rawAnalysis: JsonType) -> Analysis:
        """
        :param rawAnalysis: dictionary corresponding to a G3 API JSON
        :return Analysis object encapsulating the NLP analysis

        Note: depending on requested set of analyses and language support many of the keys can be missing
        """
        self._readVersion(rawAnalysis)
        useTopLevelMetadata = self.versionMinor < 2 and self.versionFix < 1

        metadata = rawAnalysis.get('metadata')

        unknownKeys = sorted(rawAnalysis.keys() - STD_KEYS)
        if unknownKeys:
            if useTopLevelMetadata and metadata is None:
                metadata = {key: rawAnalysis[key] for key in unknownKeys}
            else:
                warnings.warn(f'unrecognized fields in the analysis dict: {unknownKeys}')

        paragraphs = [self._readParagraph(raw) for raw in rawAnalysis.get('paragraphs', [])]
        entities = [self._readEntity(raw) for raw in rawAnalysis.get('entities', [])]
        tags = [self._readTag(raw) for raw in rawAnalysis.get('tags', [])]
        relations = [self._readRelation(raw) for raw in rawAnalysis.get('relations', [])]

        docSentiment = self._readSentiment(rawAnalysis['docSentiment']) if 'docSentiment' in rawAnalysis else None
        docVectors = self._readVectors(rawAnalysis['docVectors']) if 'docVectors' in rawAnalysis else None

        analysis = Analysis(
            docId=rawAnalysis.get('id'),
            language=Language(
                detected=getValue(rawAnalysis, 'language.detected', 'und')  # ISO 639-2 for Undetermined lg
            ),
            paragraphs=paragraphs,
            entities=entities,
            tags=tags,
            relations=relations,
            docSentiment=docSentiment,
            docVectors=docVectors,
            usedChars=rawAnalysis.get('usedChars'),
            metadata=metadata,
            debugInfo=rawAnalysis.get('debugInfo'),
        )

        for p in analysis.paragraphs:
            p.container = analysis

        # fill derived-from entities for mentions
        for e in analysis.entities:
            for m in e.mentions:
                m.derivedFrom = self.resolveId(m.derivedFrom)

        # fill tecto token entity mention
        for tt in analysis.tectoTokens:
            tt.entityMention = self.resolveId(tt.entityMention)
            tt.entity = tt.entityMention.mentionOf if tt.entityMention else None

        # fill items with their sentiment
        id2sentiment = {k: self._readSentiment(v) for k, v in rawAnalysis.get('itemSentiments', {}).items()}
        for id, sentiment in id2sentiment.items():
            self.resolveId(id).sentiment = sentiment

        # fill items with their vectors
        id2vectors = {k: self._readVectors(v) for k, v in rawAnalysis.get('itemVectors', {}).items()}
        for id, vectors in id2vectors.items():
            self.resolveId(id).vectors = vectors

        return analysis
