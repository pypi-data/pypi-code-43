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


# Except the toDict function, all functions and classes defined in this file are only internal helpers.


from typing import Dict, List

from geneeanlpclient.common.dictutil import JsonType, DictBuilder
from geneeanlpclient.g3.model import Analysis, Relation, Paragraph, Entity, Tag, Token, TectoToken, Sentence, Sentiment, Vector


def toDict(obj: Analysis) -> JsonType:
    """
    Writes the Analysis to a JSON-based dictionary to a format as returned by Geneea G3 API.
    """
    builder = DictBuilder({
        'version': '3.2.0',
        'language': {'detected': obj.language.detected},
    })
    builder.addIfNotNone('id', obj.docId)
    builder.addIfNotNone('paragraphs', [_toRawPara(p) for p in obj.paragraphs])
    builder.addIfNotNone('entities', [_toRawEntity(e) for e in obj.entities])
    builder.addIfNotNone('tags', [_toRawTag(t) for t in obj.tags])
    builder.addIfNotNone('relations', [_toRawRelation(r) for r in obj.relations])
    if obj.docSentiment:
        builder['docSentiment'] = _toRawSentiment(obj.docSentiment)
    if obj.docVectors:
        builder['docVectors'] = _toRawVectors(obj.docVectors)
    builder.addIfNotNone('itemSentiments', _toRawItemSentiment(obj))
    builder.addIfNotNone('itemVectors', _toRawItemVectors(obj))
    builder.addIfNotNone('usedChars', obj.usedChars)
    builder.addIfNotNone('metadata', obj.metadata)
    builder.addIfNotNone('debugInfo', obj.debugInfo)
    return builder.build()


def _toRawEntityMention(mention: Entity.Mention) -> JsonType:
    builder = DictBuilder({
        'text': mention.text,
        'mwl': mention.mwl,
    })
    builder.addId('id', mention)
    builder.addIds('tokenIds', mention.tokens)
    builder.addIfNotNone('feats', mention.feats)
    builder.addId('derivedFromEntityId', mention.derivedFrom)
    return builder.build()


def _toRawEntity(entity: Entity) -> JsonType:
    builder = DictBuilder({
        'stdForm': entity.stdForm,
        'type': entity.type,
    })
    builder.addId('id', entity)
    builder.addIfNotNone('gkbId', entity.gkbId)
    builder.addIfNotNone('feats', entity.feats)
    builder.addIfNotNone('mentions', [_toRawEntityMention(m) for m in entity.mentions])
    return builder.build()


def _toRawTagMention(mention: Tag.Mention) -> JsonType:
    builder = DictBuilder({})
    builder.addId('id', mention)
    builder.addIds('tokenIds', mention.tokens)
    builder.addIfNotNone('feats', mention.feats)
    return builder.build()


def _toRawTag(tag: Tag) -> JsonType:
    builder = DictBuilder({
        'stdForm': tag.stdForm,
        'type': tag.type,
        'relevance': tag.relevance,
    })
    builder.addId('id', tag)
    builder.addIfNotNone('gkbId', tag.gkbId)
    builder.addIfNotNone('feats', tag.feats)
    builder.addIfNotNone('mentions', [_toRawTagMention(m) for m in tag.mentions])
    return builder.build()


def _toRawArg(arg: Relation.Argument) -> JsonType:
    builder = DictBuilder({
        "name": arg.name,
        "type": arg.type,
    })
    builder.addId("entityId", arg.entity)
    return builder.build()


def _toRawRelationSupport(support: Relation.Support) -> JsonType:
    builder = DictBuilder({})
    builder.addIds('tokenIds', support.tokens)
    builder.addId('tectoId', support.tectoToken)
    return builder.build()


def _toRawRelation(relation: Relation) -> JsonType:
    builder = DictBuilder({
        'textRepr': relation.textRepr,
        'name': relation.name,
        'type': relation.type,
        'args': [_toRawArg(a) for a in relation.args],
    })
    builder.addId('id', relation)
    builder.addIfNotNone('feats', relation.feats)
    builder.addIfNotNone('support', [_toRawRelationSupport(s) for s in relation.support])
    return builder.build()


def _toRawSentiment(sentiment: Sentiment) -> JsonType:
    return {
        'mean': sentiment.mean,
        'label': sentiment.label,
        'positive': sentiment.positive,
        'negative': sentiment.negative,
    }


def _toRawVectors(vectors: List[Vector]) -> List[JsonType]:
    return [{
        'name': vec.name,
        'version': vec.version,
        'values': vec.values,
    } for vec in vectors]


def _toRawToken(t: Token) -> JsonType:
    builder = DictBuilder({
        'off': t.charSpan.start,
        'text': t.text,
    })
    builder.addId('id', t)
    if t.origCharSpan.start != t.charSpan.start:
        builder['origOff'] = t.origCharSpan.start
    if t.origText != t.text:
        builder['origText'] = t.origText
    builder.addIfNotNone('dLemma', t.deepLemma)
    builder.addIfNotNone('mTag', t.morphTag)
    builder.addIfNotNone('lemma', t.lemma)
    builder.addId('parId', t.parent)
    builder.addIfNotNone('feats', t.feats)
    if t.pos:
        builder['pos'] = t.pos.toStr()
    if t.fnc:
        builder['fnc'] = t.fnc.name.lower()
    return builder.build()


def _toRawTectoToken(tt: TectoToken) -> JsonType:
    builder = DictBuilder({
        'tokenIds': [t._id for t in tt.tokens] if tt.tokens else []
    })
    builder.addId('id', tt)
    builder.addIfNotNone('lemma', tt.lemma)
    builder.addIfNotNone('feats', tt.feats)
    if tt.fnc:
        builder['fnc'] = tt.fnc.lower()
    builder.addId('parId', tt.parent)
    builder.addId('entityMentionId', tt.entityMention)
    return builder.build()


def _toRawSentence(s: Sentence) -> JsonType:
    builder = DictBuilder({
        'tokens': [_toRawToken(t) for t in s.tokens],
    })
    builder.addId('id', s)
    if s.tectoTokens:
        builder['tecto'] = [_toRawTectoToken(tt) for tt in s.tectoTokens]
    return builder.build()


def _toRawPara(para: Paragraph) -> JsonType:
    builder = DictBuilder({
        'type': para.type,
        'text': para.text,
        'sentences': [_toRawSentence(s) for s in para.sentences],
    })
    builder.addId('id', para)
    if para.origText != para.text:
        builder['origText'] = para.origText
    return builder.build()


def _toRawItemSentiment(obj: Analysis) -> Dict[str, JsonType]:
    id2sentiment = dict()

    def putAll(items):
        for item in items:
            if item.sentiment:
                id2sentiment[item._id] = _toRawSentiment(item.sentiment)

    putAll(obj.paragraphs)
    for p in obj.paragraphs:
        putAll(p.sentences)

    putAll(obj.entities)
    for e in obj.entities:
        putAll(e.mentions)

    putAll(obj.tags)
    for t in obj.tags:
        putAll(t.mentions)

    putAll(obj.relations)

    return id2sentiment


def _toRawItemVectors(obj: Analysis) -> Dict[str, List[JsonType]]:
    id2vectors = dict()

    def putAll(items):
        for item in items:
            if item.vectors:
                id2vectors[item._id] = _toRawVectors(item.vectors)

    putAll(obj.paragraphs)
    for p in obj.paragraphs:
        putAll(p.sentences)

    putAll(obj.entities)
    for e in obj.entities:
        putAll(e.mentions)

    putAll(obj.tags)
    for t in obj.tags:
        putAll(t.mentions)

    putAll(obj.relations)

    return id2vectors
