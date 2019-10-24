from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from sekg.text.extractor.domain_entity.identifier_util import IdentifierInfoExtractor

class SentenceHandler:
    __HyphenHandler = 'hyphen_handler'

    # def __init__(self):
    #     self.__hyphen_handler(Doc)
    #     # Doc.set_extension(SentenceHandler.__HyphenHandler, method=SentenceHandler.__hyphen_handler(Doc), default=None, force=True)
    #
    # def __call__(self, doc: Doc):
    #     return self.__hyphen_handler(doc)
    #     # return doc

    @staticmethod
    def hyphen_handler(doc: Doc):
        """
        合并连字符，如fail-fast在tokenize之后会分成fail - fast三个，合并之后变为fail-fast
        :param doc:
        :return:
        """
        hyphen_index = []
        hyphen_index_start = -1
        method_left_brace_cache_index = -1
        left_angle_bracket = -1
        angle_brackets_list = []
        method_brace_pair_list = []
        length = len(doc)
        for i, token in enumerate(doc):
            if '-' == token.text:
                if hyphen_index_start == -1:
                    hyphen_index_start = i - 1
            else:
                if hyphen_index_start != -1:
                    if i != length-1:
                        if doc[i+1].text != '-':
                            hyphen_index.append((hyphen_index_start, i))
                            hyphen_index_start = -1
                        else:
                            continue
                    else:
                        hyphen_index.append((hyphen_index_start, i))
                        hyphen_index_start = -1

        # count = 0
        with doc.retokenize() as retokenizer:
            for start, end in hyphen_index:
                # attrs = {"LEMMA": doc[num - 1].text + '-' + doc[num + 1].text}
                attrs = {"LEMMA": "".join([token.text for token in doc[(start):(end+1)]]), "TAG": doc[end].tag_, "POS": doc[end].pos_}
                retokenizer.merge(doc[start:end+1], attrs=attrs)
                # count += 1
        for i, token in enumerate(doc):
            # todo" complete this for sentence containing method name
            # 添加了对method name的处理
            if "<" == token.text:
                if i > 0 and doc[i-1].text != ">":
                    left_angle_bracket = i-1
                else:
                    left_angle_bracket = i
            elif "<" in token.text:
                left_angle_bracket = i

            if ">" == token.text and left_angle_bracket != -1:
                angle_brackets_list.append((left_angle_bracket, i))
                left_angle_bracket = -1
        # print(method_brace_pair_list)
        with doc.retokenize() as retokenizer:
            for star_index, end_index in angle_brackets_list:
                attrs = {"LEMMA": " ".join([token.text for token in doc[(star_index):(end_index+1)]]),
                         "POS": "NOUN",
                         "TAG": "NN",
                         }
                retokenizer.merge(doc[star_index:end_index+1], attrs=attrs)

        for i, token in enumerate(doc):
            # todo" complete this for sentence containing method name
            # 添加了对method name的处理
            if "(" == token.text:
                if i > 0 and doc[i-1].text != ")" and doc[i-1].text != ".":
                    method_left_brace_cache_index = i-1
                else:
                    method_left_brace_cache_index = i
            elif "(" in token.text:
                method_left_brace_cache_index = i

            if ")" == token.text and method_left_brace_cache_index != -1:
                method_brace_pair_list.append((method_left_brace_cache_index, i))
                method_left_brace_cache_index = -1
        # print(method_brace_pair_list)
        with doc.retokenize() as retokenizer:
            for star_index, end_index in method_brace_pair_list:
                span = doc[star_index:(end_index+1)]
                if not SentenceHandler.is_complete_sentence(span):
                    attrs = {"LEMMA": " ".join([token.text for token in doc[(star_index):(end_index+1)]]),
                             "POS": "NOUN",
                             "TAG": "NN",
                             }
                    retokenizer.merge(doc[star_index:end_index+1], attrs=attrs)

        return doc

    @staticmethod
    def is_complete_sentence(doc):
        root_flag = False
        nusj_flag = False
        for token in doc:
            if token.tag_.startswith('NN'):
                nusj_flag = True
            if token.tag_.startswith('VB'):
                root_flag = True
        if root_flag and nusj_flag:
            return True
        return False

    @staticmethod
    def tag_fixer_after_parser(doc):
        for token in doc:
            if token.dep_ == 'conj' and token.pos_ == 'NOUN' and token.head.pos_ == 'VERB':
                attrs = {"LEMMA": token.lemma_, "TAG": token.head.tag_, "POS": "VERB"}
                with doc.retokenize() as retokenizer:
                    retokenizer.merge(doc[token.i:token.i+1], attrs=attrs)
        return doc

    @staticmethod
    def merge_verb_prep(doc: Doc):
        for token in doc:
            # print(token.text)
            if token.dep_ == 'ROOT' and token.pos_ == 'VERB' and token.tag_ != 'VBN':
                # print(token.text)
                if token.i < len(doc) - 1:
                    if doc[token.i + 1].dep_ == 'prep' and doc[token.i+1].head == token:
                        with doc.retokenize() as retokenizer:
                            attrs = {"LEMMA": " ".join([token.lemma_, doc[token.i+1].lemma_]),
                                     "POS": "VERB",
                                     "TAG": token.tag_
                                     }
                            retokenizer.merge(doc[token.i:token.i + 2], attrs=attrs)
                        if token.i < len(doc) - 1:
                            # print(doc[token.i+1])
                            if doc[token.i+1].dep_ == 'pobj' and doc[token.i+1].pos_ == 'NOUN':
                                with doc.retokenize() as retokenizer:
                                    attrs = {"DEP": "dobj"
                                             }
                                    retokenizer.merge(doc[token.i+1:token.i + 2], attrs=attrs)
                    break
        return doc

    @staticmethod
    def method_name_tag(doc: Doc):
        """
        为method_name自定义词性标注
        :param doc:
        :return:
        """
        idntifier = IdentifierInfoExtractor()
        # name = name.split("(")[0].split(".")[-1]
        # uncamel = self.uncamelize(name).lower()
        # doc = self.nlp(uncamel)
        return idntifier.pos_tag_for_method_name_from_method_doc(doc)

    @staticmethod
    def class_name_tag(doc: Doc):
        """
        为class_name自定义词性标注
        :param doc:
        :return:
        """
        for i in range(0, len(doc)):
            # 因为class_name可能出现RC2StringBuilder这种类型，2,4不一定就是表示to和for
            # if spacy_doc[i].text == "2" and i != 0 and len(spacy_doc) - 1:
            #     spacy_doc[i].lemma_ = "to"
            #     spacy_doc[i].pos_ = "ADP"
            #     spacy_doc[i].tag_ = "IN"
            #
            # if spacy_doc[i].text == "4" and i != 0 and len(spacy_doc) - 1:
            #     spacy_doc[i].lemma_ = "for"
            #     spacy_doc[i].pos_ = "ADP"
            #     spacy_doc[i].tag_ = "IN"

            if doc[i].text.lower() == "to":
                doc[i].lemma_ = "to"
                doc[i].pos_ = "ADP"
                doc[i].tag_ = "IN"

            if doc[i].text.lower() in ["id", "ID", "Id"]:
                doc[i].lemma_ = "id"
                doc[i].pos_ = "NOUN"
                doc[i].tag_ = "NN"

        if doc[-1].pos_ == 'VERB':
            doc[-1].pos_ = 'NOUN'
            doc[-1].tag_ = 'NN'

        return doc
