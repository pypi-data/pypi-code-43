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

import datetime
from enum import Enum
from operator import attrgetter
from typing import Iterable, NamedTuple, Mapping, List, Optional, Set, Union

from geneeanlpclient.common.common import objToStr, objRepr
from geneeanlpclient.common.dictutil import DictBuilder, JsonType
from geneeanlpclient.g3.model import Paragraph

"""
Objects used to create Requests sent via Client to the G3 API endpoint. 
Typically, requests are built using the RequestBuilder. 
"""


class ParaSpec(NamedTuple):
    type: str
    """ Type of the paragraphs, typically one of Paragraph.TYPE_TITLE, Paragraph.TYPE_ABSTRACT, Paragraph.TYPE_BODY; 
    possibly Paragraph.TYPE_SECTION_HEADING  """
    text: str
    """ Text of the paragraph """

    @staticmethod
    def title(text: str) -> 'ParaSpec':
        """
        Paragraph representing a title of the whole document. It's equivalent to `subject`.
        """
        return ParaSpec(Paragraph.TYPE_TITLE, str(text) if text is not None else '')

    @staticmethod
    def subject(text: str) -> 'ParaSpec':
        """
        Paragraph representing a subject of the document or email. It's equivalent to `title`.
        """
        return ParaSpec.title(text)

    @staticmethod
    def abstract(text: str) -> 'ParaSpec':
        """
        Paragraph representing an abstract of the document. It's equivalent to `lead` and `perex`.
        """
        return ParaSpec(Paragraph.TYPE_ABSTRACT, str(text) if text is not None else '')

    @staticmethod
    def lead(text: str) -> 'ParaSpec':
        """
        Paragraph representing a lead of the document. It's equivalent to `abstract` and `perex`.
        """
        return ParaSpec.abstract(text)

    @staticmethod
    def perex(text: str) -> 'ParaSpec':
        """
        Paragraph representing a perex of the document. It's equivalent to `abstract` and `lead`.
        """
        return ParaSpec.abstract(text)

    @staticmethod
    def body(text: str) -> 'ParaSpec':
        """
        Paragraph containing the body or text of the document.
        """
        return ParaSpec(Paragraph.TYPE_BODY, str(text) if text is not None else '')

    def __str__(self):
        return objToStr(self, self._fields)

    def __repr__(self):
        return objRepr(self, self._fields)


class AnalysisType(Enum):
    """ The linguistic analyses the G3 API can perform;
    `more detail <https://help.geneea.com/api_general/guide/analyses.html>`__ """
    ALL = 1
    """ Perform all analyses at once """
    ENTITIES = 2
    """ Recognize and standardize entities in text; 
    `more detail <https://help.geneea.com/api_general/guide/entities.html>`__"""
    TAGS = 3
    """ Assign semantic tags to a document.
    `more detail <https://help.geneea.com/api_general/guide/tags.html>`__"""
    RELATIONS = 4
    """ Relations between entities and their attributes; 
    `more detail <https://help.geneea.com/api_general/guide/relations.html>`__"""
    SENTIMENT = 5
    """ Detect the emotions of the author contained in the text;
    `more detail <https://help.geneea.com/api_general/guide/sentiment.html>`__"""
    LANGUAGE = 6
    """ Detect the language the text is written in;
     `more detail <https://help.geneea.com/api_general/guide/language.html>`__"""

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return objRepr(self, ('name',))

    @staticmethod
    def parse(val: str) -> 'AnalysisType':
        val = val.strip().upper()
        for a in AnalysisType:
            if val == a.name:
                return a
        raise ValueError(f'invalid analysis type "{val}"')


class LanguageCode(Enum):
    """ Typically used ISO 639-1 language codes. """
    CS = 'cs'
    DE = 'de'
    EN = 'en'
    ES = 'es'
    PL = 'pl'
    SK = 'sk'

    def __str__(self):
        return self.value

    def __repr__(self):
        return objRepr(self, ('name',))


class Domain(Enum):
    """ Typically used domains. For more info `see <https://help.geneea.com/api_general/guide/domains.html>`__. """
    MEDIA = 'media'
    """ General media articles. """
    NEWS = 'news'
    """ Media articles covering news. """
    SPORT = 'sport'
    """ Media articles covering sport news. """
    TABLOID = 'tabloid'
    """ Tabloid articles. """
    TECH = 'tech'
    """ Media articles covering technology and science. """
    VOC = 'voc'
    """ General Voice-of-the customer documents (e.g. reviews). """
    VOC_BANKING = 'voc-banking'
    """ Voice-of-the customer documents covering banking (e.g. reviews of banks). """
    VOC_HOSPITALITY = 'voc-hospitality'
    """ Voice-of-the customer documents covering restaurants (e.g. reviews of restaurants). """

    def __str__(self):
        return self.value

    def __repr__(self):
        return objRepr(self, ('name',))


class TextType(Enum):
    """ Typically used text types. """
    CLEAN = 'clean'
    """ Text that is mostly grammatically, orthographically and typographically correct, e.g. news articles. """
    CASUAL = 'casual'
    """ Text that ignores many formal grammatical, orthographical and typographical conventions, 
    e.g. social media posts. """

    def __str__(self):
        return self.value

    def __repr__(self):
        return objRepr(self, ('name',))


class Diacritization(Enum):
    """ Supported diacritization modes. """
    NONE = 'none'
    """ No diacritization is performed. """
    AUTO = 'auto'
    """ Diacritics is added if needed. """
    YES = 'yes'
    """ Diacritics is added to words without it if needed. """
    REDO = 'redo'
    """ Diacritics is first removed and then added if needed. """

    def __str__(self):
        return self.value

    def __repr__(self):
        return objRepr(self, ('name',))


STD_KEYS = frozenset([
    'id', 'title', 'text', 'paraSpecs', 'analyses', 'htmlExtractor', 'language', 'langDetectPrior', 'domain',
    'textType', 'referenceDate', 'diacritization', 'returnMentions', 'returnItemSentiment', 'metadata'
])
""" Standard keys used by the G3 request. """


class Request(NamedTuple):
    id: Optional[str]
    """ Unique identifier of the document """
    title: Optional[str]
    """ The title or subject of the document, when available; mutually exclusive with the ``paraSpecs`` parameter """
    text: Optional[str]
    """ The main text of the document; mutually exclusive with the ``paraSpecs`` parameter """
    paraSpecs: Optional[List[ParaSpec]]
    """ The document paragraphs; mutually exclusive with `title` and `text` parameters. """
    analyses: Optional[Set[AnalysisType]]
    """ What analyses to return """
    language: Optional[str]
    """ The language of the document as ISO 639-1; auto-detection will be used if omitted. """
    langDetectPrior: Optional[str]
    """ The language detection prior; e.g. ‘de,en’. """
    domain: Optional[str]
    """ The source domain from which the document originates. 
    See the `available domains <https://help.geneea.com/api_general/guide/domains.html>`__. """
    textType: Optional[str]
    """ The type or genre of text; not supported in public workflows/domains yet. """
    referenceDate: Optional[str]
    """ Date to be used for the analysis as a reference; values: “NOW” or in format YYYY-MM-DD. """
    diacritization: Optional[str]
    """ Determines whether to perform text diacritization """
    returnMentions: bool
    """ Should entity/tag/relation mentions be returned? No mentions are returned if None. """
    returnItemSentiment: bool
    """ Should entity/mention/tag/relation etc. sentiment be returned? No sentiment is returned if None """
    metadata: Mapping[str, str]
    """ Extra non-NLP type of information related to the document, key-value pairs """
    custom: JsonType

    class Builder:
        def __init__(
            self, *,
            analyses: Iterable[AnalysisType] = None,
            language: Union[LanguageCode, str] = None,
            langDetectPrior: str = None,
            domain: Union[Domain, str] = None,
            textType: Union[TextType, str] = None,
            referenceDate: Union[datetime.date, datetime.datetime, str] = None,
            diacritization: Union[Diacritization, str] = None,
            returnMentions: bool = False,
            returnItemSentiment: bool = False,
            metadata: Mapping[str, str] = None,
            customConfig: JsonType = None,
        ) -> None:
            """
            Create a builder with fields meant to be shared across requests

            :param analyses: What analyses to return.
            :param language: The language of the document as ISO 639-1; auto-detection will be used if omitted.
            :param langDetectPrior: The language detection prior; e.g. ‘de,en’.
            :param domain: The source domain from which the document originates.
            See the `available domains <https://help.geneea.com/api_general/guide/domains.html>`__.
            :param textType: The type or genre of text; not supported in public workflows/domains yet.
            :param referenceDate: Date to be used for the analysis as a reference; values: “NOW” or in format YYYY-MM-DD. No reference date is used if None.
            :param diacritization: Determines whether to perform text diacritization
            :param returnMentions: Should entity/tag/relation mentions be returned? No mentions are returned if None.
            :param returnItemSentiment: Should entity/mention/tag/relation etc. sentiment be returned? No sentiment is returned if None
            :param metadata: extra non-NLP type of information related to the document, key-value pairs
            :return: The builder for fluent style chaining.
            """
            self.analyses: Optional[Set[AnalysisType]] = set(analyses) if analyses is not None else analyses
            self.language: Optional[str] = str(language) if language else None
            self.langDetectPrior: Optional[str] = str(langDetectPrior) if langDetectPrior else None
            self.domain: Optional[str] = str(domain) if domain else None
            self.textType: Optional[str] = str(textType) if textType else None
            self.referenceDate: Optional[str] = self._refDate(referenceDate) if referenceDate else None
            self.diacritization: Optional[str] = str(diacritization) if diacritization else None
            self.returnMentions: bool = returnMentions
            self.returnItemSentiment: bool = returnItemSentiment
            self.metadata: Mapping[str, str] = {key: str(val) for key, val in metadata.items()} if metadata else {}
            self.customConfig: JsonType = {}
            self.setCustomConfig(**(customConfig or {}))

        @staticmethod
        def _refDate(date: Union[datetime.date, datetime.datetime, str]) -> str:
            if isinstance(date, str):
                if date.upper() == 'NOW':
                    return 'NOW'
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
            return date.strftime('%Y-%m-%d')

        def setCustomConfig(self, **customConfig) -> 'Request.Builder':
            """
            Add custom options to the request builder. Existing custom options are overwritten.

            :param customConfig: Any custom options passed to the G3 API endpoint
            :return: The builder for fluent style chaining.
            """
            keyOverlap = sorted(STD_KEYS & customConfig.keys())
            if keyOverlap:
                raise ValueError(f'custom keys {keyOverlap} overlap with the standard request keys')
            self.customConfig.update(customConfig)
            return self

        def build(self, *,
            id: Union[str, int] = None,
            title: str = None,
            text: str = None,
            paraSpecs: List[ParaSpec] = None,
            language: Union[LanguageCode, str] = None,
            referenceDate: Union[datetime.date, datetime.datetime, str] = None,
            metadata: Mapping[str, str] = None,
            customConfig: JsonType = None,
        ) -> 'Request':
            """
            Creates a new request object to be passed to the G3 client.

            :param id: Unique identifier of the document
            :param title: The title or subject of the document, when available; mutually exclusive with the ``paraSpecs`` parameter
            :param text: The main text of the document; mutually exclusive with the ``paraSpecs`` parameter
            :param paraSpecs: The document paragraphs; mutually exclusive with `title` and `text` parameters.
            :param language: The language of the document as ISO 639-1; auto-detection will be used if None.
            :param referenceDate: Date to be used for the analysis as a reference; values: ``NOW`` or in format YYYY-MM-DD. No reference date is used if None.
            :param metadata: extra non-NLP type of information related to the document, key-value pairs
            :param customConfig: Any custom options passed to the G3 API endpoint
            :return: Request object to be passed to the G3 client.
            """
            if (text is not None or title is not None) and paraSpecs is not None:
                raise ValueError('parameters text/title and paraSpecs are mutually exclusive')
            if text is None and paraSpecs is None:
                raise ValueError('either text or paraSpecs parameter has to be provided')
            if customConfig is not None:
                keyOverlap = sorted(STD_KEYS & customConfig.keys())
                if keyOverlap:
                    raise ValueError(f'custom keys {keyOverlap} overlap with the standard request keys')

            if metadata is not None and self.metadata:
                metadata = {**self.metadata, **metadata}
            if customConfig is not None and self.customConfig:
                customConfig = {**self.customConfig, **customConfig}

            if paraSpecs:
                paraSpecs = [ParaSpec(p.type, str(p.text)) for p in paraSpecs]
            if metadata:
                metadata = {key: str(val) for key, val in metadata.items()}

            return Request(
                id=str(id) if id is not None else None,
                title=str(title) if title is not None else None,
                text=str(text) if text is not None else None,
                paraSpecs=paraSpecs,
                analyses=self.analyses,
                language=str(language) if language else self.language,
                langDetectPrior=self.langDetectPrior,
                domain=self.domain,
                textType=self.textType,
                referenceDate=self._refDate(referenceDate) if referenceDate else self.referenceDate,
                diacritization=self.diacritization,
                returnMentions=self.returnMentions,
                returnItemSentiment=self.returnItemSentiment,
                metadata=metadata if metadata is not None else self.metadata,
                custom=customConfig if customConfig is not None else self.customConfig,
            )

    @staticmethod
    def fromDict(raw: JsonType) -> 'Request':
        """ Reads a request object from a JSON-like dictionary. """
        custom = {key: raw[key] for key in raw.keys() if key not in STD_KEYS}

        title, text, paraSpecs = raw.get('title'), raw.get('text'), raw.get('paraSpecs')
        if (text is not None or title is not None) and paraSpecs is not None:
            raise ValueError('parameters text/title and paraSpecs are mutually exclusive')
        if text is None and paraSpecs is None:
            raise ValueError('either text or paraSpecs parameter has to be provided')

        return Request(
            id=str(raw['id']) if 'id' in raw else None,
            title=str(title) if title is not None else None,
            text=str(text) if text is not None else None,
            paraSpecs=[ParaSpec(p['type'], str(p['text'])) for p in paraSpecs] if paraSpecs is not None else None,
            analyses=set(AnalysisType.parse(a) for a in raw['analyses']) if 'analyses' in raw else None,
            language=raw.get('language'),
            langDetectPrior=raw.get('langDetectPrior'),
            domain=raw.get('domain'),
            textType=raw.get('textType'),
            referenceDate=raw.get('referenceDate'),
            diacritization=raw.get('diacritization'),
            returnMentions=raw.get('returnMentions', False),
            returnItemSentiment=raw.get('returnItemSentiment', False),
            metadata={key: str(val) for key, val in raw.get('metadata', {}).items()},
            custom=custom,
        )

    def toDict(self) -> JsonType:
        """ Converts the request object to a JSON-like dictionary. """
        builder = DictBuilder({})
        builder.addIfNotNone('id', self.id)
        if self.paraSpecs:
            builder['paraSpecs'] = [{'type': p.type, 'text': p.text} for p in self.paraSpecs]
        else:
            builder.addIfNotNone('title', self.title)
            builder.addIfNotNone('text', self.text)
        if self.analyses:
            builder['analyses'] = [str(a) for a in sorted(self.analyses, key=attrgetter('value'))]
        builder.addIfNotNone('language', self.language)
        builder.addIfNotNone('langDetectPrior', self.langDetectPrior)
        builder.addIfNotNone('domain', self.domain)
        builder.addIfNotNone('textType', self.textType)
        builder.addIfNotNone('referenceDate', self.referenceDate)
        builder.addIfNotNone('diacritization', self.diacritization)
        if self.returnMentions:
            builder['returnMentions'] = True
        if self.returnItemSentiment:
            builder['returnItemSentiment'] = True
        builder.addIfNotNone('metadata', self.metadata)
        return {
            **builder.build(),
            **self.custom
        }

    def __str__(self):
        return objToStr(self, self._fields)

    def __repr__(self):
        return objRepr(self, self._fields)
