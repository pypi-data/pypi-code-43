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


# Except the fromDict/toDict functions, all functions and classes defined in this file are only internal helpers.
#
# Conventions:
#  - all reader methods start with `create`, `extract`, or `from`
#  - all writer methods start with `to`
#  - variables prefixed with 'raw' refer to dictionaries based on the json objects returned by the API


import collections
from typing import List, Dict, NamedTuple, Mapping, Tuple, Optional

from geneeanlpclient.common import ud
from geneeanlpclient.common.common import toFloat
from geneeanlpclient.common.dictutil import JsonType, getValue
from geneeanlpclient.g3.model import (Token, Entity, TectoToken, Sentence, Analysis, Sentiment,
    Paragraph, Tag, Relation, CharSpan, TokenSupport, Language, Tree, TreeBuilder)


def fromF2Dict(rawAnalysis: JsonType) -> Analysis:
    """ Reads the legacy F2 object (Full Analysis V2) to a corresponding Analysis object. """
    return _F2Reader().fromDict(rawAnalysis)


def toF2Dict(obj: Analysis) -> JsonType:
    """ Converts the Analysis object into a corresponding legacy F2 object (Full Analysis V2). """
    return _F2Writer().toDict(obj)


F2_KEYS = frozenset([
    'version', 'id', 'debugInfo',
    'language', 'title', 'lead', 'text', 'titleLemmas', 'leadLemmas', 'textLemmas',
    'tectoSentences', 'entities', 'keywords', 'hashtags', 'relations', 'sentiment', 'topic'
])
""" Standard keys used in F2 analysis JSON """


class _ProtoSentence(NamedTuple):
    """ An intermediary structure, just like sentence, but with tecto still being a dictionary + index mapping """
    tree: Tree[Token]
    sentiment: Sentiment

    rawTecto: List[Dict]
    """ raw dict with the tecto tokens """
    pIdx2token: Mapping[int, Token]
    """ paragraph token index to token """


class _TokenInfo(NamedTuple):
    segm2pIdx2token: Mapping[str, Mapping[int, Token]]
    """ Mapping (segment,paragraph-index) -> Token; used to resolve token indices in entities, tecto-tree, etc. """
    title: List[_ProtoSentence]
    lead: List[_ProtoSentence]
    text: List[_ProtoSentence]


class _F2Reader:
    _SEGMENT_TO_PARA = {
        'title': Paragraph.TYPE_TITLE,
        'lead': Paragraph.TYPE_ABSTRACT,
        'text': Paragraph.TYPE_BODY,
    }

    def __init__(self) -> None:
        self.registry = collections.Counter()

    def _getId(self, prefix: str) -> str:
        self.registry.update(prefix)

        return f'{prefix}{self.registry[prefix]}'

    def _createTree(self, rawSentence: List[Dict], paraText: str) -> Tuple[Tree[Token], Mapping[int, Token]]:
        tb = TreeBuilder[Token]()
        pIdx2token: Dict[int, Token] = {}

        firstTokenIdx = rawSentence[0]['idx']  # paragraph index

        for rawToken in rawSentence:
            token = self._createToken(rawToken, firstTokenIdx=firstTokenIdx, paraText=paraText)
            tb.addNode(token)
            pIdx2token[rawToken['idx']] = token

        if 'par' in rawSentence[0]:
            # syntax structure is there
            for rawToken in rawSentence:
                if rawToken['par'] != -1:
                    parent = pIdx2token.get(rawToken['par'])
                    child = pIdx2token.get(rawToken['idx'])
                    tb.addDependency(childIdx=child.idx, parentIdx=parent.idx)

        else:
            # syntax structure is missing
            tb.addDummyDependecies()

        return tb.build(), pIdx2token

    def _createToken(self, rawToken: Dict, firstTokenIdx: int, paraText: str) -> Token:
        """ transform raw token to tokens object; """
        feats = rawToken.get('ftrs', {})

        lemmaInfo = rawToken.get('inf')
        if lemmaInfo:
            feats[Token.FEAT_LEMMA_INFO] = lemmaInfo

        lemmaSrc = rawToken.get('src')
        if lemmaSrc == 'UNKNOWN_WORD':
            feats[Token.FEAT_UNKNOWN] = 'true'

        charSpan = CharSpan.withLen(rawToken['off'], rawToken['len'])
        tokenText = charSpan.extractText(paraText)
        morphTag = rawToken.get('tag')
        lemma = rawToken['val']

        paraIdx = rawToken['idx']
        sIdx = paraIdx - firstTokenIdx

        fncStr = rawToken.get('fun')
        if fncStr:
            # legacy non-UD function 'clause'
            if fncStr.upper() == 'CLAUSE':
                fnc = ud.UDep.ROOT
            else:
                fnc = ud.UDep.fromStr(fncStr)
        else:
            fnc = None

        return Token(
            id=self._getId('w'),
            text=tokenText,
            idx=sIdx,  # sentence based index
            charSpan=charSpan,
            deepLemma=lemma,
            lemma=None,  # F2 does not support the simple lemma
            morphTag=morphTag,
            pos=None,  # F2 does not support the Universal tagset
            feats=feats,
            fnc=fnc
        )

    def _create_ProtoSentence(
                self, rawSentence: List[Dict], rawTectoSentence: Dict, sentiment: Optional[float], paraText: str
    ) -> _ProtoSentence:
        tree, pIdx2token = self._createTree(rawSentence, paraText=paraText)

        return _ProtoSentence(
            tree=tree,
            rawTecto=rawTectoSentence['tokens'],
            sentiment=self._sentiment({'value': sentiment}) if (sentiment is not None) else None,
            pIdx2token=pIdx2token
        )

    def _createSegment_ProtoSentences(
                self, rawSentences: List[List[Dict]], rawTectoSentences: List[Dict], sentiments: List[float], paraText: str
    ) -> List[_ProtoSentence]:
        return [
            self._create_ProtoSentence(rawS, rawTectoS, sentiment, paraText)
            for rawS, rawTectoS, sentiment in zip(rawSentences, rawTectoSentences, sentiments)
        ]

    def _extractTokenInfo(self, rawAnalysis: Dict) -> _TokenInfo:
        titleLemmas = rawAnalysis.get('titleLemmas', [])
        leadLemmas = rawAnalysis.get('leadLemmas', [])
        textLemmas = rawAnalysis.get('textLemmas', [])
        titleText = rawAnalysis.get('title', '')
        leadText = rawAnalysis.get('lead', '')
        textText = rawAnalysis.get('text', '')

        sentenceCount = len(titleLemmas) + len(leadLemmas) + len(textLemmas)

        # tectoSentences might be missing
        tectoSentences = rawAnalysis.get('tectoSentences', [])
        if not tectoSentences:  # missing or empty
            tectoSentences = [{'tokens': []}] * sentenceCount
        if sentenceCount != len(tectoSentences):
            raise ValueError('Sentences/tectoSentences length mismatch')

        # sentiment might be missing
        sentenceSentiments = rawAnalysis.get('sentiment', {}).get('sentenceVals', [None] * sentenceCount)
        if sentenceCount != len(sentenceSentiments):
            raise ValueError('Sentences/sentiment length mismatch')

        leadStart = len(titleLemmas)
        textStart = leadStart + len(leadLemmas)

        titleTectoSentences = tectoSentences[:leadStart]
        leadTectoSentences = tectoSentences[leadStart:textStart]
        textTectoSentences = tectoSentences[textStart:]

        titleSentenceSentiment = sentenceSentiments[:leadStart]
        leadSentenceSentiment = sentenceSentiments[leadStart:textStart]
        textSentenceSentiment = sentenceSentiments[textStart:]

        titleSentences = self._createSegment_ProtoSentences(titleLemmas, titleTectoSentences, titleSentenceSentiment, titleText)
        leadSentences = self._createSegment_ProtoSentences(leadLemmas, leadTectoSentences, leadSentenceSentiment, leadText)
        textSentences = self._createSegment_ProtoSentences(textLemmas, textTectoSentences, textSentenceSentiment, textText)

        segm2pIdx2token = {
            'title': {pIdx: t for sent in titleSentences for pIdx, t in sent.pIdx2token.items()},
            'lead': {pIdx: t for sent in leadSentences for pIdx, t in sent.pIdx2token.items()},
            'text': {pIdx: t for sent in textSentences for pIdx, t in sent.pIdx2token.items()},
        }

        return _TokenInfo(
            segm2pIdx2token=segm2pIdx2token,
            title=titleSentences,
            lead=leadSentences,
            text=textSentences
        )

    @staticmethod
    def _createTokenSupport(rawMention: Dict, tokenInfo: _TokenInfo) -> TokenSupport:
        segment = rawMention['segment']
        tokenIdxs = rawMention['tokenIndices']

        tokens = [tokenInfo.segm2pIdx2token[segment][ti] for ti in tokenIdxs]

        return TokenSupport.of(tokens=tokens)

    def _createEntityMention(self, rawEntityInstance: Dict, tokenInfo: _TokenInfo) -> Entity.Mention:
        mwLemma = rawEntityInstance['mwLemma']
        assert isinstance(mwLemma, list)

        return Entity.Mention(
            id=self._getId('m'),
            text=rawEntityInstance['text'],
            mwl=' '.join(mwLemma),
            tokens=self._createTokenSupport(rawEntityInstance, tokenInfo),
            sentiment=self._sentiment({'value': rawEntityInstance['sentiment']}),
            feats=rawEntityInstance.get('feats'),
            derivedFrom=rawEntityInstance.get('derivedFromUid'),  # will be replaced by entity obj. later
        )

    def _createEntity(self, rawEntity: Dict, tokens: _TokenInfo) -> Entity:
        ent = Entity(
            id=self._getId('e'),
            gkbId=rawEntity.get('uid'),
            stdForm=rawEntity['standardForm'],
            type=rawEntity['type'],
            feats=rawEntity.get('links'),
            mentions=[self._createEntityMention(e, tokens) for e in rawEntity.get('instances', [])],
        )
        for m in ent.mentions:
            m.mentionOf = ent
        return ent

    def _createTagMention(self, rawTagMention: Dict, tokenInfo: _TokenInfo) -> Tag.Mention:
        return Tag.Mention(
            id=self._getId('m'),
            tokens=self._createTokenSupport(rawTagMention, tokenInfo),
            feats=rawTagMention.get('feats'),
        )

    def _createTag(self, rawTag: Dict, tokens: _TokenInfo) -> Tag:
        tag = Tag(
            id=self._getId('t'),
            gkbId=rawTag.get('uid'),
            stdForm=rawTag['value'],
            type=rawTag['type'],
            relevance=rawTag['weight'],
            feats=rawTag.get('feats'),
            mentions=[self._createTagMention(m, tokens) for m in rawTag.get('instances', [])],
        )
        for m in tag.mentions:
            m.mentionOf = tag
        return tag

    @staticmethod
    def _createArg(rawArg: Dict, entities: List[Entity]):
        entityIdx = rawArg.get('entityIdx', -1)
        return Relation.Argument(
            name=rawArg['name'],
            type=rawArg['type'],
            entity=entities[entityIdx] if entityIdx >= 0 else None,
        )

    def _createRelation(self, rawRelation: Dict, tectoTokens: List[TectoToken], entities: List[Entity]):
        # in older versions of FA, relations did not have a sentiment
        if 'sentiment' in rawRelation:
            sentiment = self._sentiment(rawRelation['sentiment'])
        else:
            sentiment = None

        feats = rawRelation.get('feats', {})
        modality = rawRelation.get('modality', '')
        if modality:
            feats['modality'] = modality
        negated = rawRelation.get('negated')
        if negated is not None:
            assert isinstance(negated, bool)
            feats['negated'] = str(negated).lower()

        tts = [tectoTokens[ti] for ti in rawRelation.get('tectoIndices', [])]

        name = rawRelation['name']
        args = [self._createArg(rawArg, entities) for rawArg in rawRelation['args']]
        argsStr = ', '.join(f'{a.type}: {a.name}' for a in args)
        modalityStr = f'{modality} ' if modality else ''
        negatedStr = '-not' if negated else ''
        textRepr = f'{modalityStr}{name}{negatedStr}({argsStr})'

        return Relation(
            id=self._getId('r'),
            name=name,
            textRepr=textRepr,
            type=rawRelation['type'],
            args=args,
            feats=feats,
            support=[Relation.Support(tokens=tt.tokens, tectoToken=tt) for tt in tts],
            sentiment=sentiment
        )

    def _createTectoTree(
                self, protoSentence: _ProtoSentence, segmentId: str, tokenInfo: _TokenInfo, entities: List[Entity]
    ) -> Tree[TectoToken]:
        tb = TreeBuilder[TectoToken]()

        if protoSentence.rawTecto:
            firstTokenIdx = min(t['index'] for t in protoSentence.rawTecto)

            for rawTectoToken in protoSentence.rawTecto:
                idx = rawTectoToken['index'] - firstTokenIdx
                tectoToken = self._createTectoToken(rawTectoToken, segmentId=segmentId, sIdx=idx, tokenInfo=tokenInfo, entities=entities)
                tb.addNode(tectoToken)

                if rawTectoToken['parentIndex'] != -1:
                    tb.addDependency(childIdx=idx, parentIdx=rawTectoToken['parentIndex'] - firstTokenIdx)

        # if there is no tecto structure, mimic surface syntax
        else:
            for t in protoSentence.tree.tokens:
                tt = TectoToken(
                    id=f'd{t.idx}',
                    idx=t.idx,
                    lemma=t.deepLemma,
                    feats=t.feats,
                    fnc=t.fnc.lower() if t.fnc else ud.UDep.DEP.toStr(),
                    tokens=TokenSupport.of([t]),
                    entity=None)
                tb.addNode(tt)
                if not t.isRoot:
                    tb.addDependency(t.idx, t.parent.idx)

        return tb.build()

    def _createTectoToken(
                self, rawTectoToken: Dict, segmentId: str, sIdx: int, tokenInfo: _TokenInfo, entities: List[Entity]
    ) -> TectoToken:
        feats = rawTectoToken.get('ftrs', {})

        # add non-G3 properties as private features
        if 'tag' in rawTectoToken:
            feats['__tag'] = rawTectoToken['tag']

        # resolve references to tokens
        tokens = TokenSupport.of([tokenInfo.segm2pIdx2token[segmentId][ti] for ti in rawTectoToken['tokenIndices']])

        # resolve references to entities (if any)
        if rawTectoToken['entityIdx'] is not None and rawTectoToken['entityIdx'] >= 0:
            entity = entities[rawTectoToken['entityIdx']]
        else:
            entity = None

        return TectoToken(
            id=self._getId('d'),
            idx=sIdx,
            lemma=rawTectoToken['dplemma'],
            feats=feats,
            fnc=rawTectoToken['function'].lower(),
            tokens=tokens,
            entity=entity
        )

    def _createSentence(self, protoSentence: _ProtoSentence, segmentId: str, tokenInfo: _TokenInfo, entities: List[Entity]) -> Sentence:
        tectoTree = self._createTectoTree(protoSentence, segmentId, tokenInfo, entities)

        sentence = Sentence(
            id=self._getId('s'),
            root=protoSentence.tree.root,
            tokens=protoSentence.tree.tokens,
            tectoRoot=tectoTree.root,
            tectoTokens=tectoTree.tokens,
            sentiment=protoSentence.sentiment
        )
        for t in sentence.tokens:
            t.sentence = sentence
        for t in sentence.tectoTokens:
            t.sentence = sentence

        return sentence

    def _createPara(
        self, segmentId: str, text: str,
        segment_ProtoSentences: List[_ProtoSentence],
        tokens: _TokenInfo,
        entities: List[Entity]
    ) -> Paragraph:
        para = Paragraph(
            id=self._getId('p'),
            type=_F2Reader._SEGMENT_TO_PARA[segmentId],
            text=text,
            sentences=[self._createSentence(s, segmentId, tokens, entities) for s in segment_ProtoSentences]
        )

        for s in para.sentences:
            s.paragraph = para

        return para

    def _topicTags(self, rawAnalysis: Dict) -> List[Tag]:
        tags = []
        rawTopic = rawAnalysis.get('topic', None)

        if rawTopic:
            tags.append(Tag(
                    id=self._getId('t'),
                    type=Tag.TYPE_TOPIC,
                    stdForm=rawTopic['value'],
                    relevance=rawTopic['weight'],
                    mentions=[],
            ))

            for rawTL in rawTopic['labelDistribution']:
                tags.append(Tag(
                    id=self._getId('t'),
                    type=Tag.TYPE_TOPIC_DISTRIBUTION,
                    stdForm=rawTL['value'],
                    relevance=rawTL['weight'],
                    mentions=[],
                ))

        return tags

    @staticmethod
    def _sentiment(raw: JsonType) -> Sentiment:
        val = toFloat(raw.get('value', raw.get('val')))
        label = raw.get('label')

        if not label:
            if val < -0.15:
                label = 'negative'
            elif val > 0.15:
                label = 'positive'
            else:
                label = 'neutral'

        positive = raw.get('positive', val if val > 0.0 else 0)
        negative = raw.get('negative', val if val < 0.0 else 0)

        return Sentiment(mean=val, label=label, positive=positive, negative=negative)

    def fromDict(self, rawAnalysis: JsonType) -> Analysis:
        """
        :param rawAnalysis: dictionary corresponding to full analysis JSON
        :return Analysis object encapsulating full NLP analysis
        """
        version = rawAnalysis.get('version', 'sandbox')
        if version != 'sandbox':
            raise ValueError(f'unsupported API version "{version}"')

        # Note: most keys can be missing when the dict contains Interpretor's output for an unsupported language
        if 'sentiment' in rawAnalysis:
            docSentiment = self._sentiment(rawAnalysis.get('sentiment'))
        else:
            docSentiment = None

        # extract tokens and entities so that they can be linked to
        tokenInfo = self._extractTokenInfo(rawAnalysis)

        entities = [self._createEntity(x, tokenInfo) for x in rawAnalysis.get('entities', [])]

        # fill derived-from entities for mentions
        gidToEnt = {e.gkbId: e for e in entities if e.gkbId}
        for e in entities:
            for m in e.mentions:
                m.derivedFrom = gidToEnt[m.derivedFrom] if m.derivedFrom in gidToEnt else None

        tags = [self._createTag(x, tokenInfo) for x in rawAnalysis.get('hashtags', [])]
        tags.extend(self._topicTags(rawAnalysis))

        # for now, paragraphs = segments
        paragraphs = [
            self._createPara('title', rawAnalysis.get('title', []), tokenInfo.title, tokenInfo, entities),
            self._createPara('lead', rawAnalysis.get('lead', []), tokenInfo.lead, tokenInfo, entities),
            self._createPara('text', rawAnalysis.get('text', []), tokenInfo.text, tokenInfo, entities)
        ]

        tectoTokens = [t for p in paragraphs for s in p.sentences for t in s.tectoTokens]
        relations = [self._createRelation(x, tectoTokens, entities) for x in rawAnalysis.get('relations', [])]
        metadata = {k: v for k, v in rawAnalysis.items() if k not in F2_KEYS}

        analysis = Analysis(
            docId=rawAnalysis.get('id'),
            language=Language(
                detected=getValue(rawAnalysis, 'language.value', 'und')  # ISO 639-2 for Undetermined lg
            ),
            paragraphs=paragraphs,
            entities=entities,
            tags=tags,
            relations=relations,
            docSentiment=docSentiment,
            metadata=metadata if metadata else None,
            debugInfo=rawAnalysis.get('debugInfo')
        )

        for p in analysis.paragraphs:
            p.container = analysis

        return analysis

# ----------------------------------------------------------------------------------------------------------------------
# F2 json/dict writer
# ----------------------------------------------------------------------------------------------------------------------


class _F2Writer:

    _PARA_TO_SEGMENT = {
        Paragraph.TYPE_TITLE: 'title',
        Paragraph.TYPE_ABSTRACT: 'lead',
        Paragraph.TYPE_BODY: 'text',
    }

    def __init__(self) -> None:
        self.token2paraIdx: Mapping[Token, int] = {}
        self.entity2idx: Mapping[Entity, int] = {}
        self.tt2idx: Mapping[TectoToken, int] = {}

    def _toLemmaJson(self, token: Token) -> JsonType:
        rawToken = {
            'val': token.deepLemma or token.text,
            'idx': self.token2paraIdx.get(token),
            'off': token.charSpan.start,
            'len': len(token.charSpan),
        }

        if token.morphTag:
            rawToken['tag'] = token.morphTag

        if token.fnc:
            rawToken['fun'] = token.fnc.toStr()
            rawToken['par'] = self.token2paraIdx.get(token.parent) if token.parent else -1

        if token.isUnknown:
            rawToken['src'] = 'UNKNOWN_WORD'

        lemmaInfo = token.feats.get(Token.FEAT_LEMMA_INFO)
        if lemmaInfo:
            rawToken['inf'] = lemmaInfo

        return rawToken

    def _toLemmaSentenceJson(self, tokens: List[Token]) -> List[JsonType]:
        return [self._toLemmaJson(token) for token in tokens]

    def _toTectoTokenJson(self, tectoToken: TectoToken) -> JsonType:
        if tectoToken.entity is not None:
            entity = tectoToken.entity # when tectoToken was created by F2 reader
        elif tectoToken.entityMention is not None:
            entity = tectoToken.entityMention.mentionOf # when tectoToken was created by G3 reader
        else:
            entity = None

        tt = {
            'dplemma': tectoToken.lemma,
            'entityIdx': self.entity2idx.get(entity, -1),
            'ftrs': {k: tectoToken.feats[k] for k in tectoToken.feats.keys() - {'__tag'}},
            'function': tectoToken.fnc.upper() if tectoToken.fnc else '',
            'index': self.tt2idx[tectoToken],
            'parentIndex': self.tt2idx[tectoToken.parent] if tectoToken.parent else -1,
            'tag': tectoToken.feats.get('__tag', ''),
            'tokenIndices': [self.token2paraIdx.get(t) for t in tectoToken.tokens] if tectoToken.tokens else []
        }

        return tt

    def _toTectoSentenceJson(self, sentence: Sentence) -> JsonType:
        return {
            'segment': _F2Writer._PARA_TO_SEGMENT[sentence.paragraph.type],
            'tokens': [self._toTectoTokenJson(t) for t in sentence.tectoTokens]
        }

    def _toEntityJson(self, entity: Entity) -> JsonType:
        # weight is ignored because it is unsupported in F2
        instances = []
        for m in entity.mentions:
            ei = {
                'text': m.text,
                'mwLemma': m.mwl.split() if m.mwl else [],
                'offset': m.tokens.firstCharParaOffset,
                'segment': _F2Writer._PARA_TO_SEGMENT[m.sentence.paragraph.type],
                'tokenIndices': [self.token2paraIdx.get(t) for t in m.tokens],
                'sentiment': m.sentiment.mean if m.sentiment else 0
            }
            instances.append(ei)
            if m.derivedFrom and m.derivedFrom.gkbId:
                ei['derivedFromUid'] = m.derivedFrom.gkbId

        raw = {
            'standardForm': entity.stdForm,
            'type': entity.type,
            'links': entity.feats,
            'instances': instances
        }

        if entity.gkbId:
            raw['uid'] = entity.gkbId

        return raw

    def _toKwJson(self, entity: Entity) -> JsonType:
        return {
            'value': entity.stdForm,
            'type': entity.type,
            'instances': [{
                'text': ei.text,
                'offset': ei.tokens.firstCharParaOffset,
                'segment': _F2Writer._PARA_TO_SEGMENT[ei.sentence.paragraph.type],
                'tokenIndices': [self.token2paraIdx.get(t) for t in ei.tokens]
            } for ei in entity.mentions]

        }

    def _toTagJson(self, tag: Tag) -> JsonType:
        raw = {
            'value': tag.stdForm,
            'type': tag.type,
            'weight': tag.relevance,
            'instances': [{
                'offset': m.tokens.firstCharParaOffset,
                'segment': _F2Writer._PARA_TO_SEGMENT[m.sentence.paragraph.type],
                'tokenIndices': [self.token2paraIdx.get(t) for t in m.tokens]
            } for m in tag.mentions]
        }

        if tag.gkbId:
            raw['uid'] = tag.gkbId

        return raw

    @staticmethod
    def _topicFromTags(tags: List[Tag]) -> Optional[JsonType]:
        mainTopicTags = [tag for tag in tags if tag.type == Tag.TYPE_TOPIC]
        topicTags = [tag for tag in tags if tag.type == Tag.TYPE_TOPIC_DISTRIBUTION]

        if mainTopicTags:
            return {
                'value': mainTopicTags[0].stdForm,
                'weight': mainTopicTags[0].relevance,
                'labelDistribution': [{'value': t.stdForm, 'weight': t.relevance} for t in topicTags]
            }

    def _toRelationJson(self, relation: Relation) -> JsonType:
        support = [
            {
                'segment': _F2Writer._PARA_TO_SEGMENT[sup.tokens.sentence.paragraph.type],
                'tokenIndices': [self.token2paraIdx[t] for t in sup.tokens]
            }
            for sup in relation.support
        ]
        sentiment = relation.sentiment or Sentiment(0, 'neutral', 0, 0)

        return {
            'name': relation.name,
            'type': relation.type,
            'sentiment': {'val': sentiment.mean, 'neg': sentiment.negative, 'pos': sentiment.positive},
            'args': [{'entityIdx': self.entity2idx.get(a.entity, -1), 'name': a.name, 'type': a.type} for a in relation.args],
            'negated': relation.isNegated,
            'modality': relation.modality or '',
            'tectoIndices': [self.tt2idx[sup.tectoToken] for sup in relation.support if sup.tectoToken],
            'support': support
        }

    def toDict(self, obj: Analysis) -> JsonType:
        self.token2paraIdx = {token: idx for para in obj.paragraphs for idx, token in enumerate(para.tokens)}
        self.entity2idx = {entity: idx for idx, entity in enumerate(obj.entities)}
        self.tt2idx = {tt: idx for idx, tt in enumerate(obj.tectoTokens)}

        titlePara = obj.getParaByType(Paragraph.TYPE_TITLE)
        leadPara = obj.getParaByType(Paragraph.TYPE_ABSTRACT)
        textPara = obj.getParaByType(Paragraph.TYPE_BODY)

        titleSentences = titlePara.sentences if titlePara else []
        leadSentences = leadPara.sentences if leadPara else []
        textSentences = textPara.sentences if textPara else []

        raw = {
            'version': 'sandbox',
            'language': {'value': obj.language.detected},
            'title': titlePara.text if titlePara else "",
            'lead': leadPara.text if leadPara else "",
            'text': textPara.text if textPara else "",
            'titleLemmas': [self._toLemmaSentenceJson(s.tokens) for s in titleSentences],
            'leadLemmas': [self._toLemmaSentenceJson(s.tokens) for s in leadSentences],
            'textLemmas': [self._toLemmaSentenceJson(s.tokens) for s in textSentences],
            'tectoSentences': [self._toTectoSentenceJson(x) for x in obj.sentences],
            'entities': [self._toEntityJson(x) for x in obj.entities if x.type != 'keywords'],
            'keywords': [self._toKwJson(x) for x in obj.entities if x.type == 'keywords'],
            'hashtags': [self._toTagJson(x) for x in obj.tags if x.type not in [Tag.TYPE_TOPIC, Tag.TYPE_TOPIC_DISTRIBUTION]],
            'relations': [self._toRelationJson(x) for x in obj.relations],
        }

        if obj.docId:
            raw['id'] = obj.docId

        if obj.docSentiment:
            raw['sentiment'] = {
                'value': obj.docSentiment.mean,
                'label': obj.docSentiment.label,
                'sentenceVals': [s.sentiment.mean if s.sentiment else 0 for s in obj.sentences]
            }

        rawTopic = self._topicFromTags(obj.tags)
        if rawTopic:
            raw['topic'] = rawTopic

        if obj.debugInfo:
            raw['debugInfo'] = obj.debugInfo
        if obj.metadata:
            for k, v in obj.metadata.items():
                if k in raw:
                    raise ValueError(f'Metadata conflict: "{k}" is already present in the output F2 dictionary')
                raw[k] = v

        return raw
